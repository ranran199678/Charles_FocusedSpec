"""
FMP Utils - Financial Modeling Prep API Client
==============================================

מודול מתקדם לשליפת נתונים מ-Financial Modeling Prep API.
מספק ממשק פשוט ויעיל לשליפת נתוני מחירים, יחסים פיננסיים ונתונים פונדמנטליים.

תכונות מתקדמות:
- שליפת נתוני מחירים מלאים (OHLCV)
- שליפת נתוני מחירים בסיסיים (Close only)
- תמיכה בטווחי תאריכים
- שליפת יחסים פיננסיים
- טיפול בשגיאות מתקדם
- לוגים מפורטים
- ולידציה של נתונים
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
from utils.credentials import APICredentials
from utils.logger import logger

class FMPClient:
    """
    לקוח מתקדם ל-Financial Modeling Prep API
    
    תכונות מתקדמות:
    - שליפת נתוני מחירים מלאים (OHLCV)
    - שליפת נתוני מחירים בסיסיים (Close only)
    - תמיכה בטווחי תאריכים
    - שליפת יחסים פיננסיים
    - טיפול בשגיאות מתקדם
    - לוגים מפורטים
    - ולידציה של נתונים
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """אתחול הלקוח"""
        self.api_key = api_key or APICredentials.get_fmp_key()
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Charles_FocusedSpec/1.0'
        })
        
        # הגדרות ברירת מחדל
        self.default_timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
        
        # ולידציה של API key
        if not self.api_key:
            logger.warning("FMP API key not found - some functions may not work")
    
    def fmp_get(self, endpoint: str, params: Optional[Dict] = None, 
                verify_ssl: bool = True, timeout: Optional[int] = None) -> Optional[Dict]:
        """
        שליפה גנרית מכל endpoint של FMP
        
        Args:
            endpoint: ה-endpoint לשליפה
            params: פרמטרים נוספים
            verify_ssl: האם לוודא SSL
            timeout: זמן המתנה בשניות
            
        Returns:
            JSON dict או None במקרה של שגיאה
        """
        try:
            # בניית URL
            url = f"{self.base_url}/{endpoint}"
            
            # הוספת API key
            request_params = params or {}
            if self.api_key:
                request_params['apikey'] = self.api_key
            
            # הגדרת timeout
            request_timeout = timeout or self.default_timeout
            
            # ביצוע בקשה
            response = self.session.get(
                url,
                params=request_params,
                timeout=request_timeout,
                verify=verify_ssl
            )
            
            # בדיקת תגובה
            response.raise_for_status()
            
            # המרה ל-JSON
            data = response.json()
            
            logger.debug(f"FMP API call successful: {endpoint}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"FMP API request failed for {endpoint}: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"FMP API response parsing failed for {endpoint}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in FMP API call for {endpoint}: {str(e)}")
            return None
    
    def fmp_get_price_df(self, ticker: str, verify_ssl: bool = True, 
                        start_date: Optional[str] = None, 
                        end_date: Optional[str] = None,
                        limit_days: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        שליפת מחירי סגירה היסטוריים (serietype=line)
        
        Args:
            ticker: סימבול המניה
            verify_ssl: האם לוודא SSL
            start_date: תאריך התחלה (YYYY-MM-DD)
            end_date: תאריך סיום (YYYY-MM-DD)
            limit_days: הגבלת מספר ימים
            
        Returns:
            DataFrame עם אינדקס תאריכים או None במקרה של שגיאה
        """
        try:
            # בניית פרמטרים
            params = {'serietype': 'line'}
            
            # הוספת טווח תאריכים אם מוגדר
            if start_date:
                params['from'] = start_date
            if end_date:
                params['to'] = end_date
            
            # ביצוע שליפה
            endpoint = f"historical-price-full/{ticker}"
            data = self.fmp_get(endpoint, params, verify_ssl)
            
            if not data or 'historical' not in data:
                logger.warning(f"No historical data found for {ticker}")
                return None
            
            # המרה ל-DataFrame
            df = pd.DataFrame(data['historical'])
            
            if df.empty:
                logger.warning(f"Empty historical data for {ticker}")
                return None
            
            # המרת תאריכים
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # מיון לפי תאריך (מהחדש לישן)
            df = df.sort_index(ascending=False)
            
            # הגבלת מספר ימים אם מוגדר
            if limit_days and len(df) > limit_days:
                df = df.head(limit_days)
            
            # בחירת עמודת Close בלבד
            if 'close' in df.columns:
                df = df[['close']]
            else:
                logger.warning(f"No 'close' column found for {ticker}")
                return None
            
            logger.info(f"Successfully fetched {len(df)} days of price data for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching price data for {ticker}: {str(e)}")
            return None
    
    def fmp_get_price_ohlcv_df(self, ticker: str, verify_ssl: bool = True,
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None,
                              limit_days: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        שליפת נתוני מחירים מלאים (OHLCV)
        
        Args:
            ticker: סימבול המניה
            verify_ssl: האם לוודא SSL
            start_date: תאריך התחלה (YYYY-MM-DD)
            end_date: תאריך סיום (YYYY-MM-DD)
            limit_days: הגבלת מספר ימים
            
        Returns:
            DataFrame עם OHLCV או None במקרה של שגיאה
        """
        try:
            # בניית פרמטרים
            params = {'serietype': 'full'}
            
            # הוספת טווח תאריכים אם מוגדר
            if start_date:
                params['from'] = start_date
            if end_date:
                params['to'] = end_date
            
            # ביצוע שליפה
            endpoint = f"historical-price-full/{ticker}"
            data = self.fmp_get(endpoint, params, verify_ssl)
            
            if not data or 'historical' not in data:
                logger.warning(f"No historical data found for {ticker}")
                return None
            
            # המרה ל-DataFrame
            df = pd.DataFrame(data['historical'])
            
            if df.empty:
                logger.warning(f"Empty historical data for {ticker}")
                return None
            
            # המרת תאריכים
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # מיון לפי תאריך (מהחדש לישן)
            df = df.sort_index(ascending=False)
            
            # הגבלת מספר ימים אם מוגדר
            if limit_days and len(df) > limit_days:
                df = df.head(limit_days)
            
            # בחירת עמודות OHLCV
            ohlcv_columns = ['open', 'high', 'low', 'close', 'volume']
            available_columns = [col for col in ohlcv_columns if col in df.columns]
            
            if not available_columns:
                logger.warning(f"No OHLCV columns found for {ticker}")
                return None
            
            df = df[available_columns]
            
            # המרת עמודות מספריות
            for col in available_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # הסרת שורות עם נתונים חסרים
            df = df.dropna()
            
            logger.info(f"Successfully fetched {len(df)} days of OHLCV data for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV data for {ticker}: {str(e)}")
            return None
    
    def fmp_get_float_ratio(self, ticker: str, verify_ssl: bool = True) -> Optional[float]:
        """
        שליפת יחס Float (Free Float Ratio)
        
        Args:
            ticker: סימבול המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            יחס Float או None במקרה של שגיאה
        """
        try:
            # שליפת נתוני חברה
            endpoint = f"profile/{ticker}"
            data = self.fmp_get(endpoint, verify_ssl=verify_ssl)
            
            if not data or not isinstance(data, list) or len(data) == 0:
                logger.warning(f"No company profile data found for {ticker}")
                return None
            
            company_data = data[0]
            
            # חיפוש נתוני Float
            float_ratio = None
            
            # ניסיון למצוא נתוני Float בשדות שונים
            float_fields = ['floatShares', 'sharesFloat', 'freeFloat', 'floatRatio']
            
            for field in float_fields:
                if field in company_data and company_data[field] is not None:
                    try:
                        float_ratio = float(company_data[field])
                        break
                    except (ValueError, TypeError):
                        continue
            
            if float_ratio is not None:
                logger.info(f"Successfully fetched float ratio for {ticker}: {float_ratio}")
                return float_ratio
            else:
                logger.warning(f"No float ratio data found for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching float ratio for {ticker}: {str(e)}")
            return None
    
    def fmp_get_company_profile(self, ticker: str, verify_ssl: bool = True) -> Optional[Dict]:
        """
        שליפת פרופיל חברה
        
        Args:
            ticker: סימבול המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            Dict עם נתוני החברה או None במקרה של שגיאה
        """
        try:
            endpoint = f"profile/{ticker}"
            data = self.fmp_get(endpoint, verify_ssl=verify_ssl)
            
            if not data or not isinstance(data, list) or len(data) == 0:
                logger.warning(f"No company profile data found for {ticker}")
                return None
            
            company_data = data[0]
            logger.info(f"Successfully fetched company profile for {ticker}")
            return company_data
            
        except Exception as e:
            logger.error(f"Error fetching company profile for {ticker}: {str(e)}")
            return None
    
    def fmp_get_income_statement(self, ticker: str, period: str = "annual", 
                                limit: int = 5, verify_ssl: bool = True) -> Optional[pd.DataFrame]:
        """
        שליפת דוח רווח והפסד
        
        Args:
            ticker: סימבול המניה
            period: תקופה ('annual' או 'quarter')
            limit: מספר תקופות לשליפה
            verify_ssl: האם לוודא SSL
            
        Returns:
            DataFrame עם דוח רווח והפסד או None במקרה של שגיאה
        """
        try:
            params = {
                'period': period,
                'limit': limit
            }
            
            endpoint = f"income-statement/{ticker}"
            data = self.fmp_get(endpoint, params, verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No income statement data found for {ticker}")
                return None
            
            df = pd.DataFrame(data)
            
            if df.empty:
                logger.warning(f"Empty income statement data for {ticker}")
                return None
            
            # המרת תאריכים
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            
            logger.info(f"Successfully fetched income statement for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching income statement for {ticker}: {str(e)}")
            return None
    
    def fmp_get_balance_sheet(self, ticker: str, period: str = "annual",
                            limit: int = 5, verify_ssl: bool = True) -> Optional[pd.DataFrame]:
        """
        שליפת מאזן
        
        Args:
            ticker: סימבול המניה
            period: תקופה ('annual' או 'quarter')
            limit: מספר תקופות לשליפה
            verify_ssl: האם לוודא SSL
            
        Returns:
            DataFrame עם מאזן או None במקרה של שגיאה
        """
        try:
            params = {
                'period': period,
                'limit': limit
            }
            
            endpoint = f"balance-sheet-statement/{ticker}"
            data = self.fmp_get(endpoint, params, verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No balance sheet data found for {ticker}")
                return None
            
            df = pd.DataFrame(data)
            
            if df.empty:
                logger.warning(f"Empty balance sheet data for {ticker}")
                return None
            
            # המרת תאריכים
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            
            logger.info(f"Successfully fetched balance sheet for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching balance sheet for {ticker}: {str(e)}")
            return None
    
    def fmp_get_cash_flow_statement(self, ticker: str, period: str = "annual",
                                  limit: int = 5, verify_ssl: bool = True) -> Optional[pd.DataFrame]:
        """
        שליפת תזרים מזומנים
        
        Args:
            ticker: סימבול המניה
            period: תקופה ('annual' או 'quarter')
            limit: מספר תקופות לשליפה
            verify_ssl: האם לוודא SSL
            
        Returns:
            DataFrame עם תזרים מזומנים או None במקרה של שגיאה
        """
        try:
            params = {
                'period': period,
                'limit': limit
            }
            
            endpoint = f"cash-flow-statement/{ticker}"
            data = self.fmp_get(endpoint, params, verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No cash flow data found for {ticker}")
                return None
            
            df = pd.DataFrame(data)
            
            if df.empty:
                logger.warning(f"Empty cash flow data for {ticker}")
                return None
            
            # המרת תאריכים
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            
            logger.info(f"Successfully fetched cash flow statement for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching cash flow statement for {ticker}: {str(e)}")
            return None
    
    def fmp_get_ratios(self, ticker: str, period: str = "annual",
                      limit: int = 5, verify_ssl: bool = True) -> Optional[pd.DataFrame]:
        """
        שליפת יחסים פיננסיים
        
        Args:
            ticker: סימבול המניה
            period: תקופה ('annual' או 'quarter')
            limit: מספר תקופות לשליפה
            verify_ssl: האם לוודא SSL
            
        Returns:
            DataFrame עם יחסים פיננסיים או None במקרה של שגיאה
        """
        try:
            params = {
                'period': period,
                'limit': limit
            }
            
            endpoint = f"ratios/{ticker}"
            data = self.fmp_get(endpoint, params, verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No ratios data found for {ticker}")
                return None
            
            df = pd.DataFrame(data)
            
            if df.empty:
                logger.warning(f"Empty ratios data for {ticker}")
                return None
            
            # המרת תאריכים
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            
            logger.info(f"Successfully fetched ratios for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching ratios for {ticker}: {str(e)}")
            return None
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        ולידציה של סימבול מניה
        
        Args:
            ticker: סימבול לבדיקה
            
        Returns:
            True אם תקין, False אחרת
        """
        if not ticker or not isinstance(ticker, str):
            return False
        
        # הסרת רווחים
        ticker = ticker.strip().upper()
        
        # בדיקת אורך
        if len(ticker) < 1 or len(ticker) > 10:
            return False
        
        # בדיקת תווים תקינים
        import re
        if not re.match(r'^[A-Z0-9.-]+$', ticker):
            return False
        
        return True
    
    def get_available_tickers(self, exchange: str = "NASDAQ", verify_ssl: bool = True) -> Optional[List[str]]:
        """
        שליפת רשימת סימבולים זמינים
        
        Args:
            exchange: בורסה
            verify_ssl: האם לוודא SSL
            
        Returns:
            רשימת סימבולים או None במקרה של שגיאה
        """
        try:
            endpoint = f"available-traded/list"
            data = self.fmp_get(endpoint, verify_ssl=verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No available tickers found for {exchange}")
                return None
            
            # סינון לפי בורסה
            tickers = []
            for item in data:
                if isinstance(item, dict) and item.get('exchange') == exchange:
                    symbol = item.get('symbol')
                    if symbol and self.validate_ticker(symbol):
                        tickers.append(symbol)
            
            logger.info(f"Successfully fetched {len(tickers)} tickers for {exchange}")
            return tickers
            
        except Exception as e:
            logger.error(f"Error fetching available tickers for {exchange}: {str(e)}")
            return None
    
    def fmp_get_stock_news(self, tickers: Optional[str] = None, limit: int = 20, 
                          verify_ssl: bool = True) -> Optional[List[Dict]]:
        """
        שליפת חדשות מניות
        
        Args:
            tickers: סימבולים מופרדים בפסיקים
            limit: מספר הפריטים לשליפה
            verify_ssl: האם לוודא SSL
            
        Returns:
            רשימת חדשות או None במקרה של שגיאה
        """
        try:
            params = {'limit': limit}
            if tickers:
                params['tickers'] = tickers
            
            endpoint = "stock_news"
            data = self.fmp_get(endpoint, params, verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No stock news found")
                return None
            
            logger.info(f"Successfully fetched {len(data)} news items")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching stock news: {str(e)}")
            return None
    
    def fmp_get_earnings_calendar(self, from_date: Optional[str] = None, 
                                to_date: Optional[str] = None,
                                verify_ssl: bool = True) -> Optional[List[Dict]]:
        """
        שליפת לוח זמנים של דיווחי רווחים
        
        Args:
            from_date: תאריך התחלה (YYYY-MM-DD)
            to_date: תאריך סיום (YYYY-MM-DD)
            verify_ssl: האם לוודא SSL
            
        Returns:
            רשימת אירועי רווחים או None במקרה של שגיאה
        """
        try:
            params = {}
            if from_date:
                params['from'] = from_date
            if to_date:
                params['to'] = to_date
            
            endpoint = "earning_calendar"
            data = self.fmp_get(endpoint, params, verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No earnings calendar data found")
                return None
            
            logger.info(f"Successfully fetched {len(data)} earnings calendar events")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching earnings calendar: {str(e)}")
            return None
    
    def fmp_get_historical_earnings_calendar(self, ticker: str, 
                                           verify_ssl: bool = True) -> Optional[List[Dict]]:
        """
        שליפת היסטוריית לוח זמנים של דיווחי רווחים
        
        Args:
            ticker: סימבול המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            רשימת אירועי רווחים היסטוריים או None במקרה של שגיאה
        """
        try:
            endpoint = f"historical/earning_calendar/{ticker}"
            data = self.fmp_get(endpoint, verify_ssl=verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No historical earnings calendar data found for {ticker}")
                return None
            
            logger.info(f"Successfully fetched {len(data)} historical earnings events for {ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical earnings calendar for {ticker}: {str(e)}")
            return None
    
    def fmp_get_key_metrics(self, ticker: str, period: str = "annual",
                           limit: int = 5, verify_ssl: bool = True) -> Optional[pd.DataFrame]:
        """
        שליפת מדדים מפתח
        
        Args:
            ticker: סימבול המניה
            period: תקופה ('annual' או 'quarter')
            limit: מספר תקופות לשליפה
            verify_ssl: האם לוודא SSL
            
        Returns:
            DataFrame עם מדדים מפתח או None במקרה של שגיאה
        """
        try:
            params = {
                'period': period,
                'limit': limit
            }
            
            endpoint = f"key-metrics/{ticker}"
            data = self.fmp_get(endpoint, params, verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No key metrics data found for {ticker}")
                return None
            
            df = pd.DataFrame(data)
            
            if df.empty:
                logger.warning(f"Empty key metrics data for {ticker}")
                return None
            
            # המרת תאריכים
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            
            logger.info(f"Successfully fetched key metrics for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching key metrics for {ticker}: {str(e)}")
            return None
    
    def fmp_get_ratios_ttm(self, ticker: str, verify_ssl: bool = True) -> Optional[pd.DataFrame]:
        """
        שליפת יחסים פיננסיים TTM (Trailing Twelve Months)
        
        Args:
            ticker: סימבול המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            DataFrame עם יחסים TTM או None במקרה של שגיאה
        """
        try:
            endpoint = f"ratios-ttm/{ticker}"
            data = self.fmp_get(endpoint, verify_ssl=verify_ssl)
            
            if not data or not isinstance(data, list):
                logger.warning(f"No TTM ratios data found for {ticker}")
                return None
            
            df = pd.DataFrame(data)
            
            if df.empty:
                logger.warning(f"Empty TTM ratios data for {ticker}")
                return None
            
            logger.info(f"Successfully fetched TTM ratios for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching TTM ratios for {ticker}: {str(e)}")
            return None
    
    def fmp_get_earnings_surprises(self, ticker: str, verify_ssl: bool = True) -> Optional[List[Dict]]:
        """
        שליפת הפתעות רווחים עבור מניה
        
        Args:
            ticker: סימול המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            רשימת הפתעות רווחים או None
        """
        try:
            endpoint = f"earnings-surprises/{ticker}"
            data = self.fmp_get(endpoint, verify_ssl=verify_ssl)
            
            if data and isinstance(data, list):
                logger.info(f"Retrieved {len(data)} earnings surprises for {ticker}")
                return data
            else:
                logger.warning(f"No earnings surprises data for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching earnings surprises for {ticker}: {e}")
            return None

    def get_analyst_estimates(self, ticker: str, verify_ssl: bool = True) -> Optional[List[Dict]]:
        """
        שליפת הערכות אנליסטים עבור מניה
        
        Args:
            ticker: סימול המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            רשימת הערכות אנליסטים או None
        """
        try:
            endpoint = f"analyst-estimates/{ticker}"
            data = self.fmp_get(endpoint, verify_ssl=verify_ssl)
            
            if data and isinstance(data, list):
                logger.info(f"Retrieved {len(data)} analyst estimates for {ticker}")
                return data
            else:
                logger.warning(f"No analyst estimates data for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching analyst estimates for {ticker}: {e}")
            return None

    def get_analyst_recommendations(self, ticker: str, verify_ssl: bool = True) -> Optional[List[Dict]]:
        """
        שליפת המלצות אנליסטים עבור מניה
        
        Args:
            ticker: סימול המניה
            verify_ssl: האם לוודא SSL
            
        Returns:
            רשימת המלצות אנליסטים או None
        """
        try:
            endpoint = f"analyst-recommendations/{ticker}"
            data = self.fmp_get(endpoint, verify_ssl=verify_ssl)
            
            if data and isinstance(data, list):
                logger.info(f"Retrieved {len(data)} analyst recommendations for {ticker}")
                return data
            else:
                logger.warning(f"No analyst recommendations data for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching analyst recommendations for {ticker}: {e}")
            return None

# יצירת instance גלובלי
fmp_client = FMPClient()

# ייבוא דינמי של SmartDataManager כדי למנוע מעגלי ייבוא
def _get_smart_data_manager():
    try:
        from utils.smart_data_manager import smart_data_manager  # type: ignore
        return smart_data_manager
    except Exception:
        return None

def _smart_data_available() -> bool:
    return _get_smart_data_manager() is not None

# פונקציות גלובליות לתאימות לאחור
def fmp_get(endpoint: str, params: Optional[Dict] = None, verify_ssl: bool = True) -> Optional[Dict]:
    """פונקציה גלובלית לשליפה גנרית"""
    return fmp_client.fmp_get(endpoint, params, verify_ssl)

def fmp_get_price_df(ticker: str, verify_ssl: bool = True, 
                    start_date: Optional[str] = None, 
                    end_date: Optional[str] = None,
                    limit_days: Optional[int] = None) -> Optional[pd.DataFrame]:
    """פונקציה גלובלית לשליפת מחירי סגירה"""
    return fmp_client.fmp_get_price_df(ticker, verify_ssl, start_date, end_date, limit_days)

def fmp_get_price_ohlcv_df(ticker: str, verify_ssl: bool = True,
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          limit_days: Optional[int] = None) -> Optional[pd.DataFrame]:
    """פונקציה גלובלית לשליפת נתוני OHLCV"""
    return fmp_client.fmp_get_price_ohlcv_df(ticker, verify_ssl, start_date, end_date, limit_days)

def fmp_get_float_ratio(ticker: str, verify_ssl: bool = True) -> Optional[float]:
    """פונקציה גלובלית לשליפת יחס Float"""
    return fmp_client.fmp_get_float_ratio(ticker, verify_ssl)

def fmp_get_stock_news(tickers: Optional[str] = None, limit: int = 20, verify_ssl: bool = True) -> Optional[List[Dict]]:
    """פונקציה גלובלית לשליפת חדשות מניות"""
    return fmp_client.fmp_get_stock_news(tickers, limit, verify_ssl)

def fmp_get_earnings_calendar(from_date: Optional[str] = None, to_date: Optional[str] = None, verify_ssl: bool = True) -> Optional[List[Dict]]:
    """פונקציה גלובלית לשליפת לוח זמנים של דיווחי רווחים"""
    return fmp_client.fmp_get_earnings_calendar(from_date, to_date, verify_ssl)

def fmp_get_historical_earnings_calendar(ticker: str, verify_ssl: bool = True) -> Optional[List[Dict]]:
    """פונקציה גלובלית לשליפת היסטוריית לוח זמנים של דיווחי רווחים"""
    return fmp_client.fmp_get_historical_earnings_calendar(ticker, verify_ssl)

def fmp_get_key_metrics(ticker: str, period: str = "annual", limit: int = 5, verify_ssl: bool = True) -> Optional[pd.DataFrame]:
    """פונקציה גלובלית לשליפת מדדים מפתח"""
    return fmp_client.fmp_get_key_metrics(ticker, period, limit, verify_ssl)

def fmp_get_ratios_ttm(ticker: str, verify_ssl: bool = True) -> Optional[pd.DataFrame]:
    """פונקציה גלובלית לשליפת יחסים פיננסיים TTM"""
    return fmp_client.fmp_get_ratios_ttm(ticker, verify_ssl)

def fmp_get_earnings_surprises(ticker: str, verify_ssl: bool = True) -> Optional[List[Dict]]:
    """פונקציה גלובלית לשליפת הפתעות רווחים"""
    return fmp_client.fmp_get_earnings_surprises(ticker, verify_ssl)

# פונקציות חדשות עם SmartDataManager
def smart_get_price_data(symbol: str, days: int = 90, include_live: bool = True) -> Optional[pd.DataFrame]:
    """
    שליפת נתוני מחירים חכמה - משלב נתונים מקומיים עם API
    
    Args:
        symbol: סימבול המניה
        days: מספר ימים נדרש
        include_live: האם לכלול נתונים חיים
        
    Returns:
        DataFrame עם נתונים או None
    """
    sdm = _get_smart_data_manager()
    if sdm is not None:
        return sdm.get_stock_data(symbol, days, include_live)
    else:
        # fallback לפונקציה הרגילה
        return fmp_get_price_ohlcv_df(symbol, verify_ssl=False, limit_days=days)

def smart_get_multiple_stocks(symbols: List[str], days: int = 90) -> Dict[str, pd.DataFrame]:
    """
    שליפת נתונים למספר מניות עם אסטרטגיה חכמה
    
    Args:
        symbols: רשימת סימבולים
        days: מספר ימים נדרש
        
    Returns:
        מילון של DataFrames
    """
    sdm = _get_smart_data_manager()
    if sdm is not None:
        return sdm.get_multiple_stocks(symbols, days)
    else:
        # fallback לפונקציות הרגילות
        results = {}
        for symbol in symbols:
            data = fmp_get_price_ohlcv_df(symbol, verify_ssl=False, limit_days=days)
            if data is not None:
                results[symbol] = data
        return results

def get_data_status() -> Dict:
    """
    קבלת סטטוס הנתונים במערכת
    
    Returns:
        מילון עם סטטוס הנתונים
    """
    if SMART_DATA_AVAILABLE:
        return smart_data_manager.get_data_status()
    else:
        return {"error": "SmartDataManager לא זמין"}
