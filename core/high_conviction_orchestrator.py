"""
High Conviction Orchestrator - אורקסטרטור לאיתותים בעלי ביטחון גבוה
====================================================================

סוכן שמחליט איזה איתותים נחשבים בעלי ביטחון גבוה (High Conviction)
על בסיס ניתוח מקיף של כל הסוכנים ואיתור סתירות.
"""

from core.multi_agent_validator import MultiAgentValidator
from utils.logger import get_agent_logger
from utils.validators import validate_symbol
from typing import Dict, Any, Optional
import logging

class HighConvictionOrchestrator:
    """
    אורקסטרטור לאיתותים בעלי ביטחון גבוה
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        אתחול האורקסטרטור
        
        Args:
            config: מילון הגדרות (אופציונלי)
        """
        self.config = config or {}
        self.validator = MultiAgentValidator(config)
        self.logger = get_agent_logger("high_conviction_orchestrator")
        
        # פרמטרים ברירת מחדל
        self.min_score_threshold = self.config.get("min_score_threshold", 4)
        self.min_technical_signals = self.config.get("min_technical_signals", 3)
        self.conflict_tolerance = self.config.get("conflict_tolerance", 0)
        
        self.logger.info("High Conviction Orchestrator initialized successfully")

    def decide(self, analysis_result: Dict[str, Any]) -> bool:
        """
        קבלת החלטה לגבי Conviction גבוה
        
        Args:
            analysis_result: מילון התוצאה ממנוע הניקוד
                           (המכיל "score", "signals", "recommendation")
        
        Returns:
            True אם האיתות נחשב בעל ביטחון גבוה, False אם לא
        """
        try:
            # אימות קלט
            if not self._validate_analysis_result(analysis_result):
                self.logger.warning("Invalid analysis result provided")
                return False
            
            score = analysis_result.get("score", 0)
            signals = analysis_result.get("signals", {})
            recommendation = analysis_result.get("recommendation", "")
            
            self.logger.debug(f"Analyzing conviction for score: {score}, recommendation: {recommendation}")
            
            # בדיקה ראשונית - ציון גבוה והמלצה HIGH
            high_score_flag = (score >= self.min_score_threshold and "HIGH" in recommendation.upper())
            if not high_score_flag:
                self.logger.debug("Score or recommendation does not meet high conviction criteria")
                return False
            
            # בדיקת סתירות
            conflicts = self.validator.detect_conflicts(signals)
            if conflicts:
                self.logger.warning(f"Conflicts detected: {conflicts}")
                return False
            
            # בדיקת סיכונים גיאופוליטיים
            if signals.get("Geo_risk"):
                self.logger.warning("Geopolitical risk detected - rejecting high conviction")
                return False
            
            # בדיקת איכות אותות טכניים
            technical_quality = self._assess_technical_quality(signals)
            if not technical_quality:
                self.logger.debug("Technical signals quality insufficient for high conviction")
                return False
            
            self.logger.info("High conviction criteria met successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in conviction decision: {str(e)}")
            return False

    def _validate_analysis_result(self, analysis_result: Dict[str, Any]) -> bool:
        """
        אימות תקינות תוצאת הניתוח
        
        Args:
            analysis_result: תוצאת הניתוח לאימות
            
        Returns:
            True אם תקין, False אחרת
        """
        if not isinstance(analysis_result, dict):
            return False
        
        required_keys = ["score", "signals", "recommendation"]
        for key in required_keys:
            if key not in analysis_result:
                return False
        
        # אימות טיפוסי נתונים
        if not isinstance(analysis_result.get("score"), (int, float)):
            return False
        
        if not isinstance(analysis_result.get("signals"), dict):
            return False
        
        if not isinstance(analysis_result.get("recommendation"), str):
            return False
        
        return True

    def _assess_technical_quality(self, signals: Dict[str, Any]) -> bool:
        """
        הערכת איכות האותות הטכניים
        
        Args:
            signals: מילון האותות
            
        Returns:
            True אם האיכות מספקת, False אחרת
        """
        technical_signals = [
            "RSI_compression", "Volume_tension", "Breakout_retest", 
            "Support_zone_strength", "MA_pressure", "Bullish_pattern"
        ]
        
        positive_technicals = sum(1 for sig in technical_signals if signals.get(sig))
        
        # דרישה למינימום אותות טכניים חיוביים
        if positive_technicals < self.min_technical_signals:
            return False
        
        # בדיקת עקביות בין האותות
        consistency_score = self._calculate_consistency_score(signals)
        if consistency_score < 0.7:  # דרישה לעקביות של לפחות 70%
            return False
        
        return True

    def _calculate_consistency_score(self, signals: Dict[str, Any]) -> float:
        """
        חישוב ציון עקביות בין האותות
        
        Args:
            signals: מילון האותות
            
        Returns:
            ציון עקביות (0-1)
        """
        try:
            # קבוצות אותות לפי קטגוריות
            technical_group = ["RSI_compression", "Volume_tension", "Breakout_retest", 
                             "Support_zone_strength", "MA_pressure", "Bullish_pattern"]
            
            sentiment_group = ["Sentiment", "Social_hype", "News_catalyst"]
            
            fundamental_group = ["Consistent_growth", "Valuation_anomaly", "Financial_stability"]
            
            # חישוב עקביות בתוך כל קבוצה
            technical_consistency = self._calculate_group_consistency(signals, technical_group)
            sentiment_consistency = self._calculate_group_consistency(signals, sentiment_group)
            fundamental_consistency = self._calculate_group_consistency(signals, fundamental_group)
            
            # ממוצע משוקלל
            total_consistency = (technical_consistency * 0.5 + 
                               sentiment_consistency * 0.3 + 
                               fundamental_consistency * 0.2)
            
            return total_consistency
            
        except Exception as e:
            self.logger.error(f"Error calculating consistency score: {str(e)}")
            return 0.0

    def _calculate_group_consistency(self, signals: Dict[str, Any], group_signals: list) -> float:
        """
        חישוב עקביות בתוך קבוצת אותות
        
        Args:
            signals: מילון האותות
            group_signals: רשימת אותות בקבוצה
            
        Returns:
            ציון עקביות (0-1)
        """
        try:
            available_signals = [sig for sig in group_signals if sig in signals]
            if not available_signals:
                return 0.0
            
            positive_count = sum(1 for sig in available_signals if signals.get(sig))
            total_count = len(available_signals)
            
            # אם רוב האותות חיוביים או שליליים - עקביות גבוהה
            if positive_count == 0 or positive_count == total_count:
                return 1.0
            
            # אחרת - עקביות נמוכה יותר
            return 1.0 - (abs(positive_count - total_count/2) / (total_count/2))
            
        except Exception as e:
            self.logger.error(f"Error calculating group consistency: {str(e)}")
            return 0.0

    def get_conviction_level(self, analysis_result: Dict[str, Any]) -> str:
        """
        קבלת רמת הביטחון של האיתות
        
        Args:
            analysis_result: תוצאת הניתוח
            
        Returns:
            רמת הביטחון: "HIGH", "MEDIUM", "LOW"
        """
        try:
            if self.decide(analysis_result):
                return "HIGH"
            
            score = analysis_result.get("score", 0)
            if score >= 3:
                return "MEDIUM"
            else:
                return "LOW"
                
        except Exception as e:
            self.logger.error(f"Error getting conviction level: {str(e)}")
            return "LOW"
