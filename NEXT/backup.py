import pandas as pd
import ccxt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates


# Set up the trading parameters
# symbol = 'ETH/USDT'  # Use the trading pair you are interested in
symbol = 'ETH/USDT'  # Use the trading pair you are interested in
timeframe = '1h'    # Use the desired timeframe
volume = 0.5        # Volume of the trade

# Initialize the exchange (Assuming Binance in this example)
exchange = ccxt.kucoin()

# Fetch historical data
def fetch_historical_data(symbol, timeframe, limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    # df.to_csv('./Data/ETHUSDT_100_1h.csv')
    return df

# Calculate moving averages
def calculate_moving_averages(df, short_window, long_window):
    df['ma_short'] = df['close'].rolling(window=short_window).mean()
    df['ma_long'] = df['close'].rolling(window=long_window).mean()
    return df

# Identify buy and sell signals
def identify_signals(df):
    signals = pd.DataFrame(index=df.index)
    signals['buy_signal'] = (df['ma_short'] > df['ma_long']) & (df['ma_short'].shift(1) <= df['ma_long'].shift(1))
    signals['sell_signal'] = (df['ma_short'] < df['ma_long']) & (df['ma_short'].shift(1) >= df['ma_long'].shift(1))
    return signals

# Plot price and moving averages
# Plot price and moving averages
def plot_price_and_averages(i):
    historical_data = fetch_historical_data(symbol, timeframe)
    historical_data = calculate_moving_averages(historical_data, 12, 26)
    signals = identify_signals(historical_data)

    plt.clf()  # Clear the previous plot
    plt.plot(historical_data.index, historical_data['close'], label='Price', color='blue')
    plt.plot(historical_data.index, historical_data['ma_short'], label='Short MA (10)', color='orange')
    plt.plot(historical_data.index, historical_data['ma_long'], label='Long MA (30)', color='green')

    # Plot Buy signals
    plt.scatter(signals[signals['buy_signal']].index, historical_data['close'][signals['buy_signal']], marker='^', color='g', label='Buy Signal')

    # Plot Sell signals
    plt.scatter(signals[signals['sell_signal']].index, historical_data['close'][signals['sell_signal']], marker='v', color='r', label='Sell Signal')

    plt.title('Price and Moving Averages with Buy/Sell Signals')
    plt.xlabel('Time')
    plt.ylabel('Price')

    # Format x-axis to display date and time
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))

    plt.legend()
    plt.grid(True)

# Main function
def main():
    ani = FuncAnimation(plt.gcf(), plot_price_and_averages, interval=3000)  # Update plot every 3 seconds
    plt.show()

if __name__ == "__main__":
    main()
