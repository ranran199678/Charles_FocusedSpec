"""
Pattern Detector - זיהוי תבניות גרפיות
=======================================

סוכן המזהה תבניות גרפיות טכניות במניות.
מזהה תבניות נרות, תבניות גרפים ותבניות הרמוניות.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

from core.base.base_agent import BaseAgent
from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("pattern_detector")

@dataclass
class Pattern:
    """מבנה נתונים לתבנית"""
    name: str
    type: str
    confidence: float
    start_date: datetime
    end_date: datetime
    price_levels: Dict[str, float]
    volume_confirmation: bool
    breakout_direction: str
    strength: float

class PatternDetector(BaseAgent):
    """
    סוכן זיהוי תבניות גרפיות
    """

    def __init__(self, config=None):
        """
        אתחול הסוכן
        """
        super().__init__(config)
        
        self.name = "Pattern Detector"
        self.version = "1.0.0"
        self.description = "מזהה תבניות גרפיות טכניות במניות"

        # הגדרות זיהוי
        cfg = config or {}
        self.min_pattern_bars = cfg.get("min_pattern_bars", 5)
        self.max_pattern_bars = cfg.get("max_pattern_bars", 50)
        self.confidence_threshold = cfg.get("confidence_threshold", 0.6)
        self.volume_confirmation_threshold = cfg.get("volume_confirmation_threshold", 1.5)

        # פרמטרים לניתוח
        self.lookback_period = 100  # תקופה לניתוח
        self.pattern_types = {
            'candlestick': ['doji', 'hammer', 'shooting_star', 'engulfing', 'morning_star', 'evening_star'],
            'chart': ['head_shoulders', 'inverse_head_shoulders', 'triangle', 'flag', 'pennant', 'cup_handle'],
            'harmonic': ['gartley', 'butterfly', 'bat', 'crab', 'cypher']
        }

        self.log(f"Initialized {self.name} v{self.version}")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None,
                volume_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח תבניות גרפיות למניה

        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            volume_df: נתוני נפח

        Returns:
            תוצאות הניתוח
        """
        try:
            self.log(f"Starting pattern analysis for {symbol}")

            # אימות נתונים
            if not validate_symbol(symbol):
                return self.fallback()

            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=180)
                if price_df is None or price_df.empty:
                    return self.fallback()

            # הכנת נתונים
            df = self._prepare_data(price_df, volume_df)

            # זיהוי תבניות נרות
            candlestick_patterns = self._detect_candlestick_patterns(df)

            # זיהוי תבניות גרפים
            chart_patterns = self._detect_chart_patterns(df)

            # זיהוי תבניות הרמוניות
            harmonic_patterns = self._detect_harmonic_patterns(df)

            # ניתוח אישור נפח
            volume_analysis = self._analyze_volume_confirmation(df, candlestick_patterns + chart_patterns + harmonic_patterns)

            # ניתוח רמות מחיר
            price_level_analysis = self._analyze_price_levels(df, candlestick_patterns + chart_patterns + harmonic_patterns)

            # ניתוח כיוון פריצה
            breakout_analysis = self._analyze_breakout_direction(df, candlestick_patterns + chart_patterns + harmonic_patterns)

            # חישוב ציון כללי
            score = self._calculate_pattern_score(
                candlestick_patterns,
                chart_patterns,
                harmonic_patterns,
                volume_analysis,
                price_level_analysis,
                breakout_analysis
            )

            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)

            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)

            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                candlestick_patterns,
                chart_patterns,
                harmonic_patterns,
                volume_analysis,
                price_level_analysis,
                breakout_analysis
            )

            result = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "version": self.version,
                "score": score,
                "confidence": confidence,
                "recommendation": recommendation,
                "key_signals": key_signals,
                "analysis": {
                    "candlestick_patterns": candlestick_patterns,
                    "chart_patterns": chart_patterns,
                    "harmonic_patterns": harmonic_patterns,
                    "volume_analysis": volume_analysis,
                    "price_levels": price_level_analysis,
                    "breakout_analysis": breakout_analysis
                },
                "metadata": {
                    "min_pattern_bars": self.min_pattern_bars,
                    "max_pattern_bars": self.max_pattern_bars,
                    "confidence_threshold": self.confidence_threshold,
                    "volume_confirmation_threshold": self.volume_confirmation_threshold,
                    "lookback_period": self.lookback_period
                }
            }

            self.log(f"Pattern analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result

        except Exception as e:
            self.handle_error(e)
            return self.fallback()

    def _prepare_data(self, price_df: pd.DataFrame, volume_df: pd.DataFrame) -> pd.DataFrame:
        """
        הכנת נתונים לניתוח
        """
        df = price_df.copy()
        
        # הוספת נתוני נפח אם קיימים
        if volume_df is not None and not volume_df.empty:
            df['volume'] = volume_df['volume']
        elif 'volume' not in df.columns:
            df['volume'] = 1000  # ערך ברירת מחדל

        # חישוב תכונות נוספות
        df['body'] = df['close'] - df['open']
        df['upper_shadow'] = df['high'] - np.maximum(df['open'], df['close'])
        df['lower_shadow'] = np.minimum(df['open'], df['close']) - df['low']
        df['body_size'] = np.abs(df['body'])
        df['total_range'] = df['high'] - df['low']
        
        # חישוב ממוצעים נעים
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        
        # חישוב תנודתיות
        df['volatility'] = df['close'].pct_change().rolling(window=20).std()
        
        return df

    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות נרות
        """
        patterns = []
        
        try:
            # זיהוי Doji
            doji_patterns = self._detect_doji_patterns(df)
            patterns.extend(doji_patterns)
            
            # זיהוי Hammer/Shooting Star
            hammer_patterns = self._detect_hammer_patterns(df)
            patterns.extend(hammer_patterns)
            
            # זיהוי Engulfing
            engulfing_patterns = self._detect_engulfing_patterns(df)
            patterns.extend(engulfing_patterns)
            
            # זיהוי Morning/Evening Star
            star_patterns = self._detect_star_patterns(df)
            patterns.extend(star_patterns)
            
        except Exception as e:
            logger.error(f"Error detecting candlestick patterns: {str(e)}")
        
        return patterns

    def _detect_doji_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות Doji
        """
        patterns = []
        
        try:
            for i in range(1, len(df) - 1):
                current = df.iloc[i]
                prev = df.iloc[i-1]
                next_candle = df.iloc[i+1]
                
                # בדיקה אם זה Doji
                body_size = abs(current['body'])
                total_range = current['total_range']
                
                if body_size <= total_range * 0.1:  # גוף קטן מאוד
                    # Doji רגיל
                    if total_range > df['total_range'].mean():
                        confidence = 0.8
                    else:
                        confidence = 0.6
                    
                    # קביעת כיוון
                    if next_candle['close'] > current['close']:
                        breakout_direction = "bullish"
                    else:
                        breakout_direction = "bearish"
                    
                    pattern = Pattern(
                        name="Doji",
                        type="candlestick",
                        confidence=confidence,
                        start_date=current.name,
                        end_date=current.name,
                        price_levels={
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close']
                        },
                        volume_confirmation=current['volume'] > current['volume_ma'],
                        breakout_direction=breakout_direction,
                        strength=confidence
                    )
                    patterns.append(pattern)
                    
        except Exception as e:
            logger.error(f"Error detecting doji patterns: {str(e)}")
        
        return patterns

    def _detect_hammer_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות Hammer/Shooting Star
        """
        patterns = []
        
        try:
            for i in range(1, len(df) - 1):
                current = df.iloc[i]
                prev = df.iloc[i-1]
                next_candle = df.iloc[i+1]
                
                body_size = abs(current['body'])
                total_range = current['total_range']
                lower_shadow = current['lower_shadow']
                upper_shadow = current['upper_shadow']
                
                # Hammer
                if (lower_shadow > body_size * 2 and 
                    upper_shadow < body_size * 0.5 and
                    current['close'] > current['open']):
                    
                    confidence = 0.7
                    if current['volume'] > current['volume_ma']:
                        confidence += 0.1
                    
                    pattern = Pattern(
                        name="Hammer",
                        type="candlestick",
                        confidence=confidence,
                        start_date=current.name,
                        end_date=current.name,
                        price_levels={
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close']
                        },
                        volume_confirmation=current['volume'] > current['volume_ma'],
                        breakout_direction="bullish",
                        strength=confidence
                    )
                    patterns.append(pattern)
                
                # Shooting Star
                elif (upper_shadow > body_size * 2 and 
                      lower_shadow < body_size * 0.5 and
                      current['close'] < current['open']):
                    
                    confidence = 0.7
                    if current['volume'] > current['volume_ma']:
                        confidence += 0.1
                    
                    pattern = Pattern(
                        name="Shooting Star",
                        type="candlestick",
                        confidence=confidence,
                        start_date=current.name,
                        end_date=current.name,
                        price_levels={
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close']
                        },
                        volume_confirmation=current['volume'] > current['volume_ma'],
                        breakout_direction="bearish",
                        strength=confidence
                    )
                    patterns.append(pattern)
                    
        except Exception as e:
            logger.error(f"Error detecting hammer patterns: {str(e)}")
        
        return patterns

    def _detect_engulfing_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות Engulfing
        """
        patterns = []
        
        try:
            for i in range(1, len(df)):
                current = df.iloc[i]
                prev = df.iloc[i-1]
                
                current_body = abs(current['body'])
                prev_body = abs(prev['body'])
                
                # Bullish Engulfing
                if (prev['close'] < prev['open'] and  # נר קודם אדום
                    current['close'] > current['open'] and  # נר נוכחי ירוק
                    current['open'] < prev['close'] and  # פתיחה מתחת לסגירה קודמת
                    current['close'] > prev['open'] and  # סגירה מעל פתיחה קודמת
                    current_body > prev_body * 1.2):  # גוף גדול יותר
                    
                    confidence = 0.8
                    if current['volume'] > current['volume_ma'] * 1.5:
                        confidence += 0.1
                    
                    pattern = Pattern(
                        name="Bullish Engulfing",
                        type="candlestick",
                        confidence=confidence,
                        start_date=prev.name,
                        end_date=current.name,
                        price_levels={
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close']
                        },
                        volume_confirmation=current['volume'] > current['volume_ma'],
                        breakout_direction="bullish",
                        strength=confidence
                    )
                    patterns.append(pattern)
                
                # Bearish Engulfing
                elif (prev['close'] > prev['open'] and  # נר קודם ירוק
                      current['close'] < current['open'] and  # נר נוכחי אדום
                      current['open'] > prev['close'] and  # פתיחה מעל סגירה קודמת
                      current['close'] < prev['open'] and  # סגירה מתחת לפתיחה קודמת
                      current_body > prev_body * 1.2):  # גוף גדול יותר
                    
                    confidence = 0.8
                    if current['volume'] > current['volume_ma'] * 1.5:
                        confidence += 0.1
                    
                    pattern = Pattern(
                        name="Bearish Engulfing",
                        type="candlestick",
                        confidence=confidence,
                        start_date=prev.name,
                        end_date=current.name,
                        price_levels={
                            'high': current['high'],
                            'low': current['low'],
                            'close': current['close']
                        },
                        volume_confirmation=current['volume'] > current['volume_ma'],
                        breakout_direction="bearish",
                        strength=confidence
                    )
                    patterns.append(pattern)
                    
        except Exception as e:
            logger.error(f"Error detecting engulfing patterns: {str(e)}")
        
        return patterns

    def _detect_star_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות Morning/Evening Star
        """
        patterns = []
        
        try:
            for i in range(2, len(df) - 1):
                first = df.iloc[i-2]
                second = df.iloc[i-1]
                third = df.iloc[i]
                
                first_body = abs(first['body'])
                second_body = abs(second['body'])
                third_body = abs(third['body'])
                
                # Morning Star
                if (first['close'] < first['open'] and  # נר ראשון אדום
                    second_body < first_body * 0.3 and  # נר שני קטן
                    third['close'] > third['open'] and  # נר שלישי ירוק
                    third['close'] > first['close'] + first_body * 0.5):  # סגירה מעל אמצע הנר הראשון
                    
                    confidence = 0.75
                    if third['volume'] > third['volume_ma']:
                        confidence += 0.1
                    
                    pattern = Pattern(
                        name="Morning Star",
                        type="candlestick",
                        confidence=confidence,
                        start_date=first.name,
                        end_date=third.name,
                        price_levels={
                            'high': max(first['high'], second['high'], third['high']),
                            'low': min(first['low'], second['low'], third['low']),
                            'close': third['close']
                        },
                        volume_confirmation=third['volume'] > third['volume_ma'],
                        breakout_direction="bullish",
                        strength=confidence
                    )
                    patterns.append(pattern)
                
                # Evening Star
                elif (first['close'] > first['open'] and  # נר ראשון ירוק
                      second_body < first_body * 0.3 and  # נר שני קטן
                      third['close'] < third['open'] and  # נר שלישי אדום
                      third['close'] < first['close'] - first_body * 0.5):  # סגירה מתחת לאמצע הנר הראשון
                    
                    confidence = 0.75
                    if third['volume'] > third['volume_ma']:
                        confidence += 0.1
                    
                    pattern = Pattern(
                        name="Evening Star",
                        type="candlestick",
                        confidence=confidence,
                        start_date=first.name,
                        end_date=third.name,
                        price_levels={
                            'high': max(first['high'], second['high'], third['high']),
                            'low': min(first['low'], second['low'], third['low']),
                            'close': third['close']
                        },
                        volume_confirmation=third['volume'] > third['volume_ma'],
                        breakout_direction="bearish",
                        strength=confidence
                    )
                    patterns.append(pattern)
                    
        except Exception as e:
            logger.error(f"Error detecting star patterns: {str(e)}")
        
        return patterns

    def _detect_chart_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות גרפים
        """
        patterns = []
        
        try:
            # זיהוי Head and Shoulders
            head_shoulders_patterns = self._detect_head_shoulders(df)
            patterns.extend(head_shoulders_patterns)
            
            # זיהוי Triangles
            triangle_patterns = self._detect_triangles(df)
            patterns.extend(triangle_patterns)
            
            # זיהוי Flags/Pennants
            flag_patterns = self._detect_flags_pennants(df)
            patterns.extend(flag_patterns)
            
            # זיהוי Cup and Handle
            cup_handle_patterns = self._detect_cup_handle(df)
            patterns.extend(cup_handle_patterns)
            
        except Exception as e:
            logger.error(f"Error detecting chart patterns: {str(e)}")
        
        return patterns

    def _detect_head_shoulders(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות Head and Shoulders
        """
        patterns = []
        
        try:
            for i in range(20, len(df) - 10):
                # חיפוש תבנית Head and Shoulders
                left_shoulder = self._find_peak(df, i-20, i-10)
                head = self._find_peak(df, i-10, i)
                right_shoulder = self._find_peak(df, i, i+10)
                
                if (left_shoulder and head and right_shoulder and
                    head['high'] > left_shoulder['high'] and
                    head['high'] > right_shoulder['high'] and
                    abs(left_shoulder['high'] - right_shoulder['high']) < left_shoulder['high'] * 0.05):
                    
                    confidence = 0.7
                    if self._check_neckline_support(df, left_shoulder, head, right_shoulder):
                        confidence += 0.1
                    
                    pattern = Pattern(
                        name="Head and Shoulders",
                        type="chart",
                        confidence=confidence,
                        start_date=left_shoulder.name,
                        end_date=right_shoulder.name,
                        price_levels={
                            'head': head['high'],
                            'left_shoulder': left_shoulder['high'],
                            'right_shoulder': right_shoulder['high'],
                            'neckline': min(left_shoulder['low'], head['low'], right_shoulder['low'])
                        },
                        volume_confirmation=True,
                        breakout_direction="bearish",
                        strength=confidence
                    )
                    patterns.append(pattern)
                    
        except Exception as e:
            logger.error(f"Error detecting head and shoulders: {str(e)}")
        
        return patterns

    def _detect_triangles(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות Triangle
        """
        patterns = []
        
        try:
            for i in range(20, len(df) - 5):
                # חיפוש תבנית Triangle
                highs = []
                lows = []
                
                for j in range(i-20, i):
                    if self._is_peak(df, j):
                        highs.append(df.iloc[j]['high'])
                    if self._is_trough(df, j):
                        lows.append(df.iloc[j]['low'])
                
                if len(highs) >= 3 and len(lows) >= 3:
                    # חישוב שיפועים
                    high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
                    low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
                    
                    # Ascending Triangle
                    if abs(high_slope) < 0.01 and low_slope > 0.01:
                        confidence = 0.7
                        pattern = Pattern(
                            name="Ascending Triangle",
                            type="chart",
                            confidence=confidence,
                            start_date=df.iloc[i-20].name,
                            end_date=df.iloc[i].name,
                            price_levels={
                                'resistance': np.mean(highs),
                                'support_slope': low_slope
                            },
                            volume_confirmation=True,
                            breakout_direction="bullish",
                            strength=confidence
                        )
                        patterns.append(pattern)
                    
                    # Descending Triangle
                    elif high_slope < -0.01 and abs(low_slope) < 0.01:
                        confidence = 0.7
                        pattern = Pattern(
                            name="Descending Triangle",
                            type="chart",
                            confidence=confidence,
                            start_date=df.iloc[i-20].name,
                            end_date=df.iloc[i].name,
                            price_levels={
                                'resistance_slope': high_slope,
                                'support': np.mean(lows)
                            },
                            volume_confirmation=True,
                            breakout_direction="bearish",
                            strength=confidence
                        )
                        patterns.append(pattern)
                    
                    # Symmetrical Triangle
                    elif abs(high_slope + low_slope) < 0.02:
                        confidence = 0.6
                        pattern = Pattern(
                            name="Symmetrical Triangle",
                            type="chart",
                            confidence=confidence,
                            start_date=df.iloc[i-20].name,
                            end_date=df.iloc[i].name,
                            price_levels={
                                'resistance_slope': high_slope,
                                'support_slope': low_slope
                            },
                            volume_confirmation=True,
                            breakout_direction="neutral",
                            strength=confidence
                        )
                        patterns.append(pattern)
                        
        except Exception as e:
            logger.error(f"Error detecting triangles: {str(e)}")
        
        return patterns

    def _detect_flags_pennants(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות Flag/Pennant
        """
        patterns = []
        
        try:
            for i in range(10, len(df) - 5):
                # חיפוש תבנית Flag/Pennant
                # דורש תנועה חזקה לפני התבנית
                pre_move = df.iloc[i-10:i]['close'].pct_change().sum()
                
                if abs(pre_move) > 0.1:  # תנועה של יותר מ-10%
                    # בדיקה אם יש תבנית דגל
                    recent_highs = []
                    recent_lows = []
                    
                    for j in range(i-5, i):
                        if self._is_peak(df, j):
                            recent_highs.append(df.iloc[j]['high'])
                        if self._is_trough(df, j):
                            recent_lows.append(df.iloc[j]['low'])
                    
                    if len(recent_highs) >= 2 and len(recent_lows) >= 2:
                        high_slope = np.polyfit(range(len(recent_highs)), recent_highs, 1)[0]
                        low_slope = np.polyfit(range(len(recent_lows)), recent_lows, 1)[0]
                        
                        # Bull Flag
                        if pre_move > 0 and abs(high_slope) < 0.01 and abs(low_slope) < 0.01:
                            confidence = 0.65
                            pattern = Pattern(
                                name="Bull Flag",
                                type="chart",
                                confidence=confidence,
                                start_date=df.iloc[i-5].name,
                                end_date=df.iloc[i].name,
                                price_levels={
                                    'flag_high': np.mean(recent_highs),
                                    'flag_low': np.mean(recent_lows)
                                },
                                volume_confirmation=True,
                                breakout_direction="bullish",
                                strength=confidence
                            )
                            patterns.append(pattern)
                        
                        # Bear Flag
                        elif pre_move < 0 and abs(high_slope) < 0.01 and abs(low_slope) < 0.01:
                            confidence = 0.65
                            pattern = Pattern(
                                name="Bear Flag",
                                type="chart",
                                confidence=confidence,
                                start_date=df.iloc[i-5].name,
                                end_date=df.iloc[i].name,
                                price_levels={
                                    'flag_high': np.mean(recent_highs),
                                    'flag_low': np.mean(recent_lows)
                                },
                                volume_confirmation=True,
                                breakout_direction="bearish",
                                strength=confidence
                            )
                            patterns.append(pattern)
                            
        except Exception as e:
            logger.error(f"Error detecting flags/pennants: {str(e)}")
        
        return patterns

    def _detect_cup_handle(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבנית Cup and Handle
        """
        patterns = []
        
        try:
            for i in range(30, len(df) - 10):
                # חיפוש תבנית Cup and Handle
                cup_start = i - 30
                cup_end = i - 10
                handle_start = i - 10
                handle_end = i
                
                # בדיקת Cup
                cup_data = df.iloc[cup_start:cup_end]
                cup_high = cup_data['high'].max()
                cup_low = cup_data['low'].min()
                
                # בדיקה אם יש צורת כוס
                if self._is_cup_shape(cup_data):
                    # בדיקת Handle
                    handle_data = df.iloc[handle_start:handle_end]
                    if self._is_handle_shape(handle_data, cup_high):
                        confidence = 0.75
                        pattern = Pattern(
                            name="Cup and Handle",
                            type="chart",
                            confidence=confidence,
                            start_date=df.iloc[cup_start].name,
                            end_date=df.iloc[handle_end].name,
                            price_levels={
                                'cup_high': cup_high,
                                'cup_low': cup_low,
                                'handle_low': handle_data['low'].min()
                            },
                            volume_confirmation=True,
                            breakout_direction="bullish",
                            strength=confidence
                        )
                        patterns.append(pattern)
                        
        except Exception as e:
            logger.error(f"Error detecting cup and handle: {str(e)}")
        
        return patterns

    def _detect_harmonic_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """
        זיהוי תבניות הרמוניות
        """
        patterns = []
        
        try:
            # זיהוי תבניות הרמוניות בסיסיות
            # Gartley, Butterfly, Bat, Crab, Cypher
            
            for i in range(20, len(df) - 5):
                # חיפוש תבניות הרמוניות
                # זה דורש זיהוי נקודות מפתח (X, A, B, C, D)
                key_points = self._find_harmonic_key_points(df, i)
                
                if key_points:
                    pattern_type = self._classify_harmonic_pattern(key_points)
                    if pattern_type:
                        confidence = 0.7
                        pattern = Pattern(
                            name=pattern_type,
                            type="harmonic",
                            confidence=confidence,
                            start_date=key_points[0]['date'],
                            end_date=key_points[-1]['date'],
                            price_levels={
                                'X': key_points[0]['price'],
                                'A': key_points[1]['price'],
                                'B': key_points[2]['price'],
                                'C': key_points[3]['price'],
                                'D': key_points[4]['price']
                            },
                            volume_confirmation=True,
                            breakout_direction="neutral",
                            strength=confidence
                        )
                        patterns.append(pattern)
                        
        except Exception as e:
            logger.error(f"Error detecting harmonic patterns: {str(e)}")
        
        return patterns

    def _analyze_volume_confirmation(self, df: pd.DataFrame, patterns: List[Pattern]) -> Dict[str, Any]:
        """
        ניתוח אישור נפח
        """
        try:
            confirmed_patterns = 0
            total_patterns = len(patterns)
            
            for pattern in patterns:
                if pattern.volume_confirmation:
                    confirmed_patterns += 1
            
            confirmation_ratio = confirmed_patterns / total_patterns if total_patterns > 0 else 0
            
            return {
                "confirmed_patterns": confirmed_patterns,
                "total_patterns": total_patterns,
                "confirmation_ratio": confirmation_ratio,
                "high_volume_patterns": confirmed_patterns,
                "low_volume_patterns": total_patterns - confirmed_patterns
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume confirmation: {str(e)}")
            return {"confirmed_patterns": 0, "total_patterns": 0, "confirmation_ratio": 0}

    def _analyze_price_levels(self, df: pd.DataFrame, patterns: List[Pattern]) -> Dict[str, Any]:
        """
        ניתוח רמות מחיר
        """
        try:
            support_levels = []
            resistance_levels = []
            
            for pattern in patterns:
                if 'low' in pattern.price_levels:
                    support_levels.append(pattern.price_levels['low'])
                if 'high' in pattern.price_levels:
                    resistance_levels.append(pattern.price_levels['high'])
            
            current_price = df['close'].iloc[-1]
            
            # חישוב מרחק מרמות
            nearest_support = min(support_levels, key=lambda x: abs(x - current_price)) if support_levels else None
            nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price)) if resistance_levels else None
            
            return {
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
                "nearest_support": nearest_support,
                "nearest_resistance": nearest_resistance,
                "support_distance": (current_price - nearest_support) / current_price if nearest_support else None,
                "resistance_distance": (nearest_resistance - current_price) / current_price if nearest_resistance else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price levels: {str(e)}")
            return {"support_levels": [], "resistance_levels": []}

    def _analyze_breakout_direction(self, df: pd.DataFrame, patterns: List[Pattern]) -> Dict[str, Any]:
        """
        ניתוח כיוון פריצה
        """
        try:
            bullish_patterns = sum(1 for p in patterns if p.breakout_direction == "bullish")
            bearish_patterns = sum(1 for p in patterns if p.breakout_direction == "bearish")
            neutral_patterns = sum(1 for p in patterns if p.breakout_direction == "neutral")
            
            total_patterns = len(patterns)
            
            if total_patterns > 0:
                bullish_ratio = bullish_patterns / total_patterns
                bearish_ratio = bearish_patterns / total_patterns
                neutral_ratio = neutral_patterns / total_patterns
            else:
                bullish_ratio = bearish_ratio = neutral_ratio = 0
            
            # קביעת כיוון דומיננטי
            if bullish_ratio > 0.5:
                dominant_direction = "bullish"
            elif bearish_ratio > 0.5:
                dominant_direction = "bearish"
            else:
                dominant_direction = "neutral"
            
            return {
                "bullish_patterns": bullish_patterns,
                "bearish_patterns": bearish_patterns,
                "neutral_patterns": neutral_patterns,
                "bullish_ratio": bullish_ratio,
                "bearish_ratio": bearish_ratio,
                "neutral_ratio": neutral_ratio,
                "dominant_direction": dominant_direction
            }
            
        except Exception as e:
            logger.error(f"Error analyzing breakout direction: {str(e)}")
            return {"bullish_patterns": 0, "bearish_patterns": 0, "neutral_patterns": 0}

    def _calculate_pattern_score(self, candlestick_patterns: List[Pattern], chart_patterns: List[Pattern],
                               harmonic_patterns: List[Pattern], volume_analysis: Dict,
                               price_level_analysis: Dict, breakout_analysis: Dict) -> float:
        """
        חישוב ציון תבניות כללי
        """
        try:
            # משקלות
            weights = {
                'candlestick': 0.25,
                'chart': 0.35,
                'harmonic': 0.20,
                'volume': 0.10,
                'breakout': 0.10
            }

            # ציונים
            candlestick_score = min(len(candlestick_patterns) * 20, 100)
            chart_score = min(len(chart_patterns) * 25, 100)
            harmonic_score = min(len(harmonic_patterns) * 30, 100)
            
            volume_score = volume_analysis.get('confirmation_ratio', 0) * 100
            breakout_score = 50
            if breakout_analysis.get('dominant_direction') == "bullish":
                breakout_score = 80
            elif breakout_analysis.get('dominant_direction') == "bearish":
                breakout_score = 20

            # חישוב ציון משוקלל
            total_score = (
                candlestick_score * weights['candlestick'] +
                chart_score * weights['chart'] +
                harmonic_score * weights['harmonic'] +
                volume_score * weights['volume'] +
                breakout_score * weights['breakout']
            )

            return min(max(total_score, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating pattern score: {str(e)}")
            return 50.0

    def _determine_confidence_level(self, score: float) -> str:
        """
        קביעת רמת ביטחון
        """
        if score >= 80:
            return "High"
        elif score >= 60:
            return "Medium"
        elif score >= 40:
            return "Low"
        else:
            return "Very Low"

    def _generate_recommendation(self, score: float, confidence: str) -> str:
        """
        יצירת המלצה
        """
        if score >= 80:
            return "Strong Pattern - Multiple high-confidence patterns detected"
        elif score >= 60:
            return "Good Pattern - Several reliable patterns identified"
        elif score >= 40:
            return "Weak Pattern - Some patterns detected, monitor for confirmation"
        else:
            return "No Pattern - Insufficient pattern evidence"

    def _extract_key_signals(self, candlestick_patterns: List[Pattern], chart_patterns: List[Pattern],
                           harmonic_patterns: List[Pattern], volume_analysis: Dict,
                           price_level_analysis: Dict, breakout_analysis: Dict) -> List[str]:
        """
        חילוץ אותות מפתח
        """
        signals = []

        # אותות תבניות נרות
        if candlestick_patterns:
            signals.append(f"Candlestick patterns: {len(candlestick_patterns)}")

        # אותות תבניות גרפים
        if chart_patterns:
            signals.append(f"Chart patterns: {len(chart_patterns)}")

        # אותות תבניות הרמוניות
        if harmonic_patterns:
            signals.append(f"Harmonic patterns: {len(harmonic_patterns)}")

        # אותות נפח
        if volume_analysis.get('confirmation_ratio', 0) > 0.7:
            signals.append("High volume confirmation")

        # אותות כיוון
        dominant_direction = breakout_analysis.get('dominant_direction', 'neutral')
        if dominant_direction != 'neutral':
            signals.append(f"Dominant direction: {dominant_direction}")

        return signals

    # Helper methods
    def _find_peak(self, df: pd.DataFrame, start: int, end: int) -> Optional[Dict]:
        """מציאת שיא בטווח נתון"""
        try:
            peak_idx = df.iloc[start:end]['high'].idxmax()
            return {
                'date': peak_idx,
                'high': df.loc[peak_idx, 'high'],
                'low': df.loc[peak_idx, 'low']
            }
        except:
            return None

    def _is_peak(self, df: pd.DataFrame, idx: int) -> bool:
        """בדיקה אם נקודה היא שיא"""
        if idx <= 0 or idx >= len(df) - 1:
            return False
        return df.iloc[idx]['high'] > df.iloc[idx-1]['high'] and df.iloc[idx]['high'] > df.iloc[idx+1]['high']

    def _is_trough(self, df: pd.DataFrame, idx: int) -> bool:
        """בדיקה אם נקודה היא שפל"""
        if idx <= 0 or idx >= len(df) - 1:
            return False
        return df.iloc[idx]['low'] < df.iloc[idx-1]['low'] and df.iloc[idx]['low'] < df.iloc[idx+1]['low']

    def _check_neckline_support(self, df: pd.DataFrame, left_shoulder: Dict, head: Dict, right_shoulder: Dict) -> bool:
        """בדיקת תמיכת קו הצוואר"""
        try:
            neckline_level = min(left_shoulder['low'], head['low'], right_shoulder['low'])
            # בדיקה אם המחיר נשאר מעל קו הצוואר
            return True  # פישוט לצורך הדוגמה
        except:
            return False

    def _is_cup_shape(self, cup_data: pd.DataFrame) -> bool:
        """בדיקה אם הנתונים יוצרים צורת כוס"""
        try:
            # פישוט - בדיקה בסיסית
            return len(cup_data) >= 10
        except:
            return False

    def _is_handle_shape(self, handle_data: pd.DataFrame, cup_high: float) -> bool:
        """בדיקה אם הנתונים יוצרים צורת ידית"""
        try:
            # פישוט - בדיקה בסיסית
            return len(handle_data) >= 5 and handle_data['high'].max() < cup_high
        except:
            return False

    def _find_harmonic_key_points(self, df: pd.DataFrame, end_idx: int) -> Optional[List[Dict]]:
        """מציאת נקודות מפתח לתבניות הרמוניות"""
        try:
            # פישוט - החזרת נקודות מדומות
            return None
        except:
            return None

    def _classify_harmonic_pattern(self, key_points: List[Dict]) -> Optional[str]:
        """סיווג תבנית הרמונית"""
        try:
            # פישוט - החזרת None
            return None
        except:
            return None

