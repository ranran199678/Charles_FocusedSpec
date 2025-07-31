"""
SMART DATA PROCESSOR - מעבד נתונים חכם
מעבד קבצים חדשים בלבד ולא מוחק קבצים מקוריים
"""

import os
import pandas as pd
import numpy as np
import sqlite3
import json
from datetime import datetime
import logging

class SmartDataProcessor:
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir
        self.raw_dir = f"{base_dir}/raw_price_data"
        self.processed_dir = f"{base_dir}/historical_prices/daily"
        self.db_path = f"{base_dir}/database/historical.db"
        self.processed_files_log = f"{base_dir}/metadata/processed_files.json"
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._setup_directories()
        self._setup_database()
        self._load_processed_files()
    
    def _setup_directories(self):
        directories = [
            self.raw_dir,
            self.processed_dir,
            f"{self.base_dir}/metadata",
            f"{self.base_dir}/database"
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_prices (
                date TEXT, symbol TEXT, open REAL, high REAL, low REAL, 
                close REAL, volume INTEGER, adjusted_close REAL,
                file_source TEXT, processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (date, symbol)
            )
        ''')
        conn.commit()
        conn.close()
        self.logger.info("Database setup complete")
    
    def _load_processed_files(self):
        try:
            if os.path.exists(self.processed_files_log):
                with open(self.processed_files_log, 'r', encoding='utf-8') as f:
                    self.processed_files = json.load(f)
            else:
                self.processed_files = {}
        except Exception as e:
            self.logger.warning(f"Cannot load processed files: {e}")
            self.processed_files = {}
    
    def _save_processed_files(self):
        try:
            os.makedirs(os.path.dirname(self.processed_files_log), exist_ok=True)
            with open(self.processed_files_log, 'w', encoding='utf-8') as f:
                json.dump(self.processed_files, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Cannot save processed files: {e}")
    
    def _get_file_hash(self, file_path):
        try:
            stat = os.stat(file_path)
            return f"{stat.st_size}_{stat.st_mtime}"
        except:
            return "unknown"
    
    def _is_file_new_or_changed(self, filename):
        file_path = os.path.join(self.raw_dir, filename)
        
        if not os.path.exists(file_path):
            return False
        
        current_hash = self._get_file_hash(file_path)
        
        if filename not in self.processed_files:
            self.logger.info(f"New file: {filename}")
            return True
        
        if self.processed_files[filename]['hash'] != current_hash:
            self.logger.info(f"File changed: {filename}")
            return True
        
        self.logger.info(f"File already processed: {filename}")
        return False
    
    def _read_raw_price_file(self, file_path):
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Columns in file: {list(df.columns)}")
            
            col_map = {
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Price': 'close',
                'Vol.': 'volume',
                'Volume': 'volume',
                'Adj Close': 'adjusted_close',
                'Change %': 'change_pct'
            }
            
            if 'Close' not in df.columns and 'Price' in df.columns:
                df['Close'] = df['Price']
            
            # הסרת כפילויות לפני המיפוי
            df = df.loc[:, ~df.columns.duplicated()]
            df.rename(columns=col_map, inplace=True)
            
            # הסרת כפילויות אחרי המיפוי
            df = df.loc[:, ~df.columns.duplicated()]
            
            self.logger.info(f"Columns after mapping: {list(df.columns)}")
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            numeric_cols = ['open', 'high', 'low', 'close']
            for col in numeric_cols:
                if col in df.columns:
                    self.logger.info(f"Converting column: {col}")
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            if 'volume' in df.columns:
                self.logger.info("Processing volume column")
                df['volume'] = df['volume'].astype(str).str.replace('M', '000000').str.replace('K', '000').str.replace('B', '000000000')
                df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            if 'adjusted_close' not in df.columns:
                df['adjusted_close'] = df['close']
            
            symbol = os.path.basename(file_path).split('_')[0].upper()
            df['symbol'] = symbol
            
            self.logger.info(f"Final shape: {df.shape}")
            return df.dropna()
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return pd.DataFrame()
    
    def _calculate_indicators(self, df):
        df = df.copy()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['ema_20'] = df['close'].ewm(span=20).mean()
        
        # Bollinger Bands
        df['bollinger_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bollinger_upper'] = df['bollinger_middle'] + (bb_std * 2)
        df['bollinger_lower'] = df['bollinger_middle'] - (bb_std * 2)
        
        # ATR - חישוב פשוט יותר
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        # חישוב True Range
        true_range = pd.DataFrame({
            'high_low': high_low,
            'high_close': high_close,
            'low_close': low_close
        }).max(axis=1)
        
        df['atr_14'] = true_range.rolling(14).mean()
        
        return df
    
    def _save_to_database(self, df, filename):
        conn = sqlite3.connect(self.db_path)
        
        # הוספת עמודת file_source
        df_with_source = df.copy()
        df_with_source['file_source'] = filename
        
        # בחירת עמודות נדרשות
        price_cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'adjusted_close', 'file_source']
        price_data = df_with_source[[col for col in price_cols if col in df_with_source.columns]].copy()
        
        # הוספת עמודת symbol אם לא קיימת
        if 'symbol' not in price_data.columns:
            price_data['symbol'] = df['symbol'].iloc[0]
        
        # שימוש ב-replace במקום append כדי למנוע כפילות
        price_data.to_sql('historical_prices', conn, if_exists='replace', index=False)
        conn.close()
    
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
    
    def _save_to_csv(self, df, filename):
        symbol = df['symbol'].iloc[0]
        
        # חילוץ שם הסימבול הנקי
        clean_symbol = self._extract_symbol_from_filename(filename)
        
        # זיהוי פרק זמן
        timeframe = self._detect_timeframe(filename)
        
        # יצירת תיקייה לפי פרק זמן
        timeframe_dir = os.path.join(self.base_dir, "historical_prices", timeframe)
        os.makedirs(timeframe_dir, exist_ok=True)
        
        # שם קובץ נקי
        output_file = os.path.join(timeframe_dir, f"{clean_symbol}.csv")
        
        if os.path.exists(output_file):
            existing_df = pd.read_csv(output_file)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=['date', 'symbol'])
            combined_df.to_csv(output_file, index=False)
        else:
            df.to_csv(output_file, index=False)
        
        self.logger.info(f"Saved: {output_file} (timeframe: {timeframe})")
    
    def process_single_file(self, filename):
        file_path = os.path.join(self.raw_dir, filename)
        
        try:
            self.logger.info(f"Processing: {filename}")
            
            df = self._read_raw_price_file(file_path)
            if df.empty:
                self.logger.error(f"Cannot read file: {filename}")
                return False
            
            df = self._calculate_indicators(df)
            
            self._save_to_csv(df, filename)
            self._save_to_database(df, filename)
            
            self.processed_files[filename] = {
                'hash': self._get_file_hash(file_path),
                'processed_at': datetime.now().isoformat(),
                'rows': len(df),
                'symbol': df['symbol'].iloc[0]
            }
            self._save_processed_files()
            
            self.logger.info(f"Successfully processed: {filename} ({len(df)} rows)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing {filename}: {e}")
            return False
    
    def process_new_files(self):
        if not os.path.exists(self.raw_dir):
            self.logger.error(f"Directory {self.raw_dir} does not exist")
            return
        
        files = [f for f in os.listdir(self.raw_dir) if f.endswith('.csv')]
        
        if not files:
            self.logger.info("No CSV files to process")
            return
        
        new_files = [f for f in files if self._is_file_new_or_changed(f)]
        
        if not new_files:
            self.logger.info("No new files to process")
            return
        
        self.logger.info(f"Found {len(new_files)} new files to process")
        
        for filename in new_files:
            self.process_single_file(filename)
        
        self.logger.info("Processing new files completed")
    
    def get_processing_status(self):
        if not os.path.exists(self.raw_dir):
            return {}
        
        files = [f for f in os.listdir(self.raw_dir) if f.endswith('.csv')]
        status = {
            'total_files': len(files),
            'processed_files': len(self.processed_files),
            'new_files': [],
            'processed_files_list': list(self.processed_files.keys())
        }
        
        for filename in files:
            if self._is_file_new_or_changed(filename):
                status['new_files'].append(filename)
        
        return status

def main():
    processor = SmartDataProcessor()
    
    status = processor.get_processing_status()
    print("Processing Status:")
    print(f"  Total files: {status['total_files']}")
    print(f"  Processed files: {status['processed_files']}")
    print(f"  New files: {len(status['new_files'])}")
    
    if status['new_files']:
        print(f"  New files: {status['new_files']}")
    
    processor.process_new_files()

if __name__ == "__main__":
    main() 