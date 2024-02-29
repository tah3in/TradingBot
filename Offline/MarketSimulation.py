import pandas as pd
import os 


# print(os.getcwd())
path = './Offline/PriceData/BTCUSDT_1500_5M.csv'

nm = 0
df_second_half = pd.DataFrame()

def ReceivingInformation_all(ExchangeName=0, symbol=0, timeframe=0, limit=1):
    global df_second_half
    df = pd.read_csv(path)
    if 'Unnamed: 0' in df.columns:
        df.drop(columns=["Unnamed: 0"],inplace=True)
    total_rows = df.shape[0]
    df_first_half = df.iloc[:total_rows//2, :]
    df_second_half = df.iloc[total_rows//2:, :]

    return df_first_half


def ReceivingInformation(ExchangeName=0, symbol=0, timeframe=0, limit=1):
    global nm
    df = df_second_half
    sample = df.iloc[nm].to_numpy().reshape((1, -1))  # Convert to NumPy array and reshape
    nm+=1
    # Create a new DataFrame with the reshaped data
    sample_df = pd.DataFrame(sample, columns=df.columns)
    if 'Unnamed: 0' in df.columns:
        sample_df.drop(columns=["Unnamed: 0"],inplace=True)


    return sample_df
