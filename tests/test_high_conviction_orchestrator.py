"""
בדיקות עבור High Conviction Orchestrator Agent
מבצע בדיקות יחידה לסוכן שמתאם בין סוכנים שונים
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.high_conviction_orchestrator import HighConvictionOrchestrator


class TestHighConvictionOrchestrator:
    """בדיקות עבור High Conviction Orchestrator"""
    
    @pytest.fixture
    def sample_analysis_result(self):
        """תוצאת ניתוח לדוגמה"""
        return {
            "score": 5,
            "signals": {
                "RSI_compression": True,
                "Volume_tension": True,
                "Breakout_retest": True,
                "Support_zone_strength": True,
                "MA_pressure": True,
                "Bullish_pattern": True,
                "Sentiment": True,
                "Social_hype": False,
                "News_catalyst": True,
                "Consistent_growth": True,
                "Valuation_anomaly": False,
                "Financial_stability": True
            },
            "recommendation": "HIGH CONVICTION BUY"
        }
    
    @pytest.fixture
    def orchestrator(self):
        """יצירת מופע של הסוכן"""
        return HighConvictionOrchestrator()
    
    def test_initialization(self, orchestrator):
        """בדיקת אתחול הסוכן"""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'config')
        assert hasattr(orchestrator, 'validator')
        assert hasattr(orchestrator, 'logger')
        assert hasattr(orchestrator, 'min_score_threshold')
        assert hasattr(orchestrator, 'min_technical_signals')
        assert hasattr(orchestrator, 'conflict_tolerance')
    
    def test_validate_analysis_result(self, orchestrator, sample_analysis_result):
        """בדיקת אימות תוצאת ניתוח"""
        # בדיקה עם נתונים תקינים
        result = orchestrator._validate_analysis_result(sample_analysis_result)
        assert result is True
        
        # בדיקה עם נתונים לא תקינים
        invalid_result = {"score": 5}  # חסרים signals ו-recommendation
        result = orchestrator._validate_analysis_result(invalid_result)
        assert result is False
        
        # בדיקה עם None
        result = orchestrator._validate_analysis_result(None)
        assert result is False
    
    def test_decide_high_conviction(self, orchestrator, sample_analysis_result):
        """בדיקת החלטה על conviction גבוה"""
        result = orchestrator.decide(sample_analysis_result)
        assert isinstance(result, bool)
        # עם הנתונים האלה צריך להיות True
    
    def test_decide_low_conviction(self, orchestrator):
        """בדיקת החלטה על conviction נמוך"""
        low_conviction_result = {
            "score": 2,
            "signals": {
                "RSI_compression": False,
                "Volume_tension": False,
                "Breakout_retest": False
            },
            "recommendation": "HOLD"
        }
        result = orchestrator.decide(low_conviction_result)
        assert isinstance(result, bool)
        # עם הנתונים האלה צריך להיות False
    
    def test_get_conviction_level(self, orchestrator, sample_analysis_result):
        """בדיקת קבלת רמת conviction"""
        level = orchestrator.get_conviction_level(sample_analysis_result)
        assert level in ["HIGH", "MEDIUM", "LOW"]
    
    def test_assess_technical_quality(self, orchestrator, sample_analysis_result):
        """בדיקת הערכת איכות טכנית"""
        signals = sample_analysis_result["signals"]
        quality = orchestrator._assess_technical_quality(signals)
        assert isinstance(quality, bool)
    
    def test_calculate_consistency_score(self, orchestrator, sample_analysis_result):
        """בדיקת חישוב ציון עקביות"""
        signals = sample_analysis_result["signals"]
        consistency = orchestrator._calculate_consistency_score(signals)
        assert isinstance(consistency, float)
        assert 0 <= consistency <= 1
    
    def test_calculate_group_consistency(self, orchestrator):
        """בדיקת חישוב עקביות קבוצה"""
        signals = {
            "RSI_compression": True,
            "Volume_tension": True,
            "Breakout_retest": True
        }
        group = ["RSI_compression", "Volume_tension", "Breakout_retest"]
        consistency = orchestrator._calculate_group_consistency(signals, group)
        assert isinstance(consistency, float)
        assert 0 <= consistency <= 1
    
    def test_error_handling(self, orchestrator):
        """בדיקת טיפול בשגיאות"""
        # בדיקה עם נתונים None
        result = orchestrator.decide(None)
        assert result is False
        
        # בדיקה עם נתונים לא תקינים
        invalid_data = "not a dict"
        result = orchestrator.decide(invalid_data)
        assert result is False
    
    def test_logging_functionality(self, orchestrator, sample_analysis_result):
        """בדיקת פונקציונליות לוגים"""
        with patch.object(orchestrator.logger, 'info') as mock_info:
            orchestrator.decide(sample_analysis_result)
            # בדיקה שהלוגר נקרא
            assert mock_info.called
    
    def test_performance_metrics(self, orchestrator, sample_analysis_result):
        """בדיקת מדדי ביצועים"""
        import time
        
        start_time = time.time()
        result = orchestrator.decide(sample_analysis_result)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # בדיקה שהזמן מתחת ל-1 שנייה
        assert execution_time < 1.0
        assert isinstance(result, bool)
    
    def test_edge_cases(self, orchestrator):
        """בדיקת מקרים קיצוניים"""
        # בדיקה עם אותות ריקים
        empty_signals = {
            "score": 5,
            "signals": {},
            "recommendation": "HIGH CONVICTION BUY"
        }
        result = orchestrator.decide(empty_signals)
        assert isinstance(result, bool)
        
        # בדיקה עם ציון גבוה מאוד
        high_score = {
            "score": 10,
            "signals": {"RSI_compression": True},
            "recommendation": "HIGH CONVICTION BUY"
        }
        result = orchestrator.decide(high_score)
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 