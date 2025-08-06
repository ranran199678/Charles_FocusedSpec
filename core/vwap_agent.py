"""
VWAPAgent - מנתח VWAP מתקדם
============================

סוכן מתקדם לניתוח VWAP (Volume Weighted Average Price) עם יכולות:
- ניתוח VWAP רב-ממדי
- זיהוי דפוסי מחיר יחסית ל-VWAP
- ניתוח נפח ומחיר
- זיהוי רמות תמיכה והתנגדות
- ניתוח דפוסי מסחר
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
class VWAPMetrics:
    """מבנה נתונים למדדי VWAP"""
    vwap_value: float
    price_vs_vwap: float
    price_vwap_ratio: float
    vwap_trend: str
    volume_profile: Dict
    support_resistance: Dict
    trading_patterns: List[Dict]
    momentum_indicators: Dict

class VWAPAgent(BaseAgent):
    """
    סוכן מתקדם לניתוח VWAP
    
    תכונות מתקדמות:
    - ניתוח VWAP רב-ממדי
    - זיהוי דפוסי מחיר יחסית ל-VWAP
    - ניתוח נפח ומחיר
    - זיהוי רמות תמיכה והתנגדות
    - ניתוח דפוסי מסחר
    - אינדיקטורים טכניים מתקדמים
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.zscore_threshold = cfg.get("zscore_threshold", 1.5)
        self.vwap_period = cfg.get("vwap_period", 20)  # תקופה לחישוב VWAP
        self.volume_threshold = cfg.get("volume_threshold", 1.2)  # סף נפח
        self.trend_period = cfg.get("trend_period", 10)  # תקופה לניתוח מגמה
        
        # פרמטרים למצב לייב ומגמות מתקדמות
        self.anchor_idx = cfg.get("anchored_event_index", None)
        self.weight_sync = cfg.get("weight_sync", 0.7)
        self.weight_avwap = cfg.get("weight_avwap", 0.3)
        self.quality_threshold = cfg.get("quality_threshold", 0.02)
        
        # משקלים לניתוח
        self.weights = {
            'price_vs_vwap': 0.30,
            'volume_analysis': 0.25,
            'trend_analysis': 0.20,
            'support_resistance': 0.15,
            'trading_patterns': 0.10
        }
        
        # רמות חשיבות
        self.importance_levels = {
            'critical': 'קריטי',
            'high': 'גבוה',
            'medium': 'בינוני',
            'low': 'נמוך'
        }
        
        self.log("VWAPAgent initialized with advanced configuration")

    def _calculate_vwap(self, price_df: pd.DataFrame) -> pd.Series:
        """חישוב VWAP מתקדם"""
        if len(price_df) < self.vwap_period:
            return pd.Series([price_df['close'].iloc[-1]] * len(price_df), index=price_df.index)
        
        # חישוב Typical Price
        if 'high' in price_df.columns and 'low' in price_df.columns:
            typical_price = (price_df['high'] + price_df['low'] + price_df['close']) / 3
        else:
            typical_price = price_df['close']
        
        # חישוב Volume Weighted Average Price
        volume = price_df['volume'] if 'volume' in price_df.columns else pd.Series([1] * len(price_df))
        
        # VWAP מצטבר
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        
        return vwap

    def _calc_vwap_multi_timeframe(self, price_df: pd.DataFrame) -> Dict[str, pd.Series]:
        """חישוב VWAP במספר טווחי זמן"""
        try:
            vwap_daily = self._calc_vwap(price_df, window=1)
            vwap_weekly = self._calc_vwap(price_df, window=5)
            vwap_monthly = self._calc_vwap(price_df, window=21)
            
            return {
                'daily': vwap_daily,
                'weekly': vwap_weekly,
                'monthly': vwap_monthly
            }
        except Exception as e:
            self.log(f"שגיאה בחישוב VWAP רב-טווחי: {e}")
            return {}

    def _calc_anchored_vwap(self, price_df: pd.DataFrame, anchor_idx: int) -> pd.Series:
        """חישוב Anchored VWAP"""
        try:
            if anchor_idx >= len(price_df):
                return pd.Series([None] * len(price_df), index=price_df.index)
            
            # חישוב VWAP מהנקודה המסוימת
            anchor_price = price_df.iloc[anchor_idx]
            anchor_volume = price_df.iloc[anchor_idx]['volume'] if 'volume' in price_df.columns else 1
            
            # חישוב Typical Price מהנקודה המסוימת
            if 'high' in price_df.columns and 'low' in price_df.columns:
                typical_price = (price_df['high'] + price_df['low'] + price_df['close']) / 3
            else:
                typical_price = price_df['close']
            
            # חישוב VWAP מצטבר מהנקודה המסוימת
            volume = price_df['volume'] if 'volume' in price_df.columns else pd.Series([1] * len(price_df))
            
            # חישוב מצטבר רק מהנקודה המסוימת
            cumulative_tp_vol = (typical_price * volume).iloc[anchor_idx:].cumsum()
            cumulative_vol = volume.iloc[anchor_idx:].cumsum()
            
            anchored_vwap = cumulative_tp_vol / cumulative_vol
            
            # מילוי ערכים לפני הנקודה המסוימת
            result = pd.Series([None] * len(price_df), index=price_df.index)
            result.iloc[anchor_idx:] = anchored_vwap
            
            return result
            
        except Exception as e:
            self.log(f"שגיאה בחישוב Anchored VWAP: {e}")
            return pd.Series([None] * len(price_df), index=price_df.index)

    def _analyze_vwap_breakouts(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח פריצות VWAP מתקדם"""
        try:
            n = len(price_df)
            if n < 21:
                return {
                    'sync_breakout': False,
                    'anchored_signal': False,
                    'breakout_type': 'none',
                    'breakout_quality': 0.0,
                    'vwap_levels': {}
                }
            
            # חישוב VWAP בכמה טווחים
            vwap_levels = self._calc_vwap_multi_timeframe(price_df)
            
            # Anchored VWAP
            avwap = None
            if self.anchor_idx is not None and self.anchor_idx < n:
                avwap = self._calc_anchored_vwap(price_df, self.anchor_idx)
            
            current_price = price_df["close"].iloc[-1]
            
            # בדיקת פריצה מסונכרנת
            vwap_sync_break = (
                current_price > vwap_levels.get('daily', pd.Series()).iloc[-1] and 
                current_price > vwap_levels.get('weekly', pd.Series()).iloc[-1] and 
                current_price > vwap_levels.get('monthly', pd.Series()).iloc[-1]
            )
            
            # בדיקת סיגנל Anchored
            avwap_signal = False
            if avwap is not None and avwap.iloc[-1] is not None:
                avwap_signal = current_price > avwap.iloc[-1]
            
            # חישוב איכות פריצה
            vwap_values = {
                'daily': vwap_levels.get('daily', pd.Series()).iloc[-1],
                'weekly': vwap_levels.get('weekly', pd.Series()).iloc[-1],
                'monthly': vwap_levels.get('monthly', pd.Series()).iloc[-1],
                'anchored': avwap.iloc[-1] if avwap is not None else None
            }
            
            # חישוב מרחקים מ-VWAP
            distances = {}
            for name, level in vwap_values.items():
                if level is not None:
                    distances[name] = (current_price - level) / level
            
            # איכות פריצה - ממוצע המרחקים
            valid_distances = [d for d in distances.values() if d > 0]
            breakout_quality = np.mean(valid_distances) if valid_distances else 0.0
            
            # זיהוי סוג פריצה
            if vwap_sync_break and avwap_signal:
                breakout_type = 'strong_sync'
            elif vwap_sync_break:
                breakout_type = 'sync'
            elif avwap_signal:
                breakout_type = 'anchored'
            elif any(d > 0 for d in distances.values()):
                breakout_type = 'partial'
            else:
                breakout_type = 'none'
            
            return {
                'sync_breakout': vwap_sync_break,
                'anchored_signal': avwap_signal,
                'breakout_type': breakout_type,
                'breakout_quality': breakout_quality,
                'vwap_levels': vwap_values,
                'distances': distances
            }
            
        except Exception as e:
            self.log(f"שגיאה בניתוח פריצות VWAP: {e}")
            return {
                'sync_breakout': False,
                'anchored_signal': False,
                'breakout_type': 'none',
                'breakout_quality': 0.0,
                'vwap_levels': {}
            }

    def _analyze_price_vs_vwap(self, price_df: pd.DataFrame, vwap: pd.Series) -> Dict:
        """ניתוח מחיר יחסית ל-VWAP"""
        current_price = price_df['close'].iloc[-1]
        current_vwap = vwap.iloc[-1]
        
        # יחס מחיר ל-VWAP
        price_vwap_ratio = current_price / current_vwap if current_vwap > 0 else 1.0
        
        # מרחק מה-VWAP באחוזים
        price_vs_vwap_pct = ((current_price - current_vwap) / current_vwap) * 100 if current_vwap > 0 else 0
        
        # זיהוי מיקום יחסית ל-VWAP
        if price_vwap_ratio > 1.05:
            position = 'מעל VWAP'
            signal = 'bullish'
        elif price_vwap_ratio < 0.95:
            position = 'מתחת ל-VWAP'
            signal = 'bearish'
        else:
            position = 'קרוב ל-VWAP'
            signal = 'neutral'
        
        # חישוב Z-score
        price_distances = (price_df['close'] - vwap) / vwap
        z_score = price_distances.iloc[-1] if len(price_distances) > 0 else 0
        
        return {
            'current_price': current_price,
            'current_vwap': current_vwap,
            'price_vwap_ratio': price_vwap_ratio,
            'price_vs_vwap_pct': price_vs_vwap_pct,
            'position': position,
            'signal': signal,
            'z_score': z_score
        }

    def _analyze_volume_profile(self, price_df: pd.DataFrame, vwap: pd.Series) -> Dict:
        """ניתוח פרופיל נפח"""
        if 'volume' not in price_df.columns:
            return {'volume_analysis': 'לא זמין', 'volume_score': 50}
        
        volume = price_df['volume']
        current_volume = volume.iloc[-1]
        avg_volume = volume.rolling(window=self.vwap_period).mean().iloc[-1]
        
        # יחס נפח נוכחי לממוצע
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # ניתוח נפח לפי מיקום יחסית ל-VWAP
        above_vwap_volume = volume[price_df['close'] > vwap].sum()
        below_vwap_volume = volume[price_df['close'] < vwap].sum()
        
        volume_bias = above_vwap_volume / (above_vwap_volume + below_vwap_volume) if (above_vwap_volume + below_vwap_volume) > 0 else 0.5
        
        # זיהוי דפוסי נפח
        if volume_ratio > self.volume_threshold:
            volume_pattern = 'נפח גבוה'
            volume_signal = 'positive'
        elif volume_ratio < 1 / self.volume_threshold:
            volume_pattern = 'נפח נמוך'
            volume_signal = 'negative'
        else:
            volume_pattern = 'נפח רגיל'
            volume_signal = 'neutral'
        
        return {
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'volume_bias': volume_bias,
            'volume_pattern': volume_pattern,
            'volume_signal': volume_signal
        }

    def _analyze_vwap_trend(self, vwap: pd.Series) -> Dict:
        """ניתוח מגמת VWAP"""
        if len(vwap) < self.trend_period:
            return {'trend': 'לא מספיק נתונים', 'trend_strength': 0, 'trend_score': 50}
        
        # חישוב מגמה
        recent_vwap = vwap[-self.trend_period:]
        vwap_change = (recent_vwap.iloc[-1] - recent_vwap.iloc[0]) / recent_vwap.iloc[0]
        
        # זיהוי כיוון מגמה
        if vwap_change > 0.02:  # עלייה של יותר מ-2%
            trend = 'עולה'
            trend_signal = 'bullish'
        elif vwap_change < -0.02:  # ירידה של יותר מ-2%
            trend = 'יורדת'
            trend_signal = 'bearish'
        else:
            trend = 'יציבה'
            trend_signal = 'neutral'
        
        # חישוב עוצמת מגמה
        trend_strength = abs(vwap_change) * 100
        
        return {
            'trend': trend,
            'trend_change': vwap_change,
            'trend_strength': trend_strength,
            'trend_signal': trend_signal
        }

    def _identify_support_resistance(self, price_df: pd.DataFrame, vwap: pd.Series) -> Dict:
        """זיהוי רמות תמיכה והתנגדות"""
        if len(price_df) < 20:
            return {'support': None, 'resistance': None, 'levels_score': 50}
        
        # חישוב רמות VWAP
        vwap_high = vwap.max()
        vwap_low = vwap.min()
        current_vwap = vwap.iloc[-1]
        
        # זיהוי רמות תמיכה והתנגדות
        price_high = price_df['high'].max()
        price_low = price_df['low'].min()
        current_price = price_df['close'].iloc[-1]
        
        # רמות תמיכה
        support_levels = [
            vwap_low,
            price_low,
            current_vwap * 0.95  # 5% מתחת ל-VWAP הנוכחי
        ]
        
        # רמות התנגדות
        resistance_levels = [
            vwap_high,
            price_high,
            current_vwap * 1.05  # 5% מעל ל-VWAP הנוכחי
        ]
        
        # זיהוי הרמה הקרובה ביותר
        closest_support = min(support_levels, key=lambda x: abs(current_price - x))
        closest_resistance = min(resistance_levels, key=lambda x: abs(current_price - x))
        
        return {
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'closest_support': closest_support,
            'closest_resistance': closest_resistance,
            'support_distance': ((current_price - closest_support) / current_price) * 100,
            'resistance_distance': ((closest_resistance - current_price) / current_price) * 100
        }

    def _detect_trading_patterns(self, price_df: pd.DataFrame, vwap: pd.Series) -> List[Dict]:
        """זיהוי דפוסי מסחר"""
        patterns = []
        
        if len(price_df) < 10:
            return patterns
        
        # דפוס 1: מחיר מעל VWAP עם נפח גבוה
        recent_prices = price_df['close'][-5:]
        recent_vwap = vwap[-5:]
        recent_volume = price_df['volume'][-5:] if 'volume' in price_df.columns else pd.Series([1] * 5)
        
        above_vwap_count = sum(recent_prices > recent_vwap)
        high_volume_count = sum(recent_volume > recent_volume.mean() * 1.2)
        
        if above_vwap_count >= 4 and high_volume_count >= 3:
            patterns.append({
                'pattern': 'מחיר מעל VWAP עם נפח גבוה',
                'signal': 'bullish',
                'confidence': 'high'
            })
        
        # דפוס 2: מחיר מתחת ל-VWAP עם נפח נמוך
        below_vwap_count = sum(recent_prices < recent_vwap)
        low_volume_count = sum(recent_volume < recent_volume.mean() * 0.8)
        
        if below_vwap_count >= 4 and low_volume_count >= 3:
            patterns.append({
                'pattern': 'מחיר מתחת ל-VWAP עם נפח נמוך',
                'signal': 'bearish',
                'confidence': 'medium'
            })
        
        # דפוס 3: חזרה ל-VWAP
        price_distances = (price_df['close'] - vwap) / vwap
        recent_distances = price_distances[-5:]
        
        if abs(recent_distances.iloc[-1]) < 0.01 and abs(recent_distances.iloc[0]) > 0.03:
            patterns.append({
                'pattern': 'חזרה ל-VWAP',
                'signal': 'neutral',
                'confidence': 'medium'
            })
        
        return patterns

    def _calculate_momentum_indicators(self, price_df: pd.DataFrame, vwap: pd.Series) -> Dict:
        """חישוב אינדיקטורי מומנטום"""
        if len(price_df) < 14:
            return {'rsi': 50, 'momentum': 0, 'momentum_score': 50}
        
        # RSI
        delta = price_df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # מומנטום יחסית ל-VWAP
        price_momentum = (price_df['close'].iloc[-1] - price_df['close'].iloc[-5]) / price_df['close'].iloc[-5]
        vwap_momentum = (vwap.iloc[-1] - vwap.iloc[-5]) / vwap.iloc[-5]
        relative_momentum = price_momentum - vwap_momentum
        
        return {
            'rsi': current_rsi,
            'price_momentum': price_momentum,
            'vwap_momentum': vwap_momentum,
            'relative_momentum': relative_momentum
        }

    def _calculate_composite_score(self, price_analysis: Dict, volume_analysis: Dict, 
                                 trend_analysis: Dict, support_resistance: Dict, 
                                 patterns: List[Dict], momentum: Dict) -> int:
        """חישוב ציון מורכב"""
        scores = {}
        
        # ציון מחיר vs VWAP
        z_score = abs(price_analysis['z_score'])
        if z_score > 2.0:
            price_score = 100
        elif z_score > 1.5:
            price_score = 80
        elif z_score > 1.0:
            price_score = 60
        else:
            price_score = 40
        scores['price_vs_vwap'] = price_score
        
        # ציון ניתוח נפח
        if volume_analysis.get('volume_signal') == 'positive':
            volume_score = 80
        elif volume_analysis.get('volume_signal') == 'negative':
            volume_score = 20
        else:
            volume_score = 50
        scores['volume_analysis'] = volume_score
        
        # ציון מגמה
        if trend_analysis.get('trend_signal') == 'bullish':
            trend_score = 80
        elif trend_analysis.get('trend_signal') == 'bearish':
            trend_score = 20
        else:
            trend_score = 50
        scores['trend_analysis'] = trend_score
        
        # ציון רמות תמיכה/התנגדות
        support_distance = support_resistance.get('support_distance', 0)
        resistance_distance = support_resistance.get('resistance_distance', 0)
        
        if support_distance < 2:  # קרוב לתמיכה
            levels_score = 20
        elif resistance_distance < 2:  # קרוב להתנגדות
            levels_score = 80
        else:
            levels_score = 50
        scores['support_resistance'] = levels_score
        
        # ציון דפוסי מסחר
        if patterns:
            pattern_score = 70
        else:
            pattern_score = 50
        scores['trading_patterns'] = pattern_score
        
        # חישוב ציון מורכב
        composite_score = sum(scores[component] * self.weights[component] 
                            for component in scores.keys())
        
        return int(composite_score)

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח VWAP מתקדם
        
        Args:
            symbol: סימול המניה
            price_df: DataFrame עם נתוני מחיר
            
        Returns:
            Dict עם score, explanation, details
        """
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=90)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            if len(price_df) < 20:
                return self.fallback()
            
            # חישוב VWAP
            vwap = self._calculate_vwap(price_df)
            
            # ניתוח פריצות VWAP מתקדם
            breakout_analysis = self._analyze_vwap_breakouts(price_df)
            
            # ניתוח מחיר vs VWAP
            price_analysis = self._analyze_price_vs_vwap(price_df, vwap)
            
            # ניתוח נפח
            volume_analysis = self._analyze_volume_profile(price_df, vwap)
            
            # ניתוח מגמה
            trend_analysis = self._analyze_vwap_trend(vwap)
            
            # זיהוי רמות תמיכה/התנגדות
            support_resistance = self._identify_support_resistance(price_df, vwap)
            
            # זיהוי דפוסי מסחר
            patterns = self._detect_trading_patterns(price_df, vwap)
            
            # אינדיקטורי מומנטום
            momentum = self._calculate_momentum_indicators(price_df, vwap)
            
            # חישוב ציון מורכב
            score = self._calculate_composite_score(
                price_analysis, volume_analysis, trend_analysis,
                support_resistance, patterns, momentum
            )
            
            # יצירת הסבר
            explanation_parts = []
            explanation_parts.append(f"מחיר: {price_analysis['position']}")
            explanation_parts.append(f"מגמה: {trend_analysis['trend']}")
            
            # הוספת מידע על פריצות
            if breakout_analysis.get('breakout_type') != 'none':
                explanation_parts.append(f"פריצה: {breakout_analysis['breakout_type']}")
            
            if volume_analysis.get('volume_pattern'):
                explanation_parts.append(f"נפח: {volume_analysis['volume_pattern']}")
            
            if patterns:
                explanation_parts.append(f"דפוסים: {len(patterns)}")
            
            explanation = " | ".join(explanation_parts)
            
            # יצירת פרטים מפורטים
            details = {
                'symbol': symbol,
                'price_analysis': price_analysis,
                'volume_analysis': volume_analysis,
                'trend_analysis': trend_analysis,
                'support_resistance': support_resistance,
                'trading_patterns': patterns,
                'momentum_indicators': momentum,
                'breakout_analysis': breakout_analysis,
                'vwap_value': vwap.iloc[-1],
                'analysis_date': datetime.now().isoformat(),
                'data_points': len(price_df)
            }
            
            return {
                "score": score,
                "explanation": explanation,
                "details": details
            }
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()
            }
