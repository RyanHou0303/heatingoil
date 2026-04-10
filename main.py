import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data_file = "HO-5minHLV.csv"

in_sample_start = pd.Timestamp("1980-01-01")
in_sample_end = pd.Timestamp("2000-01-01")

out_sample_start = pd.Timestamp("2000-01-01")
out_sample_end = pd.Timestamp("2023-03-23")

barsBack = 17001
PV = 42000 #point value
slpg = 47 #sllipage
#uploading data

d = pd.read_csv(data_file)
d["numTime"] = pd.to_datetime(d["Date"].astype(str)+" "+d["Time"].astype(str))

d["N"] = len(d)
d["M"] = 5
d=d.reset_index(drop=True)

print(d)
#index of in-sample/out-sample
ind_in_sample1 = max((d["numTime"]<in_sample_start).sum(),barsBack)
ind_in_sample2 = max((d["numTime"]<(in_sample_end+pd.Timedelta(days=1))).sum()-1,barsBack)

ind_out_sample1 = max((d["numTime"]<out_sample_start).sum(),barsBack)
ind_out_sample2 = max((d["numTime"]<(out_sample_end+pd.Timedelta(days=1))).sum()-1,barsBack)

#parameter to optimize(here only provides 2, can add more)
Length = np.arange(12700,12701,100) #length of the K bars window
StopPct = np.arange(0.010,0.0101,0.001) #stop loss percent

#==================================================================================================
#
#==================================================================================================
for i,L in enumerate(Length):
    print(f"calculating for length ={L}")

    HH = np.zeros(len(d))
    LL = np.zeros(len(d))

    high_vals = d["High"].to_numpy()
    low_vals = d["Low"].to_numpy()
    close_vals = d["Close"].to_numpy()

    for k in range(barsBack,len(d)):
        HH[k] = np.max(high_vals[k-L:k])
        LL[k] = np.min(low_vals[k-L:k])
        #store the previous high and low among L bars in for kth bar

    for j,S in enumerate(StopPct):
        limitBuy = np.nan
        limitSell = np.nan
        stopOrder = np.nan

        position = 0
        E = np.zeros(len(d))+100000
        DD = np.zeros(len(d))
        trades = np.zeros(len(d))
        Emax = E0

        benchmarkLong = np.nan
        benchmarkShort = np.nan

        for k in range(barsBack,len(d)):
            traded = False
            delta = PV*(close_vals[k]-close_vals[k-1])

            if position ==0:
                buy = high_vals[k]>=HH[k]
                sell = low_vals[k]<=LL[k]

                if buy and sell:
                    delta = -slpg + PV*(LL[k]-HH[k])
                    trades[k] =1
                else:
                    if buy:
                        delta = -slpg/2 + PV*(close_vals[k]-HH[k])
                        position = 1
                        traded = True
                        benchmarkLong = high_vals[k] #the longest value after long
                        trades[k]= 0.5
                    if sell:
                        delta = -slpg/2 - PV*(close_vals[k]-LL[k])
                        position = -1
                        traded = True
                        benchmarkShort = low_vals[k]#the lowest value after short
                        trades[k] = 0.5
            #logic: at K, when you don't have position, when the price hit the previous high(H[k]),
            #long, when when the price hit the previous low, short

            if position ==1 and (not traded):
                sellShort = low_vals[k]<=LL[k]
                sell = low_vals[k]<=(benchmarkLong*(1-S))

                if sellShort and sell:
                    if sellShort:
                        delta = delta -slpg - 2*PV*(close_vals[k]-LL[k])
                        position = -1
                        benchmarkShort = low_vals[k]
                        trades[k] = 1
                    else:
                        if sell:
                            delta = delta -slpg/2 - PV*(close_vals[k]-(benchmarkLong*(1-S)))
                            position = 0
                            trades[k] = 0.5
                        if sellShort:
                            delta = delta - slpg - 2 * PV * (close_vals[k] - LL[k])
                            position = -1
                            benchmarkShort = low_vals[k]
                            trades[k] = 1
                    benchmarkLong = max(high_vals[k],benchmarkLong)
            #when you hold a long position, then, when the price break stop loss, cover it, if it down to th
            #previous low, short it, benchmarklong used to decide when to exit, setting with a stop loss ratio
            #when price getting higher, we get higher stop loss as well




















#==================================================================================================
#plot
#==================================================================================================



plt.figure(1,figsize=(12,4))
plt.plot(d["numTime"],d["Close"],"b")
plt.title("Close")
plt.tight_layout()
plt.show(block = False)