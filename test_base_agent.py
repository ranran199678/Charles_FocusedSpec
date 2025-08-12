#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקת קובץ base_agent.py
בודק שהמחלקה עובדת כמו שצריך ושכל הפונקציות זמינות
"""

import sys
import os
import logging
import pandas as pd
from typing import Dict, Any, Optional

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# הגדרת לוגים
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_base_agent_import():
    """בדיקת ייבוא המחלקה"""
    try:
        from core.base.base_agent import BaseAgent
        print("✅ ייבוא BaseAgent הצליח")
        return True
    except Exception as e:
        print(f"❌ שגיאה בייבוא BaseAgent: {e}")
        return False

def test_base_agent_instantiation():
    """בדיקת יצירת מופע של המחלקה"""
    try:
        from core.base.base_agent import BaseAgent
        
        # יצירת מחלקה פשוטה לבדיקה
        class TestAgent(BaseAgent):
            def analyze(self, *args, **kwargs):
                return {
                    "score": 5,
                    "explanation": "בדיקה מוצלחת",
                    "details": {"test": True}
                }
        
        # יצירת מופע עם קונפיגורציה
        config = {"debug": True, "default_days": 30}
        agent = TestAgent(config)
        
        print(f"✅ יצירת מופע הצליחה - שם: {agent.name}")
        print(f"   debug: {agent.debug}")
        print(f"   default_days: {agent.default_days}")
        
        return True
    except Exception as e:
        print(f"❌ שגיאה ביצירת מופע: {e}")
        return False

def test_data_managers():
    """בדיקת מנהלי הנתונים"""
    try:
        from core.base.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def analyze(self, *args, **kwargs):
                return {"score": 1, "explanation": "test", "details": {}}
        
        agent = TestAgent()
        
        print(f"✅ מנהלי נתונים אותחלו:")
        print(f"   data_manager: {agent.data_manager is not None}")
        print(f"   data_fetcher: {agent.data_fetcher is not None}")
        print(f"   fmp_client: {agent.fmp_client is not None}")
        
        return True
    except Exception as e:
        print(f"❌ שגיאה באתחול מנהלי נתונים: {e}")
        return False

def test_agent_methods():
    """בדיקת הפונקציות הבסיסיות"""
    try:
        from core.base.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def analyze(self, *args, **kwargs):
                return {
                    "score": 8,
                    "explanation": "בדיקת פונקציות",
                    "details": {"method_test": True}
                }
        
        agent = TestAgent({"debug": True})
        
        # בדיקת פונקציות בסיסיות
        print("✅ בדיקת פונקציות בסיסיות:")
        
        # בדיקת log
        agent.log("הודעה לבדיקה")
        
        # בדיקת validate_input
        result = agent.validate_input("test")
        print(f"   validate_input: {result}")
        
        # בדיקת pre_process
        args, kwargs = agent.pre_process("test", param="value")
        print(f"   pre_process: {args}, {kwargs}")
        
        # בדיקת post_process
        processed = agent.post_process({"score": 5})
        print(f"   post_process: {processed}")
        
        return True
    except Exception as e:
        print(f"❌ שגיאה בבדיקת פונקציות: {e}")
        return False

def test_agent_run():
    """בדיקת הרצת הסוכן"""
    try:
        from core.base.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def analyze(self, symbol, **kwargs):
                return {
                    "score": 7,
                    "explanation": f"בדיקה עבור {symbol}",
                    "details": {"symbol": symbol, "test": True}
                }
        
        agent = TestAgent({"debug": True})
        
        # הרצת הסוכן
        result = agent.run(symbol="AAPL")
        
        print("✅ הרצת הסוכן הצליחה:")
        print(f"   score: {result.get('score')}")
        print(f"   explanation: {result.get('explanation')}")
        print(f"   details: {result.get('details')}")
        
        return True
    except Exception as e:
        print(f"❌ שגיאה בהרצת הסוכן: {e}")
        return False

def test_error_handling():
    """בדיקת טיפול בשגיאות"""
    try:
        from core.base.base_agent import BaseAgent
        
        class FailingAgent(BaseAgent):
            def analyze(self, *args, **kwargs):
                raise ValueError("שגיאה מכוונת לבדיקה")
        
        agent = FailingAgent({"debug": True})
        
        # הרצת סוכן שנכשל
        result = agent.run(symbol="TEST")
        
        print("✅ טיפול בשגיאות עובד:")
        print(f"   fallback score: {result.get('score')}")
        print(f"   fallback explanation: {result.get('explanation')}")
        
        return True
    except Exception as e:
        print(f"❌ שגיאה בבדיקת טיפול בשגיאות: {e}")
        return False

def test_dummy_result():
    """בדיקת תוצאה דמוית"""
    try:
        from core.base.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def analyze(self, *args, **kwargs):
                return self._get_dummy_result("בדיקה דמוית")
        
        agent = TestAgent()
        result = agent.run()
        
        print("✅ תוצאה דמוית עובדת:")
        print(f"   dummy score: {result.get('score')}")
        print(f"   dummy explanation: {result.get('explanation')}")
        
        return True
    except Exception as e:
        print(f"❌ שגיאה בבדיקת תוצאה דמוית: {e}")
        return False

def main():
    """הרצת כל הבדיקות"""
    print("🔍 מתחיל בדיקת base_agent.py...\n")
    
    tests = [
        ("ייבוא המחלקה", test_base_agent_import),
        ("יצירת מופע", test_base_agent_instantiation),
        ("מנהלי נתונים", test_data_managers),
        ("פונקציות בסיסיות", test_agent_methods),
        ("הרצת הסוכן", test_agent_run),
        ("טיפול בשגיאות", test_error_handling),
        ("תוצאה דמוית", test_dummy_result),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 בודק: {test_name}")
        print("-" * 50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - הצליח")
            else:
                print(f"❌ {test_name} - נכשל")
        except Exception as e:
            print(f"❌ {test_name} - שגיאה: {e}")
    
    print(f"\n📊 סיכום בדיקות:")
    print(f"   הצליחו: {passed}/{total}")
    print(f"   אחוז הצלחה: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 כל הבדיקות הצליחו! base_agent.py עובד כמו שצריך.")
    else:
        print("⚠️  יש בעיות שצריכות תיקון.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 