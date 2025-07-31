"""
VWAP Trend Agent - סוכן מגמות VWAP מתקדם
=========================================

סוכן מתקדם לניתוח מגמות VWAP עם יכולות:
- ניתוח VWAP רב-ממדי (יומי, שבועי, חודשי)
- זיהוי פריצות מסונכרנות
- ניתוח Anchored VWAP
- זיהוי דפוסי פריצה
- ניתוח איכות פריצה
- אינדיקטורים טכניים מתקדמים
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from core.base.base_agent import BaseAgent
from utils.logger import get_agent_logger
import logging

logger = logging.getLogger(__name__)

@dataclass
class VWAPTrendMetrics:
    """מבנה נתונים למדדי מגמות VWAP"""
    daily_vwap: float
    weekly_vwap: float
    monthly_vwap: float
    anchored_vwap: Optional[float]
    sync_breakout: bool
    anchored_signal: bool
    breakout_quality: float
    trend_strength: float

class VWAPTrendAgent(BaseAgent):
    """
    סוכן מתקדם לניתוח מגמות VWAP
    
    תכונות מתקדמות:
    - ניתוח VWAP רב-ממדי (יומי, שבועי, חודשי)
    - זיהוי פריצות מסונכרנות
    - ניתוח Anchored VWAP
    - זיהוי דפוסי פריצה
    - ניתוח איכות פריצה
    - אינדיקטורים טכניים מתקדמים
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        אתחול סוכן מגמות VWAP
        
        Args:
            config: מילון הגדרות
                - anchored_event_index: אינדקס אירוע עיגון (למשל יום דוח)
                - weight_sync: משקל לפריצה מסונכרנת (ברירת מחדל: 0.7)
                - weight_avwap: משקל לפריצה לעומת anchored VWAP (ברירת מחדל: 0.3)
                - quality_threshold: סף איכות פריצה (ברירת מחדל: 0.02)
                - trend_period: תקופה לניתוח מגמה (ברירת מחדל: 10)
        """
        super().__init__(config)
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.anchor_idx = cfg.get("anchored_event_index", None)
        self.weight_sync = cfg.get("weight_sync", 0.7)
        self.weight_avwap = cfg.get("weight_avwap", 0.3)
        self.quality_threshold = cfg.get("quality_threshold", 0.02)
        self.trend_period = cfg.get("trend_period", 10)
        
        # משקלים לניתוח
        self.weights = {
            'sync_breakout': 0.40,
            'anchored_signal': 0.25,
            'breakout_quality': 0.20,
            'trend_strength': 0.15
        }
        
        # סוגי פריצות
        self.breakout_types = {
            'strong_sync': 'פריצה מסונכרנת חזקה',
            'sync': 'פריצה מסונכרנת',
            'anchored': 'פריצה לעומת Anchored VWAP',
            'partial': 'פריצה חלקית',
            'none': 'אין פריצה'
        }
        
        self.logger = get_agent_logger("vwap_trend_agent")
        self.logger.info("VWAP Trend Agent initialized successfully")

    def _calc_vwap(self, price_df: pd.DataFrame, window: int) -> pd.Series:
        """
        חישוב VWAP לחלון נתון
        
        Args:
            price_df: DataFrame עם נתוני מחיר
            window: גודל החלון
            
        Returns:
            Series עם ערכי VWAP
        """
        try:
            if len(price_df) < window:
                return pd.Series([None] * len(price_df), index=price_df.index)
            
            price = price_df["close"].iloc[-window:]
            volume = price_df["volume"].iloc[-window:]
            
            # חישוב VWAP מצטבר
            vwap = (price * volume).cumsum() / volume.cumsum()
            
            # יצירת Series מלא עם None בתחילתו
            full_vwap = pd.Series([None] * (len(price_df) - window) + list(vwap), 
                                 index=price_df.index)
            
            return full_vwap
            
        except Exception as e:
            self.logger.error(f"Error calculating VWAP for window {window}: {str(e)}")
            return pd.Series([None] * len(price_df), index=price_df.index)

    def _calc_anchored_vwap(self, price_df: pd.DataFrame, anchor_idx: int) -> pd.Series:
        """
        חישוב Anchored VWAP מנקודת עיגון
        
        Args:
            price_df: DataFrame עם נתוני מחיר
            anchor_idx: אינדקס נקודת העיגון
            
        Returns:
            Series עם ערכי Anchored VWAP
        """
        try:
            if anchor_idx >= len(price_df):
                return pd.Series([None] * len(price_df), index=price_df.index)
            
            # חישוב VWAP מנקודת העיגון
            volume = price_df["volume"].iloc[anchor_idx:]
            price = price_df["close"].iloc[anchor_idx:]
            
            pv = (price * volume).cumsum()
            cum_vol = volume.cumsum()
            avwap = pv / cum_vol
            
            # יצירת Series מלא עם None לפני נקודת העיגון
            result = pd.Series([None] * anchor_idx + list(avwap), index=price_df.index)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating Anchored VWAP: {str(e)}")
            return pd.Series([None] * len(price_df), index=price_df.index)

    def _analyze_vwap_breakouts(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח פריצות VWAP
        
        Args:
            price_df: DataFrame עם נתוני מחיר
            
        Returns:
            מילון עם ניתוח הפריצות
        """
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
            vwap_daily = self._calc_vwap(price_df, window=1)
            vwap_weekly = self._calc_vwap(price_df, window=5)
            vwap_monthly = self._calc_vwap(price_df, window=21)
            
            # Anchored VWAP
            avwap = None
            if self.anchor_idx is not None and self.anchor_idx < n:
                avwap = self._calc_anchored_vwap(price_df, self.anchor_idx)
            
            current_price = price_df["close"].iloc[-1]
            
            # בדיקת פריצה מסונכרנת
            vwap_sync_break = (
                current_price > vwap_daily.iloc[-1] and 
                current_price > vwap_weekly.iloc[-1] and 
                current_price > vwap_monthly.iloc[-1]
            )
            
            # בדיקת סיגנל Anchored
            avwap_signal = False
            if avwap is not None and avwap.iloc[-1] is not None:
                avwap_signal = current_price > avwap.iloc[-1]
            
            # חישוב איכות פריצה
            vwap_levels = {
                'daily': vwap_daily.iloc[-1],
                'weekly': vwap_weekly.iloc[-1],
                'monthly': vwap_monthly.iloc[-1],
                'anchored': avwap.iloc[-1] if avwap is not None else None
            }
            
            # חישוב מרחקים מ-VWAP
            distances = {}
            for name, level in vwap_levels.items():
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
                'vwap_levels': vwap_levels,
                'distances': distances
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing VWAP breakouts: {str(e)}")
            return {
                'sync_breakout': False,
                'anchored_signal': False,
                'breakout_type': 'none',
                'breakout_quality': 0.0,
                'vwap_levels': {}
            }

    def _analyze_trend_strength(self, price_df: pd.DataFrame, vwap_levels: Dict[str, float]) -> Dict[str, Any]:
        """
        ניתוח עוצמת מגמה
        
        Args:
            price_df: DataFrame עם נתוני מחיר
            vwap_levels: מילון עם רמות VWAP
            
        Returns:
            מילון עם ניתוח עוצמת מגמה
        """
        try:
            if len(price_df) < self.trend_period:
                return {'trend_strength': 0.0, 'trend_direction': 'neutral'}
            
            # חישוב מגמה לפי VWAP
            current_price = price_df["close"].iloc[-1]
            recent_prices = price_df["close"].iloc[-self.trend_period:]
            
            # מגמה לפי מחיר
            price_trend = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
            
            # מגמה לפי VWAP
            vwap_trends = []
            for name, level in vwap_levels.items():
                if level is not None:
                    # חישוב VWAP לתקופה קודמת
                    if name == 'daily':
                        prev_vwap = self._calc_vwap(price_df.iloc[:-1], 1).iloc[-1]
                    elif name == 'weekly':
                        prev_vwap = self._calc_vwap(price_df.iloc[:-1], 5).iloc[-1]
                    elif name == 'monthly':
                        prev_vwap = self._calc_vwap(price_df.iloc[:-1], 21).iloc[-1]
                    else:
                        continue
                    
                    if prev_vwap is not None:
                        vwap_trend = (level - prev_vwap) / prev_vwap
                        vwap_trends.append(vwap_trend)
            
            # עוצמת מגמה - ממוצע המגמות
            if vwap_trends:
                trend_strength = np.mean(vwap_trends)
            else:
                trend_strength = price_trend
            
            # כיוון מגמה
            if trend_strength > self.quality_threshold:
                trend_direction = 'bullish'
            elif trend_strength < -self.quality_threshold:
                trend_direction = 'bearish'
            else:
                trend_direction = 'neutral'
            
            return {
                'trend_strength': trend_strength,
                'trend_direction': trend_direction,
                'price_trend': price_trend
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend strength: {str(e)}")
            return {'trend_strength': 0.0, 'trend_direction': 'neutral'}

    def _calculate_composite_score(self, breakout_analysis: Dict[str, Any], 
                                 trend_analysis: Dict[str, Any]) -> int:
        """
        חישוב ציון מורכב
        
        Args:
            breakout_analysis: ניתוח הפריצות
            trend_analysis: ניתוח המגמה
            
        Returns:
            ציון מורכב (1-100)
        """
        try:
            scores = {}
            
            # ציון פריצה מסונכרנת
            if breakout_analysis['sync_breakout']:
                sync_score = 100
            else:
                # חישוב ציון חלקי לפי כמה רחוק מ-VWAP
                distances = breakout_analysis.get('distances', {})
                if distances:
                    max_distance = max(distances.values())
                    sync_score = max(1, int(100 * max_distance))
                else:
                    sync_score = 1
            scores['sync_breakout'] = sync_score
            
            # ציון סיגנל Anchored
            if breakout_analysis['anchored_signal']:
                anchored_score = 100
            elif breakout_analysis.get('vwap_levels', {}).get('anchored') is not None:
                anchored_score = 30
            else:
                anchored_score = 1
            scores['anchored_signal'] = anchored_score
            
            # ציון איכות פריצה
            quality = breakout_analysis.get('breakout_quality', 0.0)
            quality_score = min(100, int(quality * 1000))  # המרה לציון
            scores['breakout_quality'] = quality_score
            
            # ציון עוצמת מגמה
            trend_strength = abs(trend_analysis.get('trend_strength', 0.0))
            trend_score = min(100, int(trend_strength * 1000))
            scores['trend_strength'] = trend_score
            
            # חישוב ציון מורכב
            composite_score = sum(scores[component] * self.weights[component] 
                                for component in scores.keys())
            
            return max(1, min(int(composite_score), 100))
            
        except Exception as e:
            self.logger.error(f"Error calculating composite score: {str(e)}")
            return 50

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח מגמות VWAP מתקדם
        
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
                    "explanation": "אין נתוני מחיר זמינים לניתוח מגמות VWAP",
                    "details": {}
                }
            
            if len(price_df) < 21:
                return {
                    "score": 50,
                    "explanation": "אין מספיק נתונים לניתוח מגמות VWAP מתקדם",
                    "details": {}
                }
            
            # ניתוח פריצות VWAP
            breakout_analysis = self._analyze_vwap_breakouts(price_df)
            
            # ניתוח עוצמת מגמה
            trend_analysis = self._analyze_trend_strength(price_df, breakout_analysis['vwap_levels'])
            
            # חישוב ציון מורכב
            score = self._calculate_composite_score(breakout_analysis, trend_analysis)
            
            # יצירת הסבר
            explanation_parts = []
            
            breakout_type = breakout_analysis['breakout_type']
            breakout_name = self.breakout_types.get(breakout_type, breakout_type)
            explanation_parts.append(f"פריצה: {breakout_name}")
            
            if breakout_analysis['sync_breakout']:
                explanation_parts.append("פריצה מסונכרנת")
            
            if breakout_analysis['anchored_signal']:
                explanation_parts.append("מעל Anchored VWAP")
            
            trend_direction = trend_analysis['trend_direction']
            if trend_direction != 'neutral':
                explanation_parts.append(f"מגמה: {trend_direction}")
            
            quality = breakout_analysis.get('breakout_quality', 0.0)
            if quality > 0.01:
                explanation_parts.append(f"איכות: {quality:.2%}")
            
            explanation = " | ".join(explanation_parts)
            
            # יצירת פרטים מפורטים
            details = {
                'symbol': symbol,
                'breakout_analysis': breakout_analysis,
                'trend_analysis': trend_analysis,
                'vwap_levels': breakout_analysis['vwap_levels'],
                'distances': breakout_analysis.get('distances', {}),
                'analysis_date': datetime.now().isoformat(),
                'data_points': len(price_df)
            }
            
            return {
                "score": score,
                "explanation": explanation,
                "details": details
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing VWAP trends for {symbol}: {str(e)}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח מגמות VWAP: {str(e)}",
                "details": {}
            }

