from Example.Binance.bots import BotBase
from Example.Binance.utility import macd_signal_int, stock_advice_int, DATA_DUMP
from binance.client import Client
import time
import math



class BotStockAdvice(BotBase):
    def optimize(self):
        pass

    def __init__(self, starting_budget, simulation=True, symbol_sell='USDT', symbol_buy='BNBUSDT', **kwargs):
        super().__init__(starting_budget, simulation, symbol_sell, symbol_buy, **kwargs)
        self.advice = 0

    def strategy(self):
        self.advice = stock_advice_int(self.data_entry, 1,3,self.fee)
        if self.advice == 1:
            if self.simulation:
                self.buy(self.current_budget, has_fee = True)
            else:
                self.buy_binance(self.current_budget)

        elif self.advice == - 1:
            if self.simulation:
                self.sell(self.current_investment, has_fee = True)
            else:
                self.sell_binance(self.current_investment)


def main():
    # Read numbers from a text file into a list
    simulation_data = []
    #with open("../data/main_data/BNBUSDT_close_prices_60m.txt", "r") as file:
    with open("../data/main_data/BNBUSDT_close_prices_1m.txt", "r") as file:
        for line in file:
            value = float(line.strip())  # remove extra spaces/newlines and convert to float
            simulation_data.append(value)

    #print(simulation_data)
    stock_advice_bot = BotStockAdvice(100, True, 'USDT', 'BNBUSDT', fee = 0, data_entry_size=3, starting_investment_value=simulation_data[0])

    for s in simulation_data[1:]:
        stock_advice_bot.execute(s,s)
        print(stock_advice_bot.current_budget, stock_advice_bot.current_investment)
        print_to_text("\n"+str(stock_advice_bot.current_budget ) + " " + str(stock_advice_bot.current_investment))
        #print(s)
        #print(((s-simulation_data[0])/simulation_data[0])*100)
        '''
        with open(DATA_DUMP + "bot_advice_text.txt", "a") as f:
            f.write(str(stock_advice_bot.advice) +","+str(stock_advice_bot.current_budget) + "," + str(stock_advice_bot.current_investment)+"\n")
        with open(DATA_DUMP + "bot_advice_text_btcvalue.txt", "a") as f:
            f.write(str(stock_advice_bot.advice) +","+str(((s-simulation_data[0])/simulation_data[0])*100)+"\n")
        '''
def print_to_text(text: str, filename: str = "output.txt"):
    """
    Writes the given string to a text file.
    """
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text)
def main_binance():
    TIME_INTERVAL = 60
    CLOSE_INDEX  = 4
    bot = BotStockAdvice(10, False, 'USDT', 'BNBUSDT', data_entry_size=3)
    bot.load_binance_data()
    first_step = True
    while True:
        kl = bot.client.get_klines(symbol=bot.symbol_buy, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1)
        closes = [k[CLOSE_INDEX] for k in kl]; price = float(closes[-1])
        if first_step:
            first_step = False
            bot.investment_value = price
        else:
            bot.execute(price, price)
        print(bot.current_budget, bot.current_investment)

        time.sleep(TIME_INTERVAL)

if __name__ == '__main__':
    main()
