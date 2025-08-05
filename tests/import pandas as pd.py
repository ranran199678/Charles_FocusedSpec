import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from core.advanced_pattern_analyzer import AdvancedPatternAnalyzer
from utils.data_fetcher import DataFetcher

def test_advanced_pattern_analyzer_1min():
    symbol = "AAPL"
    fetcher = DataFetcher()
    price_df = fetcher.fetch_prices_batch([symbol], interval="1min")[symbol]

    if price_df is not None and not price_df.empty:
        last_50 = price_df.tail(50)
        assert not last_50.empty, "DataFrame ריק אחרי סינון"
        assert all(col in last_50.columns for col in ["close", "high", "low", "volume"]), "חסרות עמודות חובה"

        # בדיקה האם הנתונים הם באמת 1min
        if len(last_50) > 1:
            time_diffs = last_50.index.to_series().diff().dropna()
            min_diff = time_diffs.min()
            max_diff = time_diffs.max()
            if not pd.Timedelta('60s') <= min_diff <= pd.Timedelta('61s') or not pd.Timedelta('60s') <= max_diff <= pd.Timedelta('61s'):
                print("\n⚠️ אזהרה: הנתונים שהתקבלו אינם 1min! (הפרש מינימלי בין נרות:", min_diff, ", מקסימלי:", max_diff, ")")
            else:
                print("\n✔️ הנתונים הם 1min (הפרש בין נרות:", min_diff, ")")

        agent = AdvancedPatternAnalyzer()
        result = agent.analyze(symbol, price_df=last_50)

        # הפקת טבלה מסודרת מהתוצאה
        summary = {
            "סימבול": symbol,
            "ציון": result.get("score"),
            "מגמה": result.get("details", {}).get("trend_analysis", {}).get("overall_trend"),
            "ביצועים 20d": result.get("details", {}).get("market_analysis", {}).get("performance_20d"),
            "ביצועים 50d": result.get("details", {}).get("market_analysis", {}).get("performance_50d"),
            "נפח נוכחי": result.get("details", {}).get("volume_analysis", {}).get("current_volume"),
            "נפח ממוצע": result.get("details", {}).get("volume_analysis", {}).get("avg_volume"),
            "יחס נפח": result.get("details", {}).get("volume_analysis", {}).get("volume_ratio"),
            "תמיכה קרובה": result.get("details", {}).get("support_resistance", {}).get("nearest_support"),
            "התנגדות קרובה": result.get("details", {}).get("support_resistance", {}).get("nearest_resistance"),
            "המלצות": "; ".join(result.get("details", {}).get("recommendations", [])),
            "טווח תאריכים": f"{last_50.index.min()} - {last_50.index.max()}"
        }
        df_summary = pd.DataFrame([summary])
        print("\nטבלת ניתוח 1 דקות:")
        print(df_summary.to_string(index=False))
        print("\nתאריכים שנותחו:")
        print(last_50.index)
    else:
        print("לא התקבלו נתוני 1 דקות")

if __name__ == "__main__":
    test_advanced_pattern_analyzer_1min()