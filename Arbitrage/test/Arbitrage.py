import pandas as pd
import numpy as np
from binance.client import Client
from huobi.linear_swap.rest.account import Account
from huobi.linear_swap.rest.market import Market
from huobi.linear_swap.rest.order import Order

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None 
import os
import sys


Binance = {"API": "ojaWM7JF5nib3nY9hpiTIM9RZDTmVWIW5k5Z4HrY11CksrN18IJuJrP42WSed2X4",
           "Secret": "qkqY8QG9xiYQCvtctBBHhFqnUvz9mC1RiAxiSkU6zkTX3RisRwFc3KRINPWn91bz"}

Huobi = {"API": "cc5417d1-d6f5a369-cdgs9k03f3-1916a",
         "Secret": "c3680fc5-19f9569d-1e6fcce3-c60a0"}

FTX = {"API": "7DS8r5ipITuiR81i9Nov_Fi8jjxujDFaMWZvLW2_",
         "Secret": "gaHIllTYJEXqX8G3gUvgmIRE-WzL36rfHmBmpc-E"}
         
Bybit = {"API": "NUxyoWG4BHAb7LTnxD", 
         "Secret": "ndCqe0JoQxXIyyZ5ptSuQjlKOpmLDxlJMobo"}


Binance_client = Client(Binance["API"], Binance["Secret"])
Huobi_client = Account(Huobi["API"], Huobi["Secret"])
Huobi_market = Market()


# Bi_watch_list = ["BTCUSDT", "ETHUSDT", "AVAXUSDT", "LTCUSDT", "ADAUSDT"]
# Bi_watch_list = ["ETHUSDT", "BTCUSDT", "AVAXUSDT", "LTCUSDT", "ADAUSDT"]
Bi_watch_list = ["AVAXUSDT"]
# Huo_watch_list = [{"contract_code": "btc-usdt"}, {"contract_code": "eth-usdt"}, {"contract_code": "avax-usdt"}, {"contract_code": "ltc-usdt"}, {"contract_code": "ada-usdt"}]
# Huo_watch_list = [{"contract_code": "eth-usdt"}, {"contract_code": "btc-usdt"}, {"contract_code": "avax-usdt"}, {"contract_code": "ltc-usdt"}, {"contract_code": "ada-usdt"}]
Huo_watch_list = [{"contract_code": "avax-usdt"}]
for j in range(len(Bi_watch_list)):
    print(Bi_watch_list[j])
    count = 0
    profit = 0
    res = []
    i = 0
    while True:
        i += 1
        # print(i)
        # for r in res:
        #     print(r)
        # sys.stdout.flush()
        Bi = Binance_client.get_orderbook_ticker(symbol = Bi_watch_list[j])
        Huo = Huobi_market.get_batch_merged(Huo_watch_list[j])
        Bi_bid = float(Bi["bidPrice"])
        Huo_bid = Huo["ticks"][0]["bid"][0]
        Bi_ask = float(Bi["askPrice"])
        Huo_ask = Huo["ticks"][0]["ask"][0]
        # if (Bi_bid - Huo_ask > 0):
        #     print("Buy Huo, sell Bi: ", "sell", Bi_bid, "buy", Huo_ask)
        # if (Huo_bid - Bi_ask > 0):
        #     print("Sell Huo, buy Bi: ", "buy", Bi_bid, "sell", Huo_ask)
        Huo_charge = 0.000
        Bi_charge = 0.000
        if (Bi_bid - Huo_ask > Bi_bid * Bi_charge + Huo_ask * Huo_charge):
            count += 1
            print(">>", i, "<<", "Buy Huo, sell Bi: ", "sell", Bi_bid, "buy", Huo_ask, "profit", profit, "volume", float(Bi["bidQty"]) * Bi_bid, Huo["ticks"][0]["ask"][1])
            profit += Bi_bid - Huo_ask - Bi_bid * Bi_charge - Huo_ask * Huo_charge
            # res.append([">> Buy Huo, sell Bi: ", "sell", Bi_bid, "buy", Huo_ask, "profit", profit])
        if (Huo_bid - Bi_ask > Bi_ask * Bi_charge + Huo_bid * Huo_charge):
            count += 1
            print(">>", i , "<<", "Sell Huo, buy Bi: ", "buy", Bi_bid, "sell", Huo_ask, "profit", profit, "volume", float(Bi["askQty"]) * Bi_ask, Huo["ticks"][0]["bid"][1])
            profit += Huo_bid - Bi_ask - Bi_ask * Bi_charge - Huo_bid * Huo_charge  
            # res.append([">> Sell Huo, buy Bi: ", "buy", Bi_bid, "sell", Huo_ask, "profit", profit])
        # os.system("clear")
    # print("Arbitrage count:", count, "profit:", profit)
