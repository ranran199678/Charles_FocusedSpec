import time
import traceback
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from core.base.base_agent import BaseAgent

class AnalystRatingAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__(config)
        self.min_strong_buy = self.config.get("min_strong_buy", 5)
        self.max_strong_sell = self.config.get("max_strong_sell", 0)
        self.check_consistency = self.config.get("check_consistency", True)
        self.min_analysts = self.config.get("min_analysts", 3)
        self.consistency_window = self.config.get("consistency_window", 3)
        self.trend_weight = self.config.get("trend_weight", 0.3)
        self.accuracy_weight = self.config.get("accuracy_weight", 0.2)
        self.industry_weight = self.config.get("industry_weight", 0.15)
        self.consensus_weight = self.config.get("consensus_weight", 0.35)

    def analyze(self, symbol, price_df=None):
        try:
            # שימוש במנהל הנתונים החכם במקום קריאה ישירה ל-API
            if not self.fmp_client:
                return {
                    "score": 1,
                    "explanation": f"❌ AnalystRatingAgent: מנהל נתונים לא זמין",
                    "details": {}
                }

            # שליפת נתוני אנליסטים דרך מנהל הנתונים
            data = self.fmp_client.get_analyst_estimates(symbol)
            if not data or not isinstance(data, list):
                return {
                    "score": 1,
                    "explanation": f"❌ AnalystRatingAgent: לא נמצאו הערכות אנליסטים עבור הסימבול",
                    "details": {}
                }

            # ניתוח מפורט של הערכות אנליסטים
            analysis_result = self._analyze_analyst_estimates(data, symbol)
            
            # ניתוח מגמות הערכות
            trend_analysis = self._analyze_rating_trends(data)
            
            # ניתוח דיוק היסטורי
            accuracy_analysis = self._analyze_historical_accuracy(symbol, data)
            
            # השוואה לתעשייה
            industry_analysis = self._analyze_industry_comparison(symbol, data)
            
            # חישוב ציון סופי משוקלל
            final_score = self._calculate_weighted_score(
                analysis_result, trend_analysis, accuracy_analysis, industry_analysis
            )
            
            explanation = self._build_comprehensive_explanation(
                analysis_result, trend_analysis, accuracy_analysis, industry_analysis, final_score
            )

            return {
                "score": final_score,
                "explanation": explanation,
                "details": {
                    "consensus_analysis": analysis_result,
                    "trend_analysis": trend_analysis,
                    "accuracy_analysis": accuracy_analysis,
                    "industry_analysis": industry_analysis,
                    "raw_data": data[:5]  # 5 הערכות אחרונות
                }
            }

        except Exception as e:
            self.handle_error(e)
            return self.fallback()

    def _analyze_analyst_estimates(self, data, symbol):
        """ניתוח מפורט של הערכות אנליסטים"""
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

        if total_analysts < self.min_analysts:
            return {
                "score": 1,
                "total_analysts": total_analysts,
                "totals": totals,
                "insufficient_data": True
            }

        # חישוב אחוזי המלצות
        strong_buy_pct = (totals["strongBuy"] / total_analysts) * 100
        buy_pct = (totals["buy"] / total_analysts) * 100
        hold_pct = (totals["hold"] / total_analysts) * 100
        sell_pct = (totals["sell"] / total_analysts) * 100
        strong_sell_pct = (totals["strongSell"] / total_analysts) * 100

        # ניקוד בסיסי לפי אחוזי המלצות
        base_score = (
            strong_buy_pct * 1.0 + 
            buy_pct * 0.7 + 
            hold_pct * 0.4 + 
            sell_pct * 0.2 + 
            strong_sell_pct * 0.0
        )

        return {
            "score": min(100, max(1, int(base_score))),
            "total_analysts": total_analysts,
            "totals": totals,
            "percentages": {
                "strong_buy": strong_buy_pct,
                "buy": buy_pct,
                "hold": hold_pct,
                "sell": sell_pct,
                "strong_sell": strong_sell_pct
            },
            "insufficient_data": False
        }

    def _analyze_rating_trends(self, data):
        """ניתוח מגמות בהערכות לאורך זמן"""
        if len(data) < 2:
            return {"score": 50, "trend": "stable", "change": 0}

        # השוואה בין הערכות אחרונות לבין קודמות
        recent = data[:2]
        older = data[2:4] if len(data) >= 4 else data[1:2]

        def calculate_rating_score(estimates):
            if not estimates:
                return 50
            total = {"strongBuy": 0, "buy": 0, "hold": 0, "sell": 0, "strongSell": 0}
            for entry in estimates:
                for key in total:
                    total[key] += int(entry.get(key, 0))
            total_analysts = sum(total.values())
            if total_analysts == 0:
                return 50
            return (
                (total["strongBuy"] / total_analysts) * 100 + 
                (total["buy"] / total_analysts) * 70 + 
                (total["hold"] / total_analysts) * 40 + 
                (total["sell"] / total_analysts) * 20
            )

        recent_score = calculate_rating_score(recent)
        older_score = calculate_rating_score(older)
        change = recent_score - older_score

        if change > 10:
            trend = "improving"
            trend_score = 80
        elif change > 5:
            trend = "slightly_improving"
            trend_score = 65
        elif change < -10:
            trend = "deteriorating"
            trend_score = 20
        elif change < -5:
            trend = "slightly_deteriorating"
            trend_score = 35
        else:
            trend = "stable"
            trend_score = 50

        return {
            "score": trend_score,
            "trend": trend,
            "change": change,
            "recent_score": recent_score,
            "older_score": older_score
        }

    def _analyze_historical_accuracy(self, symbol, current_data):
        """ניתוח דיוק היסטורי של אנליסטים"""
        try:
            # שליפת נתוני מחירים היסטוריים
            price_data = self.get_stock_data(symbol, days=365)
            if price_data is None or price_data.empty:
                return {"score": 50, "accuracy": "unknown"}

            # שליפת הערכות קודמות (אם זמינות)
            # זה דורש API מתקדם יותר - כרגע נחזיר ערך ברירת מחדל
            return {
                "score": 60,  # ברירת מחדל - דיוק בינוני
                "accuracy": "moderate",
                "note": "דיוק היסטורי דורש נתונים נוספים"
            }
        except Exception:
            return {"score": 50, "accuracy": "unknown"}

    def _analyze_industry_comparison(self, symbol, data):
        """השוואה לתעשייה"""
        try:
            # שליפת מידע על התעשייה
            company_info = self.fmp_client.get_company_profile(symbol)
            if not company_info:
                return {"score": 50, "industry": "unknown"}

            sector = company_info.get("sector", "")
            industry = company_info.get("industry", "")

            # השוואה בסיסית - כרגע נחזיר ערך ברירת מחדל
            # זה דורש נתונים על ממוצעי תעשייה
            return {
                "score": 55,
                "sector": sector,
                "industry": industry,
                "note": "השוואה לתעשייה דורשת נתונים נוספים"
            }
        except Exception:
            return {"score": 50, "industry": "unknown"}

    def _calculate_weighted_score(self, consensus, trend, accuracy, industry):
        """חישוב ציון סופי משוקלל"""
        consensus_score = consensus.get("score", 50)
        trend_score = trend.get("score", 50)
        accuracy_score = accuracy.get("score", 50)
        industry_score = industry.get("score", 50)

        weighted_score = (
            consensus_score * self.consensus_weight +
            trend_score * self.trend_weight +
            accuracy_score * self.accuracy_weight +
            industry_score * self.industry_weight
        )

        return max(1, min(100, int(weighted_score)))

    def _build_comprehensive_explanation(self, consensus, trend, accuracy, industry, final_score):
        """בניית הסבר מקיף"""
        explanation = f"🔍 AnalystRatingAgent – ניתוח מקיף:\n"
        
        # ניתוח קונצנזוס
        if consensus.get("insufficient_data"):
            explanation += f"❌ לא מספיק אנליסטים ({consensus['total_analysts']}) לבחינה מהימנה.\n"
        else:
            totals = consensus["totals"]
            explanation += f"📊 קונצנזוס: Strong Buy: {totals['strongBuy']}, Buy: {totals['buy']}, Hold: {totals['hold']}, Sell: {totals['sell']}, Strong Sell: {totals['strongSell']}\n"
        
        # ניתוח מגמה
        trend_info = trend.get("trend", "stable")
        change = trend.get("change", 0)
        if change > 0:
            explanation += f"📈 מגמה: שיפור של {change:.1f} נקודות\n"
        elif change < 0:
            explanation += f"📉 מגמה: ירידה של {abs(change):.1f} נקודות\n"
        else:
            explanation += f"➡️ מגמה: יציבה\n"
        
        # דיוק היסטורי
        accuracy_info = accuracy.get("accuracy", "unknown")
        explanation += f"🎯 דיוק היסטורי: {accuracy_info}\n"
        
        # השוואה לתעשייה
        industry_name = industry.get("industry", "לא ידוע")
        explanation += f"🏭 תעשייה: {industry_name}\n"
        
        # ציון סופי
        if final_score >= 80:
            level = "🚀 המלצה חזקה מאוד"
        elif final_score >= 65:
            level = "✅ המלצה חיובית"
        elif final_score >= 45:
            level = "⚠️ המלצה מעורבת"
        else:
            level = "❌ המלצה שלילית"
        
        explanation += f"🎯 ציון סופי: {final_score} - {level}"
        
        return explanation
