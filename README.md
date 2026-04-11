# Heating Oil Breakout Backtest

A Python backtesting project for a breakout strategy on Heating Oil 5-minute data, with in-sample / out-of-sample evaluation, parameter sweep, and performance visualization.

## Project Overview

This project tests a breakout-based trading strategy on Heating Oil futures using 5-minute bar data.

The strategy works roughly as follows:

- Compute the rolling highest high (`HH`) and lowest low (`LL`) over a lookback window `Length`
- When flat:
  - go long if price breaks above `HH`
  - go short if price breaks below `LL`
- When holding a position:
  - use a trailing stop based on `StopPct`
  - if price breaks the opposite breakout level, reverse the position
- Track equity curve, drawdown, trade activity, and yearly performance

The project also separates the sample into:

- **In-sample:** 1980-01-01 to 2000-01-01
- **Out-of-sample:** 2000-01-01 to 2023-03-23

## Files

- `main.py` — main backtest script
- `HO-5minHLV.csv` — Heating Oil 5-minute OHLCV data
- `README.md` — project description

## Strategy Logic

### Entry Rules

When there is no position:

- Buy if current high is greater than or equal to the rolling highest high `HH`
- Sell short if current low is less than or equal to the rolling lowest low `LL`

### Exit / Reversal Rules

When long:

- Exit if price falls below the trailing stop level `benchmarkLong * (1 - StopPct)`
- Reverse to short if price also breaks the rolling low `LL`

When short:

- Exit if price rises above the trailing stop level `benchmarkShort * (1 + StopPct)`
- Reverse to long if price also breaks the rolling high `HH`

## Parameters

The current script supports parameter scanning over:

- `Length`: lookback window for breakout channel
- `StopPct`: trailing stop percentage

Example:

```python
Length = np.arange(10000, 15001, 1000)
StopPct = np.arange(0.005, 0.0201, 0.0025)