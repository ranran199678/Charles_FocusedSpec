import sys
import os
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# הוספת הנתיב לספריות
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.base_agent import BaseAgent

class MacroTrendScanner(BaseAgent):
    """
    Macro Trend Scanner - ניתוח מגמות מאקרו כלכליות והשפעתן על השוק
    
    מנתח:
    - GDP, FED, PMI, CPI, אינפלציה
    - ריביות, מדיניות מוניטרית
    - מגמות סקטוריאליות
    - השפעות גלובליות
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # API Keys למקורות נתונים מאקרו
        self.fred_api_key = os.getenv("FRED_API_KEY", "")
        self.world_bank_api_key = os.getenv("WORLDBANK_API_KEY", "")
        
        # משקלים לניתוח
        self.macro_weights = {
            "gdp_growth": 0.25,
            "inflation": 0.20,
            "interest_rates": 0.20,
            "pmi": 0.15,
            "employment": 0.10,
            "consumer_sentiment": 0.10
        }
        
        # ספיי ציונים
        self.score_thresholds = {
            "very_bullish": 80,
            "bullish": 60,
            "neutral": 40,
            "bearish": 20,
            "very_bearish": 0
        }
        
        self.log("Macro Trend Scanner initialized")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח מגמות מאקרו והשפעתן על המניה
        
        Args:
            symbol: סמל המניה
            price_df: נתוני מחירים (לא נדרש לניתוח מאקרו)
            
        Returns:
            Dict עם ציון, ניתוח ופרטים
        """
        try:
            self.log(f"Starting macro analysis for {symbol}")
            
            # 1. איסוף נתוני מאקרו
            macro_data = self._fetch_macro_data()
            
            # 2. ניתוח מגמות
            trend_analysis = self._analyze_macro_trends(macro_data)
            
            # 3. חישוב ציון כולל
            overall_score = self._calculate_macro_score(trend_analysis)
            
            # 4. ניתוח השפעה על סקטור
            sector_impact = self._analyze_sector_impact(symbol, trend_analysis)
            
            # 5. יצירת סיכום
            summary = self._generate_macro_summary(trend_analysis, sector_impact)
            
            result = {
                "score": overall_score,
                "sentiment": self._get_sentiment(overall_score),
                "summary": summary,
                "details": {
                    "macro_data": macro_data,
                    "trend_analysis": trend_analysis,
                    "sector_impact": sector_impact,
                    "recommendations": self._generate_recommendations(trend_analysis)
                }
            }
            
            self.log(f"Macro analysis completed for {symbol}: Score {overall_score}")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return {
                "score": 50,  # ציון ניטרלי במקרה של שגיאה
                "sentiment": "neutral",
                "summary": f"שגיאה בניתוח מאקרו: {str(e)}",
                "details": {}
            }

    def _fetch_macro_data(self) -> Dict:
        """איסוף נתוני מאקרו ממקורות שונים"""
        macro_data = {}
        
        try:
            # 1. נתוני GDP (אם יש API)
            if self.fred_api_key:
                macro_data["gdp"] = self._fetch_gdp_data()
            
            # 2. נתוני אינפלציה
            macro_data["inflation"] = self._fetch_inflation_data()
            
            # 3. נתוני ריביות
            macro_data["interest_rates"] = self._fetch_interest_rates()
            
            # 4. נתוני PMI
            macro_data["pmi"] = self._fetch_pmi_data()
            
            # 5. נתוני תעסוקה
            macro_data["employment"] = self._fetch_employment_data()
            
            # 6. נתוני סנטימנט צרכנים
            macro_data["consumer_sentiment"] = self._fetch_consumer_sentiment()
            
        except Exception as e:
            self.log(f"Error fetching macro data: {e}")
            # נתונים דמו במקרה של שגיאה
            macro_data = self._get_demo_macro_data()
        
        return macro_data

    def _get_demo_macro_data(self) -> Dict:
        """נתוני דמו למקרה שאין גישה ל-API"""
        return {
            "gdp": {
                "current": 2.1,
                "previous": 1.9,
                "trend": "stable",
                "score": 60
            },
            "inflation": {
                "current": 3.2,
                "previous": 3.8,
                "trend": "declining",
                "score": 70
            },
            "interest_rates": {
                "current": 5.25,
                "previous": 5.50,
                "trend": "stable",
                "score": 50
            },
            "pmi": {
                "current": 52.1,
                "previous": 50.9,
                "trend": "improving",
                "score": 65
            },
            "employment": {
                "current": 3.7,
                "previous": 3.8,
                "trend": "improving",
                "score": 75
            },
            "consumer_sentiment": {
                "current": 68.2,
                "previous": 65.7,
                "trend": "improving",
                "score": 70
            }
        }

    def _analyze_macro_trends(self, macro_data: Dict) -> Dict:
        """ניתוח מגמות הנתונים המאקרו"""
        trends = {}
        
        for indicator, data in macro_data.items():
            if isinstance(data, dict) and "trend" in data:
                current = data.get("current", 0)
                previous = data.get("previous", 0)
                trend = data.get("trend", "stable")
                score = data.get("score", 50)
                
                # ניתוח מגמה
                if current > previous:
                    trend_direction = "improving"
                elif current < previous:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
                
                trends[indicator] = {
                    "current_value": current,
                    "previous_value": previous,
                    "change": current - previous,
                    "trend_direction": trend_direction,
                    "trend_strength": self._calculate_trend_strength(current, previous),
                    "score": score,
                    "impact": self._assess_macro_impact(indicator, current, trend_direction)
                }
        
        return trends

    def _calculate_trend_strength(self, current: float, previous: float) -> str:
        """חישוב עוצמת המגמה"""
        change_pct = abs((current - previous) / previous * 100) if previous != 0 else 0
        
        if change_pct > 5:
            return "strong"
        elif change_pct > 2:
            return "moderate"
        else:
            return "weak"

    def _assess_macro_impact(self, indicator: str, value: float, direction: str) -> str:
        """הערכת השפעת המדד על השוק"""
        impact_map = {
            "gdp": {"improving": "positive", "declining": "negative", "stable": "neutral"},
            "inflation": {"improving": "negative", "declining": "positive", "stable": "neutral"},
            "interest_rates": {"improving": "negative", "declining": "positive", "stable": "neutral"},
            "pmi": {"improving": "positive", "declining": "negative", "stable": "neutral"},
            "employment": {"improving": "positive", "declining": "negative", "stable": "neutral"},
            "consumer_sentiment": {"improving": "positive", "declining": "negative", "stable": "neutral"}
        }
        
        return impact_map.get(indicator, {}).get(direction, "neutral")

    def _calculate_macro_score(self, trends: Dict) -> int:
        """חישוב ציון מאקרו כולל"""
        total_score = 0
        total_weight = 0
        
        for indicator, trend_data in trends.items():
            weight = self.macro_weights.get(indicator, 0.1)
            score = trend_data.get("score", 50)
            
            # התאמת ציון לפי השפעה
            impact = trend_data.get("impact", "neutral")
            if impact == "positive":
                adjusted_score = min(100, score + 10)
            elif impact == "negative":
                adjusted_score = max(0, score - 10)
            else:
                adjusted_score = score
            
            total_score += adjusted_score * weight
            total_weight += weight
        
        final_score = int(total_score / total_weight) if total_weight > 0 else 50
        return max(0, min(100, final_score))

    def _analyze_sector_impact(self, symbol: str, trends: Dict) -> Dict:
        """ניתוח השפעת המגמות המאקרו על הסקטור של המניה"""
        # זיהוי הסקטור של המניה
        sector = self._identify_sector(symbol)
        
        sector_impacts = {
            "technology": {
                "positive_factors": ["low_interest_rates", "high_gdp_growth", "strong_pmi"],
                "negative_factors": ["high_inflation", "rising_interest_rates", "weak_consumer_sentiment"]
            },
            "financial": {
                "positive_factors": ["rising_interest_rates", "strong_gdp_growth", "low_inflation"],
                "negative_factors": ["falling_interest_rates", "weak_gdp_growth", "high_inflation"]
            },
            "healthcare": {
                "positive_factors": ["stable_economy", "strong_consumer_sentiment", "low_inflation"],
                "negative_factors": ["recession", "weak_consumer_sentiment", "high_inflation"]
            },
            "energy": {
                "positive_factors": ["high_inflation", "strong_gdp_growth", "geopolitical_tensions"],
                "negative_factors": ["low_inflation", "weak_gdp_growth", "peaceful_conditions"]
            },
            "consumer": {
                "positive_factors": ["strong_consumer_sentiment", "low_unemployment", "stable_inflation"],
                "negative_factors": ["weak_consumer_sentiment", "high_unemployment", "high_inflation"]
            }
        }
        
        sector_impact = sector_impacts.get(sector, {
            "positive_factors": [],
            "negative_factors": []
        })
        
        # חישוב השפעה על הסקטור
        positive_score = 0
        negative_score = 0
        
        for indicator, trend_data in trends.items():
            impact = trend_data.get("impact", "neutral")
            if impact == "positive":
                positive_score += 1
            elif impact == "negative":
                negative_score += 1
        
        return {
            "sector": sector,
            "positive_factors": positive_score,
            "negative_factors": negative_score,
            "overall_impact": "positive" if positive_score > negative_score else "negative" if negative_score > positive_score else "neutral"
        }

    def _identify_sector(self, symbol: str) -> str:
        """זיהוי הסקטור של המניה (פישוט)"""
        sector_keywords = {
            "technology": ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN"],
            "financial": ["JPM", "BAC", "WFC", "GS", "MS"],
            "healthcare": ["JNJ", "PFE", "UNH", "ABBV", "TMO"],
            "energy": ["XOM", "CVX", "COP", "EOG", "SLB"],
            "consumer": ["PG", "KO", "PEP", "WMT", "HD"]
        }
        
        for sector, symbols in sector_keywords.items():
            if symbol in symbols:
                return sector
        
        return "general"  # ברירת מחדל

    def _get_sentiment(self, score: int) -> str:
        """קביעת סנטימנט לפי ציון"""
        if score >= self.score_thresholds["very_bullish"]:
            return "very_bullish"
        elif score >= self.score_thresholds["bullish"]:
            return "bullish"
        elif score >= self.score_thresholds["neutral"]:
            return "neutral"
        elif score >= self.score_thresholds["bearish"]:
            return "bearish"
        else:
            return "very_bearish"

    def _generate_macro_summary(self, trends: Dict, sector_impact: Dict) -> str:
        """יצירת סיכום ניתוח המאקרו"""
        summary_parts = []
        
        # ניתוח כללי
        positive_trends = sum(1 for t in trends.values() if t.get("impact") == "positive")
        negative_trends = sum(1 for t in trends.values() if t.get("impact") == "negative")
        
        if positive_trends > negative_trends:
            summary_parts.append("מגמות מאקרו חיוביות")
        elif negative_trends > positive_trends:
            summary_parts.append("מגמות מאקרו שליליות")
        else:
            summary_parts.append("מגמות מאקרו מעורבות")
        
        # השפעה על סקטור
        sector = sector_impact.get("sector", "general")
        impact = sector_impact.get("overall_impact", "neutral")
        
        if impact == "positive":
            summary_parts.append(f"השפעה חיובית על סקטור {sector}")
        elif impact == "negative":
            summary_parts.append(f"השפעה שלילית על סקטור {sector}")
        else:
            summary_parts.append(f"השפעה ניטרלית על סקטור {sector}")
        
        # פרטים על מגמות חשובות
        important_trends = []
        for indicator, trend_data in trends.items():
            if trend_data.get("trend_strength") == "strong":
                direction = trend_data.get("trend_direction", "stable")
                important_trends.append(f"{indicator}: {direction}")
        
        if important_trends:
            summary_parts.append(f"מגמות חזקות: {', '.join(important_trends)}")
        
        return ". ".join(summary_parts)

    def _generate_recommendations(self, trends: Dict) -> List[str]:
        """יצירת המלצות על בסיס ניתוח המאקרו"""
        recommendations = []
        
        # ניתוח אינפלציה
        inflation_trend = trends.get("inflation", {})
        if inflation_trend.get("trend_direction") == "declining":
            recommendations.append("ירידת אינפלציה - סביבה חיובית לצמיחה")
        elif inflation_trend.get("trend_direction") == "improving":
            recommendations.append("עליית אינפלציה - סיכון לפעילות כלכלית")
        
        # ניתוח ריביות
        rates_trend = trends.get("interest_rates", {})
        if rates_trend.get("trend_direction") == "declining":
            recommendations.append("ירידת ריביות - תמיכה בשווקים")
        elif rates_trend.get("trend_direction") == "improving":
            recommendations.append("עליית ריביות - לחץ על שווקים")
        
        # ניתוח GDP
        gdp_trend = trends.get("gdp", {})
        if gdp_trend.get("trend_direction") == "improving":
            recommendations.append("צמיחת GDP - סביבה חיובית למניות")
        elif gdp_trend.get("trend_direction") == "declining":
            recommendations.append("האטת GDP - סיכון למניות")
        
        return recommendations

    # פונקציות עזר לשליפת נתונים (דמו)
    def _fetch_gdp_data(self) -> Dict:
        return {"current": 2.1, "previous": 1.9, "trend": "stable", "score": 60}
    
    def _fetch_inflation_data(self) -> Dict:
        return {"current": 3.2, "previous": 3.8, "trend": "declining", "score": 70}
    
    def _fetch_interest_rates(self) -> Dict:
        return {"current": 5.25, "previous": 5.50, "trend": "stable", "score": 50}
    
    def _fetch_pmi_data(self) -> Dict:
        return {"current": 52.1, "previous": 50.9, "trend": "improving", "score": 65}
    
    def _fetch_employment_data(self) -> Dict:
        return {"current": 3.7, "previous": 3.8, "trend": "improving", "score": 75}
    
    def _fetch_consumer_sentiment(self) -> Dict:
        return {"current": 68.2, "previous": 65.7, "trend": "improving", "score": 70} 