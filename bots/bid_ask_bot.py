from Example.Binance.bots import BotBase
from Example.Binance.utility import bid_ask_spread_model
import math



class BotStockAdvice(BotBase):
    def __init__(self, starting_budget, simulation=True, symbol_sell='USDT', symbol_buy='BNBUSDT', **kwargs):
        super().__init__(starting_budget, simulation, symbol_sell, symbol_buy, **kwargs)
        self.bid_prediction = 0
        self.ask_prediction = 0
        self.inventory = 1
        self.prediction = None
        self.count_buy = 0
        self.count_sell = 0
        self.kappa =0.1
        self.risk_aversion = 1

    def optimize(self):
        pass

    def strategy(self):

        self.prediction = bid_ask_spread_model(self.data_entry, self.inventory, self.risk_aversion)
        self.bid_prediction = self.prediction[0]
        self.ask_prediction = self.prediction[1]
        if self.data_entry[-1]['close']<self.bid_prediction:
            self.buy(self.current_budget)
            self.prediction = bid_ask_spread_model(self.data_entry, self.inventory,self.kappa)
            self.bid_prediction = self.prediction[0]
            #self.kappa = 1/ self.bid_prediction
            self.ask_prediction = self.prediction[1]
            self.count_buy+=1
        if self.data_entry[-1]['close'] > self.ask_prediction:
            self.sell(self.current_investment)
            self.prediction = bid_ask_spread_model(self.data_entry, self.inventory,self.kappa)
            self.bid_prediction = self.prediction[0]
            self.ask_prediction = self.prediction[1]
            #self.kappa = 1 / self.ask_prediction
            self.count_sell+=1

    def grid_search_avellaneda_stoikov(self, param_grid, simulation_data, steps=None, verbose=True):
        """
        Performs a grid search for optimal Avellaneda-Stoikov (AV) model parameters.
        Tries all combinations of parameters in 'param_grid' and selects the one that
        maximizes final current_budget + current_investment.

        :param param_grid: dict with keys ['kappa', 'risk_aversion', 'inventory']
        :param simulation_data: list of dicts [{'close': x, 'bid': y, 'ask': z}, ...]
        :param steps: optional int, limit number of simulation steps
        :param verbose: if True, prints progress
        :return: (best_params, best_total_value)
        """
        from itertools import product

        best_total_value = float('-inf')
        best_params = {}

        all_combinations = list(product(
            param_grid['kappa'],
            param_grid['risk_aversion'],
            param_grid['inventory']
        ))

        total_combos = len(all_combinations)
        combo_index = 0

        for kappa, risk_aversion, inventory in all_combinations:
            combo_index += 1

            # Reset simulation state for each parameter combo
            self.reset_bot()  # You should implement this to reset budget, investment, etc.
            self.kappa = kappa
            self.risk_aversion = risk_aversion
            self.inventory = inventory


            # Run the simulated trading loop
            sim_data_iter = simulation_data[:steps] if steps else simulation_data

            for data_point in sim_data_iter:
                self.execute(data_point, data_point)

            current_total_value = self.current_budget + self.current_investment


            if current_total_value > best_total_value:
                best_total_value = current_total_value
                best_params = {
                    'kappa': kappa,
                    'risk_aversion': risk_aversion,
                    'inventory': inventory
                }

        # Final summary
        print("\n=== Grid Search Completed ===")
        print(f"Best Parameters: {best_params}")
        print(f"Best Total Value: {best_total_value:.4f}")

        self.kappa = best_params['kappa']
        self.inventory = best_params['inventory']
        self.risk_aversion = best_params['risk_aversion']
        #return best_params, best_total_value

    def reset_bot(self):
        """Resets trading bot state (budget, investment, counters, etc.)"""
        self.current_budget = self.starting_budget
        self.current_investment = 0
        self.inventory = 0
        self.count_buy = 0
        self.count_sell = 0
        self.data_entry = []

def main():
    param_grid = {
        'kappa': [0.01, 0.05, 0.1, 0.5, 1, 1.5, 1.75,2],
        'inventory': [-2,-1.5 ,-1,-0.5,0, 0.5, 1, 1.5, 2],  # Adapt based on your strategy needs
        'risk_aversion': [0.01, 0.1, 0.25, 0.5, 0.75, 1]
    }

    # Read numbers from a text file into a list
    close = []
    #with open("../data/main_data/BNBUSDT_close_prices_60m.txt", "r") as file:
    with open("../data/main_data/BNBUSDT_close_prices_1m.txt", "r") as file:
        for line in file:
            value = float(line.strip())  # remove extra spaces/newlines and convert to float
            close.append(value)
    high = []
    #with open("../data/main_data/BNBUSDT_close_prices_60m.txt", "r") as file:
    with open("../data/main_data/BNBUSDT_high_1m.txt", "r") as file:
        for line in file:
            value = float(line.strip())  # remove extra spaces/newlines and convert to float
            high.append(value)
    low = []
    #with open("../data/main_data/BNBUSDT_close_prices_60m.txt", "r") as file:
    with open("../data/main_data/BNBUSDT_low_1m.txt", "r") as file:
        for line in file:
            value = float(line.strip())  # remove extra spaces/newlines and convert to float
            low.append(value)
    simulation_data = []
    print(high)
    for ind, d in enumerate(close):
        data_step = {}
        data_step['close'] = close[ind]
        data_step['ask'] = high[ind]
        data_step['bid'] = low[ind]

        simulation_data.append(data_step)

    #print(simulation_data)
    stock_advice_bot = BotStockAdvice(100, True, 'USDT', 'BNBUSDT', data_entry_size=30, starting_investment_value=simulation_data[0]['close'])

    #best_params, best_value = stock_advice_bot.grid_search_avellaneda_stoikov(
        #param_grid, simulation_data, steps=500)

    #print(f"Best Parameters: {best_params} with a total value of {best_value}")

    max_counter = 100
    counter = max_counter
    for ind, s in enumerate(simulation_data[1:]):
        print("ovde")
        if counter > 0:
            print("ovde")
            counter -= 1
        else:
            counter = max_counter
            prediction_steps = 500
            print("ovde")
            print(len(simulation_data[ind:]))
            if len(simulation_data[ind:])<500:
                max_counter = len(simulation_data[ind:])
            stock_advice_bot.grid_search_avellaneda_stoikov(param_grid, simulation_data[ind:], steps=prediction_steps)
        stock_advice_bot.execute(s,s)
        print(stock_advice_bot.current_budget, stock_advice_bot.current_investment)

    print(stock_advice_bot.count_buy)
    print(stock_advice_bot.count_sell)
if __name__ == '__main__':
    main()
