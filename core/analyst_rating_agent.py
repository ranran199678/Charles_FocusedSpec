import time
import traceback
from utils.constants import AGENT_NAMES
from utils.fmp_utils import fetch_analyst_estimates
from datetime import datetime

class AnalystRatingAgent:
    def __init__(self, config=None):
        self.config = config or {}
        self.min_strong_buy = self.config.get("min_strong_buy", 5)
        self.max_strong_sell = self.config.get("max_strong_sell", 0)
        self.check_consistency = self.config.get("check_consistency", True)
        self.min_analysts = self.config.get("min_analysts", 3)
        self.consistency_window = self.config.get("consistency_window", 3)

    def analyze(self, symbol, price_df=None):
        try:
            data = fetch_analyst_estimates(symbol)
            if not data or not isinstance(data, list):
                return {
                    "score": 1,
                    "explanation": f"❌ AnalystRatingAgent: לא נמצאו הערכות אנליסטים עבור הסימבול",
                    "details": {}
                }

            # חיתוך הערכות עדכניות
            recent_estimates = sorted(data[:self.consistency_window], key=lambda x: x.get("date", ""), reverse=True)

            def count_totals(estimates):
                total = {
                    "strongBuy": 0, "buy": 0, "hold": 0,
                    "sell": 0, "strongSell": 0
                }
                for entry in estimates:
                    for key in total:
                        total[key] += int(entry.get(key, 0))
                return total

            totals = count_totals(recent_estimates)
            total_analysts = sum(totals.values())

            explanation = f"🔍 AnalystRatingAgent – ניתוח {self.consistency_window} הערכות אחרונות: {totals} | סה\"כ אנליסטים: {total_analysts}. "

            if total_analysts < self.min_analysts:
                return {
                    "score": 1,
                    "explanation": explanation + "❌ לא מספיק אנליסטים לבחינה מהימנה.",
                    "details": totals
                }

            # ניקוד ע"פ שליטה של המלצות חיוביות והאם קיימת עקביות
            strong_buys = totals["strongBuy"]
            strong_sells = totals["strongSell"]
            buy = totals["buy"]
            hold = totals["hold"]
            sell = totals["sell"]

            # מדיניות ניקוד
            if strong_buys >= 10 and strong_sells == 0 and buy > hold:
                score = 95
                level = "🚀 המלצת קנייה חזקה ועקבית"
            elif strong_buys >= 5 and strong_sells <= 1:
                score = 80
                level = "✅ המלצת קנייה משמעותית"
            elif buy > hold and sell <= 2:
                score = 65
                level = "📈 נטייה חיובית"
            elif hold > buy and sell > 2:
                score = 40
                level = "⚠️ נטייה לשלילית"
            else:
                score = 25
                level = "❌ חוסר ודאות / שליליות"

            explanation += f"\n📊 סיכום: {level} (ציון: {score})"

            return {
                "score": score,
                "explanation": explanation,
                "details": totals
            }

        except Exception as e:
            return {
                "score": 1,
                "explanation": f"שגיאת AnalystRatingAgent: {e}\n{traceback.format_exc()}",
                "details": {}
            }
