"""
Multi Agent Validator - ולידטור חוצה-סוכנים
============================================

סוכן שמוודא עקביות בין האותות של כל הסוכנים השונים
ומזהה סתירות או סיכונים שעלולים להשפיע על איכות ההחלטות.
"""

from utils.logger import get_agent_logger
from typing import Dict, List, Any, Optional
import logging

class MultiAgentValidator:
    """
    ולידטור חוצה-סוכנים לזיהוי סתירות וסיכונים
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        אתחול מודול ולידציה חוצה-סוכנים
        
        Args:
            config: מילון הגדרות (אופציונלי)
        """
        self.config = config or {}
        self.logger = get_agent_logger("multi_agent_validator")
        
        # הגדרת קבוצות אותות
        self.technical_signals = [
            "RSI_compression", "Volume_tension", "Breakout_retest", 
            "Support_zone_strength", "MA_pressure", "Bullish_pattern"
        ]
        
        self.sentiment_signals = [
            "Sentiment", "Social_hype", "News_catalyst", "Analyst_rating"
        ]
        
        self.fundamental_signals = [
            "Consistent_growth", "Valuation_anomaly", "Financial_stability",
            "Earnings_surprise", "Insider_activity"
        ]
        
        self.risk_signals = [
            "Geo_risk", "Parabolic_move", "Overbought", "Oversold"
        ]
        
        # פרמטרים ברירת מחדל
        self.min_technical_consistency = self.config.get("min_technical_consistency", 0.7)
        self.conflict_threshold = self.config.get("conflict_threshold", 2)
        self.risk_tolerance = self.config.get("risk_tolerance", 0.3)
        
        self.logger.info("Multi Agent Validator initialized successfully")

    def detect_conflicts(self, signals: Dict[str, Any]) -> List[str]:
        """
        בדיקת סתירות בין אותות הסוכנים
        
        Args:
            signals: מילון אותות {שם_סוכן: Boolean}
            
        Returns:
            רשימת סתירות שנמצאו (ריקה אם אין סתירות)
        """
        try:
            if not isinstance(signals, dict):
                self.logger.warning("Invalid signals format provided")
                return ["Invalid signals format"]
            
            conflicts = []
            
            # בדיקת סתירות טכניות
            technical_conflicts = self._detect_technical_conflicts(signals)
            conflicts.extend(technical_conflicts)
            
            # בדיקת סתירות סנטימנט
            sentiment_conflicts = self._detect_sentiment_conflicts(signals)
            conflicts.extend(sentiment_conflicts)
            
            # בדיקת סתירות יסודיות
            fundamental_conflicts = self._detect_fundamental_conflicts(signals)
            conflicts.extend(fundamental_conflicts)
            
            # בדיקת סיכונים
            risk_conflicts = self._detect_risk_conflicts(signals)
            conflicts.extend(risk_conflicts)
            
            # בדיקת סתירות כלליות
            general_conflicts = self._detect_general_conflicts(signals)
            conflicts.extend(general_conflicts)
            
            if conflicts:
                self.logger.warning(f"Detected {len(conflicts)} conflicts: {conflicts}")
            else:
                self.logger.debug("No conflicts detected")
            
            return conflicts
            
        except Exception as e:
            self.logger.error(f"Error detecting conflicts: {str(e)}")
            return ["Error in conflict detection"]

    def _detect_technical_conflicts(self, signals: Dict[str, Any]) -> List[str]:
        """
        זיהוי סתירות טכניות
        
        Args:
            signals: מילון האותות
            
        Returns:
            רשימת סתירות טכניות
        """
        conflicts = []
        
        try:
            # ספירת אותות טכניים חיוביים
            positive_technicals = sum(1 for sig in self.technical_signals if signals.get(sig))
            
            # סתירה 1: אותות טכניים חזקים ללא סנטימנט חיובי
            if positive_technicals >= 3 and not signals.get("Sentiment"):
                conflicts.append("Strong technical signals without positive sentiment")
            
            # סתירה 2: תנועה פרבולית עם אותות טכניים חיוביים אחרים
            if signals.get("Parabolic_move") and positive_technicals >= 2:
                conflicts.append("Parabolic move with other positive technical signals")
            
            # סתירה 3: RSI דחוס עם נפח נמוך
            if signals.get("RSI_compression") and not signals.get("Volume_tension"):
                conflicts.append("RSI compression without volume tension")
            
            # סתירה 4: פריצה ללא אימות
            if signals.get("Breakout_retest") and not signals.get("Support_zone_strength"):
                conflicts.append("Breakout without strong support zone")
            
        except Exception as e:
            self.logger.error(f"Error in technical conflict detection: {str(e)}")
        
        return conflicts

    def _detect_sentiment_conflicts(self, signals: Dict[str, Any]) -> List[str]:
        """
        זיהוי סתירות סנטימנט
        
        Args:
            signals: מילון האותות
            
        Returns:
            רשימת סתירות סנטימנט
        """
        conflicts = []
        
        try:
            # ספירת אותות סנטימנט חיוביים
            positive_sentiment = sum(1 for sig in self.sentiment_signals if signals.get(sig))
            
            # סתירה 1: הייפ חברתי גבוה ללא יסודות תומכים
            if (signals.get("Social_hype") and 
                not signals.get("Consistent_growth") and 
                not signals.get("Valuation_anomaly")):
                conflicts.append("High social hype without fundamental support")
            
            # סתירה 2: חדשות חיוביות ללא תגובה טכנית
            if signals.get("News_catalyst") and not signals.get("Volume_tension"):
                conflicts.append("Positive news without technical response")
            
            # סתירה 3: דירוג אנליסטים חיובי ללא צמיחה עקבית
            if signals.get("Analyst_rating") and not signals.get("Consistent_growth"):
                conflicts.append("Positive analyst rating without consistent growth")
            
        except Exception as e:
            self.logger.error(f"Error in sentiment conflict detection: {str(e)}")
        
        return conflicts

    def _detect_fundamental_conflicts(self, signals: Dict[str, Any]) -> List[str]:
        """
        זיהוי סתירות יסודיות
        
        Args:
            signals: מילון האותות
            
        Returns:
            רשימת סתירות יסודיות
        """
        conflicts = []
        
        try:
            # סתירה 1: צמיחה עקבית ללא יציבות פיננסית
            if signals.get("Consistent_growth") and not signals.get("Financial_stability"):
                conflicts.append("Consistent growth without financial stability")
            
            # סתירה 2: הפתעת רווחים ללא פעילות פנימית
            if signals.get("Earnings_surprise") and not signals.get("Insider_activity"):
                conflicts.append("Earnings surprise without insider activity")
            
            # סתירה 3: אנומליית הערכה ללא צמיחה
            if signals.get("Valuation_anomaly") and not signals.get("Consistent_growth"):
                conflicts.append("Valuation anomaly without growth")
            
        except Exception as e:
            self.logger.error(f"Error in fundamental conflict detection: {str(e)}")
        
        return conflicts

    def _detect_risk_conflicts(self, signals: Dict[str, Any]) -> List[str]:
        """
        זיהוי סתירות סיכון
        
        Args:
            signals: מילון האותות
            
        Returns:
            רשימת סתירות סיכון
        """
        conflicts = []
        
        try:
            # סתירה 1: סיכון גיאופוליטי עם אותות חיוביים
            if signals.get("Geo_risk"):
                positive_count = sum(1 for sig in self.technical_signals + self.sentiment_signals 
                                   if signals.get(sig))
                if positive_count >= 2:
                    conflicts.append("Geopolitical risk with positive signals")
            
            # סתירה 2: תנועה פרבולית עם דחיסת RSI
            if signals.get("Parabolic_move") and signals.get("RSI_compression"):
                conflicts.append("Parabolic move with RSI compression")
            
            # סתירה 3: מצב קנייה יתר עם אותות חיוביים
            if signals.get("Overbought") and sum(1 for sig in self.technical_signals 
                                                if signals.get(sig)) >= 2:
                conflicts.append("Overbought condition with positive technical signals")
            
        except Exception as e:
            self.logger.error(f"Error in risk conflict detection: {str(e)}")
        
        return conflicts

    def _detect_general_conflicts(self, signals: Dict[str, Any]) -> List[str]:
        """
        זיהוי סתירות כלליות
        
        Args:
            signals: מילון האותות
            
        Returns:
            רשימת סתירות כלליות
        """
        conflicts = []
        
        try:
            # ספירת אותות חיוביים בכל הקטגוריות
            technical_positive = sum(1 for sig in self.technical_signals if signals.get(sig))
            sentiment_positive = sum(1 for sig in self.sentiment_signals if signals.get(sig))
            fundamental_positive = sum(1 for sig in self.fundamental_signals if signals.get(sig))
            
            # סתירה 1: אותות טכניים חזקים ללא תמיכה יסודית
            if technical_positive >= 3 and fundamental_positive == 0:
                conflicts.append("Strong technical signals without fundamental support")
            
            # סתירה 2: אותות סנטימנט חזקים ללא תמיכה טכנית
            if sentiment_positive >= 2 and technical_positive == 0:
                conflicts.append("Strong sentiment signals without technical support")
            
            # סתירה 3: אותות יסודיים חזקים ללא תמיכה טכנית או סנטימנט
            if fundamental_positive >= 2 and technical_positive == 0 and sentiment_positive == 0:
                conflicts.append("Strong fundamental signals without technical or sentiment support")
            
        except Exception as e:
            self.logger.error(f"Error in general conflict detection: {str(e)}")
        
        return conflicts

    def calculate_signal_consistency(self, signals: Dict[str, Any]) -> float:
        """
        חישוב עקביות האותות
        
        Args:
            signals: מילון האותות
            
        Returns:
            ציון עקביות (0-1)
        """
        try:
            if not signals:
                return 0.0
            
            # חישוב עקביות לכל קטגוריה
            technical_consistency = self._calculate_category_consistency(signals, self.technical_signals)
            sentiment_consistency = self._calculate_category_consistency(signals, self.sentiment_signals)
            fundamental_consistency = self._calculate_category_consistency(signals, self.fundamental_signals)
            
            # ממוצע משוקלל
            total_consistency = (technical_consistency * 0.4 + 
                               sentiment_consistency * 0.3 + 
                               fundamental_consistency * 0.3)
            
            return total_consistency
            
        except Exception as e:
            self.logger.error(f"Error calculating signal consistency: {str(e)}")
            return 0.0

    def _calculate_category_consistency(self, signals: Dict[str, Any], category_signals: List[str]) -> float:
        """
        חישוב עקביות בתוך קטגוריה
        
        Args:
            signals: מילון האותות
            category_signals: רשימת אותות בקטגוריה
            
        Returns:
            ציון עקביות (0-1)
        """
        try:
            available_signals = [sig for sig in category_signals if sig in signals]
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
            self.logger.error(f"Error calculating category consistency: {str(e)}")
            return 0.0

    def assess_overall_risk(self, signals: Dict[str, Any]) -> str:
        """
        הערכת סיכון כללי
        
        Args:
            signals: מילון האותות
            
        Returns:
            רמת סיכון: "LOW", "MEDIUM", "HIGH"
        """
        try:
            risk_score = 0
            
            # חישוב ציון סיכון
            if signals.get("Geo_risk"):
                risk_score += 3
            
            if signals.get("Parabolic_move"):
                risk_score += 2
            
            if signals.get("Overbought"):
                risk_score += 1
            
            if signals.get("Oversold"):
                risk_score += 1
            
            # קביעת רמת סיכון
            if risk_score >= 4:
                return "HIGH"
            elif risk_score >= 2:
                return "MEDIUM"
            else:
                return "LOW"
                
        except Exception as e:
            self.logger.error(f"Error assessing overall risk: {str(e)}")
            return "MEDIUM"
