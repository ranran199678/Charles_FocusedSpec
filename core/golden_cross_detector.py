import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.base.base_agent import BaseAgent
import logging
from typing import Dict, List

class GoldenCrossDetector(BaseAgent):
    """
    סוכן לזיהוי צלבים מוזהבים (Golden Cross) וצלבי מוות (Death Cross)
    מזהה חציות של ממוצעים נעים קצרים וארוכים ומנתח את משמעותן
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        self.short_window = cfg.get("short_window", 50)
        self.long_window = cfg.get("long_window", 200)
        self.freshness_days = cfg.get("freshness_days", 7)
        self.volume_weight = cfg.get("volume_weight", 0.3)
        self.price_weight = cfg.get("price_weight", 0.7)
        self.min_gap_threshold = cfg.get("min_gap_threshold", 0.5)  # אחוז מינימלי לפער משמעותי
        self.log("Golden Cross Agent initialized")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        מנתח צלבים מוזהבים וצלבי מוות במניה
        """
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=365)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            if len(price_df) < self.long_window:
                return self.fallback()
            
            # חישוב ממוצעים נעים
            ma_data = self._calculate_moving_averages(price_df)
            
            # זיהוי צלבים
            cross_analysis = self._detect_crosses(price_df, ma_data)
            
            # ניתוח נפח
            volume_analysis = self._analyze_volume_pattern(price_df, cross_analysis)
            
            # חישוב ציון
            score = self._calculate_cross_score(cross_analysis, volume_analysis)
            
            # יצירת סיכום
            summary = self._generate_cross_summary(cross_analysis, volume_analysis)
            
            # המלצות
            recommendations = self._generate_recommendations(cross_analysis, volume_analysis)
            
            return {
                "score": score,
                "explanation": summary,
                "details": {
                    "cross_analysis": cross_analysis,
                    "volume_analysis": volume_analysis,
                    "ma_data": ma_data,
                    "recommendations": recommendations
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()

    def _calculate_moving_averages(self, price_df: pd.DataFrame) -> Dict:
        """חישוב ממוצעים נעים קצרים וארוכים"""
        close = price_df["close"]
        
        return {
            "short_ma": close.rolling(self.short_window).mean(),
            "long_ma": close.rolling(self.long_window).mean(),
            "current_price": close.iloc[-1],
            "short_ma_current": close.rolling(self.short_window).mean().iloc[-1],
            "long_ma_current": close.rolling(self.long_window).mean().iloc[-1],
            "short_ma_prev": close.rolling(self.short_window).mean().iloc[-2] if len(close) > 1 else None,
            "long_ma_prev": close.rolling(self.long_window).mean().iloc[-2] if len(close) > 1 else None
        }

    def _detect_crosses(self, price_df: pd.DataFrame, ma_data: Dict) -> Dict:
        """זיהוי צלבים מוזהבים וצלבי מוות"""
        short_ma = ma_data["short_ma"]
        long_ma = ma_data["long_ma"]
        
        # זיהוי חציות
        golden_cross = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
        death_cross = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
        
        # מציאת אינדקסים של צלבים
        golden_cross_idx = price_df.index[golden_cross].tolist()
        death_cross_idx = price_df.index[death_cross].tolist()
        
        # ניתוח הצלב האחרון
        last_golden_cross = None
        last_death_cross = None
        
        if golden_cross_idx:
            last_golden_cross = self._analyze_cross_event(price_df, golden_cross_idx[-1], "golden")
        
        if death_cross_idx:
            last_death_cross = self._analyze_cross_event(price_df, death_cross_idx[-1], "death")
        
        # ניתוח מצב נוכחי
        current_position = self._analyze_current_position(ma_data)
        
        return {
            "golden_crosses": golden_cross_idx,
            "death_crosses": death_cross_idx,
            "last_golden_cross": last_golden_cross,
            "last_death_cross": last_death_cross,
            "current_position": current_position,
            "total_golden_crosses": len(golden_cross_idx),
            "total_death_crosses": len(death_cross_idx)
        }

    def _analyze_cross_event(self, price_df: pd.DataFrame, cross_idx, cross_type: str) -> Dict:
        """ניתוח אירוע צלב ספציפי"""
        days_since_cross = (price_df.index[-1] - cross_idx).days if hasattr(price_df.index[-1], "days") else len(price_df) - price_df.index.get_loc(cross_idx) - 1
        
        # חישוב פער בחצייה
        try:
            short_val = price_df.loc[cross_idx, "close"]
            long_val = price_df.loc[cross_idx:].iloc[0]["close"]  # ערך הממוצע הארוך
            gap = abs(short_val - long_val) / long_val * 100
        except:
            gap = 0
        
        # ניתוח טריות
        if days_since_cross <= self.freshness_days:
            freshness_score = 100
            freshness_level = "טרי מאוד"
        elif days_since_cross <= self.freshness_days * 2:
            freshness_score = 80
            freshness_level = "טרי"
        elif days_since_cross <= self.freshness_days * 4:
            freshness_score = 60
            freshness_level = "בינוני"
        else:
            freshness_score = 30
            freshness_level = "ישן"
        
        return {
            "date": cross_idx,
            "days_since": days_since_cross,
            "freshness_score": freshness_score,
            "freshness_level": freshness_level,
            "gap_percentage": gap,
            "cross_type": cross_type,
            "price_at_cross": price_df.loc[cross_idx, "close"]
        }

    def _analyze_current_position(self, ma_data: Dict) -> Dict:
        """ניתוח המיקום הנוכחי של המחיר ביחס לממוצעים"""
        current_price = ma_data["current_price"]
        short_ma = ma_data["short_ma_current"]
        long_ma = ma_data["long_ma_current"]
        
        # חישוב פערים
        short_gap = ((current_price - short_ma) / short_ma) * 100
        long_gap = ((current_price - long_ma) / long_ma) * 100
        ma_gap = ((short_ma - long_ma) / long_ma) * 100
        
        # זיהוי מצב
        if short_ma > long_ma:
            if current_price > short_ma:
                position = "מעל שני הממוצעים (בולשי חזק)"
                strength = "חזק"
            elif current_price > long_ma:
                position = "בין הממוצעים (בולשי בינוני)"
                strength = "בינוני"
            else:
                position = "מתחת לממוצע הארוך (שלילי)"
                strength = "חלש"
        else:
            if current_price < short_ma:
                position = "מתחת לשני הממוצעים (שלילי חזק)"
                strength = "חזק"
            elif current_price < long_ma:
                position = "בין הממוצעים (שלילי בינוני)"
                strength = "בינוני"
            else:
                position = "מעל הממוצע הארוך (חיובי)"
                strength = "חלש"
        
        return {
            "position": position,
            "strength": strength,
            "short_gap_percent": short_gap,
            "long_gap_percent": long_gap,
            "ma_gap_percent": ma_gap,
            "current_price": current_price,
            "short_ma": short_ma,
            "long_ma": long_ma
        }

    def _analyze_volume_pattern(self, price_df: pd.DataFrame, cross_analysis: Dict) -> Dict:
        """ניתוח דפוסי נפח סביב צלבים"""
        volume = price_df["volume"]
        
        # ניתוח נפח נוכחי
        current_volume = volume.iloc[-1]
        avg_volume = volume.rolling(20).mean().iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # זיהוי סיגנל נפח
        if volume_ratio > 2:
            volume_signal = "גבוה מאוד"
            volume_score = 100
        elif volume_ratio > 1.5:
            volume_signal = "גבוה"
            volume_score = 80
        elif volume_ratio > 1.2:
            volume_signal = "בינוני-גבוה"
            volume_score = 60
        elif volume_ratio > 0.8:
            volume_signal = "נורמלי"
            volume_score = 40
        else:
            volume_signal = "נמוך"
            volume_score = 20
        
        # מגמת נפח
        recent_volume_trend = volume.tail(5).mean() / volume.tail(20).mean()
        if recent_volume_trend > 1.2:
            volume_trend = "עולה"
        elif recent_volume_trend < 0.8:
            volume_trend = "יורד"
        else:
            volume_trend = "יציב"
        
        return {
            "current_volume": current_volume,
            "avg_volume": avg_volume,
            "volume_ratio": volume_ratio,
            "volume_signal": volume_signal,
            "volume_score": volume_score,
            "volume_trend": volume_trend,
            "recent_volume_trend": recent_volume_trend
        }

    def _calculate_cross_score(self, cross_analysis: Dict, volume_analysis: Dict) -> int:
        """חישוב ציון כולל על בסיס צלבים ונפח"""
        base_score = 50  # ציון בסיס
        
        # ניתוח צלב אחרון
        last_golden = cross_analysis.get("last_golden_cross")
        last_death = cross_analysis.get("last_death_cross")
        
        if last_golden and last_death:
            # יש שני צלבים - נבדוק איזה יותר טרי
            if last_golden["days_since"] < last_death["days_since"]:
                cross_score = last_golden["freshness_score"]
                cross_type = "golden"
            else:
                cross_score = 100 - last_death["freshness_score"]  # היפוך לצלב מוות
                cross_type = "death"
        elif last_golden:
            cross_score = last_golden["freshness_score"]
            cross_type = "golden"
        elif last_death:
            cross_score = 100 - last_death["freshness_score"]  # היפוך לצלב מוות
            cross_type = "death"
        else:
            # אין צלבים - נבדוק מיקום נוכחי
            current_pos = cross_analysis["current_position"]
            if "בולשי" in current_pos["position"]:
                cross_score = 60
                cross_type = "position_bullish"
            elif "שלילי" in current_pos["position"]:
                cross_score = 30
                cross_type = "position_bearish"
            else:
                cross_score = 45
                cross_type = "neutral"
        
        # ניתוח נפח
        volume_score = volume_analysis["volume_score"]
        
        # חישוב סופי
        final_score = int(
            (cross_score * self.price_weight) + 
            (volume_score * self.volume_weight)
        )
        
        return max(1, min(100, final_score))

    def _generate_cross_summary(self, cross_analysis: Dict, volume_analysis: Dict) -> str:
        """יצירת סיכום טקסטואלי של הניתוח"""
        current_pos = cross_analysis["current_position"]
        last_golden = cross_analysis.get("last_golden_cross")
        last_death = cross_analysis.get("last_death_cross")
        
        summary_parts = []
        
        # מיקום נוכחי
        summary_parts.append(f"מיקום נוכחי: {current_pos['position']}")
        
        # צלב אחרון
        if last_golden and last_death:
            if last_golden["days_since"] < last_death["days_since"]:
                summary_parts.append(f"צלב מוזהב {last_golden['freshness_level']} ({last_golden['days_since']} ימים)")
            else:
                summary_parts.append(f"צלב מוות {last_death['freshness_level']} ({last_death['days_since']} ימים)")
        elif last_golden:
            summary_parts.append(f"צלב מוזהב {last_golden['freshness_level']} ({last_golden['days_since']} ימים)")
        elif last_death:
            summary_parts.append(f"צלב מוות {last_death['freshness_level']} ({last_death['days_since']} ימים)")
        else:
            summary_parts.append("אין צלבים אחרונים")
        
        # נפח
        summary_parts.append(f"נפח: {volume_analysis['volume_signal']}, מגמה: {volume_analysis['volume_trend']}")
        
        # פערים
        summary_parts.append(f"פער ממוצעים: {current_pos['ma_gap_percent']:.1f}%")
        
        return ". ".join(summary_parts)

    def _generate_recommendations(self, cross_analysis: Dict, volume_analysis: Dict) -> List[str]:
        """יצירת המלצות על בסיס הניתוח"""
        recommendations = []
        current_pos = cross_analysis["current_position"]
        last_golden = cross_analysis.get("last_golden_cross")
        last_death = cross_analysis.get("last_death_cross")
        
        # המלצות על בסיס צלבים
        if last_golden and last_golden["days_since"] <= self.freshness_days:
            recommendations.append("צלב מוזהב טרי - סיגנל קנייה חזק")
        elif last_death and last_death["days_since"] <= self.freshness_days:
            recommendations.append("צלב מוות טרי - סיגנל מכירה חזק")
        
        # המלצות על בסיס מיקום
        if "בולשי חזק" in current_pos["position"]:
            recommendations.append("מחיר מעל שני הממוצעים - המשך עלייה צפוי")
        elif "שלילי חזק" in current_pos["position"]:
            recommendations.append("מחיר מתחת לשני הממוצעים - המשך ירידה צפוי")
        
        # המלצות על בסיס נפח
        if volume_analysis["volume_ratio"] > 1.5:
            recommendations.append("נפח גבוה - אישור למגמה")
        elif volume_analysis["volume_ratio"] < 0.8:
            recommendations.append("נפח נמוך - חולשה במגמה")
        
        # המלצות על בסיס פער ממוצעים
        if abs(current_pos["ma_gap_percent"]) > 5:
            if current_pos["ma_gap_percent"] > 0:
                recommendations.append("פער ממוצעים גדול - פוטנציאל לתיקון")
            else:
                recommendations.append("פער ממוצעים שלילי גדול - פוטנציאל לקנייה")
        
        if not recommendations:
            recommendations.append("שמור על עמדה נוכחית - אין סיגנלים חזקים")
        
        return recommendations
