"""
בדיקות עבור VWAP Trend Agent
מבצע בדיקות יחידה לסוכן שמנתח מגמות VWAP
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vwap_trend_agent import VWAPTrendAgent


class TestVWAPTrendAgent:
    """בדיקות עבור VWAP Trend Agent"""
    
    @pytest.fixture
    def sample_data(self):
        """נתוני בדיקה לדוגמה"""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        return pd.DataFrame({
            'open': np.random.uniform(100, 200, 100),
            'high': np.random.uniform(150, 250, 100),
            'low': np.random.uniform(50, 150, 100),
            'close': np.random.uniform(100, 200, 100),
            'volume': np.random.uniform(1000000, 5000000, 100)
        }, index=dates)
    
    @pytest.fixture
    def agent(self):
        """יצירת מופע של הסוכן"""
        return VWAPTrendAgent()
    
    def test_initialization(self, agent):
        """בדיקת אתחול הסוכן"""
        assert agent is not None
        assert hasattr(agent, 'name')
        assert hasattr(agent, 'description')
        assert agent.name == 'VWAP Trend Agent'
    
    def test_calculate_vwap(self, agent, sample_data):
        """בדיקת חישוב VWAP"""
        vwap = agent.calculate_vwap(sample_data)
        
        assert isinstance(vwap, pd.Series)
        assert len(vwap) == len(sample_data)
        assert not vwap.isna().all()  # לא כל הערכים צריכים להיות NaN
    
    def test_identify_vwap_trend(self, agent, sample_data):
        """בדיקת זיהוי מגמת VWAP"""
        trend = agent.identify_vwap_trend(sample_data)
        
        assert isinstance(trend, dict)
        assert 'trend_direction' in trend
        assert 'trend_strength' in trend
        assert 'confidence' in trend
        assert trend['trend_direction'] in ['bullish', 'bearish', 'neutral']
    
    def test_calculate_vwap_support_resistance(self, agent, sample_data):
        """בדיקת חישוב תמיכה והתנגדות VWAP"""
        levels = agent.calculate_vwap_support_resistance(sample_data)
        
        assert isinstance(levels, dict)
        assert 'support_level' in levels
        assert 'resistance_level' in levels
        assert 'current_vwap' in levels
    
    def test_analyze_price_vs_vwap(self, agent, sample_data):
        """בדיקת ניתוח מחיר מול VWAP"""
        analysis = agent.analyze_price_vs_vwap(sample_data)
        
        assert isinstance(analysis, dict)
        assert 'price_position' in analysis
        assert 'deviation_percentage' in analysis
        assert 'signal_strength' in analysis
    
    def test_generate_vwap_signals(self, agent, sample_data):
        """בדיקת יצירת אותות VWAP"""
        signals = agent.generate_vwap_signals(sample_data)
        
        assert isinstance(signals, dict)
        assert 'signal' in signals
        assert 'confidence' in signals
        assert 'reasoning' in signals
        assert signals['signal'] in ['buy', 'sell', 'hold']
    
    def test_error_handling(self, agent):
        """בדיקת טיפול בשגיאות"""
        # בדיקה עם נתונים None
        result = agent.analyze(None)
        assert result is None or 'error' in result
        
        # בדיקה עם נתונים ריקים
        empty_data = pd.DataFrame()
        result = agent.analyze(empty_data)
        assert result is None or 'error' in result
        
        # בדיקה עם נתונים חסרים
        invalid_data = pd.DataFrame({'open': [100, 101, 102]})
        result = agent.analyze(invalid_data)
        assert result is None or 'error' in result
    
    def test_analyze_with_mock_data(self, agent, sample_data):
        """בדיקת ניתוח עם נתונים מדומים"""
        with patch.object(agent, 'calculate_vwap') as mock_vwap:
            mock_vwap.return_value = pd.Series([150] * len(sample_data))
            
            result = agent.analyze(sample_data)
            
            assert result is not None
            assert 'vwap_trend' in result
            assert 'signals' in result
    
    def test_performance_metrics(self, agent, sample_data):
        """בדיקת מדדי ביצועים"""
        import time
        
        start_time = time.time()
        result = agent.analyze(sample_data)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # בדיקה שהזמן מתחת ל-3 שניות
        assert execution_time < 3.0
        assert result is not None
    
    def test_logging_functionality(self, agent, sample_data):
        """בדיקת פונקציונליות לוגים"""
        with patch('core.vwap_trend_agent.logger') as mock_logger:
            agent.analyze(sample_data)
            
            # בדיקה שהלוגר נקרא
            assert mock_logger.info.called or mock_logger.debug.called
    
    def test_edge_cases(self, agent):
        """בדיקת מקרים קיצוניים"""
        # בדיקה עם נתונים עם ערכים שליליים
        negative_data = pd.DataFrame({
            'open': [-100, -101, -102],
            'high': [-50, -51, -52],
            'low': [-150, -151, -152],
            'close': [-100, -101, -102],
            'volume': [1000000, 1000000, 1000000]
        })
        result = agent.analyze(negative_data)
        assert result is not None
        
        # בדיקה עם נתונים עם ערכים אפס
        zero_data = pd.DataFrame({
            'open': [0, 0, 0],
            'high': [0, 0, 0],
            'low': [0, 0, 0],
            'close': [0, 0, 0],
            'volume': [0, 0, 0]
        })
        result = agent.analyze(zero_data)
        assert result is not None
    
    def test_data_validation(self, agent, sample_data):
        """בדיקת אימות נתונים"""
        # בדיקה עם נתונים תקינים
        result = agent.validate_data(sample_data)
        assert result is True
        
        # בדיקה עם נתונים חסרים
        invalid_data = sample_data.drop(columns=['volume'])
        result = agent.validate_data(invalid_data)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 