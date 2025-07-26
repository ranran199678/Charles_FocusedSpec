# utils/finnhub_utils.py

import requests
import pandas as pd
import os

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d1in1ahr01qhbuvr1dggd1in1ahr01qhbuvr1dh0")

def fh_get(endpoint, params=None, verify_ssl=True):
    base_url = "https://finnhub.io/api/v1"
    url = f"{base_url}/{endpoint}"
    if params is None:
        params = {}
    params["token"] = FINNHUB_API_KEY

    try:
        response = requests.get(url, params=params, verify=verify_ssl, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Finnhub error: {e}")
        return None

def fh_get_price_df(ticker, verify_ssl=True):
    try:
        url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&count=100&token={FINNHUB_API_KEY}"
        response = requests.get(url, verify=verify_ssl)
        data = response.json()

        if data.get("s") != "ok":
            print(f"Finnhub error: {data.get('s')}")
            return None

        df = pd.DataFrame({
            'date': pd.to_datetime(data['t'], unit='s'),
            'open': data['o'],
            'high': data['h'],
            'low': data['l'],
            'close': data['c'],
            'volume': data['v']
        })
        df.set_index('date', inplace=True)
        df.name = ticker
        return df
    except Exception as e:
        print(f"❌ fh_get_price_df error for {ticker}: {e}")
        return None

def fh_get_float_ratio(ticker, verify_ssl=True):
    # לא באמת קיים API פתוח לנתון הזה – מחזיר None כרגע
    return None
