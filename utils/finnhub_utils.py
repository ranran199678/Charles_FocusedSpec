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

class FinnhubUtils:
    """
    מחלקת עזר ל-Finnhub API
    """
    
    def __init__(self, api_key: str = None):
        """
        אתחול מחלקת Finnhub
        
        Args:
            api_key: מפתח API (אופציונלי)
        """
        self.api_key = api_key or FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
    
    def get_price_data(self, symbol: str, resolution: str = "D", 
                      count: int = 100, verify_ssl: bool = True) -> pd.DataFrame:
        """
        שליפת נתוני מחירים
        
        Args:
            symbol: סמל המניה
            resolution: רזולוציה (D=יום, 1=דקה, 5=5 דקות, וכו')
            count: מספר נקודות נתונים
            verify_ssl: האם לוודא SSL
            
        Returns:
            DataFrame עם נתוני מחירים
        """
        return fh_get_price_df(symbol, verify_ssl)
    
    def get_float_ratio(self, symbol: str, verify_ssl: bool = True) -> float:
        """
        שליפת יחס Float (לא נתמך ב-Finnhub)
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            None (לא נתמך)
        """
        return fh_get_float_ratio(symbol, verify_ssl)
    
    def get_company_profile(self, symbol: str, verify_ssl: bool = True) -> dict:
        """
        שליפת פרופיל חברה
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם נתוני החברה
        """
        data = fh_get("stock/profile2", {"symbol": symbol}, verify_ssl=verify_ssl)
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
        data = fh_get("stock/earnings", {"symbol": symbol}, verify_ssl=verify_ssl)
        return data if data else {}
    
    def get_news(self, symbol: str = None, category: str = "general", 
                verify_ssl: bool = True) -> dict:
        """
        שליפת חדשות
        
        Args:
            symbol: סמל המניה (אופציונלי)
            category: קטגוריה
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם חדשות
        """
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        
        data = fh_get("news", params, verify_ssl=verify_ssl)
        return data if data else {}
    
    def get_insider_transactions(self, symbol: str, verify_ssl: bool = True) -> dict:
        """
        שליפת עסקאות פנים
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם עסקאות פנים
        """
        data = fh_get("stock/insider-transactions", {"symbol": symbol}, verify_ssl=verify_ssl)
        return data if data else {}
    
    def get_institutional_sentiment(self, symbol: str, verify_ssl: bool = True) -> dict:
        """
        שליפת sentiment מוסדי
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם sentiment מוסדי
        """
        data = fh_get("stock/institutional-sentiment", {"symbol": symbol}, verify_ssl=verify_ssl)
        return data if data else {}
    
    def get_analyst_recommendations(self, symbol: str, verify_ssl: bool = True) -> dict:
        """
        שליפת המלצות אנליסטים
        
        Args:
            symbol: סמל המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            מילון עם המלצות אנליסטים
        """
        data = fh_get("stock/recommendation", {"symbol": symbol}, verify_ssl=verify_ssl)
        return data if data else {}
