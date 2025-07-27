import sys
import os
sys.path.append('.')

from utils.data_fetcher import DataFetcher
from datetime import datetime

def debug_data_sources():
    print("=== בדיקת מקורות נתונים ===")
    
    symbol = "INTC"
    data_fetcher = DataFetcher()
    
    print(f"בדיקת מניה: {symbol}")
    print(f"תאריך בדיקה: {datetime.now()}")
    
    # בדיקה 1: DataFetcher שלנו
    print(f"\n--- DataFetcher שלנו ---")
    try:
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        print(f"עמודות: {list(price_df.columns)}")
        print(f"צורה: {price_df.shape}")
        print(f"תאריכים: {price_df.index[0]} עד {price_df.index[-1]}")
        print(f"מחיר אחרון: {price_df['close'].iloc[-1]:.2f}")
        print(f"5 המחירים האחרונים:")
        print(price_df['close'].tail())
        
        # בדיקת תאריכים
        print(f"\nתאריכים אחרונים:")
        print(price_df.index[-5:])
        
    except Exception as e:
        print(f"שגיאה ב-DataFetcher: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # בדיקה 2: מקורות שונים
    print(f"\n--- בדיקת מקורות שונים ---")
    
    # Yahoo
    try:
        yahoo_data = data_fetcher._fetch_yahoo_prices(symbol, "100d")
        if yahoo_data is not None and not yahoo_data.empty:
            print(f"Yahoo - מחיר אחרון: {yahoo_data['close'].iloc[-1]:.2f}")
            print(f"Yahoo - תאריך אחרון: {yahoo_data.index[-1]}")
        else:
            print("Yahoo - אין נתונים")
    except Exception as e:
        print(f"שגיאה ב-Yahoo: {str(e)}")
    
    # FMP
    try:
        fmp_data = data_fetcher._fetch_fmp_prices(symbol, "100d")
        if fmp_data is not None and not fmp_data.empty:
            print(f"FMP - מחיר אחרון: {fmp_data['close'].iloc[-1]:.2f}")
            print(f"FMP - תאריך אחרון: {fmp_data.index[-1]}")
        else:
            print("FMP - אין נתונים")
    except Exception as e:
        print(f"שגיאה ב-FMP: {str(e)}")
    
    # TwelveData
    try:
        twelve_data = data_fetcher._fallback_twelve_prices(symbol, "100d")
        if twelve_data is not None and not twelve_data.empty:
            print(f"TwelveData - מחיר אחרון: {twelve_data['close'].iloc[-1]:.2f}")
            print(f"TwelveData - תאריך אחרון: {twelve_data.index[-1]}")
        else:
            print("TwelveData - אין נתונים")
    except Exception as e:
        print(f"שגיאה ב-TwelveData: {str(e)}")

if __name__ == "__main__":
    debug_data_sources() 