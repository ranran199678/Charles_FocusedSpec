#!/usr/bin/env python3
"""
בדיקה פשוטה עם נתונים סינתטיים
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.alpha_score_engine import AlphaScoreEngine
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_simple_data():
    """יצירת נתונים פשוטים לבדיקה"""
    
    # יצירת תאריכים
    dates = pd.date_range(start='2024-01-01', end='2024-07-01', freq='D')
    
    # יצירת מחירים סינתטיים
    np.random.seed(42)
    
    # מחיר התחלתי
    base_price = 100.0
    
    # יצירת מחירים עם מגמה
    prices = [base_price]
    for i in range(1, len(dates)):
        # תשואה יומית עם מגמה חיובית
        daily_return = 0.001 + np.random.normal(0, 0.02)  # 0.1% ממוצע + רעש
        prices.append(prices[-1] * (1 + daily_return))
    
    # יצירת OHLCV
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        # יצירת OHLC סביב המחיר
        volatility = price * 0.02
        
        open_price = price + np.random.normal(0, volatility * 0.5)
        high_price = max(open_price, price) + abs(np.random.normal(0, volatility * 0.3))
        low_price = min(open_price, price) - abs(np.random.normal(0, volatility * 0.3))
        close_price = price + np.random.normal(0, volatility * 0.5)
        
        # נפח מסחר
        volume = 1000000 + np.random.normal(0, 300000)
        volume = max(volume, 100000)
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    return df

def test_simple():
    """בדיקה פשוטה"""
    
    print("🔧 בדיקה פשוטה עם נתונים סינתטיים...")
    print("=" * 50)
    
    # יצירת נתונים
    price_df = create_simple_data()
    print(f"✅ נוצרו {len(price_df)} נקודות נתונים")
    
    # יצירת מנוע
    engine = AlphaScoreEngine()
    
    # בדיקת מנוע
    symbol = "TEST_STOCK"
    print(f"\n📊 בדיקת {symbol}...")
    
    try:
        result = engine.evaluate(symbol, price_df)
        
        print(f"✅ תוצאות:")
        print(f"   - ציון סופי: {result.get('final_score', 0)}")
        print(f"   - מספר סוכנים: {result.get('agents_count', 0)}")
        print(f"   - המלצה: {result.get('recommendation', 'לא זמין')}")
        
        if 'agent_scores' in result:
            print(f"\n📊 ציוני סוכנים:")
            for agent_name, agent_score in list(result['agent_scores'].items())[:10]:
                print(f"   - {agent_name}: {agent_score}")
        
        print(f"\n✅ בדיקה הושלמה בהצלחה!")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple() 