import  get_signal_MovingAverage as st1
import pandas as pd
from Funcations import * 

def strategy1(dataF):
    dataF = dataF.dropna()
    dataF = dataF.reset_index()
    if 'index' in dataF.columns:
        dataF.drop('index',axis = 1,inplace=True)
        
    short_window = 12
    long_window = 26
    dataF['ma_short'] = dataF['Close'].rolling(window=short_window).mean()
    dataF['ma_long'] = dataF['Close'].rolling(window=long_window).mean()
    signals = dataF
    add_rsi(dataF)

    signals['ST1_Buy_Signal'] = np.where((dataF['ma_short'] > dataF['ma_long']) & (dataF['ma_short'].shift(1) <= dataF['ma_long'].shift(1)), 1, 0)
    signals['ST1_Sell_Signal'] = np.where((dataF['ma_short'] < dataF['ma_long']) & (dataF['ma_short'].shift(1) >= dataF['ma_long'].shift(1)), 1, 0)

    return signals


