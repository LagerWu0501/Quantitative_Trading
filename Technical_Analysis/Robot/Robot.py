import math
import numpy as np
from Indicators import *
from Strategies import *
from Trading_Offices import *
import json
import time
import datetime


class Robot:
    def __init__(self):
        # trading office
        self.API_key = None
        self.Secret_key = None
        self.myTrading_Office = None
        self.trading_office_Name = None
        self.trading_office_Parameters = None
        self.leverage = 0
        # Robot's records and robot's parameters
        self.OrderRecord = None
        # Strategy setting and parameters
        self.myStrategy = None
        self.strategy_Name = None
        self.strategy_Parameters = None
        # Assets states
        self.Money = 0   
        self.Storage = 0   

    def Run_Robot(self):
        self.Load_Local_Data()
        self.set_Strategy()
        self.set_Trading_Office()
        self.Load_Remote_Data()

        self.Print()
        # while True:
        order = self.myStrategy.Run_Strategy(self.myTrading_Office)
        self.Trade(order)
            # need to trace
            # seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            # s = self.trading_office_Parameters["Parameters"]["timeframe"]
            # seconds = int(s[:-1]) * seconds_per_unit[s[-1]]
            # time.sleep(seconds)

    def Load_Local_Data(self):
        with open('Environment_Variables.txt') as f:
            data = f.read()
        params = json.loads(data)

        self.API_key = params["API_key"]
        self.Secret_key = params["Secret_key"]
        self.trading_office_Name = params["Trading_Office_Parameters"]["Trading_Office_Name"]
        self.trading_office_Parameters = params["Trading_Office_Parameters"]
        self.strategy_Name = params["Strategy_Parameters"]["Strategy_Name"]
        self.strategy_Parameters = params["Strategy_Parameters"]

    def set_Strategy(self):
        self.myStrategy = globals()[self.strategy_Name](self.strategy_Parameters)

    def set_Trading_Office(self):
        self.myTrading_Office = globals()[self.trading_office_Name](self.API_key, self.Secret_key, self.trading_office_Parameters)

    def Load_Remote_Data(self):
        remote_data = self.myTrading_Office.Get_Data()
        self.Money = remote_data["Money"]
        self.Storage = remote_data["Storage"]
    
    def Trade(self, order):
        if (order["signal"] == None):
            return None

        if (order["type"] == "MARKET"):
            ## balance
            self.myTrading_Office.Balance()
            time.sleep(20)
            ## update data
            self.Load_Remote_Data()
            ## new trade
            amount = self.leverage * self.Money / order["price"]
            # amount = 20 / order["price"]
            amount = math.floor(amount * 1000) / 1000.0
            self.myTrading_Office.Trade(order["signal"], "MARKET", amount = amount)

        elif (order["type"] == "LIMIT"):
            ## balance
            self.myTrading_Office.Balance()
            time.sleep(20)
            ## update data
            self.Load_Remote_Data()
            ## new trade
            amount = self.leverage * self.Money / order["price"]
            # amount = 20 / order["price"]
            amount = math.floor(amount * 1000) / 1000.0
            price = order["price"]
            self.myTrading_Office.Trade(order["signal"], "LIMIT", price = price, amount = amount)

    def Write_log(self):
        pass

    def Send_Notification(self):
        pass

    def Print(self):
        log = open("Robot.log", "a")
        now = datetime.datetime.now()
        print("", file=log)
        print("+++++++++++++++++++++++", file=log)
        print("Time:", str(now), file=log)
        print("API:", self.API_key, file=log)
        print("Secret:", self.Secret_key, file=log)
        print("=======================", file=log)
        print("Strategy Name:", self.strategy_Name, file=log)
        print("Strategy Parameter:", self.strategy_Parameters, file=log)
        print("=======================", file=log)
        print("Trading Office Name:", self.trading_office_Name, file=log)
        print("Trading Office Parameter:", self.trading_office_Parameters, file=log)
        print("=======================", file=log)
        print("Money:", self.Money, "Storage:", self.Storage, file=log)
        print(self.myStrategy, file=log)
        print(self.myTrading_Office, file=log)



