"""
בדיקות עבור V-Reversal Agent
מבצע בדיקות יחידה לסוכן שמזהה תבניות V-Reversal
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.v_reversal_agent import VReversalAgent


class TestVReversalAgent:
    """בדיקות עבור V-Reversal Agent"""
    
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
    def v_pattern_data(self):
        """נתונים עם תבנית V ברורה"""
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        
        # יצירת תבנית V - ירידה ואז עלייה
        prices = []
        for i in range(50):
            if i < 25:
                # ירידה
                price = 200 - (i * 3)
            else:
                # עלייה
                price = 125 + ((i - 25) * 3)
            prices.append(price)
        
        return pd.DataFrame({
            'open': prices,
            'high': [p + 5 for p in prices],
            'low': [p - 5 for p in prices],
            'close': prices,
            'volume': np.random.uniform(1000000, 5000000, 50)
        }, index=dates)
    
    @pytest.fixture
    def agent(self):
        """יצירת מופע של הסוכן"""
        return VReversalAgent()
    
    def test_initialization(self, agent):
        """בדיקת אתחול הסוכן"""
        assert agent is not None
        assert hasattr(agent, 'name')
        assert hasattr(agent, 'description')
        assert agent.name == 'V-Reversal Agent'
    
    def test_detect_v_pattern(self, agent, v_pattern_data):
        """בדיקת זיהוי תבנית V"""
        pattern = agent.detect_v_pattern(v_pattern_data)
        
        assert isinstance(pattern, dict)
        assert 'v_pattern_detected' in pattern
        assert 'confidence' in pattern
        assert 'reversal_point' in pattern
        assert pattern['v_pattern_detected'] is True
    
    def test_calculate_reversal_strength(self, agent, v_pattern_data):
        """בדיקת חישוב חוזק ההיפוך"""
        strength = agent.calculate_reversal_strength(v_pattern_data)
        
        assert isinstance(strength, float)
        assert 0 <= strength <= 1
        assert strength > 0.5  # עם תבנית V ברורה
    
    def test_identify_reversal_point(self, agent, v_pattern_data):
        """בדיקת זיהוי נקודת ההיפוך"""
        point = agent.identify_reversal_point(v_pattern_data)
        
        assert isinstance(point, dict)
        assert 'index' in point
        assert 'price' in point
        assert 'volume_spike' in point
    
    def test_analyze_volume_confirmation(self, agent, v_pattern_data):
        """בדיקת ניתוח אישור נפח"""
        confirmation = agent.analyze_volume_confirmation(v_pattern_data)
        
        assert isinstance(confirmation, dict)
        assert 'volume_confirms' in confirmation
        assert 'volume_trend' in confirmation
        assert 'confidence' in confirmation
    
    def test_generate_reversal_signals(self, agent, v_pattern_data):
        """בדיקת יצירת אותות היפוך"""
        signals = agent.generate_reversal_signals(v_pattern_data)
        
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
        
        # בדיקה עם נתונים קצרים מדי
        short_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [100, 101, 102],
            'volume': [1000000, 1000000, 1000000]
        })
        result = agent.analyze(short_data)
        assert result is None or 'error' in result
    
    def test_analyze_with_mock_data(self, agent, sample_data):
        """בדיקת ניתוח עם נתונים מדומים"""
        with patch.object(agent, 'detect_v_pattern') as mock_detect:
            mock_detect.return_value = {
                'v_pattern_detected': True,
                'confidence': 0.8,
                'reversal_point': 25
            }
            
            result = agent.analyze(sample_data)
            
            assert result is not None
            assert 'v_pattern' in result
            assert 'signals' in result
    
    def test_performance_metrics(self, agent, v_pattern_data):
        """בדיקת מדדי ביצועים"""
        import time
        
        start_time = time.time()
        result = agent.analyze(v_pattern_data)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # בדיקה שהזמן מתחת ל-3 שניות
        assert execution_time < 3.0
        assert result is not None
    
    def test_logging_functionality(self, agent, v_pattern_data):
        """בדיקת פונקציונליות לוגים"""
        with patch('core.v_reversal_agent.logger') as mock_logger:
            agent.analyze(v_pattern_data)
            
            # בדיקה שהלוגר נקרא
            assert mock_logger.info.called or mock_logger.debug.called
    
    def test_edge_cases(self, agent):
        """בדיקת מקרים קיצוניים"""
        # בדיקה עם נתונים עם תנודות קיצוניות
        volatile_data = pd.DataFrame({
            'open': [100, 200, 50, 300, 25],
            'high': [110, 210, 60, 310, 35],
            'low': [90, 190, 40, 290, 15],
            'close': [100, 200, 50, 300, 25],
            'volume': [1000000] * 5
        })
        result = agent.analyze(volatile_data)
        assert result is not None
        
        # בדיקה עם נתונים עם ערכים שליליים
        negative_data = pd.DataFrame({
            'open': [-100, -101, -102],
            'high': [-95, -96, -97],
            'low': [-105, -106, -107],
            'close': [-100, -101, -102],
            'volume': [1000000, 1000000, 1000000]
        })
        result = agent.analyze(negative_data)
        assert result is not None
    
    def test_data_validation(self, agent, v_pattern_data):
        """בדיקת אימות נתונים"""
        # בדיקה עם נתונים תקינים
        result = agent.validate_data(v_pattern_data)
        assert result is True
        
        # בדיקה עם נתונים חסרים
        invalid_data = v_pattern_data.drop(columns=['volume'])
        result = agent.validate_data(invalid_data)
        assert result is False
    
    def test_no_v_pattern_detection(self, agent, sample_data):
        """בדיקת זיהוי כשאין תבנית V"""
        # נתונים ללא תבנית V ברורה
        result = agent.detect_v_pattern(sample_data)
        
        assert isinstance(result, dict)
        assert 'v_pattern_detected' in result
        # לא בהכרח צריך להיות True עם נתונים רנדומליים


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 