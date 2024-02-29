import pandas as pd
from Funcations import *


path = ...

# # FUTURES
# #  2024-01-16 09:30:00  -> 2024-01-19 15:59:00
# path = "./PriceData/FUTURES/GOLD_1560_1M.csv" #GOLD 
# path = "./PriceData/FUTURES/SILVER_5000_1M.csv" #SILVER

# # STOCKS
# #  2024-01-16 09:30:00  -> 2024-01-19 15:59:00
# path = "./PriceData/STOCKS/AAPL_1560_1M.csv" #APPLE 
# path = "./PriceData/STOCKS/META_1560_1M.csv" #META

# # Crypto
# path = "./PriceData/CRYPTO/DOGEUSDT_1000_15M.csv"  #DOGE
path = "./PriceData/CRYPTO/BTCUSDT_1500_15M.csv"   #BTC 15M
# path = "./PriceData/CRYPTO/ETHUSDT_1500_1d.csv"    #ETH
# path = "./PriceData/CRYPTO/BTCUSDT_1500_5M.csv"    #BTC 5M


data = pd.read_csv(path)


dataF = strategy1(data)
dataF = strategy2(dataF)


result = BackTest(dataF,'Strategy 2')

print(result.ShowResult())
