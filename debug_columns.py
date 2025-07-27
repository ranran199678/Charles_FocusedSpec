import sys
import os
sys.path.append('.')

from utils.data_fetcher import DataFetcher

def debug_columns():
    print("=== בדיקת עמודות נתונים ===")
    
    data_fetcher = DataFetcher()
    symbol = "AAPL"
    
    try:
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        print(f"עמודות זמינות: {list(price_df.columns)}")
        print(f"צורת הנתונים: {price_df.shape}")
        print(f"5 השורות הראשונות:")
        print(price_df.head())
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")

if __name__ == "__main__":
    debug_columns() 