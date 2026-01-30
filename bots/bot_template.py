"""
Step 1: import BotBase
        import all needed libraries for the strategy
"""
from Example.Binance.bots import BotBase
import random

"""
Step 2: Name a bot based on a strategy that it uses,
        New bot always inherits BotBase
"""
class BotExample(BotBase):
    """
    Step 3: Create a strategy
    
    """

    def optimize(self):
        pass

    def strategy(self):

        num = random.randint(-1, 1)
        if num == 1:
            self.buy(self.current_budget)
        elif num == - 1:
            self.sell(self.current_investment)




def main():
    # Read numbers from a text file into a list
    simulation_data = []
    with open("../data/data_2025_02/BTCUSDT_close_prices.txt", "r") as file:
        for line in file:
            value = float(line.strip())  # remove extra spaces/newlines and convert to float
            simulation_data.append(value)

    #print(simulation_data)
    macd_bot = BotExample(100, True, 'USDT', 'BNBUSDT', data_entry_size=26, starting_investment_value=simulation_data[0])
    print(macd_bot.investment_value)
    print(macd_bot.investment_value)

    for s in simulation_data[1:]:
        macd_bot.execute(s, s)
        print(macd_bot.current_budget, macd_bot.current_investment)
        print(s)


if __name__ == '__main__':
    main()