import sys
import os

from Example.Binance.utility import extract_column_values
from Example.Binance.bots import BotMacd


def main_simulation_macd():
    # Read numbers from a text file into a list
    simulation_data = []
    with open("../../data/data_2024_09_1h/BTCUSDT_close_prices_2024_09.txt", "r") as file:
        for line in file:
            value = float(line.strip())  # remove extra spaces/newlines and convert to float
            simulation_data.append(value)

    #print(simulation_data)
    macd_bot = BotMacd(100, True, 'USDT', 'BNBUSDT', data_entry_size=26, starting_investment_value=simulation_data[0])
    print(macd_bot.investment_value)
    for s in simulation_data[1:]:
        macd_bot.execute(s, s)
        print(macd_bot.current_budget, macd_bot.current_investment)
        print(s)


if __name__=="__main__":
    main_simulation_macd()