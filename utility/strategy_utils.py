import math

import numpy as np
import pandas as pd
from Example.Binance.utility import append_to_file

def bid_ask_spread_model(prices, inventory, kappa = 0.5, time_remaining = 1, risk_aversion=0.1, prices_len=30):
    """
    :param prices: contains bid and ask values (for testing high and low), and excpects at least prices_len last values
    :param inventory: determines weather the function bought or sold // set it to zero should fluctuate depending on the market
    :param kappa: Liquidity parameter controlling order arrival rate (higher = more liquid market).
    :param time_remaining: Remaining time until the trading horizon ends (T - t).
        Usually measured in seconds, minutes, or fraction of day depending on the setup.
    param: risk_aversion:  Trader’s risk aversion parameter (γ). Higher values = more conservative.
    param: prices_len: defines the length of list expected for prices list
    :return: retunrns -1 to sell, 1 to buy, 0 to hold
    """

    if len(prices) < prices_len:
        return "Not enough data to compute standard deviation."

    mid_values = []

    for p in prices:
        mid_values.append((p['bid'] + p['ask'])/2)

    sigma = np.std(mid_values,ddof=1)

    reservation_price = mid_values[-1] - inventory * risk_aversion * (sigma ** 2) * time_remaining

    # === STEP 2: Optimal spread ===
    # Spread is widened when risk aversion is high, volatility is high, or time horizon is long.
    # The formula comes from solving an HJB equation under Poisson order arrivals.
    spread = (1 / risk_aversion) * math.log(1 + (risk_aversion / kappa)) \
             + 0.5 * risk_aversion * (sigma ** 2) * time_remaining

    # === STEP 3: Final bid and ask quotes ===
    bid_price = reservation_price - spread / 2
    ask_price = reservation_price + spread / 2

    #append_to_file("bid {} ask {} spread {} kappa {}".format(bid_price, ask_price, spread, kappa),"DATA_DUMP/buy.txt")
    return bid_price, ask_price, mid_values[-1]



def stock_advice_int(prices, time_interval=1, price_len=3 ,fee = 0):
    if len(prices) < price_len:
        return "Not enough data to compute derivatives."

    # Convert the prices to a NumPy array for easier calculations
    prices = np.array(prices)
    #weiight1 = 0.5
    #weiight2 = 0.5
    #scailing_factor = 10
    # Calculate the first derivative (rate of change)
    first_derivative = np.diff(prices) / time_interval

    # Calculate the second derivative (acceleration of the rate of change)
    second_derivative = np.diff(first_derivative) / time_interval

    # Analyze the most recent first and second derivatives
    latest_first_derivative = first_derivative[-1]
    latest_second_derivative = second_derivative[-1] if len(second_derivative) > 0 else 0
    #relative_change = latest_first_derivative/prices[-1]
    #relative_change_of_derivative =latest_second_derivative/latest_first_derivative

    # Provide advice based on the derivatives
    if latest_first_derivative > 0 and latest_second_derivative > 0:
        advice = 1 # Buy
    elif latest_first_derivative < 0 and latest_second_derivative < 0:
        advice = -1 # Sell
    else:
        advice = 0 # Hold

    return advice
        #'first_derivative': latest_first_derivative,
        #'second_derivative': latest_first_derivative,
        #'relative quantity':(weiight1 * relative_change + weiight2 * relative_change_of_derivative)*10,
        #'advice': advice



def bollinger_signal_int(dict, window=20, num_std=2) -> int:
    closes = dict['close']
    n = len(closes)

    if n < window:
        return 0  # Not enough data
    # Izracunavanje moving average i standard deviation
    moving_averages = [sum(closes[i - window:i]) / window for i in range(window, n + 1)]

    std_devs = [((sum((closes[k - window:k] - ma) ** 2) / window) ** 0.5) for ma in moving_averages]

    #izracunavanje traka
    upper_bands = [ma + num_std * std for ma, std in zip(moving_averages, std_devs)]
    lower_bands = [ma - num_std * std for ma, std in zip(moving_averages, std_devs)]

    if closes[-1] < lower_bands[-1]:
        return 1  # Buy
    elif closes[-1] > upper_bands[-1]:
        return -1  # Sell
    else:
        return 0  # Hold


def macd_signal_int(closes, short=12, long=26, signal=9) -> int:
    n = len(closes)

    if n < long:
        return 0  # Not enough data

    # Izracunati exponencijalni poketni rosek
    ema12 = [sum(closes[:short]) / short]  # 12 pokretni prosek
    for price in closes[1:]:
        ema12.append((price * (2 / (short + 1))) + (ema12[-1] * (1 - (2 / (short + 1)))))

    ema26 = [sum(closes[:long]) / long]  # 26 pokretni prosek
    for price in closes[1:]:
        ema26.append((price * (2 / (long + 1))) + (ema26[-1] * (1 - (2 / (long + 1)))))

    # MACD i Signal Line
    macd = [e12 - e26 for e12, e26 in zip(ema12, ema26)]
    signal_line = [sum(macd[:signal]) / signal]  # pocetni Signal Line
    for macd_value in macd[1:]:
        signal_line.append((macd_value * (2 / (signal + 1))) + (signal_line[-1] * (1 - (2 / (signal + 1)))))


    # Latest signal
    if abs((macd[-1] - signal_line[-1]) / macd[-1]) < 0.05:
        return 0
    elif macd[-1] < signal_line[-1]:
        return 1  # Buy
    elif macd[-1] > signal_line[-1]:
        return -1  # Sell
    else:
        return 0  # Hold


def random_control_strategy_multiple(df: pd.DataFrame, start_indices: np.ndarray) -> np.ndarray:
    """
    Generise radnom niz duzine niza cena vrednosti 0,1,-1
    """
    print(df)
    all_signals = []

    for start_index in start_indices:
        length = len(df) - start_index
        random_signals = np.random.choice([1, -1, 0], size=length)
        all_signals.extend(random_signals)

    return np.array(all_signals)


if __name__ == '__main__':
    prices = [100, 102, 105, 103, 106, 110]
    result = stock_advice_int(prices)
    print(result)

    # Simulated BTC price data
    dates = pd.date_range(end=pd.Timestamp.today(), periods=100)
    prices = np.cumsum(np.random.randn(100)) + 30000
    df = pd.DataFrame({'date': dates, 'close': prices}).set_index('date')

    # Assume strategy triggered buys and sells at indices [30, 50, 75]
    trigger_indices = np.array([30, 50, 75])

    # Generate random decisions from those trigger points
    random_signals = random_control_strategy_multiple(df, trigger_indices)

    # Print the generated random signals
    print(f"Random strategija signali od {trigger_indices} do:\n", random_signals)