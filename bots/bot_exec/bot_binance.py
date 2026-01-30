import time
from binance.client import Client
from Example.Binance.utility.constants import get_key

# Replace with your own Binance API key and secret
key = get_key()
api_key = key['api_key']
api_secret= key['api_secret']

# time interval before function is called in seconds
time_interval = 2


# Initialize the Binance client
client = Client(api_key, api_secret)

# Function to get the Bitcoin price
def get_coin_price(symbol):
    # Get the latest price of Bitcoin (BTC) in USDT (Tether)
    price = client.get_symbol_ticker(symbol=symbol)
    return float(price['price'])



def main():
    #bot =
    try:
        while True:
            btc_price = get_coin_price("BTCUSDT")
            print(f"Current Bitcoin Price: ${btc_price}")
            #
            time.sleep(time_interval)
    except KeyboardInterrupt:
        print("Stopped by user.")

if __name__=="__main__":
    main()