#!/usr/bin/env python3
"""
בדיקה ישירה של yfinance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_yfinance_direct():
    """בדיקה ישירה של yfinance"""
    
    print("🔧 בדיקה ישירה של yfinance...")
    print("=" * 50)
    
    # רשימת מניות לבדיקה
    test_symbols = [
        "AAPL",
        "TSLA", 
        "NVDA",
        "MSFT",
        "GOOGL"
    ]
    
    for symbol in test_symbols:
        print(f"\n📊 בדיקת {symbol}...")
        
        try:
            # יצירת Ticker object
            ticker = yf.Ticker(symbol)
            
            # בדיקת היסטוריה
            print(f"  - מנסה לקבל היסטוריה...")
            hist = ticker.history(period="30d")
            
            if hist.empty:
                print(f"  ❌ אין נתונים ל-{symbol}")
                continue
            
            print(f"  ✅ הצלחה - {len(hist)} שורות")
            print(f"  - תאריכים: {hist.index[0]} עד {hist.index[-1]}")
            print(f"  - מחיר אחרון: {hist['Close'].iloc[-1]:.2f}")
            print(f"  - עמודות: {list(hist.columns)}")
            
            # בדיקת מידע נוסף
            print(f"  - מנסה לקבל מידע נוסף...")
            info = ticker.info
            if info:
                print(f"  ✅ מידע נוסף זמין")
                if 'longName' in info:
                    print(f"  - שם: {info['longName']}")
                if 'sector' in info:
                    print(f"  - סקטור: {info['sector']}")
            else:
                print(f"  ❌ אין מידע נוסף")
                
        except Exception as e:
            print(f"  ❌ שגיאה: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ בדיקה הושלמה!")

if __name__ == "__main__":
    test_yfinance_direct() 