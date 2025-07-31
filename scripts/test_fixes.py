#!/usr/bin/env python3
"""
סקריפט לבדיקת התיקונים
"""

import sys
import os

# הוספת הנתיב למערכת
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from utils.smart_data_manager import smart_data_manager
    print("✅ SmartDataManager נטען בהצלחה")
except ImportError as e:
    print(f"❌ שגיאה בטעינת SmartDataManager: {e}")
    sys.exit(1)

def test_single_stock():
    """בדיקת מניה אחת עם התיקונים"""
    
    symbol = 'GOOGL'
    print(f"🧪 בודק {symbol} עם התיקונים...")
    
    try:
        # 1. בדיקת נתוני מחירים
        print("  🔄 בודק נתוני מחירים...")
        price_data = smart_data_manager.get_stock_data(symbol, 90)
        if price_data is not None and not price_data.empty:
            print(f"  ✅ מחירים: {len(price_data)} שורות")
        else:
            print("  ❌ מחירים: לא נשלפו")
            return False
        
        # 2. בדיקת אינדיקטורים טכניים
        print("  📊 בודק אינדיקטורים טכניים...")
        tech_data = smart_data_manager.get_technical_indicators(symbol, 'all', 90)
        if tech_data is not None and not tech_data.empty:
            print(f"  ✅ אינדיקטורים: {len(tech_data.columns)} סוגים")
            print(f"     סוגים: {list(tech_data.columns)}")
        else:
            print("  ❌ אינדיקטורים: לא חושבו")
            return False
        
        # 3. בדיקת נתונים פונדמנטליים
        print("  💰 בודק נתונים פונדמנטליים...")
        fund_data = smart_data_manager.get_fundamentals(symbol, 'company_info')
        if fund_data is not None and not fund_data.empty:
            print(f"  ✅ פונדמנטליים: {len(fund_data)} שורות")
            print(f"     עמודות: {list(fund_data.columns)}")
        else:
            print("  ❌ פונדמנטליים: לא נשלפו")
            return False
        
        print("🎉 כל הבדיקות עברו בהצלחה!")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקה: {e}")
        return False

if __name__ == "__main__":
    test_single_stock() 