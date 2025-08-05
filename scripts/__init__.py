"""
Charles_FocusedSpec - Scripts Module
מערכת חיזוי מניות פורצות - מודול סקריפטים

מודול זה מכיל את כל הסקריפטים והכלים לניהול המערכת
"""

# Data Processing Scripts
from .smart_data_processor import SmartDataProcessor
from .enhanced_data_processor import EnhancedDataProcessor
from .advanced_indicators_processor import AdvancedIndicatorsProcessor
from .fill_historical_data import fill_historical_data
from .test_yfinance_fill_data import test_yfinance_fill_data

# Testing Scripts
from .test_working_agents import test_working_agents
from .test_alpha_score_engine import test_alpha_score_engine
from .test_enhanced_analyzer import test_enhanced_analyzer
from .test_complete_system import test_complete_system
from .test_real_stocks import test_real_stocks
from .test_smart_data_manager import test_smart_data_manager

# Analysis Scripts
from .agents_status_report import generate_agents_status_report
from .calculate_all_indicators import calculate_all_indicators

# Version
__version__ = "1.0.0"
__author__ = "Charles_FocusedSpec Team"
__description__ = "סקריפטים וכלי ניהול למערכת חיזוי מניות"

# Main exports
__all__ = [
    # Data Processing
    'SmartDataProcessor',
    'EnhancedDataProcessor',
    'AdvancedIndicatorsProcessor',
    'fill_historical_data',
    'test_yfinance_fill_data',
    
    # Testing
    'test_working_agents',
    'test_alpha_score_engine',
    'test_enhanced_analyzer',
    'test_complete_system',
    'test_real_stocks',
    'test_smart_data_manager',
    
    # Analysis
    'generate_agents_status_report',
    'calculate_all_indicators',
]
