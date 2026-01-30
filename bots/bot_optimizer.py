import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from Example.Binance.bots import BotBase
from Example.Binance.utility import  DATA_DUMP
from Example.Binance.bots import BotLSTM, BitcoinLSTMModel
from concurrent.futures import ProcessPoolExecutor, as_completed
import itertools
import copy

def optimize(bot_type, **kwargs):
    """
    Run a parallelized grid search over (sequence_length, steps_ahead)
    to maximize final portfolio value.
    """

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

    param_grid = list(itertools.product(seq_lengths, step_aheads))
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


