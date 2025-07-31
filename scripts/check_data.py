#!/usr/bin/env python3
"""
סקריפט לבדיקת הנתונים שנשמרו
"""

import pandas as pd
import os

def check_data():
    """בדיקת הנתונים שנשמרו"""
    
    # רשימת המניות החדשות
    new_symbols = ['GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX']
    
    print("🔍 בודק נתונים שנשמרו עבור 5 המניות החדשות")
    print("=" * 60)
    
    for symbol in new_symbols:
        print(f"\n📊 {symbol}:")
        
        # בדיקת נתוני מחירים
        price_file = f"data/historical_prices/daily/{symbol}.csv.gz"
        if os.path.exists(price_file):
            try:
                df = pd.read_csv(price_file, compression='gzip')
                print(f"  ✅ מחירים: {len(df)} שורות")
                if len(df) > 0:
                    print(f"     תאריך ראשון: {df.iloc[0]['date']}")
                    print(f"     תאריך אחרון: {df.iloc[-1]['date']}")
                    print(f"     מחיר אחרון: ${df.iloc[-1]['close']:.2f}")
            except Exception as e:
                print(f"  ❌ מחירים: שגיאה - {e}")
        else:
            print(f"  ❌ מחירים: קובץ לא נמצא")
        
        # בדיקת אינדיקטורים טכניים
        tech_files_found = 0
        tech_dirs = ['rsi', 'macd', 'bollinger', 'sma', 'ema']
        for tech_dir in tech_dirs:
            tech_file = f"data/technical_indicators/{tech_dir}/daily/{symbol}.csv.gz"
            if os.path.exists(tech_file):
                tech_files_found += 1
        
        if tech_files_found > 0:
            print(f"  ✅ אינדיקטורים טכניים: {tech_files_found} סוגים נשמרו")
        else:
            print(f"  ❌ אינדיקטורים טכניים: לא נמצאו קבצים")
        
        # בדיקת נתונים פונדמנטליים
        fund_file = f"data/fundamentals/company_info/{symbol}_info.csv"
        if os.path.exists(fund_file):
            try:
                df = pd.read_csv(fund_file)
                print(f"  ✅ נתונים פונדמנטליים: {len(df)} שורות")
            except Exception as e:
                print(f"  ❌ נתונים פונדמנטליים: שגיאה - {e}")
        else:
            print(f"  ❌ נתונים פונדמנטליים: קובץ לא נמצא")

if __name__ == "__main__":
    check_data() 