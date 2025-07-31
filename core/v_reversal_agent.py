"""
V-Reversal Agent - סוכן היפוכי V מתקדם
=======================================

סוכן מתקדם לזיהוי תבניות היפוך V עם יכולות:
- זיהוי תבניות V מתקדם
- ניתוח נפח בהיפוך
- זיהוי נקודות pivot
- ניתוח מהירות היפוך
- ולידציה של תבניות
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
class VReversalMetrics:
    """מבנה נתונים למדדי היפוך V"""
    pivot_point: Optional[float]
    drop_percentage: float
    rise_percentage: float
    v_speed_ratio: float
    volume_confirmation: bool
    reversal_strength: float
    pattern_quality: float

class VReversalAgent(BaseAgent):
    """
    סוכן מתקדם לזיהוי תבניות היפוך V
    
    תכונות מתקדמות:
    - זיהוי תבניות V מתקדם
    - ניתוח נפח בהיפוך
    - זיהוי נקודות pivot
    - ניתוח מהירות היפוך
    - ולידציה של תבניות
    - אינדיקטורים טכניים מתקדמים
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        אתחול סוכן היפוכי V
        
        Args:
            config: מילון הגדרות
                - window: כמה ימים לבדוק (ברירת מחדל: 25)
                - pivot_lookback: מינימום ימי pivot (שפל) [ברירת מחדל: 3]
                - min_drop_pct: אחוז ירידה נדרש לפני היפוך V (ברירת מחדל: 8)
                - min_rise_pct: אחוז עליה נדרשת מהשפל (ברירת מחדל: 7)
                - min_vol_increase: עליה בווליום ביום המהפך (ברירת מחדל: 1.5)
                - v_min_speed: יחס מהירות עליה/ירידה (ברירת מחדל: 1.4)
                - quality_threshold: סף איכות תבנית (ברירת מחדל: 0.7)
        """
        super().__init__(config)
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.window = cfg.get("window", 25)
        self.pivot_lookback = cfg.get("pivot_lookback", 3)
        self.min_drop_pct = cfg.get("min_drop_pct", 8)
        self.min_rise_pct = cfg.get("min_rise_pct", 7)
        self.min_vol_increase = cfg.get("min_vol_increase", 1.5)
        self.v_min_speed = cfg.get("v_min_speed", 1.4)
        self.quality_threshold = cfg.get("quality_threshold", 0.7)
        
        # משקלים לניתוח
        self.weights = {
            'pattern_detection': 0.35,
            'volume_confirmation': 0.25,
            'reversal_strength': 0.20,
            'speed_ratio': 0.15,
            'pattern_quality': 0.05
        }
        
        # סוגי תבניות
        self.pattern_types = {
            'strong_v': 'תבנית V חזקה',
            'v_pattern': 'תבנית V',
            'weak_v': 'תבנית V חלשה',
            'partial_v': 'תבנית V חלקית',
            'no_pattern': 'אין תבנית V'
        }
        
        self.logger = get_agent_logger("v_reversal_agent")
        self.logger.info("V-Reversal Agent initialized successfully")

    def _find_pivot_point(self, price_df: pd.DataFrame) -> Optional[Tuple[int, float]]:
        """
        זיהוי נקודת pivot (שפל)
        
        Args:
            price_df: DataFrame עם נתוני מחיר
            
        Returns:
            Tuple של (אינדקס, מחיר) או None
        """
        try:
            if len(price_df) < self.window:
                return None
            
            # חיפוש נקודת השפל בחלון הנתון
            recent_data = price_df['close'].iloc[-self.window:]
            pivot_idx = recent_data.idxmin()
            pivot_price = recent_data.min()
            
            # בדיקה שהנקודה היא באמת pivot (לא בקצוות)
            pivot_position = recent_data.index.get_loc(pivot_idx)
            if pivot_position < self.pivot_lookback or pivot_position > len(recent_data) - self.pivot_lookback:
                return None
            
            return (pivot_position, pivot_price)
            
        except Exception as e:
            self.logger.error(f"Error finding pivot point: {str(e)}")
            return None

    def _analyze_v_pattern(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח תבנית V
        
        Args:
            price_df: DataFrame עם נתוני מחיר
            
        Returns:
            מילון עם ניתוח התבנית
        """
        try:
            if len(price_df) < self.window:
                return {
                    'pattern_detected': False,
                    'pattern_type': 'no_pattern',
                    'pivot_point': None,
                    'drop_percentage': 0.0,
                    'rise_percentage': 0.0,
                    'v_speed_ratio': 0.0
                }
            
            # זיהוי נקודת pivot
            pivot_result = self._find_pivot_point(price_df)
            if pivot_result is None:
                return {
                    'pattern_detected': False,
                    'pattern_type': 'no_pattern',
                    'pivot_point': None,
                    'drop_percentage': 0.0,
                    'rise_percentage': 0.0,
                    'v_speed_ratio': 0.0
                }
            
            pivot_idx, pivot_price = pivot_result
            recent_data = price_df['close'].iloc[-self.window:]
            
            # חישוב ירידה לפני pivot
            start_price = recent_data.iloc[0]
            drop_percentage = ((start_price - pivot_price) / start_price) * 100
            
            # חישוב עלייה אחרי pivot
            end_price = recent_data.iloc[-1]
            rise_percentage = ((end_price - pivot_price) / pivot_price) * 100
            
            # חישוב מהירות היפוך
            drop_days = pivot_idx
            rise_days = len(recent_data) - pivot_idx - 1
            
            if drop_days > 0 and rise_days > 0:
                drop_speed = drop_percentage / drop_days
                rise_speed = rise_percentage / rise_days
                v_speed_ratio = rise_speed / drop_speed if drop_speed > 0 else 0
            else:
                v_speed_ratio = 0
            
            # זיהוי סוג תבנית
            if (drop_percentage >= self.min_drop_pct and 
                rise_percentage >= self.min_rise_pct and 
                v_speed_ratio >= self.v_min_speed):
                if v_speed_ratio >= 2.0:
                    pattern_type = 'strong_v'
                else:
                    pattern_type = 'v_pattern'
                pattern_detected = True
            elif (drop_percentage >= self.min_drop_pct * 0.7 and 
                  rise_percentage >= self.min_rise_pct * 0.7):
                pattern_type = 'weak_v'
                pattern_detected = True
            elif drop_percentage > 0 and rise_percentage > 0:
                pattern_type = 'partial_v'
                pattern_detected = True
            else:
                pattern_type = 'no_pattern'
                pattern_detected = False
            
            return {
                'pattern_detected': pattern_detected,
                'pattern_type': pattern_type,
                'pivot_point': pivot_price,
                'drop_percentage': drop_percentage,
                'rise_percentage': rise_percentage,
                'v_speed_ratio': v_speed_ratio,
                'drop_days': drop_days,
                'rise_days': rise_days
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing V pattern: {str(e)}")
            return {
                'pattern_detected': False,
                'pattern_type': 'no_pattern',
                'pivot_point': None,
                'drop_percentage': 0.0,
                'rise_percentage': 0.0,
                'v_speed_ratio': 0.0
            }

    def _analyze_volume_confirmation(self, price_df: pd.DataFrame, pivot_result: Optional[Tuple[int, float]]) -> Dict[str, Any]:
        """
        ניתוח אישור נפח בהיפוך
        
        Args:
            price_df: DataFrame עם נתוני מחיר
            pivot_result: תוצאת זיהוי pivot
            
        Returns:
            מילון עם ניתוח נפח
        """
        try:
            if 'volume' not in price_df.columns or pivot_result is None:
                return {
                    'volume_confirmed': False,
                    'volume_ratio': 1.0,
                    'volume_pattern': 'no_data'
                }
            
            pivot_idx, _ = pivot_result
            recent_volume = price_df['volume'].iloc[-self.window:]
            
            # נפח לפני pivot
            pre_pivot_volume = recent_volume.iloc[:pivot_idx].mean()
            
            # נפח אחרי pivot
            post_pivot_volume = recent_volume.iloc[pivot_idx:].mean()
            
            # יחס נפח
            volume_ratio = post_pivot_volume / pre_pivot_volume if pre_pivot_volume > 0 else 1.0
            
            # בדיקת אישור נפח
            volume_confirmed = volume_ratio >= self.min_vol_increase
            
            # זיהוי דפוס נפח
            if volume_ratio >= 2.0:
                volume_pattern = 'נפח גבוה מאוד'
            elif volume_ratio >= self.min_vol_increase:
                volume_pattern = 'נפח גבוה'
            elif volume_ratio >= 1.2:
                volume_pattern = 'נפח מעל הממוצע'
            else:
                volume_pattern = 'נפח נמוך'
            
            return {
                'volume_confirmed': volume_confirmed,
                'volume_ratio': volume_ratio,
                'volume_pattern': volume_pattern,
                'pre_pivot_volume': pre_pivot_volume,
                'post_pivot_volume': post_pivot_volume
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing volume confirmation: {str(e)}")
            return {
                'volume_confirmed': False,
                'volume_ratio': 1.0,
                'volume_pattern': 'error'
            }

    def _calculate_reversal_strength(self, pattern_analysis: Dict[str, Any]) -> float:
        """
        חישוב עוצמת ההיפוך
        
        Args:
            pattern_analysis: ניתוח התבנית
            
        Returns:
            עוצמת ההיפוך (0-1)
        """
        try:
            if not pattern_analysis['pattern_detected']:
                return 0.0
            
            # חישוב עוצמה לפי אחוזי השינוי
            drop_strength = min(1.0, pattern_analysis['drop_percentage'] / self.min_drop_pct)
            rise_strength = min(1.0, pattern_analysis['rise_percentage'] / self.min_rise_pct)
            
            # חישוב עוצמה לפי מהירות
            speed_strength = min(1.0, pattern_analysis['v_speed_ratio'] / self.v_min_speed)
            
            # ממוצע משוקלל
            reversal_strength = (drop_strength * 0.3 + rise_strength * 0.4 + speed_strength * 0.3)
            
            return reversal_strength
            
        except Exception as e:
            self.logger.error(f"Error calculating reversal strength: {str(e)}")
            return 0.0

    def _calculate_pattern_quality(self, pattern_analysis: Dict[str, Any], 
                                 volume_analysis: Dict[str, Any]) -> float:
        """
        חישוב איכות התבנית
        
        Args:
            pattern_analysis: ניתוח התבנית
            volume_analysis: ניתוח הנפח
            
        Returns:
            איכות התבנית (0-1)
        """
        try:
            quality_factors = []
            
            # איכות לפי סוג תבנית
            pattern_type = pattern_analysis['pattern_type']
            if pattern_type == 'strong_v':
                quality_factors.append(1.0)
            elif pattern_type == 'v_pattern':
                quality_factors.append(0.8)
            elif pattern_type == 'weak_v':
                quality_factors.append(0.6)
            elif pattern_type == 'partial_v':
                quality_factors.append(0.4)
            else:
                quality_factors.append(0.0)
            
            # איכות לפי אישור נפח
            if volume_analysis.get('volume_confirmed', False):
                quality_factors.append(1.0)
            else:
                quality_factors.append(0.5)
            
            # איכות לפי עוצמת ההיפוך
            reversal_strength = self._calculate_reversal_strength(pattern_analysis)
            quality_factors.append(reversal_strength)
            
            # ממוצע איכות
            pattern_quality = np.mean(quality_factors)
            
            return pattern_quality
            
        except Exception as e:
            self.logger.error(f"Error calculating pattern quality: {str(e)}")
            return 0.0

    def _calculate_composite_score(self, pattern_analysis: Dict[str, Any], 
                                 volume_analysis: Dict[str, Any]) -> int:
        """
        חישוב ציון מורכב
        
        Args:
            pattern_analysis: ניתוח התבנית
            volume_analysis: ניתוח הנפח
            
        Returns:
            ציון מורכב (1-100)
        """
        try:
            scores = {}
            
            # ציון זיהוי תבנית
            if pattern_analysis['pattern_detected']:
                pattern_type = pattern_analysis['pattern_type']
                if pattern_type == 'strong_v':
                    pattern_score = 100
                elif pattern_type == 'v_pattern':
                    pattern_score = 85
                elif pattern_type == 'weak_v':
                    pattern_score = 70
                elif pattern_type == 'partial_v':
                    pattern_score = 50
                else:
                    pattern_score = 30
            else:
                pattern_score = 10
            scores['pattern_detection'] = pattern_score
            
            # ציון אישור נפח
            if volume_analysis.get('volume_confirmed', False):
                volume_score = 100
            else:
                volume_ratio = volume_analysis.get('volume_ratio', 1.0)
                volume_score = min(100, int(volume_ratio * 50))
            scores['volume_confirmation'] = volume_score
            
            # ציון עוצמת היפוך
            reversal_strength = self._calculate_reversal_strength(pattern_analysis)
            strength_score = int(reversal_strength * 100)
            scores['reversal_strength'] = strength_score
            
            # ציון יחס מהירות
            speed_ratio = pattern_analysis.get('v_speed_ratio', 0.0)
            if speed_ratio >= 2.0:
                speed_score = 100
            elif speed_ratio >= self.v_min_speed:
                speed_score = 80
            elif speed_ratio >= 1.0:
                speed_score = 60
            else:
                speed_score = 30
            scores['speed_ratio'] = speed_score
            
            # ציון איכות תבנית
            pattern_quality = self._calculate_pattern_quality(pattern_analysis, volume_analysis)
            quality_score = int(pattern_quality * 100)
            scores['pattern_quality'] = quality_score
            
            # חישוב ציון מורכב
            composite_score = sum(scores[component] * self.weights[component] 
                                for component in scores.keys())
            
            return max(1, min(int(composite_score), 100))
            
        except Exception as e:
            self.logger.error(f"Error calculating composite score: {str(e)}")
            return 50

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח תבניות היפוך V מתקדם
        
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
                    "explanation": "אין נתוני מחיר זמינים לניתוח תבניות V",
                    "details": {}
                }
            
            if len(price_df) < self.window:
                return {
                    "score": 50,
                    "explanation": "אין מספיק נתונים לניתוח תבניות V מתקדם",
                    "details": {}
                }
            
            # ניתוח תבנית V
            pattern_analysis = self._analyze_v_pattern(price_df)
            
            # ניתוח אישור נפח
            pivot_result = self._find_pivot_point(price_df)
            volume_analysis = self._analyze_volume_confirmation(price_df, pivot_result)
            
            # חישוב ציון מורכב
            score = self._calculate_composite_score(pattern_analysis, volume_analysis)
            
            # יצירת הסבר
            explanation_parts = []
            
            pattern_type = pattern_analysis['pattern_type']
            pattern_name = self.pattern_types.get(pattern_type, pattern_type)
            explanation_parts.append(f"תבנית: {pattern_name}")
            
            if pattern_analysis['pattern_detected']:
                explanation_parts.append(f"ירידה: {pattern_analysis['drop_percentage']:.1f}%")
                explanation_parts.append(f"עלייה: {pattern_analysis['rise_percentage']:.1f}%")
                
                if pattern_analysis['v_speed_ratio'] > 1.0:
                    explanation_parts.append(f"מהירות: {pattern_analysis['v_speed_ratio']:.1f}x")
            
            if volume_analysis.get('volume_confirmed'):
                explanation_parts.append("נפח מאשר")
            
            explanation = " | ".join(explanation_parts)
            
            # יצירת פרטים מפורטים
            details = {
                'symbol': symbol,
                'pattern_analysis': pattern_analysis,
                'volume_analysis': volume_analysis,
                'pivot_result': pivot_result,
                'reversal_strength': self._calculate_reversal_strength(pattern_analysis),
                'pattern_quality': self._calculate_pattern_quality(pattern_analysis, volume_analysis),
                'analysis_date': datetime.now().isoformat(),
                'data_points': len(price_df)
            }
            
            return {
                "score": score,
                "explanation": explanation,
                "details": details
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing V reversal for {symbol}: {str(e)}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח תבניות V: {str(e)}",
                "details": {}
            }
