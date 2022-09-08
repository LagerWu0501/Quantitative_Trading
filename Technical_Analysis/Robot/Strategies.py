from Indicators import *
class Strategy():
    def __init__(self, parameters):
        short_period = parameters["short_period"]
        long_period = parameters["long_period"]
        self.short_period = short_period
        self.long_period = long_period
    def Run_Strategy(self, data):
        pass

class EMA_Strategy(Strategy):
    def Run_Strategy(self, trading_office):
        data = trading_office.Get_Historical_Data()
        data = data["close"]

        Short_EMA = ema(data, self.short_period)
        Long_EMA = ema(data, self.long_period)
        
        price, amount = -1, -1 #待完成
        price = data[len(data) - 1]
        if (Short_EMA[len(Short_EMA) - 3] < Long_EMA[len(Long_EMA) - 3] and Short_EMA[len(Short_EMA) - 2] > Long_EMA[len(Long_EMA) - 2]):
            return {"signal":"BUY", "price":price, "amount": amount, "type": "MARKET"}
        elif (Short_EMA[len(Short_EMA) - 3] > Long_EMA[len(Long_EMA) - 3] and Short_EMA[len(Short_EMA) - 2] < Long_EMA[len(Long_EMA) - 2]):
            return {"signal":"SELL", "price":price, "amount": amount, "type": "MARKET"}            

        return {"signal":None, "price":None, "amount": None, "type": None}            

class test_Strategy(Strategy):
    def Run_Strategy(self):
        print(self.short_period, self.long_period)
