import os
import pandas as pd
import time
import requests
import json
from datetime import datetime, timedelta

# הגדרות SSL ורשת
os.environ["CURL_CA_BUNDLE"] = r"C:\CharlesCertFix\cacert.pem"
os.environ["REQUESTS_CA_BUNDLE"] = r"C:\CharlesCertFix\cacert.pem"

# הגדרת User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_stock_data_yahoo(symbol, start_date, end_date, max_retries=3):
    """הורדת נתונים ישירות מ-Yahoo Finance API"""
    for attempt in range(max_retries):
        try:
            print(f"📥 מוריד נתונים עבור {symbol}... (ניסיון {attempt + 1}/{max_retries})")
            
            # השהייה בין בקשות
            if attempt > 0:
                wait_time = 2 ** attempt
                print(f"⏳ ממתין {wait_time} שניות...")
                time.sleep(wait_time)
            
            # המרת תאריכים ל-timestamp
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
            
            # URL של Yahoo Finance
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
                        'Date': [datetime.fromtimestamp(ts) for ts in timestamps],
                        'Open': quotes.get('open', []),
                        'High': quotes.get('high', []),
                        'Low': quotes.get('low', []),
                        'Close': quotes.get('close', []),
                        'Volume': quotes.get('volume', [])
                    }
                    
                    df = pd.DataFrame(df_data)
                    df.set_index('Date', inplace=True)
                    
                    # הסרת שורות עם ערכים חסרים
                    df = df.dropna()
                    
                    if not df.empty:
                        print(f"✅ הורדו {len(df)} שורות נתונים")
                        print(f"📅 טווח תאריכים: {df.index[0].date()} עד {df.index[-1].date()}")
                        return df
                    else:
                        print("❌ לא נמצאו נתונים תקינים")
                else:
                    print("❌ לא נמצאו נתונים בתגובה")
            else:
                print(f"❌ שגיאת HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ שגיאה בהורדת נתונים עבור {symbol} (ניסיון {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                print("🔄 מנסה שוב...")
            else:
                print("❌ נכשלו כל הניסיונות")
    
    return None

def convert_to_our_format(df, symbol):
    """המרת הנתונים לפורמט של המערכת שלנו"""
    # יצירת DataFrame חדש בפורמט שלנו
    new_df = pd.DataFrame({
        'Date': df.index.strftime('%m/%d/%Y'),
        'Price': df['Close'],  # Price = Close
        'Open': df['Open'],
        'High': df['High'],
        'Low': df['Low'],
        'Vol.': df['Volume'].apply(lambda x: f"{x:,.0f}"),
        'Change %': ((df['Close'] - df['Close'].shift(1)) / df['Close'].shift(1) * 100).round(2).apply(lambda x: f"{x:.2f}%")
    })
    
    # הסרת השורה הראשונה (אין לה Change %)
    new_df = new_df.iloc[1:]
    
    return new_df

def save_to_csv(df, filename):
    """שמירת נתונים לקובץ CSV בתיקיית raw_price_data"""
    try:
        # יצירת תיקיית raw_price_data אם לא קיימת
        raw_data_dir = "data/raw_price_data"
        os.makedirs(raw_data_dir, exist_ok=True)
        
        # נתיב מלא לקובץ
        file_path = os.path.join(raw_data_dir, filename)
        
        df.to_csv(file_path, index=False)
        print(f"✅ שמירת הקובץ {file_path} הושלמה")
        print(f"📊 גודל הקובץ: {len(df)} שורות")
        return True
    except Exception as e:
        print(f"❌ שגיאה בשמירת הקובץ: {str(e)}")
        return False

def download_multiple_stocks(symbols, start_date, end_date):
    """הורדת נתונים למספר מניות"""
    results = {}
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"📈 מעבד מניה: {symbol}")
        print(f"{'='*50}")
        
        # הורדת נתונים
        df = download_stock_data_yahoo(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            # המרה לפורמט שלנו
            formatted_df = convert_to_our_format(df, symbol)
            
            # שמירת הקובץ בתיקיית raw_price_data
            filename = f"{symbol} Stock Price History.csv"
            success = save_to_csv(formatted_df, filename)
            
            if success:
                print(f"\n📋 סיכום עבור {symbol}:")
                print(f"✅ הורדו {len(formatted_df)} שורות נתונים")
                print(f"💰 מחיר אחרון: ${df['Close'].iloc[-1]:.2f}")
                print(f"📈 מחיר גבוה ביותר: ${df['High'].max():.2f}")
                print(f"📉 מחיר נמוך ביותר: ${df['Low'].min():.2f}")
                print(f"📊 נפח ממוצע: {df['Volume'].mean():,.0f}")
                
                results[symbol] = {
                    'filename': filename,
                    'filepath': f"data/raw_price_data/{filename}",
                    'rows': len(formatted_df),
                    'last_price': df['Close'].iloc[-1],
                    'high': df['High'].max(),
                    'low': df['Low'].min(),
                    'avg_volume': df['Volume'].mean()
                }
            else:
                print(f"❌ נכשל בשמירת הקובץ עבור {symbol}")
        else:
            print(f"❌ לא ניתן להוריד נתונים עבור {symbol}")
    
    return results

# הגדרת פרמטרים - בדיקה מהירה עם 3 מניות בלבד
symbols = ["AAPL", "MSFT", "TSLA"]  # בדיקה מהירה - 3 מניות בלבד
start_date = "2020-01-01"  # 5 שנים אחורה
end_date = "2025-07-28"

print("🚀 מתחיל הורדת נתונים...")
print(f"📈 מניות: {', '.join(symbols)}")
print(f"📅 מ: {start_date}")
print(f"📅 עד: {end_date}")
print(f"💾 שמירה בתיקייה: data/raw_price_data/")
print("-" * 50)

# הורדת נתונים לכל המניות
results = download_multiple_stocks(symbols, start_date, end_date)

# סיכום כללי
if results:
    print(f"\n{'='*60}")
    print("📊 סיכום כללי:")
    print(f"{'='*60}")
    print(f"✅ הורדו נתונים עבור {len(results)} מניות")
    
    for symbol, data in results.items():
        print(f"📈 {symbol}: {data['rows']} שורות, מחיר אחרון: ${data['last_price']:.2f}")
    
    print(f"\n💾 קבצים נוצרו ב-data/raw_price_data/:")
    for symbol, data in results.items():
        print(f"   📄 {data['filename']}")
else:
    print("❌ לא הורדו נתונים עבור אף מניה")
