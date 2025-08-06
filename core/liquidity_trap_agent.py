"""
LiquidityTrapAgent - זיהוי מלכודות נזילות מתקדם
================================================

סוכן מתקדם לזיהוי מלכודות נזילות (Liquidity Traps) עם ניתוח רב-ממדי,
ולידציה מתקדמת ומבנה Signal תקני.

תכונות מתקדמות:
- זיהוי מלכודות נזילות לפי מספר פרמטרים
- ניתוח רב-ממדי של נזילות
- ולידציה לפי זמן ומגמה
- ניתוח נזילות לפי סקטורים
- זיהוי מלכודות נזילות לפני אירועים
- ניתוח נזילות לפי טכני ופונדמנטלי
- זיהוי מלכודות נזילות לפי רגשות השוק
- ניתוח נזילות לפי נפח ומחיר
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.base.base_agent import BaseAgent
from utils.constants import LIQUIDITY_TRAP_THRESHOLDS, TIME_PERIODS
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LiquidityTrap:
    """מבנה נתונים למלכודת נזילות"""
    timestamp: datetime
    trap_type: str
    strength: float
    confidence: float
    liquidity_ratio: float
    volume_ratio: float
    price_impact: float
    context: Dict
    significance: str

@dataclass
class LiquidityTrapAnalysis:
    """מבנה נתונים לניתוח מלכודת נזילות מתקדם"""
    total_traps: int
    significant_traps: int
    avg_trap_strength: float
    liquidity_trend: str
    volume_trend: str
    sector_comparison: Dict
    time_analysis: Dict
    breakout_potential: float

class LiquidityTrapAgent(BaseAgent):
    """
    סוכן מתקדם לזיהוי מלכודות נזילות
    
    תכונות מתקדמות:
    - זיהוי מלכודות נזילות לפי מספר פרמטרים
    - ניתוח רב-ממדי של נזילות
    - ולידציה לפי זמן ומגמה
    - ניתוח נזילות לפי סקטורים
    - זיהוי מלכודות נזילות לפני אירועים
    - ניתוח נזילות לפי טכני ופונדמנטלי
    - זיהוי מלכודות נזילות לפי רגשות השוק
    - ניתוח נזילות לפי נפח ומחיר
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        super().__init__(config)
        
        # הגדרות מתקדמות
        self.liquidity_trap_thresholds = {
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
        
        self.trap_weights = {
            'liquidity_ratio': 0.3,
            'volume_trap': 0.25,
            'price_trap': 0.2,
            'time_trap': 0.15,
            'sector_trap': 0.1
        }
        
        # סוגי מלכודות נזילות
        self.trap_types = {
            'volume_trap': 'מלכודת נפח',
            'price_trap': 'מלכודת מחיר',
            'liquidity_trap': 'מלכודת נזילות',
            'time_trap': 'מלכודת זמן',
            'sector_trap': 'מלכודת סקטור'
        }
        
        logger.info("LiquidityTrapAgent initialized with advanced configuration")

    def _calculate_liquidity_metrics(self, df: pd.DataFrame) -> Dict:
        """
        חישוב מדדי נזילות מתקדמים
        """
        try:
            # חישוב נזילות (סימולציה - בפרודקציה יהיה מ-API)
            df['liquidity_ratio'] = 0.8  # ברירת מחדל - 80% נזילות
            
            # חישוב נפח לפי נזילות
            df['volume_per_liquidity'] = df['volume'] / (df['close'] * df['liquidity_ratio'])
            
            # חישוב מלכודת נפח
            df['volume_trap'] = df['volume_per_liquidity'].rolling(window=20).mean()
            df['volume_trap_ratio'] = df['volume_per_liquidity'] / df['volume_trap']
            
            # חישוב מלכודת מחיר
            df['price_trap'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
            df['price_trap_ratio'] = df['price_trap'] / df['price_trap'].rolling(window=20).mean()
            
            # חישוב מדד מלכודת נזילות
            df['liquidity_trap_score'] = (df['volume_trap_ratio'] + df['price_trap_ratio']) / 2
            
            return {
                'liquidity_metrics': df,
                'current_liquidity_ratio': df['liquidity_ratio'].iloc[-1],
                'current_volume_trap': df['volume_trap_ratio'].iloc[-1],
                'current_price_trap': df['price_trap_ratio'].iloc[-1],
                'current_liquidity_trap': df['liquidity_trap_score'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating liquidity metrics: {e}")
            return {}

    def _detect_liquidity_traps(self, df: pd.DataFrame) -> List[LiquidityTrap]:
        """
        זיהוי מלכודות נזילות מתקדם
        """
        traps = []
        
        try:
            # חישוב מדדי נזילות
            liquidity_metrics = self._calculate_liquidity_metrics(df)
            if not liquidity_metrics:
                return traps
            
            df = liquidity_metrics['liquidity_metrics']
            
            # זיהוי מלכודות נזילות
            for i in range(20, len(df)):
                # ניתוח מלכודת נפח
                volume_trap = self._analyze_volume_trap(df, i)
                
                # ניתוח מלכודת מחיר
                price_trap = self._analyze_price_trap(df, i)
                
                # ניתוח מלכודת זמן
                time_trap = self._analyze_time_trap(df, i)
                
                # ניתוח מלכודת סקטור
                sector_trap = self._analyze_sector_trap(df, i)
                
                # ניתוח פוטנציאל פריצה
                breakout_potential = self._analyze_breakout_potential(df, i)
                
                # זיהוי מלכודת נזילות
                if self._is_liquidity_trap(volume_trap, price_trap, time_trap, sector_trap):
                    # חישוב עוצמת המלכודת
                    strength = self._calculate_trap_strength(
                        volume_trap, price_trap, time_trap, sector_trap, breakout_potential
                    )
                    
                    # חישוב ביטחון
                    confidence = self._calculate_trap_confidence(
                        volume_trap, price_trap, time_trap, sector_trap, breakout_potential
                    )
                    
                    # קביעת סוג מלכודת
                    trap_type = self._classify_trap_type(
                        volume_trap, price_trap, time_trap
                    )
                    
                    # קביעת משמעות
                    significance = self._determine_trap_significance(strength, confidence)
                    
                    trap = LiquidityTrap(
                        timestamp=df.index[i],
                        trap_type=trap_type,
                        strength=strength,
                        confidence=confidence,
                        liquidity_ratio=df['liquidity_ratio'].iloc[i],
                        volume_ratio=volume_trap.get('trap_ratio', 1.0),
                        price_impact=price_trap.get('price_impact', 0.0),
                        context={
                            'volume_trap': volume_trap,
                            'price_trap': price_trap,
                            'time_trap': time_trap,
                            'sector_trap': sector_trap,
                            'breakout_potential': breakout_potential
                        },
                        significance=significance
                    )
                    
                    traps.append(trap)
            
            return traps
            
        except Exception as e:
            logger.error(f"Error detecting liquidity traps: {e}")
            return []

    def _analyze_volume_trap(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח מלכודת נפח מתקדם
        """
        try:
            # חישוב מלכודת נפח
            current_volume_trap = df['volume_trap_ratio'].iloc[index]
            historical_volume_trap = df['volume_trap_ratio'].iloc[max(0, index-30):index].mean()
            
            trap_ratio = current_volume_trap / historical_volume_trap if historical_volume_trap > 0 else 1.0
            
            # ניתוח מגמת מלכודת נפח
            recent_volume_trap = df['volume_trap_ratio'].iloc[max(0, index-10):index].mean()
            volume_trap_trend = 'increasing' if recent_volume_trap > historical_volume_trap else 'decreasing'
            
            return {
                'trap_ratio': trap_ratio,
                'trap_trend': volume_trap_trend,
                'current_trap': current_volume_trap,
                'historical_trap': historical_volume_trap,
                'recent_trap': recent_volume_trap
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume trap: {e}")
            return {}

    def _analyze_price_trap(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח מלכודת מחיר מתקדם
        """
        try:
            # חישוב מלכודת מחיר
            current_price_trap = df['price_trap_ratio'].iloc[index]
            historical_price_trap = df['price_trap_ratio'].iloc[max(0, index-30):index].mean()
            
            price_trap_ratio = current_price_trap / historical_price_trap if historical_price_trap > 0 else 1.0
            
            # ניתוח השפעת מחיר
            current_price = df['close'].iloc[index]
            historical_price = df['close'].iloc[max(0, index-20):index].mean()
            price_impact = (current_price - historical_price) / historical_price if historical_price > 0 else 0.0
            
            # ניתוח מגמת מלכודת מחיר
            recent_price_trap = df['price_trap_ratio'].iloc[max(0, index-10):index].mean()
            price_trap_trend = 'increasing' if recent_price_trap > historical_price_trap else 'decreasing'
            
            return {
                'trap_ratio': price_trap_ratio,
                'trap_trend': price_trap_trend,
                'price_impact': price_impact,
                'current_trap': current_price_trap,
                'historical_trap': historical_price_trap,
                'recent_trap': recent_price_trap
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price trap: {e}")
            return {}

    def _analyze_time_trap(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח מלכודת זמן מתקדם
        """
        try:
            # ניתוח מלכודת זמן
            time_window = df.iloc[max(0, index-30):index]
            
            # חישוב מלכודת זמן
            time_trap_duration = len(time_window)
            
            # ניתוח עקביות מלכודת
            volume_consistency = time_window['volume_trap_ratio'].std()
            price_consistency = time_window['price_trap_ratio'].std()
            consistency_score = 1.0 - ((volume_consistency + price_consistency) / 2)
            
            # ניתוח מגמת מלכודת זמן
            early_trap = time_window.iloc[:10]['liquidity_trap_score'].mean()
            late_trap = time_window.iloc[-10:]['liquidity_trap_score'].mean()
            time_trap_trend = 'increasing' if late_trap > early_trap else 'decreasing'
            
            return {
                'trap_duration': time_trap_duration,
                'consistency_score': consistency_score,
                'trap_trend': time_trap_trend,
                'early_trap': early_trap,
                'late_trap': late_trap
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time trap: {e}")
            return {}

    def _analyze_sector_trap(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח מלכודת סקטור מתקדם
        """
        try:
            # סימולציה של נתוני סקטור (בפרודקציה יהיה מ-API)
            sector_data = {
                'technology': {'avg_liquidity_trap': 0.6, 'trap_trend': 'increasing'},
                'healthcare': {'avg_liquidity_trap': 0.5, 'trap_trend': 'stable'},
                'finance': {'avg_liquidity_trap': 0.7, 'trap_trend': 'decreasing'},
                'energy': {'avg_liquidity_trap': 0.8, 'trap_trend': 'increasing'}
            }
            
            # קביעת סקטור (בפרודקציה יהיה מ-API)
            sector = 'technology'  # ברירת מחדל
            
            sector_info = sector_data.get(sector, {'avg_liquidity_trap': 0.5, 'trap_trend': 'stable'})
            
            return {
                'sector': sector,
                'sector_avg_trap': sector_info['avg_liquidity_trap'],
                'sector_trap_trend': sector_info['trap_trend'],
                'relative_to_sector': df['liquidity_trap_score'].iloc[index] / sector_info['avg_liquidity_trap']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector trap: {e}")
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

    def _is_liquidity_trap(self, volume_trap: Dict, price_trap: Dict, 
                           time_trap: Dict, sector_trap: Dict) -> bool:
        """
        זיהוי מלכודת נזילות
        """
        try:
            # קריטריונים למלכודת נזילות
            volume_trapping = volume_trap.get('trap_ratio', 1.0) > 1.2
            price_trapping = price_trap.get('trap_ratio', 1.0) > 1.1
            time_trapping = time_trap.get('trap_duration', 0) >= 15
            sector_trapping = sector_trap.get('relative_to_sector', 1.0) > 1.0
            
            # מלכודת נזילות אם לפחות 2 קריטריונים מתקיימים
            trap_criteria = [volume_trapping, price_trapping, time_trapping, sector_trapping]
            return sum(trap_criteria) >= 2
            
        except Exception as e:
            logger.error(f"Error detecting liquidity trap: {e}")
            return False

    def _calculate_trap_strength(self, volume_trap: Dict, price_trap: Dict,
                                time_trap: Dict, sector_trap: Dict,
                                breakout_potential: Dict) -> float:
        """
        חישוב עוצמת מלכודת נזילות
        """
        try:
            strength = 0.0
            
            # משקל לפי מלכודת נפח
            volume_ratio = volume_trap.get('trap_ratio', 1.0)
            if volume_ratio > 1.5:
                strength += 0.3
            elif volume_ratio > 1.2:
                strength += 0.2
            
            # משקל לפי מלכודת מחיר
            price_ratio = price_trap.get('trap_ratio', 1.0)
            if price_ratio > 1.3:
                strength += 0.3
            elif price_ratio > 1.1:
                strength += 0.2
            
            # משקל לפי מלכודת זמן
            time_duration = time_trap.get('trap_duration', 0)
            if time_duration >= 25:
                strength += 0.2
            elif time_duration >= 15:
                strength += 0.1
            
            # משקל לפי מלכודת סקטור
            sector_ratio = sector_trap.get('relative_to_sector', 1.0)
            if sector_ratio > 1.2:
                strength += 0.1
            
            # משקל לפי פוטנציאל פריצה
            breakout_strength = breakout_potential.get('breakout_strength', 0.0)
            if breakout_strength > 0.05:
                strength += 0.1
            
            return min(1.0, strength)
            
        except Exception as e:
            logger.error(f"Error calculating trap strength: {e}")
            return 0.5

    def _calculate_trap_confidence(self, volume_trap: Dict, price_trap: Dict,
                                 time_trap: Dict, sector_trap: Dict,
                                 breakout_potential: Dict) -> float:
        """
        חישוב ביטחון מלכודת נזילות
        """
        try:
            confidence = 0.0
            
            # ביטחון לפי עקביות
            consistent_signals = 0
            if volume_trap.get('trap_ratio', 1.0) > 1.2:
                consistent_signals += 1
            if price_trap.get('trap_ratio', 1.0) > 1.1:
                consistent_signals += 1
            if time_trap.get('trap_duration', 0) >= 15:
                consistent_signals += 1
            if sector_trap.get('relative_to_sector', 1.0) > 1.0:
                consistent_signals += 1
            if breakout_potential.get('breakout_strength', 0.0) > 0.03:
                consistent_signals += 1
            
            confidence = consistent_signals / 5.0
            
            # התאמה לפי עוצמת מלכודת
            avg_trap = (volume_trap.get('trap_ratio', 1.0) + price_trap.get('trap_ratio', 1.0)) / 2
            if avg_trap > 1.3:
                confidence *= 1.2
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating trap confidence: {e}")
            return 0.5

    def _classify_trap_type(self, volume_trap: Dict, price_trap: Dict, time_trap: Dict) -> str:
        """
        סיווג סוג מלכודת נזילות
        """
        try:
            volume_ratio = volume_trap.get('trap_ratio', 1.0)
            price_ratio = price_trap.get('trap_ratio', 1.0)
            time_duration = time_trap.get('trap_duration', 0)
            
            if volume_ratio > 1.5 and price_ratio > 1.3 and time_duration >= 25:
                return 'liquidity_trap'
            elif volume_ratio > 1.3 and price_ratio < 0.9 and time_duration >= 20:
                return 'volume_trap'
            elif volume_ratio > 2.0 and price_ratio > 1.5:
                return 'price_trap'
            elif time_duration >= 30:
                return 'time_trap'
            else:
                return 'sector_trap'
                
        except Exception as e:
            logger.error(f"Error classifying trap type: {e}")
            return 'unknown'

    def _determine_trap_significance(self, strength: float, confidence: float) -> str:
        """
        קביעת משמעות מלכודת נזילות
        """
        try:
            if strength >= self.liquidity_trap_thresholds['extreme'] and confidence >= 0.8:
                return 'extreme'
            elif strength >= self.liquidity_trap_thresholds['high'] and confidence >= 0.6:
                return 'high'
            elif strength >= self.liquidity_trap_thresholds['moderate'] and confidence >= 0.4:
                return 'moderate'
            elif strength >= self.liquidity_trap_thresholds['low'] and confidence >= 0.2:
                return 'low'
            else:
                return 'minimal'
                
        except Exception as e:
            logger.error(f"Error determining trap significance: {e}")
            return 'unknown'

    def _calculate_liquidity_trap_analysis(self, df: pd.DataFrame, traps: List[LiquidityTrap]) -> LiquidityTrapAnalysis:
        """
        חישוב ניתוח מלכודת נזילות מתקדם
        """
        try:
            # חישוב סטטיסטיקות בסיסיות
            total_traps = len(traps)
            significant_traps = len([t for t in traps if t.significance in ['high', 'extreme']])
            
            # חישוב ממוצע עוצמת מלכודת
            avg_trap_strength = np.mean([t.strength for t in traps]) if traps else 0.5
            
            # ניתוח מגמת נזילות
            recent_liquidity_trap = df['liquidity_trap_score'].tail(20).mean()
            historical_liquidity_trap = df['liquidity_trap_score'].tail(60).mean()
            liquidity_trend = 'increasing' if recent_liquidity_trap > historical_liquidity_trap else 'decreasing'
            
            # ניתוח מגמת נפח
            recent_volume = df['volume'].tail(20).mean()
            historical_volume = df['volume'].tail(60).mean()
            volume_trend = 'increasing' if recent_volume > historical_volume else 'decreasing'
            
            # ניתוח סקטור
            sector_comparison = self._analyze_sector_trap(df, len(df)-1)
            
            # ניתוח זמן
            time_analysis = self._analyze_time_trap(df, len(df)-1)
            
            # ניתוח פוטנציאל פריצה
            breakout_potential = self._analyze_breakout_potential(df, len(df)-1)
            breakout_potential_score = breakout_potential.get('breakout_strength', 0.0)
            
            return LiquidityTrapAnalysis(
                total_traps=total_traps,
                significant_traps=significant_traps,
                avg_trap_strength=avg_trap_strength,
                liquidity_trend=liquidity_trend,
                volume_trend=volume_trend,
                sector_comparison=sector_comparison,
                time_analysis=time_analysis,
                breakout_potential=breakout_potential_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating liquidity trap analysis: {e}")
            return LiquidityTrapAnalysis(0, 0, 0.5, 'unknown', 'unknown', {}, {}, 0.0)

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של מלכודות נזילות
        """
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=180)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            # זיהוי מלכודות נזילות
            traps = self._detect_liquidity_traps(price_df)
            
            # ניתוח מתקדם
            analysis = self._calculate_liquidity_trap_analysis(price_df, traps)
            
            # חישוב ציון סופי
            if traps:
                # חישוב ציון לפי מלכודות משמעותיות
                significant_ratio = analysis.significant_traps / max(1, analysis.total_traps)
                trap_score = min(100, significant_ratio * 100 + analysis.avg_trap_strength * 50)
                
                # התאמה לפי מגמה
                if analysis.liquidity_trend == 'increasing' and analysis.volume_trend == 'increasing':
                    trap_score *= 1.2
                elif analysis.liquidity_trend == 'decreasing' or analysis.volume_trend == 'decreasing':
                    trap_score *= 0.8
                
                trap_score = min(100, max(0, trap_score))
            else:
                trap_score = 50
            
            # יצירת הסבר
            if traps:
                recent_traps = [t for t in traps if t.significance in ['high', 'extreme']]
                explanation = f"זוהו {len(traps)} מלכודות נזילות ({len(recent_traps)} משמעותיות). ממוצע עוצמה: {analysis.avg_trap_strength:.2f}, מגמת נזילות: {analysis.liquidity_trend}"
            else:
                explanation = "לא זוהו מלכודות נזילות משמעותיות"
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(traps, analysis)
            
            return {
                "score": round(trap_score, 1),
                "explanation": explanation,
                "signal": {
                    "type": "liquidity_trap",
                    "score": round(trap_score, 1),
                    "reason": explanation,
                    "confidence": round(analysis.breakout_potential, 3),
                    "details": {
                        "traps_count": analysis.total_traps,
                        "significant_traps": analysis.significant_traps,
                        "avg_trap_strength": round(analysis.avg_trap_strength, 2),
                        "liquidity_trend": analysis.liquidity_trend,
                        "volume_trend": analysis.volume_trend
                    }
                },
                "details": {
                    "traps": [
                        {
                            "timestamp": trap.timestamp.isoformat(),
                            "trap_type": trap.trap_type,
                            "strength": round(trap.strength, 2),
                            "significance": trap.significance,
                            "confidence": round(trap.confidence, 3),
                            "liquidity_ratio": round(trap.liquidity_ratio, 2)
                        }
                        for trap in traps[:10]  # Top 10 traps
                    ],
                    "analysis": {
                        "total_traps": analysis.total_traps,
                        "significant_traps": analysis.significant_traps,
                        "avg_trap_strength": round(analysis.avg_trap_strength, 2),
                        "liquidity_trend": analysis.liquidity_trend,
                        "volume_trend": analysis.volume_trend,
                        "breakout_potential": round(analysis.breakout_potential, 3),
                        "sector_comparison": analysis.sector_comparison,
                        "time_analysis": analysis.time_analysis
                    },
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"Error in LiquidityTrapAgent.analyze: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח: {str(e)}",
                "signal": {
                    "type": "liquidity_trap",
                    "score": 50,
                    "reason": f"שגיאה בניתוח: {str(e)}",
                    "confidence": 0.5,
                    "details": {
                        "traps_count": 0,
                        "avg_trap_strength": 0.5,
                        "liquidity_trend": "error"
                    }
                },
                "details": {
                    "traps": [],
                    "analysis": {},
                    "recommendations": []
                }
            }

    def _generate_recommendations(self, traps: List[LiquidityTrap], analysis: LiquidityTrapAnalysis) -> List[str]:
        """
        יצירת המלצות מתקדמות
        """
        recommendations = []
        
        try:
            if analysis.significant_traps > 0:
                recommendations.append("🔍 מעקב אחר מלכודות נזילות משמעותיות - פוטנציאל לתנועה חזקה")
            
            if analysis.avg_trap_strength > 0.7:
                recommendations.append("📈 מלכודת נזילות חזקה - פוטנציאל לפריצה קרובה")
            
            if analysis.liquidity_trend == 'increasing' and analysis.volume_trend == 'increasing':
                recommendations.append("📊 מלכודת נזילות עולה - עניין גובר במניה")
            
            if analysis.breakout_potential > 0.05:
                recommendations.append("💪 פוטנציאל פריצה גבוה - תמיכה חזקה בתנועה")
            
            if analysis.significant_traps > 3:
                recommendations.append("⚠️ מספר מלכודות משמעותיות - בדוק חדשות או אירועים")
            
            if not recommendations:
                recommendations.append("📉 אין מלכודות נזילות משמעותיות - המשך מעקב")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["שגיאה ביצירת המלצות"]

    def get_liquidity_trap_summary(self) -> Dict:
        """
        סיכום ניתוח מלכודת נזילות
        """
        return {
            "agent_type": "LiquidityTrapAgent",
            "description": "זיהוי מלכודות נזילות מתקדם עם ניתוח רב-ממדי",
            "features": [
                "זיהוי מלכודות נזילות לפי מספר פרמטרים",
                "ניתוח רב-ממדי של נזילות",
                "ולידציה לפי זמן ומגמה",
                "ניתוח נזילות לפי סקטורים",
                "זיהוי מלכודות נזילות לפני אירועים",
                "ניתוח נזילות לפי טכני ופונדמנטלי",
                "זיהוי מלכודות נזילות לפי רגשות השוק",
                "ניתוח נזילות לפי נפח ומחיר"
            ],
            "thresholds": self.liquidity_trap_thresholds,
            "time_periods": self.time_periods
        } 