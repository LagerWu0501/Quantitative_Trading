from binance.client import Client
import time
import pandas as pd

class Trading_Office:
    def __init__(self, API_key, Secret_key, parameters = [["BTC", "4h", "2 year ago UTC"]]):
        self.API_key = API_key
        self.Secret_key = Secret_key
        self.Parameters = parameters

        self.historical_data = None
        self.storage = 0
        self.money = 0

        self.price = []
        self.amount = []

    def Get_Data(self):
        pass
    def Get_Historical_Data(self):
        pass
    def Get_Orderbook(self):
        pass
    def Get_Bids_Asks(self):
        pass
    def Trade(self):
        pass

class Binance(Trading_Office):
    def __init__(self, API_key, Secret_key, parameters=[["BTC", "12h", "1 year ago UTC"]]):
        super().__init__(API_key, Secret_key, parameters)
        self.client = Client(self.API_key, self.Secret_key)

    def Get_Data(self):
        # money = float(self.client.get_asset_balance("USDT")["free"])
        # storage = {"BTC":float(self.client.get_asset_balance("BTC")["free"]), "ETH":float(self.client.get_asset_balance("ETH")["free"])}
        money = float(self.client.futures_account_balance()[6]["withdrawAvailable"])
        storage = {"BTC":float(self.client.futures_position_information(symbol = "BTCUSDT")[0]["positionAmt"]), "ETH":float(self.client.futures_position_information(symbol = "ETHUSDT")[0]["positionAmt"])}
        return {"Money":money, "Storage":storage}

    def Get_Historical_Data(self):
        pair = self.Parameters["Symbol"]
        timeframe = self.Parameters["Parameters"]["timeframe"]
        startdate  = self.Parameters["Parameters"]["startDate"]

        bars = self.client.get_historical_klines(symbol= pair,interval=timeframe,start_str=startdate)
        test_df = pd.DataFrame(bars[:],columns=["timestamp","open","high","low","close","volume", "close_time", "quote_asset_volume", "number_of_trade", "TBB", "TBQ", "ignore"])
        test_df["date"]=pd.to_datetime(test_df["timestamp"],unit="ms").astype(str)
        # test_df = test_df.drop(["timestamp", "close_time", "quote_asset_volume", "number_of_trade", "TBB", "TBQ", "ignore"], axis=1)
        test_df = test_df.drop(["close_time", "quote_asset_volume", "number_of_trade", "TBB", "TBQ", "ignore"], axis=1)
        test_df["open"] = pd.to_numeric(test_df["open"])
        test_df["high"] = pd.to_numeric(test_df["high"])
        test_df["low"] = pd.to_numeric(test_df["low"])
        test_df["close"] = pd.to_numeric(test_df["close"])
        test_df["volume"] = pd.to_numeric(test_df["volume"])

        return test_df

    def Get_Orderbook(self):
        symbol = self.Parameters["Symbol"]
        orders = self.client.get_order_book(symbol = symbol)
        return {"bids": orders["bids"], "asks": orders["asks"]}

    def Get_Bids_Asks(self):
        bid_ask = self.client.get_orderbook_ticker(symbol = self.Parameters["Symbol"])
        return {"bid": [bid_ask["bidPrice"], bid_ask["bidQty"]], "ask": [bid_ask["askPrice"], bid_ask["askQty"]]}
    

    def Balance(self):
        symbol = self.Parameters["Symbol"]
        storage = float(self.client.futures_position_information(symbol = symbol)[0]["positionAmt"])
        if (storage < 0):
            self.client.futures_create_order(
                symbol = self.Parameters["Symbol"],
                side = "BUY",
                type = "MARKET",
                time_in_force = "GTC",
                quantity = -1* storage
            )
        elif (storage > 0):
            self.client.futures_create_order(
                symbol = self.Parameters["Symbol"],
                side = "SELL",
                type = "MARKET",
                time_in_force = "GTC",
                quantity = storage
            ) 

    def Trade(self, order = None, order_type = None, price = 0, amount = 0):
        if (order == None or order_type == None):
            return ["None"]
        print("order:", order, "ordertype:", order_type, "price:", price, "amont:", amount)
        self.client.futures_change_leverage(symbol=self.Parameters["Symbol"], leverage=self.Parameters["leverage"])
        if (order_type == 'LIMIT'):
            self.client.futures_create_order(
                symbol = self.Parameters["Symbol"],
                side = order,
                type = order_type,
                time_in_force = "GTC",
                price = price,
                quantity = amount
            )
        elif (order_type == 'MARKET'):
            self.client.futures_create_order(
                symbol = self.Parameters["Symbol"],
                side = order,
                type = order_type,
                time_in_force = "GTC",
                quantity = amount
            )

   