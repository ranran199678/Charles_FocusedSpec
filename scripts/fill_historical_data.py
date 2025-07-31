#!/usr/bin/env python3
"""
Fill Historical Data - מילוי נתונים היסטוריים מלאים
מוריד נתונים היסטוריים עבור כל המניות וממלא את התיקיות החסרות
"""

import os
import sys
import pandas as pd
import numpy as np
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import logging

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.smart_data_manager import smart_data_manager
from utils.data_fetcher import DataFetcher

# הגדרת לוגר
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HistoricalDataFiller:
    """מחלקה למילוי נתונים היסטוריים"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.smart_manager = smart_data_manager
        
        # רשימת מניות עיקריות
        self.main_symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", 
            "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "BAC",
            "ADBE", "CRM", "INTC", "ORCL", "CSCO", "PFE", "ABT", "TMO", "ACN",
            "WMT", "KO", "PEP", "AVGO", "COST", "DHR", "NEE", "LLY", "TXN",
            "HON", "UNP", "LOW", "UPS", "CAT", "DE", "BA", "AXP", "SPGI",
            "RTX", "IBM", "GE", "MMC", "BLK", "GS", "MS", "SCHW", "CME"
        ]
        
        # הגדרת תיקיות
        self.data_dir = Path("data")
        self.daily_dir = self.data_dir / "historical_prices" / "daily"
        self.weekly_dir = self.data_dir / "historical_prices" / "weekly"
        self.monthly_dir = self.data_dir / "historical_prices" / "monthly"
        
        # יצירת תיקיות אם לא קיימות
        self.daily_dir.mkdir(parents=True, exist_ok=True)
        self.weekly_dir.mkdir(parents=True, exist_ok=True)
        self.monthly_dir.mkdir(parents=True, exist_ok=True)
    
    def get_existing_symbols(self) -> list:
        """מחזיר רשימת מניות שכבר קיימות"""
        existing_files = list(self.daily_dir.glob("*.csv.gz"))
        return [f.stem for f in existing_files]
    
    def get_missing_symbols(self) -> list:
        """מחזיר רשימת מניות שחסרות"""
        existing = set(self.get_existing_symbols())
        return [s for s in self.main_symbols if s not in existing]
    
    def download_symbol_data(self, symbol: str, days: int = 365) -> pd.DataFrame:
        """מוריד נתונים למניה ספציפית"""
        try:
            logger.info(f"מוריד נתונים עבור {symbol}...")
            
            # ניסיון עם SmartDataManager
            df = self.smart_manager.get_stock_data(symbol, days, include_live=True)
            
            if df is not None and not df.empty:
                logger.info(f"✅ הורדו {len(df)} שורות עבור {symbol}")
                return df
            
            # fallback ל-DataFetcher
            logger.info(f"ניסיון עם DataFetcher עבור {symbol}...")
            df = self.data_fetcher.get_price_history(symbol, f"{days}d")
            
            if df is not None and not df.empty:
                logger.info(f"✅ הורדו {len(df)} שורות עבור {symbol} (DataFetcher)")
                return df
            
            logger.warning(f"❌ לא הצלחנו להוריד נתונים עבור {symbol}")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"שגיאה בהורדת נתונים עבור {symbol}: {e}")
            return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """שומר נתונים לקובץ דחוס"""
        try:
            if df.empty:
                return False
            
            # בחירת תיקייה
            if timeframe == "daily":
                target_dir = self.daily_dir
            elif timeframe == "weekly":
                target_dir = self.weekly_dir
            elif timeframe == "monthly":
                target_dir = self.monthly_dir
            else:
                raise ValueError(f"תדירות לא נתמכת: {timeframe}")
            
            # הוספת עמודת symbol
            df = df.copy()
            df['symbol'] = symbol
            
            # שמירה דחוסה
            file_path = target_dir / f"{symbol}.csv.gz"
            df.to_csv(file_path, compression='gzip', index=False)
            
            logger.info(f"✅ נשמר {symbol} ({timeframe}): {len(df)} שורות")
            return True
            
        except Exception as e:
            logger.error(f"שגיאה בשמירת {symbol} ({timeframe}): {e}")
            return False
    
    def resample_data(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """ממיר נתונים יומיים לשבועיים/חודשיים"""
        try:
            if df.empty:
                return df
            
            # הגדרת אינדקס תאריך
            if 'date' in df.columns:
                df = df.set_index('date')
            elif 'Date' in df.columns:
                df = df.set_index('Date')
            
            # המרה לתאריך
            df.index = pd.to_datetime(df.index)
            
            # Resampling
            if timeframe == "weekly":
                resampled = df.resample('W').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                })
            elif timeframe == "monthly":
                resampled = df.resample('M').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                })
            else:
                return df
            
            # הסרת שורות ריקות
            resampled = resampled.dropna()
            
            # איפוס אינדקס
            resampled = resampled.reset_index()
            resampled = resampled.rename(columns={resampled.index.name: 'date'})
            
            return resampled
            
        except Exception as e:
            logger.error(f"שגיאה ב-resampling ל-{timeframe}: {e}")
            return df
    
    def fill_all_data(self, symbols: list = None, days: int = 365):
        """ממלא נתונים לכל המניות"""
        if symbols is None:
            symbols = self.get_missing_symbols()
        
        logger.info(f"מתחיל מילוי נתונים עבור {len(symbols)} מניות...")
        
        results = {
            'success': [],
            'failed': [],
            'stats': {
                'total_symbols': len(symbols),
                'daily_files': 0,
                'weekly_files': 0,
                'monthly_files': 0
            }
        }
        
        for i, symbol in enumerate(symbols, 1):
            logger.info(f"מעבד {symbol} ({i}/{len(symbols)})...")
            
            try:
                # הורדת נתונים יומיים
                daily_df = self.download_symbol_data(symbol, days)
                
                if not daily_df.empty:
                    # שמירת נתונים יומיים
                    if self.save_data(daily_df, symbol, "daily"):
                        results['stats']['daily_files'] += 1
                    
                    # יצירת נתונים שבועיים
                    weekly_df = self.resample_data(daily_df, "weekly")
                    if self.save_data(weekly_df, symbol, "weekly"):
                        results['stats']['weekly_files'] += 1
                    
                    # יצירת נתונים חודשיים
                    monthly_df = self.resample_data(daily_df, "monthly")
                    if self.save_data(monthly_df, symbol, "monthly"):
                        results['stats']['monthly_files'] += 1
                    
                    results['success'].append(symbol)
                    logger.info(f"✅ הושלם {symbol}")
                else:
                    results['failed'].append(symbol)
                    logger.warning(f"❌ נכשל {symbol}")
                
                # השהייה בין בקשות
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"שגיאה בעיבוד {symbol}: {e}")
                results['failed'].append(symbol)
        
        return results
    
    def update_metadata(self):
        """מעדכן מטא-דאטה"""
        try:
            metadata = {
                'last_updated': datetime.now().isoformat(),
                'total_symbols': len(self.main_symbols),
                'daily_files': len(list(self.daily_dir.glob("*.csv.gz"))),
                'weekly_files': len(list(self.weekly_dir.glob("*.csv.gz"))),
                'monthly_files': len(list(self.monthly_dir.glob("*.csv.gz"))),
                'symbols': {}
            }
            
            # מידע על כל מניה
            for symbol in self.main_symbols:
                daily_file = self.daily_dir / f"{symbol}.csv.gz"
                if daily_file.exists():
                    try:
                        df = pd.read_csv(daily_file, compression='gzip')
                        metadata['symbols'][symbol] = {
                            'has_daily': True,
                            'daily_rows': len(df),
                            'date_range': {
                                'start': df['date'].min() if 'date' in df.columns else 'unknown',
                                'end': df['date'].max() if 'date' in df.columns else 'unknown'
                            }
                        }
                    except Exception as e:
                        metadata['symbols'][symbol] = {'error': str(e)}
                else:
                    metadata['symbols'][symbol] = {'has_daily': False}
            
            # שמירת מטא-דאטה
            metadata_file = self.data_dir / "metadata" / "data_status.json"
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ מטא-דאטה עודכן")
            
        except Exception as e:
            logger.error(f"שגיאה בעדכון מטא-דאטה: {e}")
    
    def print_summary(self, results: dict):
        """מדפיס סיכום התוצאות"""
        print("\n" + "="*60)
        print("📊 סיכום מילוי נתונים היסטוריים")
        print("="*60)
        print(f"📈 מניות שהושלמו: {len(results['success'])}")
        print(f"❌ מניות שנכשלו: {len(results['failed'])}")
        print(f"📄 קבצים יומיים: {results['stats']['daily_files']}")
        print(f"📄 קבצים שבועיים: {results['stats']['weekly_files']}")
        print(f"📄 קבצים חודשיים: {results['stats']['monthly_files']}")
        
        if results['success']:
            print(f"\n✅ מניות שהושלמו: {', '.join(results['success'])}")
        
        if results['failed']:
            print(f"\n❌ מניות שנכשלו: {', '.join(results['failed'])}")

def main():
    """פונקציה ראשית"""
    print("🚀 מתחיל מילוי נתונים היסטוריים...")
    
    filler = HistoricalDataFiller()
    
    # בדיקת מניות חסרות
    missing_symbols = filler.get_missing_symbols()
    print(f"📋 מניות חסרות: {len(missing_symbols)}")
    print(f"📋 מניות קיימות: {len(filler.get_existing_symbols())}")
    
    if not missing_symbols:
        print("✅ כל הנתונים כבר קיימים!")
        return
    
    # מילוי נתונים
    results = filler.fill_all_data(missing_symbols, days=365)
    
    # עדכון מטא-דאטה
    filler.update_metadata()
    
    # הדפסת סיכום
    filler.print_summary(results)
    
    print("\n🎉 מילוי נתונים היסטוריים הושלם!")

if __name__ == "__main__":
    main() 