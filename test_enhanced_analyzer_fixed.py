#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_sample_data():
    """יצירת נתוני דוגמה"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # מחירים עם מגמה עולה
    base_price = 100
    prices = []
    for i in range(len(dates)):
        # מגמה עולה עם תנודתיות
        price = base_price + i * 0.5 + np.random.normal(0, 2)
        prices.append(max(price, 50))  # מינימום מחיר
    
    # נפח עם מגמה
    volumes = []
    for i in range(len(dates)):
        volume = 1000000 + np.random.normal(0, 200000)
        volumes.append(max(volume, 100000))
    
    df = pd.DataFrame({
        'Open': [p * 0.99 for p in prices],
        'High': [p * 1.02 for p in prices],
        'Low': [p * 0.98 for p in prices],
        'Close': prices,
        'Volume': volumes
    }, index=dates)
    
    return df

def test_enhanced_analyzer():
    """בדיקת הסוכן המתקדם"""
    try:
        print("🔧 בדיקת EnhancedAdvancedAnalyzer...")
        
        # יצירת נתוני דוגמה
        sample_data = create_sample_data()
        print(f"✅ נתוני דוגמה נוצרו: {len(sample_data)} שורות")
        
        # ייבוא הסוכן
        from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
        agent = EnhancedAdvancedAnalyzer()
        print("✅ EnhancedAdvancedAnalyzer יובא בהצלחה")
        
        # בדיקת הניתוח
        result = agent.analyze('TEST', sample_data)
        print("✅ ניתוח הושלם בהצלחה")
        
        # הצגת התוצאות
        print(f"\n📊 תוצאות הניתוח:")
        print(f"ציון: {result.get('score', 'N/A')}")
        print(f"הסבר: {result.get('explanation', 'N/A')}")
        
        if 'details' in result:
            details = result['details']
            print(f"\n📈 פרטים:")
            print(f"- תבניות מורכבות: {len(details.get('complex_patterns', {}))}")
            print(f"- ניתוח שוק: {len(details.get('market_analysis', {}))}")
            print(f"- ניתוח נפח: {len(details.get('volume_analysis', {}))}")
            print(f"- ניתוח מגמות: {len(details.get('trend_analysis', {}))}")
            print(f"- תמיכה/התנגדות: {len(details.get('support_resistance', {}))}")
        
        print("\n✅ כל הבדיקות הושלמו בהצלחה!")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקה: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_analyzer()
    if success:
        print("\n🎉 EnhancedAdvancedAnalyzer פועל במלואו!")
    else:
        print("\n⚠️ יש בעיות שדורשות תיקון") 