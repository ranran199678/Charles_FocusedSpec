# -*- coding: utf-8 -*-
"""
מערכת ניהול נתונים היסטוריים מתקדמת - Charles FocusedSpec
יוצר: AI Lead Developer
"""
import os
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import logging

class EnhancedDataProcessor:
    def __init__(self):
        self.raw_dir = "data/raw_price_data"
        self.historical_dir = "data/historical_prices/daily"
        self.weekly_dir = "data/historical_prices/weekly"
        self.monthly_dir = "data/historical_prices/monthly"
        self.db_path = "data/database/historical.db"
        self.setup_directories()
        self.setup_database()
    
    def setup_directories(self):
        """יצירת תיקיות נדרשות"""
        directories = [
            "data/raw_price_data",
            "data/historical_prices/daily",
            "data/historical_prices/weekly",
            "data/historical_prices/monthly",
            "data/historical_prices/metadata",
            "data/technical_indicators",
            "data/database"
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def setup_database(self):
        """הגדרת מסד נתונים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_prices (
                date TEXT,
                symbol TEXT,
                timeframe TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                adjusted_close REAL,
                PRIMARY KEY (date, symbol, timeframe)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                date TEXT,
                symbol TEXT,
                timeframe TEXT,
                rsi_14 REAL,
                macd REAL,
                macd_signal REAL,
                sma_20 REAL,
                ema_20 REAL,
                bollinger_upper REAL,
                bollinger_lower REAL,
                atr_14 REAL,
                PRIMARY KEY (date, symbol, timeframe)
            )
        ''')
        conn.commit()
        conn.close()
    
    def calculate_enhanced_indicators(self, df):
        """חישוב אינדיקטורים מתקדמים"""
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
        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr_14'] = true_range.rolling(14).mean()
        return df
    
    def aggregate_to_weekly(self, df):
        """המרת נתונים יומיים לשבועיים"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # יצירת עמודת שבוע
        df['week'] = df['date'].dt.to_period('W')
        
        # חישוב נתונים שבועיים
        weekly_data = df.groupby('week').agg({
            'open': 'first',  # מחיר פתיחה של היום הראשון בשבוע
            'high': 'max',    # מחיר הגבוה ביותר בשבוע
            'low': 'min',     # מחיר הנמוך ביותר בשבוע
            'close': 'last',  # מחיר סגירה של היום האחרון בשבוע
            'volume': 'sum',  # סכום הנפח השבועי
            'adjusted_close': 'last'  # מחיר מותאם של היום האחרון
        }).reset_index()
        
        # המרת תאריך חזרה למחרוזת
        weekly_data['date'] = weekly_data['week'].dt.strftime('%Y-%m-%d')
        weekly_data = weekly_data.drop('week', axis=1)
        
        return weekly_data
    
    def aggregate_to_monthly(self, df):
        """המרת נתונים יומיים לחודשיים"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # יצירת עמודת חודש
        df['month'] = df['date'].dt.to_period('M')
        
        # חישוב נתונים חודשיים
        monthly_data = df.groupby('month').agg({
            'open': 'first',  # מחיר פתיחה של היום הראשון בחודש
            'high': 'max',    # מחיר הגבוה ביותר בחודש
            'low': 'min',     # מחיר הנמוך ביותר בחודש
            'close': 'last',  # מחיר סגירה של היום האחרון בחודש
            'volume': 'sum',  # סכום הנפח החודשי
            'adjusted_close': 'last'  # מחיר מותאם של היום האחרון
        }).reset_index()
        
        # המרת תאריך חזרה למחרוזת
        monthly_data['date'] = monthly_data['month'].dt.strftime('%Y-%m-%d')
        monthly_data = monthly_data.drop('month', axis=1)
        
        return monthly_data
    
    def calculate_timeframe_indicators(self, df, timeframe):
        """חישוב אינדיקטורים עבור טווח זמן ספציפי"""
        df = df.copy()
        
        # התאמת פרמטרים לפי טווח הזמן
        if timeframe == 'weekly':
            rsi_period = 14
            macd_fast = 12
            macd_slow = 26
            macd_signal = 9
            sma_period = 20
            ema_period = 20
            bb_period = 20
            atr_period = 14
        elif timeframe == 'monthly':
            rsi_period = 14
            macd_fast = 12
            macd_slow = 26
            macd_signal = 9
            sma_period = 20
            ema_period = 20
            bb_period = 20
            atr_period = 14
        else:  # daily
            rsi_period = 14
            macd_fast = 12
            macd_slow = 26
            macd_signal = 9
            sma_period = 20
            ema_period = 20
            bb_period = 20
            atr_period = 14
        
        # RSI
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(rsi_period).mean()
        avg_loss = loss.rolling(rsi_period).mean()
        rs = avg_gain / avg_loss
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_fast = df['close'].ewm(span=macd_fast).mean()
        ema_slow = df['close'].ewm(span=macd_slow).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=macd_signal).mean()
        
        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=sma_period).mean()
        df['ema_20'] = df['close'].ewm(span=ema_period).mean()
        
        # Bollinger Bands
        df['bollinger_middle'] = df['close'].rolling(window=bb_period).mean()
        bb_std = df['close'].rolling(window=bb_period).std()
        df['bollinger_upper'] = df['bollinger_middle'] + (bb_std * 2)
        df['bollinger_lower'] = df['bollinger_middle'] - (bb_std * 2)
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr_14'] = true_range.rolling(atr_period).mean()
        
        return df
    
    def process_all_files(self):
        """עיבוד כל הקבצים הגולמיים"""
        for file in os.listdir(self.raw_dir):
            if file.endswith(".csv"):
                self.process_single_file(file)
    
    def process_single_file(self, filename):
        """עיבוד קובץ בודד"""
        try:
            file_path = os.path.join(self.raw_dir, filename)
            df = pd.read_csv(file_path)
            
            print(f"📊 מעבד קובץ: {filename}")
            print(f"📋 עמודות זמינות: {list(df.columns)}")
            
            # מיפוי עמודות לפורמט הנדרש
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
                'Change %': 'change_pct',
                'Symbol': 'symbol'
            }
            
            # מיפוי עמודות
            df.rename(columns=col_map, inplace=True)
            
            # הוספת עמודת adjusted_close אם לא קיימת
            if 'adjusted_close' not in df.columns and 'close' in df.columns:
                df['adjusted_close'] = df['close']
            
            # הוספת עמודת symbol אם לא קיימת
            if 'symbol' not in df.columns:
                # חילוץ שם הסימבול משם הקובץ
                symbol = filename.replace(' Stock Price History.csv', '').replace('.csv', '')
                df['symbol'] = symbol
            
            # ניקוי נתונים
            df.dropna(how='all', inplace=True)
            df.drop_duplicates(inplace=True)
            
            # בדיקת עמודות נדרשות
            required_cols = {'date', 'open', 'high', 'low', 'close', 'volume'}
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                print(f"❌ קובץ {filename} חסר עמודות: {missing_cols}")
                print(f"עמודות זמינות: {list(df.columns)}")
                return
            
            # המרת תאריכים
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df.dropna(subset=['date'], inplace=True)
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            # המרת ערכים מספריים
            numeric_cols = ['open', 'high', 'low', 'close', 'adjusted_close']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # המרת volume בנפרד
            if 'volume' in df.columns:
                # המרת volume מ-"1,771,400" ל-1771400
                volume_str = df['volume'].astype(str)
                volume_converted = volume_str.str.replace(',', '').str.replace('M', '000000').str.replace('K', '000').str.replace('B', '000000000')
                df['volume'] = pd.to_numeric(volume_converted, errors='coerce')
                df = df[df['volume'].notna()]
            
            if 'close' in df.columns:
                df = df[df['close'] > 0]
            
            print(f"📊 נתונים אחרי ניקוי: {len(df)} שורות")
            
            # חישוב אינדיקטורים יומיים
            df_daily = self.calculate_enhanced_indicators(df)
            
            # יצירת נתונים שבועיים
            df_weekly = self.aggregate_to_weekly(df)
            df_weekly = self.calculate_timeframe_indicators(df_weekly, 'weekly')
            
            # יצירת נתונים חודשיים
            df_monthly = self.aggregate_to_monthly(df)
            df_monthly = self.calculate_timeframe_indicators(df_monthly, 'monthly')
            
            # שמירת קבצים
            if 'symbol' in df.columns and len(df) > 0:
                symbol = df['symbol'].iloc[0]
            else:
                symbol = filename.replace(' Stock Price History.csv', '').replace('.csv', '')
            
            # שמירת קבצים יומיים
            output_file_daily = os.path.join(self.historical_dir, f"{symbol}.csv")
            df_daily.to_csv(output_file_daily, index=False)
            
            # שמירת קבצים שבועיים
            output_file_weekly = os.path.join(self.weekly_dir, f"{symbol}.csv")
            df_weekly.to_csv(output_file_weekly, index=False)
            
            # שמירת קבצים חודשיים
            output_file_monthly = os.path.join(self.monthly_dir, f"{symbol}.csv")
            df_monthly.to_csv(output_file_monthly, index=False)
            
            # שמירה למסד נתונים
            self.save_to_database(df_daily, symbol, 'daily')
            self.save_to_database(df_weekly, symbol, 'weekly')
            self.save_to_database(df_monthly, symbol, 'monthly')
            
            print(f"✅ עובד: {filename} -> {symbol}")
            print(f"   📅 יומי: {len(df_daily)} שורות")
            print(f"   📅 שבועי: {len(df_weekly)} שורות")
            print(f"   📅 חודשי: {len(df_monthly)} שורות")
            
        except Exception as e:
            print(f"❌ שגיאה בעיבוד {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    def save_to_database(self, df, symbol, timeframe):
        """שמירה למסד נתונים"""
        conn = sqlite3.connect(self.db_path)
        
        # הוספת עמודת timeframe
        df_with_timeframe = df.copy()
        df_with_timeframe['timeframe'] = timeframe
        
        # שמירת נתוני מחירים
        price_cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'adjusted_close', 'timeframe']
        price_data = df_with_timeframe[[col for col in price_cols if col in df_with_timeframe.columns]].copy()
        price_data['symbol'] = symbol
        price_data.to_sql('historical_prices', conn, if_exists='replace', index=False)
        
        # שמירת אינדיקטורים
        indicator_cols = ['date', 'rsi_14', 'macd', 'macd_signal', 'sma_20', 'ema_20', 'bollinger_upper', 'bollinger_lower', 'atr_14', 'timeframe']
        indicator_data = df_with_timeframe[[col for col in indicator_cols if col in df_with_timeframe.columns]].copy()
        indicator_data['symbol'] = symbol
        indicator_data.to_sql('technical_indicators', conn, if_exists='replace', index=False)
        
        conn.close()

if __name__ == "__main__":
    processor = EnhancedDataProcessor()
    processor.process_all_files()
    print("✅ עיבוד נתונים הושלם!") 