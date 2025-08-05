"""
Data Validators - מערכת אימות נתונים
=====================================

מערכת אימות נתונים מקיפה לכל הסוכנים.
כוללת אימות סמלי מניות, נתוני מחיר, נפח, תאריכים ועוד.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
import re
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def validate_symbol(symbol: str) -> bool:
    """
    אימות סמל מניה
    
    Args:
        symbol: סמל המניה לאימות
        
    Returns:
        True אם הסמל תקין, False אחרת
    """
    try:
        if not symbol or not isinstance(symbol, str):
            return False
        
        # הסרת רווחים מיותרים
        symbol = symbol.strip().upper()
        
        # בדיקת אורך מינימלי
        if len(symbol) < 1 or len(symbol) > 10:
            return False
        
        # בדיקת תווים מותרים (אותיות, מספרים, נקודות)
        if not re.match(r'^[A-Z0-9.]+$', symbol):
            return False
        
        # בדיקת סמלים מיוחדים לא מותרים
        invalid_symbols = ['NULL', 'NONE', 'NAN', 'INF', 'N/A', '']
        if symbol in invalid_symbols:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating symbol {symbol}: {str(e)}")
        return False

def validate_stock_data(price_df: pd.DataFrame) -> bool:
    """
    אימות נתוני מחיר מניה
    
    Args:
        price_df: DataFrame עם נתוני מחיר
        
    Returns:
        True אם הנתונים תקינים, False אחרת
    """
    try:
        if price_df is None or not isinstance(price_df, pd.DataFrame):
            return False
        
        # בדיקת DataFrame ריק
        if price_df.empty:
            return False
        
        # בדיקת עמודות נדרשות
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in price_df.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
        
        # בדיקת אורך מינימלי
        if len(price_df) < 5:
            logger.warning("Insufficient data points (minimum 5 required)")
            return False
        
        # בדיקת ערכים שליליים במחירים
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if (price_df[col] <= 0).any():
                logger.warning(f"Negative or zero values found in {col}")
                return False
        
        # בדיקת ערכים שליליים בנפח
        if (price_df['volume'] < 0).any():
            logger.warning("Negative volume values found")
            return False
        
        # בדיקת עקביות מחירים (high >= low)
        if not (price_df['high'] >= price_df['low']).all():
            logger.warning("Inconsistent price data: high < low")
            return False
        
        # בדיקת עקביות מחירים (high >= open, high >= close)
        if not (price_df['high'] >= price_df['open']).all() or not (price_df['high'] >= price_df['close']).all():
            logger.warning("Inconsistent price data: high < open or close")
            return False
        
        # בדיקת עקביות מחירים (low <= open, low <= close)
        if not (price_df['low'] <= price_df['open']).all() or not (price_df['low'] <= price_df['close']).all():
            logger.warning("Inconsistent price data: low > open or close")
            return False
        
        # בדיקת ערכים NaN
        if price_df[required_columns].isna().any().any():
            logger.warning("NaN values found in price data")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating stock data: {str(e)}")
        return False

def validate_volume_data(volume_df: pd.DataFrame) -> bool:
    """
    אימות נתוני נפח
    
    Args:
        volume_df: DataFrame עם נתוני נפח
        
    Returns:
        True אם הנתונים תקינים, False אחרת
    """
    try:
        if volume_df is None or not isinstance(volume_df, pd.DataFrame):
            return False
        
        # בדיקת DataFrame ריק
        if volume_df.empty:
            return False
        
        # בדיקת עמודת נפח
        if 'volume' not in volume_df.columns:
            logger.warning("Volume column not found")
            return False
        
        # בדיקת אורך מינימלי
        if len(volume_df) < 5:
            logger.warning("Insufficient volume data points (minimum 5 required)")
            return False
        
        # בדיקת ערכים שליליים
        if (volume_df['volume'] < 0).any():
            logger.warning("Negative volume values found")
            return False
        
        # בדיקת ערכים NaN
        if volume_df['volume'].isna().any():
            logger.warning("NaN values found in volume data")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating volume data: {str(e)}")
        return False

def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    אימות טווח תאריכים
    
    Args:
        start_date: תאריך התחלה
        end_date: תאריך סיום
        
    Returns:
        True אם התאריכים תקינים, False אחרת
    """
    try:
        # המרה לתאריכים
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # בדיקת תאריכים תקינים
        if pd.isna(start) or pd.isna(end):
            return False
        
        # בדיקת סדר תאריכים
        if start >= end:
            logger.warning("Start date must be before end date")
            return False
        
        # בדיקת תאריכים עתידיים
        if end > datetime.now():
            logger.warning("End date cannot be in the future")
            return False
        
        # בדיקת טווח מינימלי
        if (end - start).days < 1:
            logger.warning("Date range must be at least 1 day")
            return False
        
        # בדיקת טווח מקסימלי (5 שנים)
        if (end - start).days > 1825:
            logger.warning("Date range cannot exceed 5 years")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating date range: {str(e)}")
        return False

def validate_technical_parameters(params: Dict[str, Any]) -> bool:
    """
    אימות פרמטרים טכניים
    
    Args:
        params: מילון פרמטרים לאימות
        
    Returns:
        True אם הפרמטרים תקינים, False אחרת
    """
    try:
        if not isinstance(params, dict):
            return False
        
        # פרמטרים נדרשים
        required_params = ['window', 'threshold']
        for param in required_params:
            if param not in params:
                logger.warning(f"Missing required parameter: {param}")
                return False
        
        # אימות window
        window = params.get('window')
        if not isinstance(window, (int, float)) or window <= 0:
            logger.warning("Window must be a positive number")
            return False
        
        # אימות threshold
        threshold = params.get('threshold')
        if not isinstance(threshold, (int, float)):
            logger.warning("Threshold must be a number")
            return False
        
        # אימות פרמטרים נוספים
        if 'min_periods' in params:
            min_periods = params['min_periods']
            if not isinstance(min_periods, int) or min_periods <= 0 or min_periods > window:
                logger.warning("min_periods must be a positive integer <= window")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating technical parameters: {str(e)}")
        return False

def validate_news_data(news_data: List[Dict]) -> bool:
    """
    אימות נתוני חדשות
    
    Args:
        news_data: רשימת מילונים עם נתוני חדשות
        
    Returns:
        True אם הנתונים תקינים, False אחרת
    """
    try:
        if not isinstance(news_data, list):
            return False
        
        if not news_data:  # רשימה ריקה תקינה
            return True
        
        # בדיקת כל פריט חדשות
        for i, news in enumerate(news_data):
            if not isinstance(news, dict):
                logger.warning(f"News item {i} is not a dictionary")
                return False
            
            # בדיקת שדות נדרשים
            required_fields = ['title', 'content', 'date']
            for field in required_fields:
                if field not in news:
                    logger.warning(f"Missing required field '{field}' in news item {i}")
                    return False
            
            # אימות תאריך
            try:
                pd.to_datetime(news['date'])
            except:
                logger.warning(f"Invalid date format in news item {i}")
                return False
            
            # אימות תוכן לא ריק
            if not news['title'].strip() or not news['content'].strip():
                logger.warning(f"Empty title or content in news item {i}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating news data: {str(e)}")
        return False

def validate_social_media_data(social_data: List[Dict]) -> bool:
    """
    אימות נתוני רשתות חברתיות
    
    Args:
        social_data: רשימת מילונים עם נתוני רשתות חברתיות
        
    Returns:
        True אם הנתונים תקינים, False אחרת
    """
    try:
        if not isinstance(social_data, list):
            return False
        
        if not social_data:  # רשימה ריקה תקינה
            return True
        
        # בדיקת כל פריט
        for i, post in enumerate(social_data):
            if not isinstance(post, dict):
                logger.warning(f"Social media item {i} is not a dictionary")
                return False
            
            # בדיקת שדות נדרשים
            required_fields = ['content', 'date', 'engagement_rate']
            for field in required_fields:
                if field not in post:
                    logger.warning(f"Missing required field '{field}' in social media item {i}")
                    return False
            
            # אימות תאריך
            try:
                pd.to_datetime(post['date'])
            except:
                logger.warning(f"Invalid date format in social media item {i}")
                return False
            
            # אימות engagement_rate
            engagement = post['engagement_rate']
            if not isinstance(engagement, (int, float)) or engagement < 0:
                logger.warning(f"Invalid engagement_rate in social media item {i}")
                return False
            
            # אימות תוכן לא ריק
            if not post['content'].strip():
                logger.warning(f"Empty content in social media item {i}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating social media data: {str(e)}")
        return False

def validate_company_info(company_info: Dict) -> bool:
    """
    אימות מידע על חברה
    
    Args:
        company_info: מילון עם מידע על החברה
        
    Returns:
        True אם המידע תקין, False אחרת
    """
    try:
        if not isinstance(company_info, dict):
            return False
        
        # בדיקת שדות נדרשים
        required_fields = ['name', 'sector', 'market_cap']
        for field in required_fields:
            if field not in company_info:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # אימות שם חברה
        if not company_info['name'].strip():
            logger.warning("Company name cannot be empty")
            return False
        
        # אימות סקטור
        if not company_info['sector'].strip():
            logger.warning("Sector cannot be empty")
            return False
        
        # אימות שווי שוק
        market_cap = company_info['market_cap']
        if not isinstance(market_cap, (int, float)) or market_cap <= 0:
            logger.warning("Market cap must be a positive number")
            return False
        
        # אימות שדות אופציונליים
        optional_fields = ['revenue', 'net_income', 'pe_ratio', 'debt_ratio']
        for field in optional_fields:
            if field in company_info:
                value = company_info[field]
                if value is not None and not isinstance(value, (int, float)):
                    logger.warning(f"Invalid {field} value")
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating company info: {str(e)}")
        return False

def validate_market_data(market_data: pd.DataFrame) -> bool:
    """
    אימות נתוני שוק
    
    Args:
        market_data: DataFrame עם נתוני שוק
        
    Returns:
        True אם הנתונים תקינים, False אחרת
    """
    try:
        if market_data is None or not isinstance(market_data, pd.DataFrame):
            return False
        
        # בדיקת DataFrame ריק
        if market_data.empty:
            return False
        
        # בדיקת עמודות נדרשות
        required_columns = ['close', 'volume']
        missing_columns = [col for col in required_columns if col not in market_data.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
        
        # בדיקת אורך מינימלי
        if len(market_data) < 5:
            logger.warning("Insufficient market data points (minimum 5 required)")
            return False
        
        # בדיקת ערכים שליליים
        if (market_data['close'] <= 0).any():
            logger.warning("Negative or zero values found in close prices")
            return False
        
        if (market_data['volume'] < 0).any():
            logger.warning("Negative volume values found")
            return False
        
        # בדיקת ערכים NaN
        if market_data[required_columns].isna().any().any():
            logger.warning("NaN values found in market data")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating market data: {str(e)}")
        return False

def validate_sector_data(sector_data: pd.DataFrame) -> bool:
    """
    אימות נתוני סקטור
    
    Args:
        sector_data: DataFrame עם נתוני סקטור
        
    Returns:
        True אם הנתונים תקינים, False אחרת
    """
    try:
        if sector_data is None or not isinstance(sector_data, pd.DataFrame):
            return False
        
        # בדיקת DataFrame ריק
        if sector_data.empty:
            return False
        
        # בדיקת עמודות נדרשות
        required_columns = ['close', 'volume']
        missing_columns = [col for col in required_columns if col not in sector_data.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
        
        # בדיקת אורך מינימלי
        if len(sector_data) < 5:
            logger.warning("Insufficient sector data points (minimum 5 required)")
            return False
        
        # בדיקת ערכים שליליים
        if (sector_data['close'] <= 0).any():
            logger.warning("Negative or zero values found in sector close prices")
            return False
        
        if (sector_data['volume'] < 0).any():
            logger.warning("Negative volume values found in sector data")
            return False
        
        # בדיקת ערכים NaN
        if sector_data[required_columns].isna().any().any():
            logger.warning("NaN values found in sector data")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating sector data: {str(e)}")
        return False

def validate_ipo_info(ipo_info: Dict) -> bool:
    """
    אימות מידע IPO
    
    Args:
        ipo_info: מילון עם מידע על ה-IPO
        
    Returns:
        True אם המידע תקין, False אחרת
    """
    try:
        if not isinstance(ipo_info, dict):
            return False
        
        # בדיקת שדות נדרשים
        required_fields = ['ipo_date', 'ipo_price', 'shares_offered']
        for field in required_fields:
            if field not in ipo_info:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # אימות תאריך IPO
        try:
            ipo_date = pd.to_datetime(ipo_info['ipo_date'])
            if ipo_date > datetime.now():
                logger.warning("IPO date cannot be in the future")
                return False
        except:
            logger.warning("Invalid IPO date format")
            return False
        
        # אימות מחיר IPO
        ipo_price = ipo_info['ipo_price']
        if not isinstance(ipo_price, (int, float)) or ipo_price <= 0:
            logger.warning("IPO price must be a positive number")
            return False
        
        # אימות מספר מניות
        shares_offered = ipo_info['shares_offered']
        if not isinstance(shares_offered, (int, float)) or shares_offered <= 0:
            logger.warning("Shares offered must be a positive number")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating IPO info: {str(e)}")
        return False

def validate_macro_events_data(macro_events: List[Dict]) -> bool:
    """
    אימות נתוני אירועים מאקרו
    
    Args:
        macro_events: רשימת מילונים עם נתוני אירועים מאקרו
        
    Returns:
        True אם הנתונים תקינים, False אחרת
    """
    try:
        if not isinstance(macro_events, list):
            return False
        
        if not macro_events:  # רשימה ריקה תקינה
            return True
        
        # בדיקת כל אירוע
        for i, event in enumerate(macro_events):
            if not isinstance(event, dict):
                logger.warning(f"Macro event {i} is not a dictionary")
                return False
            
            # בדיקת שדות נדרשים
            required_fields = ['date', 'type', 'description']
            for field in required_fields:
                if field not in event:
                    logger.warning(f"Missing required field '{field}' in macro event {i}")
                    return False
            
            # אימות תאריך
            try:
                event_date = pd.to_datetime(event['date'])
                if event_date > datetime.now():
                    logger.warning(f"Macro event date cannot be in the future: {i}")
                    return False
            except:
                logger.warning(f"Invalid date format in macro event {i}")
                return False
            
            # אימות סוג אירוע
            event_type = event['type']
            valid_types = [
                'fomc_meeting', 'fed_rate_decision', 'employment_report',
                'gdp_report', 'inflation_data', 'retail_sales',
                'manufacturing_pmi', 'services_pmi', 'housing_data',
                'trade_balance', 'consumer_confidence', 'business_sentiment'
            ]
            if event_type not in valid_types:
                logger.warning(f"Invalid event type in macro event {i}: {event_type}")
                return False
            
            # אימות תיאור לא ריק
            if not event['description'].strip():
                logger.warning(f"Empty description in macro event {i}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating macro events data: {str(e)}")
        return False

def validate_economic_indicators(economic_indicators: Dict) -> bool:
    """
    אימות אינדיקטורים כלכליים
    
    Args:
        economic_indicators: מילון עם אינדיקטורים כלכליים
        
    Returns:
        True אם הנתונים תקינים, False אחרת
    """
    try:
        if not isinstance(economic_indicators, dict):
            return False
        
        if not economic_indicators:  # מילון ריק תקין
            return True
        
        # בדיקת כל אינדיקטור
        for indicator_name, indicator_data in economic_indicators.items():
            if not isinstance(indicator_name, str) or not indicator_name.strip():
                logger.warning("Invalid indicator name")
                return False
            
            # בדיקת נתוני אינדיקטור
            if indicator_data is not None:
                if isinstance(indicator_data, pd.Series):
                    # אימות Series
                    if indicator_data.empty:
                        logger.warning(f"Empty data for indicator: {indicator_name}")
                        return False
                    
                    if indicator_data.isna().all():
                        logger.warning(f"All NaN values for indicator: {indicator_name}")
                        return False
                
                elif isinstance(indicator_data, (int, float)):
                    # אימות מספר
                    if np.isnan(indicator_data) or np.isinf(indicator_data):
                        logger.warning(f"Invalid numeric value for indicator: {indicator_name}")
                        return False
                
                else:
                    logger.warning(f"Invalid data type for indicator {indicator_name}")
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating economic indicators: {str(e)}")
        return False

def validate_short_interest_data(short_interest_data: pd.DataFrame) -> bool:
    """
    אימות נתוני שורט אינטרסט
    
    Args:
        short_interest_data: DataFrame עם נתוני שורט אינטרסט
        
    Returns:
        True אם הנתונים תקינים, False אחרת
    """
    try:
        if short_interest_data is None or not isinstance(short_interest_data, pd.DataFrame):
            return False
        
        # בדיקת DataFrame ריק
        if short_interest_data.empty:
            return False
        
        # בדיקת עמודות נדרשות
        required_columns = ['short_interest', 'date']
        missing_columns = [col for col in required_columns if col not in short_interest_data.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False
        
        # בדיקת אורך מינימלי
        if len(short_interest_data) < 2:
            logger.warning("Insufficient short interest data points (minimum 2 required)")
            return False
        
        # אימות תאריכים
        try:
            pd.to_datetime(short_interest_data['date'])
        except:
            logger.warning("Invalid date format in short interest data")
            return False
        
        # אימות ערכי שורט אינטרסט
        short_interest = short_interest_data['short_interest']
        if (short_interest < 0).any():
            logger.warning("Negative short interest values found")
            return False
        
        # בדיקת ערכים NaN
        if short_interest_data[required_columns].isna().any().any():
            logger.warning("NaN values found in short interest data")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating short interest data: {str(e)}")
        return False

def validate_data_consistency(price_df: pd.DataFrame, volume_df: pd.DataFrame = None,
                            market_data: pd.DataFrame = None) -> bool:
    """
    אימות עקביות נתונים בין מקורות שונים
    
    Args:
        price_df: נתוני מחיר
        volume_df: נתוני נפח (אופציונלי)
        market_data: נתוני שוק (אופציונלי)
        
    Returns:
        True אם הנתונים עקביים, False אחרת
    """
    try:
        # אימות נתוני מחיר
        if not validate_stock_data(price_df):
            return False
        
        # אימות נתוני נפח אם קיימים
        if volume_df is not None:
            if not validate_volume_data(volume_df):
                return False
            
            # בדיקת עקביות אורך
            if len(price_df) != len(volume_df):
                logger.warning("Price and volume data have different lengths")
                return False
            
            # בדיקת עקביות אינדקס
            if not price_df.index.equals(volume_df.index):
                logger.warning("Price and volume data have different indices")
                return False
        
        # אימות נתוני שוק אם קיימים
        if market_data is not None:
            if not validate_market_data(market_data):
                return False
            
            # בדיקת חפיפה תאריכית
            common_dates = price_df.index.intersection(market_data.index)
            if len(common_dates) < 5:
                logger.warning("Insufficient overlapping dates between stock and market data")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating data consistency: {str(e)}")
        return False


def validate_text_data(text_data: list) -> bool:
    """
    אימות רשימת טקסטים לניתוח סנטימנט/מודלים
    
    Args:
        text_data: רשימת מחרוזות טקסט
    
    Returns:
        True אם כל הטקסטים תקינים, False אחרת
    """
    try:
        if text_data is None or not isinstance(text_data, list):
            logger.warning("text_data is not a list or is None")
            return False
        if len(text_data) == 0:
            logger.warning("text_data is empty")
            return False
        for i, text in enumerate(text_data):
            if not isinstance(text, str):
                logger.warning(f"text_data[{i}] is not a string: {text}")
                return False
            if not text.strip():
                logger.warning(f"text_data[{i}] is empty or whitespace")
                return False
            if len(text) > 5000:
                logger.warning(f"text_data[{i}] is too long (>5000 chars)")
                return False
            # בדיקת תווים אסורים (שליטה בסיסית בלבד)
            if any(c in text for c in ['\0', '\x00', '\ufffd']):
                logger.warning(f"text_data[{i}] contains forbidden characters")
                return False
        return True
    except Exception as e:
        logger.error(f"Error validating text_data: {str(e)}")
        return False