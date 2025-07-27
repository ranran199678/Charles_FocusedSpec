import sys
import os
sys.path.append('.')

from utils.credentials import APICredentials
from utils.data_fetcher import DataFetcher

def check_api_keys():
    print("=== בדיקת מפתחות API ===")
    
    # בדיקת מפתחות
    print(f"FMP Key: {'✅ קיים' if APICredentials.get_fmp_key() else '❌ חסר'}")
    print(f"Finnhub Key: {'✅ קיים' if APICredentials.get_finnhub_key() else '❌ חסר'}")
    print(f"TwelveData Key: {'✅ קיים' if APICredentials.get_twelve_key() else '❌ חסר'}")
    
    # בדיקת DataFetcher
    print(f"\n--- בדיקת DataFetcher ---")
    data_fetcher = DataFetcher()
    
    symbol = "INTC"
    
    # בדיקה עם תקופות שונות
    periods = ["30d", "100d", "1y"]
    
    for period in periods:
        print(f"\nבדיקת תקופה: {period}")
        try:
            df = data_fetcher.get_price_history(symbol, period)
            if df is not None and not df.empty:
                print(f"  ✅ הצלחה - {len(df)} שורות")
                print(f"  תאריכים: {df.index[0]} עד {df.index[-1]}")
                print(f"  מחיר אחרון: {df['close'].iloc[-1]:.2f}")
            else:
                print(f"  ❌ אין נתונים")
        except Exception as e:
            print(f"  ❌ שגיאה: {str(e)}")

if __name__ == "__main__":
    check_api_keys() 