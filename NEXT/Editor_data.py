# import pandas as pd



# df = pd.read_csv('./Data/BTCUSD_1500_15M.csv')

# df.drop(columns='signal',inplace=True)

# df.to_csv('./Data/BTCUSD_1500_15M.csv')

# ___________________________________________________________________________________________________

import pandas as pd

# ساخت دیتافریم نمونه
data = {'id': [1, 2, 3],
        'name': ['John', 'Alice', 'Bob'],
        'age': [25, 30, 22]}

df = pd.DataFrame(data)

# نمایش دیتافریم قبل از تغییر
print("DataFrame before the change:")
print(df)

# نمونه ای که می‌خواهیم تغییر دهیم
sample_index = 1  # مثلاً نمونه دوم

# تغییر مقدار در ستون "age"
new_age_value = 32
df.at[sample_index, 'age'] = new_age_value

# یا می‌توانید از loc نیز استفاده کنید:
# df.loc[sample_index, 'age'] = new_age_value

# نمایش دیتافریم پس از تغییر
print("\nDataFrame after the change:")
# ___________________________________________________________________________________________________
print(df)
