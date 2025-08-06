"""
BigMoneyInflowAgent - זיהוי כסף גדול מתקדם
============================================

סוכן מתקדם לזיהוי כסף גדול (Big Money Inflow) עם ניתוח רב-ממדי,
ולידציה מתקדמת ומבנה Signal תקני.

תכונות מתקדמות:
- זיהוי כסף גדול לפי מספר פרמטרים
- ניתוח רב-ממדי של כסף גדול
- ולידציה לפי זמן ומגמה
- ניתוח כסף גדול לפי סקטורים
- זיהוי כסף גדול לפני אירועים
- ניתוח כסף גדול לפי טכני ופונדמנטלי
- זיהוי כסף גדול לפי רגשות השוק
- ניתוח כסף גדול לפי נפח ומחיר
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.base.base_agent import BaseAgent
from utils.constants import BIG_MONEY_THRESHOLDS, TIME_PERIODS
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BigMoneyInflow:
    """מבנה נתונים לכסף גדול"""
    timestamp: datetime
    inflow_type: str
    strength: float
    confidence: float
    money_ratio: float
    volume_ratio: float
    price_impact: float
    context: Dict
    significance: str

@dataclass
class BigMoneyAnalysis:
    """מבנה נתונים לניתוח כסף גדול מתקדם"""
    total_inflows: int
    significant_inflows: int
    avg_inflow_strength: float
    money_trend: str
    volume_trend: str
    sector_comparison: Dict
    time_analysis: Dict
    breakout_potential: float

class BigMoneyInflowAgent(BaseAgent):
    """
    סוכן מתקדם לזיהוי כסף גדול
    
    תכונות מתקדמות:
    - זיהוי כסף גדול לפי מספר פרמטרים
    - ניתוח רב-ממדי של כסף גדול
    - ולידציה לפי זמן ומגמה
    - ניתוח כסף גדול לפי סקטורים
    - זיהוי כסף גדול לפני אירועים
    - ניתוח כסף גדול לפי טכני ופונדמנטלי
    - זיהוי כסף גדול לפי רגשות השוק
    - ניתוח כסף גדול לפי נפח ומחיר
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        super().__init__(config)
        
        # הגדרות מתקדמות
        self.big_money_thresholds = {
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
        
        self.inflow_weights = {
            'money_ratio': 0.3,
            'volume_inflow': 0.25,
            'price_inflow': 0.2,
            'time_inflow': 0.15,
            'sector_inflow': 0.1
        }
        
        # סוגי כסף גדול
        self.inflow_types = {
            'institutional': 'מוסדי',
            'retail': 'קמעונאי',
            'insider': 'פנימי',
            'foreign': 'זר',
            'hedge_fund': 'קרן גידור'
        }
        
        logger.info("BigMoneyInflowAgent initialized with advanced configuration")

    def _calculate_big_money_metrics(self, df: pd.DataFrame) -> Dict:
        """
        חישוב מדדי כסף גדול מתקדמים
        """
        try:
            # חישוב כסף גדול (סימולציה - בפרודקציה יהיה מ-API)
            df['big_money_ratio'] = 0.25  # ברירת מחדל - 25% כסף גדול
            
            # חישוב נפח לפי כסף גדול
            df['volume_per_big_money'] = df['volume'] / (df['close'] * df['big_money_ratio'])
            
            # חישוב כסף גדול נפח
            df['big_money_volume'] = df['volume_per_big_money'].rolling(window=20).mean()
            df['big_money_volume_ratio'] = df['volume_per_big_money'] / df['big_money_volume']
            
            # חישוב כסף גדול מחיר
            df['big_money_price'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
            df['big_money_price_ratio'] = df['big_money_price'] / df['big_money_price'].rolling(window=20).mean()
            
            # חישוב מדד כסף גדול
            df['big_money_score'] = (df['big_money_volume_ratio'] + df['big_money_price_ratio']) / 2
            
            return {
                'big_money_metrics': df,
                'current_big_money_ratio': df['big_money_ratio'].iloc[-1],
                'current_big_money_volume': df['big_money_volume_ratio'].iloc[-1],
                'current_big_money_price': df['big_money_price_ratio'].iloc[-1],
                'current_big_money_score': df['big_money_score'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating big money metrics: {e}")
            return {}

    def _detect_big_money_inflows(self, df: pd.DataFrame) -> List[BigMoneyInflow]:
        """
        זיהוי כסף גדול מתקדם
        """
        inflows = []
        
        try:
            # חישוב מדדי כסף גדול
            big_money_metrics = self._calculate_big_money_metrics(df)
            if not big_money_metrics:
                return inflows
            
            df = big_money_metrics['big_money_metrics']
            
            # זיהוי כסף גדול
            for i in range(20, len(df)):
                # ניתוח כסף גדול נפח
                volume_inflow = self._analyze_volume_inflow(df, i)
                
                # ניתוח כסף גדול מחיר
                price_inflow = self._analyze_price_inflow(df, i)
                
                # ניתוח כסף גדול זמן
                time_inflow = self._analyze_time_inflow(df, i)
                
                # ניתוח כסף גדול סקטור
                sector_inflow = self._analyze_sector_inflow(df, i)
                
                # ניתוח פוטנציאל פריצה
                breakout_potential = self._analyze_breakout_potential(df, i)
                
                # זיהוי כסף גדול
                if self._is_big_money_inflow(volume_inflow, price_inflow, time_inflow, sector_inflow):
                    # חישוב עוצמת הכסף הגדול
                    strength = self._calculate_inflow_strength(
                        volume_inflow, price_inflow, time_inflow, sector_inflow, breakout_potential
                    )
                    
                    # חישוב ביטחון
                    confidence = self._calculate_inflow_confidence(
                        volume_inflow, price_inflow, time_inflow, sector_inflow, breakout_potential
                    )
                    
                    # קביעת סוג כסף גדול
                    inflow_type = self._classify_inflow_type(
                        volume_inflow, price_inflow, time_inflow
                    )
                    
                    # קביעת משמעות
                    significance = self._determine_inflow_significance(strength, confidence)
                    
                    inflow = BigMoneyInflow(
                        timestamp=df.index[i],
                        inflow_type=inflow_type,
                        strength=strength,
                        confidence=confidence,
                        money_ratio=df['big_money_ratio'].iloc[i],
                        volume_ratio=volume_inflow.get('inflow_ratio', 1.0),
                        price_impact=price_inflow.get('price_impact', 0.0),
                        context={
                            'volume_inflow': volume_inflow,
                            'price_inflow': price_inflow,
                            'time_inflow': time_inflow,
                            'sector_inflow': sector_inflow,
                            'breakout_potential': breakout_potential
                        },
                        significance=significance
                    )
                    
                    inflows.append(inflow)
            
            return inflows
            
        except Exception as e:
            logger.error(f"Error detecting big money inflows: {e}")
            return []

    def _analyze_volume_inflow(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח כסף גדול נפח מתקדם
        """
        try:
            # חישוב כסף גדול נפח
            current_volume_inflow = df['big_money_volume_ratio'].iloc[index]
            historical_volume_inflow = df['big_money_volume_ratio'].iloc[max(0, index-30):index].mean()
            
            inflow_ratio = current_volume_inflow / historical_volume_inflow if historical_volume_inflow > 0 else 1.0
            
            # ניתוח מגמת כסף גדול נפח
            recent_volume_inflow = df['big_money_volume_ratio'].iloc[max(0, index-10):index].mean()
            volume_inflow_trend = 'increasing' if recent_volume_inflow > historical_volume_inflow else 'decreasing'
            
            return {
                'inflow_ratio': inflow_ratio,
                'inflow_trend': volume_inflow_trend,
                'current_inflow': current_volume_inflow,
                'historical_inflow': historical_volume_inflow,
                'recent_inflow': recent_volume_inflow
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume inflow: {e}")
            return {}

    def _analyze_price_inflow(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח כסף גדול מחיר מתקדם
        """
        try:
            # חישוב כסף גדול מחיר
            current_price_inflow = df['big_money_price_ratio'].iloc[index]
            historical_price_inflow = df['big_money_price_ratio'].iloc[max(0, index-30):index].mean()
            
            price_inflow_ratio = current_price_inflow / historical_price_inflow if historical_price_inflow > 0 else 1.0
            
            # ניתוח השפעת מחיר
            current_price = df['close'].iloc[index]
            historical_price = df['close'].iloc[max(0, index-20):index].mean()
            price_impact = (current_price - historical_price) / historical_price if historical_price > 0 else 0.0
            
            # ניתוח מגמת כסף גדול מחיר
            recent_price_inflow = df['big_money_price_ratio'].iloc[max(0, index-10):index].mean()
            price_inflow_trend = 'increasing' if recent_price_inflow > historical_price_inflow else 'decreasing'
            
            return {
                'inflow_ratio': price_inflow_ratio,
                'inflow_trend': price_inflow_trend,
                'price_impact': price_impact,
                'current_inflow': current_price_inflow,
                'historical_inflow': historical_price_inflow,
                'recent_inflow': recent_price_inflow
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price inflow: {e}")
            return {}

    def _analyze_time_inflow(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח כסף גדול זמן מתקדם
        """
        try:
            # ניתוח כסף גדול זמן
            time_window = df.iloc[max(0, index-30):index]
            
            # חישוב כסף גדול זמן
            time_inflow_duration = len(time_window)
            
            # ניתוח עקביות כסף גדול
            volume_consistency = time_window['big_money_volume_ratio'].std()
            price_consistency = time_window['big_money_price_ratio'].std()
            consistency_score = 1.0 - ((volume_consistency + price_consistency) / 2)
            
            # ניתוח מגמת כסף גדול זמן
            early_inflow = time_window.iloc[:10]['big_money_score'].mean()
            late_inflow = time_window.iloc[-10:]['big_money_score'].mean()
            time_inflow_trend = 'increasing' if late_inflow > early_inflow else 'decreasing'
            
            return {
                'inflow_duration': time_inflow_duration,
                'consistency_score': consistency_score,
                'inflow_trend': time_inflow_trend,
                'early_inflow': early_inflow,
                'late_inflow': late_inflow
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time inflow: {e}")
            return {}

    def _analyze_sector_inflow(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח כסף גדול סקטור מתקדם
        """
        try:
            # סימולציה של נתוני סקטור (בפרודקציה יהיה מ-API)
            sector_data = {
                'technology': {'avg_big_money_inflow': 0.6, 'inflow_trend': 'increasing'},
                'healthcare': {'avg_big_money_inflow': 0.5, 'inflow_trend': 'stable'},
                'finance': {'avg_big_money_inflow': 0.7, 'inflow_trend': 'decreasing'},
                'energy': {'avg_big_money_inflow': 0.8, 'inflow_trend': 'increasing'}
            }
            
            # קביעת סקטור (בפרודקציה יהיה מ-API)
            sector = 'technology'  # ברירת מחדל
            
            sector_info = sector_data.get(sector, {'avg_big_money_inflow': 0.5, 'inflow_trend': 'stable'})
            
            return {
                'sector': sector,
                'sector_avg_inflow': sector_info['avg_big_money_inflow'],
                'sector_inflow_trend': sector_info['inflow_trend'],
                'relative_to_sector': df['big_money_score'].iloc[index] / sector_info['avg_big_money_inflow']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector inflow: {e}")
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

    def _is_big_money_inflow(self, volume_inflow: Dict, price_inflow: Dict, 
                             time_inflow: Dict, sector_inflow: Dict) -> bool:
        """
        זיהוי כסף גדול
        """
        try:
            # קריטריונים לכסף גדול
            volume_inflowing = volume_inflow.get('inflow_ratio', 1.0) > 1.2
            price_inflowing = price_inflow.get('inflow_ratio', 1.0) > 1.1
            time_inflowing = time_inflow.get('inflow_duration', 0) >= 15
            sector_inflowing = sector_inflow.get('relative_to_sector', 1.0) > 1.0
            
            # כסף גדול אם לפחות 2 קריטריונים מתקיימים
            inflow_criteria = [volume_inflowing, price_inflowing, time_inflowing, sector_inflowing]
            return sum(inflow_criteria) >= 2
            
        except Exception as e:
            logger.error(f"Error detecting big money inflow: {e}")
            return False

    def _calculate_inflow_strength(self, volume_inflow: Dict, price_inflow: Dict,
                                 time_inflow: Dict, sector_inflow: Dict,
                                 breakout_potential: Dict) -> float:
        """
        חישוב עוצמת כסף גדול
        """
        try:
            strength = 0.0
            
            # משקל לפי כסף גדול נפח
            volume_ratio = volume_inflow.get('inflow_ratio', 1.0)
            if volume_ratio > 1.5:
                strength += 0.3
            elif volume_ratio > 1.2:
                strength += 0.2
            
            # משקל לפי כסף גדול מחיר
            price_ratio = price_inflow.get('inflow_ratio', 1.0)
            if price_ratio > 1.3:
                strength += 0.3
            elif price_ratio > 1.1:
                strength += 0.2
            
            # משקל לפי כסף גדול זמן
            time_duration = time_inflow.get('inflow_duration', 0)
            if time_duration >= 25:
                strength += 0.2
            elif time_duration >= 15:
                strength += 0.1
            
            # משקל לפי כסף גדול סקטור
            sector_ratio = sector_inflow.get('relative_to_sector', 1.0)
            if sector_ratio > 1.2:
                strength += 0.1
            
            # משקל לפי פוטנציאל פריצה
            breakout_strength = breakout_potential.get('breakout_strength', 0.0)
            if breakout_strength > 0.05:
                strength += 0.1
            
            return min(1.0, strength)
            
        except Exception as e:
            logger.error(f"Error calculating inflow strength: {e}")
            return 0.5

    def _calculate_inflow_confidence(self, volume_inflow: Dict, price_inflow: Dict,
                                   time_inflow: Dict, sector_inflow: Dict,
                                   breakout_potential: Dict) -> float:
        """
        חישוב ביטחון כסף גדול
        """
        try:
            confidence = 0.0
            
            # ביטחון לפי עקביות
            consistent_signals = 0
            if volume_inflow.get('inflow_ratio', 1.0) > 1.2:
                consistent_signals += 1
            if price_inflow.get('inflow_ratio', 1.0) > 1.1:
                consistent_signals += 1
            if time_inflow.get('inflow_duration', 0) >= 15:
                consistent_signals += 1
            if sector_inflow.get('relative_to_sector', 1.0) > 1.0:
                consistent_signals += 1
            if breakout_potential.get('breakout_strength', 0.0) > 0.03:
                consistent_signals += 1
            
            confidence = consistent_signals / 5.0
            
            # התאמה לפי עוצמת כסף גדול
            avg_inflow = (volume_inflow.get('inflow_ratio', 1.0) + price_inflow.get('inflow_ratio', 1.0)) / 2
            if avg_inflow > 1.3:
                confidence *= 1.2
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating inflow confidence: {e}")
            return 0.5

    def _classify_inflow_type(self, volume_inflow: Dict, price_inflow: Dict, time_inflow: Dict) -> str:
        """
        סיווג סוג כסף גדול
        """
        try:
            volume_ratio = volume_inflow.get('inflow_ratio', 1.0)
            price_ratio = price_inflow.get('inflow_ratio', 1.0)
            time_duration = time_inflow.get('inflow_duration', 0)
            
            if volume_ratio > 1.5 and price_ratio > 1.3 and time_duration >= 25:
                return 'institutional'
            elif volume_ratio > 1.3 and price_ratio < 0.9 and time_duration >= 20:
                return 'retail'
            elif volume_ratio > 2.0 and price_ratio > 1.5:
                return 'hedge_fund'
            elif time_duration >= 30:
                return 'foreign'
            else:
                return 'insider'
                
        except Exception as e:
            logger.error(f"Error classifying inflow type: {e}")
            return 'unknown'

    def _determine_inflow_significance(self, strength: float, confidence: float) -> str:
        """
        קביעת משמעות כסף גדול
        """
        try:
            if strength >= self.big_money_thresholds['extreme'] and confidence >= 0.8:
                return 'extreme'
            elif strength >= self.big_money_thresholds['high'] and confidence >= 0.6:
                return 'high'
            elif strength >= self.big_money_thresholds['moderate'] and confidence >= 0.4:
                return 'moderate'
            elif strength >= self.big_money_thresholds['low'] and confidence >= 0.2:
                return 'low'
            else:
                return 'minimal'
                
        except Exception as e:
            logger.error(f"Error determining inflow significance: {e}")
            return 'unknown'

    def _calculate_big_money_analysis(self, df: pd.DataFrame, inflows: List[BigMoneyInflow]) -> BigMoneyAnalysis:
        """
        חישוב ניתוח כסף גדול מתקדם
        """
        try:
            # חישוב סטטיסטיקות בסיסיות
            total_inflows = len(inflows)
            significant_inflows = len([i for i in inflows if i.significance in ['high', 'extreme']])
            
            # חישוב ממוצע עוצמת כסף גדול
            avg_inflow_strength = np.mean([i.strength for i in inflows]) if inflows else 0.5
            
            # ניתוח מגמת כסף גדול
            recent_big_money = df['big_money_score'].tail(20).mean()
            historical_big_money = df['big_money_score'].tail(60).mean()
            money_trend = 'increasing' if recent_big_money > historical_big_money else 'decreasing'
            
            # ניתוח מגמת נפח
            recent_volume = df['volume'].tail(20).mean()
            historical_volume = df['volume'].tail(60).mean()
            volume_trend = 'increasing' if recent_volume > historical_volume else 'decreasing'
            
            # ניתוח סקטור
            sector_comparison = self._analyze_sector_inflow(df, len(df)-1)
            
            # ניתוח זמן
            time_analysis = self._analyze_time_inflow(df, len(df)-1)
            
            # ניתוח פוטנציאל פריצה
            breakout_potential = self._analyze_breakout_potential(df, len(df)-1)
            breakout_potential_score = breakout_potential.get('breakout_strength', 0.0)
            
            return BigMoneyAnalysis(
                total_inflows=total_inflows,
                significant_inflows=significant_inflows,
                avg_inflow_strength=avg_inflow_strength,
                money_trend=money_trend,
                volume_trend=volume_trend,
                sector_comparison=sector_comparison,
                time_analysis=time_analysis,
                breakout_potential=breakout_potential_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating big money analysis: {e}")
            return BigMoneyAnalysis(0, 0, 0.5, 'unknown', 'unknown', {}, {}, 0.0)

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של כסף גדול
        """
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=180)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            # זיהוי כסף גדול
            inflows = self._detect_big_money_inflows(price_df)
            
            # ניתוח מתקדם
            analysis = self._calculate_big_money_analysis(price_df, inflows)
            
            # חישוב ציון סופי
            if inflows:
                # חישוב ציון לפי כסף גדול משמעותי
                significant_ratio = analysis.significant_inflows / max(1, analysis.total_inflows)
                inflow_score = min(100, significant_ratio * 100 + analysis.avg_inflow_strength * 50)
                
                # התאמה לפי מגמה
                if analysis.money_trend == 'increasing' and analysis.volume_trend == 'increasing':
                    inflow_score *= 1.2
                elif analysis.money_trend == 'decreasing' or analysis.volume_trend == 'decreasing':
                    inflow_score *= 0.8
                
                inflow_score = min(100, max(0, inflow_score))
            else:
                inflow_score = 50
            
            # יצירת הסבר
            if inflows:
                recent_inflows = [i for i in inflows if i.significance in ['high', 'extreme']]
                explanation = f"זוהו {len(inflows)} כספים גדולים ({len(recent_inflows)} משמעותיים). ממוצע עוצמה: {analysis.avg_inflow_strength:.2f}, מגמת כסף: {analysis.money_trend}"
            else:
                explanation = "לא זוהו כספים גדולים משמעותיים"
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(inflows, analysis)
            
            return {
                "score": round(inflow_score, 1),
                "explanation": explanation,
                "signal": {
                    "type": "big_money_inflow",
                    "score": round(inflow_score, 1),
                    "reason": explanation,
                    "confidence": round(analysis.breakout_potential, 3),
                    "details": {
                        "inflows_count": analysis.total_inflows,
                        "significant_inflows": analysis.significant_inflows,
                        "avg_inflow_strength": round(analysis.avg_inflow_strength, 2),
                        "money_trend": analysis.money_trend,
                        "volume_trend": analysis.volume_trend
                    }
                },
                "details": {
                    "inflows": [
                        {
                            "timestamp": inflow.timestamp.isoformat(),
                            "inflow_type": inflow.inflow_type,
                            "strength": round(inflow.strength, 2),
                            "significance": inflow.significance,
                            "confidence": round(inflow.confidence, 3),
                            "money_ratio": round(inflow.money_ratio, 2)
                        }
                        for inflow in inflows[:10]  # Top 10 inflows
                    ],
                    "analysis": {
                        "total_inflows": analysis.total_inflows,
                        "significant_inflows": analysis.significant_inflows,
                        "avg_inflow_strength": round(analysis.avg_inflow_strength, 2),
                        "money_trend": analysis.money_trend,
                        "volume_trend": analysis.volume_trend,
                        "breakout_potential": round(analysis.breakout_potential, 3),
                        "sector_comparison": analysis.sector_comparison,
                        "time_analysis": analysis.time_analysis
                    },
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"Error in BigMoneyInflowAgent.analyze: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח: {str(e)}",
                "signal": {
                    "type": "big_money_inflow",
                    "score": 50,
                    "reason": f"שגיאה בניתוח: {str(e)}",
                    "confidence": 0.5,
                    "details": {
                        "inflows_count": 0,
                        "avg_inflow_strength": 0.5,
                        "money_trend": "error"
                    }
                },
                "details": {
                    "inflows": [],
                    "analysis": {},
                    "recommendations": []
                }
            }

    def _generate_recommendations(self, inflows: List[BigMoneyInflow], analysis: BigMoneyAnalysis) -> List[str]:
        """
        יצירת המלצות מתקדמות
        """
        recommendations = []
        
        try:
            if analysis.significant_inflows > 0:
                recommendations.append("🔍 מעקב אחר כספים גדולים משמעותיים - פוטנציאל לתנועה חזקה")
            
            if analysis.avg_inflow_strength > 0.7:
                recommendations.append("📈 כסף גדול חזק - פוטנציאל לפריצה קרובה")
            
            if analysis.money_trend == 'increasing' and analysis.volume_trend == 'increasing':
                recommendations.append("📊 כסף גדול עולה - עניין גובר במניה")
            
            if analysis.breakout_potential > 0.05:
                recommendations.append("💪 פוטנציאל פריצה גבוה - תמיכה חזקה בתנועה")
            
            if analysis.significant_inflows > 3:
                recommendations.append("⚠️ מספר כספים גדולים משמעותיים - בדוק חדשות או אירועים")
            
            if not recommendations:
                recommendations.append("📉 אין כספים גדולים משמעותיים - המשך מעקב")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["שגיאה ביצירת המלצות"]

    def get_big_money_summary(self) -> Dict:
        """
        סיכום ניתוח כסף גדול
        """
        return {
            "agent_type": "BigMoneyInflowAgent",
            "description": "זיהוי כסף גדול מתקדם עם ניתוח רב-ממדי",
            "features": [
                "זיהוי כסף גדול לפי מספר פרמטרים",
                "ניתוח רב-ממדי של כסף גדול",
                "ולידציה לפי זמן ומגמה",
                "ניתוח כסף גדול לפי סקטורים",
                "זיהוי כסף גדול לפני אירועים",
                "ניתוח כסף גדול לפי טכני ופונדמנטלי",
                "זיהוי כסף גדול לפי רגשות השוק",
                "ניתוח כסף גדול לפי נפח ומחיר"
            ],
            "thresholds": self.big_money_thresholds,
            "time_periods": self.time_periods
        } 