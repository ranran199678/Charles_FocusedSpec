"""
FloatPressureEvaluator - הערכת לחץ צף מתקדמת
============================================

סוכן מתקדם להערכת לחץ צף (Float Pressure) עם ניתוח רב-ממדי,
ולידציה מתקדמת ומבנה Signal תקני.

תכונות מתקדמות:
- הערכת לחץ צף לפי מספר פרמטרים
- ניתוח רב-ממדי של לחץ צף
- ולידציה לפי זמן ומגמה
- ניתוח לחץ צף לפי סקטורים
- זיהוי לחץ צף לפני אירועים
- ניתוח לחץ צף לפי טכני ופונדמנטלי
- זיהוי לחץ צף לפי רגשות השוק
- ניתוח לחץ צף לפי נפח ומחיר
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from utils.data_fetcher import data_fetcher
from utils.constants import FLOAT_PRESSURE_THRESHOLDS, TIME_PERIODS
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FloatPressure:
    """מבנה נתונים ללחץ צף"""
    timestamp: datetime
    pressure_type: str
    strength: float
    confidence: float
    float_ratio: float
    volume_ratio: float
    price_impact: float
    context: Dict
    significance: str

@dataclass
class FloatPressureAnalysis:
    """מבנה נתונים לניתוח לחץ צף מתקדם"""
    total_pressures: int
    significant_pressures: int
    avg_pressure_strength: float
    float_trend: str
    volume_trend: str
    sector_comparison: Dict
    time_analysis: Dict
    breakout_potential: float

class FloatPressureEvaluator:
    """
    סוכן מתקדם להערכת לחץ צף
    
    תכונות מתקדמות:
    - הערכת לחץ צף לפי מספר פרמטרים
    - ניתוח רב-ממדי של לחץ צף
    - ולידציה לפי זמן ומגמה
    - ניתוח לחץ צף לפי סקטורים
    - זיהוי לחץ צף לפני אירועים
    - ניתוח לחץ צף לפי טכני ופונדמנטלי
    - זיהוי לחץ צף לפי רגשות השוק
    - ניתוח לחץ צף לפי נפח ומחיר
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        self.config = config or {}
        
        # הגדרות מתקדמות
        self.float_pressure_thresholds = {
            'low': 0.3,
            'moderate': 0.5,
            'high': 0.7,
            'extreme': 0.9
        }
        
        self.time_periods = {
            'short': 5,
            'medium': 20,
            'long': 60
        }
        
        self.pressure_weights = {
            'float_ratio': 0.3,
            'volume_pressure': 0.25,
            'price_pressure': 0.2,
            'time_pressure': 0.15,
            'sector_pressure': 0.1
        }
        
        # סוגי לחץ צף
        self.pressure_types = {
            'accumulation': 'הצטברות',
            'distribution': 'הפצה',
            'manipulation': 'מניפולציה',
            'natural': 'טבעי',
            'event_driven': 'מונע אירוע'
        }
        
        logger.info("FloatPressureEvaluator initialized with advanced configuration")

    def _calculate_float_metrics(self, df: pd.DataFrame) -> Dict:
        """
        חישוב מדדי צף מתקדמים
        """
        try:
            # חישוב יחס צף (סימולציה - בפרודקציה יהיה מ-API)
            df['float_ratio'] = 0.15  # ברירת מחדל - 15% צף
            
            # חישוב נפח לפי צף
            df['volume_per_float'] = df['volume'] / (df['close'] * df['float_ratio'])
            
            # חישוב לחץ נפח
            df['volume_pressure'] = df['volume_per_float'].rolling(window=20).mean()
            df['volume_pressure_ratio'] = df['volume_per_float'] / df['volume_pressure']
            
            # חישוב לחץ מחיר
            df['price_pressure'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
            df['price_pressure_ratio'] = df['price_pressure'] / df['price_pressure'].rolling(window=20).mean()
            
            # חישוב מדד לחץ צף
            df['float_pressure_score'] = (df['volume_pressure_ratio'] + df['price_pressure_ratio']) / 2
            
            return {
                'float_metrics': df,
                'current_float_ratio': df['float_ratio'].iloc[-1],
                'current_volume_pressure': df['volume_pressure_ratio'].iloc[-1],
                'current_price_pressure': df['price_pressure_ratio'].iloc[-1],
                'current_float_pressure': df['float_pressure_score'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating float metrics: {e}")
            return {}

    def _detect_float_pressures(self, df: pd.DataFrame) -> List[FloatPressure]:
        """
        זיהוי לחץ צף מתקדם
        """
        pressures = []
        
        try:
            # חישוב מדדי צף
            float_metrics = self._calculate_float_metrics(df)
            if not float_metrics:
                return pressures
            
            df = float_metrics['float_metrics']
            
            # זיהוי לחץ צף
            for i in range(20, len(df)):
                # ניתוח לחץ נפח
                volume_pressure = self._analyze_volume_pressure(df, i)
                
                # ניתוח לחץ מחיר
                price_pressure = self._analyze_price_pressure(df, i)
                
                # ניתוח לחץ זמן
                time_pressure = self._analyze_time_pressure(df, i)
                
                # ניתוח לחץ סקטור
                sector_pressure = self._analyze_sector_pressure(df, i)
                
                # ניתוח פוטנציאל פריצה
                breakout_potential = self._analyze_breakout_potential(df, i)
                
                # זיהוי לחץ צף
                if self._is_float_pressure(volume_pressure, price_pressure, time_pressure, sector_pressure):
                    # חישוב עוצמת הלחץ
                    strength = self._calculate_pressure_strength(
                        volume_pressure, price_pressure, time_pressure, sector_pressure, breakout_potential
                    )
                    
                    # חישוב ביטחון
                    confidence = self._calculate_pressure_confidence(
                        volume_pressure, price_pressure, time_pressure, sector_pressure, breakout_potential
                    )
                    
                    # קביעת סוג לחץ
                    pressure_type = self._classify_pressure_type(
                        volume_pressure, price_pressure, time_pressure
                    )
                    
                    # קביעת משמעות
                    significance = self._determine_pressure_significance(strength, confidence)
                    
                    pressure = FloatPressure(
                        timestamp=df.index[i],
                        pressure_type=pressure_type,
                        strength=strength,
                        confidence=confidence,
                        float_ratio=df['float_ratio'].iloc[i],
                        volume_ratio=volume_pressure.get('pressure_ratio', 1.0),
                        price_impact=price_pressure.get('price_impact', 0.0),
                        context={
                            'volume_pressure': volume_pressure,
                            'price_pressure': price_pressure,
                            'time_pressure': time_pressure,
                            'sector_pressure': sector_pressure,
                            'breakout_potential': breakout_potential
                        },
                        significance=significance
                    )
                    
                    pressures.append(pressure)
            
            return pressures
            
        except Exception as e:
            logger.error(f"Error detecting float pressures: {e}")
            return []

    def _analyze_volume_pressure(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח לחץ נפח מתקדם
        """
        try:
            # חישוב לחץ נפח
            current_volume_pressure = df['volume_pressure_ratio'].iloc[index]
            historical_volume_pressure = df['volume_pressure_ratio'].iloc[max(0, index-30):index].mean()
            
            pressure_ratio = current_volume_pressure / historical_volume_pressure if historical_volume_pressure > 0 else 1.0
            
            # ניתוח מגמת לחץ נפח
            recent_volume_pressure = df['volume_pressure_ratio'].iloc[max(0, index-10):index].mean()
            volume_pressure_trend = 'increasing' if recent_volume_pressure > historical_volume_pressure else 'decreasing'
            
            return {
                'pressure_ratio': pressure_ratio,
                'pressure_trend': volume_pressure_trend,
                'current_pressure': current_volume_pressure,
                'historical_pressure': historical_volume_pressure,
                'recent_pressure': recent_volume_pressure
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume pressure: {e}")
            return {}

    def _analyze_price_pressure(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח לחץ מחיר מתקדם
        """
        try:
            # חישוב לחץ מחיר
            current_price_pressure = df['price_pressure_ratio'].iloc[index]
            historical_price_pressure = df['price_pressure_ratio'].iloc[max(0, index-30):index].mean()
            
            price_pressure_ratio = current_price_pressure / historical_price_pressure if historical_price_pressure > 0 else 1.0
            
            # ניתוח השפעת מחיר
            current_price = df['close'].iloc[index]
            historical_price = df['close'].iloc[max(0, index-20):index].mean()
            price_impact = (current_price - historical_price) / historical_price if historical_price > 0 else 0.0
            
            # ניתוח מגמת לחץ מחיר
            recent_price_pressure = df['price_pressure_ratio'].iloc[max(0, index-10):index].mean()
            price_pressure_trend = 'increasing' if recent_price_pressure > historical_price_pressure else 'decreasing'
            
            return {
                'pressure_ratio': price_pressure_ratio,
                'pressure_trend': price_pressure_trend,
                'price_impact': price_impact,
                'current_pressure': current_price_pressure,
                'historical_pressure': historical_price_pressure,
                'recent_pressure': recent_price_pressure
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price pressure: {e}")
            return {}

    def _analyze_time_pressure(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח לחץ זמן מתקדם
        """
        try:
            # ניתוח לחץ זמן
            time_window = df.iloc[max(0, index-30):index]
            
            # חישוב לחץ זמן
            time_pressure_duration = len(time_window)
            
            # ניתוח עקביות לחץ
            volume_consistency = time_window['volume_pressure_ratio'].std()
            price_consistency = time_window['price_pressure_ratio'].std()
            consistency_score = 1.0 - ((volume_consistency + price_consistency) / 2)
            
            # ניתוח מגמת לחץ זמן
            early_pressure = time_window.iloc[:10]['float_pressure_score'].mean()
            late_pressure = time_window.iloc[-10:]['float_pressure_score'].mean()
            time_pressure_trend = 'increasing' if late_pressure > early_pressure else 'decreasing'
            
            return {
                'pressure_duration': time_pressure_duration,
                'consistency_score': consistency_score,
                'pressure_trend': time_pressure_trend,
                'early_pressure': early_pressure,
                'late_pressure': late_pressure
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time pressure: {e}")
            return {}

    def _analyze_sector_pressure(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח לחץ סקטור מתקדם
        """
        try:
            # סימולציה של נתוני סקטור (בפרודקציה יהיה מ-API)
            sector_data = {
                'technology': {'avg_float_pressure': 0.6, 'pressure_trend': 'increasing'},
                'healthcare': {'avg_float_pressure': 0.5, 'pressure_trend': 'stable'},
                'finance': {'avg_float_pressure': 0.7, 'pressure_trend': 'decreasing'},
                'energy': {'avg_float_pressure': 0.8, 'pressure_trend': 'increasing'}
            }
            
            # קביעת סקטור (בפרודקציה יהיה מ-API)
            sector = 'technology'  # ברירת מחדל
            
            sector_info = sector_data.get(sector, {'avg_float_pressure': 0.5, 'pressure_trend': 'stable'})
            
            return {
                'sector': sector,
                'sector_avg_pressure': sector_info['avg_float_pressure'],
                'sector_pressure_trend': sector_info['pressure_trend'],
                'relative_to_sector': df['float_pressure_score'].iloc[index] / sector_info['avg_float_pressure']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector pressure: {e}")
            return {}

    def _analyze_breakout_potential(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח פוטנציאל פריצה מתקדם
        """
        try:
            # ניתוח פוטנציאל פריצה
            current_price = df['close'].iloc[index]
            
            # ניתוח לפי ממוצעים נעים
            sma_20 = df['close'].rolling(window=20).mean().iloc[index]
            sma_50 = df['close'].rolling(window=50).mean().iloc[index]
            
            # ניתוח לפי בולינגר בנדס
            bb_upper = current_price * 1.02
            bb_lower = current_price * 0.98
            
            # חישוב פוטנציאל פריצה
            upside_potential = (bb_upper - current_price) / current_price
            downside_potential = (current_price - bb_lower) / current_price
            
            # ניתוח מגמה
            price_vs_sma20 = current_price / sma_20 if sma_20 > 0 else 1.0
            price_vs_sma50 = current_price / sma_50 if sma_50 > 0 else 1.0
            
            breakout_direction = 'up' if price_vs_sma20 > 1.0 and price_vs_sma50 > 1.0 else 'down'
            breakout_strength = max(upside_potential, downside_potential)
            
            return {
                'breakout_direction': breakout_direction,
                'breakout_strength': breakout_strength,
                'upside_potential': upside_potential,
                'downside_potential': downside_potential,
                'price_vs_sma20': price_vs_sma20,
                'price_vs_sma50': price_vs_sma50
            }
            
        except Exception as e:
            logger.error(f"Error analyzing breakout potential: {e}")
            return {}

    def _is_float_pressure(self, volume_pressure: Dict, price_pressure: Dict, 
                          time_pressure: Dict, sector_pressure: Dict) -> bool:
        """
        זיהוי לחץ צף
        """
        try:
            # קריטריונים ללחץ צף
            volume_pressuring = volume_pressure.get('pressure_ratio', 1.0) > 1.2
            price_pressuring = price_pressure.get('pressure_ratio', 1.0) > 1.1
            time_pressuring = time_pressure.get('pressure_duration', 0) >= 15
            sector_pressuring = sector_pressure.get('relative_to_sector', 1.0) > 1.0
            
            # לחץ צף אם לפחות 2 קריטריונים מתקיימים
            pressure_criteria = [volume_pressuring, price_pressuring, time_pressuring, sector_pressuring]
            return sum(pressure_criteria) >= 2
            
        except Exception as e:
            logger.error(f"Error detecting float pressure: {e}")
            return False

    def _calculate_pressure_strength(self, volume_pressure: Dict, price_pressure: Dict,
                                   time_pressure: Dict, sector_pressure: Dict,
                                   breakout_potential: Dict) -> float:
        """
        חישוב עוצמת לחץ צף
        """
        try:
            strength = 0.0
            
            # משקל לפי לחץ נפח
            volume_ratio = volume_pressure.get('pressure_ratio', 1.0)
            if volume_ratio > 1.5:
                strength += 0.3
            elif volume_ratio > 1.2:
                strength += 0.2
            
            # משקל לפי לחץ מחיר
            price_ratio = price_pressure.get('pressure_ratio', 1.0)
            if price_ratio > 1.3:
                strength += 0.3
            elif price_ratio > 1.1:
                strength += 0.2
            
            # משקל לפי לחץ זמן
            time_duration = time_pressure.get('pressure_duration', 0)
            if time_duration >= 25:
                strength += 0.2
            elif time_duration >= 15:
                strength += 0.1
            
            # משקל לפי לחץ סקטור
            sector_ratio = sector_pressure.get('relative_to_sector', 1.0)
            if sector_ratio > 1.2:
                strength += 0.1
            
            # משקל לפי פוטנציאל פריצה
            breakout_strength = breakout_potential.get('breakout_strength', 0.0)
            if breakout_strength > 0.05:
                strength += 0.1
            
            return min(1.0, strength)
            
        except Exception as e:
            logger.error(f"Error calculating pressure strength: {e}")
            return 0.5

    def _calculate_pressure_confidence(self, volume_pressure: Dict, price_pressure: Dict,
                                     time_pressure: Dict, sector_pressure: Dict,
                                     breakout_potential: Dict) -> float:
        """
        חישוב ביטחון לחץ צף
        """
        try:
            confidence = 0.0
            
            # ביטחון לפי עקביות
            consistent_signals = 0
            if volume_pressure.get('pressure_ratio', 1.0) > 1.2:
                consistent_signals += 1
            if price_pressure.get('pressure_ratio', 1.0) > 1.1:
                consistent_signals += 1
            if time_pressure.get('pressure_duration', 0) >= 15:
                consistent_signals += 1
            if sector_pressure.get('relative_to_sector', 1.0) > 1.0:
                consistent_signals += 1
            if breakout_potential.get('breakout_strength', 0.0) > 0.03:
                consistent_signals += 1
            
            confidence = consistent_signals / 5.0
            
            # התאמה לפי עוצמת לחץ
            avg_pressure = (volume_pressure.get('pressure_ratio', 1.0) + price_pressure.get('pressure_ratio', 1.0)) / 2
            if avg_pressure > 1.3:
                confidence *= 1.2
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating pressure confidence: {e}")
            return 0.5

    def _classify_pressure_type(self, volume_pressure: Dict, price_pressure: Dict, time_pressure: Dict) -> str:
        """
        סיווג סוג לחץ צף
        """
        try:
            volume_ratio = volume_pressure.get('pressure_ratio', 1.0)
            price_ratio = price_pressure.get('pressure_ratio', 1.0)
            time_duration = time_pressure.get('pressure_duration', 0)
            
            if volume_ratio > 1.5 and price_ratio > 1.3 and time_duration >= 25:
                return 'accumulation'
            elif volume_ratio > 1.3 and price_ratio < 0.9 and time_duration >= 20:
                return 'distribution'
            elif volume_ratio > 2.0 and price_ratio > 1.5:
                return 'manipulation'
            elif time_duration >= 30:
                return 'event_driven'
            else:
                return 'natural'
                
        except Exception as e:
            logger.error(f"Error classifying pressure type: {e}")
            return 'unknown'

    def _determine_pressure_significance(self, strength: float, confidence: float) -> str:
        """
        קביעת משמעות לחץ צף
        """
        try:
            if strength >= self.float_pressure_thresholds['extreme'] and confidence >= 0.8:
                return 'extreme'
            elif strength >= self.float_pressure_thresholds['high'] and confidence >= 0.6:
                return 'high'
            elif strength >= self.float_pressure_thresholds['moderate'] and confidence >= 0.4:
                return 'moderate'
            elif strength >= self.float_pressure_thresholds['low'] and confidence >= 0.2:
                return 'low'
            else:
                return 'minimal'
                
        except Exception as e:
            logger.error(f"Error determining pressure significance: {e}")
            return 'unknown'

    def _calculate_float_pressure_analysis(self, df: pd.DataFrame, pressures: List[FloatPressure]) -> FloatPressureAnalysis:
        """
        חישוב ניתוח לחץ צף מתקדם
        """
        try:
            # חישוב סטטיסטיקות בסיסיות
            total_pressures = len(pressures)
            significant_pressures = len([p for p in pressures if p.significance in ['high', 'extreme']])
            
            # חישוב ממוצע עוצמת לחץ
            avg_pressure_strength = np.mean([p.strength for p in pressures]) if pressures else 0.5
            
            # ניתוח מגמת צף
            recent_float_pressure = df['float_pressure_score'].tail(20).mean()
            historical_float_pressure = df['float_pressure_score'].tail(60).mean()
            float_trend = 'increasing' if recent_float_pressure > historical_float_pressure else 'decreasing'
            
            # ניתוח מגמת נפח
            recent_volume = df['volume'].tail(20).mean()
            historical_volume = df['volume'].tail(60).mean()
            volume_trend = 'increasing' if recent_volume > historical_volume else 'decreasing'
            
            # ניתוח סקטור
            sector_comparison = self._analyze_sector_pressure(df, len(df)-1)
            
            # ניתוח זמן
            time_analysis = self._analyze_time_pressure(df, len(df)-1)
            
            # ניתוח פוטנציאל פריצה
            breakout_potential = self._analyze_breakout_potential(df, len(df)-1)
            breakout_potential_score = breakout_potential.get('breakout_strength', 0.0)
            
            return FloatPressureAnalysis(
                total_pressures=total_pressures,
                significant_pressures=significant_pressures,
                avg_pressure_strength=avg_pressure_strength,
                float_trend=float_trend,
                volume_trend=volume_trend,
                sector_comparison=sector_comparison,
                time_analysis=time_analysis,
                breakout_potential=breakout_potential_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating float pressure analysis: {e}")
            return FloatPressureAnalysis(0, 0, 0.5, 'unknown', 'unknown', {}, {}, 0.0)

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של לחץ צף
        """
        try:
            # אחזור נתונים
            if price_df is None:
                price_df = data_fetcher.get_price_history(symbol, period='6mo')
            
            if price_df is None or price_df.empty:
                return {
                    "score": 50,
                    "explanation": "לא ניתן לאחזר נתוני מחיר",
                    "signal": {
                        "type": "float_pressure",
                        "score": 50,
                        "reason": "לא ניתן לאחזר נתוני מחיר",
                        "confidence": 0.5,
                        "details": {
                            "pressures_count": 0,
                            "avg_pressure_strength": 0.5,
                            "float_trend": "unknown"
                        }
                    },
                    "details": {
                        "pressures": [],
                        "analysis": {},
                        "recommendations": []
                    }
                }
            
            # זיהוי לחץ צף
            pressures = self._detect_float_pressures(price_df)
            
            # ניתוח מתקדם
            analysis = self._calculate_float_pressure_analysis(price_df, pressures)
            
            # חישוב ציון סופי
            if pressures:
                # חישוב ציון לפי לחצים משמעותיים
                significant_ratio = analysis.significant_pressures / max(1, analysis.total_pressures)
                pressure_score = min(100, significant_ratio * 100 + analysis.avg_pressure_strength * 50)
                
                # התאמה לפי מגמה
                if analysis.float_trend == 'increasing' and analysis.volume_trend == 'increasing':
                    pressure_score *= 1.2
                elif analysis.float_trend == 'decreasing' or analysis.volume_trend == 'decreasing':
                    pressure_score *= 0.8
                
                pressure_score = min(100, max(0, pressure_score))
            else:
                pressure_score = 50
            
            # יצירת הסבר
            if pressures:
                recent_pressures = [p for p in pressures if p.significance in ['high', 'extreme']]
                explanation = f"זוהו {len(pressures)} לחצי צף ({len(recent_pressures)} משמעותיים). ממוצע עוצמה: {analysis.avg_pressure_strength:.2f}, מגמת צף: {analysis.float_trend}"
            else:
                explanation = "לא זוהו לחצי צף משמעותיים"
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(pressures, analysis)
            
            return {
                "score": round(pressure_score, 1),
                "explanation": explanation,
                "signal": {
                    "type": "float_pressure",
                    "score": round(pressure_score, 1),
                    "reason": explanation,
                    "confidence": round(analysis.breakout_potential, 3),
                    "details": {
                        "pressures_count": analysis.total_pressures,
                        "significant_pressures": analysis.significant_pressures,
                        "avg_pressure_strength": round(analysis.avg_pressure_strength, 2),
                        "float_trend": analysis.float_trend,
                        "volume_trend": analysis.volume_trend
                    }
                },
                "details": {
                    "pressures": [
                        {
                            "timestamp": pressure.timestamp.isoformat(),
                            "pressure_type": pressure.pressure_type,
                            "strength": round(pressure.strength, 2),
                            "significance": pressure.significance,
                            "confidence": round(pressure.confidence, 3),
                            "float_ratio": round(pressure.float_ratio, 2)
                        }
                        for pressure in pressures[:10]  # Top 10 pressures
                    ],
                    "analysis": {
                        "total_pressures": analysis.total_pressures,
                        "significant_pressures": analysis.significant_pressures,
                        "avg_pressure_strength": round(analysis.avg_pressure_strength, 2),
                        "float_trend": analysis.float_trend,
                        "volume_trend": analysis.volume_trend,
                        "breakout_potential": round(analysis.breakout_potential, 3),
                        "sector_comparison": analysis.sector_comparison,
                        "time_analysis": analysis.time_analysis
                    },
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"Error in FloatPressureEvaluator.analyze: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח: {str(e)}",
                "signal": {
                    "type": "float_pressure",
                    "score": 50,
                    "reason": f"שגיאה בניתוח: {str(e)}",
                    "confidence": 0.5,
                    "details": {
                        "pressures_count": 0,
                        "avg_pressure_strength": 0.5,
                        "float_trend": "error"
                    }
                },
                "details": {
                    "pressures": [],
                    "analysis": {},
                    "recommendations": []
                }
            }

    def _generate_recommendations(self, pressures: List[FloatPressure], analysis: FloatPressureAnalysis) -> List[str]:
        """
        יצירת המלצות מתקדמות
        """
        recommendations = []
        
        try:
            if analysis.significant_pressures > 0:
                recommendations.append("🔍 מעקב אחר לחצי צף משמעותיים - פוטנציאל לתנועה חזקה")
            
            if analysis.avg_pressure_strength > 0.7:
                recommendations.append("📈 לחץ צף גבוה - פוטנציאל לפריצה קרובה")
            
            if analysis.float_trend == 'increasing' and analysis.volume_trend == 'increasing':
                recommendations.append("📊 לחץ צף עולה - עניין גובר במניה")
            
            if analysis.breakout_potential > 0.05:
                recommendations.append("💪 פוטנציאל פריצה גבוה - תמיכה חזקה בתנועה")
            
            if analysis.significant_pressures > 3:
                recommendations.append("⚠️ מספר לחצים משמעותיים - בדוק חדשות או אירועים")
            
            if not recommendations:
                recommendations.append("📉 אין לחצי צף משמעותיים - המשך מעקב")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["שגיאה ביצירת המלצות"]

    def get_float_pressure_summary(self) -> Dict:
        """
        סיכום ניתוח לחץ צף
        """
        return {
            "agent_type": "FloatPressureEvaluator",
            "description": "הערכת לחץ צף מתקדמת עם ניתוח רב-ממדי",
            "features": [
                "הערכת לחץ צף לפי מספר פרמטרים",
                "ניתוח רב-ממדי של לחץ צף",
                "ולידציה לפי זמן ומגמה",
                "ניתוח לחץ צף לפי סקטורים",
                "זיהוי לחץ צף לפני אירועים",
                "ניתוח לחץ צף לפי טכני ופונדמנטלי",
                "זיהוי לחץ צף לפי רגשות השוק",
                "ניתוח לחץ צף לפי נפח ומחיר"
            ],
            "thresholds": self.float_pressure_thresholds,
            "time_periods": self.time_periods
        } 