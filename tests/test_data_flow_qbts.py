import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from utils.smart_data_manager import SmartDataManager
from utils.validators import validate_stock_data

def test_qbts_daily_last_50_days():
    symbol = "QBTS"
    required_days = 50

    # אתחול מנהל נתונים חכם
    smart_data_manager = SmartDataManager()

    # שליפת נתונים היסטוריים - יומיים
    df = smart_data_manager.get_stock_data(symbol, days=required_days, include_live=True)

    if df is None:
        print("❌ לא הצלחנו לשלוף נתונים עבור", symbol)
        return

    df = df.sort_index(ascending=False).head(required_days)

    print(f"\n✅ נמשכו {len(df)} שורות של נתוני מחיר יומיים עבור {symbol}:\n")
    print(df.head())

    # אימות תקינות
    is_valid = validate_stock_data(df)
    print("\n✔️ אימות נתונים:", "תקין" if is_valid else "שגוי")

    # בדיקות
    assert 'open' in df.columns
    assert 'close' in df.columns
    assert 'volume' in df.columns
    assert 'high' in df.columns
    assert 'low' in df.columns
    assert len(df) >= 5, "לא מספיק ימים זמינים"
    assert is_valid, "הנתונים שנמשכו אינם תקינים לפי מערכת הוולידציה"

if __name__ == "__main__":
    test_qbts_daily_last_50_days()
