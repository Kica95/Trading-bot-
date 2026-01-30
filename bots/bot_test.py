
from Example.Binance.bots import BotBase
import random


class BotExample(BotBase):
    def optimize(self):
        pass

    def strategy(self):

        self.buy(self.current_budget)


def main():
    # Read numbers from a text file into a list
    simulation_data = []
    with open("../data/data_2025_02/BTCUSDT_close_prices.txt", "r") as file:
        for line in file:
            value = float(line.strip())  # remove extra spaces/newlines and convert to float
            simulation_data.append(value)

    # print(simulation_data)
    macd_bot = BotExample(100, True, 'USDT', 'BNBUSDT', data_entry_size=26,
                          starting_investment_value=simulation_data[0])
    print(macd_bot.investment_value)
    print(macd_bot.investment_value)

    for s in simulation_data[1:]:
        macd_bot.execute(s, s)
        print(macd_bot.current_budget, macd_bot.current_investment)
        print(s)


if __name__ == '__main__':
    main()