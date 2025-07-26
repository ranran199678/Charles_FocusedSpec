# utils/twelve_utils.py

import requests
import pandas as pd
import os

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY", "1674fddb50d947cc97e7caafecd246a4")

def td_get(endpoint, params=None, verify_ssl=True):
    base_url = "https://api.twelvedata.com"
    url = f"{base_url}/{endpoint}"
    if params is None:
        params = {}
    params["apikey"] = TWELVE_API_KEY

    try:
        response = requests.get(url, params=params, verify=verify_ssl, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"TwelveData error: {e}")
        return None

def td_get_price_df(ticker, verify_ssl=True):
    data = td_get("time_series", {
        "symbol": ticker,
        "interval": "1day",
        "outputsize": 100
    }, verify_ssl=verify_ssl)

    if data is None or "values" not in data:
        return None

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.set_index("datetime", inplace=True)
    df = df.astype(float)
    df = df.rename(columns={
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume"
    })
    df.sort_index(inplace=True)
    df.name = ticker
    return df

def td_get_float_ratio(ticker, verify_ssl=True):
    # TwelveData לא באמת מספק נתון float ratio. מוחזר None.
    return None
