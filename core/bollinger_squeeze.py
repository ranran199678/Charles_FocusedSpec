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

try:
    from ta.volatility import BollingerBands
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    print("⚠️ ta library not available, using manual calculation")

class BollingerSqueeze(BaseAgent):
    """
    סוכן לזיהוי התכווצות בולינגר באנדס
    מזהה מצבים של התכווצות שעלולים להוביל לפריצה
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        self.window = cfg.get("window", 20)  # חלון לחישוב
        self.window_dev = cfg.get("window_dev", 2)  # סטיית תקן
        self.squeeze_threshold = cfg.get("squeeze_threshold", 0.75)  # סף התכווצות
        self.volume_weight = cfg.get("volume_weight", 0.3)  # משקל נפח
        self.price_weight = cfg.get("price_weight", 0.7)  # משקל מחיר
        self.log("Bollinger Squeeze Agent initialized")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        מנתח התכווצות בולינגר באנדס
        
        Args:
            symbol: סמל המניה
            price_df: DataFrame עם נתוני מחיר
            
        Returns:
            Dict עם תוצאות הניתוח
        """
        try:
            if price_df is None or price_df.empty:
                return self._get_dummy_result("אין נתוני מחיר זמינים")
            
            if len(price_df) < self.window:
                return self._get_dummy_result(f"לא מספיק נתונים (נדרש {self.window}, יש {len(price_df)})")
            
            # חישוב בולינגר באנדס
            bb_data = self._calculate_bollinger_bands(price_df)
            
            # ניתוח התכווצות
            squeeze_analysis = self._analyze_squeeze(bb_data)
            
            # חישוב ציון
            score = self._calculate_squeeze_score(squeeze_analysis)
            
            # ניתוח נפח
            volume_analysis = self._analyze_volume_pattern(price_df, bb_data)
            
            # יצירת סיכום
            summary = self._generate_squeeze_summary(squeeze_analysis, volume_analysis)
            
            # המלצות
            recommendations = self._generate_recommendations(squeeze_analysis, volume_analysis)
            
            return {
                "score": score,
                "explanation": summary,
                "details": {
                    "squeeze_analysis": squeeze_analysis,
                    "volume_analysis": volume_analysis,
                    "bb_data": bb_data,
                    "recommendations": recommendations
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log(f"שגיאה בניתוח התכווצות בולינגר: {str(e)}")
            return self._get_dummy_result(f"שגיאה: {str(e)}")

    def _calculate_bollinger_bands(self, price_df: pd.DataFrame) -> Dict:
        """חישוב בולינגר באנדס"""
        close = price_df["close"]
        
        if TA_AVAILABLE:
            # שימוש בספריית ta
            indicator = BollingerBands(close=close, window=self.window, window_dev=self.window_dev)
            bb_middle = indicator.bollinger_mavg()
            bb_upper = indicator.bollinger_hband()
            bb_lower = indicator.bollinger_lband()
        else:
            # חישוב ידני
            bb_middle = close.rolling(window=self.window).mean()
            bb_std = close.rolling(window=self.window).std()
            bb_upper = bb_middle + (bb_std * self.window_dev)
            bb_lower = bb_middle - (bb_std * self.window_dev)
        
        bb_width = bb_upper - bb_lower
        bb_percent = (close - bb_lower) / (bb_upper - bb_lower)
        
        return {
            "middle": bb_middle,
            "upper": bb_upper,
            "lower": bb_lower,
            "width": bb_width,
            "percent": bb_percent,
            "current_middle": bb_middle.iloc[-1],
            "current_upper": bb_upper.iloc[-1],
            "current_lower": bb_lower.iloc[-1],
            "current_width": bb_width.iloc[-1],
            "current_percent": bb_percent.iloc[-1],
            "current_price": close.iloc[-1]
        }

    def _analyze_squeeze(self, bb_data: Dict) -> Dict:
        """ניתוח התכווצות"""
        current_width = bb_data["current_width"]
        avg_width = bb_data["width"].rolling(window=self.window).mean().iloc[-1]
        
        # זיהוי התכווצות
        is_squeeze = current_width < avg_width * self.squeeze_threshold
        squeeze_ratio = current_width / avg_width if avg_width > 0 else 1
        
        # רמת התכווצות
        squeeze_level = self._get_squeeze_level(squeeze_ratio)
        
        # מיקום המחיר
        price_position = self._analyze_price_position(bb_data)
        
        return {
            "is_squeeze": is_squeeze,
            "squeeze_ratio": squeeze_ratio,
            "squeeze_level": squeeze_level,
            "current_width": current_width,
            "avg_width": avg_width,
            "price_position": price_position
        }

    def _get_squeeze_level(self, ratio: float) -> str:
        """קביעת רמת ההתכווצות"""
        if ratio < 0.5:
            return "התכווצות קיצונית"
        elif ratio < 0.75:
            return "התכווצות חזקה"
        elif ratio < 0.9:
            return "התכווצות בינונית"
        else:
            return "אין התכווצות"

    def _analyze_price_position(self, bb_data: Dict) -> str:
        """ניתוח מיקום המחיר"""
        current_price = bb_data["current_price"]
        current_upper = bb_data["current_upper"]
        current_lower = bb_data["current_lower"]
        current_middle = bb_data["current_middle"]
        
        if current_price > current_upper:
            return "מעל הפס העליון"
        elif current_price < current_lower:
            return "מתחת לפס התחתון"
        elif current_price > current_middle:
            return "בחצי העליון"
        else:
            return "בחצי התחתון"

    def _analyze_volume_pattern(self, price_df: pd.DataFrame, bb_data: Dict) -> Dict:
        """ניתוח דפוסי נפח"""
        if "volume" not in price_df.columns:
            return {}
        
        volume = price_df["volume"]
        avg_volume = volume.rolling(window=20).mean()
        current_volume = volume.iloc[-1]
        avg_volume_current = avg_volume.iloc[-1]
        
        volume_ratio = current_volume / avg_volume_current if avg_volume_current > 0 else 1
        
        # ניתוח מגמת נפח
        volume_trend = self._calculate_volume_trend(volume)
        
        return {
            "volume_ratio": volume_ratio,
            "volume_trend": volume_trend,
            "current_volume": current_volume,
            "avg_volume": avg_volume_current,
            "volume_signal": "גבוה" if volume_ratio > 1.5 else "בינוני" if volume_ratio > 1.2 else "נמוך"
        }

    def _calculate_volume_trend(self, volume: pd.Series) -> str:
        """חישוב מגמת נפח"""
        if len(volume) < 10:
            return "לא מספיק נתונים"
        
        recent_avg = volume.iloc[-5:].mean()
        previous_avg = volume.iloc[-10:-5].mean()
        
        change = (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0
        
        if change > 0.2:
            return "עולה"
        elif change < -0.2:
            return "יורד"
        else:
            return "יציב"

    def _calculate_squeeze_score(self, squeeze_analysis: Dict) -> int:
        """חישוב ציון התכווצות"""
        is_squeeze = squeeze_analysis["is_squeeze"]
        squeeze_ratio = squeeze_analysis["squeeze_ratio"]
        squeeze_level = squeeze_analysis["squeeze_level"]
        price_position = squeeze_analysis["price_position"]
        
        # ציון בסיס לפי התכווצות
        if not is_squeeze:
            base_score = 20
        else:
            base_score = {
                "התכווצות קיצונית": 90,
                "התכווצות חזקה": 75,
                "התכווצות בינונית": 60
            }.get(squeeze_level, 50)
        
        # התאמה לפי מיקום מחיר
        position_multiplier = {
            "מעל הפס העליון": 1.2,  # פריצה חיובית
            "מתחת לפס התחתון": 0.8,  # פריצה שלילית
            "בחצי העליון": 1.1,
            "בחצי התחתון": 0.9
        }.get(price_position, 1.0)
        
        # התאמה לפי יחס התכווצות
        ratio_multiplier = 1.0
        if is_squeeze:
            if squeeze_ratio < 0.6:
                ratio_multiplier = 1.1
            elif squeeze_ratio < 0.8:
                ratio_multiplier = 1.05
        
        final_score = int(base_score * position_multiplier * ratio_multiplier)
        return max(1, min(100, final_score))

    def _generate_squeeze_summary(self, squeeze_analysis: Dict, volume_analysis: Dict) -> str:
        """יצירת סיכום התכווצות"""
        is_squeeze = squeeze_analysis["is_squeeze"]
        squeeze_level = squeeze_analysis["squeeze_level"]
        price_position = squeeze_analysis["price_position"]
        current_width = squeeze_analysis["current_width"]
        avg_width = squeeze_analysis["avg_width"]
        
        summary = f"בולינגר באנדס: {squeeze_level}. "
        
        if is_squeeze:
            summary += f"זוהתה התכווצות (רוחב נוכחי: {current_width:.3f}, ממוצע: {avg_width:.3f}). "
        else:
            summary += f"אין התכווצות משמעותית (רוחב נוכחי: {current_width:.3f}, ממוצע: {avg_width:.3f}). "
        
        summary += f"מחיר ממוקם: {price_position}. "
        
        if volume_analysis:
            volume_signal = volume_analysis["volume_signal"]
            volume_trend = volume_analysis["volume_trend"]
            summary += f"נפח: {volume_signal}, מגמה: {volume_trend}."
        
        return summary

    def _generate_recommendations(self, squeeze_analysis: Dict, volume_analysis: Dict) -> List[str]:
        """יצירת המלצות"""
        recommendations = []
        
        is_squeeze = squeeze_analysis["is_squeeze"]
        squeeze_level = squeeze_analysis["squeeze_level"]
        price_position = squeeze_analysis["price_position"]
        
        if is_squeeze:
            if squeeze_level in ["התכווצות קיצונית", "התכווצות חזקה"]:
                recommendations.append("התכווצות חזקה - צפי לפריצה קרובה")
            
            if price_position == "מעל הפס העליון":
                recommendations.append("פריצה חיובית - סיגנל קנייה")
            elif price_position == "מתחת לפס התחתון":
                recommendations.append("פריצה שלילית - סיגנל מכירה")
            elif price_position == "בחצי העליון":
                recommendations.append("מחיר בחצי העליון - נטייה חיובית")
        
        if volume_analysis and volume_analysis.get("volume_signal") == "גבוה":
            recommendations.append("נפח גבוה - אישור לתנועה")
        
        if not recommendations:
            recommendations.append("שמור על עמדה נוכחית - אין סיגנלים חזקים")
        
        return recommendations

    def _get_dummy_result(self, message: str) -> Dict:
        """תוצאה ברירת מחדל"""
        return {
            "score": 1,
            "explanation": f"לא ניתן לנתח התכווצות בולינגר: {message}",
            "details": {},
            "timestamp": datetime.now().isoformat()
        }
