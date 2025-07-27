"""
VolumeSpikeAgent - זיהוי קפיצות נפח מתקדם
============================================

סוכן מתקדם לזיהוי קפיצות נפח משמעותיות עם ניתוח היסטורי,
ולידציה מתקדמת ומבנה Signal תקני.

תכונות מתקדמות:
- זיהוי קפיצות נפח יחסיות ומוחלטות
- ניתוח היסטורי של דפוסי נפח
- ולידציה לפי זמן ומגמה
- ניתוח נפח לפי מחיר
- זיהוי נפח חריג (Unusual Volume)
- ניתוח נפח לפי שעות מסחר
- זיהוי נפח לפני אירועים
- ניתוח נפח לפי סקטורים
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from utils.data_fetcher import data_fetcher
from utils.constants import VOLUME_THRESHOLDS, TIME_PERIODS
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VolumeSpike:
    """מבנה נתונים לקפיצת נפח"""
    timestamp: datetime
    volume: float
    price: float
    avg_volume: float
    volume_ratio: float
    spike_type: str
    confidence: float
    significance: str
    context: Dict

@dataclass
class VolumeAnalysis:
    """מבנה נתונים לניתוח נפח מתקדם"""
    total_spikes: int
    significant_spikes: int
    avg_volume_ratio: float
    volume_trend: str
    unusual_volume_count: int
    sector_comparison: Dict
    time_analysis: Dict
    price_volume_correlation: float

class VolumeSpikeAgent:
    """
    סוכן מתקדם לזיהוי קפיצות נפח משמעותיות
    
    תכונות מתקדמות:
    - זיהוי קפיצות נפח יחסיות ומוחלטות
    - ניתוח היסטורי של דפוסי נפח
    - ולידציה לפי זמן ומגמה
    - ניתוח נפח לפי מחיר
    - זיהוי נפח חריג (Unusual Volume)
    - ניתוח נפח לפי שעות מסחר
    - זיהוי נפח לפני אירועים
    - ניתוח נפח לפי סקטורים
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        self.config = config or {}
        
        # הגדרות מתקדמות
        self.volume_thresholds = {
            'low': 1.5,      # קפיצה נמוכה
            'medium': 2.5,   # קפיצה בינונית
            'high': 4.0,     # קפיצה גבוהה
            'extreme': 8.0   # קפיצה קיצונית
        }
        
        self.time_periods = {
            'short': 5,      # 5 ימים
            'medium': 20,    # 20 ימים
            'long': 60       # 60 ימים
        }
        
        self.significance_weights = {
            'volume_ratio': 0.3,
            'price_movement': 0.2,
            'time_context': 0.15,
            'sector_comparison': 0.15,
            'historical_pattern': 0.2
        }
        
        # קטגוריות קפיצות נפח
        self.spike_categories = {
            'earnings_related': ['earnings', 'report', 'guidance'],
            'news_related': ['news', 'announcement', 'press'],
            'technical_breakout': ['breakout', 'resistance', 'support'],
            'sector_movement': ['sector', 'industry', 'peer'],
            'institutional': ['institutional', 'block', 'large']
        }
        
        logger.info("VolumeSpikeAgent initialized with advanced configuration")

    def _calculate_volume_metrics(self, df: pd.DataFrame) -> Dict:
        """
        חישוב מדדי נפח מתקדמים
        """
        try:
            # חישוב ממוצעים נעים של נפח
            df['volume_sma_5'] = df['volume'].rolling(window=5).mean()
            df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
            df['volume_sma_60'] = df['volume'].rolling(window=60).mean()
            
            # חישוב סטיית תקן של נפח
            df['volume_std_20'] = df['volume'].rolling(window=20).std()
            
            # חישוב יחסי נפח
            df['volume_ratio_5'] = df['volume'] / df['volume_sma_5']
            df['volume_ratio_20'] = df['volume'] / df['volume_sma_20']
            df['volume_ratio_60'] = df['volume'] / df['volume_sma_60']
            
            # חישוב זרועות בולינגר של נפח
            df['volume_bb_upper'] = df['volume_sma_20'] + (df['volume_std_20'] * 2)
            df['volume_bb_lower'] = df['volume_sma_20'] - (df['volume_std_20'] * 2)
            
            # חישוב מדד נפח יחסי
            df['relative_volume'] = df['volume'] / df['volume_sma_20']
            
            # חישוב נפח לפי מחיר
            df['price_volume_ratio'] = df['volume'] / df['close']
            
            return {
                'volume_metrics': df,
                'avg_volume_20': df['volume_sma_20'].iloc[-1],
                'volume_volatility': df['volume_std_20'].iloc[-1],
                'current_volume_ratio': df['volume_ratio_20'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume metrics: {e}")
            return {}

    def _detect_volume_spikes(self, df: pd.DataFrame) -> List[VolumeSpike]:
        """
        זיהוי קפיצות נפח מתקדם
        """
        spikes = []
        
        try:
            # זיהוי קפיצות לפי סף יחסי
            for i in range(20, len(df)):
                current_volume = df['volume'].iloc[i]
                avg_volume_20 = df['volume_sma_20'].iloc[i]
                volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
                
                # זיהוי קפיצה משמעותית
                if volume_ratio >= self.volume_thresholds['low']:
                    # ניתוח הקשר
                    price_change = (df['close'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1]
                    time_context = self._analyze_time_context(df, i)
                    sector_comparison = self._analyze_sector_context(df, i)
                    historical_pattern = self._analyze_historical_pattern(df, i)
                    
                    # חישוב ביטחון
                    confidence = self._calculate_spike_confidence(
                        volume_ratio, price_change, time_context, 
                        sector_comparison, historical_pattern
                    )
                    
                    # קביעת סוג קפיצה
                    spike_type = self._classify_spike_type(
                        volume_ratio, price_change, time_context
                    )
                    
                    # קביעת משמעות
                    significance = self._determine_significance(volume_ratio, confidence)
                    
                    spike = VolumeSpike(
                        timestamp=df.index[i],
                        volume=current_volume,
                        price=df['close'].iloc[i],
                        avg_volume=avg_volume_20,
                        volume_ratio=volume_ratio,
                        spike_type=spike_type,
                        confidence=confidence,
                        significance=significance,
                        context={
                            'price_change': price_change,
                            'time_context': time_context,
                            'sector_comparison': sector_comparison,
                            'historical_pattern': historical_pattern
                        }
                    )
                    
                    spikes.append(spike)
            
            return spikes
            
        except Exception as e:
            logger.error(f"Error detecting volume spikes: {e}")
            return []

    def _analyze_time_context(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח הקשר זמן מתקדם
        """
        try:
            current_time = df.index[index]
            
            # ניתוח לפי שעות מסחר
            hour = current_time.hour
            trading_hour_volume = df[df.index.hour == hour]['volume'].mean()
            
            # ניתוח לפי ימי שבוע
            day_of_week = current_time.weekday()
            day_volume = df[df.index.weekday == day_of_week]['volume'].mean()
            
            # ניתוח לפי חודש
            month = current_time.month
            month_volume = df[df.index.month == month]['volume'].mean()
            
            # ניתוח נפח לפני אירועים
            event_proximity = self._analyze_event_proximity(df, index)
            
            return {
                'hour_analysis': {
                    'current_hour': hour,
                    'hour_avg_volume': trading_hour_volume,
                    'hour_volume_ratio': df['volume'].iloc[index] / trading_hour_volume if trading_hour_volume > 0 else 1
                },
                'day_analysis': {
                    'day_of_week': day_of_week,
                    'day_avg_volume': day_volume,
                    'day_volume_ratio': df['volume'].iloc[index] / day_volume if day_volume > 0 else 1
                },
                'month_analysis': {
                    'month': month,
                    'month_avg_volume': month_volume,
                    'month_volume_ratio': df['volume'].iloc[index] / month_volume if month_volume > 0 else 1
                },
                'event_proximity': event_proximity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time context: {e}")
            return {}

    def _analyze_sector_context(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח הקשר סקטור מתקדם
        """
        try:
            # סימולציה של נתוני סקטור (בפרודקציה יהיה מ-API)
            sector_data = {
                'technology': {'avg_volume_ratio': 1.2, 'volume_trend': 'increasing'},
                'healthcare': {'avg_volume_ratio': 1.1, 'volume_trend': 'stable'},
                'finance': {'avg_volume_ratio': 1.3, 'volume_trend': 'decreasing'},
                'energy': {'avg_volume_ratio': 1.5, 'volume_trend': 'increasing'}
            }
            
            # קביעת סקטור (בפרודקציה יהיה מ-API)
            sector = 'technology'  # ברירת מחדל
            
            sector_info = sector_data.get(sector, {'avg_volume_ratio': 1.0, 'volume_trend': 'stable'})
            
            return {
                'sector': sector,
                'sector_avg_volume_ratio': sector_info['avg_volume_ratio'],
                'sector_volume_trend': sector_info['volume_trend'],
                'relative_to_sector': df['volume'].iloc[index] / (df['volume_sma_20'].iloc[index] * sector_info['avg_volume_ratio'])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector context: {e}")
            return {}

    def _analyze_historical_pattern(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח דפוס היסטורי מתקדם
        """
        try:
            # ניתוח דפוסי נפח היסטוריים
            historical_window = df.iloc[max(0, index-60):index]
            
            # חישוב תדירות קפיצות נפח
            volume_spikes_count = len(historical_window[historical_window['volume_ratio_20'] >= 2.0])
            spike_frequency = volume_spikes_count / len(historical_window) if len(historical_window) > 0 else 0
            
            # ניתוח מגמת נפח
            volume_trend = 'increasing' if df['volume_sma_20'].iloc[index] > df['volume_sma_20'].iloc[max(0, index-20)] else 'decreasing'
            
            # ניתוח עונתיות נפח
            seasonal_pattern = self._analyze_seasonal_pattern(df, index)
            
            return {
                'spike_frequency': spike_frequency,
                'volume_trend': volume_trend,
                'seasonal_pattern': seasonal_pattern,
                'historical_avg_ratio': historical_window['volume_ratio_20'].mean()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing historical pattern: {e}")
            return {}

    def _analyze_event_proximity(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח קרבה לאירועים
        """
        try:
            # סימולציה של אירועים קרובים (בפרודקציה יהיה מ-API)
            events = {
                'earnings': {'days_away': 3, 'impact': 'high'},
                'dividend': {'days_away': 7, 'impact': 'medium'},
                'conference': {'days_away': 1, 'impact': 'medium'}
            }
            
            current_date = df.index[index]
            closest_event = None
            min_days = float('inf')
            
            for event_type, event_info in events.items():
                days_diff = abs((current_date - pd.Timestamp.now()).days - event_info['days_away'])
                if days_diff < min_days:
                    min_days = days_diff
                    closest_event = {'type': event_type, 'days_away': event_info['days_away'], 'impact': event_info['impact']}
            
            return {
                'closest_event': closest_event,
                'event_proximity_score': max(0, 1 - (min_days / 30)) if min_days != float('inf') else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing event proximity: {e}")
            return {}

    def _analyze_seasonal_pattern(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח דפוס עונתי
        """
        try:
            current_date = df.index[index]
            
            # ניתוח לפי רבעון
            quarter = (current_date.month - 1) // 3 + 1
            quarter_data = df[df.index.quarter == quarter]
            quarter_avg_volume = quarter_data['volume'].mean() if len(quarter_data) > 0 else df['volume'].mean()
            
            # ניתוח לפי חודש
            month_data = df[df.index.month == current_date.month]
            month_avg_volume = month_data['volume'].mean() if len(month_data) > 0 else df['volume'].mean()
            
            return {
                'quarter': quarter,
                'quarter_avg_volume': quarter_avg_volume,
                'month': current_date.month,
                'month_avg_volume': month_avg_volume,
                'seasonal_factor': quarter_avg_volume / df['volume'].mean() if df['volume'].mean() > 0 else 1
            }
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal pattern: {e}")
            return {}

    def _calculate_spike_confidence(self, volume_ratio: float, price_change: float, 
                                  time_context: Dict, sector_comparison: Dict, 
                                  historical_pattern: Dict) -> float:
        """
        חישוב ביטחון קפיצת נפח מתקדם
        """
        try:
            # משקלים לפי חשיבות
            weights = self.significance_weights
            
            # ניקוד לפי יחס נפח
            volume_score = min(1.0, volume_ratio / self.volume_thresholds['extreme'])
            
            # ניקוד לפי תנועת מחיר
            price_score = min(1.0, abs(price_change) * 10)
            
            # ניקוד לפי הקשר זמן
            time_score = time_context.get('hour_analysis', {}).get('hour_volume_ratio', 1.0)
            time_score = min(1.0, time_score / 2.0)
            
            # ניקוד לפי השוואה סקטורית
            sector_score = sector_comparison.get('relative_to_sector', 1.0)
            sector_score = min(1.0, sector_score / 2.0)
            
            # ניקוד לפי דפוס היסטורי
            historical_score = 1.0 - historical_pattern.get('spike_frequency', 0.0)
            
            # חישוב ביטחון סופי
            confidence = (
                volume_score * weights['volume_ratio'] +
                price_score * weights['price_movement'] +
                time_score * weights['time_context'] +
                sector_score * weights['sector_comparison'] +
                historical_score * weights['historical_pattern']
            )
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating spike confidence: {e}")
            return 0.5

    def _classify_spike_type(self, volume_ratio: float, price_change: float, time_context: Dict) -> str:
        """
        סיווג סוג קפיצת נפח
        """
        try:
            if volume_ratio >= self.volume_thresholds['extreme']:
                return 'extreme_volume'
            elif volume_ratio >= self.volume_thresholds['high']:
                return 'high_volume'
            elif volume_ratio >= self.volume_thresholds['medium']:
                return 'medium_volume'
            elif volume_ratio >= self.volume_thresholds['low']:
                return 'low_volume'
            else:
                return 'normal_volume'
                
        except Exception as e:
            logger.error(f"Error classifying spike type: {e}")
            return 'unknown'

    def _determine_significance(self, volume_ratio: float, confidence: float) -> str:
        """
        קביעת משמעות קפיצת נפח
        """
        try:
            if volume_ratio >= self.volume_thresholds['extreme'] and confidence >= 0.8:
                return 'extreme'
            elif volume_ratio >= self.volume_thresholds['high'] and confidence >= 0.6:
                return 'high'
            elif volume_ratio >= self.volume_thresholds['medium'] and confidence >= 0.4:
                return 'medium'
            elif volume_ratio >= self.volume_thresholds['low'] and confidence >= 0.2:
                return 'low'
            else:
                return 'minimal'
                
        except Exception as e:
            logger.error(f"Error determining significance: {e}")
            return 'unknown'

    def _calculate_volume_analysis(self, df: pd.DataFrame, spikes: List[VolumeSpike]) -> VolumeAnalysis:
        """
        חישוב ניתוח נפח מתקדם
        """
        try:
            # חישוב סטטיסטיקות בסיסיות
            total_spikes = len(spikes)
            significant_spikes = len([s for s in spikes if s.significance in ['high', 'extreme']])
            
            # חישוב ממוצע יחסי נפח
            avg_volume_ratio = np.mean([s.volume_ratio for s in spikes]) if spikes else 1.0
            
            # ניתוח מגמת נפח
            recent_volume = df['volume'].tail(20).mean()
            historical_volume = df['volume'].tail(60).mean()
            volume_trend = 'increasing' if recent_volume > historical_volume else 'decreasing'
            
            # ניתוח נפח חריג
            unusual_volume_count = len([s for s in spikes if s.volume_ratio >= 3.0])
            
            # ניתוח סקטור
            sector_comparison = self._analyze_sector_context(df, len(df)-1)
            
            # ניתוח זמן
            time_analysis = self._analyze_time_context(df, len(df)-1)
            
            # ניתוח קורלציה מחיר-נפח
            price_volume_correlation = df['close'].corr(df['volume'])
            
            return VolumeAnalysis(
                total_spikes=total_spikes,
                significant_spikes=significant_spikes,
                avg_volume_ratio=avg_volume_ratio,
                volume_trend=volume_trend,
                unusual_volume_count=unusual_volume_count,
                sector_comparison=sector_comparison,
                time_analysis=time_analysis,
                price_volume_correlation=price_volume_correlation
            )
            
        except Exception as e:
            logger.error(f"Error calculating volume analysis: {e}")
            return VolumeAnalysis(0, 0, 1.0, 'unknown', 0, {}, {}, 0.0)

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של קפיצות נפח
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
                        "type": "volume_spike",
                        "score": 50,
                        "reason": "לא ניתן לאחזר נתוני מחיר",
                        "confidence": 0.5,
                        "details": {
                            "spikes_count": 0,
                            "avg_volume_ratio": 1.0,
                            "volume_trend": "unknown"
                        }
                    },
                    "details": {
                        "spikes": [],
                        "analysis": {},
                        "recommendations": []
                    }
                }
            
            # חישוב מדדי נפח
            volume_metrics = self._calculate_volume_metrics(price_df)
            
            # זיהוי קפיצות נפח
            spikes = self._detect_volume_spikes(price_df)
            
            # ניתוח מתקדם
            analysis = self._calculate_volume_analysis(price_df, spikes)
            
            # חישוב ציון סופי
            if spikes:
                # חישוב ציון לפי קפיצות משמעותיות
                significant_ratio = analysis.significant_spikes / max(1, analysis.total_spikes)
                volume_score = min(100, significant_ratio * 100 + analysis.avg_volume_ratio * 20)
                
                # התאמה לפי מגמה
                if analysis.volume_trend == 'increasing':
                    volume_score *= 1.1
                elif analysis.volume_trend == 'decreasing':
                    volume_score *= 0.9
                
                volume_score = min(100, max(0, volume_score))
            else:
                volume_score = 50
            
            # יצירת הסבר
            if spikes:
                recent_spikes = [s for s in spikes if s.significance in ['high', 'extreme']]
                explanation = f"זוהו {len(spikes)} קפיצות נפח ({len(recent_spikes)} משמעותיות). ממוצע יחס: {analysis.avg_volume_ratio:.2f}, מגמה: {analysis.volume_trend}"
            else:
                explanation = "לא זוהו קפיצות נפח משמעותיות"
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(spikes, analysis)
            
            return {
                "score": round(volume_score, 1),
                "explanation": explanation,
                "signal": {
                    "type": "volume_spike",
                    "score": round(volume_score, 1),
                    "reason": explanation,
                    "confidence": round(analysis.price_volume_correlation, 3),
                    "details": {
                        "spikes_count": analysis.total_spikes,
                        "significant_spikes": analysis.significant_spikes,
                        "avg_volume_ratio": round(analysis.avg_volume_ratio, 2),
                        "volume_trend": analysis.volume_trend,
                        "unusual_volume_count": analysis.unusual_volume_count
                    }
                },
                "details": {
                    "spikes": [
                        {
                            "timestamp": spike.timestamp.isoformat(),
                            "volume_ratio": round(spike.volume_ratio, 2),
                            "type": spike.spike_type,
                            "significance": spike.significance,
                            "confidence": round(spike.confidence, 3)
                        }
                        for spike in spikes[:10]  # Top 10 spikes
                    ],
                    "analysis": {
                        "total_spikes": analysis.total_spikes,
                        "significant_spikes": analysis.significant_spikes,
                        "avg_volume_ratio": round(analysis.avg_volume_ratio, 2),
                        "volume_trend": analysis.volume_trend,
                        "unusual_volume_count": analysis.unusual_volume_count,
                        "price_volume_correlation": round(analysis.price_volume_correlation, 3),
                        "sector_comparison": analysis.sector_comparison,
                        "time_analysis": analysis.time_analysis
                    },
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"Error in VolumeSpikeAgent.analyze: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח: {str(e)}",
                "signal": {
                    "type": "volume_spike",
                    "score": 50,
                    "reason": f"שגיאה בניתוח: {str(e)}",
                    "confidence": 0.5,
                    "details": {
                        "spikes_count": 0,
                        "avg_volume_ratio": 1.0,
                        "volume_trend": "error"
                    }
                },
                "details": {
                    "spikes": [],
                    "analysis": {},
                    "recommendations": []
                }
            }

    def _generate_recommendations(self, spikes: List[VolumeSpike], analysis: VolumeAnalysis) -> List[str]:
        """
        יצירת המלצות מתקדמות
        """
        recommendations = []
        
        try:
            if analysis.significant_spikes > 0:
                recommendations.append("🔍 מעקב אחר קפיצות נפח משמעותיות - פוטנציאל לתנועה חזקה")
            
            if analysis.avg_volume_ratio > 2.0:
                recommendations.append("📈 נפח גבוה מהרגיל - בדוק חדשות או אירועים קרובים")
            
            if analysis.volume_trend == 'increasing':
                recommendations.append("📊 מגמת נפח עולה - עניין גובר במניה")
            
            if analysis.unusual_volume_count > 3:
                recommendations.append("⚠️ מספר קפיצות חריגות - בדוק פעילות מוסדית")
            
            if analysis.price_volume_correlation > 0.7:
                recommendations.append("💪 קורלציה גבוהה מחיר-נפח - תמיכה חזקה בתנועה")
            
            if not recommendations:
                recommendations.append("📉 נפח יציב - אין סיגנלים משמעותיים")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["שגיאה ביצירת המלצות"]

    def get_volume_summary(self) -> Dict:
        """
        סיכום ניתוח נפח
        """
        return {
            "agent_type": "VolumeSpikeAgent",
            "description": "זיהוי קפיצות נפח מתקדם עם ניתוח היסטורי וולידציה",
            "features": [
                "זיהוי קפיצות נפח יחסיות ומוחלטות",
                "ניתוח היסטורי של דפוסי נפח",
                "ולידציה לפי זמן ומגמה",
                "ניתוח נפח לפי מחיר",
                "זיהוי נפח חריג (Unusual Volume)",
                "ניתוח נפח לפי שעות מסחר",
                "זיהוי נפח לפני אירועים",
                "ניתוח נפח לפי סקטורים"
            ],
            "thresholds": self.volume_thresholds,
            "time_periods": self.time_periods
        } 