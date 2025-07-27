#!/usr/bin/env python3
"""
בדיקת חיבור רשת
"""

import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_network_connectivity():
    """בדיקת חיבור רשת"""
    
    print("🔧 בדיקת חיבור רשת...")
    print("=" * 50)
    
    # בדיקת חיבור כללי
    print("📡 בדיקת חיבור לאינטרנט...")
    try:
        response = requests.get("https://www.google.com", timeout=10)
        print(f"✅ חיבור לאינטרנט עובד - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ בעיית חיבור לאינטרנט: {e}")
        return
    
    # בדיקת Yahoo Finance
    print("\n📊 בדיקת Yahoo Finance...")
    try:
        response = requests.get("https://finance.yahoo.com", timeout=10)
        print(f"✅ Yahoo Finance נגיש - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ בעיה עם Yahoo Finance: {e}")
    
    # בדיקת yfinance עם SSL מושבת
    print("\n🔧 בדיקת yfinance עם SSL מושבת...")
    try:
        # ניסיון עם SSL מושבת
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            print(f"✅ yfinance עובד עם SSL מושבת - {len(hist)} שורות")
            print(f"   - מחיר אחרון: {hist['Close'].iloc[-1]:.2f}")
        else:
            print("❌ yfinance לא מחזיר נתונים גם עם SSL מושבת")
            
    except Exception as e:
        print(f"❌ שגיאה עם yfinance: {e}")
    
    # בדיקת תקופות שונות
    print("\n📅 בדיקת תקופות שונות...")
    periods = ["1d", "5d", "1mo", "3mo"]
    
    for period in periods:
        try:
            ticker = yf.Ticker("AAPL")
            hist = ticker.history(period=period)
            
            if not hist.empty:
                print(f"✅ תקופה {period}: {len(hist)} שורות")
            else:
                print(f"❌ תקופה {period}: אין נתונים")
                
        except Exception as e:
            print(f"❌ תקופה {period}: שגיאה - {e}")
    
    # בדיקת מניות שונות
    print("\n📈 בדיקת מניות שונות...")
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                print(f"✅ {symbol}: {len(hist)} שורות")
            else:
                print(f"❌ {symbol}: אין נתונים")
                
        except Exception as e:
            print(f"❌ {symbol}: שגיאה - {e}")
    
    print(f"\n✅ בדיקת רשת הושלמה!")

if __name__ == "__main__":
    test_network_connectivity() 