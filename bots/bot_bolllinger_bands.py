from Example.Binance.bots import BotBase
from Example.Binance.utility import macd_signal_int, stock_advice_int, DATA_DUMP
import math


class BotBollingerBands(BotBase):
    def strategy(self):
        BollingerBnds = macd_signal_int(self.data_entry)
        if BollingerBnds == 1:
            self.buy(self.current_budget)
        elif BollingerBnds == - 1:
            self.sell(self.current_investment)
    def optimize(self):
        pass
def main():
    # Read numbers from a text file into a list
    simulation_data = []
    with open("../data/main_data/BNBUSDT_close_prices_1m.txt", "r") as file:
        for line in file:
            value = float(line.strip())  # remove extra spaces/newlines and convert to float
            simulation_data.append(value)

    #print(simulation_data)
    Bollinger_Band_Bot = BotBollingerBands(100, True, 'USDT', 'BNBUSDT', data_entry_size=26, starting_investment_value=simulation_data[0])

    for s in simulation_data[1:]:
        Bollinger_Band_Bot.execute(s,s)
        print(Bollinger_Band_Bot.current_budget, Bollinger_Band_Bot.current_investment)
        #print(s)
        print(((s-simulation_data[0])/simulation_data[0])*100)
        '''
        with open(DATA_DUMP + "bot_advice_text.txt", "a") as f:
            f.write(str(stock_advice_bot.advice) +","+str(stock_advice_bot.current_budget) + "," + str(stock_advice_bot.current_investment)+"\n")
        with open(DATA_DUMP + "bot_advice_text_btcvalue.txt", "a") as f:
            f.write(str(stock_advice_bot.advice) +","+str(((s-simulation_data[0])/simulation_data[0])*100)+"\n")
        '''

if __name__ == '__main__':
    main()