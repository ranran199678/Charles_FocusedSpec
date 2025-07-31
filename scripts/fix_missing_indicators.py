import os
import pandas as pd
import numpy as np
from datetime import datetime

def check_missing_indicators():
    """בדיקת אינדיקטורים חסרים"""
    
    print("🔍 בודק אינדיקטורים חסרים...")
    print("=" * 60)
    
    indicators_dir = "data/technical_indicators"
    timeframes = ['daily', 'weekly', 'monthly']
    
    # רשימת האינדיקטורים שצריכים להיות זמינים
    expected_indicators = ['rsi', 'macd', 'bollinger', 'sma', 'ema', 'atr', 'stochastic', 'adx', 'cci', 'williams_r']
    
    missing_indicators = []
    
    for indicator in expected_indicators:
        indicator_path = os.path.join(indicators_dir, indicator)
        if os.path.exists(indicator_path):
            print(f"✅ {indicator.upper()}: קיים")
            
            # בדיקת קבצים בכל timeframe
            for timeframe in timeframes:
                timeframe_path = os.path.join(indicator_path, timeframe)
                if os.path.exists(timeframe_path):
                    files = [f for f in os.listdir(timeframe_path) if f.endswith('.csv')]
                    if files:
                        print(f"   📅 {timeframe}: {len(files)} קבצים")
                    else:
                        print(f"   ⚠️ {timeframe}: אין קבצים")
                        missing_indicators.append(f"{indicator}_{timeframe}")
                else:
                    print(f"   ❌ {timeframe}: תיקייה לא קיימת")
                    missing_indicators.append(f"{indicator}_{timeframe}")
        else:
            print(f"❌ {indicator.upper()}: לא קיים")
            missing_indicators.append(indicator)
    
    return missing_indicators

def create_missing_indicators():
    """יצירת אינדיקטורים חסרים"""
    
    print(f"\n🔧 יוצר אינדיקטורים חסרים...")
    print("=" * 60)
    
    # קריאת נתונים גולמיים
    raw_dir = "data/raw_price_data"
    if not os.path.exists(raw_dir):
        print("❌ תיקיית נתונים גולמיים לא קיימת")
        return
    
    files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    
    if not files:
        print("❌ לא נמצאו קבצי נתונים גולמיים")
        return
    
    print(f"📊 נמצאו {len(files)} קבצים לעיבוד")
    
    for file_name in files:
        print(f"\n📈 מעבד: {file_name}")
        
        file_path = os.path.join(raw_dir, file_name)
        
        try:
            # קריאת נתונים
            df = pd.read_csv(file_path)
            
            # המרת עמודות
            col_map = {
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Price': 'close',
                'Vol.': 'volume',
                'Volume': 'volume'
            }
            
            df.rename(columns=col_map, inplace=True)
            
            # הוספת עמודת Close אם לא קיימת
            if 'Close' not in df.columns and 'Price' in df.columns:
                df['Close'] = df['Price']
            
            # המרת תאריכים
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # המרת עמודות מספריות
            numeric_cols = ['open', 'high', 'low', 'close']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # חילוץ שם הסימבול
            clean_symbol = file_name.replace(' Stock Price History.csv', '').replace('.csv', '')
            clean_symbol = clean_symbol.replace(' (1)', '').replace(' (2)', '').replace(' (3)', '').upper()
            
            # זיהוי timeframe
            if '(1)' in file_name:
                timeframe = 'weekly'
            elif '(2)' in file_name:
                timeframe = 'monthly'
            else:
                timeframe = 'daily'
            
            # חישוב אינדיקטורים חסרים
            indicators_to_create = ['adx', 'cci']
            
            for indicator in indicators_to_create:
                print(f"   📊 יוצר {indicator.upper()}...")
                
                if indicator == 'adx':
                    adx_values = calculate_adx(df)
                    if adx_values is not None:
                        save_indicator(adx_values, clean_symbol, 'adx', timeframe)
                
                elif indicator == 'cci':
                    cci_values = calculate_cci(df)
                    if cci_values is not None:
                        save_indicator(cci_values, clean_symbol, 'cci', timeframe)
            
        except Exception as e:
            print(f"   ❌ שגיאה בעיבוד {file_name}: {str(e)}")

def calculate_adx(df, period=14):
    """חישוב ADX"""
    try:
        # חישוב +DM ו--DM
        high_diff = df['high'].diff()
        low_diff = df['low'].diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = -low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        # חישוב TR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.DataFrame({
            'high_low': high_low,
            'high_close': high_close,
            'low_close': low_close
        })
        true_range = ranges.max(axis=1)
        tr = true_range.rolling(window=period).mean()
        
        # חישוב +DI ו--DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr)
        
        # חישוב DX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
        
    except Exception as e:
        print(f"      ❌ שגיאה בחישוב ADX: {str(e)}")
        return None

def calculate_cci(df, period=20):
    """חישוב CCI"""
    try:
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        
        # חישוב MAD (Mean Absolute Deviation)
        def mad_func(x):
            return np.mean(np.abs(x - x.mean()))
        
        mad = typical_price.rolling(window=period).apply(mad_func)
        cci = (typical_price - sma_tp) / (0.015 * mad)
        
        return cci
        
    except Exception as e:
        print(f"      ❌ שגיאה בחישוב CCI: {str(e)}")
        return None

def save_indicator(values, symbol, indicator_type, timeframe):
    """שמירת אינדיקטור לקובץ"""
    try:
        # יצירת DataFrame
        indicator_df = pd.DataFrame({
            'date': pd.date_range(start='2015-01-01', periods=len(values), freq='D'),
            'symbol': symbol,
            'value': values
        })
        
        # הסרת ערכים NaN
        indicator_df = indicator_df.dropna()
        
        if not indicator_df.empty:
            # יצירת תיקייה אם לא קיימת
            output_dir = f"data/technical_indicators/{indicator_type}/{timeframe}"
            os.makedirs(output_dir, exist_ok=True)
            
            # שמירת קובץ
            output_file = f"{output_dir}/{symbol}_{indicator_type}_{timeframe}.csv"
            indicator_df.to_csv(output_file, index=False)
            
            print(f"      ✅ נשמר: {output_file} ({len(indicator_df)} שורות)")
        else:
            print(f"      ⚠️ אין נתונים תקינים ל-{indicator_type}")
            
    except Exception as e:
        print(f"      ❌ שגיאה בשמירת {indicator_type}: {str(e)}")

def main():
    """הפונקציה הראשית"""
    
    print("🚀 מתחיל תיקון אינדיקטורים חסרים...")
    print("=" * 60)
    
    # בדיקת אינדיקטורים חסרים
    missing = check_missing_indicators()
    
    if missing:
        print(f"\n⚠️ נמצאו אינדיקטורים חסרים: {len(missing)}")
        print("📋 רשימה:", ', '.join(missing))
        
        # יצירת אינדיקטורים חסרים
        create_missing_indicators()
        
        # בדיקה חוזרת
        print(f"\n🔍 בודק שוב...")
        missing_after = check_missing_indicators()
        
        if missing_after:
            print(f"⚠️ עדיין חסרים: {len(missing_after)}")
        else:
            print("✅ כל האינדיקטורים זמינים!")
    else:
        print("✅ כל האינדיקטורים זמינים!")

if __name__ == "__main__":
    main()