"""
Options Unusual Volume Agent - זיהוי נפחי אופציות חריגים
==========================================================

סוכן המזהה נפחי אופציות חריגים ומזהה אותות השקעה.
מבוסס על ניתוח נפחי אופציות, Put/Call ratio וזיהוי תבניות.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger()

class OptionsUnusualVolumeAgent:
    """
    סוכן לזיהוי נפחי אופציות חריגים
    """
    
    def __init__(self):
        """אתחול סוכן נפחי אופציות"""
        self.logger = logger
        self.validator = validate_symbol
        self.data_validator = validate_stock_data
        
        # פרמטרים לזיהוי נפח חריג
        self.volume_threshold = 3.0  # נפח גבוה פי 3 מהממוצע
        self.put_call_threshold = 2.0  # Put/Call ratio גבוה
        self.strike_threshold = 0.1  # מרחק של 10% מהמחיר הנוכחי
        self.expiry_threshold = 30  # ימים עד פקיעה
        
        # סוגי אופציות
        self.option_types = {
            'call': 'Call',
            'put': 'Put'
        }
        
    def analyze(self, symbol: str, price_df: pd.DataFrame,
                options_data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """
        ניתוח נפחי אופציות חריגים
        
        Args:
            symbol: סמל המניה
            price_df: DataFrame עם נתוני מחיר
            options_data: מילון עם נתוני אופציות
            
        Returns:
            Dict[str, Any]: תוצאות הניתוח
        """
        try:
            # אימות קלט
            is_valid_symbol, symbol_errors = self.validator(symbol)
            if not is_valid_symbol:
                return self._create_error_result(f"סמל לא תקין: {symbol_errors}")
                
            is_valid_data, data_errors = self.data_validator(price_df)
            if not is_valid_data:
                return self._create_error_result(f"נתונים לא תקינים: {data_errors}")
            
            self.logger.info(f"מתחיל ניתוח נפחי אופציות עבור {symbol}")
            
            # ניתוח נפחי אופציות
            volume_analysis = self._analyze_options_volume(options_data)
            put_call_analysis = self._analyze_put_call_ratio(options_data)
            strike_analysis = self._analyze_strike_distribution(price_df, options_data)
            expiry_analysis = self._analyze_expiry_patterns(options_data)
            correlation_analysis = self._analyze_price_correlation(price_df, options_data)
            
            # חישוב ציון כללי
            overall_score = self._calculate_options_score(
                volume_analysis, put_call_analysis, strike_analysis,
                expiry_analysis, correlation_analysis
            )
            
            # קביעת רמת ביטחון
            confidence_level = self._determine_confidence_level(overall_score)
            
            # יצירת המלצה
            recommendation = self._generate_recommendation(overall_score, confidence_level)
            
            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                volume_analysis, put_call_analysis, strike_analysis,
                expiry_analysis, correlation_analysis
            )
            
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'overall_score': overall_score,
                'confidence_level': confidence_level,
                'recommendation': recommendation,
                'key_signals': key_signals,
                'volume_analysis': volume_analysis,
                'put_call_analysis': put_call_analysis,
                'strike_analysis': strike_analysis,
                'expiry_analysis': expiry_analysis,
                'correlation_analysis': correlation_analysis,
                'status': 'success'
            }
            
            self.logger.info(f"ניתוח נפחי אופציות הושלם עבור {symbol} - ציון: {overall_score:.2f}")
            return result
            
        except Exception as e:
            error_msg = f"שגיאה בניתוח נפחי אופציות עבור {symbol}: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_options_volume(self, options_data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """ניתוח נפחי אופציות"""
        try:
            if not options_data:
                return {
                    'total_volume': 0,
                    'call_volume': 0,
                    'put_volume': 0,
                    'unusual_volume_count': 0,
                    'volume_trend': 'stable',
                    'score': 0
                }
            
            total_volume = 0
            call_volume = 0
            put_volume = 0
            unusual_volume_count = 0
            
            for option_type, data in options_data.items():
                if data is None or len(data) == 0:
                    continue
                
                # חישוב נפח כולל
                volume = data.get('Volume', pd.Series([0])).sum()
                total_volume += volume
                
                if option_type == 'call':
                    call_volume += volume
                elif option_type == 'put':
                    put_volume += volume
                
                # זיהוי נפח חריג
                if 'Volume' in data.columns:
                    avg_volume = data['Volume'].mean()
                    unusual_volume = data[data['Volume'] > avg_volume * self.volume_threshold]
                    unusual_volume_count += len(unusual_volume)
            
            # ניתוח מגמת נפח
            volume_trend = 'increasing' if total_volume > 0 else 'stable'
            
            return {
                'total_volume': total_volume,
                'call_volume': call_volume,
                'put_volume': put_volume,
                'unusual_volume_count': unusual_volume_count,
                'volume_trend': volume_trend,
                'score': min(100, unusual_volume_count * 20)
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח נפח: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_put_call_ratio(self, options_data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """ניתוח Put/Call ratio"""
        try:
            if not options_data:
                return {
                    'put_call_ratio': 1.0,
                    'ratio_trend': 'neutral',
                    'significance': 'low',
                    'score': 0
                }
            
            call_volume = 0
            put_volume = 0
            
            if 'call' in options_data and options_data['call'] is not None:
                call_volume = options_data['call'].get('Volume', pd.Series([0])).sum()
            
            if 'put' in options_data and options_data['put'] is not None:
                put_volume = options_data['put'].get('Volume', pd.Series([0])).sum()
            
            # חישוב Put/Call ratio
            put_call_ratio = put_volume / call_volume if call_volume > 0 else 1.0
            
            # ניתוח מגמה
            if put_call_ratio > self.put_call_threshold:
                ratio_trend = 'bearish'
                significance = 'high'
            elif put_call_ratio < 1 / self.put_call_threshold:
                ratio_trend = 'bullish'
                significance = 'high'
            else:
                ratio_trend = 'neutral'
                significance = 'low'
            
            # חישוב ציון
            score = min(100, max(0, abs(put_call_ratio - 1) * 50))
            
            return {
                'put_call_ratio': put_call_ratio,
                'ratio_trend': ratio_trend,
                'significance': significance,
                'call_volume': call_volume,
                'put_volume': put_volume,
                'score': score
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח Put/Call ratio: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_strike_distribution(self, price_df: pd.DataFrame,
                                   options_data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """ניתוח התפלגות Strike prices"""
        try:
            if not options_data or price_df is None or len(price_df) == 0:
                return {
                    'current_price': 0,
                    'itm_options': 0,
                    'otm_options': 0,
                    'atm_options': 0,
                    'strike_distribution': {},
                    'score': 0
                }
            
            current_price = price_df['Close'].iloc[-1] if len(price_df) > 0 else 0
            
            itm_options = 0  # In-the-money
            otm_options = 0  # Out-of-the-money
            atm_options = 0  # At-the-money
            strike_distribution = {}
            
            for option_type, data in options_data.items():
                if data is None or len(data) == 0 or 'Strike' not in data.columns:
                    continue
                
                for _, row in data.iterrows():
                    strike = row.get('Strike', 0)
                    volume = row.get('Volume', 0)
                    
                    # סיווג לפי Strike
                    if abs(strike - current_price) / current_price < 0.02:
                        atm_options += volume
                    elif (option_type == 'call' and strike < current_price) or \
                         (option_type == 'put' and strike > current_price):
                        itm_options += volume
                    else:
                        otm_options += volume
                    
                    # התפלגות Strike
                    strike_key = f"{strike:.0f}"
                    strike_distribution[strike_key] = strike_distribution.get(strike_key, 0) + volume
            
            # חישוב ציון
            total_options = itm_options + otm_options + atm_options
            if total_options > 0:
                otm_ratio = otm_options / total_options
                score = min(100, otm_ratio * 100)  # ציון גבוה יותר ל-OTM options
            else:
                score = 0
            
            return {
                'current_price': current_price,
                'itm_options': itm_options,
                'otm_options': otm_options,
                'atm_options': atm_options,
                'strike_distribution': strike_distribution,
                'otm_ratio': otm_ratio if total_options > 0 else 0,
                'score': score
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח Strike distribution: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_expiry_patterns(self, options_data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """ניתוח תבניות פקיעה"""
        try:
            if not options_data:
                return {
                    'near_term_volume': 0,
                    'far_term_volume': 0,
                    'expiry_distribution': {},
                    'urgency_score': 0,
                    'score': 0
                }
            
            near_term_volume = 0  # פחות מ-30 ימים
            far_term_volume = 0   # יותר מ-30 ימים
            expiry_distribution = {}
            
            for option_type, data in options_data.items():
                if data is None or len(data) == 0:
                    continue
                
                if 'Expiry' in data.columns and 'Volume' in data.columns:
                    for _, row in data.iterrows():
                        expiry_date = row.get('Expiry')
                        volume = row.get('Volume', 0)
                        
                        if expiry_date:
                            try:
                                days_to_expiry = (pd.to_datetime(expiry_date) - datetime.now()).days
                                
                                if days_to_expiry <= self.expiry_threshold:
                                    near_term_volume += volume
                                else:
                                    far_term_volume += volume
                                
                                # התפלגות פקיעה
                                expiry_key = f"{days_to_expiry}d"
                                expiry_distribution[expiry_key] = expiry_distribution.get(expiry_key, 0) + volume
                                
                            except:
                                continue
            
            # חישוב ציון דחיפות
            total_volume = near_term_volume + far_term_volume
            if total_volume > 0:
                urgency_ratio = near_term_volume / total_volume
                urgency_score = min(100, urgency_ratio * 100)
            else:
                urgency_score = 0
            
            return {
                'near_term_volume': near_term_volume,
                'far_term_volume': far_term_volume,
                'expiry_distribution': expiry_distribution,
                'urgency_ratio': urgency_ratio if total_volume > 0 else 0,
                'urgency_score': urgency_score,
                'score': urgency_score
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח תבניות פקיעה: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_price_correlation(self, price_df: pd.DataFrame,
                                 options_data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """ניתוח קורלציה בין נפחי אופציות למחיר"""
        try:
            if not options_data or price_df is None or len(price_df) == 0:
                return {
                    'price_correlation': 0,
                    'volume_price_trend': 'neutral',
                    'significance': 'low',
                    'score': 0
                }
            
            # יצירת סדרת זמן של נפחי אופציות
            options_volume_series = pd.Series([0] * len(price_df), index=price_df.index)
            
            for option_type, data in options_data.items():
                if data is None or len(data) == 0:
                    continue
                
                if 'Date' in data.columns and 'Volume' in data.columns:
                    for _, row in data.iterrows():
                        date = row.get('Date')
                        volume = row.get('Volume', 0)
                        
                        if date in options_volume_series.index:
                            options_volume_series[date] += volume
            
            # חישוב קורלציה
            price_changes = price_df['Close'].pct_change().dropna()
            options_volume_changes = options_volume_series.pct_change().dropna()
            
            # התאמת אינדקסים
            common_index = price_changes.index.intersection(options_volume_changes.index)
            if len(common_index) > 5:
                correlation = price_changes[common_index].corr(options_volume_changes[common_index])
            else:
                correlation = 0
            
            # ניתוח מגמה
            if correlation > 0.3:
                volume_price_trend = 'positive'
                significance = 'high'
            elif correlation < -0.3:
                volume_price_trend = 'negative'
                significance = 'high'
            else:
                volume_price_trend = 'neutral'
                significance = 'low'
            
            return {
                'price_correlation': correlation,
                'volume_price_trend': volume_price_trend,
                'significance': significance,
                'options_volume_series': options_volume_series.to_dict(),
                'score': min(100, max(0, abs(correlation) * 100))
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח קורלציה: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _calculate_options_score(self, volume_analysis: Dict, put_call_analysis: Dict,
                                strike_analysis: Dict, expiry_analysis: Dict,
                                correlation_analysis: Dict) -> float:
        """חישוב ציון נפחי אופציות כללי"""
        try:
            weights = {
                'volume': 0.25,
                'put_call': 0.25,
                'strike': 0.20,
                'expiry': 0.15,
                'correlation': 0.15
            }
            
            scores = {
                'volume': volume_analysis.get('score', 0),
                'put_call': put_call_analysis.get('score', 0),
                'strike': strike_analysis.get('score', 0),
                'expiry': expiry_analysis.get('score', 0),
                'correlation': correlation_analysis.get('score', 0)
            }
            
            weighted_score = sum(scores[key] * weights[key] for key in weights)
            
            # בונוסים נוספים
            bonuses = 0
            
            # בונוס לנפח חריג גבוה
            unusual_volume_count = volume_analysis.get('unusual_volume_count', 0)
            if unusual_volume_count >= 5:
                bonuses += 15
            
            # בונוס ל-Put/Call ratio חריג
            put_call_ratio = put_call_analysis.get('put_call_ratio', 1.0)
            if put_call_ratio > 2.0 or put_call_ratio < 0.5:
                bonuses += 10
            
            # בונוס לדחיפות גבוהה
            urgency_score = expiry_analysis.get('urgency_score', 0)
            if urgency_score > 70:
                bonuses += 10
            
            final_score = min(100, weighted_score + bonuses)
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"שגיאה בחישוב ציון: {str(e)}")
            return 0
    
    def _determine_confidence_level(self, score: float) -> str:
        """קביעת רמת ביטחון"""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _generate_recommendation(self, score: float, confidence: str) -> str:
        """יצירת המלצה"""
        if score >= 80:
            return "נפחי אופציות חריגים מאוד - סימן חזק לשינוי מגמה"
        elif score >= 60:
            return "נפחי אופציות חריגים - סימן משמעותי לשינוי"
        elif score >= 40:
            return "נפחי אופציות מוגברים - סימן מתון לשינוי"
        elif score >= 20:
            return "נפחי אופציות רגילים - ללא סימנים משמעותיים"
        else:
            return "נפחי אופציות נמוכים - ללא סימני שינוי"
    
    def _extract_key_signals(self, volume_analysis: Dict, put_call_analysis: Dict,
                            strike_analysis: Dict, expiry_analysis: Dict,
                            correlation_analysis: Dict) -> List[str]:
        """חילוץ אותות מפתח"""
        signals = []
        
        # אותות נפח
        unusual_volume_count = volume_analysis.get('unusual_volume_count', 0)
        if unusual_volume_count > 0:
            signals.append(f"{unusual_volume_count} אופציות עם נפח חריג")
        
        # אותות Put/Call ratio
        put_call_ratio = put_call_analysis.get('put_call_ratio', 1.0)
        if put_call_ratio > 2.0:
            signals.append("Put/Call ratio גבוה - סימן דובי")
        elif put_call_ratio < 0.5:
            signals.append("Put/Call ratio נמוך - סימן שורי")
        
        # אותות Strike
        otm_ratio = strike_analysis.get('otm_ratio', 0)
        if otm_ratio > 0.7:
            signals.append("ריכוז גבוה ב-OTM options")
        
        # אותות פקיעה
        urgency_score = expiry_analysis.get('urgency_score', 0)
        if urgency_score > 70:
            signals.append("ריכוז גבוה באופציות קרובות פקיעה")
        
        # אותות קורלציה
        correlation = correlation_analysis.get('price_correlation', 0)
        if abs(correlation) > 0.5:
            signals.append("קורלציה גבוהה בין נפחי אופציות למחיר")
        
        return signals
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """יצירת תוצאת שגיאה"""
        return {
            'symbol': 'unknown',
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0,
            'confidence_level': 'Very Low',
            'recommendation': 'לא ניתן לנתח - שגיאה בנתונים',
            'key_signals': [],
            'error': error_message,
            'status': 'error'
        }

# פונקציות עזר
def analyze_options_volume(symbol: str, price_df: pd.DataFrame,
                          options_data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
    """
    ניתוח נפחי אופציות חריגים
    
    Args:
        symbol: סמל המניה
        price_df: DataFrame עם נתוני מחיר
        options_data: מילון עם נתוני אופציות
        
    Returns:
        Dict[str, Any]: תוצאות הניתוח
    """
    agent = OptionsUnusualVolumeAgent()
    return agent.analyze(symbol, price_df, options_data)

def get_options_signals(analysis_result: Dict[str, Any]) -> List[str]:
    """
    קבלת אותות נפחי אופציות
    
    Args:
        analysis_result: תוצאת הניתוח
        
    Returns:
        List[str]: רשימת אותות
    """
    return analysis_result.get('key_signals', [])

def is_options_volume_significant(analysis_result: Dict[str, Any]) -> bool:
    """
    בדיקה אם נפחי האופציות משמעותיים
    
    Args:
        analysis_result: תוצאת הניתוח
        
    Returns:
        bool: True אם הנפחים משמעותיים
    """
    score = analysis_result.get('overall_score', 0)
    return score >= 60