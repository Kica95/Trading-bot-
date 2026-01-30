from abc import ABC, abstractmethod
import os
import sys
from decimal import Decimal, ROUND_DOWN
from binance.exceptions import BinanceAPIException
from Example.Binance.utility import get_key, get_key_linux
from binance.client import Client
from binance.helpers import round_step_size
import json
from math import floor


class BotBase(ABC):
    def __init__(self, starting_budget, simulation=True, symbol_sell='USDT', symbol_buy='BNB', **kwargs):
        """

        :param starting_budget: amount of money that bot starts
        :param symbol_sell: is a ticker symbol of currency being used as standard (usually USDT)
        :param symbol_buy: is a ticker symbol being exchanged by default is BNB
        :param max_steps: after max steps is stored in list steps are stored in appendable text file,
        this should contain all the information that should be needed to replicate the results
        :param data_entry_size: after max data entry is surpassed data_entry is cleared

         , data_entry_size=1, simulation=True, starting_investment_value=1, max_steps=100, save_steps_location="steps.txt"
        """


        self.symbol_sell = symbol_sell
        self.symbol_buy = symbol_buy

        self.starting_budget = starting_budget
        self.current_budget = starting_budget

        self.current_investment = 0
        self.investment_value = 1
        self.simulation = simulation
        if 'starting_investment_value' in kwargs and self.simulation:
            self.investment_value = kwargs['starting_investment_value']


        self.save_steps_location = 'steps.txt'
        if 'save_steps_location' in kwargs:
            self.save_steps_location = kwargs['save_steps_location']

        # after max steps is passed it stores the data in a file and clears the steps list
        self.current_steps = 0
        self.max_steps = 100
        if 'max_steps' in kwargs:
            self.max_steps = kwargs['max_steps']

        # data entry is a list stored of all the previous entries and can be used for all the different strategies
        self.data_entry = []

        # this variable determines how much data_entry should be in a list
        self.data_entry_size = 1
        if 'data_entry_size' in kwargs:
            self.data_entry_size = kwargs['data_entry_size']

        self.fee = 0
        if 'fee' in kwargs:
            self.fee = kwargs['fee']

        # after strategy executes a step it stores all information in this list
        self.steps = []

        self.current_step = None

        # Binance properties
        self.key_path = ''
        self.DRY_RUN = False
        self.client = None

    def load_binance_data(self, default=True,file_name='default', path="", **kwargs):
        '''
        Loads all data from json file
        '''
        # Load JSON from a file
        if default:
            self.simulation = False
            self.DRY_RUN = False
            k = get_key_linux()
            self.client = Client(k['api_key'], k['api_secret'])
        else:
            with open(os.path.join(path, file_name+".json"), "r") as f:
                data = json.load(f)

            print(data)
            #TODO: add custom data load

    def data_enter(self,data):
        if self.data_entry_size == len(self.data_entry):
            self.data_entry.pop(0)
            self.data_entry.append(data)
            return True
        else:
            self.data_entry.append(data)
            return False

    def data_reset(self):
        self.data_entry.clear()

    def save_step(self):
        if self.current_steps >= self.max_steps:
            self.current_steps = 0
            self.store_steps()
            self.steps = []

    def store_steps(self):
        with open(self.save_steps_location, "a") as f:
            for s in self.steps:
                f.write(s.print())

    def update_investment(self, new_investment_value, price_type = 'close'):
        new_value = 0
        #print(new_investment_value)
        if isinstance(new_investment_value, (int, float)):
            new_value = new_investment_value
        elif isinstance(new_investment_value, dict):
            new_value = new_investment_value[price_type]
        else:
            print("It's something else")
        #print(new_value)
        self.current_investment += self.current_investment * (new_value-self.investment_value)/ self.investment_value
        self.investment_value = new_value

    def _symbol_filters(self, symbol):
        info = self.client.get_symbol_info(symbol)
        f = {i["filterType"]: i for i in info["filters"]}
        step = float((f.get("MARKET_LOT_SIZE") or f.get("LOT_SIZE"))["stepSize"])
        mn = f.get("MIN_NOTIONAL") or f.get("NOTIONAL")
        min_notional = float(mn.get("minNotional") or mn.get("notional"))
        return step, min_notional

    def buy_binance_gpt(self, usdt_amount: float):
        """
        Spend a fixed USDT amount (e.g. 10 USDT) to buy the quote asset in self.symbol_buy (e.g. BTCUSDT).
        """
        try:
            balance = float((self.client.get_asset_balance(asset="USDT") or {}).get("free", 0) or 0)

            if balance < usdt_amount:
                return print(f"[SKIP] Not enough USDT. Need {usdt_amount}, have {balance}")

            if self.DRY_RUN:
                print(f"[DRY] BUY {self.symbol_buy} for {usdt_amount} USDT")
                return

            # Validate without executing a fill
            self.client.create_test_order(
                symbol=self.symbol_buy,
                side="BUY",
                type="MARKET",
                quoteOrderQty=str(usdt_amount),
            )

            # Execute real order
            resp = self.client.create_order(
                symbol=self.symbol_buy,
                side="BUY",
                type="MARKET",
                quoteOrderQty=str(usdt_amount),
            )

            print(f"[OK] BUY {self.symbol_buy} orderId={resp['orderId']} ~{usdt_amount} USDT")

            spent = float(resp.get("cummulativeQuoteQty", 0))
            bought = float(resp.get("executedQty", 0))

            print(f"[INFO] Spent {spent:.2f} USDT and bought {bought} {self.symbol_buy.replace('USDT', '')}")

        except BinanceAPIException as e:
            print("[ERR] BUY", e.code, e.message)

    def buy_binance(self, usdt_amount: float):
        try:
            resp = self.client.create_order(
                symbol=self.symbol_buy,
                side="BUY",
                type="MARKET",
                quoteOrderQty=str(usdt_amount),
            )
            spent = float(resp.get("cummulativeQuoteQty", 0))
            self.buy(spent)
            return spent
        except BinanceAPIException:
            print("BUY error")
            return 0.0

    def buy(self, amount, has_fee = False):
        """
        :param amount:
        :return:
        """
        fee = 0
        if has_fee:
            fee = self.fee
        if self.current_budget < amount:
            self.current_investment += self.current_budget*(1-fee)
            self.current_budget = 0

        else:
            self.current_investment += amount*(1-fee)
            self.current_budget -= amount

    def sell_all_binance_gpt(self):
        """
        Sell 100% of asset for self.symbol_buy (e.g., 'BTCUSDT') if balance > 0.
        Uses Decimal-safe rounding to LOT_SIZE and checks MIN_NOTIONAL.
        """
        try:
            symbol = self.symbol_buy
            asset = symbol.replace("USDT", "")  # adjust if you also use BUSD/USDC etc.

            # --- balances ---
            bal = Decimal(str((self.client.get_asset_balance(asset=asset) or {}).get("free", 0) or 0))
            if bal <= 0:
                return print(f"[SKIP] No {asset} to sell (balance={bal})")

            # --- symbol filters ---
            info = self.client.get_symbol_info(symbol)
            if not info:
                return print(f"[ERR] No symbol info for {symbol}")

            step_size = None
            min_notional = None

            for f in info.get("filters", []):
                if f.get("filterType") == "LOT_SIZE":
                    step_size = Decimal(str(f.get("stepSize")))
                elif f.get("filterType") in ("MIN_NOTIONAL", "NOTIONAL"):
                    # binance variants: MIN_NOTIONAL or NOTIONAL (for some markets)
                    mn = f.get("minNotional") or f.get("notional")
                    if mn is not None:
                        min_notional = Decimal(str(mn))

            if step_size is None or step_size <= 0:
                return print(f"[ERR] Invalid LOT_SIZE stepSize for {symbol}: {step_size}")

            if min_notional is None:
                # Fallback if the exchange doesn’t report MIN_NOTIONAL (rare on spot)
                min_notional = Decimal("0")

            # --- latest price for notional checks ---
            price = Decimal(str(self.client.get_symbol_ticker(symbol=symbol)["price"]))

            # --- target qty: 100% minus tiny dust to avoid precision rejects ---
            target = bal * Decimal("0.999")

            # --- Decimal-safe round-down to step_size (equivalent to binance.helpers.round_step_size) ---
            # qty = floor(target / step_size) * step_size
            qty = (target // step_size) * step_size

            if qty <= 0:
                return print(f"[SKIP] Qty rounds to 0 (bal={bal}, step={step_size})")

            notional = qty * price
            if notional < min_notional:
                return print(f"[SKIP] Notional {notional:.8f} < min_notional {min_notional} for {symbol}")

            if self.DRY_RUN:
                return print(f"[DRY] SELL ALL {qty} {asset} ({symbol}) ≈ {notional:.2f} USDT @ {price:.2f}")

            # test first
            self.client.create_test_order(symbol=symbol, side="SELL", type="MARKET", quantity=str(qty))
            # then real
            resp = self.client.create_order(symbol=symbol, side="SELL", type="MARKET", quantity=str(qty))
            print(f"[OK] SELL ALL orderId={resp['orderId']} qty={qty} {asset} ≈ {notional:.2f} USDT @ {price:.2f}")

        except BinanceAPIException as e:
            print("[ERR] SELL_ALL", e.code, e.message)
        except Exception as e:
            # Helpful debug if stepSize/minNotional parsing goes wrong
            print(f"[ERR] SELL_ALL unexpected: {e}")

    def sell_binance(self, usdt_amount: float) -> float:
        try:
            symbol = self.symbol_buy
            asset = symbol.replace("USDT", "")
            price = float(self.client.get_symbol_ticker(symbol=symbol)["price"])

            info = self.client.get_symbol_info(symbol)
            step = None
            min_notional = 0.0
            for f in info.get("filters", []):
                t = f.get("filterType")
                if t == "LOT_SIZE":
                    step = float(f.get("stepSize", 0))
                elif t in ("MIN_NOTIONAL", "NOTIONAL"):
                    mn = f.get("minNotional") or f.get("notional")
                    if mn is not None:
                        min_notional = float(mn)
            if not step or step <= 0:
                return 0.0
            if usdt_amount < min_notional:
                return 0.0

            qty_raw = usdt_amount / price
            qty = floor(qty_raw / step) * step
            if qty <= 0:
                return 0.0

            bal = float((self.client.get_asset_balance(asset=asset) or {}).get("free", 0) or 0)
            if bal < qty:
                qty = floor(bal / step) * step
            if qty <= 0:
                return 0.0

            self.client.create_test_order(symbol=symbol, side="SELL", type="MARKET", quantity=str(qty))
            resp = self.client.create_order(symbol=symbol, side="SELL", type="MARKET", quantity=str(qty))
            sold = float(resp.get("cummulativeQuoteQty", 0.0))
            self.sell(sold)
            return sold
        except BinanceAPIException:
            print("SELL error binance")
            return 0.0
        except Exception:
            print("SELL error")
            return 0.0


    def sell(self, amount, has_fee = False):
        fee = 0
        if has_fee:
            fee = self.fee
        if self.current_investment < amount:
            self.current_budget += self.current_investment*(1-fee)
            self.current_investment = 0
        else:
            self.current_budget += amount * (1-fee)
            self.current_investment -= amount

    @abstractmethod
    def optimize(self, simulation_data, **kwargs):
        """
        This function reparametrize all the values for all the bots
        that use strategies that require updates based on data
        :return:
        """
        pass

    @abstractmethod
    def strategy(self):
        """

        :return:
        """
        pass

    def execute(self, data, new_investment_value):
        self.update_investment(new_investment_value)
        if self.data_enter(data):
            self.strategy()
        self.save_step()






def main():
    #starting_budget, symbol_sell='USDT', symbol_buy='BNBUSDT', data_entry_size=1, max_steps=100)
    #test = BotBase(100)
    pass



if __name__ == '__main__':
    main()
