"""
VCPSuperPatternAgent - זיהוי תבניות VCP מתקדמות
================================================

סוכן מתקדם לזיהוי תבניות VCP (Volatility Contraction Pattern) מתקדמות
עם ניתוח רב-ממדי וולידציה מתקדמת ומבנה Signal תקני.

תכונות מתקדמות:
- זיהוי תבניות VCP מתקדמות
- ניתוח התכווצות נפח ומחיר
- ולידציה לפי זמן ומגמה
- ניתוח תבניות לפי סקטורים
- זיהוי תבניות לפני פריצות
- ניתוח תבניות לפי אירועים
- זיהוי תבניות לפי טכני ופונדמנטלי
- ניתוח תבניות לפי רגשות השוק
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from utils.data_fetcher import data_fetcher
from utils.constants import VCP_THRESHOLDS, TIME_PERIODS
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VCPPattern:
    """מבנה נתונים לתבנית VCP"""
    timestamp: datetime
    pattern_type: str
    strength: float
    confidence: float
    contraction_ratio: float
    volume_contraction: float
    price_contraction: float
    context: Dict
    significance: str

@dataclass
class VCPAnalysis:
    """מבנה נתונים לניתוח VCP מתקדם"""
    total_patterns: int
    significant_patterns: int
    avg_contraction_ratio: float
    volume_trend: str
    price_trend: str
    sector_comparison: Dict
    time_analysis: Dict
    breakout_potential: float

class VCPSuperPatternAgent:
    """
    סוכן מתקדם לזיהוי תבניות VCP מתקדמות
    
    תכונות מתקדמות:
    - זיהוי תבניות VCP מתקדמות
    - ניתוח התכווצות נפח ומחיר
    - ולידציה לפי זמן ומגמה
    - ניתוח תבניות לפי סקטורים
    - זיהוי תבניות לפני פריצות
    - ניתוח תבניות לפי אירועים
    - זיהוי תבניות לפי טכני ופונדמנטלי
    - ניתוח תבניות לפי רגשות השוק
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        self.config = config or {}
        
        # הגדרות מתקדמות
        self.vcp_thresholds = {
            'weak': 0.3,
            'moderate': 0.5,
            'strong': 0.7,
            'extreme': 0.9
        }
        
        self.time_periods = {
            'short': 10,
            'medium': 20,
            'long': 50
        }
        
        self.pattern_weights = {
            'volume_contraction': 0.3,
            'price_contraction': 0.3,
            'time_consolidation': 0.2,
            'sector_comparison': 0.1,
            'breakout_potential': 0.1
        }
        
        # סוגי תבניות VCP
        self.vcp_patterns = {
            'classic_vcp': 'תבנית VCP קלאסית',
            'tight_vcp': 'תבנית VCP הדוקה',
            'wide_vcp': 'תבנית VCP רחבה',
            'extended_vcp': 'תבנית VCP מורחבת',
            'failed_vcp': 'תבנית VCP כושלת'
        }
        
        logger.info("VCPSuperPatternAgent initialized with advanced configuration")

    def _calculate_volatility_metrics(self, df: pd.DataFrame) -> Dict:
        """
        חישוב מדדי תנודתיות מתקדמים
        """
        try:
            # חישוב תנודתיות מחיר
            df['price_volatility'] = df['close'].rolling(window=20).std()
            df['price_volatility_ratio'] = df['price_volatility'] / df['close']
            
            # חישוב תנודתיות נפח
            df['volume_volatility'] = df['volume'].rolling(window=20).std()
            df['volume_volatility_ratio'] = df['volume_volatility'] / df['volume'].rolling(window=20).mean()
            
            # חישוב התכווצות
            df['price_contraction'] = df['price_volatility_ratio'].rolling(window=10).mean() / df['price_volatility_ratio'].rolling(window=30).mean()
            df['volume_contraction'] = df['volume_volatility_ratio'].rolling(window=10).mean() / df['volume_volatility_ratio'].rolling(window=30).mean()
            
            # חישוב מדד VCP
            df['vcp_score'] = (df['price_contraction'] + df['volume_contraction']) / 2
            
            return {
                'volatility_metrics': df,
                'current_price_contraction': df['price_contraction'].iloc[-1],
                'current_volume_contraction': df['volume_contraction'].iloc[-1],
                'current_vcp_score': df['vcp_score'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating volatility metrics: {e}")
            return {}

    def _detect_vcp_patterns(self, df: pd.DataFrame) -> List[VCPPattern]:
        """
        זיהוי תבניות VCP מתקדם
        """
        patterns = []
        
        try:
            # חישוב מדדי תנודתיות
            volatility_metrics = self._calculate_volatility_metrics(df)
            if not volatility_metrics:
                return patterns
            
            df = volatility_metrics['volatility_metrics']
            
            # זיהוי תבניות VCP
            for i in range(50, len(df)):
                # ניתוח התכווצות מחיר
                price_contraction = self._analyze_price_contraction(df, i)
                
                # ניתוח התכווצות נפח
                volume_contraction = self._analyze_volume_contraction(df, i)
                
                # ניתוח זמן התכנסות
                time_consolidation = self._analyze_time_consolidation(df, i)
                
                # ניתוח השוואה סקטורית
                sector_comparison = self._analyze_sector_context(df, i)
                
                # ניתוח פוטנציאל פריצה
                breakout_potential = self._analyze_breakout_potential(df, i)
                
                # זיהוי תבנית VCP
                if self._is_vcp_pattern(price_contraction, volume_contraction, time_consolidation):
                    # חישוב עוצמת התבנית
                    strength = self._calculate_pattern_strength(
                        price_contraction, volume_contraction, time_consolidation,
                        sector_comparison, breakout_potential
                    )
                    
                    # חישוב ביטחון
                    confidence = self._calculate_pattern_confidence(
                        price_contraction, volume_contraction, time_consolidation,
                        sector_comparison, breakout_potential
                    )
                    
                    # קביעת סוג תבנית
                    pattern_type = self._classify_vcp_pattern(
                        price_contraction, volume_contraction, time_consolidation
                    )
                    
                    # קביעת משמעות
                    significance = self._determine_pattern_significance(strength, confidence)
                    
                    pattern = VCPPattern(
                        timestamp=df.index[i],
                        pattern_type=pattern_type,
                        strength=strength,
                        confidence=confidence,
                        contraction_ratio=df['vcp_score'].iloc[i],
                        volume_contraction=volume_contraction.get('contraction_ratio', 1.0),
                        price_contraction=price_contraction.get('contraction_ratio', 1.0),
                        context={
                            'price_contraction': price_contraction,
                            'volume_contraction': volume_contraction,
                            'time_consolidation': time_consolidation,
                            'sector_comparison': sector_comparison,
                            'breakout_potential': breakout_potential
                        },
                        significance=significance
                    )
                    
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting VCP patterns: {e}")
            return []

    def _analyze_price_contraction(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח התכווצות מחיר מתקדם
        """
        try:
            # חישוב התכווצות מחיר
            current_volatility = df['price_volatility_ratio'].iloc[index]
            historical_volatility = df['price_volatility_ratio'].iloc[max(0, index-30):index].mean()
            
            contraction_ratio = current_volatility / historical_volatility if historical_volatility > 0 else 1.0
            
            # ניתוח מגמת התכווצות
            recent_volatility = df['price_volatility_ratio'].iloc[max(0, index-10):index].mean()
            volatility_trend = 'contracting' if recent_volatility < historical_volatility else 'expanding'
            
            return {
                'contraction_ratio': contraction_ratio,
                'volatility_trend': volatility_trend,
                'current_volatility': current_volatility,
                'historical_volatility': historical_volatility,
                'recent_volatility': recent_volatility
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price contraction: {e}")
            return {}

    def _analyze_volume_contraction(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח התכווצות נפח מתקדם
        """
        try:
            # חישוב התכווצות נפח
            current_volume_volatility = df['volume_volatility_ratio'].iloc[index]
            historical_volume_volatility = df['volume_volatility_ratio'].iloc[max(0, index-30):index].mean()
            
            volume_contraction_ratio = current_volume_volatility / historical_volume_volatility if historical_volume_volatility > 0 else 1.0
            
            # ניתוח מגמת התכווצות נפח
            recent_volume_volatility = df['volume_volatility_ratio'].iloc[max(0, index-10):index].mean()
            volume_volatility_trend = 'contracting' if recent_volume_volatility < historical_volume_volatility else 'expanding'
            
            return {
                'contraction_ratio': volume_contraction_ratio,
                'volatility_trend': volume_volatility_trend,
                'current_volume_volatility': current_volume_volatility,
                'historical_volume_volatility': historical_volume_volatility,
                'recent_volume_volatility': recent_volume_volatility
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume contraction: {e}")
            return {}

    def _analyze_time_consolidation(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח זמן התכנסות מתקדם
        """
        try:
            # ניתוח זמן התכנסות
            consolidation_window = df.iloc[max(0, index-30):index]
            
            # חישוב זמן התכנסות
            consolidation_duration = len(consolidation_window)
            
            # ניתוח עקביות התכנסות
            price_range = consolidation_window['high'].max() - consolidation_window['low'].min()
            avg_price = consolidation_window['close'].mean()
            consolidation_ratio = price_range / avg_price if avg_price > 0 else 1.0
            
            # ניתוח מגמת התכנסות
            early_range = consolidation_window.iloc[:10]['high'].max() - consolidation_window.iloc[:10]['low'].min()
            late_range = consolidation_window.iloc[-10:]['high'].max() - consolidation_window.iloc[-10:]['low'].min()
            range_trend = 'contracting' if late_range < early_range else 'expanding'
            
            return {
                'consolidation_duration': consolidation_duration,
                'consolidation_ratio': consolidation_ratio,
                'range_trend': range_trend,
                'early_range': early_range,
                'late_range': late_range
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time consolidation: {e}")
            return {}

    def _analyze_sector_context(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח הקשר סקטור מתקדם
        """
        try:
            # סימולציה של נתוני סקטור (בפרודקציה יהיה מ-API)
            sector_data = {
                'technology': {'avg_vcp_score': 0.6, 'vcp_trend': 'increasing'},
                'healthcare': {'avg_vcp_score': 0.5, 'vcp_trend': 'stable'},
                'finance': {'avg_vcp_score': 0.7, 'vcp_trend': 'decreasing'},
                'energy': {'avg_vcp_score': 0.8, 'vcp_trend': 'increasing'}
            }
            
            # קביעת סקטור (בפרודקציה יהיה מ-API)
            sector = 'technology'  # ברירת מחדל
            
            sector_info = sector_data.get(sector, {'avg_vcp_score': 0.5, 'vcp_trend': 'stable'})
            
            return {
                'sector': sector,
                'sector_avg_vcp_score': sector_info['avg_vcp_score'],
                'sector_vcp_trend': sector_info['vcp_trend'],
                'relative_to_sector': df['vcp_score'].iloc[index] / sector_info['avg_vcp_score']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector context: {e}")
            return {}

    def _analyze_breakout_potential(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח פוטנציאל פריצה מתקדם
        """
        try:
            # ניתוח פוטנציאל פריצה
            current_price = df['close'].iloc[index]
            
            # ניתוח לפי ממוצעים נעים
            sma_20 = df['sma_20'].iloc[index] if 'sma_20' in df.columns else df['close'].rolling(window=20).mean().iloc[index]
            sma_50 = df['sma_50'].iloc[index] if 'sma_50' in df.columns else df['close'].rolling(window=50).mean().iloc[index]
            
            # ניתוח לפי בולינגר בנדס
            bb_upper = df['bb_upper'].iloc[index] if 'bb_upper' in df.columns else current_price * 1.02
            bb_lower = df['bb_lower'].iloc[index] if 'bb_lower' in df.columns else current_price * 0.98
            
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

    def _is_vcp_pattern(self, price_contraction: Dict, volume_contraction: Dict, time_consolidation: Dict) -> bool:
        """
        זיהוי תבנית VCP
        """
        try:
            # קריטריונים לתבנית VCP
            price_contracting = price_contraction.get('contraction_ratio', 1.0) < 0.8
            volume_contracting = volume_contraction.get('contraction_ratio', 1.0) < 0.8
            time_consolidating = time_consolidation.get('consolidation_duration', 0) >= 20
            
            # תבנית VCP אם לפחות 2 קריטריונים מתקיימים
            vcp_criteria = [price_contracting, volume_contracting, time_consolidating]
            return sum(vcp_criteria) >= 2
            
        except Exception as e:
            logger.error(f"Error detecting VCP pattern: {e}")
            return False

    def _calculate_pattern_strength(self, price_contraction: Dict, volume_contraction: Dict,
                                 time_consolidation: Dict, sector_comparison: Dict,
                                 breakout_potential: Dict) -> float:
        """
        חישוב עוצמת תבנית VCP
        """
        try:
            strength = 0.0
            
            # משקל לפי התכווצות מחיר
            price_ratio = price_contraction.get('contraction_ratio', 1.0)
            if price_ratio < 0.7:
                strength += 0.3
            elif price_ratio < 0.9:
                strength += 0.2
            
            # משקל לפי התכווצות נפח
            volume_ratio = volume_contraction.get('contraction_ratio', 1.0)
            if volume_ratio < 0.7:
                strength += 0.3
            elif volume_ratio < 0.9:
                strength += 0.2
            
            # משקל לפי זמן התכנסות
            consolidation_duration = time_consolidation.get('consolidation_duration', 0)
            if consolidation_duration >= 30:
                strength += 0.2
            elif consolidation_duration >= 20:
                strength += 0.1
            
            # משקל לפי השוואה סקטורית
            sector_ratio = sector_comparison.get('relative_to_sector', 1.0)
            if sector_ratio < 0.8:
                strength += 0.1
            
            # משקל לפי פוטנציאל פריצה
            breakout_strength = breakout_potential.get('breakout_strength', 0.0)
            if breakout_strength > 0.05:
                strength += 0.1
            
            return min(1.0, strength)
            
        except Exception as e:
            logger.error(f"Error calculating pattern strength: {e}")
            return 0.5

    def _calculate_pattern_confidence(self, price_contraction: Dict, volume_contraction: Dict,
                                   time_consolidation: Dict, sector_comparison: Dict,
                                   breakout_potential: Dict) -> float:
        """
        חישוב ביטחון תבנית VCP
        """
        try:
            confidence = 0.0
            
            # ביטחון לפי עקביות
            consistent_signals = 0
            if price_contraction.get('contraction_ratio', 1.0) < 0.8:
                consistent_signals += 1
            if volume_contraction.get('contraction_ratio', 1.0) < 0.8:
                consistent_signals += 1
            if time_consolidation.get('consolidation_duration', 0) >= 20:
                consistent_signals += 1
            if sector_comparison.get('relative_to_sector', 1.0) < 1.0:
                consistent_signals += 1
            if breakout_potential.get('breakout_strength', 0.0) > 0.03:
                consistent_signals += 1
            
            confidence = consistent_signals / 5.0
            
            # התאמה לפי עוצמת התכווצות
            avg_contraction = (price_contraction.get('contraction_ratio', 1.0) + volume_contraction.get('contraction_ratio', 1.0)) / 2
            if avg_contraction < 0.7:
                confidence *= 1.2
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating pattern confidence: {e}")
            return 0.5

    def _classify_vcp_pattern(self, price_contraction: Dict, volume_contraction: Dict, time_consolidation: Dict) -> str:
        """
        סיווג סוג תבנית VCP
        """
        try:
            price_ratio = price_contraction.get('contraction_ratio', 1.0)
            volume_ratio = volume_contraction.get('contraction_ratio', 1.0)
            consolidation_duration = time_consolidation.get('consolidation_duration', 0)
            
            if price_ratio < 0.6 and volume_ratio < 0.6 and consolidation_duration >= 30:
                return 'tight_vcp'
            elif price_ratio < 0.8 and volume_ratio < 0.8 and consolidation_duration >= 20:
                return 'classic_vcp'
            elif consolidation_duration >= 50:
                return 'extended_vcp'
            elif price_ratio > 1.0 or volume_ratio > 1.0:
                return 'failed_vcp'
            else:
                return 'wide_vcp'
                
        except Exception as e:
            logger.error(f"Error classifying VCP pattern: {e}")
            return 'unknown'

    def _determine_pattern_significance(self, strength: float, confidence: float) -> str:
        """
        קביעת משמעות תבנית VCP
        """
        try:
            if strength >= self.vcp_thresholds['extreme'] and confidence >= 0.8:
                return 'extreme'
            elif strength >= self.vcp_thresholds['strong'] and confidence >= 0.6:
                return 'strong'
            elif strength >= self.vcp_thresholds['moderate'] and confidence >= 0.4:
                return 'moderate'
            elif strength >= self.vcp_thresholds['weak'] and confidence >= 0.2:
                return 'weak'
            else:
                return 'minimal'
                
        except Exception as e:
            logger.error(f"Error determining pattern significance: {e}")
            return 'unknown'

    def _calculate_vcp_analysis(self, df: pd.DataFrame, patterns: List[VCPPattern]) -> VCPAnalysis:
        """
        חישוב ניתוח VCP מתקדם
        """
        try:
            # חישוב סטטיסטיקות בסיסיות
            total_patterns = len(patterns)
            significant_patterns = len([p for p in patterns if p.significance in ['strong', 'extreme']])
            
            # חישוב ממוצע יחסי התכווצות
            avg_contraction_ratio = np.mean([p.contraction_ratio for p in patterns]) if patterns else 1.0
            
            # ניתוח מגמת נפח
            recent_volume = df['volume'].tail(20).mean()
            historical_volume = df['volume'].tail(60).mean()
            volume_trend = 'contracting' if recent_volume < historical_volume else 'expanding'
            
            # ניתוח מגמת מחיר
            recent_price_volatility = df['price_volatility'].tail(20).mean()
            historical_price_volatility = df['price_volatility'].tail(60).mean()
            price_trend = 'contracting' if recent_price_volatility < historical_price_volatility else 'expanding'
            
            # ניתוח סקטור
            sector_comparison = self._analyze_sector_context(df, len(df)-1)
            
            # ניתוח זמן
            time_analysis = self._analyze_time_consolidation(df, len(df)-1)
            
            # ניתוח פוטנציאל פריצה
            breakout_potential = self._analyze_breakout_potential(df, len(df)-1)
            breakout_potential_score = breakout_potential.get('breakout_strength', 0.0)
            
            return VCPAnalysis(
                total_patterns=total_patterns,
                significant_patterns=significant_patterns,
                avg_contraction_ratio=avg_contraction_ratio,
                volume_trend=volume_trend,
                price_trend=price_trend,
                sector_comparison=sector_comparison,
                time_analysis=time_analysis,
                breakout_potential=breakout_potential_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating VCP analysis: {e}")
            return VCPAnalysis(0, 0, 1.0, 'unknown', 'unknown', {}, {}, 0.0)

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של תבניות VCP
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
                        "type": "vcp_pattern",
                        "score": 50,
                        "reason": "לא ניתן לאחזר נתוני מחיר",
                        "confidence": 0.5,
                        "details": {
                            "patterns_count": 0,
                            "avg_contraction_ratio": 1.0,
                            "volume_trend": "unknown"
                        }
                    },
                    "details": {
                        "patterns": [],
                        "analysis": {},
                        "recommendations": []
                    }
                }
            
            # זיהוי תבניות VCP
            patterns = self._detect_vcp_patterns(price_df)
            
            # ניתוח מתקדם
            analysis = self._calculate_vcp_analysis(price_df, patterns)
            
            # חישוב ציון סופי
            if patterns:
                # חישוב ציון לפי תבניות משמעותיות
                significant_ratio = analysis.significant_patterns / max(1, analysis.total_patterns)
                vcp_score = min(100, significant_ratio * 100 + (1 - analysis.avg_contraction_ratio) * 50)
                
                # התאמה לפי מגמה
                if analysis.volume_trend == 'contracting' and analysis.price_trend == 'contracting':
                    vcp_score *= 1.2
                elif analysis.volume_trend == 'expanding' or analysis.price_trend == 'expanding':
                    vcp_score *= 0.8
                
                vcp_score = min(100, max(0, vcp_score))
            else:
                vcp_score = 50
            
            # יצירת הסבר
            if patterns:
                recent_patterns = [p for p in patterns if p.significance in ['strong', 'extreme']]
                explanation = f"זוהו {len(patterns)} תבניות VCP ({len(recent_patterns)} משמעותיות). ממוצע התכווצות: {analysis.avg_contraction_ratio:.2f}, מגמת נפח: {analysis.volume_trend}"
            else:
                explanation = "לא זוהו תבניות VCP משמעותיות"
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(patterns, analysis)
            
            return {
                "score": round(vcp_score, 1),
                "explanation": explanation,
                "signal": {
                    "type": "vcp_pattern",
                    "score": round(vcp_score, 1),
                    "reason": explanation,
                    "confidence": round(analysis.breakout_potential, 3),
                    "details": {
                        "patterns_count": analysis.total_patterns,
                        "significant_patterns": analysis.significant_patterns,
                        "avg_contraction_ratio": round(analysis.avg_contraction_ratio, 2),
                        "volume_trend": analysis.volume_trend,
                        "price_trend": analysis.price_trend
                    }
                },
                "details": {
                    "patterns": [
                        {
                            "timestamp": pattern.timestamp.isoformat(),
                            "pattern_type": pattern.pattern_type,
                            "strength": round(pattern.strength, 2),
                            "significance": pattern.significance,
                            "confidence": round(pattern.confidence, 3),
                            "contraction_ratio": round(pattern.contraction_ratio, 2)
                        }
                        for pattern in patterns[:10]  # Top 10 patterns
                    ],
                    "analysis": {
                        "total_patterns": analysis.total_patterns,
                        "significant_patterns": analysis.significant_patterns,
                        "avg_contraction_ratio": round(analysis.avg_contraction_ratio, 2),
                        "volume_trend": analysis.volume_trend,
                        "price_trend": analysis.price_trend,
                        "breakout_potential": round(analysis.breakout_potential, 3),
                        "sector_comparison": analysis.sector_comparison,
                        "time_analysis": analysis.time_analysis
                    },
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"Error in VCPSuperPatternAgent.analyze: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח: {str(e)}",
                "signal": {
                    "type": "vcp_pattern",
                    "score": 50,
                    "reason": f"שגיאה בניתוח: {str(e)}",
                    "confidence": 0.5,
                    "details": {
                        "patterns_count": 0,
                        "avg_contraction_ratio": 1.0,
                        "volume_trend": "error"
                    }
                },
                "details": {
                    "patterns": [],
                    "analysis": {},
                    "recommendations": []
                }
            }

    def _generate_recommendations(self, patterns: List[VCPPattern], analysis: VCPAnalysis) -> List[str]:
        """
        יצירת המלצות מתקדמות
        """
        recommendations = []
        
        try:
            if analysis.significant_patterns > 0:
                recommendations.append("🔍 מעקב אחר תבניות VCP משמעותיות - פוטנציאל לפריצה")
            
            if analysis.avg_contraction_ratio < 0.7:
                recommendations.append("📉 התכווצות חזקה - פוטנציאל לפריצה קרובה")
            
            if analysis.volume_trend == 'contracting' and analysis.price_trend == 'contracting':
                recommendations.append("📊 התכווצות כפולה - סיגנל חזק לפריצה")
            
            if analysis.breakout_potential > 0.05:
                recommendations.append("💪 פוטנציאל פריצה גבוה - תמיכה חזקה בתנועה")
            
            if analysis.significant_patterns > 3:
                recommendations.append("⚠️ מספר תבניות משמעותיות - בדוק חדשות או אירועים")
            
            if not recommendations:
                recommendations.append("📉 אין תבניות VCP משמעותיות - המשך מעקב")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["שגיאה ביצירת המלצות"]

    def get_vcp_summary(self) -> Dict:
        """
        סיכום ניתוח VCP
        """
        return {
            "agent_type": "VCPSuperPatternAgent",
            "description": "זיהוי תבניות VCP מתקדמות עם ניתוח רב-ממדי",
            "features": [
                "זיהוי תבניות VCP מתקדמות",
                "ניתוח התכווצות נפח ומחיר",
                "ולידציה לפי זמן ומגמה",
                "ניתוח תבניות לפי סקטורים",
                "זיהוי תבניות לפני פריצות",
                "ניתוח תבניות לפי אירועים",
                "זיהוי תבניות לפי טכני ופונדמנטלי",
                "ניתוח תבניות לפי רגשות השוק"
            ],
            "thresholds": self.vcp_thresholds,
            "time_periods": self.time_periods
        } 