import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import os ,sys
from Funcations import * 
import Offline.MarketSimulation as MS
from  get_signal_MovingAverage import strategy1

os.system('cls')

def plot_chart(ax):
    global data
    ax.clear()
    ax.plot(data['Datetime'], data['Close'], label='Close Price', color='blue')
    buy_signals = data[data['ST2_Buy_Signal'] == 1]
    sell_signals = data[data['ST2_Sell_Signal'] == 1]
    ax.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='Buy Signal')
    ax.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='Sell Signal')

    ax.set_title('Candlestick Chart with Signals')
    ax.legend()
    plt.show()



def animate(frame, ax):
    global data
    print("Updating...")
    df = ReceivingInformation(ExchangeName, symbol, timeframe, 1)
    df = fixshape(df)

    data = pd.concat([data, df], ignore_index=True)
    
    dataF = strategy2(data)
    # dataF = strategy1(dataF)

    result = BackTest(dataF,'Strategy 2')

    print(result.ShowResult())


    #for watching BackTest
    time.sleep(3)

    # Update the plot
    plot_chart(ax)


if __name__ == '__main__':
    ExchangeName = 'kucoin'
    symbol = 'BTC/USDT'
    timeframe = '1h'
    limit = 200
    data = ReceivingInformation(ExchangeName, symbol, timeframe, limit)
    path = f"./Save/{symbol.replace('/','')}_{limit}_{timeframe}.csv"
    data.to_csv(path)
   

    data = fixshape(data)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create animation
    ani = FuncAnimation(fig, animate, fargs=(ax,), interval=int(TimeConvert(timeframe)*1000))   #interval -> (milisecound)

    plt.show()
