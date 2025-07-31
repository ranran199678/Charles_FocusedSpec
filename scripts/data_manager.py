# -*- coding: utf-8 -*-
"""
DataManager - ניהול מאגר נתונים מרכזי למערכת Charles FocusedSpec
מנהל שליפה, בדיקת חוסרים, ועדכון נתונים (מחירים, אינדיקטורים, חדשות, מאקרו)
"""
import os
import pandas as pd
import sqlite3
from datetime import datetime

class DataManager:
    def __init__(self, db_path="data/database/historical.db"):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """יוצר טבלאות נדרשות אם לא קיימות"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_prices (
                date TEXT, symbol TEXT, open REAL, high REAL, low REAL, close REAL, volume INTEGER, adjusted_close REAL,
                PRIMARY KEY (date, symbol)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                date TEXT, symbol TEXT, rsi_14 REAL, macd REAL, macd_signal REAL, sma_20 REAL, ema_20 REAL,
                bollinger_upper REAL, bollinger_lower REAL, atr_14 REAL, PRIMARY KEY (date, symbol)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_sentiment (
                date TEXT, symbol TEXT, headline TEXT, sentiment REAL, source TEXT, url TEXT, category TEXT,
                PRIMARY KEY (date, symbol, headline)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS macro_data (
                date TEXT, indicator TEXT, value REAL, PRIMARY KEY (date, indicator)
            )
        ''')
        conn.commit()
        conn.close()

    def get_price_data(self, symbol, start_date, end_date):
        """שליפת נתוני מחירים מהמאגר"""
        conn = sqlite3.connect(self.db_path)
        query = '''SELECT * FROM historical_prices WHERE symbol=? AND date BETWEEN ? AND ? ORDER BY date'''
        df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
        conn.close()
        return df

    def get_technical_indicators(self, symbol, start_date, end_date):
        """שליפת אינדיקטורים טכניים מהמאגר"""
        conn = sqlite3.connect(self.db_path)
        query = '''SELECT * FROM technical_indicators WHERE symbol=? AND date BETWEEN ? AND ? ORDER BY date'''
        df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
        conn.close()
        return df

    def get_news(self, symbol, start_date, end_date):
        """שליפת חדשות/סנטימנט מהמאגר"""
        conn = sqlite3.connect(self.db_path)
        query = '''SELECT * FROM news_sentiment WHERE symbol=? AND date BETWEEN ? AND ? ORDER BY date'''
        df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
        conn.close()
        return df

    def get_macro_data(self, indicator, start_date, end_date):
        """שליפת נתוני מאקרו מהמאגר"""
        conn = sqlite3.connect(self.db_path)
        query = '''SELECT * FROM macro_data WHERE indicator=? AND date BETWEEN ? AND ? ORDER BY date'''
        df = pd.read_sql_query(query, conn, params=(indicator, start_date, end_date))
        conn.close()
        return df

    def find_missing_dates(self, symbol, start_date, end_date):
        """בודק אילו תאריכים חסרים במאגר עבור סימבול מסוים"""
        df = self.get_price_data(symbol, start_date, end_date)
        all_dates = pd.date_range(start=start_date, end=end_date, freq='B').strftime('%Y-%m-%d')
        existing_dates = set(df['date'])
        missing = [d for d in all_dates if d not in existing_dates]
        return missing

    def update_price_data(self, symbol, df_new):
        """עדכון/הוספת נתוני מחירים חדשים למאגר"""
        conn = sqlite3.connect(self.db_path)
        df_new['symbol'] = symbol
        df_new.to_sql('historical_prices', conn, if_exists='append', index=False)
        conn.close()

    def update_technical_indicators(self, symbol, df_new):
        """עדכון/הוספת אינדיקטורים חדשים למאגר"""
        conn = sqlite3.connect(self.db_path)
        df_new['symbol'] = symbol
        df_new.to_sql('technical_indicators', conn, if_exists='append', index=False)
        conn.close()

    def update_news(self, symbol, df_new):
        """עדכון/הוספת חדשות/סנטימנט למאגר"""
        conn = sqlite3.connect(self.db_path)
        df_new['symbol'] = symbol
        df_new.to_sql('news_sentiment', conn, if_exists='append', index=False)
        conn.close()

    def update_macro_data(self, indicator, df_new):
        """עדכון/הוספת נתוני מאקרו למאגר"""
        conn = sqlite3.connect(self.db_path)
        df_new['indicator'] = indicator
        df_new.to_sql('macro_data', conn, if_exists='append', index=False)
        conn.close()

# דוגמה לשימוש
if __name__ == "__main__":
    dm = DataManager()
    # שליפת נתוני מחירים
    df = dm.get_price_data('AAPL', '2020-01-01', '2020-12-31')
    print(df.head())
    # בדיקת אילו תאריכים חסרים
    missing = dm.find_missing_dates('AAPL', '2020-01-01', '2020-12-31')
    print("תאריכים חסרים:", missing) 