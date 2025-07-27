#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
import numpy as np

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple_scores():
    """בדיקה פשוטה של ציוני הסוכנים"""
    try:
        print("🔧 בדיקת ציוני סוכנים...")
        
        # יצירת נתוני דוגמה
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        base_price = 100
        prices = []
        for i in range(len(dates)):
            price = base_price + i * 0.5 + np.random.normal(0, 2)
            prices.append(max(price, 50))
        
        volumes = []
        for i in range(len(dates)):
            volume = 1000000 + np.random.normal(0, 200000)
            volumes.append(max(volume, 100000))
        
        sample_data = pd.DataFrame({
            'Open': [p * 0.99 for p in prices],
            'High': [p * 1.02 for p in prices],
            'Low': [p * 0.98 for p in prices],
            'Close': prices,
            'Volume': volumes
        }, index=dates)
        
        print(f"✅ נתוני דוגמה נוצרו: {len(sample_data)} שורות")
        
        # בדיקת AlphaScoreEngine
        from core.alpha_score_engine import AlphaScoreEngine
        engine = AlphaScoreEngine()
        
        print(f"✅ AlphaScoreEngine נטען עם {len(engine.agents)} סוכנים")
        
        # הרצת הערכה
        result = engine.evaluate('TEST', sample_data)
        
        print("\n" + "=" * 80)
        print("🏆 ציוני סוכנים:")
        print("=" * 80)
        
        agent_scores = result.get('agent_scores', {})
        final_score = result.get('final_score', 'N/A')
        agents_count = result.get('agents_count', 0)
        
        print(f"📈 ציון סופי: {final_score}")
        print(f"📊 מספר סוכנים פעילים: {agents_count}")
        print()
        
        if agent_scores:
            # מיון לפי ציון
            sorted_scores = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
            
            for i, (agent_name, score) in enumerate(sorted_scores, 1):
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
        
        # סיכום סטטיסטי
        if agent_scores:
            scores_list = list(agent_scores.values())
            print(f"\n📊 סיכום סטטיסטי:")
            print(f"ציון ממוצע: {sum(scores_list) / len(scores_list):.1f}")
            print(f"ציון מקסימלי: {max(scores_list)}")
            print(f"ציון מינימלי: {min(scores_list)}")
            print(f"סוכנים מעל 80: {sum(1 for s in scores_list if s >= 80)}")
            print(f"סוכנים מתחת ל-40: {sum(1 for s in scores_list if s < 40)}")
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_scores()
    if success:
        print("\n🎉 בדיקה הושלמה!")
    else:
        print("\n⚠️ יש בעיות") 