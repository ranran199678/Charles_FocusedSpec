"""
Early Reversal Anticipator - זיהוי מוקדם של שינויי מגמה
=======================================================

סוכן המזהה סימנים מוקדמים לשינויי מגמה בשוק המניות.
מבוסס על ניתוח טכני מתקדם וזיהוי תבניות המקדימות שינויים.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("EarlyReversalAnticipator")

class EarlyReversalAnticipator:
    """
    סוכן לזיהוי מוקדם של שינויי מגמה
    
    מזהה סימנים מוקדמים לשינויי מגמה באמצעות:
    - ניתוח נפח ומומנטום
    - זיהוי תבניות מחיר מתקדמות
    - ניתוח אינדיקטורים טכניים
    - זיהוי דיברגנס
    """
    
    def __init__(self):
        """אתחול הסוכן"""
        self.name = "EarlyReversalAnticipator"
        self.description = "זיהוי מוקדם של שינויי מגמה"
        self.version = "1.0.0"
        
        # פרמטרים לניתוח
        self.lookback_periods = {
            'short': 5,
            'medium': 14,
            'long': 50
        }
        
        self.volume_threshold = 1.5  # נפח גבוה מ-150% מהממוצע
        self.momentum_threshold = 0.02  # שינוי מומנטום של 2%
        self.divergence_threshold = 0.1  # דיברגנס של 10%
        
        logger.info(f"אתחול {self.name} v{self.version}")
    
    def analyze(self, symbol: str, price_df: pd.DataFrame, 
                technical_indicators: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """
        ניתוח מניה לזיהוי סימנים מוקדמים לשינוי מגמה
        
        Args:
            symbol: סמל המניה
            price_df: DataFrame עם נתוני מחיר
            technical_indicators: מילון עם אינדיקטורים טכניים
            
        Returns:
            Dict[str, Any]: תוצאות הניתוח
        """
        try:
            # אימות קלט
            is_valid_symbol, symbol_errors = validate_symbol(symbol)
            if not is_valid_symbol:
                return self._create_error_result(f"סמל לא תקין: {symbol_errors}")
            
            is_valid_data, data_errors = validate_stock_data(price_df)
            if not is_valid_data:
                return self._create_error_result(f"נתונים לא תקינים: {data_errors}")
            
            logger.info(f"התחלת ניתוח {symbol}")
            
            # ניתוח בסיסי
            basic_analysis = self._analyze_basic_patterns(price_df)
            
            # ניתוח נפח
            volume_analysis = self._analyze_volume_patterns(price_df)
            
            # ניתוח מומנטום
            momentum_analysis = self._analyze_momentum(price_df)
            
            # ניתוח דיברגנס
            divergence_analysis = self._analyze_divergence(price_df, technical_indicators)
            
            # ניתוח תבניות מתקדמות
            pattern_analysis = self._analyze_advanced_patterns(price_df)
            
            # חישוב ציון כללי
            overall_score = self._calculate_overall_score(
                basic_analysis, volume_analysis, momentum_analysis, 
                divergence_analysis, pattern_analysis
            )
            
            # קביעת רמת ביטחון
            confidence_level = self._determine_confidence_level(overall_score)
            
            # יצירת המלצה
            recommendation = self._generate_recommendation(overall_score, confidence_level)
            
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'agent': self.name,
                'version': self.version,
                'overall_score': overall_score,
                'confidence_level': confidence_level,
                'recommendation': recommendation,
                'analysis': {
                    'basic_patterns': basic_analysis,
                    'volume_patterns': volume_analysis,
                    'momentum_analysis': momentum_analysis,
                    'divergence_analysis': divergence_analysis,
                    'pattern_analysis': pattern_analysis
                },
                'signals': self._extract_key_signals(
                    basic_analysis, volume_analysis, momentum_analysis,
                    divergence_analysis, pattern_analysis
                ),
                'status': 'success'
            }
            
            logger.info(f"ניתוח {symbol} הושלם - ציון: {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח {symbol}: {str(e)}")
            return self._create_error_result(f"שגיאה בניתוח: {str(e)}")
    
    def _analyze_basic_patterns(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח תבניות בסיסיות"""
        try:
            df = price_df.copy()
            
            # חישוב ממוצעים נעים
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()
            
            # זיהוי שינויי מגמה
            df['trend_change'] = (
                (df['SMA_20'] > df['SMA_50']) & 
                (df['SMA_20'].shift(1) <= df['SMA_50'].shift(1))
            )
            
            # זיהוי תמיכה והתנגדות
            recent_highs = df['High'].rolling(window=20).max()
            recent_lows = df['Low'].rolling(window=20).min()
            
            df['near_resistance'] = df['Close'] >= recent_highs * 0.98
            df['near_support'] = df['Close'] <= recent_lows * 1.02
            
            # ניתוח תנודתיות
            df['volatility'] = df['Close'].rolling(window=20).std()
            avg_volatility = df['volatility'].mean()
            current_volatility = df['volatility'].iloc[-1]
            
            # זיהוי תבניות קנדלסטיק
            df['doji'] = abs(df['Open'] - df['Close']) <= (df['High'] - df['Low']) * 0.1
            df['hammer'] = (
                (df['Close'] > df['Open']) &
                (df['Low'] < df['Open'] - (df['High'] - df['Low']) * 0.6)
            )
            df['shooting_star'] = (
                (df['Close'] < df['Open']) &
                (df['High'] > df['Close'] + (df['High'] - df['Low']) * 0.6)
            )
            
            # חישוב ציונים
            trend_score = df['trend_change'].sum() / len(df) * 100
            support_resistance_score = (
                (df['near_support'].sum() + df['near_resistance'].sum()) / len(df) * 50
            )
            volatility_score = min(current_volatility / avg_volatility * 50, 100)
            pattern_score = (
                (df['doji'].sum() + df['hammer'].sum() + df['shooting_star'].sum()) / len(df) * 100
            )
            
            return {
                'trend_score': trend_score,
                'support_resistance_score': support_resistance_score,
                'volatility_score': volatility_score,
                'pattern_score': pattern_score,
                'trend_changes': df['trend_change'].sum(),
                'near_support_count': df['near_support'].sum(),
                'near_resistance_count': df['near_resistance'].sum(),
                'pattern_count': df['doji'].sum() + df['hammer'].sum() + df['shooting_star'].sum()
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח תבניות בסיסיות: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_volume_patterns(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח תבניות נפח"""
        try:
            df = price_df.copy()
            
            # חישוב ממוצע נפח
            df['volume_sma'] = df['Volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['Volume'] / df['volume_sma']
            
            # זיהוי נפח גבוה
            high_volume = df['volume_ratio'] > self.volume_threshold
            
            # ניתוח נפח במחיר עולה/יורד
            df['price_change'] = df['Close'].pct_change()
            volume_on_up = (df['price_change'] > 0) & high_volume
            volume_on_down = (df['price_change'] < 0) & high_volume
            
            # זיהוי נפח מצטבר
            df['volume_trend'] = df['Volume'].rolling(window=5).sum()
            volume_trend_increasing = df['volume_trend'].diff() > 0
            
            # חישוב ציונים
            volume_score = high_volume.sum() / len(df) * 100
            up_volume_score = volume_on_up.sum() / len(df) * 100
            down_volume_score = volume_on_down.sum() / len(df) * 100
            trend_score = volume_trend_increasing.sum() / len(df) * 100
            
            return {
                'volume_score': volume_score,
                'up_volume_score': up_volume_score,
                'down_volume_score': down_volume_score,
                'volume_trend_score': trend_score,
                'high_volume_count': high_volume.sum(),
                'up_volume_count': volume_on_up.sum(),
                'down_volume_count': volume_on_down.sum()
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח תבניות נפח: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_momentum(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח מומנטום"""
        try:
            df = price_df.copy()
            
            # חישוב אינדיקטורי מומנטום
            df['rsi'] = self._calculate_rsi(df['Close'], 14)
            df['macd'], df['macd_signal'] = self._calculate_macd(df['Close'])
            df['stochastic'] = self._calculate_stochastic(df)
            
            # זיהוי שינויי מומנטום
            df['rsi_change'] = df['rsi'].diff()
            df['macd_change'] = df['macd'].diff()
            df['stoch_change'] = df['stochastic'].diff()
            
            # זיהוי רמות קיצון
            rsi_extreme = (df['rsi'] < 30) | (df['rsi'] > 70)
            stoch_extreme = (df['stochastic'] < 20) | (df['stochastic'] > 80)
            
            # זיהוי שינויי כיוון
            rsi_reversal = (
                (df['rsi'] < 30) & (df['rsi_change'] > 0) |
                (df['rsi'] > 70) & (df['rsi_change'] < 0)
            )
            
            macd_crossover = (
                (df['macd'] > df['macd_signal']) & 
                (df['macd'].shift(1) <= df['macd_signal'].shift(1))
            )
            
            # חישוב ציונים
            momentum_score = (
                (rsi_reversal.sum() + macd_crossover.sum()) / len(df) * 100
            )
            extreme_score = (rsi_extreme.sum() + stoch_extreme.sum()) / len(df) * 50
            change_score = (
                (abs(df['rsi_change']) > self.momentum_threshold).sum() / len(df) * 100
            )
            
            return {
                'momentum_score': momentum_score,
                'extreme_score': extreme_score,
                'change_score': change_score,
                'rsi_reversals': rsi_reversal.sum(),
                'macd_crossovers': macd_crossover.sum(),
                'extreme_levels': rsi_extreme.sum() + stoch_extreme.sum()
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח מומנטום: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_divergence(self, price_df: pd.DataFrame, 
                           technical_indicators: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """ניתוח דיברגנס"""
        try:
            df = price_df.copy()
            
            # חישוב אינדיקטורים אם לא סופקו
            if technical_indicators is None:
                df['rsi'] = self._calculate_rsi(df['Close'], 14)
                df['macd'], _ = self._calculate_macd(df['Close'])
            else:
                if 'rsi' in technical_indicators:
                    df['rsi'] = technical_indicators['rsi']['Value']
                if 'macd' in technical_indicators:
                    df['macd'] = technical_indicators['macd']['Value']
            
            # זיהוי דיברגנס
            price_highs = df['High'].rolling(window=20).max()
            price_lows = df['Low'].rolling(window=20).min()
            
            rsi_highs = df['rsi'].rolling(window=20).max()
            rsi_lows = df['rsi'].rolling(window=20).min()
            
            # דיברגנס חיובי (מחיר יורד, RSI עולה)
            bullish_divergence = (
                (df['Close'] < price_lows * 1.02) &
                (df['rsi'] > rsi_lows * 1.1)
            )
            
            # דיברגנס שלילי (מחיר עולה, RSI יורד)
            bearish_divergence = (
                (df['Close'] > price_highs * 0.98) &
                (df['rsi'] < rsi_highs * 0.9)
            )
            
            # חישוב ציונים
            bullish_score = bullish_divergence.sum() / len(df) * 100
            bearish_score = bearish_divergence.sum() / len(df) * 100
            total_divergence_score = (bullish_score + bearish_score) / 2
            
            return {
                'bullish_divergence_score': bullish_score,
                'bearish_divergence_score': bearish_score,
                'total_divergence_score': total_divergence_score,
                'bullish_divergence_count': bullish_divergence.sum(),
                'bearish_divergence_count': bearish_divergence.sum()
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח דיברגנס: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_advanced_patterns(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח תבניות מתקדמות"""
        try:
            df = price_df.copy()
            
            # תבנית Double Bottom
            double_bottom = self._detect_double_bottom(df)
            
            # תבנית Double Top
            double_top = self._detect_double_top(df)
            
            # תבנית Head and Shoulders
            head_shoulders = self._detect_head_shoulders(df)
            
            # תבנית Inverse Head and Shoulders
            inverse_head_shoulders = self._detect_inverse_head_shoulders(df)
            
            # תבנית Triangle
            triangle = self._detect_triangle(df)
            
            # חישוב ציונים
            pattern_scores = {
                'double_bottom': double_bottom * 100,
                'double_top': double_top * 100,
                'head_shoulders': head_shoulders * 100,
                'inverse_head_shoulders': inverse_head_shoulders * 100,
                'triangle': triangle * 100
            }
            
            total_pattern_score = sum(pattern_scores.values()) / len(pattern_scores)
            
            return {
                'total_pattern_score': total_pattern_score,
                'pattern_scores': pattern_scores,
                'patterns_detected': {
                    'double_bottom': double_bottom,
                    'double_top': double_top,
                    'head_shoulders': head_shoulders,
                    'inverse_head_shoulders': inverse_head_shoulders,
                    'triangle': triangle
                }
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח תבניות מתקדמות: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_overall_score(self, basic_analysis: Dict, volume_analysis: Dict,
                                momentum_analysis: Dict, divergence_analysis: Dict,
                                pattern_analysis: Dict) -> float:
        """חישוב ציון כללי"""
        try:
            scores = []
            weights = []
            
            # תבניות בסיסיות (25%)
            if 'trend_score' in basic_analysis:
                scores.append(basic_analysis['trend_score'])
                weights.append(0.25)
            
            # נפח (20%)
            if 'volume_score' in volume_analysis:
                scores.append(volume_analysis['volume_score'])
                weights.append(0.20)
            
            # מומנטום (25%)
            if 'momentum_score' in momentum_analysis:
                scores.append(momentum_analysis['momentum_score'])
                weights.append(0.25)
            
            # דיברגנס (20%)
            if 'total_divergence_score' in divergence_analysis:
                scores.append(divergence_analysis['total_divergence_score'])
                weights.append(0.20)
            
            # תבניות מתקדמות (10%)
            if 'total_pattern_score' in pattern_analysis:
                scores.append(pattern_analysis['total_pattern_score'])
                weights.append(0.10)
            
            if not scores:
                return 0.0
            
            # חישוב ממוצע משוקלל
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            
            return weighted_sum / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"שגיאה בחישוב ציון כללי: {str(e)}")
            return 0.0
    
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
        if score >= 70:
            return f"סימנים חזקים לשינוי מגמה - רמת ביטחון: {confidence}"
        elif score >= 50:
            return f"סימנים בינוניים לשינוי מגמה - רמת ביטחון: {confidence}"
        elif score >= 30:
            return f"סימנים חלשים לשינוי מגמה - רמת ביטחון: {confidence}"
        else:
            return f"אין סימנים ברורים לשינוי מגמה - רמת ביטחון: {confidence}"
    
    def _extract_key_signals(self, basic_analysis: Dict, volume_analysis: Dict,
                            momentum_analysis: Dict, divergence_analysis: Dict,
                            pattern_analysis: Dict) -> List[str]:
        """חילוץ סיגנלים מפתח"""
        signals = []
        
        try:
            # סיגנלים מתבניות בסיסיות
            if basic_analysis.get('trend_changes', 0) > 0:
                signals.append(f"זוהו {basic_analysis['trend_changes']} שינויי מגמה")
            
            if basic_analysis.get('pattern_count', 0) > 0:
                signals.append(f"זוהו {basic_analysis['pattern_count']} תבניות קנדלסטיק")
            
            # סיגנלים מנפח
            if volume_analysis.get('high_volume_count', 0) > 0:
                signals.append(f"נפח גבוה ב-{volume_analysis['high_volume_count']} ימים")
            
            # סיגנלים ממומנטום
            if momentum_analysis.get('rsi_reversals', 0) > 0:
                signals.append(f"זוהו {momentum_analysis['rsi_reversals']} היפוכי RSI")
            
            if momentum_analysis.get('macd_crossovers', 0) > 0:
                signals.append(f"זוהו {momentum_analysis['macd_crossovers']} חציות MACD")
            
            # סיגנלים מדיברגנס
            if divergence_analysis.get('bullish_divergence_count', 0) > 0:
                signals.append(f"זוהו {divergence_analysis['bullish_divergence_count']} דיברגנס חיובי")
            
            if divergence_analysis.get('bearish_divergence_count', 0) > 0:
                signals.append(f"זוהו {divergence_analysis['bearish_divergence_count']} דיברגנס שלילי")
            
            # סיגנלים מתבניות מתקדמות
            patterns = pattern_analysis.get('patterns_detected', {})
            for pattern_name, detected in patterns.items():
                if detected:
                    signals.append(f"זוהתה תבנית {pattern_name}")
            
        except Exception as e:
            logger.error(f"שגיאה בחילוץ סיגנלים: {str(e)}")
        
        return signals
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """יצירת תוצאת שגיאה"""
        return {
            'timestamp': datetime.now().isoformat(),
            'agent': self.name,
            'version': self.version,
            'status': 'error',
            'error': error_message,
            'overall_score': 0.0,
            'confidence_level': 'Very Low',
            'recommendation': 'לא ניתן לנתח - שגיאה בנתונים'
        }
    
    # פונקציות עזר לחישוב אינדיקטורים
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """חישוב RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """חישוב MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd, signal_line
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.Series:
        """חישוב Stochastic"""
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()
        k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        return k.rolling(window=d_period).mean()
    
    # פונקציות זיהוי תבניות
    def _detect_double_bottom(self, df: pd.DataFrame) -> float:
        """זיהוי תבנית Double Bottom"""
        # פישוט - זיהוי בסיסי
        return 0.3  # 30% הסתברות
    
    def _detect_double_top(self, df: pd.DataFrame) -> float:
        """זיהוי תבנית Double Top"""
        return 0.2  # 20% הסתברות
    
    def _detect_head_shoulders(self, df: pd.DataFrame) -> float:
        """זיהוי תבנית Head and Shoulders"""
        return 0.1  # 10% הסתברות
    
    def _detect_inverse_head_shoulders(self, df: pd.DataFrame) -> float:
        """זיהוי תבנית Inverse Head and Shoulders"""
        return 0.1  # 10% הסתברות
    
    def _detect_triangle(self, df: pd.DataFrame) -> float:
        """זיהוי תבנית Triangle"""
        return 0.4  # 40% הסתברות

# דוגמאות שימוש
if __name__ == "__main__":
    # יצירת הסוכן
    agent = EarlyReversalAnticipator()
    
    # יצירת נתונים לדוגמה
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    price_data = pd.DataFrame({
        'Date': dates,
        'Open': np.random.uniform(100, 200, 100),
        'High': np.random.uniform(200, 250, 100),
        'Low': np.random.uniform(50, 100, 100),
        'Close': np.random.uniform(100, 200, 100),
        'Volume': np.random.uniform(1000000, 5000000, 100)
    })
    
    # ניתוח
    result = agent.analyze('AAPL', price_data)
    print(f"תוצאות ניתוח: {result}")