"""
בדיקות עבור Multi Agent Validator
מבצע בדיקות יחידה לסוכן שמאמת תוצאות של סוכנים מרובים
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.multi_agent_validator import MultiAgentValidator


class TestMultiAgentValidator:
    """בדיקות עבור Multi Agent Validator"""
    
    @pytest.fixture
    def sample_signals(self):
        """אותות לדוגמה"""
        return {
            "RSI_compression": True,
            "Volume_tension": True,
            "Breakout_retest": True,
            "Support_zone_strength": False,
            "MA_pressure": True,
            "Bullish_pattern": True,
            "Sentiment": True,
            "Social_hype": False,
            "News_catalyst": True,
            "Consistent_growth": True,
            "Valuation_anomaly": False,
            "Financial_stability": True
        }
    
    @pytest.fixture
    def validator(self):
        """יצירת מופע של הסוכן"""
        return MultiAgentValidator()
    
    def test_initialization(self, validator):
        """בדיקת אתחול הסוכן"""
        assert validator is not None
        assert hasattr(validator, 'config')
        assert hasattr(validator, 'logger')
        assert hasattr(validator, 'technical_signals')
        assert hasattr(validator, 'sentiment_signals')
        assert hasattr(validator, 'fundamental_signals')
        assert hasattr(validator, 'risk_signals')
        assert hasattr(validator, 'min_technical_consistency')
        assert hasattr(validator, 'conflict_threshold')
        assert hasattr(validator, 'risk_tolerance')
    
    def test_detect_conflicts(self, validator, sample_signals):
        """בדיקת זיהוי קונפליקטים"""
        conflicts = validator.detect_conflicts(sample_signals)
        assert isinstance(conflicts, list)
        # עם הנתונים האלה יכול להיות קונפליקט או לא
    
    def test_detect_conflicts_with_conflicts(self, validator):
        """בדיקת זיהוי קונפליקטים עם סתירות ברורות"""
        conflicting_signals = {
            "RSI_compression": True,
            "Volume_tension": False,  # סתירה עם RSI_compression
            "Parabolic_move": True,
            "MA_pressure": True,  # סתירה עם Parabolic_move
            "Geo_risk": True,
            "Sentiment": True  # סתירה עם Geo_risk
        }
        
        conflicts = validator.detect_conflicts(conflicting_signals)
        assert isinstance(conflicts, list)
        assert len(conflicts) > 0  # צריך להיות קונפליקט
    
    def test_calculate_signal_consistency(self, validator, sample_signals):
        """בדיקת חישוב עקביות אותות"""
        consistency = validator.calculate_signal_consistency(sample_signals)
        assert isinstance(consistency, float)
        assert 0 <= consistency <= 1
    
    def test_assess_overall_risk(self, validator, sample_signals):
        """בדיקת הערכת סיכון כללי"""
        risk = validator.assess_overall_risk(sample_signals)
        assert risk in ["LOW", "MEDIUM", "HIGH"]
    
    def test_assess_overall_risk_high(self, validator):
        """בדיקת הערכת סיכון גבוה"""
        high_risk_signals = {
            "Geo_risk": True,
            "Parabolic_move": True,
            "Overbought": True
        }
        risk = validator.assess_overall_risk(high_risk_signals)
        assert risk == "HIGH"
    
    def test_error_handling(self, validator):
        """בדיקת טיפול בשגיאות"""
        # בדיקה עם None
        conflicts = validator.detect_conflicts(None)
        assert isinstance(conflicts, list)
        assert len(conflicts) > 0  # צריך להחזיר שגיאה
        
        # בדיקה עם רשימה במקום מילון
        conflicts = validator.detect_conflicts([1, 2, 3])
        assert isinstance(conflicts, list)
        assert len(conflicts) > 0  # צריך להחזיר שגיאה
    
    def test_performance_under_load(self, validator, sample_signals):
        """בדיקת ביצועים תחת עומס"""
        import time
        
        # יצירת הרבה אותות
        many_signals = {}
        for i in range(50):
            many_signals[f'signal_{i}'] = (i % 2 == 0)
        
        start_time = time.time()
        conflicts = validator.detect_conflicts(many_signals)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # בדיקה שהזמן מתחת ל-2 שניות
        assert execution_time < 2.0
        assert isinstance(conflicts, list)
    
    def test_logging_functionality(self, validator, sample_signals):
        """בדיקת פונקציונליות לוגים"""
        with patch.object(validator.logger, 'warning') as mock_warning:
            validator.detect_conflicts(sample_signals)
            
            # בדיקה שהלוגר נקרא
            assert mock_warning.called
    
    def test_edge_cases(self, validator):
        """בדיקת מקרים קיצוניים"""
        # בדיקה עם אותות ריקים
        empty_signals = {}
        conflicts = validator.detect_conflicts(empty_signals)
        assert isinstance(conflicts, list)
        
        # בדיקה עם אותות לא מוכרים
        unknown_signals = {
            "unknown_signal_1": True,
            "unknown_signal_2": False
        }
        conflicts = validator.detect_conflicts(unknown_signals)
        assert isinstance(conflicts, list)
    
    def test_technical_conflicts_detection(self, validator):
        """בדיקת זיהוי סתירות טכניות"""
        technical_conflicts = {
            "RSI_compression": True,
            "Volume_tension": False,  # סתירה
            "Parabolic_move": True,
            "MA_pressure": True  # סתירה עם Parabolic_move
        }
        
        conflicts = validator.detect_conflicts(technical_conflicts)
        assert isinstance(conflicts, list)
        # צריך להיות לפחות סתירה אחת
    
    def test_sentiment_conflicts_detection(self, validator):
        """בדיקת זיהוי סתירות סנטימנט"""
        sentiment_conflicts = {
            "Social_hype": True,
            "Consistent_growth": False,  # סתירה
            "Valuation_anomaly": False,  # סתירה נוספת
            "News_catalyst": True,
            "Volume_tension": False  # סתירה עם News_catalyst
        }
        
        conflicts = validator.detect_conflicts(sentiment_conflicts)
        assert isinstance(conflicts, list)
        # צריך להיות לפחות סתירה אחת


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 