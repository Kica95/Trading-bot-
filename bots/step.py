

class Step:
    def __init__(self, buy_coin_symbol, sell_coin_symbol, amount=0, **kwargs):
        '''
        This object stores all the data that happened in one step,
         how much currency is exchanged from one point to another,
         all the data that bot needed to produce that step,
         and maybe even data that bot used to produce that step,
         so for instance
        :param kwargs:
        '''
        self.data = kwargs
        self.buy_coin_symbol = buy_coin_symbol
        self.sell_coin_symbol = sell_coin_symbol


    def update(self,data_name, data):
        self.data[data_name] = data

    def print(self):
        step_string = ''
        for key, value in self.data.items():
            step_string +=  f'{key} : {value}\n'
        step_string += '\n'
        return step_string



def main():
    step = Step('BTCUSDT', 'USDT', test=5124, test2='casca', test3=-512412)
    step.update('test5', 'test')
    step.print()


if __name__ == '__main__':
    main()