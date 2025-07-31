#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_alpha_score_engine():
    """בדיקת AlphaScoreEngine"""
    try:
        print("🔧 בדיקת AlphaScoreEngine...")
        
        # ייבוא המנוע
        from core.alpha_score_engine import AlphaScoreEngine
        engine = AlphaScoreEngine()
        print("✅ AlphaScoreEngine יובא בהצלחה")
        
        # בדיקת EnhancedAdvancedAnalyzer
        print(f"✅ EnhancedAdvancedAnalyzer ב-AGENT_WEIGHTS: {'EnhancedAdvancedAnalyzer' in engine.AGENT_WEIGHTS}")
        print(f"✅ משקל EnhancedAdvancedAnalyzer: {engine.AGENT_WEIGHTS.get('EnhancedAdvancedAnalyzer', 'לא נמצא')}")
        
        # בדיקת סוכנים נטענים
        print(f"✅ סוכנים נטענים: {len(engine.agents)}")
        print(f"✅ EnhancedAdvancedAnalyzer נטען: {'EnhancedAdvancedAnalyzer' in engine.agents}")
        
        # בדיקת סטטוס
        status = engine.get_agent_status()
        print(f"✅ סך הכל סוכנים: {status['total_agents']}")
        print(f"✅ סוכנים נטענים: {status['loaded_agents']}")
        print(f"✅ שמות סוכנים נטענים: {status['loaded_agent_names']}")
        
        print("\n✅ כל הבדיקות הושלמו בהצלחה!")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקה: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_alpha_score_engine()
    if success:
        print("\n🎉 AlphaScoreEngine פועל במלואו!")
    else:
        print("\n⚠️ יש בעיות שדורשות תיקון") 