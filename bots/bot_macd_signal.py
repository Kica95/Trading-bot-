from Example.Binance.bots import *
from Example.Binance.utility import macd_signal_int


class BotMacd(BotBase):

    def strategy(self):
        macd = macd_signal_int(self.data_entry)
        if macd == 1:
            self.buy(self.current_budget)
        elif macd == - 1:
            self.sell(self.current_investment)
    def optimize(self):
        pass



def main():
    #starting_budget, symbol_sell='USDT', symbol_buy='BNBUSDT', data_entry_size=1, max_steps=100)
    #test = BotBase(100)
    bot = BotMacd(100)
    print(bot.strategy())
    pass



if __name__ == '__main__':
    main()