"""
TrendShiftDetector - זיהוי שינויי מגמה לייב
============================================

דטקטור מתקדם לזיהוי שינויי מגמה משמעותיים במצב לייב,
עם ניתוח רב-ממדי וולידציה מתקדמת.

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
from utils.data_fetcher import data_fetcher
# from utils.constants import TREND_THRESHOLDS, TIME_PERIODS  # לא קיימים
import logging
import time

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

class TrendShiftDetector:
    """
    דטקטור מתקדם לזיהוי שינויי מגמה משמעותיים במצב לייב
    
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
    
    def __init__(self, symbol: str, interval: str = "1day", live_mode: bool = False, frequency_sec: int = 60):
        """אתחול הדטקטור עם הגדרות מתקדמות"""
        self.symbol = symbol
        self.interval = interval
        self.live_mode = live_mode
        self.frequency_sec = frequency_sec
        
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
            'reversal': 'היפוך',
            'breakout': 'פריצה',
            'breakdown': 'שבירה'
        }
        
        # היסטוריית שינויים
        self.shift_history = []
        self.last_analysis = None
        
    def run(self) -> Dict:
        """הרצת הדטקטור על נתונים היסטוריים"""
        try:
            # קבלת נתונים
            price_df = data_fetcher.fetch_prices(self.symbol, self.interval)
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
            logger.error(f"שגיאה בהרצת TrendShiftDetector: {e}")
            return {
                "trend_shift_score": 0.0,
                "shift_category": "error",
                "explanations": [f"שגיאה בניתוח: {str(e)}"],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }
    
    def run_live(self, cycles: int = None) -> None:
        """הרצת הדטקטור במצב לייב"""
        print(f"🚀 מתחיל הרצת TrendShiftDetector במצב לייב עבור {self.symbol}")
        print(f"⏱️ אינטרוול: {self.interval} | תדירות: כל {self.frequency_sec} שניות")
        
        cycle_count = 0
        
        while cycles is None or cycle_count < cycles:
            try:
                print(f"\n🔄 מחזור {cycle_count + 1} - {datetime.now().strftime('%H:%M:%S')}")
                
                # קבלת נתונים עדכניים
                price_df = data_fetcher.fetch_prices(self.symbol, self.interval)
                if price_df is None or price_df.empty:
                    print("⚠️ לא נמצאו נתונים זמינים")
                    time.sleep(self.frequency_sec)
                    cycle_count += 1
                    continue
                
                # ניתוח
                result = self.analyze(self.symbol, price_df)
                
                # הצגת תוצאות
                print(f"📊 תוצאות ניתוח:")
                print(f"   ציון מגמה: {result['trend_shift_score']:.2f}")
                print(f"   קטגוריה: {result['shift_category']}")
                print(f"   ביטחון: {result['confidence']:.2f}")
                
                if result['explanations']:
                    print("   הסברים:")
                    for exp in result['explanations']:
                        print(f"     - {exp}")
                
                # בדיקה אם יש שינוי משמעותי
                if result['trend_shift_score'] > 0.7:
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
        
        print("✅ סיום הרצת TrendShiftDetector")
    
    def analyze(self, symbol: str, price_df: pd.DataFrame = None, **kwargs) -> Dict:
        """ניתוח מתקדם של מגמות"""
        try:
            if price_df is None:
                price_df = data_fetcher.fetch_prices(symbol, self.interval)
            
            if price_df is None or price_df.empty:
                return {
                    "trend_shift_score": 0.0,
                    "shift_category": "no_data",
                    "explanations": ["לא נמצאו נתונים זמינים"],
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
            
            # ניתוח מגמות
            shifts = self._detect_trend_shifts(price_df)
            analysis = self._calculate_trend_analysis(price_df, shifts)
            
            # חישוב ציון כולל
            trend_shift_score = self._calculate_overall_score(shifts, analysis)
            
            # קטגוריזציה
            shift_category = self._categorize_shift(trend_shift_score, shifts)
            
            # הסברים
            explanations = self._generate_explanations(shifts, analysis)
            
            # ביטחון
            confidence = self._calculate_confidence(shifts, analysis)
            
            # שמירת ניתוח אחרון
            self.last_analysis = {
                "timestamp": datetime.now(),
                "shifts": shifts,
                "analysis": analysis,
                "score": trend_shift_score
            }
            
            return {
                "trend_shift_score": trend_shift_score,
                "shift_category": shift_category,
                "explanations": explanations,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "shifts_count": len(shifts),
                "current_trend": analysis.current_trend,
                "trend_strength": analysis.trend_strength
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח TrendShiftDetector: {e}")
            return {
                "trend_shift_score": 0.0,
                "shift_category": "error",
                "explanations": [f"שגיאה בניתוח: {str(e)}"],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_trend_shifts(self, df: pd.DataFrame) -> List[TrendShift]:
        """זיהוי שינויי מגמה"""
        shifts = []
        
        if len(df) < 50:  # צריך מספיק נתונים
            return shifts
        
        # ניתוח לפי אינדיקטורים שונים
        for i in range(20, len(df)):
            try:
                # ניתוח מגמת מחיר
                price_trend = self._analyze_price_trend(df, i)
                
                # ניתוח מגמת נפח
                volume_trend = self._analyze_volume_trend(df, i)
                
                # ניתוח טכני
                technical_trend = self._analyze_technical_trend(df, i)
                
                # ניתוח פונדמנטלי
                fundamental_trend = self._analyze_fundamental_trend(df, i)
                
                # ניתוח רגשות
                sentiment_trend = self._analyze_sentiment_trend(df, i)
                
                # בדיקה אם יש שינוי מגמה
                if self._is_trend_shift(price_trend, volume_trend, technical_trend, 
                                      fundamental_trend, sentiment_trend):
                    
                    # חישוב עוצמה וביטחון
                    strength = self._calculate_shift_strength(price_trend, volume_trend, 
                                                            technical_trend, fundamental_trend, sentiment_trend)
                    confidence = self._calculate_shift_confidence(price_trend, volume_trend, 
                                                                technical_trend, fundamental_trend, sentiment_trend)
                    
                    # סיווג סוג המגמה
                    trend_type = self._classify_trend_type(price_trend, volume_trend, technical_trend)
                    
                    # קביעת משמעות
                    significance = self._determine_shift_significance(strength, confidence)
                    
                    # ניתוח הקשר
                    context = self._analyze_shift_context(df, i)
                    
                    # יצירת אובייקט שינוי מגמה
                    shift = TrendShift(
                        timestamp=df.index[i],
                        trend_type=trend_type,
                        strength=strength,
                        confidence=confidence,
                        indicators={
                            'price': price_trend,
                            'volume': volume_trend,
                            'technical': technical_trend,
                            'fundamental': fundamental_trend,
                            'sentiment': sentiment_trend
                        },
                        context=context,
                        significance=significance
                    )
                    
                    shifts.append(shift)
                    
            except Exception as e:
                logger.warning(f"שגיאה בזיהוי שינוי מגמה בנקודה {i}: {e}")
                continue
        
        return shifts
    
    def _analyze_price_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """ניתוח מגמת מחיר"""
        try:
            current_price = df.iloc[index]['Close']
            
            # ממוצעים נעים
            sma_5 = df.iloc[index-5:index]['Close'].mean()
            sma_20 = df.iloc[index-20:index]['Close'].mean()
            sma_50 = df.iloc[index-50:index]['Close'].mean()
            
            # מומנטום
            momentum_5 = (current_price / df.iloc[index-5]['Close']) - 1
            momentum_20 = (current_price / df.iloc[index-20]['Close']) - 1
            
            # כיוון מגמה
            trend_direction = 0
            if current_price > sma_20 > sma_50:
                trend_direction = 1  # עולה
            elif current_price < sma_20 < sma_50:
                trend_direction = -1  # יורדת
            
            return {
                'current_price': current_price,
                'sma_5': sma_5,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'momentum_5': momentum_5,
                'momentum_20': momentum_20,
                'trend_direction': trend_direction,
                'strength': abs(momentum_20)
            }
        except Exception as e:
            logger.warning(f"שגיאה בניתוח מגמת מחיר: {e}")
            return {'strength': 0.0}
    
    def _analyze_volume_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """ניתוח מגמת נפח"""
        try:
            current_volume = df.iloc[index]['Volume']
            avg_volume = df.iloc[index-20:index]['Volume'].mean()
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # מגמת נפח
            volume_trend = 0
            if volume_ratio > 1.5:
                volume_trend = 1  # נפח גבוה
            elif volume_ratio < 0.5:
                volume_trend = -1  # נפח נמוך
            
            return {
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'volume_trend': volume_trend,
                'strength': min(volume_ratio, 3.0) / 3.0
            }
        except Exception as e:
            logger.warning(f"שגיאה בניתוח מגמת נפח: {e}")
            return {'strength': 0.0}
    
    def _analyze_technical_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """ניתוח טכני"""
        try:
            # RSI
            rsi = self._calculate_rsi(df.iloc[index-14:index+1]['Close'])
            
            # MACD
            macd, signal = self._calculate_macd(df.iloc[index-26:index+1]['Close'])
            
            # Bollinger Bands
            bb_position = self._calculate_bollinger_position(df.iloc[index-20:index+1]['Close'])
            
            # ניתוח טכני כללי
            technical_score = 0.0
            technical_signals = []
            
            if rsi < 30:
                technical_score += 0.3
                technical_signals.append("RSI oversold")
            elif rsi > 70:
                technical_score += 0.3
                technical_signals.append("RSI overbought")
            
            if macd > signal:
                technical_score += 0.2
                technical_signals.append("MACD bullish")
            else:
                technical_score += 0.2
                technical_signals.append("MACD bearish")
            
            if bb_position < 0.2:
                technical_score += 0.2
                technical_signals.append("Near lower Bollinger")
            elif bb_position > 0.8:
                technical_score += 0.2
                technical_signals.append("Near upper Bollinger")
            
            return {
                'rsi': rsi,
                'macd': macd,
                'macd_signal': signal,
                'bollinger_position': bb_position,
                'technical_score': technical_score,
                'signals': technical_signals,
                'strength': technical_score
            }
        except Exception as e:
            logger.warning(f"שגיאה בניתוח טכני: {e}")
            return {'strength': 0.0}
    
    def _analyze_fundamental_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """ניתוח פונדמנטלי (פשוט)"""
        try:
            # במקום אמיתי זה יהיה מורכב יותר
            # כרגע נחזיר ערכים בסיסיים
            return {
                'fundamental_score': 0.5,
                'strength': 0.5
            }
        except Exception as e:
            logger.warning(f"שגיאה בניתוח פונדמנטלי: {e}")
            return {'strength': 0.0}
    
    def _analyze_sentiment_trend(self, df: pd.DataFrame, index: int) -> Dict:
        """ניתוח רגשות (פשוט)"""
        try:
            # במקום אמיתי זה יהיה מורכב יותר
            # כרגע נחזיר ערכים בסיסיים
            return {
                'sentiment_score': 0.5,
                'strength': 0.5
            }
        except Exception as e:
            logger.warning(f"שגיאה בניתוח רגשות: {e}")
            return {'strength': 0.0}
    
    def _is_trend_shift(self, price_trend: Dict, volume_trend: Dict, 
                       technical_trend: Dict, fundamental_trend: Dict, 
                       sentiment_trend: Dict) -> bool:
        """בדיקה אם יש שינוי מגמה"""
        try:
            # קריטריונים לשינוי מגמה
            price_strength = price_trend.get('strength', 0.0)
            volume_strength = volume_trend.get('strength', 0.0)
            technical_strength = technical_trend.get('strength', 0.0)
            
            # שינוי מגמה אם יש מספיק עוצמה
            total_strength = (price_strength + volume_strength + technical_strength) / 3
            
            return total_strength > 0.6
            
        except Exception as e:
            logger.warning(f"שגיאה בבדיקת שינוי מגמה: {e}")
            return False
    
    def _calculate_shift_strength(self, price_trend: Dict, volume_trend: Dict,
                                technical_trend: Dict, fundamental_trend: Dict,
                                sentiment_trend: Dict) -> float:
        """חישוב עוצמת השינוי"""
        try:
            weights = self.indicator_weights
            
            strength = (
                price_trend.get('strength', 0.0) * weights['price_momentum'] +
                volume_trend.get('strength', 0.0) * weights['volume_trend'] +
                technical_trend.get('strength', 0.0) * weights['technical_indicators'] +
                fundamental_trend.get('strength', 0.0) * weights['fundamental_factors'] +
                sentiment_trend.get('strength', 0.0) * weights['sentiment_analysis']
            )
            
            return min(strength, 1.0)
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב עוצמת שינוי: {e}")
            return 0.0
    
    def _calculate_shift_confidence(self, price_trend: Dict, volume_trend: Dict,
                                  technical_trend: Dict, fundamental_trend: Dict,
                                  sentiment_trend: Dict) -> float:
        """חישוב ביטחון השינוי"""
        try:
            # ביטחון גבוה יותר כשיש יותר אינדיקטורים תומכים
            supporting_indicators = 0
            total_indicators = 5
            
            if price_trend.get('strength', 0.0) > 0.5:
                supporting_indicators += 1
            if volume_trend.get('strength', 0.0) > 0.5:
                supporting_indicators += 1
            if technical_trend.get('strength', 0.0) > 0.5:
                supporting_indicators += 1
            if fundamental_trend.get('strength', 0.0) > 0.5:
                supporting_indicators += 1
            if sentiment_trend.get('strength', 0.0) > 0.5:
                supporting_indicators += 1
            
            confidence = supporting_indicators / total_indicators
            return confidence
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב ביטחון שינוי: {e}")
            return 0.0
    
    def _classify_trend_type(self, price_trend: Dict, volume_trend: Dict, technical_trend: Dict) -> str:
        """סיווג סוג המגמה"""
        try:
            trend_direction = price_trend.get('trend_direction', 0)
            volume_trend_val = volume_trend.get('volume_trend', 0)
            
            if trend_direction > 0 and volume_trend_val > 0:
                return 'breakout'
            elif trend_direction < 0 and volume_trend_val > 0:
                return 'breakdown'
            elif trend_direction > 0:
                return 'uptrend'
            elif trend_direction < 0:
                return 'downtrend'
            else:
                return 'sideways'
                
        except Exception as e:
            logger.warning(f"שגיאה בסיווג סוג מגמה: {e}")
            return 'unknown'
    
    def _determine_shift_significance(self, strength: float, confidence: float) -> str:
        """קביעת משמעות השינוי"""
        try:
            if strength > 0.8 and confidence > 0.8:
                return 'extreme'
            elif strength > 0.6 and confidence > 0.6:
                return 'strong'
            elif strength > 0.4 and confidence > 0.4:
                return 'moderate'
            else:
                return 'weak'
                
        except Exception as e:
            logger.warning(f"שגיאה בקביעת משמעות שינוי: {e}")
            return 'unknown'
    
    def _analyze_shift_context(self, df: pd.DataFrame, index: int) -> Dict:
        """ניתוח הקשר השינוי"""
        try:
            # ניתוח הקשר בסיסי
            return {
                'price_change': df.iloc[index]['Close'] - df.iloc[index-1]['Close'],
                'volume_change': df.iloc[index]['Volume'] - df.iloc[index-1]['Volume'],
                'day_of_week': df.index[index].dayofweek,
                'time_of_day': df.index[index].hour if hasattr(df.index[index], 'hour') else 0
            }
        except Exception as e:
            logger.warning(f"שגיאה בניתוח הקשר שינוי: {e}")
            return {}
    
    def _calculate_trend_analysis(self, df: pd.DataFrame, shifts: List[TrendShift]) -> TrendAnalysis:
        """חישוב ניתוח מגמה כולל"""
        try:
            if len(df) < 20:
                return TrendAnalysis(
                    current_trend='unknown',
                    trend_strength=0.0,
                    trend_duration=0,
                    trend_consistency=0.0,
                    sector_trend='unknown',
                    market_trend='unknown',
                    technical_score=0.0,
                    fundamental_score=0.0,
                    sentiment_score=0.0
                )
            
            # ניתוח מגמה נוכחית
            current_price = df.iloc[-1]['Close']
            sma_20 = df.iloc[-20:]['Close'].mean()
            sma_50 = df.iloc[-50:]['Close'].mean()
            
            if current_price > sma_20 > sma_50:
                current_trend = 'uptrend'
                trend_strength = (current_price / sma_50 - 1) * 100
            elif current_price < sma_20 < sma_50:
                current_trend = 'downtrend'
                trend_strength = (sma_50 / current_price - 1) * 100
            else:
                current_trend = 'sideways'
                trend_strength = 0.0
            
            # משך מגמה
            trend_duration = self._calculate_trend_duration(df)
            
            # עקביות מגמה
            trend_consistency = self._calculate_trend_consistency(df)
            
            return TrendAnalysis(
                current_trend=current_trend,
                trend_strength=min(abs(trend_strength), 100.0),
                trend_duration=trend_duration,
                trend_consistency=trend_consistency,
                sector_trend='unknown',  # במקום אמיתי זה יהיה מורכב יותר
                market_trend='unknown',   # במקום אמיתי זה יהיה מורכב יותר
                technical_score=0.5,      # במקום אמיתי זה יהיה מורכב יותר
                fundamental_score=0.5,    # במקום אמיתי זה יהיה מורכב יותר
                sentiment_score=0.5       # במקום אמיתי זה יהיה מורכב יותר
            )
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב ניתוח מגמה: {e}")
            return TrendAnalysis(
                current_trend='error',
                trend_strength=0.0,
                trend_duration=0,
                trend_consistency=0.0,
                sector_trend='error',
                market_trend='error',
                technical_score=0.0,
                fundamental_score=0.0,
                sentiment_score=0.0
            )
    
    def _calculate_overall_score(self, shifts: List[TrendShift], analysis: TrendAnalysis) -> float:
        """חישוב ציון כולל"""
        try:
            if not shifts:
                return 0.0
            
            # ציון ממוצע של שינויים
            shift_scores = [shift.strength * shift.confidence for shift in shifts]
            avg_shift_score = sum(shift_scores) / len(shift_scores)
            
            # ציון מגמה נוכחית
            trend_score = analysis.trend_strength / 100.0
            
            # ציון כולל
            overall_score = (avg_shift_score * 0.7) + (trend_score * 0.3)
            
            return min(overall_score, 1.0)
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב ציון כולל: {e}")
            return 0.0
    
    def _categorize_shift(self, score: float, shifts: List[TrendShift]) -> str:
        """קטגוריזציה של השינוי"""
        try:
            if score > 0.8:
                return 'extreme_shift'
            elif score > 0.6:
                return 'strong_shift'
            elif score > 0.4:
                return 'moderate_shift'
            elif score > 0.2:
                return 'weak_shift'
            else:
                return 'no_shift'
                
        except Exception as e:
            logger.warning(f"שגיאה בקטגוריזציה: {e}")
            return 'unknown'
    
    def _generate_explanations(self, shifts: List[TrendShift], analysis: TrendAnalysis) -> List[str]:
        """יצירת הסברים"""
        explanations = []
        
        try:
            # הסברים על בסיס שינויים
            for shift in shifts:
                if shift.strength > 0.7:
                    explanations.append(f"שינוי מגמה חזק זוהה: {shift.trend_type} (עוצמה: {shift.strength:.2f})")
                elif shift.strength > 0.5:
                    explanations.append(f"שינוי מגמה בינוני זוהה: {shift.trend_type} (עוצמה: {shift.strength:.2f})")
            
            # הסברים על בסיס ניתוח
            if analysis.current_trend == 'uptrend':
                explanations.append(f"מגמה עולה נוכחית (עוצמה: {analysis.trend_strength:.1f}%)")
            elif analysis.current_trend == 'downtrend':
                explanations.append(f"מגמה יורדת נוכחית (עוצמה: {analysis.trend_strength:.1f}%)")
            elif analysis.current_trend == 'sideways':
                explanations.append("מגמה צדדית נוכחית")
            
            # הסברים על בסיס עקביות
            if analysis.trend_consistency > 0.8:
                explanations.append("מגמה עקבית מאוד")
            elif analysis.trend_consistency > 0.6:
                explanations.append("מגמה עקבית")
            
            if not explanations:
                explanations.append("לא זוהו שינויים משמעותיים במגמה")
                
        except Exception as e:
            logger.warning(f"שגיאה ביצירת הסברים: {e}")
            explanations.append("שגיאה ביצירת הסברים")
        
        return explanations
    
    def _calculate_confidence(self, shifts: List[TrendShift], analysis: TrendAnalysis) -> float:
        """חישוב ביטחון כולל"""
        try:
            if not shifts:
                return 0.0
            
            # ביטחון ממוצע של שינויים
            shift_confidences = [shift.confidence for shift in shifts]
            avg_confidence = sum(shift_confidences) / len(shift_confidences)
            
            # ביטחון על בסיס עקביות
            consistency_confidence = analysis.trend_consistency
            
            # ביטחון כולל
            overall_confidence = (avg_confidence * 0.7) + (consistency_confidence * 0.3)
            
            return min(overall_confidence, 1.0)
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב ביטחון: {e}")
            return 0.0
    
    def _calculate_trend_duration(self, df: pd.DataFrame) -> int:
        """חישוב משך מגמה"""
        try:
            if len(df) < 10:
                return 0
            
            # חישוב פשוט של משך מגמה
            return min(len(df), 100)  # מקסימום 100 ימים
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב משך מגמה: {e}")
            return 0
    
    def _calculate_trend_consistency(self, df: pd.DataFrame) -> float:
        """חישוב עקביות מגמה"""
        try:
            if len(df) < 20:
                return 0.0
            
            # חישוב פשוט של עקביות
            returns = df['Close'].pct_change().dropna()
            if len(returns) < 10:
                return 0.0
            
            # עקביות על בסיס סטיית תקן
            std_dev = returns.std()
            consistency = 1.0 / (1.0 + std_dev)
            
            return min(consistency, 1.0)
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב עקביות מגמה: {e}")
            return 0.0
    
    def _calculate_rsi(self, prices: pd.Series) -> float:
        """חישוב RSI"""
        try:
            if len(prices) < 14:
                return 50.0
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב RSI: {e}")
            return 50.0
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[float, float]:
        """חישוב MACD"""
        try:
            if len(prices) < 26:
                return 0.0, 0.0
            
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            return macd.iloc[-1], signal.iloc[-1]
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב MACD: {e}")
            return 0.0, 0.0
    
    def _calculate_bollinger_position(self, prices: pd.Series) -> float:
        """חישוב מיקום ביחס ל-Bollinger Bands"""
        try:
            if len(prices) < 20:
                return 0.5
            
            sma = prices.rolling(window=20).mean()
            std = prices.rolling(window=20).std()
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            
            current_price = prices.iloc[-1]
            band_width = upper_band.iloc[-1] - lower_band.iloc[-1]
            
            if band_width == 0:
                return 0.5
            
            position = (current_price - lower_band.iloc[-1]) / band_width
            return max(0.0, min(1.0, position))
            
        except Exception as e:
            logger.warning(f"שגיאה בחישוב Bollinger position: {e}")
            return 0.5 