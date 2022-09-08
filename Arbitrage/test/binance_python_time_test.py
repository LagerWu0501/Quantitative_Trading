import pandas as pd
import numpy as np
from binance.client import Client

client1 = Client()
client2 = Client()
client3 = Client()
symbols = ["ETHUSDT", "ETHBTC", "BTCUSDT"]
FTX_maker_charge = 0.001
unit = 100

BTC_Storage = 0
ETH_Storage = 0
USDT_Storage = 100
i = 0
while True:
    FTX_orders = client1.get_order_book(symbol=symbols[0])
    FTX_orders = client2.get_order_book(symbol=symbols[1])
    FTX_orders = client3.get_order_book(symbol=symbols[2])
    i += 1
    if (i % 100 == 99):
        print(i)
    if (i == 1200):
        break