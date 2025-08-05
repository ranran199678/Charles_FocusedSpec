"""
Charles_FocusedSpec - Tests Module
מערכת חיזוי מניות פורצות - מודול בדיקות

מודול זה מכיל את כל הבדיקות והטסטים של המערכת
"""

# Core Tests
from .test_alpha_score_engine import TestAlphaScoreEngine
from .test_data_fetcher import TestDataFetcher
from .test_smart_data_manager import TestSmartDataManager

# Agent Tests
from .test_adx_score_agent import TestADXScoreAgent
from .test_trend_shift_detector import TestTrendShiftDetector
from .test_trend_detector import TestTrendDetector
from .test_nlp_analyzer import TestNLPAnalyzer
from .test_event_scanner import TestEventScanner
from .test_vwap_trend_agent import TestVWAPTrendAgent
from .test_v_reversal_agent import TestVReversalAgent
from .test_multi_agent_validator import TestMultiAgentValidator
from .test_high_conviction_orchestrator import TestHighConvictionOrchestrator
from .test_support_zone_strength import TestSupportZoneStrength
from .test_return_forecaster import TestReturnForecaster
from .test_breakout_screener import TestBreakoutScreener

# Data Flow Tests
from .test_data_flow_qbts import TestDataFlowQBTS

# Version
__version__ = "1.0.0"
__author__ = "Charles_FocusedSpec Team"
__description__ = "בדיקות וטסטים למערכת חיזוי מניות"

# Main exports
__all__ = [
    # Core Tests
    'TestAlphaScoreEngine',
    'TestDataFetcher',
    'TestSmartDataManager',
    
    # Agent Tests
    'TestADXScoreAgent',
    'TestTrendShiftDetector',
    'TestTrendDetector',
    'TestNLPAnalyzer',
    'TestEventScanner',
    'TestVWAPTrendAgent',
    'TestVReversalAgent',
    'TestMultiAgentValidator',
    'TestHighConvictionOrchestrator',
    'TestSupportZoneStrength',
    'TestReturnForecaster',
    'TestBreakoutScreener',
    
    # Data Flow Tests
    'TestDataFlowQBTS',
]
