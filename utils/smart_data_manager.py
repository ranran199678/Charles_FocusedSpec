"""
Smart Data Manager - ניהול נתונים חכם
משלב נתונים מקומיים עם API עם אחסון אוטומטי
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import gzip
import pickle
import hashlib
from functools import lru_cache
import json
import time

# ייבוא המודולים הקיימים
from utils.fmp_utils import fmp_client
from utils.data_fetcher import DataFetcher
from utils.credentials import APICredentials

# הגדרת לוגר מתקדם
logger = logging.getLogger(__name__)

class UsageTracker:
    """מעקב אחר שימוש במערכת"""
    
    def __init__(self, log_file: str = "data/usage_log.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.usage_stats = self._load_usage_stats()
    
    def _load_usage_stats(self) -> Dict:
        """טעינת סטטיסטיקות שימוש"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"שגיאה בטעינת סטטיסטיקות שימוש: {e}")
        return {
            'api_calls': {},
            'data_requests': {},
            'cache_stats': {'hits': 0, 'misses': 0},
            'performance': {},
            'errors': []
        }
    
    def _save_usage_stats(self):
        """שמירת סטטיסטיקות שימוש"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"שגיאה בשמירת סטטיסטיקות שימוש: {e}")
    
    def log_api_call(self, source: str, symbol: str, success: bool, duration: float):
        """תיעוד קריאת API"""
        if source not in self.usage_stats['api_calls']:
            self.usage_stats['api_calls'][source] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_duration': 0,
                'symbols': {}
            }
        
        stats = self.usage_stats['api_calls'][source]
        stats['total_calls'] += 1
        stats['total_duration'] += duration
        
        if success:
            stats['successful_calls'] += 1
        else:
            stats['failed_calls'] += 1
        
        if symbol not in stats['symbols']:
            stats['symbols'][symbol] = 0
        stats['symbols'][symbol] += 1
        
        self._save_usage_stats()
    
    def log_data_request(self, symbol: str, days: int, source: str, duration: float):
        """תיעוד בקשת נתונים"""
        if symbol not in self.usage_stats['data_requests']:
            self.usage_stats['data_requests'][symbol] = {
                'total_requests': 0,
                'days_requested': 0,
                'sources_used': {},
                'avg_duration': 0
            }
        
        stats = self.usage_stats['data_requests'][symbol]
        stats['total_requests'] += 1
        stats['days_requested'] += days
        
        if source not in stats['sources_used']:
            stats['sources_used'][source] = 0
        stats['sources_used'][source] += 1
        
        # חישוב ממוצע משך זמן
        total_duration = stats['avg_duration'] * (stats['total_requests'] - 1) + duration
        stats['avg_duration'] = total_duration / stats['total_requests']
        
        self._save_usage_stats()
    
    def log_cache_hit(self, hit: bool):
        """תיעוד פגיעה במטמון"""
        if hit:
            self.usage_stats['cache_stats']['hits'] += 1
        else:
            self.usage_stats['cache_stats']['misses'] += 1
        self._save_usage_stats()
    
    def log_error(self, error_type: str, message: str, symbol: str = None):
        """תיעוד שגיאות"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'symbol': symbol
        }
        self.usage_stats['errors'].append(error_entry)
        
        # שמירת רק 100 השגיאות האחרונות
        if len(self.usage_stats['errors']) > 100:
            self.usage_stats['errors'] = self.usage_stats['errors'][-100:]
        
        self._save_usage_stats()
    
    def get_usage_report(self) -> Dict:
        """קבלת דוח שימוש"""
        return {
            'api_calls_summary': {
                source: {
                    'total': stats['total_calls'],
                    'success_rate': stats['successful_calls'] / stats['total_calls'] if stats['total_calls'] > 0 else 0,
                    'avg_duration': stats['total_duration'] / stats['total_calls'] if stats['total_calls'] > 0 else 0
                }
                for source, stats in self.usage_stats['api_calls'].items()
            },
            'cache_efficiency': {
                'hit_rate': self.usage_stats['cache_stats']['hits'] / (self.usage_stats['cache_stats']['hits'] + self.usage_stats['cache_stats']['misses']) if (self.usage_stats['cache_stats']['hits'] + self.usage_stats['cache_stats']['misses']) > 0 else 0,
                'total_requests': self.usage_stats['cache_stats']['hits'] + self.usage_stats['cache_stats']['misses']
            },
            'top_requested_symbols': sorted(
                self.usage_stats['data_requests'].items(),
                key=lambda x: x[1]['total_requests'],
                reverse=True
            )[:10],
            'recent_errors': self.usage_stats['errors'][-10:]
        }

class SmartDataManager:
    """
    מנהל נתונים חכם שמשלב נתונים מקומיים עם API
    עם אופטימיזציות ביצועים מתקדמות
    """
    
    def __init__(self, data_dir: str = "data", enable_compression: bool = True, 
                 cache_size: int = 100, enable_indexing: bool = True):
        self.data_dir = Path(data_dir)
        self.historical_dir = self.data_dir / "historical_prices" / "daily"
        self.raw_dir = self.data_dir / "raw_price_data"
        self.metadata_dir = self.data_dir / "metadata"
        self.cache_dir = self.data_dir / "cache"
        
        # תיקיות נוספות לנתונים מורחבים
        self.technical_dir = self.data_dir / "technical_indicators"
        self.news_dir = self.data_dir / "news_sentiment"
        self.fundamentals_dir = self.data_dir / "fundamentals"
        
        # הגדרות ביצועים
        self.enable_compression = enable_compression
        self.enable_indexing = enable_indexing
        self.cache_size = cache_size
        
        # יצירת תיקיות נדרשות
        self._ensure_directories()
        
        # ייבוא מודולים
        try:
            self.fmp_client = fmp_client
            self.data_fetcher = DataFetcher()
            self._smart_data_available = True
        except Exception as e:
            logger.warning(f"SmartDataManager לא זמין - יוחזרו נתונים ישירות מ-API: {e}")
            self.fmp_client = None
            self.data_fetcher = None
            self._smart_data_available = False
        
        # מטא-דאטה לניהול קבצים
        self.metadata_file = self.metadata_dir / "data_status.json"
        self.index_file = self.metadata_dir / "data_index.pkl"
        self._load_metadata()
        self._load_index()
        
        # זיכרון מטמון
        self._data_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        # מערכת מעקב שימוש
        self.usage_tracker = UsageTracker()
    
    def _ensure_directories(self):
        """יצירת תיקיות נדרשות"""
        directories = [
            self.historical_dir,
            self.raw_dir,
            self.metadata_dir,
            self.cache_dir,
            self.technical_dir,
            self.news_dir,
            self.fundamentals_dir
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_metadata(self):
        """טעינת מטא-דאטה"""
        try:
            if self.metadata_file.exists():
                import json
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}
        except Exception as e:
            logger.warning(f"שגיאה בטעינת מטא-דאטה: {e}")
            self.metadata = {}
    
    def _save_metadata(self):
        """שמירת מטא-דאטה"""
        try:
            import json
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"שגיאה בשמירת מטא-דאטה: {e}")
    
    def _load_index(self):
        """טעינת אינדקס נתונים"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'rb') as f:
                    self.data_index = pickle.load(f)
            else:
                self.data_index = {}
        except Exception as e:
            logger.warning(f"שגיאה בטעינת אינדקס: {e}")
            self.data_index = {}
    
    def _save_index(self):
        """שמירת אינדקס נתונים"""
        try:
            with open(self.index_file, 'wb') as f:
                pickle.dump(self.data_index, f)
        except Exception as e:
            logger.error(f"שגיאה בשמירת אינדקס: {e}")
    
    def _get_file_path(self, symbol: str, compressed: bool = None) -> Path:
        """קבלת נתיב קובץ עם תמיכה בדחיסה"""
        if compressed is None:
            compressed = self.enable_compression
        
        if compressed:
            return self.historical_dir / f"{symbol.upper()}.csv.gz"
        else:
            return self.historical_dir / f"{symbol.upper()}.csv"
    
    def _compress_data(self, data: pd.DataFrame) -> bytes:
        """דחיסת נתונים"""
        if self.enable_compression:
            csv_data = data.to_csv(index=True)
            return gzip.compress(csv_data.encode('utf-8'))
        else:
            return data.to_csv(index=True).encode('utf-8')
    
    def _decompress_data(self, compressed_data: bytes) -> pd.DataFrame:
        """פתיחת נתונים דחוסים"""
        if self.enable_compression:
            csv_data = gzip.decompress(compressed_data).decode('utf-8')
        else:
            csv_data = compressed_data.decode('utf-8')
        
        import io
        return pd.read_csv(io.StringIO(csv_data), index_col=0, parse_dates=True)
    
    @lru_cache(maxsize=100)
    def _get_cached_data(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """קבלת נתונים מהמטמון"""
        cache_key = f"{symbol}_{days}"
        if cache_key in self._data_cache:
            self._cache_hits += 1
            return self._data_cache[cache_key]
        
        self._cache_misses += 1
        return None
    
    def _set_cached_data(self, symbol: str, days: int, data: pd.DataFrame):
        """שמירת נתונים במטמון"""
        cache_key = f"{symbol}_{days}"
        
        # ניהול גודל המטמון
        if len(self._data_cache) >= self.cache_size:
            # הסרת הפריט הישן ביותר
            oldest_key = next(iter(self._data_cache))
            del self._data_cache[oldest_key]
        
        self._data_cache[cache_key] = data
    
    def get_stock_data(self, symbol: str, days: int = 90, 
                      include_live: bool = True) -> Optional[pd.DataFrame]:
        """
        שליפת נתוני מניה עם אסטרטגיה חכמה ואופטימיזציות
        
        Args:
            symbol: סימבול המניה
            days: מספר ימים נדרש
            include_live: האם לכלול נתונים חיים
            
        Returns:
            DataFrame עם נתונים או None
        """
        start_time = time.time()
        
        try:
            # בדיקה במטמון
            cached_data = self._get_cached_data(symbol, days)
            if cached_data is not None:
                logger.info(f"נתונים מהמטמון עבור {symbol}")
                self.usage_tracker.log_cache_hit(True)
                self.usage_tracker.log_data_request(symbol, days, 'cache', time.time() - start_time)
                return cached_data
            
            self.usage_tracker.log_cache_hit(False)
            
            # 1. בדיקה אם יש נתונים מקומיים
            local_data = self._get_local_data(symbol)
            
            if local_data is not None and not local_data.empty:
                logger.info(f"נמצאו נתונים מקומיים עבור {symbol}")
                
                # בדיקה אם יש מספיק נתונים
                if len(local_data) >= days:
                    logger.info(f"נתונים מקומיים מספיקים עבור {symbol}")
                    result = local_data.head(days)
                    self._set_cached_data(symbol, days, result)
                    self.usage_tracker.log_data_request(symbol, days, 'local', time.time() - start_time)
                    return result
                
                # חישוב כמה ימים חסרים
                missing_days = days - len(local_data)
                if include_live and missing_days > 0:
                    logger.info(f"משלים {missing_days} ימים מ-API עבור {symbol}")
                    api_data = self._get_api_data(symbol, missing_days)
                    if api_data is not None and not api_data.empty:
                        combined_data = self._combine_data(local_data, api_data)
                        self._save_data(symbol, combined_data)  # ✅ שמירה של כלל הנתונים המאוחדים
                        result = combined_data.head(days)
                        self._set_cached_data(symbol, days, result)
                        self.usage_tracker.log_data_request(symbol, days, 'local+api', time.time() - start_time)
                        return result
                
                # החזרת הנתונים המקומיים הקיימים
                result = local_data.head(len(local_data))
                self._set_cached_data(symbol, days, result)
                self.usage_tracker.log_data_request(symbol, days, 'local_partial', time.time() - start_time)
                return result
            
            # אם אין נתונים מקומיים, שליפה מ-API
            logger.info(f"שליפת נתונים מ-API עבור {symbol}")
            api_data = self._get_api_data(symbol, days)
            if api_data is not None and not api_data.empty:
                self._save_data(symbol, api_data)  # שמירת נתונים חדשים
                self._set_cached_data(symbol, days, api_data)
                self.usage_tracker.log_data_request(symbol, days, 'api', time.time() - start_time)
                return api_data
            
            logger.warning(f"לא הצלחנו לקבל נתונים עבור {symbol}")
            self.usage_tracker.log_error('data_fetch_failed', f'לא הצלחנו לקבל נתונים עבור {symbol}', symbol)
            return None
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת נתונים עבור {symbol}: {e}")
            self.usage_tracker.log_error('data_fetch_exception', str(e), symbol)
            return None
    
    def _get_local_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """שליפת נתונים מקומיים"""
        try:
            file_path = self._get_file_path(symbol)
            if file_path.exists():
                df = self._decompress_data(file_path.read_bytes())
                if not df.empty:
                    # טיפול בעמודת תאריך - בדיקה אם קיימת
                    if 'date' in df.columns:
                        # המרת עמודת תאריך לאינדקס
                        df['date'] = pd.to_datetime(df['date'])
                        df = df.set_index('date')
                        df = df.sort_index(ascending=False)  # מהחדש לישן
                    elif 'Date' in df.columns:
                        # טיפול במקרה של 'Date' במקום 'date'
                        df['date'] = pd.to_datetime(df['Date'])
                        df = df.drop('Date', axis=1)
                        df = df.set_index('date')
                        df = df.sort_index(ascending=False)
                    else:
                        # אם אין עמודת תאריך, ניצור אחת מהיום הנוכחי אחורה
                        logger.warning(f"לא נמצאה עמודת תאריך בנתונים עבור {symbol} - יוצרת עמודת תאריך")
                        from datetime import datetime, timedelta
                        dates = [datetime.now() - timedelta(days=i) for i in range(len(df))]
                        df['date'] = dates
                        df = df.set_index('date')
                        df = df.sort_index(ascending=False)
                    
                    return df
            return None
        except Exception as e:
            logger.error(f"שגיאה בקריאת נתונים מקומיים עבור {symbol}: {e}")
            return None
    
    def _get_api_data(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """שליפת נתונים מ-API עם fallback"""
        try:
            # ניסיון ראשון: yfinance (חינמי)
            logger.info(f"ניסיון שליפה מ-yfinance עבור {symbol}")
            df = self._get_yfinance_data(symbol, days)
            if df is not None and not df.empty:
                logger.info(f"הצלחה עם yfinance עבור {symbol}")
                return df
            
            # ניסיון שני: FMP (רק אם זמין)
            if self._smart_data_available and self.fmp_client:
                logger.info(f"ניסיון שליפה מ-FMP עבור {symbol}")
                try:
                    df = self.fmp_client.fmp_get_price_ohlcv_df(
                        symbol, 
                        verify_ssl=False, 
                        limit_days=days
                    )
                    if df is not None and not df.empty:
                        logger.info(f"הצלחה עם FMP עבור {symbol}")
                        return df
                except Exception as e:
                    logger.warning(f"שגיאה עם FMP עבור {symbol}: {e}")
            
            # ניסיון שלישי: DataFetcher (רק אם זמין)
            if self._smart_data_available and self.data_fetcher:
                logger.info(f"ניסיון שליפה מ-DataFetcher עבור {symbol}")
                try:
                    df = self.data_fetcher.get_price_history(symbol, f"{days}d")
                    if df is not None and not df.empty:
                        logger.info(f"הצלחה עם DataFetcher עבור {symbol}")
                        return df
                except Exception as e:
                    logger.warning(f"שגיאה עם DataFetcher עבור {symbol}: {e}")
            
            logger.warning(f"לא הצלחנו לקבל נתונים עבור {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת נתונים מ-API עבור {symbol}: {e}")
            return None
    
    def _get_yfinance_data(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """שליפת נתונים מ-Yahoo Finance API ישירות (כמו הקוד שעבד)"""
        try:
            import requests
            import json
            import os
            
            # הגדרות SSL ורשת (כמו הקוד שעבד)
            os.environ["CURL_CA_BUNDLE"] = r"C:\CharlesCertFix\cacert.pem"
            os.environ["REQUESTS_CA_BUNDLE"] = r"C:\CharlesCertFix\cacert.pem"
            
            # הגדרת User-Agent (כמו הקוד שעבד)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # חישוב תאריכים
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 10)
            
            # המרת תאריכים ל-timestamp
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            # URL של Yahoo Finance (כמו הקוד שעבד)
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"
            
            response = requests.get(url, headers=headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    
                    # חילוץ נתונים
                    timestamps = result['timestamp']
                    quotes = result['indicators']['quote'][0]
                    
                    # יצירת DataFrame
                    df_data = {
                        'date': [datetime.fromtimestamp(ts) for ts in timestamps],
                        'open': quotes.get('open', []),
                        'high': quotes.get('high', []),
                        'low': quotes.get('low', []),
                        'close': quotes.get('close', []),
                        'volume': quotes.get('volume', [])
                    }
                    
                    df = pd.DataFrame(df_data)
                    df = df.set_index('date')
                    
                    # הסרת שורות עם ערכים חסרים
                    df = df.dropna()
                    
                    if not df.empty:
                        # מיון מהחדש לישן
                        df = df.sort_index(ascending=False)
                        logger.info(f"הצלחה עם Yahoo Finance API עבור {symbol}")
                        return df
            
            logger.warning(f"שגיאה ב-Yahoo Finance API עבור {symbol}")
            return None
            
        except Exception as e:
            logger.warning(f"שגיאה ב-Yahoo Finance API עבור {symbol}: {e}")
            return None
    
    def _combine_data(self, local_data: pd.DataFrame, api_data: pd.DataFrame) -> pd.DataFrame:
        """שילוב נתונים מקומיים עם API"""
        try:
            # הוספת עמודת source לזיהוי מקור הנתונים
            local_data['source'] = 'local'
            api_data['source'] = 'api'
            
            # שילוב הנתונים
            combined = pd.concat([api_data, local_data])
            
            # הסרת כפילויות לפי תאריך
            combined = combined[~combined.index.duplicated(keep='first')]
            
            # מיון מהחדש לישן
            combined = combined.sort_index(ascending=False)
            
            return combined
            
        except Exception as e:
            logger.error(f"שגיאה בשילוב נתונים: {e}")
            return local_data
    
    def _save_data(self, symbol: str, data: pd.DataFrame):
        """אחסון נתונים חדשים"""
        try:
            # הוספת עמודת symbol
            data_with_symbol = data.copy()
            data_with_symbol['symbol'] = symbol
            
            # שמירה לקובץ
            file_path = self._get_file_path(symbol)
            compressed_data = self._compress_data(data_with_symbol)
            
            # שמירה לקובץ דחוס
            with open(file_path, 'wb') as f:
                f.write(compressed_data)
            
            # עדכון מטא-דאטה
            self.metadata[symbol] = {
                'last_updated': datetime.now().isoformat(),
                'rows': len(data),
                'source': 'api',
                'file_size': file_path.stat().st_size
            }
            self._save_metadata()
            
            # עדכון אינדקס
            self.data_index[symbol] = {
                'last_updated': datetime.now().isoformat(),
                'days_available': len(data)
            }
            self._save_index()
            
            logger.info(f"נשמרו {len(data)} שורות עבור {symbol}")
            
        except Exception as e:
            logger.error(f"שגיאה באחסון נתונים עבור {symbol}: {e}")
    
    def get_multiple_stocks(self, symbols: List[str], days: int = 90) -> Dict[str, pd.DataFrame]:
        """שליפת נתונים למספר מניות"""
        results = {}
        
        for symbol in symbols:
            logger.info(f"שליפת נתונים עבור {symbol}")
            data = self.get_stock_data(symbol, days)
            if data is not None:
                results[symbol] = data
            else:
                logger.warning(f"לא הצלחנו לקבל נתונים עבור {symbol}")
        
        return results
    
    def get_data_status(self) -> Dict:
        """סטטוס הנתונים במערכת"""
        try:
            status = {
                'total_files': 0,
                'total_symbols': 0,
                'recent_updates': [],
                'missing_symbols': []
            }
            
            # ספירת קבצים
            if self.historical_dir.exists():
                files = list(self.historical_dir.glob("*.csv.gz")) + list(self.historical_dir.glob("*.csv"))
                status['total_files'] = len(files)
                status['total_symbols'] = len(files) # This is a simplification, ideally count unique symbols
                
                # בדיקת עדכונים אחרונים
                for file_path in files:
                    symbol = file_path.stem.replace('.csv', '').replace('.csv.gz', '').upper()
                    if symbol in self.metadata:
                        last_updated = self.metadata[symbol].get('last_updated', 'Unknown')
                        status['recent_updates'].append({
                            'symbol': symbol,
                            'last_updated': last_updated,
                            'rows': self.metadata[symbol].get('rows', 0)
                        })
            
            return status
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת סטטוס: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """ניקוי נתונים ישנים"""
        logger.info(f"ניקוי נתונים ישנים מ-{days_to_keep} ימים")
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for file_path in self.historical_dir.glob("*.csv.gz") + self.historical_dir.glob("*.csv"):
            symbol = file_path.stem.replace('.csv', '').replace('.csv.gz', '').upper()
            df = self._decompress_data(file_path.read_bytes())
            
            if not df.empty:
                df['date'] = df['date'] # Assuming 'date' is the index
                df_filtered = df[df['date'] >= cutoff_date]
                
                if len(df_filtered) < len(df):
                    compressed_data = self._compress_data(df_filtered)
                    with open(file_path, 'wb') as f:
                        f.write(compressed_data)
                    logger.info(f"נוקו נתונים ישנים עבור {symbol}")
    
    def get_performance_stats(self) -> Dict:
        """קבלת סטטיסטיקות ביצועים"""
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': self._cache_hits / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0,
            'cache_size': len(self._data_cache),
            'compression_enabled': self.enable_compression,
            'indexing_enabled': self.enable_indexing
        }
    
    def optimize_storage(self):
        """אופטימיזציה של אחסון הנתונים"""
        logger.info("מתחיל אופטימיזציה של אחסון")
        
        # דחיסה מחדש של כל הקבצים
        for file_path in self.historical_dir.glob("*.csv"):
            if not file_path.name.endswith('.gz'):
                symbol = file_path.stem.upper()
                logger.info(f"דחיסת קובץ עבור {symbol}")
                
                # קריאת הקובץ
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                
                # שמירה דחוסה
                compressed_data = self._compress_data(df)
                compressed_path = self._get_file_path(symbol, compressed=True)
                
                with open(compressed_path, 'wb') as f:
                    f.write(compressed_data)
                
                # מחיקת הקובץ המקורי
                file_path.unlink()
        
        # עדכון אינדקס
        self._rebuild_index()
        logger.info("אופטימיזציה הושלמה")
    
    def _rebuild_index(self):
        """בנייה מחדש של האינדקס"""
        self.data_index = {}
        
        for file_path in self.historical_dir.glob("*.csv.gz") + self.historical_dir.glob("*.csv"):
            symbol = file_path.stem.replace('.csv', '').replace('.csv.gz', '').upper()
            
            try:
                df = self._decompress_data(file_path.read_bytes())
                self.data_index[symbol] = {
                    'last_updated': datetime.now().isoformat(),
                    'days_available': len(df),
                    'file_size': file_path.stat().st_size,
                    'compressed': file_path.name.endswith('.gz')
                }
            except Exception as e:
                logger.warning(f"שגיאה בבניית אינדקס עבור {symbol}: {e}")
        
        self._save_index()
    
    def batch_process(self, symbols: List[str], days: int = 90, 
                     include_live: bool = True, max_workers: int = 4) -> Dict[str, pd.DataFrame]:
        """עיבוד מרובה מניות במקביל"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # יצירת משימות
            future_to_symbol = {
                executor.submit(self.get_stock_data, symbol, days, include_live): symbol
                for symbol in symbols
            }
            
            # איסוף תוצאות
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    results[symbol] = data
                    logger.info(f"הושלם עיבוד עבור {symbol}")
                except Exception as e:
                    logger.error(f"שגיאה בעיבוד {symbol}: {e}")
                    results[symbol] = None
        
        return results

    def get_technical_indicators(self, symbol: str, indicator: str = 'all', 
                                days: int = 90) -> Optional[pd.DataFrame]:
        """
        שליפת אינדיקטורים טכניים
        
        Args:
            symbol: סימבול המניה
            indicator: סוג האינדיקטור (rsi, macd, bollinger, all)
            days: מספר ימים נדרש
            
        Returns:
            DataFrame עם אינדיקטורים טכניים
        """
        try:
            # בדיקה בנתונים מקומיים
            local_file = self.technical_dir / str(indicator) / "daily" / f"{symbol.upper()}.csv.gz"
            if local_file.exists():
                df = self._decompress_data(local_file.read_bytes())
                if len(df) >= days:
                    return df.head(days)
            
            # אם אין נתונים מקומיים, חישוב מהנתונים הבסיסיים
            price_data = self.get_stock_data(symbol, days)
            if price_data is None or price_data.empty:
                return None
            
            # חישוב אינדיקטורים
            indicators = self._calculate_technical_indicators(price_data, indicator)
            
            # שמירה מקומית
            self._save_technical_data(symbol, indicator, indicators)
            
            return indicators
            
        except Exception as e:
            logger.error(f"שגיאה בחישוב אינדיקטורים עבור {symbol}: {e}")
            return None
    
    def _calculate_technical_indicators(self, price_data: pd.DataFrame, 
                                      indicator: str) -> pd.DataFrame:
        """חישוב אינדיקטורים טכניים"""
        try:
            if price_data.empty or len(price_data) < 20:
                logger.warning(f"נתונים לא מספיקים לחישוב אינדיקטורים: {len(price_data)} שורות")
                return pd.DataFrame()
            
            # וידוא שיש עמודות נדרשות
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in price_data.columns]
            if missing_columns:
                logger.error(f"חסרות עמודות נדרשות: {missing_columns}")
                return pd.DataFrame()
            
            # ניסיון להשתמש ב-TA-Lib
            try:
                import talib
                return self._calculate_talib_indicators(price_data, indicator)
            except (ImportError, ModuleNotFoundError):
                logger.info("TA-Lib לא מותקן, משתמש בספריית ta")
                return self._calculate_ta_indicators(price_data, indicator)
            except Exception as e:
                logger.warning(f"TA-Lib נכשל, משתמש בספריית ta: {e}")
                return self._calculate_ta_indicators(price_data, indicator)
                
        except Exception as e:
            logger.error(f"שגיאה בחישוב אינדיקטורים עבור {indicator}: {e}")
            return pd.DataFrame()
    
    def _calculate_talib_indicators(self, price_data: pd.DataFrame, indicator: str) -> pd.DataFrame:
        """חישוב אינדיקטורים באמצעות TA-Lib"""
        import talib
        
        result = pd.DataFrame(index=price_data.index)
        
        if indicator == 'all' or indicator == 'rsi':
            result['rsi'] = talib.RSI(price_data['close'].values, timeperiod=14)
        
        if indicator == 'all' or indicator == 'macd':
            macd, macd_signal, macd_hist = talib.MACD(price_data['close'].values)
            result['macd'] = macd
            result['macd_signal'] = macd_signal
            result['macd_histogram'] = macd_hist
        
        if indicator == 'all' or indicator == 'bollinger':
            upper, middle, lower = talib.BBANDS(price_data['close'].values)
            result['bb_upper'] = upper
            result['bb_middle'] = middle
            result['bb_lower'] = lower
        
        if indicator == 'all' or indicator == 'sma':
            result['sma_20'] = talib.SMA(price_data['close'].values, timeperiod=20)
            result['sma_50'] = talib.SMA(price_data['close'].values, timeperiod=50)
            result['sma_200'] = talib.SMA(price_data['close'].values, timeperiod=200)
        
        if indicator == 'all' or indicator == 'ema':
            result['ema_12'] = talib.EMA(price_data['close'].values, timeperiod=12)
            result['ema_26'] = talib.EMA(price_data['close'].values, timeperiod=26)
        
        if indicator == 'all' or indicator == 'stochastic':
            slowk, slowd = talib.STOCH(price_data['high'].values, price_data['low'].values, 
                                      price_data['close'].values)
            result['stoch_k'] = slowk
            result['stoch_d'] = slowd
        
        if indicator == 'all' or indicator == 'williams_r':
            result['williams_r'] = talib.WILLR(price_data['high'].values, price_data['low'].values, 
                                              price_data['close'].values, timeperiod=14)
        
        if indicator == 'all' or indicator == 'cci':
            result['cci'] = talib.CCI(price_data['high'].values, price_data['low'].values, 
                                     price_data['close'].values, timeperiod=14)
        
        if indicator == 'all' or indicator == 'atr':
            result['atr'] = talib.ATR(price_data['high'].values, price_data['low'].values, 
                                     price_data['close'].values, timeperiod=14)
        
        if indicator == 'all' or indicator == 'adx':
            result['adx'] = talib.ADX(price_data['high'].values, price_data['low'].values, 
                                     price_data['close'].values, timeperiod=14)
        
        return result.dropna()
    
    def _calculate_ta_indicators(self, price_data: pd.DataFrame, indicator: str) -> pd.DataFrame:
        """חישוב אינדיקטורים באמצעות ספריית ta"""
        import ta
        
        result = pd.DataFrame(index=price_data.index)
        
        if indicator == 'all' or indicator == 'rsi':
            result['rsi'] = ta.momentum.RSIIndicator(price_data['close']).rsi()
        
        if indicator == 'all' or indicator == 'macd':
            macd = ta.trend.MACD(price_data['close'])
            result['macd'] = macd.macd()
            result['macd_signal'] = macd.macd_signal()
            result['macd_histogram'] = macd.macd_diff()
        
        if indicator == 'all' or indicator == 'bollinger':
            bb = ta.volatility.BollingerBands(price_data['close'])
            result['bb_upper'] = bb.bollinger_hband()
            result['bb_middle'] = bb.bollinger_mavg()
            result['bb_lower'] = bb.bollinger_lband()
        
        if indicator == 'all' or indicator == 'sma':
            result['sma_20'] = ta.trend.SMAIndicator(price_data['close'], window=20).sma_indicator()
            result['sma_50'] = ta.trend.SMAIndicator(price_data['close'], window=50).sma_indicator()
            result['sma_200'] = ta.trend.SMAIndicator(price_data['close'], window=200).sma_indicator()
        
        if indicator == 'all' or indicator == 'ema':
            result['ema_12'] = ta.trend.EMAIndicator(price_data['close'], window=12).ema_indicator()
            result['ema_26'] = ta.trend.EMAIndicator(price_data['close'], window=26).ema_indicator()
        
        if indicator == 'all' or indicator == 'stochastic':
            stoch = ta.momentum.StochasticOscillator(price_data['high'], price_data['low'], price_data['close'])
            result['stoch_k'] = stoch.stoch()
            result['stoch_d'] = stoch.stoch_signal()
        
        if indicator == 'all' or indicator == 'williams_r':
            result['williams_r'] = ta.momentum.WilliamsRIndicator(price_data['high'], price_data['low'], price_data['close']).williams_r()
        
        if indicator == 'all' or indicator == 'cci':
            result['cci'] = ta.trend.CCIIndicator(price_data['high'], price_data['low'], price_data['close']).cci()
        
        if indicator == 'all' or indicator == 'atr':
            result['atr'] = ta.volatility.AverageTrueRange(price_data['high'], price_data['low'], price_data['close']).average_true_range()
        
        if indicator == 'all' or indicator == 'adx':
            result['adx'] = ta.trend.ADXIndicator(price_data['high'], price_data['low'], price_data['close']).adx()
        
        return result.dropna()
    

    
    def _save_technical_data(self, symbol: str, indicator: str, data: pd.DataFrame):
        """שמירת נתוני אינדיקטורים טכניים"""
        try:
            # שמירה לכל אינדיקטור בנפרד
            for col in data.columns:
                if col != 'date' and not pd.isna(data[col]).all():
                    # יצירת DataFrame נפרד לכל אינדיקטור
                    indicator_data = pd.DataFrame({
                        'date': data.index,
                        'symbol': symbol,
                        'value': data[col],
                        'indicator': col
                    })
                    
                    # הסרת שורות עם NaN
                    indicator_data = indicator_data.dropna()
                    
                    if not indicator_data.empty:
                        # שמירה בתיקייה הנכונה לפי סוג האינדיקטור
                        if 'rsi' in col.lower():
                            indicator_dir = self.technical_dir / "rsi" / "daily"
                        elif 'macd' in col.lower():
                            indicator_dir = self.technical_dir / "macd" / "daily"
                        elif 'bollinger' in col.lower() or 'bb_' in col.lower():
                            indicator_dir = self.technical_dir / "bollinger" / "daily"
                        elif 'sma' in col.lower():
                            indicator_dir = self.technical_dir / "sma" / "daily"
                        elif 'ema' in col.lower():
                            indicator_dir = self.technical_dir / "ema" / "daily"
                        elif 'stoch' in col.lower():
                            indicator_dir = self.technical_dir / "stochastic" / "daily"
                        elif 'williams' in col.lower():
                            indicator_dir = self.technical_dir / "williams_r" / "daily"
                        elif 'cci' in col.lower():
                            indicator_dir = self.technical_dir / "cci" / "daily"
                        elif 'atr' in col.lower():
                            indicator_dir = self.technical_dir / "atr" / "daily"
                        elif 'adx' in col.lower():
                            indicator_dir = self.technical_dir / "adx" / "daily"
                        else:
                            # ברירת מחדל - שמירה בתיקיית all
                            indicator_dir = self.technical_dir / "all" / "daily"
                        
                        indicator_dir.mkdir(parents=True, exist_ok=True)
                        file_path = indicator_dir / f"{symbol.upper()}.csv.gz"
                        compressed_data = self._compress_data(indicator_data)
                        
                        with open(file_path, 'wb') as f:
                            f.write(compressed_data)
            
            logger.info(f"נשמרו אינדיקטורים טכניים עבור {symbol}")
            
        except Exception as e:
            logger.error(f"שגיאה בשמירת אינדיקטורים עבור {symbol}: {e}")
    
    def get_news_sentiment(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        שליפת נתוני חדשות ורגשות
        
        Args:
            symbol: סימבול המניה
            days: מספר ימים נדרש
            
        Returns:
            DataFrame עם נתוני חדשות ורגשות
        """
        try:
            # בדיקה בנתונים מקומיים
            local_file = self.news_dir / "financial_news" / f"{symbol.upper()}.csv.gz"
            if local_file.exists():
                df = self._decompress_data(local_file.read_bytes())
                if len(df) >= days:
                    return df.head(days)
            
            # שליפה מ-API
            news_data = self._fetch_news_data(symbol, days)
            if news_data is not None and not news_data.empty:
                self._save_news_data(symbol, news_data)
                return news_data
            
            return None
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת חדשות עבור {symbol}: {e}")
            return None
    
    def _fetch_news_data(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """שליפת נתוני חדשות מ-API"""
        try:
            # בדיקת API key
            api_key = APICredentials.get_fmp_key()
            if not api_key:
                logger.error("FMP API key לא נמצא")
                return self._try_alternative_news_sources(symbol, days)
            
            # ניסיון מ-FMP עם פרמטרים שונים
            try:
                # ניסיון 1: עם ticker ספציפי
                news_data = self.fmp_client.fmp_get_stock_news(symbol, limit=days*5, verify_ssl=False)
                if news_data is not None and len(news_data) > 0:
                    logger.info(f"נשלפו {len(news_data)} חדשות מ-FMP עבור {symbol}")
                    df = pd.DataFrame(news_data)
                    return df
                
                # ניסיון 2: ללא ticker ספציפי (חדשות כלליות)
                news_data = self.fmp_client.fmp_get_stock_news(limit=days*5, verify_ssl=False)
                if news_data is not None and len(news_data) > 0:
                    # סינון לפי symbol
                    filtered_news = [news for news in news_data if symbol.upper() in news.get('title', '').upper() or 
                                   symbol.upper() in news.get('text', '').upper()]
                    if filtered_news:
                        logger.info(f"נשלפו {len(filtered_news)} חדשות מ-FMP (סוננו) עבור {symbol}")
                        df = pd.DataFrame(filtered_news)
                        return df
                
            except Exception as e:
                logger.warning(f"FMP חדשות נכשל עבור {symbol}: {e}")
            
            # ניסיון מקורות חלופיים
            return self._try_alternative_news_sources(symbol, days)
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת חדשות מ-API עבור {symbol}: {e}")
            return self._try_alternative_news_sources(symbol, days)
    
    def _try_alternative_news_sources(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """ניסיון מקורות חדשות חלופיים"""
        try:
            # ניסיון מ-Yahoo Finance RSS (מקור חופשי)
            try:
                yahoo_news = self._get_yahoo_finance_news(symbol, days)
                if yahoo_news is not None and len(yahoo_news) > 0:
                    logger.info(f"נשלפו {len(yahoo_news)} חדשות מ-Yahoo Finance עבור {symbol}")
                    return pd.DataFrame(yahoo_news)
            except Exception as e:
                logger.warning(f"Yahoo Finance חדשות נכשל עבור {symbol}: {e}")
            
            # ניסיון מ-Google News RSS (מקור חופשי)
            try:
                google_news = self._get_google_news(symbol, days)
                if google_news is not None and len(google_news) > 0:
                    logger.info(f"נשלפו {len(google_news)} חדשות מ-Google News עבור {symbol}")
                    return pd.DataFrame(google_news)
            except Exception as e:
                logger.warning(f"Google News חדשות נכשל עבור {symbol}: {e}")
            
            # ניסיון מ-Seeking Alpha RSS (מקור חופשי)
            try:
                seeking_alpha_news = self._get_seeking_alpha_news(symbol, days)
                if seeking_alpha_news is not None and len(seeking_alpha_news) > 0:
                    logger.info(f"נשלפו {len(seeking_alpha_news)} חדשות מ-Seeking Alpha עבור {symbol}")
                    return pd.DataFrame(seeking_alpha_news)
            except Exception as e:
                logger.warning(f"Seeking Alpha חדשות נכשל עבור {symbol}: {e}")
            
            # ניסיון מ-Finnhub News (יש לנו API key)
            try:
                finnhub_news = self._get_finnhub_news(symbol, days)
                if finnhub_news is not None and len(finnhub_news) > 0:
                    logger.info(f"נשלפו {len(finnhub_news)} חדשות מ-Finnhub עבור {symbol}")
                    return pd.DataFrame(finnhub_news)
            except Exception as e:
                logger.warning(f"Finnhub חדשות נכשל עבור {symbol}: {e}")
            
            # ניסיון מ-NewsData API
            try:
                newsdata_news = self._get_newsdata_news(symbol, days)
                if newsdata_news is not None and len(newsdata_news) > 0:
                    logger.info(f"נשלפו {len(newsdata_news)} חדשות מ-NewsData עבור {symbol}")
                    return pd.DataFrame(newsdata_news)
            except Exception as e:
                logger.warning(f"NewsData חדשות נכשל עבור {symbol}: {e}")
            
            # ניסיון מ-Alpha Vantage News
            try:
                alpha_news = self._get_alpha_vantage_news(symbol, days)
                if alpha_news is not None and len(alpha_news) > 0:
                    logger.info(f"נשלפו {len(alpha_news)} חדשות מ-Alpha Vantage עבור {symbol}")
                    return pd.DataFrame(alpha_news)
            except Exception as e:
                logger.warning(f"Alpha Vantage חדשות נכשל עבור {symbol}: {e}")
            
            logger.error(f"כל מקורות החדשות נכשלו עבור {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"שגיאה בניסיון מקורות חלופיים עבור {symbol}: {e}")
            return None
    
    def _get_yahoo_finance_news(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """שליפת חדשות מ-Yahoo Finance RSS"""
        try:
            import feedparser
            from datetime import datetime, timedelta
            
            # Yahoo Finance RSS feed
            rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
            
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                return None
            
            news_data = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for entry in feed.entries[:days*3]:  # יותר חדשות ליום
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if pub_date >= cutoff_date:
                        news_data.append({
                            'date': pub_date.strftime('%Y-%m-%d'),
                            'symbol': symbol,
                            'headline': entry.title,
                            'summary': entry.summary if hasattr(entry, 'summary') else '',
                            'source': 'Yahoo Finance',
                            'url': entry.link,
                            'category': 'general'
                        })
                except Exception as e:
                    logger.warning(f"שגיאה בעיבוד חדשה מ-Yahoo: {e}")
                    continue
            
            return news_data
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת חדשות מ-Yahoo Finance: {e}")
            return None
    
    def _get_newsdata_news(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """שליפת חדשות מ-NewsData API"""
        try:
            import requests
            from datetime import datetime, timedelta
            
            api_key = APICredentials.get_newsdata_key()
            if not api_key:
                return None
            
            # NewsData API endpoint
            url = "https://newsdata.io/api/1/news"
            params = {
                'apikey': api_key,
                'q': symbol,
                'language': 'en',
                'country': 'us'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('results'):
                return None
            
            news_data = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for article in data['results'][:days*3]:
                try:
                    pub_date = datetime.fromisoformat(article['pubDate'].replace('Z', '+00:00'))
                    if pub_date >= cutoff_date:
                        news_data.append({
                            'date': pub_date.strftime('%Y-%m-%d'),
                            'symbol': symbol,
                            'headline': article['title'],
                            'summary': article.get('description', ''),
                            'source': article.get('source_id', 'NewsData'),
                            'url': article['link'],
                            'category': article.get('category', ['general'])[0] if article.get('category') else 'general'
                        })
                except Exception as e:
                    logger.warning(f"שגיאה בעיבוד חדשה מ-NewsData: {e}")
                    continue
            
            return news_data
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת חדשות מ-NewsData: {e}")
            return None
    
    def _get_alpha_vantage_news(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """שליפת חדשות מ-Alpha Vantage API"""
        try:
            import requests
            from datetime import datetime, timedelta
            
            api_key = APICredentials.get_alpha_vantage_key()
            if not api_key:
                return None
            
            # Alpha Vantage News API endpoint
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'apikey': api_key,
                'limit': min(days*3, 50)  # Alpha Vantage מגביל ל-50
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('feed'):
                return None
            
            news_data = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for article in data['feed']:
                try:
                    pub_date = datetime.fromisoformat(article['time_published'].replace('Z', '+00:00'))
                    if pub_date >= cutoff_date:
                        news_data.append({
                            'date': pub_date.strftime('%Y-%m-%d'),
                            'symbol': symbol,
                            'headline': article['title'],
                            'summary': article.get('summary', ''),
                            'source': article.get('source', 'Alpha Vantage'),
                            'url': article.get('url', ''),
                            'category': article.get('category_within_source', 'general')
                        })
                except Exception as e:
                    logger.warning(f"שגיאה בעיבוד חדשה מ-Alpha Vantage: {e}")
                    continue
            
            return news_data
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת חדשות מ-Alpha Vantage: {e}")
            return None
    
    def _get_finnhub_news(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """שליפת חדשות מ-Finnhub API"""
        try:
            import requests
            from datetime import datetime, timedelta
            
            api_key = APICredentials.get_finnhub_key()
            if not api_key:
                return None
            
            # Finnhub News API endpoint
            url = "https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': symbol,
                'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'to': datetime.now().strftime('%Y-%m-%d'),
                'token': api_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                return None
            
            news_data = []
            
            for article in data[:days*3]:  # הגבלה למספר סביר
                try:
                    pub_date = datetime.fromtimestamp(article['datetime'])
                    news_data.append({
                        'date': pub_date.strftime('%Y-%m-%d'),
                        'symbol': symbol,
                        'headline': article['headline'],
                        'summary': article.get('summary', ''),
                        'source': article.get('source', 'Finnhub'),
                        'url': article.get('url', ''),
                        'category': article.get('category', 'general')
                    })
                except Exception as e:
                    logger.warning(f"שגיאה בעיבוד חדשה מ-Finnhub: {e}")
                    continue
            
            return news_data
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת חדשות מ-Finnhub: {e}")
            return None
    
    def _get_google_news(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """שליפת חדשות מ-Google News RSS"""
        try:
            import feedparser
            from datetime import datetime, timedelta
            
            # Google News RSS feed
            rss_url = f"https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                return None
            
            news_data = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for entry in feed.entries[:days*3]:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if pub_date >= cutoff_date:
                        news_data.append({
                            'date': pub_date.strftime('%Y-%m-%d'),
                            'symbol': symbol,
                            'headline': entry.title,
                            'summary': entry.summary if hasattr(entry, 'summary') else '',
                            'source': 'Google News',
                            'url': entry.link,
                            'category': 'general'
                        })
                except Exception as e:
                    logger.warning(f"שגיאה בעיבוד חדשה מ-Google News: {e}")
                    continue
            
            return news_data
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת חדשות מ-Google News: {e}")
            return None
    
    def _get_seeking_alpha_news(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """שליפת חדשות מ-Seeking Alpha RSS"""
        try:
            import feedparser
            from datetime import datetime, timedelta
            
            # Seeking Alpha RSS feed
            rss_url = f"https://seekingalpha.com/feed/symbol/{symbol}"
            
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                return None
            
            news_data = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for entry in feed.entries[:days*3]:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    if pub_date >= cutoff_date:
                        news_data.append({
                            'date': pub_date.strftime('%Y-%m-%d'),
                            'symbol': symbol,
                            'headline': entry.title,
                            'summary': entry.summary if hasattr(entry, 'summary') else '',
                            'source': 'Seeking Alpha',
                            'url': entry.link,
                            'category': 'financial'
                        })
                except Exception as e:
                    logger.warning(f"שגיאה בעיבוד חדשה מ-Seeking Alpha: {e}")
                    continue
            
            return news_data
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת חדשות מ-Seeking Alpha: {e}")
            return None
    
    def _generate_demo_news(self, symbol: str, days: int) -> pd.DataFrame:
        """יצירת חדשות מדומות"""
        try:
            from datetime import datetime, timedelta
            import random
            
            news_templates = [
                f"{symbol} Reports Strong Q4 Earnings",
                f"New {symbol} Product Announced",
                f"{symbol} Expands Business Operations",
                f"{symbol} Stock Performance Update",
                f"{symbol} Financial Results Released",
                f"{symbol} Announces Strategic Partnership",
                f"{symbol} Market Analysis Report",
                f"{symbol} Investor Relations Update"
            ]
            
            news_data = []
            for i in range(min(days, 10)):  # מקסימום 10 חדשות
                news_date = datetime.now() - timedelta(days=random.randint(1, days))
                
                news_data.append({
                    'date': news_date.strftime('%Y-%m-%d'),
                    'symbol': symbol,
                    'headline': random.choice(news_templates),
                    'summary': f'Demo news article about {symbol} performance and market updates.',
                    'source': 'Demo News',
                    'url': f'https://demo-news.com/{symbol.lower()}-{i}',
                    'category': 'earnings' if 'earnings' in random.choice(news_templates).lower() else 'general'
                })
            
            df = pd.DataFrame(news_data)
            return df
            
        except Exception as e:
            logger.error(f"שגיאה ביצירת חדשות מדומות עבור {symbol}: {e}")
            return pd.DataFrame()
    
    def _save_news_data(self, symbol: str, data: pd.DataFrame):
        """שמירת נתוני חדשות"""
        try:
            news_dir = self.news_dir / "financial_news"
            news_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = news_dir / f"{symbol.upper()}.csv.gz"
            compressed_data = self._compress_data(data)
            
            with open(file_path, 'wb') as f:
                f.write(compressed_data)
            
            logger.info(f"נשמרו נתוני חדשות עבור {symbol}")
            
        except Exception as e:
            logger.error(f"שגיאה בשמירת חדשות עבור {symbol}: {e}")
    
    def get_fundamentals(self, symbol: str, statement_type: str = 'income') -> Optional[pd.DataFrame]:
        """
        שליפת נתונים פונדמנטליים
        
        Args:
            symbol: סימבול המניה
            statement_type: סוג הדוח (income, balance, cash_flow, ratios, company_info)
            
        Returns:
            DataFrame עם נתונים פונדמנטליים
        """
        try:
            # אם מבקשים נתוני חברה בסיסיים
            if statement_type == 'company_info':
                return self._get_company_info(symbol)
            
            # בדיקה בנתונים מקומיים
            local_file = self.fundamentals_dir / statement_type / f"{symbol.upper()}.csv.gz"
            if local_file.exists():
                df = self._decompress_data(local_file.read_bytes())
                return df
            
            # שליפה מ-API
            fundamentals_data = self._fetch_fundamentals_data(symbol, statement_type)
            if fundamentals_data is not None and not fundamentals_data.empty:
                self._save_fundamentals_data(symbol, statement_type, fundamentals_data)
                return fundamentals_data
            
            return None
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת נתונים פונדמנטליים עבור {symbol}: {e}")
            return None
    
    def _get_company_info(self, symbol: str) -> Optional[pd.DataFrame]:
        """שליפת נתוני חברה בסיסיים"""
        try:
            # בדיקה בנתונים מקומיים
            local_file = self.fundamentals_dir / "company_info" / f"{symbol.upper()}_info.csv"
            if local_file.exists():
                return pd.read_csv(local_file)
            
            # שליפה מ-API
            company_data = self.fmp_client.fmp_get_company_profile(symbol)
            if company_data is not None:
                # בדיקה אם זה DataFrame או dict
                if isinstance(company_data, dict):
                    # המרה ל-DataFrame
                    company_data = pd.DataFrame([company_data])
                
                if not company_data.empty:
                    # שמירה לקובץ CSV רגיל (לא דחוס)
                    company_info_dir = self.fundamentals_dir / "company_info"
                    company_info_dir.mkdir(parents=True, exist_ok=True)
                    
                    file_path = company_info_dir / f"{symbol.upper()}_info.csv"
                    company_data.to_csv(file_path, index=False)
                    
                    logger.info(f"נשמרו נתוני חברה עבור {symbol}")
                    return company_data
            
            return None
            
        except Exception as e:
            logger.error(f"שגיאה בשליפת נתוני חברה עבור {symbol}: {e}")
            return None
    
    def _fetch_fundamentals_data(self, symbol: str, statement_type: str) -> Optional[pd.DataFrame]:
        """שליפת נתונים פונדמנטליים מ-API"""
        try:
            if statement_type == 'income':
                return self.fmp_client.fmp_get_income_statement(symbol)
            elif statement_type == 'balance':
                return self.fmp_client.fmp_get_balance_sheet(symbol)
            elif statement_type == 'cash_flow':
                return self.fmp_client.fmp_get_cash_flow_statement(symbol)
            elif statement_type == 'ratios':
                return self.fmp_client.fmp_get_ratios_ttm(symbol)
            else:
                logger.warning(f"סוג דוח לא נתמך: {statement_type}")
                return None
                
        except Exception as e:
            logger.error(f"שגיאה בשליפת נתונים פונדמנטליים מ-API עבור {symbol}: {e}")
            return None
    
    def _save_fundamentals_data(self, symbol: str, statement_type: str, data: pd.DataFrame):
        """שמירת נתונים פונדמנטליים"""
        try:
            fundamentals_dir = self.fundamentals_dir / statement_type
            fundamentals_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = fundamentals_dir / f"{symbol.upper()}.csv.gz"
            compressed_data = self._compress_data(data)
            
            with open(file_path, 'wb') as f:
                f.write(compressed_data)
            
            logger.info(f"נשמרו נתונים פונדמנטליים עבור {symbol}")
            
        except Exception as e:
            logger.error(f"שגיאה בשמירת נתונים פונדמנטליים עבור {symbol}: {e}")
    
    def get_comprehensive_data(self, symbol: str, days: int = 90, 
                             include_technical: bool = True,
                             include_news: bool = True,
                             include_fundamentals: bool = False) -> Dict[str, pd.DataFrame]:
        """
        שליפת נתונים מקיפים למניה
        
        Args:
            symbol: סימבול המניה
            days: מספר ימים נדרש
            include_technical: האם לכלול אינדיקטורים טכניים
            include_news: האם לכלול חדשות
            include_fundamentals: האם לכלול נתונים פונדמנטליים
            
        Returns:
            מילון עם כל סוגי הנתונים
        """
        result = {}
        
        # נתוני מחירים בסיסיים
        result['price_data'] = self.get_stock_data(symbol, days)
        
        # אינדיקטורים טכניים
        if include_technical and result['price_data'] is not None:
            result['technical_indicators'] = self.get_technical_indicators(symbol, 'all', days)
        
        # חדשות ורגשות
        if include_news:
            result['news_sentiment'] = self.get_news_sentiment(symbol, min(days, 30))
        
        # נתונים פונדמנטליים
        if include_fundamentals:
            result['fundamentals'] = {}
            for statement_type in ['income', 'balance', 'cash_flow', 'ratios']:
                result['fundamentals'][statement_type] = self.get_fundamentals(symbol, statement_type)
        
        return result 

# יצירת מופע גלובלי
smart_data_manager = SmartDataManager() 