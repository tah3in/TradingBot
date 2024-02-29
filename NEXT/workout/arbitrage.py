import ccxt
import time

exchange_one = ccxt.binance() #binance
exchange_two = ccxt.kucoin()

def main():
    price_ex_one = exchange_one.fetch_ticker('DOGE/USDT')['last']
    price_ex_two = exchange_two.fetch_ticker('DOGE/USDT')['last']

    arbitrage = price_ex_two - price_ex_one

    if float(arbitrage) > 0:
        print('arbitrage')
    else:
        print('no arbitrage')


if __name__ == "__main__":
    main()