import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



#==================================================================================================
#Load data
#==================================================================================================
data_file = "HO-5minHLV.csv"

in_sample_start = pd.Timestamp("1980-01-01")
in_sample_end = pd.Timestamp("2000-01-01")

out_sample_start = pd.Timestamp("2000-01-01")
out_sample_end = pd.Timestamp("2023-03-23")
#initail setting
#not trading until first 17001 bars, in heating oil market, the point value is 42000

barsBack = 17001
PV = 42000 #point value
slpg = 47 #sllipage

E0 = 100000 #initial capital
result_label = ["Profit", "WorstDrawDown", "StDev", "#trades"]
trades = []
limitBuy = np.nan
limitSell = np.nan
stopOrder = np.nan
position = 0

#parameter to optimize(here only provides 2, can add more)
Length = np.arange(12700,12701,100) #length of the K bars window
StopPct = np.arange(0.010,0.0101,0.001) #stop loss percent


result_in_sample = np.zeros((len(Length), len(StopPct), len(result_label)))
result_out_sample = np.zeros((len(Length), len(StopPct), len(result_label)))

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




#==================================================================================================
#Trade
#==================================================================================================
for i, L in enumerate(Length):
    print(f"calculating for Length = {L}")

    # we can calculate HH and LL for all StopPct with the same Length
    HH = np.zeros(len(d))
    LL = np.zeros(len(d))

    high_vals = d["High"].to_numpy()
    low_vals = d["Low"].to_numpy()
    close_vals = d["Close"].to_numpy()

    for k in range(barsBack, len(d)):

        # Python 0-based: use [k-L : k]
        HH[k] = np.max(high_vals[k - L:k])
        LL[k] = np.min(low_vals[k - L:k])

    for j, S in enumerate(StopPct):

        # setting initial conditions:
        limitBuy = np.nan
        limitSell = np.nan
        stopOrder = np.nan

        position = 0
        E = np.zeros(len(d)) + E0
        DD = np.zeros(len(d))
        trades = np.zeros(len(d))
        Emax = E0

        benchmarkLong = np.nan
        benchmarkShort = np.nan

        # running through the time and trading:
        for k in range(barsBack, len(d)):
            traded = False
            delta = PV * (close_vals[k] - close_vals[k - 1]) * position

            if position == 0:
                buy = high_vals[k] >= HH[k]
                sell = low_vals[k] <= LL[k]

                if buy and sell:
                    delta = -slpg + PV * (LL[k] - HH[k])
                    trades[k] = 1
                else:
                    if buy:
                        delta = -slpg / 2 + PV * (close_vals[k] - HH[k])
                        position = 1
                        traded = True
                        benchmarkLong = high_vals[k]
                        trades[k] = 0.5

                    if sell:
                        delta = -slpg / 2 - PV * (close_vals[k] - LL[k])
                        position = -1
                        traded = True
                        benchmarkShort = low_vals[k]
                        trades[k] = 0.5

            if position == 1 and (not traded):
                sellShort = low_vals[k] <= LL[k]
                sell = low_vals[k] <= (benchmarkLong * (1 - S))

                if sellShort and sell:
                    # copy of sell short
                    if sellShort:
                        delta = delta - slpg - 2 * PV * (close_vals[k] - LL[k])
                        position = -1
                        benchmarkShort = low_vals[k]
                        trades[k] = 1
                else:
                    if sell:
                        delta = delta - slpg / 2 - PV * (close_vals[k] - (benchmarkLong * (1 - S)))
                        position = 0
                        trades[k] = 0.5

                    if sellShort:
                        delta = delta - slpg - 2 * PV * (close_vals[k] - LL[k])
                        position = -1
                        benchmarkShort = low_vals[k]
                        trades[k] = 1

                benchmarkLong = max(high_vals[k], benchmarkLong)

            if position == -1 and (not traded):
                buyLong = high_vals[k] >= HH[k]
                buy = high_vals[k] >= (benchmarkShort * (1 + S))

                if buyLong and buy:
                    # copy of buyLong
                    if buyLong:
                        delta = delta - slpg + 2 * PV * (close_vals[k] - HH[k])
                        position = 1
                        benchmarkLong = high_vals[k]
                        trades[k] = 1
                else:
                    if buy:
                        delta = delta - slpg / 2 + PV * (close_vals[k] - (benchmarkShort * (1 + S)))
                        position = 0
                        trades[k] = 0.5

                    if buyLong:
                        delta = delta - slpg + 2 * PV * (close_vals[k] - HH[k])
                        position = 1
                        benchmarkLong = high_vals[k]
                        trades[k] = 1

                benchmarkShort = min(low_vals[k], benchmarkShort)

            # update equity
            E[k] = E[k - 1] + delta

            # calculate drawdown
            Emax = max(Emax, E[k])
            DD[k] = E[k] - Emax

        # in-sample slices
        E_in = E[ind_in_sample1:ind_in_sample2 + 1]
        DD_in = DD[ind_in_sample1:ind_in_sample2 + 1]
        trades_in = trades[ind_in_sample1:ind_in_sample2 + 1]
        pnl_in = np.diff(E_in, prepend=E_in[0])

        # out-of-sample slices
        E_out = E[ind_out_sample1:ind_out_sample2 + 1]
        DD_out = DD[ind_out_sample1:ind_out_sample2 + 1]
        trades_out = trades[ind_out_sample1:ind_out_sample2 + 1]
        pnl_out = np.diff(E_out, prepend=E_out[0])

        # store results
        result_in_sample[i, j, 0] = E_in[-1] - E_in[0]
        result_in_sample[i, j, 1] = np.min(DD_in)
        result_in_sample[i, j, 2] = np.std(pnl_in[1:], ddof=1) if len(pnl_in) > 1 else np.nan
        result_in_sample[i, j, 3] = np.sum(trades_in)

        result_out_sample[i, j, 0] = E_out[-1] - E_out[0]
        result_out_sample[i, j, 1] = np.min(DD_out)
        result_out_sample[i, j, 2] = np.std(pnl_out[1:], ddof=1) if len(pnl_out) > 1 else np.nan
        result_out_sample[i, j, 3] = np.sum(trades_out)



            #when you hold a long position, then, when the price break stop loss, cover it, if it down to th
            #previous low, short it, benchmarklong used to decide when to exit, setting with a stop loss ratio
            #when price getting higher, we get higher stop loss as well


print(result_in_sample)
print(result_out_sample)

# ==================================================================================================
# Performance
# ==================================================================================================

pnl = np.diff(E,prepend=E0)
total_profit = E[-1]-E[0]
total_return_pct = (E[-1]/E[0]-1)*100

max_drawdown = np.min(DD)
max_drawdown_pct = np.min(DD/np.maximum.accumulate(E))*100
pnl_std = np.std(pnl[barsBack:], ddof=1)
n_trades = np.sum(trades)
mean_pnl = np.mean(pnl[barsBack:])

if pnl_std > 0:
    sharpe_like = mean_pnl / pnl_std
else:
    sharpe_like = np.nan

if max_drawdown != 0:
    calmar_like = total_profit / abs(max_drawdown)
else:
    calmar_like = np.nan

print("========== Performance ==========")
print(f"Total Profit      : {total_profit:.2f}")
print(f"Total Return %    : {total_return_pct:.2f}%")
print(f"Max Drawdown      : {max_drawdown:.2f}")
print(f"Max Drawdown %    : {max_drawdown_pct:.2f}%")
print(f"PnL Std           : {pnl_std:.2f}")
print(f"# Trades          : {n_trades:.1f}")
print(f"Sharpe-like       : {sharpe_like:.4f}")
print(f"Calmar-like       : {calmar_like:.4f}")

result_label = ["Profit", "WorstDrawDown", "StDev", "#trades"]











#==================================================================================================
#plot
#==================================================================================================
plt.figure(figsize=(12, 5))
plt.plot(d["numTime"], E, label="Equity")
plt.axvline(in_sample_end, linestyle="--", label="In-sample End")
plt.axvline(out_sample_start, linestyle="--", label="Out-sample Start")
plt.title("Equity Curve")
plt.xlabel("Time")
plt.ylabel("Equity")
plt.legend()
plt.grid(True)
plt.show()


plt.figure(figsize=(12, 4))
plt.plot(d["numTime"], DD)
plt.title("Drawdown")
plt.xlabel("Time")
plt.ylabel("Drawdown")
plt.grid(True)
plt.show()

plt.figure(figsize=(12, 3))
plt.plot(d["numTime"], trades)
plt.title("Trades Over Time")
plt.xlabel("Time")
plt.ylabel("Trade Marker")
plt.grid(True)
plt.show()

trade_df = pd.DataFrame({
    "numTime": d["numTime"],
    "trades": trades
})
trade_df["date"] = trade_df["numTime"].dt.date
daily_trades = trade_df.groupby("date")["trades"].sum()

plt.figure(figsize=(12, 4))
plt.plot(daily_trades.index, daily_trades.values)
plt.title("Daily Trading Activity")
plt.xlabel("Date")
plt.ylabel("Trades")
plt.grid(True)
plt.show()

perf_df = pd.DataFrame({
    "numTime": d["numTime"],
    "Equity": E
})
perf_df["date"] = perf_df["numTime"].dt.date
perf_df["year"] = perf_df["numTime"].dt.year


daily_equity = perf_df.groupby("date")["Equity"].last().reset_index()
daily_equity["date"] = pd.to_datetime(daily_equity["date"])
daily_equity["year"] = daily_equity["date"].dt.year

yearly_perf = daily_equity.groupby("year")["Equity"].agg(["first", "last"])
yearly_perf["Profit"] = yearly_perf["last"] - yearly_perf["first"]
yearly_perf["ReturnPct"] = (yearly_perf["last"] / yearly_perf["first"] - 1) * 100

print(yearly_perf)

plt.figure(figsize=(12, 4))
plt.bar(yearly_perf.index.astype(str), yearly_perf["Profit"])
plt.title("Yearly Profit")
plt.xlabel("Year")
plt.ylabel("Profit")
plt.grid(True, axis="y")
plt.show()