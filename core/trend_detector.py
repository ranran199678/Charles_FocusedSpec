"""
TrendDetector - מנתח מגמות מתקדם
=================================

סוכן מתקדם לזיהוי מגמות עם יכולות:
- זיהוי מגמות מתקדם רב-ממדי
- ניתוח מגמות לפי זמן
- ולידציה של מגמות
- זיהוי שינויי מגמה
- ניתוח עוצמת מגמה
- אינדיקטורים טכניים מתקדמים
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.base.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

@dataclass
class TrendMetrics:
    """מבנה נתונים למדדי מגמה"""
    trend_direction: str
    trend_strength: float
    trend_confidence: float
    trend_duration: int
    trend_validation: Dict
    momentum_indicators: Dict
    volume_analysis: Dict
    support_resistance: Dict

class TrendDetector(BaseAgent):
    """
    סוכן מתקדם לזיהוי מגמות
    
    תכונות מתקדמות:
    - זיהוי מגמות מתקדם רב-ממדי
    - ניתוח מגמות לפי זמן
    - ולידציה של מגמות
    - זיהוי שינויי מגמה
    - ניתוח עוצמת מגמה
    - אינדיקטורים טכניים מתקדמים
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.short_window = cfg.get("short_window", 20)
        self.long_window = cfg.get("long_window", 50)
        self.volume_threshold = cfg.get("volume_threshold", 1.1)
        self.trend_threshold = cfg.get("trend_threshold", 0.02)  # 2% לשינוי מגמה
        self.confirmation_period = cfg.get("confirmation_period", 5)  # ימים לאישור מגמה
        
        # משקלים לניתוח
        self.weights = {
            'price_trend': 0.35,
            'volume_confirmation': 0.25,
            'momentum_indicators': 0.20,
            'support_resistance': 0.15,
            'trend_validation': 0.05
        }
        
        # סוגי מגמות
        self.trend_types = {
            'strong_uptrend': 'מגמה עולה חזקה',
            'uptrend': 'מגמה עולה',
            'weak_uptrend': 'מגמה עולה חלשה',
            'neutral': 'מגמה ניטרלית',
            'weak_downtrend': 'מגמה יורדת חלשה',
            'downtrend': 'מגמה יורדת',
            'strong_downtrend': 'מגמה יורדת חזקה'
        }
        
        self.log("TrendDetector initialized with advanced configuration")

    def _calculate_moving_averages(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """חישוב ממוצעים נעים מתקדמים"""
        df = price_df.copy()
        
        # ממוצעים נעים בסיסיים
        df['MA_short'] = df['close'].rolling(window=self.short_window).mean()
        df['MA_long'] = df['close'].rolling(window=self.long_window).mean()
        df['MA_diff'] = df['MA_short'] - df['MA_long']
        df['MA_ratio'] = df['MA_short'] / df['MA_long']
        
        # ממוצעים נעים מעריכיים
        df['EMA_short'] = df['close'].ewm(span=self.short_window).mean()
        df['EMA_long'] = df['close'].ewm(span=self.long_window).mean()
        df['EMA_diff'] = df['EMA_short'] - df['EMA_long']
        
        # ממוצעים נעים משוקללים
        df['WMA_short'] = df['close'].rolling(window=self.short_window).apply(
            lambda x: np.average(x, weights=np.arange(1, len(x) + 1))
        )
        df['WMA_long'] = df['close'].rolling(window=self.long_window).apply(
            lambda x: np.average(x, weights=np.arange(1, len(x) + 1))
        )
        
        return df

    def _analyze_price_trend(self, df: pd.DataFrame) -> Dict:
        """ניתוח מגמת מחיר מתקדם"""
        if len(df) < self.long_window:
            return {'trend': 'insufficient_data', 'strength': 0, 'confidence': 0}
        
        # חישוב שינויי מחיר
        df['price_change'] = df['close'].pct_change()
        df['price_change_ma'] = df['price_change'].rolling(window=10).mean()
        
        # ניתוח מגמה לפי ממוצעים נעים
        current_ma_diff = df['MA_diff'].iloc[-1]
        current_ma_ratio = df['MA_ratio'].iloc[-1]
        current_ema_diff = df['EMA_diff'].iloc[-1]
        
        # חישוב עוצמת מגמה
        ma_trend_strength = abs(current_ma_diff / df['close'].iloc[-1]) * 100
        ema_trend_strength = abs(current_ema_diff / df['close'].iloc[-1]) * 100
        
        # זיהוי כיוון מגמה
        if current_ma_diff > 0 and current_ema_diff > 0:
            if ma_trend_strength > 5:
                trend = 'strong_uptrend'
                strength = min(100, ma_trend_strength * 20)
            else:
                trend = 'uptrend'
                strength = min(100, ma_trend_strength * 15)
        elif current_ma_diff < 0 and current_ema_diff < 0:
            if ma_trend_strength > 5:
                trend = 'strong_downtrend'
                strength = min(100, ma_trend_strength * 20)
            else:
                trend = 'downtrend'
                strength = min(100, ma_trend_strength * 15)
        else:
            trend = 'neutral'
            strength = 50
        
        # חישוב ביטחון במגמה
        recent_ma_diffs = df['MA_diff'].tail(10)
        trend_consistency = (recent_ma_diffs > 0).mean() if trend.startswith('up') else (recent_ma_diffs < 0).mean()
        confidence = trend_consistency * 100
        
        return {
            'trend': trend,
            'strength': strength,
            'confidence': confidence,
            'ma_diff': current_ma_diff,
            'ema_diff': current_ema_diff,
            'trend_consistency': trend_consistency
        }

    def _analyze_volume_confirmation(self, df: pd.DataFrame, trend: str) -> Dict:
        """ניתוח אישור נפח למגמה"""
        if 'volume' not in df.columns:
            return {'volume_confirmed': False, 'volume_score': 50, 'volume_pattern': 'no_data'}
        
        volume = df['volume']
        current_volume = volume.iloc[-1]
        avg_volume = volume.rolling(window=self.short_window).mean().iloc[-1]
        
        # יחס נפח נוכחי לממוצע
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # ניתוח נפח לפי מגמה
        if trend.startswith('up'):
            # במגמה עולה - נפח גבוה מאשר את המגמה
            volume_confirmed = volume_ratio > self.volume_threshold
            volume_score = min(100, volume_ratio * 50)
        elif trend.startswith('down'):
            # במגמה יורדת - נפח גבוה מאשר את המגמה
            volume_confirmed = volume_ratio > self.volume_threshold
            volume_score = min(100, volume_ratio * 50)
        else:
            volume_confirmed = True
            volume_score = 50
        
        # זיהוי דפוסי נפח
        if volume_ratio > 2.0:
            volume_pattern = 'נפח גבוה מאוד'
        elif volume_ratio > 1.5:
            volume_pattern = 'נפח גבוה'
        elif volume_ratio > 1.2:
            volume_pattern = 'נפח מעל הממוצע'
        elif volume_ratio < 0.5:
            volume_pattern = 'נפח נמוך מאוד'
        else:
            volume_pattern = 'נפח רגיל'
        
        return {
            'volume_confirmed': volume_confirmed,
            'volume_score': volume_score,
            'volume_ratio': volume_ratio,
            'volume_pattern': volume_pattern
        }

    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict:
        """חישוב אינדיקטורי מומנטום"""
        if len(df) < 14:
            return {'rsi': 50, 'macd': 0, 'momentum_score': 50}
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # MACD
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        macd_histogram = macd_line - signal_line
        
        current_macd = macd_histogram.iloc[-1]
        
        # Stochastic
        low_min = df['low'].rolling(window=14).min()
        high_max = df['high'].rolling(window=14).max()
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=3).mean()
        
        current_stoch_k = k_percent.iloc[-1]
        current_stoch_d = d_percent.iloc[-1]
        
        # חישוב ציון מומנטום
        momentum_score = 50
        
        # RSI contribution
        if current_rsi > 70:
            momentum_score += 20
        elif current_rsi > 60:
            momentum_score += 10
        elif current_rsi < 30:
            momentum_score -= 20
        elif current_rsi < 40:
            momentum_score -= 10
        
        # MACD contribution
        if current_macd > 0:
            momentum_score += 15
        else:
            momentum_score -= 15
        
        # Stochastic contribution
        if current_stoch_k > 80 and current_stoch_d > 80:
            momentum_score -= 10
        elif current_stoch_k < 20 and current_stoch_d < 20:
            momentum_score += 10
        
        return {
            'rsi': current_rsi,
            'macd': current_macd,
            'stoch_k': current_stoch_k,
            'stoch_d': current_stoch_d,
            'momentum_score': max(0, min(100, momentum_score))
        }

    def _identify_support_resistance(self, df: pd.DataFrame) -> Dict:
        """זיהוי רמות תמיכה והתנגדות"""
        if len(df) < 20:
            return {'support': None, 'resistance': None, 'levels_score': 50}
        
        # חישוב רמות לפי ממוצעים נעים
        current_price = df['close'].iloc[-1]
        ma_short = df['MA_short'].iloc[-1]
        ma_long = df['MA_long'].iloc[-1]
        
        # רמות תמיכה
        support_levels = [
            ma_short,
            ma_long,
            df['low'].tail(20).min()
        ]
        
        # רמות התנגדות
        resistance_levels = [
            ma_short,
            ma_long,
            df['high'].tail(20).max()
        ]
        
        # זיהוי הרמה הקרובה ביותר
        closest_support = min(support_levels, key=lambda x: abs(current_price - x))
        closest_resistance = min(resistance_levels, key=lambda x: abs(current_price - x))
        
        # חישוב מרחקים
        support_distance = ((current_price - closest_support) / current_price) * 100
        resistance_distance = ((closest_resistance - current_price) / current_price) * 100
        
        # ציון רמות
        if support_distance < 2:  # קרוב לתמיכה
            levels_score = 20
        elif resistance_distance < 2:  # קרוב להתנגדות
            levels_score = 80
        else:
            levels_score = 50
        
        return {
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'closest_support': closest_support,
            'closest_resistance': closest_resistance,
            'support_distance': support_distance,
            'resistance_distance': resistance_distance,
            'levels_score': levels_score
        }

    def _validate_trend(self, df: pd.DataFrame, trend: str) -> Dict:
        """ולידציה של מגמה"""
        if len(df) < self.confirmation_period:
            return {'validated': False, 'validation_score': 0}
        
        # בדיקת עקביות המגמה
        recent_ma_diffs = df['MA_diff'].tail(self.confirmation_period)
        
        if trend.startswith('up'):
            consistency = (recent_ma_diffs > 0).mean()
        elif trend.startswith('down'):
            consistency = (recent_ma_diffs < 0).mean()
        else:
            consistency = 0.5
        
        # בדיקת עוצמת המגמה
        trend_strength = abs(df['MA_diff'].iloc[-1] / df['close'].iloc[-1]) * 100
        
        # ציון ולידציה
        validation_score = consistency * 100
        
        return {
            'validated': consistency > 0.7,
            'validation_score': validation_score,
            'consistency': consistency,
            'trend_strength': trend_strength
        }

    def _calculate_composite_score(self, price_trend: Dict, volume_analysis: Dict, 
                                 momentum: Dict, support_resistance: Dict, 
                                 validation: Dict) -> int:
        """חישוב ציון מורכב"""
        scores = {}
        
        # ציון מגמת מחיר
        scores['price_trend'] = price_trend.get('strength', 50)
        
        # ציון אישור נפח
        scores['volume_confirmation'] = volume_analysis.get('volume_score', 50)
        
        # ציון מומנטום
        scores['momentum_indicators'] = momentum.get('momentum_score', 50)
        
        # ציון רמות תמיכה/התנגדות
        scores['support_resistance'] = support_resistance.get('levels_score', 50)
        
        # ציון ולידציה
        scores['trend_validation'] = validation.get('validation_score', 50)
        
        # חישוב ציון מורכב
        composite_score = sum(scores[component] * self.weights[component] 
                            for component in scores.keys())
        
        return int(composite_score)

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח מגמות מתקדם
        
        Args:
            symbol: סימול המניה
            price_df: DataFrame עם נתוני מחיר
            
        Returns:
            Dict עם score, explanation, details
        """
        try:
            if price_df is None or price_df.empty:
                return {
                    "score": 50,
                    "explanation": "אין נתוני מחיר זמינים לניתוח מגמות",
                    "details": {}
                }
            
            if len(price_df) < self.long_window:
                return {
                    "score": 50,
                    "explanation": "אין מספיק נתונים לניתוח מגמות מתקדם",
                    "details": {}
                }
            
            # חישוב אינדיקטורים
            df = self._calculate_moving_averages(price_df)
            
            # ניתוח מגמת מחיר
            price_trend = self._analyze_price_trend(df)
            
            # ניתוח אישור נפח
            volume_analysis = self._analyze_volume_confirmation(df, price_trend['trend'])
            
            # אינדיקטורי מומנטום
            momentum = self._calculate_momentum_indicators(df)
            
            # רמות תמיכה/התנגדות
            support_resistance = self._identify_support_resistance(df)
            
            # ולידציה
            validation = self._validate_trend(df, price_trend['trend'])
            
            # חישוב ציון מורכב
            score = self._calculate_composite_score(
                price_trend, volume_analysis, momentum, 
                support_resistance, validation
            )
            
            # יצירת הסבר
            explanation_parts = []
            trend_name = self.trend_types.get(price_trend['trend'], price_trend['trend'])
            explanation_parts.append(f"מגמה: {trend_name}")
            explanation_parts.append(f"עוצמה: {price_trend['strength']:.1f}")
            
            if volume_analysis.get('volume_confirmed'):
                explanation_parts.append("נפח מאשר")
            
            if momentum.get('momentum_score', 50) > 60:
                explanation_parts.append("מומנטום חיובי")
            elif momentum.get('momentum_score', 50) < 40:
                explanation_parts.append("מומנטום שלילי")
            
            explanation = " | ".join(explanation_parts)
            
            # יצירת פרטים מפורטים
            details = {
                'symbol': symbol,
                'price_trend': price_trend,
                'volume_analysis': volume_analysis,
                'momentum_indicators': momentum,
                'support_resistance': support_resistance,
                'trend_validation': validation,
                'analysis_date': datetime.now().isoformat(),
                'data_points': len(price_df)
            }
            
            return {
                "score": score,
                "explanation": explanation,
                "details": details
            }
            
        except Exception as e:
            self.log(f"שגיאה בניתוח מגמות עבור {symbol}: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח מגמות: {str(e)}",
                "details": {}
            }
