#!/usr/bin/env python3
"""
סקריפט לבדיקת הבעיה עם האינדיקטורים הטכניים
"""

import sys
import os
import pandas as pd

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

def debug_technical_indicators():
    """בדיקת הבעיה עם האינדיקטורים הטכניים"""
    
    symbol = 'GOOGL'
    print(f"🔍 בודק בעיה עם אינדיקטורים טכניים עבור {symbol}")
    
    try:
        # 1. שליפת נתוני מחירים
        print("1. שולף נתוני מחירים...")
        price_data = smart_data_manager.get_stock_data(symbol, 90)
        if price_data is None or price_data.empty:
            print("❌ לא ניתן לשלוף נתוני מחירים")
            return
        
        print(f"✅ נתוני מחירים: {len(price_data)} שורות")
        print(f"   עמודות: {list(price_data.columns)}")
        print(f"   תאריכים: {price_data.index[0]} עד {price_data.index[-1]}")
        
        # 2. בדיקת חישוב אינדיקטורים
        print("\n2. מחשב אינדיקטורים טכניים...")
        
        # ניסיון עם RSI בלבד
        try:
            import ta
            print("   מנסה RSI...")
            rsi = ta.momentum.RSIIndicator(price_data['close']).rsi()
            print(f"   ✅ RSI חושב: {len(rsi.dropna())} ערכים תקינים")
            
            # יצירת DataFrame עם RSI
            result = pd.DataFrame(index=price_data.index)
            result['rsi'] = rsi
            result = result.dropna()
            
            print(f"   ✅ תוצאה: {len(result)} שורות")
            print(f"   עמודות: {list(result.columns)}")
            
            # שמירה
            print("\n3. שומר אינדיקטורים...")
            smart_data_manager._save_technical_data(symbol, 'rsi', result)
            print("✅ נשמר בהצלחה!")
            
        except Exception as e:
            print(f"   ❌ שגיאה בחישוב RSI: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_technical_indicators() 