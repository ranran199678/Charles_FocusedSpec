import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.base_agent import BaseAgent
from utils.data_fetcher import DataFetcher

class MovingAveragePressureBot(BaseAgent):
    """
    סוכן לזיהוי לחץ ממוצעים נעים
    מנתח את הלחץ שמפעילים ממוצעים נעים שונים על המחיר
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        self.short_ma = cfg.get("short_ma", 10)  # ממוצע קצר
        self.medium_ma = cfg.get("medium_ma", 20)  # ממוצע בינוני
        self.long_ma = cfg.get("long_ma", 50)  # ממוצע ארוך
        self.pressure_threshold = cfg.get("pressure_threshold", 0.02)  # סף לחץ (2%)
        self.volume_weight = cfg.get("volume_weight", 0.3)  # משקל נפח
        self.price_weight = cfg.get("price_weight", 0.7)  # משקל מחיר
        self.log("Moving Average Pressure Bot initialized")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        מנתח לחץ ממוצעים נעים על המחיר
        
        Args:
            symbol: סמל המניה
            price_df: DataFrame עם נתוני מחיר
            
        Returns:
            Dict עם תוצאות הניתוח
        """
        try:
            if price_df is None or price_df.empty:
                return self._get_dummy_result("אין נתוני מחיר זמינים")
            
            # חישוב ממוצעים נעים
            ma_data = self._calculate_moving_averages(price_df)
            
            # ניתוח לחץ
            pressure_analysis = self._analyze_pressure(price_df, ma_data)
            
            # חישוב ציון
            score = self._calculate_pressure_score(pressure_analysis)
            
            # ניתוח מגמות
            trend_analysis = self._analyze_trends(ma_data)
            
            # יצירת סיכום
            summary = self._generate_pressure_summary(pressure_analysis, trend_analysis)
            
            # המלצות
            recommendations = self._generate_recommendations(pressure_analysis, trend_analysis)
            
            return {
                "score": score,
                "explanation": summary,
                "details": {
                    "pressure_analysis": pressure_analysis,
                    "trend_analysis": trend_analysis,
                    "ma_data": ma_data,
                    "recommendations": recommendations
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log(f"שגיאה בניתוח לחץ ממוצעים נעים: {str(e)}")
            return self._get_dummy_result(f"שגיאה: {str(e)}")

    def _calculate_moving_averages(self, price_df: pd.DataFrame) -> Dict:
        """חישוב ממוצעים נעים שונים"""
        close = price_df["Close"]
        
        return {
            "short_ma": close.rolling(self.short_ma).mean(),
            "medium_ma": close.rolling(self.medium_ma).mean(),
            "long_ma": close.rolling(self.long_ma).mean(),
            "current_price": close.iloc[-1],
            "short_ma_current": close.rolling(self.short_ma).mean().iloc[-1],
            "medium_ma_current": close.rolling(self.medium_ma).mean().iloc[-1],
            "long_ma_current": close.rolling(self.long_ma).mean().iloc[-1]
        }

    def _analyze_pressure(self, price_df: pd.DataFrame, ma_data: Dict) -> Dict:
        """ניתוח לחץ הממוצעים על המחיר"""
        current_price = ma_data["current_price"]
        short_ma = ma_data["short_ma_current"]
        medium_ma = ma_data["medium_ma_current"]
        long_ma = ma_data["long_ma_current"]
        
        # חישוב מרחקים מהממוצעים
        short_distance = abs(current_price - short_ma) / short_ma
        medium_distance = abs(current_price - medium_ma) / medium_ma
        long_distance = abs(current_price - long_ma) / long_ma
        
        # זיהוי סוג לחץ
        pressure_type = self._identify_pressure_type(current_price, short_ma, medium_ma, long_ma)
        
        # חישוב עוצמת לחץ
        pressure_strength = self._calculate_pressure_strength(short_distance, medium_distance, long_distance)
        
        # ניתוח נפח (אם זמין)
        volume_analysis = self._analyze_volume_pressure(price_df) if "Volume" in price_df.columns else {}
        
        return {
            "pressure_type": pressure_type,
            "pressure_strength": pressure_strength,
            "short_distance": short_distance,
            "medium_distance": medium_distance,
            "long_distance": long_distance,
            "current_price": current_price,
            "short_ma": short_ma,
            "medium_ma": medium_ma,
            "long_ma": long_ma,
            "volume_analysis": volume_analysis
        }

    def _identify_pressure_type(self, price: float, short_ma: float, medium_ma: float, long_ma: float) -> str:
        """זיהוי סוג הלחץ"""
        if price > short_ma > medium_ma > long_ma:
            return "לחץ תמיכה חזק (מחיר מעל כל הממוצעים)"
        elif price < short_ma < medium_ma < long_ma:
            return "לחץ התנגדות חזק (מחיר מתחת לכל הממוצעים)"
        elif price > short_ma and price < medium_ma:
            return "לחץ תמיכה בינוני (מחיר בין ממוצעים)"
        elif price < short_ma and price > medium_ma:
            return "לחץ התנגדות בינוני (מחיר בין ממוצעים)"
        elif abs(price - short_ma) < self.pressure_threshold:
            return "לחץ קרוב לממוצע קצר"
        else:
            return "לחץ מעורב"

    def _calculate_pressure_strength(self, short_dist: float, medium_dist: float, long_dist: float) -> str:
        """חישוב עוצמת הלחץ"""
        avg_distance = (short_dist + medium_dist + long_dist) / 3
        
        if avg_distance < 0.01:
            return "לחץ גבוה מאוד"
        elif avg_distance < 0.02:
            return "לחץ גבוה"
        elif avg_distance < 0.05:
            return "לחץ בינוני"
        else:
            return "לחץ נמוך"

    def _analyze_volume_pressure(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח לחץ נפח"""
        if "Volume" not in price_df.columns:
            return {}
        
        volume = price_df["Volume"]
        avg_volume = volume.rolling(20).mean()
        current_volume = volume.iloc[-1]
        avg_volume_current = avg_volume.iloc[-1]
        
        volume_ratio = current_volume / avg_volume_current if avg_volume_current > 0 else 1
        
        return {
            "volume_ratio": volume_ratio,
            "volume_pressure": "גבוה" if volume_ratio > 1.5 else "בינוני" if volume_ratio > 1.2 else "נמוך",
            "current_volume": current_volume,
            "avg_volume": avg_volume_current
        }

    def _analyze_trends(self, ma_data: Dict) -> Dict:
        """ניתוח מגמות הממוצעים"""
        short_ma = ma_data["short_ma"]
        medium_ma = ma_data["medium_ma"]
        long_ma = ma_data["long_ma"]
        
        # חישוב מגמות
        short_trend = self._calculate_trend(short_ma)
        medium_trend = self._calculate_trend(medium_ma)
        long_trend = self._calculate_trend(long_ma)
        
        # זיהוי צלבים
        golden_cross = short_ma.iloc[-1] > medium_ma.iloc[-1] and short_ma.iloc[-2] <= medium_ma.iloc[-2]
        death_cross = short_ma.iloc[-1] < medium_ma.iloc[-1] and short_ma.iloc[-2] >= medium_ma.iloc[-2]
        
        return {
            "short_trend": short_trend,
            "medium_trend": medium_trend,
            "long_trend": long_trend,
            "golden_cross": golden_cross,
            "death_cross": death_cross,
            "trend_alignment": self._check_trend_alignment(short_trend, medium_trend, long_trend)
        }

    def _calculate_trend(self, series: pd.Series) -> str:
        """חישוב מגמה של סדרה"""
        if len(series) < 5:
            return "לא מספיק נתונים"
        
        recent = series.iloc[-5:].mean()
        previous = series.iloc[-10:-5].mean()
        
        change = (recent - previous) / previous if previous != 0 else 0
        
        if change > 0.02:
            return "עולה"
        elif change < -0.02:
            return "יורד"
        else:
            return "יציב"

    def _check_trend_alignment(self, short_trend: str, medium_trend: str, long_trend: str) -> str:
        """בדיקת יישור מגמות"""
        if short_trend == medium_trend == long_trend:
            return "יישור מלא"
        elif short_trend == medium_trend:
            return "יישור קצר-בינוני"
        elif medium_trend == long_trend:
            return "יישור בינוני-ארוך"
        else:
            return "אין יישור"

    def _calculate_pressure_score(self, pressure_analysis: Dict) -> int:
        """חישוב ציון לחץ כולל"""
        pressure_type = pressure_analysis["pressure_type"]
        pressure_strength = pressure_analysis["pressure_strength"]
        
        # ציון בסיס לפי סוג לחץ
        base_score = {
            "לחץ תמיכה חזק": 80,
            "לחץ תמיכה בינוני": 60,
            "לחץ התנגדות חזק": 20,
            "לחץ התנגדות בינוני": 40,
            "לחץ קרוב לממוצע קצר": 50,
            "לחץ מעורב": 30
        }.get(pressure_type, 30)
        
        # התאמה לפי עוצמה
        strength_multiplier = {
            "לחץ גבוה מאוד": 1.2,
            "לחץ גבוה": 1.1,
            "לחץ בינוני": 1.0,
            "לחץ נמוך": 0.8
        }.get(pressure_strength, 1.0)
        
        # התאמה לפי נפח
        volume_multiplier = 1.0
        if "volume_analysis" in pressure_analysis and pressure_analysis["volume_analysis"]:
            volume_pressure = pressure_analysis["volume_analysis"]["volume_pressure"]
            volume_multiplier = {
                "גבוה": 1.1,
                "בינוני": 1.0,
                "נמוך": 0.9
            }.get(volume_pressure, 1.0)
        
        final_score = int(base_score * strength_multiplier * volume_multiplier)
        return max(1, min(100, final_score))

    def _generate_pressure_summary(self, pressure_analysis: Dict, trend_analysis: Dict) -> str:
        """יצירת סיכום לחץ"""
        pressure_type = pressure_analysis["pressure_type"]
        pressure_strength = pressure_analysis["pressure_strength"]
        current_price = pressure_analysis["current_price"]
        short_ma = pressure_analysis["short_ma"]
        
        summary = f"לחץ ממוצעים נעים: {pressure_type} ({pressure_strength}). "
        summary += f"מחיר נוכחי: {current_price:.2f}, ממוצע קצר: {short_ma:.2f}. "
        
        if trend_analysis["golden_cross"]:
            summary += "זוהה צלב מוזהב - סיגנל חיובי. "
        elif trend_analysis["death_cross"]:
            summary += "זוהה צלב מוות - סיגנל שלילי. "
        
        summary += f"מגמה קצרה: {trend_analysis['short_trend']}, מגמה בינונית: {trend_analysis['medium_trend']}."
        
        return summary

    def _generate_recommendations(self, pressure_analysis: Dict, trend_analysis: Dict) -> List[str]:
        """יצירת המלצות"""
        recommendations = []
        
        pressure_type = pressure_analysis["pressure_type"]
        pressure_strength = pressure_analysis["pressure_strength"]
        
        if "תמיכה" in pressure_type and pressure_strength in ["לחץ גבוה מאוד", "לחץ גבוה"]:
            recommendations.append("שקול רכישה - לחץ תמיכה חזק")
        
        if "התנגדות" in pressure_type and pressure_strength in ["לחץ גבוה מאוד", "לחץ גבוה"]:
            recommendations.append("היזהר - לחץ התנגדות חזק")
        
        if trend_analysis["golden_cross"]:
            recommendations.append("צלב מוזהב - סיגנל חיובי לקנייה")
        
        if trend_analysis["death_cross"]:
            recommendations.append("צלב מוות - סיגנל שלילי למכירה")
        
        if trend_analysis["trend_alignment"] == "יישור מלא":
            recommendations.append("יישור מגמות - סיגנל חזק")
        
        if not recommendations:
            recommendations.append("שמור על עמדה נוכחית - לחץ מאוזן")
        
        return recommendations

    def _get_dummy_result(self, message: str) -> Dict:
        """תוצאה ברירת מחדל"""
        return {
            "score": 1,
            "explanation": f"לא ניתן לנתח לחץ ממוצעים נעים: {message}",
            "details": {},
            "timestamp": datetime.now().isoformat()
        }
