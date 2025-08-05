"""
Insider Activity Monitor - מעקב אחר פעילות פנים-ארגונית
==========================================================

סוכן המעקב אחר פעילות פנים-ארגונית ומזהה אותות השקעה.
מבוסס על ניתוח עסקאות פנים, נפח חריג וזמני ביצוע.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("InsiderActivityMonitor")

class InsiderActivityMonitor:
    """
    סוכן למעקב אחר פעילות פנים-ארגונית
    """
    
    def __init__(self):
        """אתחול סוכן מעקב פעילות פנים"""
        self.logger = logger
        self.validator = validate_symbol
        self.data_validator = validate_stock_data
        
        # פרמטרים לזיהוי פעילות פנים
        self.volume_threshold = 2.0  # נפח גבוה פי 2 מהממוצע
        self.price_change_threshold = 0.03  # שינוי מחיר של 3%
        self.insider_confidence_threshold = 0.7  # סף ביטחון לפעילות פנים
        self.lookback_days = 30  # ימי מעקב אחורה
        
        # סוגי פעילות פנים
        self.insider_activity_types = {
            'buy': 'רכישה',
            'sell': 'מכירה',
            'option_exercise': 'מימוש אופציות',
            'gift': 'תרומה',
            'inheritance': 'ירושה',
            'divorce': 'גירושין',
            'estate_planning': 'תכנון עיזבון'
        }
        
    def analyze(self, symbol: str, price_df: pd.DataFrame,
                volume_data: pd.DataFrame = None,
                insider_transactions: List[Dict] = None) -> Dict[str, Any]:
        """
        ניתוח פעילות פנים-ארגונית
        
        Args:
            symbol: סמל המניה
            price_df: DataFrame עם נתוני מחיר
            volume_data: נתוני נפח (אופציונלי)
            insider_transactions: רשימת עסקאות פנים (אופציונלי)
            
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
            
            self.logger.info(f"מתחיל ניתוח פעילות פנים עבור {symbol}")
            
            # ניתוח פעילות פנים
            volume_analysis = self._analyze_volume_patterns(price_df, volume_data)
            price_analysis = self._analyze_price_patterns(price_df)
            timing_analysis = self._analyze_timing_patterns(price_df)
            transaction_analysis = self._analyze_insider_transactions(insider_transactions)
            correlation_analysis = self._analyze_insider_correlation(price_df, insider_transactions)
            
            # חישוב ציון כללי
            overall_score = self._calculate_insider_score(
                volume_analysis, price_analysis, timing_analysis,
                transaction_analysis, correlation_analysis
            )
            
            # קביעת רמת ביטחון
            confidence_level = self._determine_confidence_level(overall_score)
            
            # יצירת המלצה
            recommendation = self._generate_recommendation(overall_score, confidence_level)
            
            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                volume_analysis, price_analysis, timing_analysis,
                transaction_analysis, correlation_analysis
            )
            
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'overall_score': overall_score,
                'confidence_level': confidence_level,
                'recommendation': recommendation,
                'key_signals': key_signals,
                'volume_analysis': volume_analysis,
                'price_analysis': price_analysis,
                'timing_analysis': timing_analysis,
                'transaction_analysis': transaction_analysis,
                'correlation_analysis': correlation_analysis,
                'status': 'success'
            }
            
            self.logger.info(f"ניתוח פעילות פנים הושלם עבור {symbol} - ציון: {overall_score:.2f}")
            return result
            
        except Exception as e:
            error_msg = f"שגיאה בניתוח פעילות פנים עבור {symbol}: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_volume_patterns(self, price_df: pd.DataFrame,
                                volume_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח תבניות נפח"""
        try:
            df = price_df.copy()
            
            # חישוב ממוצע נפח
            df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
            
            # זיהוי נפח חריג
            high_volume_days = df[df['volume_ratio'] > self.volume_threshold]
            very_high_volume_days = df[df['volume_ratio'] > self.volume_threshold * 1.5]
            
            # ניתוח נפח ביחס למחיר
            df['price_change'] = df['Close'].pct_change()
            df['volume_price_correlation'] = df['volume_ratio'].rolling(10).corr(df['price_change'])
            
            recent_volume_ratio = df['volume_ratio'].iloc[-1] if len(df) > 0 else 1
            recent_correlation = df['volume_price_correlation'].iloc[-1] if len(df) > 0 else 0
            
            # זיהוי תבניות נפח חשודות
            suspicious_patterns = []
            if recent_volume_ratio > self.volume_threshold:
                suspicious_patterns.append("נפח גבוה מהרגיל")
            if recent_correlation > 0.7:
                suspicious_patterns.append("קורלציה גבוהה בין נפח למחיר")
            
            return {
                'recent_volume_ratio': recent_volume_ratio,
                'volume_price_correlation': recent_correlation,
                'high_volume_days': len(high_volume_days),
                'very_high_volume_days': len(very_high_volume_days),
                'suspicious_patterns': suspicious_patterns,
                'volume_trend': 'increasing' if recent_volume_ratio > 1.5 else 'stable' if recent_volume_ratio > 0.8 else 'decreasing',
                'score': min(100, recent_volume_ratio * 30)
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח נפח: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_price_patterns(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח תבניות מחיר"""
        try:
            df = price_df.copy()
            
            # חישוב שינויים במחיר
            df['price_change'] = df['Close'].pct_change()
            df['price_change_abs'] = df['price_change'].abs()
            
            # זיהוי שינויים חריגים
            recent_price_change = df['price_change'].iloc[-1] if len(df) > 0 else 0
            recent_price_change_abs = df['price_change_abs'].iloc[-1] if len(df) > 0 else 0
            
            # ניתוח תנודתיות
            volatility = df['price_change'].tail(self.lookback_days).std()
            avg_volatility = df['price_change'].std()
            relative_volatility = volatility / avg_volatility if avg_volatility > 0 else 1
            
            # זיהוי תבניות חשודות
            suspicious_patterns = []
            if recent_price_change_abs > self.price_change_threshold:
                suspicious_patterns.append("שינוי מחיר חריג")
            if relative_volatility > 1.5:
                suspicious_patterns.append("תנודתיות גבוהה מהרגיל")
            
            # ניתוח מגמה
            df['sma_20'] = df['Close'].rolling(window=20).mean()
            current_price = df['Close'].iloc[-1] if len(df) > 0 else 0
            current_sma = df['sma_20'].iloc[-1] if len(df) > 0 else 0
            
            trend = 'bullish' if current_price > current_sma else 'bearish'
            
            return {
                'recent_price_change': recent_price_change,
                'recent_price_change_abs': recent_price_change_abs,
                'volatility': volatility,
                'relative_volatility': relative_volatility,
                'suspicious_patterns': suspicious_patterns,
                'trend': trend,
                'current_price': current_price,
                'current_sma_20': current_sma,
                'score': min(100, max(0, 50 + (recent_price_change * 1000)))
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח מחיר: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_timing_patterns(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח תבניות זמנים"""
        try:
            df = price_df.copy()
            
            # ניתוח תבניות יומיות
            df['day_of_week'] = pd.to_datetime(df.index).dayofweek
            df['month'] = pd.to_datetime(df.index).month
            
            # זיהוי ימים עם פעילות חריגה
            daily_volume = df.groupby('day_of_week')['Volume'].mean()
            daily_price_change = df.groupby('day_of_week')['Close'].pct_change().mean()
            
            # זיהוי חודשים עם פעילות חריגה
            monthly_volume = df.groupby('month')['Volume'].mean()
            monthly_price_change = df.groupby('month')['Close'].pct_change().mean()
            
            # ניתוח תבניות זמן
            current_day = pd.to_datetime(df.index[-1]).dayofweek if len(df) > 0 else 0
            current_month = pd.to_datetime(df.index[-1]).month if len(df) > 0 else 1
            
            day_volume_ratio = df['Volume'].iloc[-1] / daily_volume.get(current_day, df['Volume'].mean()) if len(df) > 0 else 1
            
            timing_patterns = []
            if day_volume_ratio > 1.5:
                timing_patterns.append("נפח גבוה ביחס ליום זה בשבוע")
            
            return {
                'daily_volume_patterns': daily_volume.to_dict(),
                'daily_price_patterns': daily_price_change.to_dict(),
                'monthly_volume_patterns': monthly_volume.to_dict(),
                'monthly_price_patterns': monthly_price_change.to_dict(),
                'current_day_volume_ratio': day_volume_ratio,
                'timing_patterns': timing_patterns,
                'score': min(100, day_volume_ratio * 50)
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח זמנים: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_insider_transactions(self, insider_transactions: List[Dict] = None) -> Dict[str, Any]:
        """ניתוח עסקאות פנים"""
        try:
            if not insider_transactions:
                return {
                    'transaction_count': 0,
                    'buy_transactions': 0,
                    'sell_transactions': 0,
                    'total_volume': 0,
                    'average_transaction_size': 0,
                    'recent_transactions': [],
                    'score': 0
                }
            
            # ניתוח עסקאות
            buy_transactions = [t for t in insider_transactions if t.get('type') == 'buy']
            sell_transactions = [t for t in insider_transactions if t.get('type') == 'sell']
            
            total_volume = sum(t.get('volume', 0) for t in insider_transactions)
            average_transaction_size = total_volume / len(insider_transactions) if insider_transactions else 0
            
            # עסקאות אחרונות
            recent_transactions = sorted(insider_transactions, 
                                       key=lambda x: x.get('date', ''), reverse=True)[:5]
            
            # חישוב ציון
            transaction_score = min(100, len(insider_transactions) * 10)
            if buy_transactions and not sell_transactions:
                transaction_score += 20  # בונוס לרכישות בלבד
            
            return {
                'transaction_count': len(insider_transactions),
                'buy_transactions': len(buy_transactions),
                'sell_transactions': len(sell_transactions),
                'total_volume': total_volume,
                'average_transaction_size': average_transaction_size,
                'recent_transactions': recent_transactions,
                'buy_sell_ratio': len(buy_transactions) / len(sell_transactions) if sell_transactions else float('inf'),
                'score': transaction_score
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח עסקאות: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_insider_correlation(self, price_df: pd.DataFrame,
                                   insider_transactions: List[Dict] = None) -> Dict[str, Any]:
        """ניתוח קורלציה בין פעילות פנים למחיר"""
        try:
            if not insider_transactions:
                return {'score': 0, 'correlation': 0, 'significance': 'low'}
            
            # יצירת DataFrame עם עסקאות פנים
            transaction_dates = [t.get('date') for t in insider_transactions if t.get('date')]
            transaction_volumes = [t.get('volume', 0) for t in insider_transactions if t.get('date')]
            
            if not transaction_dates:
                return {'score': 0, 'correlation': 0, 'significance': 'low'}
            
            # חישוב קורלציה
            df = price_df.copy()
            df['insider_activity'] = 0
            
            for date, volume in zip(transaction_dates, transaction_volumes):
                if date in df.index:
                    df.loc[date, 'insider_activity'] = volume
            
            # חישוב קורלציה בין פעילות פנים לשינויי מחיר
            df['price_change'] = df['Close'].pct_change()
            correlation = df['insider_activity'].corr(df['price_change'])
            
            # חישוב משמעות
            significance = 'high' if abs(correlation) > 0.5 else 'medium' if abs(correlation) > 0.3 else 'low'
            
            return {
                'correlation': correlation,
                'significance': significance,
                'transaction_dates': transaction_dates,
                'transaction_volumes': transaction_volumes,
                'score': min(100, max(0, abs(correlation) * 100))
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח קורלציה: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _calculate_insider_score(self, volume_analysis: Dict, price_analysis: Dict,
                                timing_analysis: Dict, transaction_analysis: Dict,
                                correlation_analysis: Dict) -> float:
        """חישוב ציון פעילות פנים כללי"""
        try:
            weights = {
                'volume': 0.25,
                'price': 0.20,
                'timing': 0.15,
                'transactions': 0.25,
                'correlation': 0.15
            }
            
            scores = {
                'volume': volume_analysis.get('score', 0),
                'price': price_analysis.get('score', 0),
                'timing': timing_analysis.get('score', 0),
                'transactions': transaction_analysis.get('score', 0),
                'correlation': correlation_analysis.get('score', 0)
            }
            
            weighted_score = sum(scores[key] * weights[key] for key in weights)
            
            # בונוסים נוספים
            bonuses = 0
            
            # בונוס לנפח חריג
            if volume_analysis.get('recent_volume_ratio', 1) > 2.0:
                bonuses += 10
            
            # בונוס לעסקאות רכישה בלבד
            buy_sell_ratio = transaction_analysis.get('buy_sell_ratio', 0)
            if buy_sell_ratio > 2:
                bonuses += 15
            
            # בונוס לקורלציה גבוהה
            if correlation_analysis.get('significance') == 'high':
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
            return "פעילות פנים חזקה - סימן חיובי להשקעה"
        elif score >= 60:
            return "פעילות פנים משמעותית - כדאי לעקוב"
        elif score >= 40:
            return "פעילות פנים מתונה - סימנים מעורבים"
        elif score >= 20:
            return "פעילות פנים חלשה - לא סימן משמעותי"
        else:
            return "אין פעילות פנים משמעותית - לא מומלץ"
    
    def _extract_key_signals(self, volume_analysis: Dict, price_analysis: Dict,
                            timing_analysis: Dict, transaction_analysis: Dict,
                            correlation_analysis: Dict) -> List[str]:
        """חילוץ אותות מפתח"""
        signals = []
        
        # אותות נפח
        if volume_analysis.get('recent_volume_ratio', 1) > 1.5:
            signals.append("נפח גבוה מהרגיל")
        
        # אותות מחיר
        if price_analysis.get('recent_price_change_abs', 0) > 0.02:
            signals.append("שינוי מחיר משמעותי")
        
        # אותות עסקאות
        transaction_count = transaction_analysis.get('transaction_count', 0)
        if transaction_count > 0:
            signals.append(f"{transaction_count} עסקאות פנים")
        
        buy_sell_ratio = transaction_analysis.get('buy_sell_ratio', 0)
        if buy_sell_ratio > 2:
            signals.append("עסקאות רכישה דומיננטיות")
        
        # אותות קורלציה
        if correlation_analysis.get('significance') == 'high':
            signals.append("קורלציה גבוהה בין פעילות פנים למחיר")
        
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
def monitor_insider_activity(symbol: str, price_df: pd.DataFrame,
                           volume_data: pd.DataFrame = None,
                           insider_transactions: List[Dict] = None) -> Dict[str, Any]:
    """
    מעקב אחר פעילות פנים-ארגונית
    
    Args:
        symbol: סמל המניה
        price_df: DataFrame עם נתוני מחיר
        volume_data: נתוני נפח (אופציונלי)
        insider_transactions: רשימת עסקאות פנים (אופציונלי)
        
    Returns:
        Dict[str, Any]: תוצאות הניתוח
    """
    monitor = InsiderActivityMonitor()
    return monitor.analyze(symbol, price_df, volume_data, insider_transactions)

def get_insider_signals(analysis_result: Dict[str, Any]) -> List[str]:
    """
    קבלת אותות פעילות פנים
    
    Args:
        analysis_result: תוצאת הניתוח
        
    Returns:
        List[str]: רשימת אותות
    """
    return analysis_result.get('key_signals', [])

def is_insider_activity_significant(analysis_result: Dict[str, Any]) -> bool:
    """
    בדיקה אם פעילות הפנים משמעותית
    
    Args:
        analysis_result: תוצאת הניתוח
        
    Returns:
        bool: True אם הפעילות משמעותית
    """
    score = analysis_result.get('overall_score', 0)
    return score >= 60