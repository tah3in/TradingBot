import pandas as pd
import numpy as np
from datetime import datetime
import ccxt

#_________________________________________________________________________________________________________________________
# Calculation of several indicators

def add_macd(df,short_window=12, long_window=26,signal_window=9):
    df['Short_MA'] = df['Close'].rolling(window=short_window).mean()
    df['Long_MA'] = df['Close'].rolling(window=long_window).mean()
    df['MACD'] = df['Short_MA'] - df['Long_MA']
    df['Signal_Line'] = df['MACD'].rolling(window=signal_window).mean()

def add_rsi(df,rsi_window=14):
    close_price = df['Close']
    daily_return = close_price.diff()
    gain = daily_return.where(daily_return > 0, 0)
    loss = -daily_return.where(daily_return < 0, 0)
    average_gain = gain.rolling(window=rsi_window, min_periods=1).mean()
    average_loss = loss.rolling(window=rsi_window, min_periods=1).mean()
    rs = average_gain / average_loss
    df['RSI'] = 100 - (100 / (1 + rs))

def add_BollingerBands(df,bb_window=20):
    df['Upper_Band'] = df['Close'].rolling(window=bb_window).mean() + 2 * df['Close'].rolling(window=bb_window).std()
    df['Lower_Band'] = df['Close'].rolling(window=bb_window).mean() - 2 * df['Close'].rolling(window=bb_window).std()


#_________________________________________________________________________________________________________________________
#strategy 1
def strategy1(dataF):
    # dataF = dataF.dropna()
    # dataF = dataF.reset_index()
    # if 'index' in dataF.columns:
    #     dataF.drop('index',axis = 1,inplace=True)
        
    short_window = 12
    long_window = 26
    dataF['ma_short'] = dataF['Close'].rolling(window=short_window).mean()
    dataF['ma_long'] = dataF['Close'].rolling(window=long_window).mean()
    add_rsi(dataF)

    dataF['ST1_Buy_Signal'] = np.where((dataF['ma_short'] > dataF['ma_long']) & (dataF['ma_short'].shift(1) <= dataF['ma_long'].shift(1)), 1, 0)
    dataF['ST1_Sell_Signal'] = np.where((dataF['ma_short'] < dataF['ma_long']) & (dataF['ma_short'].shift(1) >= dataF['ma_long'].shift(1)), 1, 0)
    dataF = pd.DataFrame(dataF,columns=['Datetime','Open','High','Low','Close',"ST1_Buy_Signal","ST1_Sell_Signal"])
    return dataF

#_________________________________________________________________________________________________________________________
#strategy 2
def strategy2(dataF):
    add_rsi(dataF)
    def strategy2(df):
        open = df.Open.iloc[-1]
        close = df.Close.iloc[-1]
        previous_open = df.Open.iloc[-2]
        previous_close = df.Close.iloc[-2]
        RSI = df.RSI.iloc[-1]
        
        # Bearish Pattern
        if (open>close and 
        previous_open<previous_close and 
        close<previous_open and
        open>=previous_close and RSI>60):
            return 1

        # Bullish Pattern
        elif (open<close and 
            previous_open>previous_close and 
            close>previous_open and
            open<=previous_close and RSI<40):
            return 2
        
        # No clear pattern
        else:
            return 0

    BuySignal = [0]
    SellSignal = [0]

    for i in range(1,len(dataF)):
        df = dataF[i-1:i+1]
        signal = strategy2(df)
        if signal == 1:
            BuySignal.append(1)
            SellSignal.append(0)
        elif signal == 2:
            SellSignal.append(1)
            BuySignal.append(0)
        else:
            SellSignal.append(0)
            BuySignal.append(0)
    #signal_generator(data)
    dataF["ST2_Buy_Signal"] = BuySignal
    dataF["ST2_Sell_Signal"] = SellSignal
    dataF.drop('RSI',axis=1,inplace=True)
    return dataF
#_________________________________________________________________________________________________________________________
#Backtest
class BackTest:
    BadSignal , GoodSignal = 0 , 0 
    def __init__(self,dataF,Strategy,limit_ft=1):
        self.dataF = dataF
        self.limit_ft = limit_ft
        self.Strategy = Strategy.lower()
    def ComparePrices(self,limit_ft):
        TotalSignal = 0 
        BadSignal , GoodSignal = 0 , 0
        if self.Strategy == 'strategy 1' :
            Column_Buy = "ST1_Buy_Signal"
            Column_Sell = "ST1_Sell_Signal"
        elif self.Strategy == 'strategy 2':
            Column_Buy = "ST2_Buy_Signal"
            Column_Sell = "ST2_Sell_Signal"
        dataliBUY = self.dataF[Column_Buy].to_list()
        dataliSELL = self.dataF[Column_Sell].to_list()
        for i in range(0,len(self.dataF["Close"])- limit_ft):
            FuturePrice =0
            CurrentPrice = self.dataF.iloc[i].Close
            FuturePrice=self.dataF.iloc[i+ limit_ft].Close
            if dataliSELL[i] == 1: #Sell
                if FuturePrice < CurrentPrice:
                    GoodSignal += 1
                elif FuturePrice > CurrentPrice:
                    BadSignal +=1
            elif dataliBUY[i] == 1: #Buy
                if FuturePrice > CurrentPrice:
                    GoodSignal += 1
                elif FuturePrice < CurrentPrice:
                    BadSignal +=1
        
        self.GoodSignal = GoodSignal
        self.BadSignal = BadSignal
        for i in range(0,len(self.dataF["Close"])):
            if dataliBUY[i] != 0 or dataliSELL[i] != 0 : 
                TotalSignal+=1   
        if TotalSignal == 0 :
            print("Total signal = 0")
            return
        # print(self.GoodSignal,self.BadSignal)
        return (GoodSignal/TotalSignal)*100
    
    def ShowResult(self):
        best_winrate = 0
        for i in range(0,12):
            if best_winrate < self.ComparePrices(i):
                best_winrate = self.ComparePrices(i)
                best_limit = i
                
        self.ComparePrices(best_limit)
        best_winrate = (self.GoodSignal/(self.GoodSignal+self.BadSignal))*100
        return f"Best Winrate : {best_winrate} \nBest Waiting time : {Get_best_waiting_time(self.dataF,best_limit)}\nGood Signal : {self.GoodSignal} \nBad Signal : {self.BadSignal}"
#_________________________________________________________________________________________________________________________
#ReceivingInformation
def ReceivingInformation(ExchangeName,symbol,timeframe,NumPerviousCandles):
    while(1):
        try:
            exchange = create_exchange(ExchangeName)
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=NumPerviousCandles)
            df = pd.DataFrame(ohlcv, columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Datetime'] = pd.to_datetime(df['Datetime'], unit='ms')
            df['Datetime'] = df['Datetime'].astype(str)
            return df 
        except Exception as e:
            print(f"please wait ... \n{e}")

def fixshape(df):
    if 'ST1_Sell_Signal' in df.columns:
        df['ST1_Buy_Signal'] =0
        df['ST1_Sell_Signal'] =0
        df['ST2_Buy_Signal'] =0
        df['ST2_Sell_Signal'] =0
    return df


#_________________________________________________________________________________________________________________________
#Conversion functions
def TimeConvert(timeframe):
    if "m" in timeframe.lower():
        timeframe = int(timeframe.replace('m',''))*60
    elif "h" in timeframe.lower():
        timeframe = int(timeframe.replace('h',''))*3600
    elif "d" in timeframe.lower():
        timeframe = int(timeframe.replace('d',''))*86400
    return timeframe


def Get_best_waiting_time(dataF,best_limit):
    #differnet between time1 and time2
    if 'Datetime' in dataF.columns:
        time_str1 = dataF.at[2,'Datetime']
        time_str2 = dataF.at[3,'Datetime']
    elif 'Datetime' in dataF.index.name:
        time_str1 = dataF.iloc[2].name    
        time_str2 = dataF.iloc[3].name    

    if type(time_str1) != type("str"):
        time_str1 , time_str2 = str(time_str1) , str(time_str2)
        
    time1 = datetime.strptime(time_str1, '%Y-%m-%d %H:%M:%S') if ' ' in time_str1 else datetime.strptime(time_str1, '%Y-%m-%d')
    time2 = datetime.strptime(time_str2, '%Y-%m-%d') if ' ' not in time_str2 else datetime.strptime(time_str2, '%Y-%m-%d %H:%M:%S')

    # محاسبه تفاوت دو تایم
    time_difference = time2 - time1

    # تبدیل تفاوت به دقیقه
    minutes_difference = time_difference.total_seconds() / 60

    result = best_limit*minutes_difference

    if result>=1440:
        return f"{int(result/1440)} day"
    if result>=60:
        return f"{int(result/60)} hour"
    else:
        return f"{int(result)} minutes"


def create_exchange(ExchangeName = 'kucoin'):
    exchange_dict = {
        'ace': ccxt.ace,
        'alpaca': ccxt.alpaca,
        'ascendex': ccxt.ascendex,
        'bequant': ccxt.bequant,
        'bigone': ccxt.bigone,
        'binance': ccxt.binance,
        'binancecoinm': ccxt.binancecoinm,
        'binanceus': ccxt.binanceus,
        'binanceusdm': ccxt.binanceusdm,
        'bingx': ccxt.bingx,
        'bit2c': ccxt.bit2c,
        'bitbank': ccxt.bitbank,
        'bitbay': ccxt.bitbay,
        'bitbns': ccxt.bitbns,
        'bitcoincom': ccxt.bitcoincom,
        'bitfinex': ccxt.bitfinex,
        'bitfinex2': ccxt.bitfinex2,
        'bitflyer': ccxt.bitflyer,
        'bitforex': ccxt.bitforex,
        'bitget': ccxt.bitget,
        'bithumb': ccxt.bithumb,
        'bitmart': ccxt.bitmart,
        'bitmex': ccxt.bitmex,
        'bitopro': ccxt.bitopro,
        'bitpanda': ccxt.bitpanda,
        'bitrue': ccxt.bitrue,
        'bitso': ccxt.bitso,
        'bitstamp': ccxt.bitstamp,
        'bittrex': ccxt.bittrex,
        'bitvavo': ccxt.bitvavo,
        'bl3p': ccxt.bl3p,
        'blockchaincom': ccxt.blockchaincom,
        'btcalpha': ccxt.btcalpha,
        'btcbox': ccxt.btcbox,
        'btcmarkets': ccxt.btcmarkets,
        'btcturk': ccxt.btcturk,
        'bybit': ccxt.bybit,
        'cex': ccxt.cex,
        'coinbase': ccxt.coinbase,
        'coinbaseprime': ccxt.coinbaseprime,
        'coinbasepro': ccxt.coinbasepro,
        'coincheck': ccxt.coincheck,
        'coinex': ccxt.coinex,
        'coinlist': ccxt.coinlist,
        'coinmate': ccxt.coinmate,
        'coinone': ccxt.coinone,
        'coinsph': ccxt.coinsph,
        'coinspot': ccxt.coinspot,
        'cryptocom': ccxt.cryptocom,
        'currencycom': ccxt.currencycom,
        'delta': ccxt.delta,
        'deribit': ccxt.deribit,
        'digifinex': ccxt.digifinex,
        'exmo': ccxt.exmo,
        'fmfwio': ccxt.fmfwio,
        'gate': ccxt.gate,
        'gateio': ccxt.gateio,
        'gemini': ccxt.gemini,
        'hitbtc': ccxt.hitbtc,
        'hitbtc3': ccxt.hitbtc3,
        'hollaex': ccxt.hollaex,
        'htx': ccxt.htx,
        'huobi': ccxt.huobi,
        'huobijp': ccxt.huobijp,
        'idex': ccxt.idex,
        'independentreserve': ccxt.independentreserve,
        'indodax': ccxt.indodax,
        'kraken': ccxt.kraken,
        'krakenfutures': ccxt.krakenfutures,
        'kucoin': ccxt.kucoin,
        'kucoinfutures': ccxt.kucoinfutures,
        'kuna': ccxt.kuna,
        'latoken': ccxt.latoken,
        'lbank': ccxt.lbank,
        'luno': ccxt.luno,
        'lykke': ccxt.lykke,
        'mercado': ccxt.mercado,
        'mexc': ccxt.mexc,
        'ndax': ccxt.ndax,
        'novadax': ccxt.novadax,
        'oceanex': ccxt.oceanex,
        'okcoin': ccxt.okcoin,
        'okx': ccxt.okx,
        'p2b': ccxt.p2b,
        'paymium': ccxt.paymium,
        'phemex': ccxt.phemex,
        'poloniex': ccxt.poloniex,
        'poloniexfutures': ccxt.poloniexfutures,
        'probit': ccxt.probit,
        'timex': ccxt.timex,
        'tokocrypto': ccxt.tokocrypto,
        'upbit': ccxt.upbit,
        'wavesexchange': ccxt.wavesexchange,
        'wazirx': ccxt.wazirx,
        'whitebit': ccxt.whitebit,
        'woo': ccxt.woo,
        'yobit': ccxt.yobit,
        'zaif': ccxt.zaif,
        'zonda': ccxt.zonda,
    }
    exchange_constructor = exchange_dict.get(ExchangeName, None)

    if exchange_constructor:
        exchange = exchange_constructor()
        return exchange
    else:
        raise ValueError(f"Unknown exchange name: {ExchangeName}")


