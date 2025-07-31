import pandas as pd
import numpy as np
import os
import sqlite3
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
# import talib  # נדרש להתקנה

class AdvancedIndicatorsProcessor:
    """
    מעבד מתקדם לאינדיקטורים טכניים
    מחשב אינדיקטורים מקבצי מחירים גולמיים ושומר במבנה תיקיות מאורגן
    """
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self.raw_dir = f"{base_dir}/raw_price_data"
        self.indicators_dir = f"{base_dir}/technical_indicators"
        self.db_path = f"{base_dir}/database/historical.db"
        
        # הגדרת לוגים
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # יצירת תיקיות אם לא קיימות
        self._setup_directories()
        self._setup_database()
    
    def _setup_directories(self):
        """יצירת תיקיות נדרשות"""
        indicators = [
            'rsi', 'macd', 'sma', 'ema', 'bollinger', 'atr',
            'stochastic', 'williams_r', 'cci', 'adx'
        ]
        timeframes = ['daily', 'hourly', 'weekly', 'monthly']
        
        for indicator in indicators:
            for timeframe in timeframes:
                path = f"{self.indicators_dir}/{indicator}/{timeframe}"
                os.makedirs(path, exist_ok=True)
        
        self.logger.info("תיקיות אינדיקטורים נוצרו בהצלחה")
    
    def _setup_database(self):
        """הגדרת מסד נתונים לאינדיקטורים"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טבלת אינדיקטורים מפורטים
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators_detailed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                indicator_type TEXT NOT NULL,
                indicator_value REAL,
                indicator_params TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date, timeframe, indicator_type)
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("מסד נתונים לאינדיקטורים הוגדר")
    
    def _read_raw_price_file(self, file_path: str) -> pd.DataFrame:
        """קריאת קובץ מחירים גולמי"""
        try:
            # קריאה עם זיהוי אוטומטי של פורמט
            df = pd.read_csv(file_path)
            
            # הדפסת עמודות לבדיקה
            self.logger.info(f"עמודות בקובץ: {list(df.columns)}")
            
            # מיפוי עמודות לפורמט סטנדרטי
            col_map = {
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Price': 'close',  # Price משמש כ-Close
                'Vol.': 'volume',
                'Volume': 'volume',
                'Adj Close': 'adjusted_close',
                'Change %': 'change_pct'
            }
            
            # הוספת עמודת Close אם לא קיימת
            if 'Close' not in df.columns and 'Price' in df.columns:
                df['Close'] = df['Price']
            
            # הסרת כפילויות בעמודות לפני המיפוי
            df = df.loc[:, ~df.columns.duplicated()]
            
            df.rename(columns=col_map, inplace=True)
            
            # הסרת כפילויות בעמודות אחרי המיפוי
            df = df.loc[:, ~df.columns.duplicated()]
            
            # הדפסת עמודות אחרי המיפוי
            self.logger.info(f"עמודות אחרי מיפוי: {list(df.columns)}")
            
            # המרת תאריכים
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # המרת עמודות מספריות
            numeric_cols = ['open', 'high', 'low', 'close']
            for col in numeric_cols:
                if col in df.columns:
                    self.logger.info(f"ממיר עמודה: {col}, סוג: {type(df[col])}")
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # טיפול מיוחד בעמודת volume
            if 'volume' in df.columns:
                # המרת suffixes כמו M, K, B וגם הסרת פסיקים
                volume_str = df['volume'].astype(str)
                volume_converted = volume_str.str.replace(',', '').str.replace('M', '000000').str.replace('K', '000').str.replace('B', '000000000')
                df['volume'] = pd.to_numeric(volume_converted, errors='coerce')
            
            # הוספת עמודת adjusted_close אם לא קיימת
            if 'adjusted_close' not in df.columns:
                df['adjusted_close'] = df['close']
            
            # הוספת עמודת symbol
            symbol = os.path.basename(file_path).split('_')[0].upper()
            df['symbol'] = symbol
            
            self.logger.info(f"עמודות אחרי עיבוד: {list(df.columns)}")
            self.logger.info(f"מספר שורות: {len(df)}")
            
            return df.dropna()
            
        except Exception as e:
            self.logger.error(f"שגיאה בקריאת קובץ {file_path}: {e}")
            import traceback
            self.logger.error(f"פירוט השגיאה: {traceback.format_exc()}")
            return pd.DataFrame()
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """חישוב RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """חישוב MACD"""
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def calculate_sma(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """חישוב SMA"""
        return df['close'].rolling(window=period).mean()
    
    def calculate_ema(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """חישוב EMA"""
        return df['close'].ewm(span=period).mean()
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """חישוב Bollinger Bands"""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """חישוב ATR"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.DataFrame({
            'high_low': high_low,
            'high_close': high_close,
            'low_close': low_close
        })
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """חישוב Stochastic Oscillator"""
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent
    
    def calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """חישוב Williams %R"""
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
        return williams_r
    
    def calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """חישוב CCI"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        
        # חישוב MAD (Mean Absolute Deviation)
        def mad_func(x):
            return np.mean(np.abs(x - x.mean()))
        
        mad = typical_price.rolling(window=period).apply(mad_func)
        cci = (typical_price - sma_tp) / (0.015 * mad)
        return cci
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """חישוב ADX"""
        # חישוב +DM ו--DM
        high_diff = df['high'].diff()
        low_diff = df['low'].diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = -low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        # חישוב TR
        tr = self.calculate_atr(df, period)
        
        # חישוב +DI ו--DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr)
        
        # חישוב DX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx, plus_di, minus_di
    
    def process_single_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """עיבוד קובץ בודד וחישוב כל האינדיקטורים"""
        self.logger.info(f"מעבד קובץ: {file_path}")
        
        # קריאת נתונים
        df = self._read_raw_price_file(file_path)
        if df.empty:
            return {}
        
        # חילוץ שם הסימבול הנקי משם הקובץ
        filename = os.path.basename(file_path)
        clean_symbol = self._extract_symbol_from_filename(filename)
        
        results = {}
        
        # חישוב אינדיקטורים
        indicators = {
            'rsi': self.calculate_rsi(df),
            'sma_20': self.calculate_sma(df, 20),
            'sma_50': self.calculate_sma(df, 50),
            'ema_20': self.calculate_ema(df, 20),
            'ema_50': self.calculate_ema(df, 50),
            'atr_14': self.calculate_atr(df, 14)
        }
        
        # MACD
        macd, signal, histogram = self.calculate_macd(df)
        indicators.update({
            'macd': macd,
            'macd_signal': signal,
            'macd_histogram': histogram
        })
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df)
        indicators.update({
            'bollinger_upper': bb_upper,
            'bollinger_middle': bb_middle,
            'bollinger_lower': bb_lower
        })
        
        # Stochastic
        stoch_k, stoch_d = self.calculate_stochastic(df)
        indicators.update({
            'stochastic_k': stoch_k,
            'stochastic_d': stoch_d
        })
        
        # Williams %R
        indicators['williams_r'] = self.calculate_williams_r(df)
        
        # CCI
        indicators['cci'] = self.calculate_cci(df)
        
        # ADX
        adx, plus_di, minus_di = self.calculate_adx(df)
        indicators.update({
            'adx': adx,
            'plus_di': plus_di,
            'minus_di': minus_di
        })
        
        # יצירת DataFrames נפרדים לכל אינדיקטור
        for indicator_name, indicator_values in indicators.items():
            if indicator_values is not None and not indicator_values.empty:
                indicator_df = pd.DataFrame({
                    'date': df['date'],
                    'symbol': clean_symbol,
                    'value': indicator_values
                })
                indicator_df = indicator_df.dropna()
                results[indicator_name] = indicator_df
        
        return results
    
    def _detect_timeframe(self, filename):
        """זיהוי פרק זמן לפי שם הקובץ"""
        filename_lower = filename.lower()
        
        # בדיקה לפי סיומות ספציפיות
        if '(1)' in filename or 'weekly' in filename_lower:
            return 'weekly'
        elif '(2)' in filename or 'monthly' in filename_lower:
            return 'monthly'
        elif '(3)' in filename or 'hourly' in filename_lower:
            return 'hourly'
        else:
            return 'daily'
    
    def _extract_symbol_from_filename(self, filename):
        """חילוץ שם הסימבול משם הקובץ"""
        # הסרת סיומות
        clean_name = filename.replace(' Stock Price History.csv', '').replace('.csv', '')
        
        # הסרת סיומות פרקי זמן
        clean_name = clean_name.replace(' (1)', '').replace(' (2)', '').replace(' (3)', '')
        
        return clean_name.upper()
    
    def save_indicators_to_files(self, indicators_dict: Dict[str, pd.DataFrame], symbol: str, timeframe: str):
        """שמירת אינדיקטורים לקבצים במבנה תיקיות"""
        for indicator_name, df in indicators_dict.items():
            if df.empty:
                continue
            
            # קביעת תיקיית יעד לפי סוג האינדיקטור
            indicator_type = indicator_name.split('_')[0]  # rsi, macd, sma, etc.
            
            output_dir = f"{self.indicators_dir}/{indicator_type}/{timeframe}"
            output_file = f"{output_dir}/{symbol}_{indicator_name}_{timeframe}.csv"
            
            df.to_csv(output_file, index=False)
            self.logger.info(f"נשמר: {output_file}")
    
    def save_indicators_to_database(self, indicators_dict: Dict[str, pd.DataFrame]):
        """שמירת אינדיקטורים למסד נתונים"""
        conn = sqlite3.connect(self.db_path)
        
        for indicator_name, df in indicators_dict.items():
            if df.empty:
                continue
            
            # הוספת מידע על האינדיקטור
            df['indicator_type'] = indicator_name
            df['timeframe'] = 'daily'  # כרגע רק daily
            
            # שמירה למסד נתונים
            df.to_sql('technical_indicators_detailed', conn, if_exists='append', index=False)
        
        conn.close()
        self.logger.info("אינדיקטורים נשמרו למסד נתונים")
    
    def process_all_files(self):
        """עיבוד כל קבצי המחירים הגולמיים"""
        if not os.path.exists(self.raw_dir):
            self.logger.error(f"תיקיית {self.raw_dir} לא קיימת")
            return
        
        files = [f for f in os.listdir(self.raw_dir) if f.endswith('.csv')]
        
        if not files:
            self.logger.warning(f"לא נמצאו קבצי CSV ב-{self.raw_dir}")
            return
        
        total_files = len(files)
        self.logger.info(f"נמצאו {total_files} קבצים לעיבוד")
        
        for i, file_name in enumerate(files, 1):
            file_path = os.path.join(self.raw_dir, file_name)
            self.logger.info(f"מעבד קובץ {i}/{total_files}: {file_name}")
            
            try:
                # עיבוד הקובץ
                indicators_dict = self.process_single_file(file_path)
                
                if indicators_dict:
                    # חילוץ שם הסימבול הנקי
                    clean_symbol = self._extract_symbol_from_filename(file_name)
                    
                    # זיהוי פרק זמן
                    timeframe = self._detect_timeframe(file_name)
                    
                    # שמירה לקבצים
                    self.save_indicators_to_files(indicators_dict, clean_symbol, timeframe)
                    
                    # שמירה למסד נתונים
                    self.save_indicators_to_database(indicators_dict)
                    
                    self.logger.info(f"הקובץ {file_name} עובד בהצלחה")
                else:
                    self.logger.warning(f"לא ניתן לעבד את הקובץ {file_name}")
                    
            except Exception as e:
                self.logger.error(f"שגיאה בעיבוד {file_name}: {e}")
        
        self.logger.info("עיבוד כל הקבצים הושלם")

def main():
    """הרצת המעבד"""
    processor = AdvancedIndicatorsProcessor()
    processor.process_all_files()

if __name__ == "__main__":
    main() 