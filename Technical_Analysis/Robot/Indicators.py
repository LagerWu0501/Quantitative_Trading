import pandas as pd
import numpy as np
import pandas_ta as ta

def sma(data, period = 100):
    return data.rolling(period).mean()
    
def ema(data, period = 100):
    return data.ewm(span=period).mean() 

def macd(data, short_period = 12, long_period = 26, dif_period = 9):
    dif = ema(data, short_period) - ema(data, long_period)
    dem = ema(dif, dif_period)
    osc = dif - dem
    return osc

def rsi(data, period = 7):
    data = data['A'][-period:]
    a = data.abs()
    b = (a + data) / 2
    return b.sum() / a.sum()


def Supertrend(df,high,low,close,atr_period,multiplier):

    price_diffs=[ high-low, 
                    high-close.shift(), 
                    close.shift()-low]
    true_range=pd.concat(price_diffs, axis=1)
    true_range=true_range.abs().max(axis=1)
    atr=true_range.ewm(alpha=1/atr_period,min_periods=atr_period).mean() 
    hl2=(high+low)/2
    final_upperband=upperband=hl2+(multiplier*atr)
    final_lowerband=lowerband=hl2-(multiplier*atr)
    
    supertrend=[True]*len(df)
    
    for i in range(1,len(df.index)):
        curr,prev=i,i-1
        
        if close[curr]>final_upperband[prev]:
            supertrend[curr]=True
        elif close[curr]<final_lowerband[prev]:
            supertrend[curr]=False
        else:
            supertrend[curr]=supertrend[prev]
            if supertrend[curr]==True and final_lowerband[curr]<final_lowerband[prev]:
                final_lowerband[curr]=final_lowerband[prev]
            if supertrend[curr]==False and final_upperband[curr]>final_upperband[prev]:
                final_upperband[curr]=final_upperband[prev]

        if supertrend[curr]==True:
            final_upperband[curr]=np.nan
        else:
            final_lowerband[curr]=np.nan
    
    return df.join(pd.DataFrame({
        'Supertrend':supertrend,
        'Final Lowerband':final_lowerband,
        'Final Upperband':final_upperband
    },index=df.index))

def HA(df):
    ha_df=ta.ha(df["open"], df["high"], df["low"],df["close"])
    df=df.join(ha_df)
    return df

df = pd.DataFrame({'A': range(-5, 6)})

rsi(df)