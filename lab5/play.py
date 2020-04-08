import pandas as pd
import numpy as nd

tips = "./data/tips.csv"

tips = pd.read_csv(tips)
print(tips.describe())

data2 = tips.set_index(['day', 'time'])
print(data2.head())