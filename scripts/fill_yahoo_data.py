import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_fetcher import DataFetcher
import pandas as pd
from datetime import datetime, timedelta

symbol = "ZETA"
fetcher = DataFetcher()

def filter_last_n_trading_days(df, n):
    if df is None or df.empty:
        return df
    unique_days = df.index.normalize().unique()
    last_days = unique_days[-n:]
    return df[df.index.normalize().isin(last_days)]

# 1min - 3 ימי מסחר
interval = "1m"
folder = "data/1min"
os.makedirs(folder, exist_ok=True)
df_1min = fetcher._fallback_yahoo_prices(symbol, interval="1m")
print("1min shape:", df_1min.shape if df_1min is not None else None)
if df_1min is not None:
    last_days = filter_last_n_trading_days(df_1min, 3)
    print("1min after filter:", last_days.shape)
    last_days.to_csv(f"{folder}/{symbol}_1min.csv")

# 5min - 5 ימי מסחר
interval = "5m"
folder = "data/5min"
os.makedirs(folder, exist_ok=True)
df_5min = fetcher._fallback_yahoo_prices(symbol, interval="5m")
print("5min shape:", df_5min.shape if df_5min is not None else None)
if df_5min is not None:
    last_days = filter_last_n_trading_days(df_5min, 5)
    print("5min after filter:", last_days.shape)
    last_days.to_csv(f"{folder}/{symbol}_5min.csv")

# 1h - 30 ימי מסחר
interval = "1h"
folder = "data/1h"
os.makedirs(folder, exist_ok=True)
df_1h = fetcher._fallback_yahoo_prices(symbol, interval="1h")
print("1h shape:", df_1h.shape if df_1h is not None else None)
if df_1h is not None:
    last_days = filter_last_n_trading_days(df_1h, 30)
    print("1h after filter:", last_days.shape)
    last_days.to_csv(f"{folder}/{symbol}_1h.csv")

# 1d - 5 שנים (בערך 1260 ימי מסחר)
interval = "1d"
folder = "data/1d"
os.makedirs(folder, exist_ok=True)
df_1d = fetcher._fallback_yahoo_prices(symbol, interval="1d")
print("1d shape:", df_1d.shape if df_1d is not None else None)
if df_1d is not None:
    last_days = df_1d.tail(1260)
    print("1d after tail:", last_days.shape)
    last_days.to_csv(f"{folder}/{symbol}_1d.csv")

# 1wk - גזירה מנתוני 1d
folder = "data/1wk"
os.makedirs(folder, exist_ok=True)
if df_1d is not None:
    df_1wk = df_1d.resample('W').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    print("1wk shape:", df_1wk.shape)
    df_1wk.to_csv(f"{folder}/{symbol}_1wk.csv")

# 1mo - גזירה מנתוני 1d
folder = "data/1mo"
os.makedirs(folder, exist_ok=True)
if df_1d is not None:
    df_1mo = df_1d.resample('M').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    print("1mo shape:", df_1mo.shape)
    df_1mo.to_csv(f"{folder}/{symbol}_1mo.csv")

# --- Finnhub ---

# 1min - 3 ימי מסחר
interval = "1min"
folder = "data/1min"
df_finnhub_1min = fetcher._fallback_finnhub_prices(symbol, interval=interval)
print("finnhub 1min shape:", df_finnhub_1min.shape if df_finnhub_1min is not None else None)
if df_finnhub_1min is not None:
    last_days = filter_last_n_trading_days(df_finnhub_1min, 3)
    last_days.to_csv(f"{folder}/finnhub_{symbol}_1min.csv")

# 5min - 5 ימי מסחר
interval = "5min"
folder = "data/5min"
df_finnhub_5min = fetcher._fallback_finnhub_prices(symbol, interval=interval)
print("finnhub 5min shape:", df_finnhub_5min.shape if df_finnhub_5min is not None else None)
if df_finnhub_5min is not None:
    last_days = filter_last_n_trading_days(df_finnhub_5min, 5)
    last_days.to_csv(f"{folder}/finnhub_{symbol}_5min.csv")

# 1h - 30 ימי מסחר
interval = "1h"
folder = "data/1h"
df_finnhub_1h = fetcher._fallback_finnhub_prices(symbol, interval=interval)
print("finnhub 1h shape:", df_finnhub_1h.shape if df_finnhub_1h is not None else None)
if df_finnhub_1h is not None:
    last_days = filter_last_n_trading_days(df_finnhub_1h, 30)
    last_days.to_csv(f"{folder}/finnhub_{symbol}_1h.csv")

# 1d - 5 שנים (בערך 1260 ימי מסחר)
interval = "1day"
folder = "data/1d"
df_finnhub_1d = fetcher._fallback_finnhub_prices(symbol, interval=interval)
print("finnhub 1d shape:", df_finnhub_1d.shape if df_finnhub_1d is not None else None)
if df_finnhub_1d is not None:
    last_days = df_finnhub_1d.tail(1260)
    print("finnhub 1d after tail:", last_days.shape)
    last_days.to_csv(f"{folder}/finnhub_{symbol}_1d.csv")

# 1wk - גזירה מנתוני 1d
folder = "data/1wk"
if df_finnhub_1d is not None:
    df_finnhub_1wk = df_finnhub_1d.resample('W').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    print("finnhub 1wk shape:", df_finnhub_1wk.shape)
    df_finnhub_1wk.to_csv(f"{folder}/finnhub_{symbol}_1wk.csv")

# 1mo - גזירה מנתוני 1d
folder = "data/1mo"
if df_finnhub_1d is not None:
    df_finnhub_1mo = df_finnhub_1d.resample('M').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    print("finnhub 1mo shape:", df_finnhub_1mo.shape)
    df_finnhub_1mo.to_csv(f"{folder}/finnhub_{symbol}_1mo.csv")

print("✔️ כל הנתונים נשמרו בהצלחה!")
