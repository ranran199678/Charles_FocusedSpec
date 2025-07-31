#!/usr/bin/env python3
"""
בדיקה עם מקורות נתונים חלופיים
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_fetcher import DataFetcher
from utils.fmp_utils import fmp_client
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_alternative_data_sources():
    """בדיקה עם מקורות נתונים חלופיים"""
    
    print("🔧 בדיקת מקורות נתונים חלופיים...")
    print("=" * 60)
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # רשימת מניות לבדיקה
    test_symbols = [
        "INTC",   # Intel - עובד עם DataFetcher
        "AAPL",   # Apple
        "MSFT",   # Microsoft
        "GOOGL",  # Google
        "TSLA"    # Tesla
    ]
    
    results = []
    
    for symbol in test_symbols:
        print(f"\n📊 בדיקת {symbol}...")
        
        try:
            # בדיקה עם DataFetcher
            print(f"  - מנסה DataFetcher...")
            df_data_fetcher = data_fetcher.get_price_history(symbol, "30d")
            
            if df_data_fetcher is not None and not df_data_fetcher.empty:
                print(f"  ✅ DataFetcher עובד - {len(df_data_fetcher)} שורות")
                print(f"    - מחיר אחרון: {df_data_fetcher['close'].iloc[-1]:.2f}")
                print(f"    - עמודות: {list(df_data_fetcher.columns)}")
                
                # בדיקה עם FMP
                print(f"  - מנסה FMP...")
                fmp_df = fmp_client.fmp_get_price_df(symbol, verify_ssl=False)
                
                if fmp_df is not None and not fmp_df.empty:
                    print(f"  ✅ FMP עובד - {len(fmp_df)} שורות")
                    print(f"    - מחיר אחרון: {fmp_df['close'].iloc[-1]:.2f}")
                    print(f"    - עמודות: {list(fmp_df.columns)}")
                else:
                    print(f"  ❌ FMP לא עובד")
                
                # בדיקה עם Analyst Estimates
                print(f"  - מנסה Analyst Estimates...")
                # הערה: fetch_analyst_estimates לא קיים במודול המעודכן
                analyst_data = None
                
                if analyst_data is not None:
                    print(f"  ✅ Analyst Estimates עובד - {len(analyst_data)} הערכות")
                else:
                    print(f"  ❌ Analyst Estimates לא עובד")
                
                result = {
                    "symbol": symbol,
                    "data_fetcher": True,
                    "fmp": fmp_df is not None and not fmp_df.empty,
                    "analyst": analyst_data is not None,
                    "data_points": len(df_data_fetcher),
                    "last_price": df_data_fetcher['close'].iloc[-1]
                }
                
            else:
                print(f"  ❌ DataFetcher לא עובד")
                result = {
                    "symbol": symbol,
                    "data_fetcher": False,
                    "fmp": False,
                    "analyst": False,
                    "data_points": 0,
                    "last_price": 0
                }
            
            results.append(result)
            
        except Exception as e:
            print(f"  ❌ שגיאה: {e}")
            result = {
                "symbol": symbol,
                "data_fetcher": False,
                "fmp": False,
                "analyst": False,
                "data_points": 0,
                "last_price": 0,
                "error": str(e)
            }
            results.append(result)
    
    # סיכום
    print("\n" + "=" * 60)
    print("📋 סיכום מקורות נתונים:")
    print("=" * 60)
    
    working_symbols = [r for r in results if r["data_fetcher"]]
    fmp_working = [r for r in results if r["fmp"]]
    analyst_working = [r for r in results if r["analyst"]]
    
    print(f"📊 מניות עם נתונים זמינים: {len(working_symbols)}/{len(results)}")
    print(f"📊 מניות עם FMP: {len(fmp_working)}/{len(results)}")
    print(f"📊 מניות עם Analyst Estimates: {len(analyst_working)}/{len(results)}")
    
    if working_symbols:
        print(f"\n✅ מניות עובדות:")
        for result in working_symbols:
            print(f"  - {result['symbol']}: {result['data_points']} נקודות, מחיר: {result['last_price']:.2f}")
    
    if not working_symbols:
        print(f"\n❌ אין מניות עובדות")
    
    print(f"\n✅ בדיקה הושלמה!")

if __name__ == "__main__":
    test_alternative_data_sources() 