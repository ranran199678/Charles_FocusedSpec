import os
import sys
import pytest

# ✅ הוספת נתיב לתיקיית הפרויקט הראשית
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.trend_shift_detector import TrendShiftDetector

@pytest.mark.integration
def test_trend_shift_detector_on_symbols():
    symbols = ["OPEN"]
    intervals = ["1day", "30min"]

    for interval in intervals:
        print(f"\n🔄 בדיקות עבור interval = {interval}\n{'-'*40}")
        for symbol in symbols:
            print(f"\n🧪 סימבול: {symbol}")
            detector = TrendShiftDetector(symbol, interval=interval)
            result = detector.run()

            # בדיקות תקינות לפלט
            assert "trend_shift_score" in result, "❌ חסר ציון מגמה"
            assert "shift_category" in result, "❌ חסרה קטגוריה"
            assert "explanations" in result, "❌ חסרים הסברים"
            assert isinstance(result["explanations"], list), "❌ ההסברים אינם רשימה"

            # תצוגה
            print(f"✅ [{interval}] ציון כולל: {result['trend_shift_score']} | קטגוריה: {result['shift_category']}")
            print("📚 הסברים:")
            for exp in result["explanations"]:
                if "Divergence" in exp or "סטייה" in exp:
                    print(f"   🔍 {exp} ← 🧠 תת-סוכן זיהה סטייה")
                else:
                    print(f"   - {exp}")

            # סיכום סטייה
            if any("Divergence" in exp for exp in result["explanations"]):
                print("🧠 ✅ תת-סוכן MACD/RSI Divergence איתר סטייה בשוק.")
            else:
                print("🧠 ⛔ לא זוהתה סטייה בין מחיר לאינדיקטורים.")
