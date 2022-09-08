#跑出來的數字很奇怪，BTC 歐印, 12HR的報酬只有幾十%，怪怪的


import pandas as pd
import numpy as np
from binance.client import Client
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None 
class Strategy():
    def __init__(self, client, symbols, timeframe, startdate = "2 year ago UTC", service_charge = 0.00075, money = 1000, storage = 0):
        self.client = client
        self.symbols = symbols
        self.timeframe = timeframe
        self.startdate = startdate
        self.service_charge = service_charge
        self.start_money = [money] * len(symbols)
        self.start_storage = [storage] * len(symbols)

        self.all_data = []
        for coin in symbols:
            bars = client.get_historical_klines(symbol=f'{coin}USDT',interval=timeframe,start_str=self.startdate)
            test_df = pd.DataFrame(bars[:],columns=["timestamp","open","high","low","close","volume", "close_time", "quote_asset_volume", "number_of_trade", "TBB", "TBQ", "ignore"])
            test_df["date"]=pd.to_datetime(test_df["timestamp"],unit="ms").astype(str)
            test_df = test_df.drop(["timestamp", "close_time", "quote_asset_volume", "number_of_trade", "TBB", "TBQ", "ignore"], axis=1)
            test_df["open"] = pd.to_numeric(test_df["open"])
            test_df["high"] = pd.to_numeric(test_df["high"])
            test_df["low"] = pd.to_numeric(test_df["low"])
            test_df["close"] = pd.to_numeric(test_df["close"])
            test_df["volume"] = pd.to_numeric(test_df["volume"])
            test_df["signal"] = ["None"] * len(test_df)
            self.all_data.append(test_df)

        self.profit = [0] * len(symbols)
    def print(self):
        print("Time frame", self.timeframe)
        print("Start from", self.startdate)

        for i in range(len(self.symbols)):
            print("=============")
            print(self.symbols[i], self.profit[i])

        print("=============")
        print("average", sum(self.profit) / len(self.profit))

    def decide_action(self):
        pass

    def back_test(self, type = "all in", fixed_money = None):
        for i in range(len(self.symbols)):
            money = self.start_money[i]
            storage = self.start_storage[i]
            for j in range(len(self.all_data[i])):
                if (self.all_data[i]["signal"][j] == "buy"):
                    if (type == "all in"):
                        if (storage < 0):
                            money -= -1 * storage * self.all_data[i]["close"][j]
                            storage = 0
                        storage += money / self.all_data[i]["close"][j] 
                        money = 0
                    else:
                        if (storage > 0):
                            money -= -1 * storage * self.all_data[i]["close"][j]
                            storage = 0
                        storage += fixed_money[i] / self.all_data[i]["close"][j] 
                        money -= fixed_money[i]
                elif (self.all_data[i]["signal"][j] == "sell"):
                    if (type == "all in"):
                        if (storage > 0):
                            money += storage * self.all_data[i]["close"][j]
                            storage = 0
                        storage -= money / self.all_data[i]["close"][j] 
                        money += money
                    else:
                        if (storage > 0):
                            money += storage * self.all_data[i]["close"][j]
                            storage = 0
                        storage -= fixed_money[i] / self.all_data[i]["close"][j] 
                        money += fixed_money[i]
            self.profit[i] = (money + storage * self.all_data[i]["close"][len(self.all_data[i]) - 1]) / self.start_money[i]
class MACD(Strategy):
    def decide_action(self, smooth = 2, short_period = 12, long_period = 26, xMACD_day = 9, stable_offset = 150): #stable_offset: 前面幾根不列入收益損計算，只用來跑K棒
        for i in range(len(self.all_data)):
            self.all_data[i]["short EMA"] = self.all_data[i]["close"].copy()
            self.all_data[i]["long EMA"] = self.all_data[i]["close"].copy()


            for j in range(1, len(self.all_data[i])):
                self.all_data[i]["short EMA"][j] = self.all_data[i]["short EMA"][j] * smooth / (short_period + 1) + self.all_data[i]["short EMA"][j - 1] * (1 - smooth / (short_period + 1))
                self.all_data[i]["long EMA"][j] = self.all_data[i]["long EMA"][j] * smooth / (long_period + 1) + self.all_data[i]["long EMA"][j - 1] * (1 - smooth / (long_period + 1))
            self.all_data[i]["DIF"] = self.all_data[i]["short EMA"] - self.all_data[i]["long EMA"]
            self.all_data[i]["xMACD"] = self.all_data[i]["DIF"].copy()
            for j in range(1, len(self.all_data[i])):
                self.all_data[i]['xMACD'][j] =  self.all_data[i]["DIF"][j] * smooth / (xMACD_day + 1) + self.all_data[i]["xMACD"][j - 1] * (1 - smooth / (xMACD_day + 1))
            #做平均K線
            for j in range(stable_offset, len(self.all_data[i])):
                if (self.all_data[i]["DIF"][j - 1] - self.all_data[i]["xMACD"][j - 1] > 0) and self.all_data[i]["DIF"][j - 2] - self.all_data[i]["xMACD"][j - 2] < 0:
                    self.all_data[i]["signal"][j] = "buy"
                elif (self.all_data[i]["DIF"][j - 1] - self.all_data[i]["xMACD"][j - 1] < 0) and self.all_data[i]["DIF"][j - 2] - self.all_data[i]["xMACD"][j - 2] > 0:
                    self.all_data[i]["signal"][j] = "sell"
profits = []
count = 0
target_symbol = ["BTC"]
time_frames = ["1d", "12h", "6h", "4h", "2h", "1h"]
time_frames = ["12h"]
start_str = "1 year ago UTC"
client = Client("Fmrs52YBNKoZteqjPdRZaykPWxTvQfnGiEAIDXLvUZKKXD4v86GT9E5IyutPVmHC", "Nm1AvQxIiZ6wgWeso5tMDa5SzyvOssOrJHU5Hdi9tKxOwb2XYenHZCsyQtjdBib1")
res = []
for timeframe in time_frames:
    for short_period in range(5, 25):
        for long_period in range(80,120):
            for xMACD_day in range(5,10):
                a = MACD(client, target_symbol, timeframe, start_str)
                a.decide_action(short_period=short_period, long_period=long_period, xMACD_day = xMACD_day)
                a.back_test(type="all in")
                res.append([short_period, long_period, timeframe, sum(a.profit) / len(a.profit)])
                print("short", short_period, "long", long_period, "timeframe", timeframe, "average", sum(a.profit) / len(a.profit))
a.print()
