"""
Charles_FocusedSpec - Utils Module
מערכת חיזוי מניות פורצות - מודול כלים

מודול זה מכיל את כל הכלים והפונקציות העזר של המערכת
"""

# Core Utilities
from .smart_data_manager import SmartDataManager
from .data_fetcher import DataFetcher
from .validators import (
    validate_symbol, validate_stock_data, validate_volume_data,
    validate_date_range, validate_technical_parameters, validate_news_data,
    validate_social_media_data, validate_company_info, validate_market_data,
    validate_sector_data, validate_ipo_info, validate_macro_events_data,
    validate_economic_indicators, validate_short_interest_data,
    validate_data_consistency
)
from .logger import setup_logger, get_logger
from .file_utils import FileManager, DataFileHandler
from .fmp_utils import FMPClient
from .constants import *
from .credentials import CredentialsManager, check_api_keys

# Additional Utilities
from .twelve_utils import TwelveDataUtils
from .finnhub_utils import FinnhubUtils
from .forecast_logger import ForecastLogger
from .fix_cert import fix_certificates

# Version
__version__ = "1.0.0"
__author__ = "Charles_FocusedSpec Team"
__description__ = "כלים ופונקציות עזר למערכת חיזוי מניות"

# Main exports
__all__ = [
    # Core Utilities
    'SmartDataManager',
    'DataFetcher',
    # Validators
    'validate_symbol',
    'validate_stock_data',
    'validate_volume_data',
    'validate_date_range',
    'validate_technical_parameters',
    'validate_news_data',
    'validate_social_media_data',
    'validate_company_info',
    'validate_market_data',
    'validate_sector_data',
    'validate_ipo_info',
    'validate_macro_events_data',
    'validate_economic_indicators',
    'validate_short_interest_data',
    'validate_data_consistency',
    'setup_logger',
    'get_logger',
    'FileManager',
    'DataFileHandler',
    'FMPClient',
    'CredentialsManager',
    'check_api_keys',
    
    # Additional Utilities
    'TwelveDataUtils',
    'FinnhubUtils',
    'ForecastLogger',
    'fix_certificates',
]
