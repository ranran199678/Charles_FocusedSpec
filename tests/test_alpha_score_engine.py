import os
import sys
import pytest

# מאפשר הרצה מתוך כל סביבת פיתוח
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

@pytest.mark.integration
def test_alpha_score_engine_full_run():
    symbols = ["QBTS", "NVDA", "PLTR"]
    engine = AlphaScoreEngine()
    fetcher = DataFetcher()

    for symbol in symbols:
        print(f"\n🧪 הרצה עבור: {symbol}")
        price_data = fetcher.fetch_prices_batch([symbol])
        df = price_data.get(symbol)

        assert df is not None and not df.empty, f"❌ אין נתונים זמינים עבור {symbol}"

        result = engine.evaluate(symbol, df)

        assert "score" in result, "❌ חסר שדה score"
        assert "signals" in result, "❌ חסר שדה signals"
        assert "explanations" in result, "❌ חסר שדה explanations"

        print(f"📊 ציון אלפא כולל: {result['score']}")
        print(f"📈 המלצה: {result['recommendation']}")
        print(f"🔍 ניתוח סוכנים פעילים ({len(result['signals'])} סוכנים):")

        for agent_name, agent_score in result["signals"].items():
            explanation = result["explanations"].get(agent_name, "")
            tag = "✅" if agent_score > 50 else "⛔" if agent_score < 20 else "➖"
            if "TrendShift" in agent_name:
                tag = "📊🔄"  # דגש לסוכן שלנו
            print(f" {tag} {agent_name}: {agent_score} | {explanation}")

        # סוכן ספציפי
        trend_score = result["signals"].get("TrendShiftAgent", None)
        assert trend_score is not None, "❌ סוכן TrendShiftAgent לא מחזיר תוצאה"
        assert isinstance(trend_score, int), "❌ ציון TrendShiftAgent אינו מספר"

        if trend_score >= 60:
            print("📊 ✅ TrendShiftAgent מזהה שינוי מגמה חיובי!")
        elif trend_score <= 20:
            print("📉 ⛔ TrendShiftAgent מזהה מגמת ירידה.")
        else:
            print("🔄 TrendShiftAgent מזהה מצב נייטרלי.")
