import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from Example.Binance.bots import BotBase
from Example.Binance.utility import  DATA_DUMP
from concurrent.futures import ProcessPoolExecutor, as_completed
import itertools
import copy


class BitcoinLSTMModel:
    def __init__(self, sequence_length=30, hidden_size=50, num_layers=1, lr=0.01, epochs=200, device=None):
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lr = lr
        self.epochs = epochs
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.scaler = MinMaxScaler()
        self.model = self._build_model().to(self.device)

    class _LSTM(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers, output_size, tolerance = 0.005):
            super().__init__()
            self.positive_tolerance = 1 + tolerance
            self.negative_tolerance = 1 - tolerance
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
            self.fc = nn.Linear(hidden_size, output_size)

        def forward(self, x):
            h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
            c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
            out, _ = self.lstm(x, (h0, c0))
            out = self.fc(out[:, -1, :])
            return out

    def _build_model(self):
        return self._LSTM(input_size=1, hidden_size=self.hidden_size, num_layers=self.num_layers, output_size=1)

    def prepare_data(self, prices):
        """Prepares normalized sequences for training/testing."""
        prices = np.array(prices).reshape(-1, 1)
        prices_scaled = self.scaler.fit_transform(prices)

        X, y = [], []
        for i in range(len(prices_scaled) - self.sequence_length):
            X.append(prices_scaled[i:i + self.sequence_length])
            y.append(prices_scaled[i + self.sequence_length])
        X, y = np.array(X), np.array(y)

        X_tensor = torch.from_numpy(X).float()
        y_tensor = torch.from_numpy(y).float()
        return X_tensor, y_tensor

    def train(self, prices):
        """Train LSTM model on given close prices."""
        X, y = self.prepare_data(prices)
        train_size = int(0.8 * len(X))
        X_train, y_train = X[:train_size], y[:train_size]
        X_test, y_test = X[train_size:], y[train_size:]

        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

        self.model.train()
        for epoch in range(self.epochs):
            outputs = self.model(X_train.to(self.device))
            loss = criterion(outputs, y_train.to(self.device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        self.X_test, self.y_test = X_test, y_test

    def evaluate(self):
        """Evaluate model on test data."""
        self.model.eval()
        with torch.no_grad():
            train_pred = self.model(self.X_test.to(self.device)).cpu().numpy()
            y_true = self.y_test.numpy()

        train_pred_inv = self.scaler.inverse_transform(train_pred)
        y_true_inv = self.scaler.inverse_transform(y_true)

        mse = mean_squared_error(y_true_inv, train_pred_inv)


    def predict_future(self, recent_prices, steps_ahead=30):
        """Given last N close prices (as dict or list), predict next `steps_ahead` prices."""
        if isinstance(recent_prices, dict):
            recent_prices = list(recent_prices.values())
        elif not isinstance(recent_prices, (list, np.ndarray)):
            raise ValueError("Input must be a list, np.ndarray, or dict of close prices.")

        data = np.array(recent_prices).reshape(-1, 1)
        scaled_data = self.scaler.transform(data)

        seq = scaled_data[-self.sequence_length:].tolist()
        predictions = []

        self.model.eval()
        for _ in range(steps_ahead):
            seq_tensor = torch.tensor([seq[-self.sequence_length:]], dtype=torch.float32).to(self.device)
            with torch.no_grad():
                pred = self.model(seq_tensor).cpu().item()
            seq.append([pred])
            predictions.append(pred)

        predictions = np.array(predictions).reshape(-1, 1)
        prediction = self.scaler.inverse_transform(predictions).flatten()
        if np.mean(prediction) > self._build_model().positive_tolerance * recent_prices[-1]:
            return 1
        elif np.mean(prediction) < recent_prices[-1]:
            return -1
        else:
            return 0




class BotLSTM(BotBase):

    def __init__(self, starting_budget, simulation=True, symbol_sell='USDT', symbol_buy='BNBUSDT', **kwargs):
        super().__init__(starting_budget, simulation, symbol_sell, symbol_buy, **kwargs)
        self.neural_network = BitcoinLSTMModel(sequence_length=30, epochs=200)
        self.optimize_steps = 100
        if 'optimize_steps' in kwargs:
            self.optimize_steps = kwargs['optimize_steps']
        self.current_optimize_steps = self.optimize_steps

    def optimize(self, simulation_data, **kwargs):
        """
        Run a parallelized grid search over (sequence_length, steps_ahead)
        to maximize final portfolio value.
        """
        max_workers = None
        seq_lengths = (30, 60, 100, 150)
        if "seq_length" in kwargs:
            seq_length = kwargs["seq_length"]

        step_ahead = (10, 30, 60, 100)

        if 'steps_ahead' in kwargs:
            step_ahead = kwargs['steps_ahead']

        # --- Helper function for one run ---
        def simulate(seq_len, steps_ahead):
            bot = BotLSTM(
                self.starting_budget,
                True,
                self.symbol_sell,
                self.symbol_buy,
                data_entry_size=seq_len,
                starting_investment_value=simulation_data[0]
            )
            bot.neural_network = BitcoinLSTMModel(sequence_length=seq_len, epochs=100)
            total = 0
            for price in simulation_data[1:]:
                bot.execute(price, price)
            total = bot.current_budget + bot.current_investment
            return (seq_len, steps_ahead, total)

        param_grid = list(itertools.product(seq_lengths, step_ahead))
        print(f"Running grid search on {len(param_grid)} combinations...")

        results = []
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(simulate, seq, step): (seq, step) for seq, step in param_grid}

            for i, future in enumerate(as_completed(futures)):
                seq, step = futures[future]
                try:
                    seq_len, steps_ahead, value = future.result()
                    results.append((seq_len, steps_ahead, value))
                    print(f"[{i + 1}/{len(param_grid)}] seq={seq_len}, step={steps_ahead} → value={value:.2f}")
                except Exception as e:
                    print(f"Error for seq={seq}, step={step}: {e}")

    def strategy(self):
        # 1. Fetch Bitcoin data


        # 2. Create and train model
        self.neural_network.train(self.data_entry)

        # 3. Evaluate
        self.neural_network.evaluate()

        # 4. Predict next 30 days given last 100 close prices
        recent_dict = {i: p for i, p in enumerate(self.data_entry[-100:])}
        predict_data = self.neural_network.predict_future(recent_dict, steps_ahead=30)
        self.data_reset()

        if predict_data== 1:
            self.buy(self.current_budget)
        elif predict_data == - 1:
            self.sell(self.current_investment)

        if self.current_optimize_steps > 0:
            self.current_optimize_steps -= 1
        else:

            self.current_optimize_steps = self.optimize_steps
            self.optimize(self.data_entry)




def main():
    # Read numbers from a text file into a list
    simulation_data = []
    #with open("../data/main_data/BNBUSDT_close_prices_60m.txt", "r") as file:
    with open("../data/main_data/BNBUSDT_close_prices_1m.txt", "r") as file:
        for line in file:
            value = float(line.strip())  # remove extra spaces/newlines and convert to float
            simulation_data.append(value)

    #print(simulation_data)

    lstm_bot = BotLSTM(100, True, 'USDT', 'BNBUSDT', data_entry_size=100, starting_investment_value=simulation_data[0])
    #print(lstm_bot.investment_value)
    i = 0
    for s in simulation_data[1:]:
        lstm_bot.execute(s,s)
        print(lstm_bot.current_optimize_steps)
        print(lstm_bot.current_budget, lstm_bot.current_investment)
        print(i)
        i+=1
        #print(s)
        #print(((s-simulation_data[0])/simulation_data[0])*100)
        '''
        with open(DATA_DUMP + "bot_advice_text.txt", "a") as f:
            f.write(str(stock_advice_bot.advice) +","+str(stock_advice_bot.current_budget) + "," + str(stock_advice_bot.current_investment)+"\n")
        with open(DATA_DUMP + "bot_advice_text_btcvalue.txt", "a") as f:
            f.write(str(stock_advice_bot.advice) +","+str(((s-simulation_data[0])/simulation_data[0])*100)+"\n")
        '''

if __name__ == '__main__':
    main()

