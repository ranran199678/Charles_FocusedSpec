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

class TwelveDataUtils:
    """
    מחלקת עזר ל-TwelveData API
    """
    
    def __init__(self, api_key: str = None):
        """
        אתחול מחלקת TwelveData
        
        Args:
            api_key: מפתח API (אופציונלי)
        """
        self.api_key = api_key or TWELVE_API_KEY
        self.base_url = "https://api.twelvedata.com"
    
    def get_price_data(self, symbol: str, interval: str = "1day", 
                      outputsize: int = 100, verify_ssl: bool = True) -> pd.DataFrame:
        """
        שליפת נתוני מחירים
        
        Args:
            symbol: סמל המניה
            interval: מרווח זמן
            outputsize: מספר נקודות נתונים
            verify_ssl: האם לוודא SSL
            
        Returns:
            DataFrame עם נתוני מחירים
        """
        return td_get_price_df(symbol, verify_ssl)
    
    def get_float_ratio(self, symbol: str, verify_ssl: bool = True) -> float:
        """
        שליפת יחס Float (לא נתמך ב-TwelveData)
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            None (לא נתמך)
        """
        return td_get_float_ratio(symbol, verify_ssl)
    
    def get_company_profile(self, symbol: str, verify_ssl: bool = True) -> dict:
        """
        שליפת פרופיל חברה
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם נתוני החברה
        """
        data = td_get("quote", {"symbol": symbol}, verify_ssl=verify_ssl)
        return data if data else {}
    
    def get_earnings(self, symbol: str, verify_ssl: bool = True) -> dict:
        """
        שליפת נתוני רווחים
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם נתוני רווחים
        """
        data = td_get("earnings", {"symbol": symbol}, verify_ssl=verify_ssl)
        return data if data else {}
    
    def get_dividends(self, symbol: str, verify_ssl: bool = True) -> dict:
        """
        שליפת נתוני דיבידנדים
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם נתוני דיבידנדים
        """
        data = td_get("dividends", {"symbol": symbol}, verify_ssl=verify_ssl)
        return data if data else {}
    
    def get_splits(self, symbol: str, verify_ssl: bool = True) -> dict:
        """
        שליפת נתוני פיצולים
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם נתוני פיצולים
        """
        data = td_get("splits", {"symbol": symbol}, verify_ssl=verify_ssl)
        return data if data else {}
    
    def get_technical_indicators(self, symbol: str, indicator: str = "sma", 
                               interval: str = "1day", time_period: int = 20,
                               verify_ssl: bool = True) -> dict:
        """
        שליפת אינדיקטורים טכניים
        
        Args:
            symbol: סמל המניה
            indicator: סוג האינדיקטור
            interval: מרווח זמן
            time_period: תקופת זמן
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם נתוני האינדיקטור
        """
        params = {
            "symbol": symbol,
            "indicator": indicator,
            "interval": interval,
            "time_period": time_period
        }
        data = td_get("technical_indicators", params, verify_ssl=verify_ssl)
        return data if data else {}
