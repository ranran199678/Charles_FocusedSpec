# utils/fmp_utils.py

import requests
import pandas as pd
import os

FMP_API_KEY = os.getenv("FMP_API_KEY", "f8avXV34RWqtoYQXSZxVWrDlvhKCwIF5")

def fmp_get(endpoint, params=None, verify_ssl=True):
    base_url = "https://financialmodelingprep.com/api/v3"
    url = f"{base_url}/{endpoint}"
    if params is None:
        params = {}
    params["apikey"] = FMP_API_KEY

    try:
        response = requests.get(url, params=params, verify=verify_ssl, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"FMP error: {e}")
        return None

def fmp_get_price_df(ticker, verify_ssl=True):
    try:
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={FMP_API_KEY}&serietype=line"
        response = requests.get(url, verify=verify_ssl)
        if response.status_code != 200:
            print(f"FMP error: HTTP {response.status_code}")
            return None

        data = response.json()
        if 'historical' not in data:
            print("FMP error: 'historical' key missing")
            return None

        df = pd.DataFrame(data['historical'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.sort_index()
        df.name = ticker
        return df
    except Exception as e:
        print(f"❌ fmp_get_price_df error for {ticker}: {e}")
        return None

def fmp_get_float_ratio(ticker, verify_ssl=True):
    # נתוני float ratio לא תמיד זמינים. מחזיר None כברירת מחדל.
    return None

def fetch_analyst_estimates(ticker, verify_ssl=True):
    """
    שליפת הערכות אנליסטים מ-FMP
    """
    try:
        url = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}?apikey={FMP_API_KEY}&limit=10"
        response = requests.get(url, verify=verify_ssl, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data
            else:
                print(f"אין נתוני הערכות אנליסטים עבור {ticker}")
                return None
        else:
            print(f"שגיאה בקבלת הערכות אנליסטים: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"שגיאה בקבלת הערכות אנליסטים עבור {ticker}: {e}")
        return None
