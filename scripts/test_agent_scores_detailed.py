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

def test_all_agent_scores():
    """בדיקת ציוני כל הסוכנים"""
    try:
        print("🔧 בדיקת ציוני כל הסוכנים...")
        print("=" * 80)
        
        # יצירת נתוני דוגמה
        sample_data = create_sample_data()
        print(f"✅ נתוני דוגמה נוצרו: {len(sample_data)} שורות")
        
        # בדיקת AlphaScoreEngine
        from core.alpha_score_engine import AlphaScoreEngine
        engine = AlphaScoreEngine()
        
        print(f"\n📊 בדיקת AlphaScoreEngine...")
        print(f"✅ מספר סוכנים נטענים: {len(engine.agents)}")
        
        # הרצת הערכה
        result = engine.evaluate('TEST', sample_data)
        
        print(f"\n🎯 תוצאות מפורטות:")
        print("=" * 80)
        
        # הצגת ציוני כל סוכן
        agent_scores = result.get('agent_scores', {})
        agent_details = result.get('agent_details', {})
        
        if agent_scores:
            print(f"📈 ציון סופי: {result.get('final_score', 'N/A')}")
            print(f"📊 מספר סוכנים פעילים: {result.get('agents_count', 0)}")
            print(f"⚖️ משקל כולל: {result.get('total_weight', 0)}")
            print()
            
            # מיון לפי ציון
            sorted_scores = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
            
            print("🏆 ציוני סוכנים (ממוינים לפי ציון):")
            print("-" * 80)
            
            for i, (agent_name, score) in enumerate(sorted_scores, 1):
                details = agent_details.get(agent_name, {})
                explanation = details.get('explanation', 'אין הסבר')
                
                # סימון צבע לפי ציון
                if score >= 80:
                    status = "🟢 מעולה"
                elif score >= 60:
                    status = "🟡 טוב"
                elif score >= 40:
                    status = "🟠 בינוני"
                else:
                    status = "🔴 נמוך"
                
                print(f"{i:2d}. {agent_name:<30} | {score:3d}/100 | {status}")
                print(f"    הסבר: {explanation[:80]}...")
                print()
        else:
            print("❌ אין ציוני סוכנים זמינים")
        
        # סיכום סטטיסטי
        if agent_scores:
            scores_list = list(agent_scores.values())
            print("📊 סיכום סטטיסטי:")
            print("-" * 40)
            print(f"ציון ממוצע: {sum(scores_list) / len(scores_list):.1f}")
            print(f"ציון מקסימלי: {max(scores_list)}")
            print(f"ציון מינימלי: {min(scores_list)}")
            print(f"סוכנים מעל 80: {sum(1 for s in scores_list if s >= 80)}")
            print(f"סוכנים מתחת ל-40: {sum(1 for s in scores_list if s < 40)}")
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקה: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_agent_scores()
    if success:
        print("\n🎉 בדיקת ציוני הסוכנים הושלמה!")
    else:
        print("\n⚠️ יש בעיות בבדיקת הסוכנים") 