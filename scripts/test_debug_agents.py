#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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

def test_problematic_agents():
    """בדיקת הסוכנים הבעייתיים"""
    try:
        print("🔧 בדיקת הסוכנים הבעייתיים...")
        
        # יצירת נתוני דוגמה
        sample_data = create_sample_data()
        print(f"✅ נתוני דוגמה נוצרו: {len(sample_data)} שורות")
        
        # רשימת הסוכנים הבעייתיים
        problematic_agents = [
            "BullishPatternSpotter",
            "ADXScoreAgent", 
            "TrendShiftDetector",
            "ParabolicAgent",
            "MovingAveragePressureBot"
        ]
        
        results = {}
        
        for agent_name in problematic_agents:
            try:
                print(f"\n📊 בדיקת {agent_name}...")
                
                # ייבוא הסוכן
                module_name = f"core.{agent_name.lower()}"
                class_name = agent_name
                
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    agent_class = getattr(module, class_name)
                    agent = agent_class()
                    
                    # בדיקת חתימת הפונקציה
                    import inspect
                    sig = inspect.signature(agent.analyze)
                    print(f"  - חתימת analyze: {sig}")
                    
                    # הרצת הסוכן
                    if len(sig.parameters) == 2:
                        result = agent.analyze('TEST')
                    else:
                        result = agent.analyze('TEST', sample_data)
                    
                    score = result.get('score', 'N/A')
                    explanation = result.get('explanation', 'N/A')[:100]
                    
                    print(f"  - ציון: {score}")
                    print(f"  - הסבר: {explanation}...")
                    
                    results[agent_name] = {
                        'score': score,
                        'explanation': explanation,
                        'status': '✅ הצלחה'
                    }
                    
                except Exception as e:
                    print(f"  - שגיאה: {str(e)}")
                    results[agent_name] = {
                        'score': 'N/A',
                        'explanation': str(e),
                        'status': '❌ שגיאה'
                    }
                    
            except Exception as e:
                print(f"  - שגיאה בייבוא: {str(e)}")
                results[agent_name] = {
                    'score': 'N/A',
                    'explanation': f"שגיאה בייבוא: {str(e)}",
                    'status': '❌ שגיאה ייבוא'
                }
        
        # סיכום
        print("\n" + "=" * 60)
        print("📋 סיכום בדיקת הסוכנים הבעייתיים:")
        print("=" * 60)
        
        for agent_name, result in results.items():
            print(f"🎯 {agent_name}:")
            print(f"  - סטטוס: {result['status']}")
            print(f"  - ציון: {result['score']}")
            print(f"  - הסבר: {result['explanation']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקה: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_problematic_agents()
    if success:
        print("\n🎉 בדיקת הסוכנים הבעייתיים הושלמה!")
    else:
        print("\n⚠️ יש בעיות בבדיקת הסוכנים") 