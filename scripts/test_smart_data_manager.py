"""
בדיקת Smart Data Manager
מבצע בדיקות למערכת החדשה שמשלב נתונים מקומיים עם API
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.smart_data_manager import smart_data_manager
from utils.fmp_utils import smart_get_price_data, smart_get_multiple_stocks, get_data_status

def test_smart_data_manager():
    """בדיקת המערכת החכמה"""
    print("🧪 בדיקת Smart Data Manager")
    print("=" * 50)
    
    # בדיקת סטטוס הנתונים
    print("\n📊 סטטוס הנתונים במערכת:")
    status = get_data_status()
    print(f"סה״כ קבצים: {status.get('total_files', 0)}")
    print(f"סה״כ מניות: {status.get('total_symbols', 0)}")
    
    # בדיקת עדכונים אחרונים
    recent_updates = status.get('recent_updates', [])
    if recent_updates:
        print(f"\n🔄 עדכונים אחרונים:")
        for update in recent_updates[:5]:  # רק 5 הראשונים
            print(f"  {update['symbol']}: {update['last_updated']} ({update['rows']} שורות)")
    
    # בדיקת מניות ספציפיות
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    
    print(f"\n🔍 בדיקת שליפת נתונים למניות:")
    for symbol in test_symbols:
        print(f"\n📈 בדיקת {symbol}:")
        
        # בדיקה עם 30 ימים
        data_30 = smart_get_price_data(symbol, days=30)
        if data_30 is not None and not data_30.empty:
            print(f"  ✅ 30 ימים: {len(data_30)} שורות")
            print(f"     תאריך אחרון: {data_30.index[0]}")
            print(f"     מחיר אחרון: {data_30['close'].iloc[0]:.2f}")
        else:
            print(f"  ❌ לא הצלחנו לקבל נתונים עבור {symbol}")
    
    # בדיקת שליפה מרובה
    print(f"\n📊 בדיקת שליפה מרובה:")
    multiple_data = smart_get_multiple_stocks(['AAPL', 'MSFT'], days=60)
    print(f"  התקבלו נתונים עבור {len(multiple_data)} מניות")
    
    for symbol, data in multiple_data.items():
        if data is not None and not data.empty:
            print(f"    {symbol}: {len(data)} שורות")
        else:
            print(f"    {symbol}: אין נתונים")

def test_data_combination():
    """בדיקת שילוב נתונים"""
    print("\n🔄 בדיקת שילוב נתונים")
    print("=" * 30)
    
    symbol = 'AAPL'
    
    # בדיקה עם נתונים מקומיים בלבד
    print(f"\n📁 בדיקת נתונים מקומיים בלבד:")
    data_local = smart_data_manager.get_stock_data(symbol, days=90, include_live=False)
    if data_local is not None:
        print(f"  נתונים מקומיים: {len(data_local)} שורות")
        if len(data_local) > 0:
            print(f"    תאריך ראשון: {data_local.index[-1]}")
            print(f"    תאריך אחרון: {data_local.index[0]}")
    
    # בדיקה עם נתונים חיים
    print(f"\n🌐 בדיקת נתונים עם השלמה מ-API:")
    data_with_api = smart_data_manager.get_stock_data(symbol, days=90, include_live=True)
    if data_with_api is not None:
        print(f"  נתונים עם API: {len(data_with_api)} שורות")
        if len(data_with_api) > 0:
            print(f"    תאריך ראשון: {data_with_api.index[-1]}")
            print(f"    תאריך אחרון: {data_with_api.index[0]}")
    
    # השוואה
    if data_local is not None and data_with_api is not None:
        additional_rows = len(data_with_api) - len(data_local)
        if additional_rows > 0:
            print(f"  ➕ נוספו {additional_rows} שורות מ-API")

def test_fallback_system():
    """בדיקת מערכת ה-fallback"""
    print("\n🔄 בדיקת מערכת Fallback")
    print("=" * 30)
    
    # בדיקה עם מניה שלא קיימת מקומית
    test_symbol = 'TEST123'
    print(f"\n🧪 בדיקת מניה לא קיימת: {test_symbol}")
    
    data = smart_get_price_data(test_symbol, days=30)
    if data is not None and not data.empty:
        print(f"  ✅ הצלחנו לקבל נתונים מ-API: {len(data)} שורות")
    else:
        print(f"  ❌ לא הצלחנו לקבל נתונים")
    
    # בדיקת yfinance fallback
    print(f"\n📈 בדיקת yfinance fallback:")
    try:
        import yfinance as yf
        print("  ✅ yfinance זמין")
    except ImportError:
        print("  ⚠️ yfinance לא זמין")

def main():
    """פונקציה ראשית"""
    print("🚀 הפעלת בדיקות Smart Data Manager")
    print("=" * 60)
    
    try:
        # בדיקות בסיסיות
        test_smart_data_manager()
        
        # בדיקת שילוב נתונים
        test_data_combination()
        
        # בדיקת fallback
        test_fallback_system()
        
        print("\n✅ כל הבדיקות הושלמו בהצלחה!")
        
    except Exception as e:
        print(f"\n❌ שגיאה בבדיקות: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 