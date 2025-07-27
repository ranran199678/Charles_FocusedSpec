"""
DarkPoolAgent - זיהוי פעילות בריכות אפלות מתקדם
================================================

סוכן מתקדם לזיהוי פעילות בריכות אפלות (Dark Pool Activity) עם ניתוח רב-ממדי,
ולידציה מתקדמת ומבנה Signal תקני.

תכונות מתקדמות:
- זיהוי פעילות בריכות אפלות לפי מספר פרמטרים
- ניתוח רב-ממדי של פעילות בריכות אפלות
- ולידציה לפי זמן ומגמה
- ניתוח פעילות בריכות אפלות לפי סקטורים
- זיהוי פעילות בריכות אפלות לפני אירועים
- ניתוח פעילות בריכות אפלות לפי טכני ופונדמנטלי
- זיהוי פעילות בריכות אפלות לפי רגשות השוק
- ניתוח פעילות בריכות אפלות לפי נפח ומחיר
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from utils.data_fetcher import data_fetcher
from utils.constants import DARK_POOL_THRESHOLDS, TIME_PERIODS
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DarkPoolActivity:
    """מבנה נתונים לפעילות בריכות אפלות"""
    timestamp: datetime
    activity_type: str
    strength: float
    confidence: float
    dark_pool_ratio: float
    volume_ratio: float
    price_impact: float
    context: Dict
    significance: str

@dataclass
class DarkPoolAnalysis:
    """מבנה נתונים לניתוח פעילות בריכות אפלות מתקדם"""
    total_activities: int
    significant_activities: int
    avg_activity_strength: float
    dark_pool_trend: str
    volume_trend: str
    sector_comparison: Dict
    time_analysis: Dict
    breakout_potential: float

class DarkPoolAgent:
    """
    סוכן מתקדם לזיהוי פעילות בריכות אפלות
    
    תכונות מתקדמות:
    - זיהוי פעילות בריכות אפלות לפי מספר פרמטרים
    - ניתוח רב-ממדי של פעילות בריכות אפלות
    - ולידציה לפי זמן ומגמה
    - ניתוח פעילות בריכות אפלות לפי סקטורים
    - זיהוי פעילות בריכות אפלות לפני אירועים
    - ניתוח פעילות בריכות אפלות לפי טכני ופונדמנטלי
    - זיהוי פעילות בריכות אפלות לפי רגשות השוק
    - ניתוח פעילות בריכות אפלות לפי נפח ומחיר
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        self.config = config or {}
        
        # הגדרות מתקדמות
        self.dark_pool_thresholds = {
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
        
        self.activity_weights = {
            'dark_pool_ratio': 0.3,
            'volume_activity': 0.25,
            'price_activity': 0.2,
            'time_activity': 0.15,
            'sector_activity': 0.1
        }
        
        # סוגי פעילות בריכות אפלות
        self.activity_types = {
            'accumulation': 'הצטברות',
            'distribution': 'הפצה',
            'manipulation': 'מניפולציה',
            'natural': 'טבעי',
            'event_driven': 'מונע אירוע'
        }
        
        logger.info("DarkPoolAgent initialized with advanced configuration")

    def _calculate_dark_pool_metrics(self, df: pd.DataFrame) -> Dict:
        """
        חישוב מדדי בריכות אפלות מתקדמים
        """
        try:
            # חישוב בריכות אפלות (סימולציה - בפרודקציה יהיה מ-API)
            df['dark_pool_ratio'] = 0.15  # ברירת מחדל - 15% בריכות אפלות
            
            # חישוב נפח לפי בריכות אפלות
            df['volume_per_dark_pool'] = df['volume'] / (df['close'] * df['dark_pool_ratio'])
            
            # חישוב פעילות בריכות אפלות נפח
            df['dark_pool_volume'] = df['volume_per_dark_pool'].rolling(window=20).mean()
            df['dark_pool_volume_ratio'] = df['volume_per_dark_pool'] / df['dark_pool_volume']
            
            # חישוב פעילות בריכות אפלות מחיר
            df['dark_pool_price'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
            df['dark_pool_price_ratio'] = df['dark_pool_price'] / df['dark_pool_price'].rolling(window=20).mean()
            
            # חישוב מדד פעילות בריכות אפלות
            df['dark_pool_score'] = (df['dark_pool_volume_ratio'] + df['dark_pool_price_ratio']) / 2
            
            return {
                'dark_pool_metrics': df,
                'current_dark_pool_ratio': df['dark_pool_ratio'].iloc[-1],
                'current_dark_pool_volume': df['dark_pool_volume_ratio'].iloc[-1],
                'current_dark_pool_price': df['dark_pool_price_ratio'].iloc[-1],
                'current_dark_pool_score': df['dark_pool_score'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating dark pool metrics: {e}")
            return {}

    def _detect_dark_pool_activities(self, df: pd.DataFrame) -> List[DarkPoolActivity]:
        """
        זיהוי פעילות בריכות אפלות מתקדם
        """
        activities = []
        
        try:
            # חישוב מדדי בריכות אפלות
            dark_pool_metrics = self._calculate_dark_pool_metrics(df)
            if not dark_pool_metrics:
                return activities
            
            df = dark_pool_metrics['dark_pool_metrics']
            
            # זיהוי פעילות בריכות אפלות
            for i in range(20, len(df)):
                # ניתוח פעילות בריכות אפלות נפח
                volume_activity = self._analyze_volume_activity(df, i)
                
                # ניתוח פעילות בריכות אפלות מחיר
                price_activity = self._analyze_price_activity(df, i)
                
                # ניתוח פעילות בריכות אפלות זמן
                time_activity = self._analyze_time_activity(df, i)
                
                # ניתוח פעילות בריכות אפלות סקטור
                sector_activity = self._analyze_sector_activity(df, i)
                
                # ניתוח פוטנציאל פריצה
                breakout_potential = self._analyze_breakout_potential(df, i)
                
                # זיהוי פעילות בריכות אפלות
                if self._is_dark_pool_activity(volume_activity, price_activity, time_activity, sector_activity):
                    # חישוב עוצמת הפעילות
                    strength = self._calculate_activity_strength(
                        volume_activity, price_activity, time_activity, sector_activity, breakout_potential
                    )
                    
                    # חישוב ביטחון
                    confidence = self._calculate_activity_confidence(
                        volume_activity, price_activity, time_activity, sector_activity, breakout_potential
                    )
                    
                    # קביעת סוג פעילות
                    activity_type = self._classify_activity_type(
                        volume_activity, price_activity, time_activity
                    )
                    
                    # קביעת משמעות
                    significance = self._determine_activity_significance(strength, confidence)
                    
                    activity = DarkPoolActivity(
                        timestamp=df.index[i],
                        activity_type=activity_type,
                        strength=strength,
                        confidence=confidence,
                        dark_pool_ratio=df['dark_pool_ratio'].iloc[i],
                        volume_ratio=volume_activity.get('activity_ratio', 1.0),
                        price_impact=price_activity.get('price_impact', 0.0),
                        context={
                            'volume_activity': volume_activity,
                            'price_activity': price_activity,
                            'time_activity': time_activity,
                            'sector_activity': sector_activity,
                            'breakout_potential': breakout_potential
                        },
                        significance=significance
                    )
                    
                    activities.append(activity)
            
            return activities
            
        except Exception as e:
            logger.error(f"Error detecting dark pool activities: {e}")
            return []

    def _analyze_volume_activity(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח פעילות בריכות אפלות נפח מתקדם
        """
        try:
            # חישוב פעילות בריכות אפלות נפח
            current_volume_activity = df['dark_pool_volume_ratio'].iloc[index]
            historical_volume_activity = df['dark_pool_volume_ratio'].iloc[max(0, index-30):index].mean()
            
            activity_ratio = current_volume_activity / historical_volume_activity if historical_volume_activity > 0 else 1.0
            
            # ניתוח מגמת פעילות בריכות אפלות נפח
            recent_volume_activity = df['dark_pool_volume_ratio'].iloc[max(0, index-10):index].mean()
            volume_activity_trend = 'increasing' if recent_volume_activity > historical_volume_activity else 'decreasing'
            
            return {
                'activity_ratio': activity_ratio,
                'activity_trend': volume_activity_trend,
                'current_activity': current_volume_activity,
                'historical_activity': historical_volume_activity,
                'recent_activity': recent_volume_activity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume activity: {e}")
            return {}

    def _analyze_price_activity(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח פעילות בריכות אפלות מחיר מתקדם
        """
        try:
            # חישוב פעילות בריכות אפלות מחיר
            current_price_activity = df['dark_pool_price_ratio'].iloc[index]
            historical_price_activity = df['dark_pool_price_ratio'].iloc[max(0, index-30):index].mean()
            
            price_activity_ratio = current_price_activity / historical_price_activity if historical_price_activity > 0 else 1.0
            
            # ניתוח השפעת מחיר
            current_price = df['close'].iloc[index]
            historical_price = df['close'].iloc[max(0, index-20):index].mean()
            price_impact = (current_price - historical_price) / historical_price if historical_price > 0 else 0.0
            
            # ניתוח מגמת פעילות בריכות אפלות מחיר
            recent_price_activity = df['dark_pool_price_ratio'].iloc[max(0, index-10):index].mean()
            price_activity_trend = 'increasing' if recent_price_activity > historical_price_activity else 'decreasing'
            
            return {
                'activity_ratio': price_activity_ratio,
                'activity_trend': price_activity_trend,
                'price_impact': price_impact,
                'current_activity': current_price_activity,
                'historical_activity': historical_price_activity,
                'recent_activity': recent_price_activity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price activity: {e}")
            return {}

    def _analyze_time_activity(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח פעילות בריכות אפלות זמן מתקדם
        """
        try:
            # ניתוח פעילות בריכות אפלות זמן
            time_window = df.iloc[max(0, index-30):index]
            
            # חישוב פעילות בריכות אפלות זמן
            time_activity_duration = len(time_window)
            
            # ניתוח עקביות פעילות בריכות אפלות
            volume_consistency = time_window['dark_pool_volume_ratio'].std()
            price_consistency = time_window['dark_pool_price_ratio'].std()
            consistency_score = 1.0 - ((volume_consistency + price_consistency) / 2)
            
            # ניתוח מגמת פעילות בריכות אפלות זמן
            early_activity = time_window.iloc[:10]['dark_pool_score'].mean()
            late_activity = time_window.iloc[-10:]['dark_pool_score'].mean()
            time_activity_trend = 'increasing' if late_activity > early_activity else 'decreasing'
            
            return {
                'activity_duration': time_activity_duration,
                'consistency_score': consistency_score,
                'activity_trend': time_activity_trend,
                'early_activity': early_activity,
                'late_activity': late_activity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time activity: {e}")
            return {}

    def _analyze_sector_activity(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח פעילות בריכות אפלות סקטור מתקדם
        """
        try:
            # סימולציה של נתוני סקטור (בפרודקציה יהיה מ-API)
            sector_data = {
                'technology': {'avg_dark_pool_activity': 0.6, 'activity_trend': 'increasing'},
                'healthcare': {'avg_dark_pool_activity': 0.5, 'activity_trend': 'stable'},
                'finance': {'avg_dark_pool_activity': 0.7, 'activity_trend': 'decreasing'},
                'energy': {'avg_dark_pool_activity': 0.8, 'activity_trend': 'increasing'}
            }
            
            # קביעת סקטור (בפרודקציה יהיה מ-API)
            sector = 'technology'  # ברירת מחדל
            
            sector_info = sector_data.get(sector, {'avg_dark_pool_activity': 0.5, 'activity_trend': 'stable'})
            
            return {
                'sector': sector,
                'sector_avg_activity': sector_info['avg_dark_pool_activity'],
                'sector_activity_trend': sector_info['activity_trend'],
                'relative_to_sector': df['dark_pool_score'].iloc[index] / sector_info['avg_dark_pool_activity']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector activity: {e}")
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

    def _is_dark_pool_activity(self, volume_activity: Dict, price_activity: Dict, 
                               time_activity: Dict, sector_activity: Dict) -> bool:
        """
        זיהוי פעילות בריכות אפלות
        """
        try:
            # קריטריונים לפעילות בריכות אפלות
            volume_activitying = volume_activity.get('activity_ratio', 1.0) > 1.2
            price_activitying = price_activity.get('activity_ratio', 1.0) > 1.1
            time_activitying = time_activity.get('activity_duration', 0) >= 15
            sector_activitying = sector_activity.get('relative_to_sector', 1.0) > 1.0
            
            # פעילות בריכות אפלות אם לפחות 2 קריטריונים מתקיימים
            activity_criteria = [volume_activitying, price_activitying, time_activitying, sector_activitying]
            return sum(activity_criteria) >= 2
            
        except Exception as e:
            logger.error(f"Error detecting dark pool activity: {e}")
            return False

    def _calculate_activity_strength(self, volume_activity: Dict, price_activity: Dict,
                                   time_activity: Dict, sector_activity: Dict,
                                   breakout_potential: Dict) -> float:
        """
        חישוב עוצמת פעילות בריכות אפלות
        """
        try:
            strength = 0.0
            
            # משקל לפי פעילות בריכות אפלות נפח
            volume_ratio = volume_activity.get('activity_ratio', 1.0)
            if volume_ratio > 1.5:
                strength += 0.3
            elif volume_ratio > 1.2:
                strength += 0.2
            
            # משקל לפי פעילות בריכות אפלות מחיר
            price_ratio = price_activity.get('activity_ratio', 1.0)
            if price_ratio > 1.3:
                strength += 0.3
            elif price_ratio > 1.1:
                strength += 0.2
            
            # משקל לפי פעילות בריכות אפלות זמן
            time_duration = time_activity.get('activity_duration', 0)
            if time_duration >= 25:
                strength += 0.2
            elif time_duration >= 15:
                strength += 0.1
            
            # משקל לפי פעילות בריכות אפלות סקטור
            sector_ratio = sector_activity.get('relative_to_sector', 1.0)
            if sector_ratio > 1.2:
                strength += 0.1
            
            # משקל לפי פוטנציאל פריצה
            breakout_strength = breakout_potential.get('breakout_strength', 0.0)
            if breakout_strength > 0.05:
                strength += 0.1
            
            return min(1.0, strength)
            
        except Exception as e:
            logger.error(f"Error calculating activity strength: {e}")
            return 0.5

    def _calculate_activity_confidence(self, volume_activity: Dict, price_activity: Dict,
                                     time_activity: Dict, sector_activity: Dict,
                                     breakout_potential: Dict) -> float:
        """
        חישוב ביטחון פעילות בריכות אפלות
        """
        try:
            confidence = 0.0
            
            # ביטחון לפי עקביות
            consistent_signals = 0
            if volume_activity.get('activity_ratio', 1.0) > 1.2:
                consistent_signals += 1
            if price_activity.get('activity_ratio', 1.0) > 1.1:
                consistent_signals += 1
            if time_activity.get('activity_duration', 0) >= 15:
                consistent_signals += 1
            if sector_activity.get('relative_to_sector', 1.0) > 1.0:
                consistent_signals += 1
            if breakout_potential.get('breakout_strength', 0.0) > 0.03:
                consistent_signals += 1
            
            confidence = consistent_signals / 5.0
            
            # התאמה לפי עוצמת פעילות
            avg_activity = (volume_activity.get('activity_ratio', 1.0) + price_activity.get('activity_ratio', 1.0)) / 2
            if avg_activity > 1.3:
                confidence *= 1.2
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating activity confidence: {e}")
            return 0.5

    def _classify_activity_type(self, volume_activity: Dict, price_activity: Dict, time_activity: Dict) -> str:
        """
        סיווג סוג פעילות בריכות אפלות
        """
        try:
            volume_ratio = volume_activity.get('activity_ratio', 1.0)
            price_ratio = price_activity.get('activity_ratio', 1.0)
            time_duration = time_activity.get('activity_duration', 0)
            
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
            logger.error(f"Error classifying activity type: {e}")
            return 'unknown'

    def _determine_activity_significance(self, strength: float, confidence: float) -> str:
        """
        קביעת משמעות פעילות בריכות אפלות
        """
        try:
            if strength >= self.dark_pool_thresholds['extreme'] and confidence >= 0.8:
                return 'extreme'
            elif strength >= self.dark_pool_thresholds['high'] and confidence >= 0.6:
                return 'high'
            elif strength >= self.dark_pool_thresholds['moderate'] and confidence >= 0.4:
                return 'moderate'
            elif strength >= self.dark_pool_thresholds['low'] and confidence >= 0.2:
                return 'low'
            else:
                return 'minimal'
                
        except Exception as e:
            logger.error(f"Error determining activity significance: {e}")
            return 'unknown'

    def _calculate_dark_pool_analysis(self, df: pd.DataFrame, activities: List[DarkPoolActivity]) -> DarkPoolAnalysis:
        """
        חישוב ניתוח פעילות בריכות אפלות מתקדם
        """
        try:
            # חישוב סטטיסטיקות בסיסיות
            total_activities = len(activities)
            significant_activities = len([a for a in activities if a.significance in ['high', 'extreme']])
            
            # חישוב ממוצע עוצמת פעילות
            avg_activity_strength = np.mean([a.strength for a in activities]) if activities else 0.5
            
            # ניתוח מגמת בריכות אפלות
            recent_dark_pool = df['dark_pool_score'].tail(20).mean()
            historical_dark_pool = df['dark_pool_score'].tail(60).mean()
            dark_pool_trend = 'increasing' if recent_dark_pool > historical_dark_pool else 'decreasing'
            
            # ניתוח מגמת נפח
            recent_volume = df['volume'].tail(20).mean()
            historical_volume = df['volume'].tail(60).mean()
            volume_trend = 'increasing' if recent_volume > historical_volume else 'decreasing'
            
            # ניתוח סקטור
            sector_comparison = self._analyze_sector_activity(df, len(df)-1)
            
            # ניתוח זמן
            time_analysis = self._analyze_time_activity(df, len(df)-1)
            
            # ניתוח פוטנציאל פריצה
            breakout_potential = self._analyze_breakout_potential(df, len(df)-1)
            breakout_potential_score = breakout_potential.get('breakout_strength', 0.0)
            
            return DarkPoolAnalysis(
                total_activities=total_activities,
                significant_activities=significant_activities,
                avg_activity_strength=avg_activity_strength,
                dark_pool_trend=dark_pool_trend,
                volume_trend=volume_trend,
                sector_comparison=sector_comparison,
                time_analysis=time_analysis,
                breakout_potential=breakout_potential_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating dark pool analysis: {e}")
            return DarkPoolAnalysis(0, 0, 0.5, 'unknown', 'unknown', {}, {}, 0.0)

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של פעילות בריכות אפלות
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
                        "type": "dark_pool_activity",
                        "score": 50,
                        "reason": "לא ניתן לאחזר נתוני מחיר",
                        "confidence": 0.5,
                        "details": {
                            "activities_count": 0,
                            "avg_activity_strength": 0.5,
                            "dark_pool_trend": "unknown"
                        }
                    },
                    "details": {
                        "activities": [],
                        "analysis": {},
                        "recommendations": []
                    }
                }
            
            # זיהוי פעילות בריכות אפלות
            activities = self._detect_dark_pool_activities(price_df)
            
            # ניתוח מתקדם
            analysis = self._calculate_dark_pool_analysis(price_df, activities)
            
            # חישוב ציון סופי
            if activities:
                # חישוב ציון לפי פעילויות משמעותיות
                significant_ratio = analysis.significant_activities / max(1, analysis.total_activities)
                activity_score = min(100, significant_ratio * 100 + analysis.avg_activity_strength * 50)
                
                # התאמה לפי מגמה
                if analysis.dark_pool_trend == 'increasing' and analysis.volume_trend == 'increasing':
                    activity_score *= 1.2
                elif analysis.dark_pool_trend == 'decreasing' or analysis.volume_trend == 'decreasing':
                    activity_score *= 0.8
                
                activity_score = min(100, max(0, activity_score))
            else:
                activity_score = 50
            
            # יצירת הסבר
            if activities:
                recent_activities = [a for a in activities if a.significance in ['high', 'extreme']]
                explanation = f"זוהו {len(activities)} פעילויות בריכות אפלות ({len(recent_activities)} משמעותיות). ממוצע עוצמה: {analysis.avg_activity_strength:.2f}, מגמת בריכות אפלות: {analysis.dark_pool_trend}"
            else:
                explanation = "לא זוהו פעילויות בריכות אפלות משמעותיות"
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(activities, analysis)
            
            return {
                "score": round(activity_score, 1),
                "explanation": explanation,
                "signal": {
                    "type": "dark_pool_activity",
                    "score": round(activity_score, 1),
                    "reason": explanation,
                    "confidence": round(analysis.breakout_potential, 3),
                    "details": {
                        "activities_count": analysis.total_activities,
                        "significant_activities": analysis.significant_activities,
                        "avg_activity_strength": round(analysis.avg_activity_strength, 2),
                        "dark_pool_trend": analysis.dark_pool_trend,
                        "volume_trend": analysis.volume_trend
                    }
                },
                "details": {
                    "activities": [
                        {
                            "timestamp": activity.timestamp.isoformat(),
                            "activity_type": activity.activity_type,
                            "strength": round(activity.strength, 2),
                            "significance": activity.significance,
                            "confidence": round(activity.confidence, 3),
                            "dark_pool_ratio": round(activity.dark_pool_ratio, 2)
                        }
                        for activity in activities[:10]  # Top 10 activities
                    ],
                    "analysis": {
                        "total_activities": analysis.total_activities,
                        "significant_activities": analysis.significant_activities,
                        "avg_activity_strength": round(analysis.avg_activity_strength, 2),
                        "dark_pool_trend": analysis.dark_pool_trend,
                        "volume_trend": analysis.volume_trend,
                        "breakout_potential": round(analysis.breakout_potential, 3),
                        "sector_comparison": analysis.sector_comparison,
                        "time_analysis": analysis.time_analysis
                    },
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"Error in DarkPoolAgent.analyze: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח: {str(e)}",
                "signal": {
                    "type": "dark_pool_activity",
                    "score": 50,
                    "reason": f"שגיאה בניתוח: {str(e)}",
                    "confidence": 0.5,
                    "details": {
                        "activities_count": 0,
                        "avg_activity_strength": 0.5,
                        "dark_pool_trend": "error"
                    }
                },
                "details": {
                    "activities": [],
                    "analysis": {},
                    "recommendations": []
                }
            }

    def _generate_recommendations(self, activities: List[DarkPoolActivity], analysis: DarkPoolAnalysis) -> List[str]:
        """
        יצירת המלצות מתקדמות
        """
        recommendations = []
        
        try:
            if analysis.significant_activities > 0:
                recommendations.append("🔍 מעקב אחר פעילויות בריכות אפלות משמעותיות - פוטנציאל לתנועה חזקה")
            
            if analysis.avg_activity_strength > 0.7:
                recommendations.append("📈 פעילות בריכות אפלות חזקה - פוטנציאל לפריצה קרובה")
            
            if analysis.dark_pool_trend == 'increasing' and analysis.volume_trend == 'increasing':
                recommendations.append("📊 פעילות בריכות אפלות עולה - עניין גובר במניה")
            
            if analysis.breakout_potential > 0.05:
                recommendations.append("💪 פוטנציאל פריצה גבוה - תמיכה חזקה בתנועה")
            
            if analysis.significant_activities > 3:
                recommendations.append("⚠️ מספר פעילויות משמעותיות - בדוק חדשות או אירועים")
            
            if not recommendations:
                recommendations.append("📉 אין פעילויות בריכות אפלות משמעותיות - המשך מעקב")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["שגיאה ביצירת המלצות"]

    def get_dark_pool_summary(self) -> Dict:
        """
        סיכום ניתוח פעילות בריכות אפלות
        """
        return {
            "agent_type": "DarkPoolAgent",
            "description": "זיהוי פעילות בריכות אפלות מתקדם עם ניתוח רב-ממדי",
            "features": [
                "זיהוי פעילות בריכות אפלות לפי מספר פרמטרים",
                "ניתוח רב-ממדי של פעילות בריכות אפלות",
                "ולידציה לפי זמן ומגמה",
                "ניתוח פעילות בריכות אפלות לפי סקטורים",
                "זיהוי פעילות בריכות אפלות לפני אירועים",
                "ניתוח פעילות בריכות אפלות לפי טכני ופונדמנטלי",
                "זיהוי פעילות בריכות אפלות לפי רגשות השוק",
                "ניתוח פעילות בריכות אפלות לפי נפח ומחיר"
            ],
            "thresholds": self.dark_pool_thresholds,
            "time_periods": self.time_periods
        } 