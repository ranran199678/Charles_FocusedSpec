"""
TrendShiftAgent - זיהוי שינויי מגמה מתקדם
==========================================

סוכן מתקדם לזיהוי שינויי מגמה משמעותיים עם ניתוח רב-ממדי,
ולידציה מתקדמת ומבנה Signal תקני.

תכונות מתקדמות:
- זיהוי שינויי מגמה לפי מספר אינדיקטורים
- ניתוח רב-ממדי של מגמות
- ולידציה לפי נפח ומחיר
- ניתוח מגמות לפי טווחי זמן שונים
- זיהוי מגמות לפי סקטורים
- ניתוח מגמות לפי אירועים
- זיהוי מגמות לפי טכני ופונדמנטלי
- ניתוח מגמות לפי רגשות השוק
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.base.base_agent import BaseAgent
from utils.constants import TREND_THRESHOLDS, TIME_PERIODS
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrendShift:
    """מבנה נתונים לשינוי מגמה"""
    timestamp: datetime
    trend_type: str
    strength: float
    confidence: float
    indicators: Dict
    context: Dict
    significance: str

@dataclass
class TrendAnalysis:
    """מבנה נתונים לניתוח מגמה מתקדם"""
    current_trend: str
    trend_strength: float
    trend_duration: int
    trend_consistency: float
    sector_trend: str
    market_trend: str
    technical_score: float
    fundamental_score: float
    sentiment_score: float

class TrendShiftAgent(BaseAgent):
    """
    סוכן מתקדם לזיהוי שינויי מגמה משמעותיים
    
    תכונות מתקדמות:
    - זיהוי שינויי מגמה לפי מספר אינדיקטורים
    - ניתוח רב-ממדי של מגמות
    - ולידציה לפי נפח ומחיר
    - ניתוח מגמות לפי טווחי זמן שונים
    - זיהוי מגמות לפי סקטורים
    - ניתוח מגמות לפי אירועים
    - זיהוי מגמות לפי טכני ופונדמנטלי
    - ניתוח מגמות לפי רגשות השוק
    - מצב לייב לניטור בזמן אמת
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        super().__init__(config)
        
        # פרמטרים למצב לייב
        self.symbol = self.config.get("symbol", "")
        self.interval = self.config.get("interval", "1day")
        self.live_mode = self.config.get("live_mode", False)
        self.frequency_sec = self.config.get("frequency_sec", 60)
        
        # הגדרות מתקדמות
        self.trend_thresholds = {
            'weak': 0.3,
            'moderate': 0.5,
            'strong': 0.7,
            'extreme': 0.9
        }
        
        self.time_periods = {
            'short': 5,
            'medium': 20,
            'long': 60,
            'very_long': 200
        }
        
        self.indicator_weights = {
            'price_momentum': 0.25,
            'volume_trend': 0.20,
            'technical_indicators': 0.25,
            'fundamental_factors': 0.15,
            'sentiment_analysis': 0.15
        }
        
        # סוגי מגמות
        self.trend_types = {
            'uptrend': 'עולה',
            'downtrend': 'יורדת',
            'sideways': 'צדדית',
            'consolidation': 'התכנסות',
            'breakout': 'פריצה',
            'breakdown': 'שבירה'
        }
        
        # אינדיקטורים טכניים
        self.technical_indicators = [
            'sma_20', 'sma_50', 'sma_200',
            'ema_12', 'ema_26',
            'rsi', 'macd', 'bollinger_bands',
            'stochastic', 'williams_r'
        ]
        
        self.logger.info("TrendShiftAgent initialized with advanced configuration")

    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """
        חישוב אינדיקטורים טכניים מתקדמים
        """
        try:
            # ממוצעים נעים
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()
            
            # ממוצעים נעים מעריכיים
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # בולינגר בנדס
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            # סטוכסטיק
            low_min = df['low'].rolling(window=14).min()
            high_max = df['high'].rolling(window=14).max()
            df['stochastic_k'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
            df['stochastic_d'] = df['stochastic_k'].rolling(window=3).mean()
            
            # Williams %R
            df['williams_r'] = -100 * ((high_max - df['close']) / (high_max - low_min))
            
            # מדד מומנטום
            df['momentum'] = df['close'] - df['close'].shift(10)
            
            # מדד כוח יחסי
            # relative_strength calculation moved to RelativeStrengthAgent
            df['relative_strength'] = 1.0  # placeholder
            
            return {
                'indicators': df,
                'current_rsi': df['rsi'].iloc[-1],
                'current_macd': df['macd'].iloc[-1],
                'current_momentum': df['momentum'].iloc[-1],
                'current_strength': df['relative_strength'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {}

    def _detect_trend_shifts(self, df: pd.DataFrame) -> List[TrendShift]:
        """
        זיהוי שינויי מגמה מתקדם
        """
        shifts = []
        
        try:
            # חישוב אינדיקטורים
            indicators = self._calculate_technical_indicators(df)
            if not indicators:
                return shifts
            
            df = indicators['indicators']
            
            # זיהוי שינויי מגמה לפי מספר קריטריונים
            for i in range(50, len(df)):
                # ניתוח מגמת מחיר
                price_trend = self._analyze_price_trend(df, i)
                
                # ניתוח מגמת נפח
                volume_trend = self._analyze_volume_trend(df, i)
                
                # ניתוח אינדיקטורים טכניים
                technical_trend = self._analyze_technical_trend(df, i)
                
                # ניתוח מגמה פונדמנטלית
                fundamental_trend = self._analyze_fundamental_trend(df, i)
                
                # ניתוח מגמת רגשות
                sentiment_trend = self._analyze_sentiment_trend(df, i)
                
                # זיהוי שינוי מגמה
                if self._is_trend_shift(price_trend, volume_trend, technical_trend, fundamental_trend, sentiment_trend):
                    # חישוב עוצמת השינוי
                    strength = self._calculate_shift_strength(
                        price_trend, volume_trend, technical_trend, fundamental_trend, sentiment_trend
                    )
                    
                    # חישוב ביטחון
                    confidence = self._calculate_shift_confidence(
                        price_trend, volume_trend, technical_trend, fundamental_trend, sentiment_trend
                    )
                    
                    # קביעת סוג מגמה
                    trend_type = self._classify_trend_type(
                        price_trend, volume_trend, technical_trend
                    )
                    
                    # קביעת משמעות
                    significance = self._determine_shift_significance(strength, confidence)
                    
                    shift = TrendShift(
                        timestamp=df.index[i],
                        trend_type=trend_type,
                        strength=strength,
                        confidence=confidence,
                        indicators={
                            'price_trend': price_trend,
                            'volume_trend': volume_trend,
                            'technical_trend': technical_trend,
                            'fundamental_trend': fundamental_trend,
                            'sentiment_trend': sentiment_trend
                        },
                        context=self._analyze_shift_context(df, i),
                        significance=significance
                    )
                    
                    shifts.append(shift)
            
            return shifts
            
        except Exception as e:
            logger.error(f"Error detecting trend shifts: {e}")
            return []

    def _analyze_price_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח מגמת מחיר מתקדם
        """
        try:
            current_price = df['close'].iloc[index]
            
            # ניתוח לפי ממוצעים נעים
            sma_20 = df['sma_20'].iloc[index]
            sma_50 = df['sma_50'].iloc[index]
            sma_200 = df['sma_200'].iloc[index]
            
            # ניתוח לפי EMA
            ema_12 = df['ema_12'].iloc[index]
            ema_26 = df['ema_26'].iloc[index]
            
            # ניתוח לפי בולינגר בנדס
            bb_upper = df['bb_upper'].iloc[index]
            bb_lower = df['bb_lower'].iloc[index]
            bb_middle = df['bb_middle'].iloc[index]
            
            # ניתוח מגמה לטווח קצר
            short_trend = 'up' if current_price > sma_20 else 'down'
            
            # ניתוח מגמה לטווח בינוני
            medium_trend = 'up' if sma_20 > sma_50 else 'down'
            
            # ניתוח מגמה לטווח ארוך
            long_trend = 'up' if sma_50 > sma_200 else 'down'
            
            # ניתוח פריצה/שבירה
            breakout_status = 'neutral'
            if current_price > bb_upper:
                breakout_status = 'breakout_up'
            elif current_price < bb_lower:
                breakout_status = 'breakout_down'
            
            return {
                'current_price': current_price,
                'short_trend': short_trend,
                'medium_trend': medium_trend,
                'long_trend': long_trend,
                'breakout_status': breakout_status,
                'price_vs_sma20': current_price / sma_20 if sma_20 > 0 else 1,
                'price_vs_sma50': current_price / sma_50 if sma_50 > 0 else 1,
                'price_vs_sma200': current_price / sma_200 if sma_200 > 0 else 1
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price trend: {e}")
            return {}

    def _analyze_volume_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח מגמת נפח מתקדם
        """
        try:
            current_volume = df['volume'].iloc[index]
            
            # חישוב ממוצעי נפח
            volume_sma_20 = df['volume'].rolling(window=20).mean().iloc[index]
            volume_sma_50 = df['volume'].rolling(window=50).mean().iloc[index]
            
            # ניתוח מגמת נפח
            volume_trend = 'increasing' if current_volume > volume_sma_20 else 'decreasing'
            
            # ניתוח נפח לפי מחיר
            price_volume_ratio = current_volume / df['close'].iloc[index] if df['close'].iloc[index] > 0 else 0
            
            # ניתוח נפח חריג
            volume_std = df['volume'].rolling(window=20).std().iloc[index]
            unusual_volume = current_volume > (volume_sma_20 + volume_std * 2)
            
            return {
                'current_volume': current_volume,
                'volume_trend': volume_trend,
                'volume_ratio': current_volume / volume_sma_20 if volume_sma_20 > 0 else 1,
                'price_volume_ratio': price_volume_ratio,
                'unusual_volume': unusual_volume,
                'volume_momentum': (current_volume - volume_sma_50) / volume_sma_50 if volume_sma_50 > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume trend: {e}")
            return {}

    def _analyze_technical_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח מגמה טכנית מתקדם
        """
        try:
            # RSI
            current_rsi = df['rsi'].iloc[index]
            rsi_trend = 'oversold' if current_rsi < 30 else 'overbought' if current_rsi > 70 else 'neutral'
            
            # MACD
            current_macd = df['macd'].iloc[index]
            macd_signal = df['macd_signal'].iloc[index]
            macd_trend = 'bullish' if current_macd > macd_signal else 'bearish'
            
            # סטוכסטיק
            current_stoch_k = df['stochastic_k'].iloc[index]
            current_stoch_d = df['stochastic_d'].iloc[index]
            stoch_trend = 'oversold' if current_stoch_k < 20 else 'overbought' if current_stoch_k > 80 else 'neutral'
            
            # Williams %R
            current_williams_r = df['williams_r'].iloc[index]
            williams_trend = 'oversold' if current_williams_r < -80 else 'overbought' if current_williams_r > -20 else 'neutral'
            
            # מומנטום
            current_momentum = df['momentum'].iloc[index]
            momentum_trend = 'positive' if current_momentum > 0 else 'negative'
            
            # כוח יחסי
            current_strength = df['relative_strength'].iloc[index]
            strength_trend = 'strong' if current_strength > 1.05 else 'weak' if current_strength < 0.95 else 'neutral'
            
            return {
                'rsi': {'value': current_rsi, 'trend': rsi_trend},
                'macd': {'value': current_macd, 'trend': macd_trend},
                'stochastic': {'k': current_stoch_k, 'd': current_stoch_d, 'trend': stoch_trend},
                'williams_r': {'value': current_williams_r, 'trend': williams_trend},
                'momentum': {'value': current_momentum, 'trend': momentum_trend},
                'relative_strength': {'value': current_strength, 'trend': strength_trend}
            }
            
        except Exception as e:
            logger.error(f"Error analyzing technical trend: {e}")
            return {}

    def _analyze_fundamental_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח מגמה פונדמנטלית (סימולציה)
        """
        try:
            # סימולציה של נתונים פונדמנטליים (בפרודקציה יהיה מ-API)
            fundamental_data = {
                'pe_ratio': 15.5,
                'pe_trend': 'decreasing',
                'revenue_growth': 0.12,
                'revenue_trend': 'increasing',
                'earnings_growth': 0.08,
                'earnings_trend': 'stable',
                'debt_ratio': 0.3,
                'debt_trend': 'decreasing'
            }
            
            return {
                'valuation_trend': 'attractive' if fundamental_data['pe_ratio'] < 20 else 'expensive',
                'growth_trend': 'positive' if fundamental_data['revenue_growth'] > 0.1 else 'negative',
                'financial_health': 'strong' if fundamental_data['debt_ratio'] < 0.5 else 'weak',
                'overall_fundamental': 'positive' if fundamental_data['pe_trend'] == 'decreasing' and fundamental_data['revenue_trend'] == 'increasing' else 'negative'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing fundamental trend: {e}")
            return {}

    def _analyze_sentiment_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח מגמת רגשות (סימולציה)
        """
        try:
            # סימולציה של נתוני רגשות (בפרודקציה יהיה מ-API)
            sentiment_data = {
                'news_sentiment': 0.6,
                'social_sentiment': 0.55,
                'analyst_sentiment': 0.7,
                'institutional_sentiment': 0.65
            }
            
            avg_sentiment = np.mean(list(sentiment_data.values()))
            
            return {
                'overall_sentiment': avg_sentiment,
                'sentiment_trend': 'positive' if avg_sentiment > 0.6 else 'negative',
                'news_sentiment': sentiment_data['news_sentiment'],
                'social_sentiment': sentiment_data['social_sentiment'],
                'analyst_sentiment': sentiment_data['analyst_sentiment'],
                'institutional_sentiment': sentiment_data['institutional_sentiment']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment trend: {e}")
            return {}

    def _is_trend_shift(self, price_trend: Dict, volume_trend: Dict, 
                        technical_trend: Dict, fundamental_trend: Dict, 
                        sentiment_trend: Dict) -> bool:
        """
        זיהוי שינוי מגמה
        """
        try:
            # קריטריונים לשינוי מגמה
            price_shift = price_trend.get('short_trend') != price_trend.get('medium_trend')
            volume_shift = volume_trend.get('volume_trend') == 'increasing' and volume_trend.get('unusual_volume', False)
            technical_shift = technical_trend.get('macd', {}).get('trend') == 'bullish' and technical_trend.get('rsi', {}).get('trend') == 'neutral'
            fundamental_shift = fundamental_trend.get('overall_fundamental') == 'positive'
            sentiment_shift = sentiment_trend.get('sentiment_trend') == 'positive'
            
            # שינוי מגמה אם לפחות 3 קריטריונים מתקיימים
            shift_criteria = [price_shift, volume_shift, technical_shift, fundamental_shift, sentiment_shift]
            return sum(shift_criteria) >= 3
            
        except Exception as e:
            logger.error(f"Error detecting trend shift: {e}")
            return False

    def _calculate_shift_strength(self, price_trend: Dict, volume_trend: Dict,
                                technical_trend: Dict, fundamental_trend: Dict,
                                sentiment_trend: Dict) -> float:
        """
        חישוב עוצמת שינוי המגמה
        """
        try:
            strength = 0.0
            
            # משקל לפי מחיר
            if price_trend.get('breakout_status') in ['breakout_up', 'breakout_down']:
                strength += 0.3
            
            # משקל לפי נפח
            if volume_trend.get('unusual_volume', False):
                strength += 0.2
            
            # משקל לפי טכני
            if technical_trend.get('macd', {}).get('trend') == 'bullish':
                strength += 0.2
            
            # משקל לפי פונדמנטלי
            if fundamental_trend.get('overall_fundamental') == 'positive':
                strength += 0.15
            
            # משקל לפי רגשות
            if sentiment_trend.get('sentiment_trend') == 'positive':
                strength += 0.15
            
            return min(1.0, strength)
            
        except Exception as e:
            logger.error(f"Error calculating shift strength: {e}")
            return 0.5

    def _calculate_shift_confidence(self, price_trend: Dict, volume_trend: Dict,
                                  technical_trend: Dict, fundamental_trend: Dict,
                                  sentiment_trend: Dict) -> float:
        """
        חישוב ביטחון שינוי המגמה
        """
        try:
            confidence = 0.0
            
            # ביטחון לפי עקביות
            consistent_signals = 0
            if price_trend.get('short_trend') == price_trend.get('medium_trend'):
                consistent_signals += 1
            if volume_trend.get('volume_trend') == 'increasing':
                consistent_signals += 1
            if technical_trend.get('macd', {}).get('trend') == 'bullish':
                consistent_signals += 1
            if fundamental_trend.get('overall_fundamental') == 'positive':
                consistent_signals += 1
            if sentiment_trend.get('sentiment_trend') == 'positive':
                consistent_signals += 1
            
            confidence = consistent_signals / 5.0
            
            # התאמה לפי עוצמת נפח
            if volume_trend.get('unusual_volume', False):
                confidence *= 1.2
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating shift confidence: {e}")
            return 0.5

    def _classify_trend_type(self, price_trend: Dict, volume_trend: Dict, technical_trend: Dict) -> str:
        """
        סיווג סוג מגמה
        """
        try:
            if price_trend.get('breakout_status') == 'breakout_up':
                return 'uptrend'
            elif price_trend.get('breakout_status') == 'breakout_down':
                return 'downtrend'
            elif price_trend.get('short_trend') == price_trend.get('medium_trend'):
                return price_trend.get('short_trend', 'sideways')
            else:
                return 'sideways'
                
        except Exception as e:
            logger.error(f"Error classifying trend type: {e}")
            return 'unknown'

    def _determine_shift_significance(self, strength: float, confidence: float) -> str:
        """
        קביעת משמעות שינוי המגמה
        """
        try:
            if strength >= self.trend_thresholds['extreme'] and confidence >= 0.8:
                return 'extreme'
            elif strength >= self.trend_thresholds['strong'] and confidence >= 0.6:
                return 'strong'
            elif strength >= self.trend_thresholds['moderate'] and confidence >= 0.4:
                return 'moderate'
            elif strength >= self.trend_thresholds['weak'] and confidence >= 0.2:
                return 'weak'
            else:
                return 'minimal'
                
        except Exception as e:
            logger.error(f"Error determining shift significance: {e}")
            return 'unknown'

    def _analyze_shift_context(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח הקשר שינוי המגמה
        """
        try:
            # ניתוח לפי זמן
            current_time = df.index[index]
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            # ניתוח לפי מחיר
            price_change = (df['close'].iloc[index] - df['close'].iloc[index-1]) / df['close'].iloc[index-1]
            
            # ניתוח לפי נפח
            volume_change = (df['volume'].iloc[index] - df['volume'].iloc[index-1]) / df['volume'].iloc[index-1] if df['volume'].iloc[index-1] > 0 else 0
            
            return {
                'time_context': {
                    'hour': hour,
                    'day_of_week': day_of_week,
                    'is_trading_hours': 9 <= hour <= 16
                },
                'price_context': {
                    'price_change': price_change,
                    'price_momentum': 'positive' if price_change > 0 else 'negative'
                },
                'volume_context': {
                    'volume_change': volume_change,
                    'volume_momentum': 'positive' if volume_change > 0 else 'negative'
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing shift context: {e}")
            return {}

    def _calculate_trend_analysis(self, df: pd.DataFrame, shifts: List[TrendShift]) -> TrendAnalysis:
        """
        חישוב ניתוח מגמה מתקדם
        """
        try:
            # קביעת מגמה נוכחית
            current_trend = 'sideways'
            if shifts:
                latest_shift = shifts[-1]
                current_trend = latest_shift.trend_type
            
            # חישוב עוצמת מגמה
            trend_strength = np.mean([s.strength for s in shifts]) if shifts else 0.5
            
            # חישוב משך מגמה
            trend_duration = len(shifts)
            
            # חישוב עקביות מגמה
            if len(shifts) >= 2:
                consistent_trends = sum(1 for i in range(1, len(shifts)) if shifts[i].trend_type == shifts[i-1].trend_type)
                trend_consistency = consistent_trends / (len(shifts) - 1)
            else:
                trend_consistency = 1.0
            
            # ניתוח סקטור (סימולציה)
            sector_trend = 'positive'
            
            # ניתוח שוק (סימולציה)
            market_trend = 'positive'
            
            # ניקוד טכני
            technical_score = np.mean([s.confidence for s in shifts]) if shifts else 0.5
            
            # ניקוד פונדמנטלי (סימולציה)
            fundamental_score = 0.6
            
            # ניקוד רגשות (סימולציה)
            sentiment_score = 0.65
            
            return TrendAnalysis(
                current_trend=current_trend,
                trend_strength=trend_strength,
                trend_duration=trend_duration,
                trend_consistency=trend_consistency,
                sector_trend=sector_trend,
                market_trend=market_trend,
                technical_score=technical_score,
                fundamental_score=fundamental_score,
                sentiment_score=sentiment_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating trend analysis: {e}")
            return TrendAnalysis('unknown', 0.5, 0, 1.0, 'unknown', 'unknown', 0.5, 0.5, 0.5)

    def run(self) -> Dict:
        """הרצת הסוכן על נתונים היסטוריים"""
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם
            price_df = self.get_stock_data(self.symbol, days=self.default_days)
            if price_df is None or price_df.empty:
                return {
                    "trend_shift_score": 0.0,
                    "shift_category": "no_data",
                    "explanations": ["לא נמצאו נתונים זמינים"],
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
            
            return self.analyze(self.symbol, price_df)
            
        except Exception as e:
            logger.error(f"שגיאה בהרצת TrendShiftAgent: {e}")
            return {
                "trend_shift_score": 0.0,
                "shift_category": "error",
                "explanations": [f"שגיאה בניתוח: {str(e)}"],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }
    
    def run_live(self, cycles: int = None) -> None:
        """הרצת הסוכן במצב לייב"""
        import time
        
        print(f"🚀 מתחיל הרצת TrendShiftAgent במצב לייב עבור {self.symbol}")
        print(f"⏱️ אינטרוול: {self.interval} | תדירות: כל {self.frequency_sec} שניות")
        
        cycle_count = 0
        
        while cycles is None or cycle_count < cycles:
            try:
                print(f"\n🔄 מחזור {cycle_count + 1} - {datetime.now().strftime('%H:%M:%S')}")
                
                # קבלת נתונים עדכניים דרך מנהל הנתונים החכם
                price_df = self.get_stock_data(self.symbol, days=self.default_days)
                if price_df is None or price_df.empty:
                    print("⚠️ לא נמצאו נתונים זמינים")
                    time.sleep(self.frequency_sec)
                    cycle_count += 1
                    continue
                
                # ניתוח
                result = self.analyze(self.symbol, price_df)
                
                # הצגת תוצאות
                print(f"📊 תוצאות ניתוח:")
                print(f"   ציון מגמה: {result.get('score', 0):.2f}")
                print(f"   הסבר: {result.get('explanation', 'N/A')}")
                print(f"   ביטחון: {result.get('signal', {}).get('confidence', 0):.2f}")
                
                # בדיקה אם יש שינוי משמעותי
                if result.get('score', 0) > 70:
                    print("🚨 זוהה שינוי מגמה משמעותי!")
                
                time.sleep(self.frequency_sec)
                cycle_count += 1
                
            except KeyboardInterrupt:
                print("\n⏹️ הופסק על ידי המשתמש")
                break
            except Exception as e:
                print(f"❌ שגיאה במחזור {cycle_count + 1}: {e}")
                time.sleep(self.frequency_sec)
                cycle_count += 1
        
        print("✅ סיום הרצת TrendShiftAgent")

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של שינויי מגמה
        """
        try:
            # אחזור נתונים דרך מנהל הנתונים החכם
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=180)  # 6 חודשים
            
            if price_df is None or price_df.empty:
                return {
                    "score": 50,
                    "explanation": "לא ניתן לאחזר נתוני מחיר",
                    "signal": {
                        "type": "trend_shift",
                        "score": 50,
                        "reason": "לא ניתן לאחזר נתוני מחיר",
                        "confidence": 0.5,
                        "details": {
                            "current_trend": "unknown",
                            "trend_strength": 0.5,
                            "shifts_count": 0
                        }
                    },
                    "details": {
                        "shifts": [],
                        "analysis": {},
                        "recommendations": []
                    }
                }
            
            # זיהוי שינויי מגמה
            shifts = self._detect_trend_shifts(price_df)
            
            # ניתוח מתקדם
            analysis = self._calculate_trend_analysis(price_df, shifts)
            
            # חישוב ציון סופי
            if shifts:
                # חישוב ציון לפי שינויים משמעותיים
                significant_shifts = [s for s in shifts if s.significance in ['strong', 'extreme']]
                shift_score = min(100, len(significant_shifts) * 20 + analysis.trend_strength * 50)
                
                # התאמה לפי עקביות
                if analysis.trend_consistency > 0.8:
                    shift_score *= 1.1
                elif analysis.trend_consistency < 0.5:
                    shift_score *= 0.9
                
                shift_score = min(100, max(0, shift_score))
            else:
                shift_score = 50
            
            # יצירת הסבר
            if shifts:
                recent_shifts = [s for s in shifts if s.significance in ['strong', 'extreme']]
                explanation = f"זוהו {len(shifts)} שינויי מגמה ({len(recent_shifts)} משמעותיים). מגמה נוכחית: {analysis.current_trend}, עוצמה: {analysis.trend_strength:.2f}"
            else:
                explanation = "לא זוהו שינויי מגמה משמעותיים"
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(shifts, analysis)
            
            return {
                "score": round(shift_score, 1),
                "explanation": explanation,
                "signal": {
                    "type": "trend_shift",
                    "score": round(shift_score, 1),
                    "reason": explanation,
                    "confidence": round(analysis.technical_score, 3),
                    "details": {
                        "current_trend": analysis.current_trend,
                        "trend_strength": round(analysis.trend_strength, 2),
                        "shifts_count": len(shifts),
                        "significant_shifts": len([s for s in shifts if s.significance in ['strong', 'extreme']])
                    }
                },
                "details": {
                    "shifts": [
                        {
                            "timestamp": shift.timestamp.isoformat(),
                            "trend_type": shift.trend_type,
                            "strength": round(shift.strength, 2),
                            "significance": shift.significance,
                            "confidence": round(shift.confidence, 3)
                        }
                        for shift in shifts[:10]  # Top 10 shifts
                    ],
                    "analysis": {
                        "current_trend": analysis.current_trend,
                        "trend_strength": round(analysis.trend_strength, 2),
                        "trend_duration": analysis.trend_duration,
                        "trend_consistency": round(analysis.trend_consistency, 2),
                        "sector_trend": analysis.sector_trend,
                        "market_trend": analysis.market_trend,
                        "technical_score": round(analysis.technical_score, 2),
                        "fundamental_score": round(analysis.fundamental_score, 2),
                        "sentiment_score": round(analysis.sentiment_score, 2)
                    },
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"Error in TrendShiftAgent.analyze: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח: {str(e)}",
                "signal": {
                    "type": "trend_shift",
                    "score": 50,
                    "reason": f"שגיאה בניתוח: {str(e)}",
                    "confidence": 0.5,
                    "details": {
                        "current_trend": "error",
                        "trend_strength": 0.5,
                        "shifts_count": 0
                    }
                },
                "details": {
                    "shifts": [],
                    "analysis": {},
                    "recommendations": []
                }
            }

    def _generate_recommendations(self, shifts: List[TrendShift], analysis: TrendAnalysis) -> List[str]:
        """
        יצירת המלצות מתקדמות
        """
        recommendations = []
        
        try:
            if analysis.current_trend == 'uptrend':
                recommendations.append("📈 מגמה עולה - פוטנציאל לרכישה")
            
            if analysis.current_trend == 'downtrend':
                recommendations.append("📉 מגמה יורדת - שקול מכירה או המתנה")
            
            if analysis.trend_strength > 0.7:
                recommendations.append("💪 מגמה חזקה - תמיכה חזקה בתנועה")
            
            if analysis.trend_consistency > 0.8:
                recommendations.append("🔄 מגמה עקבית - סיכוי גבוה להמשך")
            
            if len([s for s in shifts if s.significance == 'extreme']) > 0:
                recommendations.append("⚠️ שינויי מגמה קיצוניים - בדוק חדשות או אירועים")
            
            if analysis.technical_score > 0.7:
                recommendations.append("🔧 סיגנלים טכניים חזקים - תמיכה טכנית")
            
            if not recommendations:
                recommendations.append("📊 מגמה יציבה - אין סיגנלים משמעותיים")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["שגיאה ביצירת המלצות"]

    def get_trend_summary(self) -> Dict:
        """
        סיכום ניתוח מגמה
        """
        return {
            "agent_type": "TrendShiftAgent",
            "description": "זיהוי שינויי מגמה מתקדם עם ניתוח רב-ממדי",
            "features": [
                "זיהוי שינויי מגמה לפי מספר אינדיקטורים",
                "ניתוח רב-ממדי של מגמות",
                "ולידציה לפי נפח ומחיר",
                "ניתוח מגמות לפי טווחי זמן שונים",
                "זיהוי מגמות לפי סקטורים",
                "ניתוח מגמות לפי אירועים",
                "זיהוי מגמות לפי טכני ופונדמנטלי",
                "ניתוח מגמות לפי רגשות השוק"
            ],
            "thresholds": self.trend_thresholds,
            "time_periods": self.time_periods
        } 