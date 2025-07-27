import pandas as pd
import numpy as np
from datetime import datetime
from core.base.base_agent import BaseAgent
import logging
from typing import Dict, List

class BullishPatternSpotter(BaseAgent):
    """
    סוכן מתקדם לזיהוי תבניות בולשיות במחיר
    כולל תבניות קנדלסטיק פשוטות ותבניות מורכבות מבוססות למידה
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        self.min_pattern_strength = cfg.get("min_pattern_strength", 0.02)
        self.volume_weight = cfg.get("volume_weight", 0.3)
        self.price_weight = cfg.get("price_weight", 0.7)
        self.pattern_threshold = cfg.get("pattern_threshold", 0.6)
        self.cup_handle_lookback = cfg.get("cup_handle_lookback", 60)  # ימים לניתוח Cup & Handle
        self.flag_lookback = cfg.get("flag_lookback", 30)  # ימים לניתוח דגלים
        self.relative_strength_period = cfg.get("relative_strength_period", 20)  # תקופה לחוזק יחסי
        self.log("Enhanced Bullish Pattern Spotter initialized")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        מנתח תבניות בולשיות מתקדמות במניה
        """
        try:
            if price_df is None or price_df.empty:
                return self._get_dummy_result("אין נתוני מחיר זמינים")
            
            if len(price_df) < 30:
                return self._get_dummy_result("לא מספיק נתונים לניתוח תבניות מתקדמות")
            
            # זיהוי תבניות קנדלסטיק בסיסיות
            candlestick_patterns = self._identify_candlestick_patterns(price_df)
            
            # זיהוי תבניות מורכבות
            complex_patterns = self._identify_complex_patterns(price_df)
            
            # ניתוח חוזק יחסי
            relative_strength = self._analyze_relative_strength(price_df)
            
            # ניתוח נפח מתקדם
            volume_analysis = self._analyze_advanced_volume(price_df, candlestick_patterns)
            
            # חישוב ציון כולל
            score = self._calculate_comprehensive_score(candlestick_patterns, complex_patterns, relative_strength, volume_analysis)
            
            # יצירת סיכום מתקדם
            summary = self._generate_advanced_summary(candlestick_patterns, complex_patterns, relative_strength, volume_analysis)
            
            # המלצות מתקדמות
            recommendations = self._generate_advanced_recommendations(candlestick_patterns, complex_patterns, relative_strength, volume_analysis)
            
            return {
                "score": score,
                "explanation": summary,
                "details": {
                    "candlestick_patterns": candlestick_patterns,
                    "complex_patterns": complex_patterns,
                    "relative_strength": relative_strength,
                    "volume_analysis": volume_analysis,
                    "recommendations": recommendations
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log(f"שגיאה בזיהוי תבניות בולשיות מתקדמות: {str(e)}")
            return self._get_dummy_result(f"שגיאה: {str(e)}")

    def _identify_candlestick_patterns(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבניות קנדלסטיק בסיסיות"""
        patterns = {
            "hammer": self._detect_hammer(price_df),
            "doji": self._detect_doji(price_df),
            "engulfing": self._detect_bullish_engulfing(price_df),
            "morning_star": self._detect_morning_star(price_df),
            "piercing": self._detect_piercing(price_df),
            "three_white_soldiers": self._detect_three_white_soldiers(price_df),
            "current_candle": self._analyze_current_candle(price_df)
        }
        
        # חישוב ציון כללי לתבניות
        total_patterns = sum(1 for p in patterns.values() if p.get('detected', False))
        pattern_strength = sum(p.get('strength', 0) for p in patterns.values() if p.get('detected', False))
        
        return {
            "individual_patterns": patterns,
            "total_patterns": total_patterns,
            "pattern_strength": pattern_strength,
            "overall_strength": pattern_strength / max(total_patterns, 1)
        }

    def _identify_complex_patterns(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבניות מורכבות מבוססות למידה"""
        patterns = {
            "cup_and_handle": self._detect_cup_and_handle(price_df),
            "bull_flag": self._detect_bull_flag(price_df),
            "ascending_triangle": self._detect_ascending_triangle(price_df),
            "symmetrical_triangle": self._detect_symmetrical_triangle(price_df),
            "double_bottom": self._detect_double_bottom(price_df),
            "inverse_head_shoulders": self._detect_inverse_head_shoulders(price_df)
        }
        
        # חישוב ציון כללי לתבניות מורכבות
        total_complex_patterns = sum(1 for p in patterns.values() if p.get('detected', False))
        complex_pattern_strength = sum(p.get('strength', 0) for p in patterns.values() if p.get('detected', False))
        
        return {
            "individual_patterns": patterns,
            "total_patterns": total_complex_patterns,
            "pattern_strength": complex_pattern_strength,
            "overall_strength": complex_pattern_strength / max(total_complex_patterns, 1)
        }

    def _detect_hammer(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Hammer"""
        if len(price_df) < 1:
            return {"detected": False, "strength": 0}
        
        current = price_df.iloc[-1]
        open_price = current['open']
        close_price = current['close']
        high_price = current['high']
        low_price = current['low']
        
        # חישוב גוף הנר
        body = abs(close_price - open_price)
        total_range = high_price - low_price
        
        # חישוב הצל
        upper_shadow = high_price - max(open_price, close_price)
        lower_shadow = min(open_price, close_price) - low_price
        
        # תנאים ל-Hammer
        is_hammer = (
            lower_shadow > 2 * body and  # צל תחתון ארוך
            upper_shadow < body and       # צל עליון קצר
            total_range > 0 and           # טווח חיובי
            body > 0                      # גוף חיובי
        )
        
        strength = 0
        if is_hammer:
            strength = min(100, (lower_shadow / body) * 20)
        
        return {
            "detected": is_hammer,
            "strength": strength,
            "body": body,
            "lower_shadow": lower_shadow,
            "upper_shadow": upper_shadow
        }

    def _detect_doji(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Doji"""
        if len(price_df) < 1:
            return {"detected": False, "strength": 0}
        
        current = price_df.iloc[-1]
        open_price = current['open']
        close_price = current['close']
        high_price = current['high']
        low_price = current['low']
        
        # חישוב גוף הנר
        body = abs(close_price - open_price)
        total_range = high_price - low_price
        
        # תנאים ל-Doji
        is_doji = (
            body < total_range * 0.1 and  # גוף קטן מאוד
            total_range > 0               # טווח חיובי
        )
        
        strength = 0
        if is_doji:
            strength = min(100, (total_range / body) * 10 if body > 0 else 100)
        
        return {
            "detected": is_doji,
            "strength": strength,
            "body": body,
            "total_range": total_range
        }

    def _detect_bullish_engulfing(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Bullish Engulfing"""
        if len(price_df) < 2:
            return {"detected": False, "strength": 0}
        
        current = price_df.iloc[-1]
        previous = price_df.iloc[-2]
        
        current_open = current['open']
        current_close = current['close']
        previous_open = previous['open']
        previous_close = previous['close']
        
        # חישוב גופי הנרות
        current_body = current_close - current_open
        previous_body = previous_close - previous_open
        
        # תנאים ל-Bullish Engulfing
        is_bullish_engulfing = (
            previous_body < 0 and         # נר קודם שלילי
            current_body > 0 and          # נר נוכחי חיובי
            current_open < previous_close and  # פתיחה מתחת לסגירה הקודמת
            current_close > previous_open      # סגירה מעל הפתיחה הקודמת
        )
        
        strength = 0
        if is_bullish_engulfing:
            strength = min(100, abs(current_body / previous_body) * 20)
        
        return {
            "detected": is_bullish_engulfing,
            "strength": strength,
            "current_body": current_body,
            "previous_body": previous_body
        }

    def _detect_morning_star(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Morning Star"""
        if len(price_df) < 3:
            return {"detected": False, "strength": 0}
        
        first = price_df.iloc[-3]
        second = price_df.iloc[-2]
        third = price_df.iloc[-1]
        
        first_body = first['close'] - first['open']
        second_body = second['close'] - second['open']
        third_body = third['close'] - third['open']
        
        # תנאים ל-Morning Star
        is_morning_star = (
            first_body < 0 and            # נר ראשון שלילי
            abs(second_body) < abs(first_body) * 0.3 and  # נר שני קטן
            third_body > 0 and            # נר שלישי חיובי
            third['close'] > (first['open'] + first['close']) / 2  # סגירה מעל אמצע הנר הראשון
        )
        
        strength = 0
        if is_morning_star:
            strength = min(100, (third_body / abs(first_body)) * 30)
        
        return {
            "detected": is_morning_star,
            "strength": strength,
            "first_body": first_body,
            "second_body": second_body,
            "third_body": third_body
        }

    def _detect_piercing(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Piercing"""
        if len(price_df) < 2:
            return {"detected": False, "strength": 0}
        
        current = price_df.iloc[-1]
        previous = price_df.iloc[-2]
        
        current_open = current['open']
        current_close = current['close']
        previous_open = previous['open']
        previous_close = previous['close']
        
        # חישוב גופי הנרות
        current_body = current_close - current_open
        previous_body = previous_close - previous_open
        
        # תנאים ל-Piercing
        is_piercing = (
            previous_body < 0 and         # נר קודם שלילי
            current_body > 0 and          # נר נוכחי חיובי
            current_open < previous_close and  # פתיחה מתחת לסגירה הקודמת
            current_close > previous_close + previous_body * 0.5  # סגירה מעל אמצע הנר הקודם
        )
        
        strength = 0
        if is_piercing:
            strength = min(100, (current_body / abs(previous_body)) * 25)
        
        return {
            "detected": is_piercing,
            "strength": strength,
            "current_body": current_body,
            "previous_body": previous_body
        }

    def _detect_three_white_soldiers(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Three White Soldiers"""
        if len(price_df) < 3:
            return {"detected": False, "strength": 0}
        
        candles = [price_df.iloc[-3], price_df.iloc[-2], price_df.iloc[-1]]
        
        # בדיקה שכל הנרות חיוביים
        all_bullish = all(candle['close'] > candle['open'] for candle in candles)
        
        # בדיקה שכל הנרות גדלים
        bodies = [candle['close'] - candle['open'] for candle in candles]
        increasing = all(bodies[i] <= bodies[i+1] for i in range(len(bodies)-1))
        
        # בדיקה שכל הנרות נפתחים בתוך גוף הנר הקודם
        opens_within_previous = all(
            candles[i]['open'] >= candles[i-1]['open'] and
            candles[i]['open'] <= candles[i-1]['close']
            for i in range(1, len(candles))
        )
        
        is_three_white_soldiers = all_bullish and increasing and opens_within_previous
        
        strength = 0
        if is_three_white_soldiers:
            strength = min(100, sum(bodies) / price_df['close'].iloc[-3] * 100)
        
        return {
            "detected": is_three_white_soldiers,
            "strength": strength,
            "bodies": bodies
        }

    def _analyze_current_candle(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח הנר הנוכחי"""
        if len(price_df) < 1:
            return {"detected": False, "strength": 0}
        
        current = price_df.iloc[-1]
        open_price = current['open']
        close_price = current['close']
        high_price = current['high']
        low_price = current['low']
        
        # חישוב גוף הנר
        body = close_price - open_price
        total_range = high_price - low_price
        
        # ניתוח חוזק הנר
        if body > 0:  # נר חיובי (בולשי)
            strength = min(100, (body / total_range) * 100 if total_range > 0 else 50)
            candle_type = "בולשי"
            # נר בולשי מקבל ציון חיובי
            score = strength
        else:  # נר שלילי (שלילי)
            strength = min(100, (abs(body) / total_range) * 100 if total_range > 0 else 50)
            candle_type = "שלילי"
            # נר שלילי מקבל ציון נמוך (הפוך מהחוזק)
            score = max(1, 100 - strength)
        
        return {
            "detected": True,
            "strength": strength,
            "score": score,  # ציון מתוקן לפי כיוון
            "candle_type": candle_type,
            "body": body,
            "total_range": total_range,
            "body_percentage": (body / total_range * 100) if total_range > 0 else 0
        }

    def _detect_cup_and_handle(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Cup & Handle"""
        if len(price_df) < self.cup_handle_lookback:
            return {"detected": False, "strength": 0}
        
        # ניתוח תבנית Cup & Handle
        close_prices = price_df['close'].tail(self.cup_handle_lookback)
        high_prices = price_df['high'].tail(self.cup_handle_lookback)
        low_prices = price_df['low'].tail(self.cup_handle_lookback)
        
        # חלוקה ל-Cup ו-Handle
        cup_length = int(self.cup_handle_lookback * 0.7)
        handle_length = self.cup_handle_lookback - cup_length
        
        cup_prices = close_prices[:cup_length]
        handle_prices = close_prices[cup_length:]
        
        # בדיקת תנאי Cup
        cup_start = cup_prices.iloc[0]
        cup_end = cup_prices.iloc[-1]
        cup_min = cup_prices.min()
        
        # Cup צריך להיות סימטרי עם תחתית מעוגלת
        cup_symmetry = abs(cup_start - cup_end) / max(cup_start, cup_end) < 0.1
        cup_rounded = (cup_prices.iloc[:len(cup_prices)//2].min() - cup_min) / cup_min < 0.05
        
        # Handle צריך להיות ירידה קטנה
        handle_decline = (handle_prices.iloc[0] - handle_prices.min()) / handle_prices.iloc[0] < 0.15
        
        # בדיקת נפח
        volume_increase = price_df['volume'].tail(5).mean() > price_df['volume'].tail(20).mean() * 1.2
        
        is_cup_handle = cup_symmetry and cup_rounded and handle_decline and volume_increase
        
        strength = 0
        if is_cup_handle:
            # חישוב חוזק על בסיס איכות התבנית
            symmetry_score = (1 - abs(cup_start - cup_end) / max(cup_start, cup_end)) * 100
            volume_score = min(100, (price_df['volume'].tail(5).mean() / price_df['volume'].tail(20).mean()) * 50)
            strength = (symmetry_score + volume_score) / 2
        
        return {
            "detected": is_cup_handle,
            "strength": strength,
            "cup_start": cup_start,
            "cup_end": cup_end,
            "cup_min": cup_min,
            "handle_decline": (handle_prices.iloc[0] - handle_prices.min()) / handle_prices.iloc[0] if handle_decline else 0
        }

    def _detect_bull_flag(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Bull Flag"""
        if len(price_df) < self.flag_lookback:
            return {"detected": False, "strength": 0}
        
        # ניתוח תבנית Bull Flag
        close_prices = price_df['close'].tail(self.flag_lookback)
        high_prices = price_df['high'].tail(self.flag_lookback)
        low_prices = price_df['low'].tail(self.flag_lookback)
        
        # חלוקה ל-Pole ו-Flag
        pole_length = int(self.flag_lookback * 0.3)
        flag_length = self.flag_lookback - pole_length
        
        pole_prices = close_prices[:pole_length]
        flag_prices = close_prices[pole_length:]
        
        # Pole צריך להיות עלייה חזקה
        pole_rise = (pole_prices.iloc[-1] - pole_prices.iloc[0]) / pole_prices.iloc[0]
        strong_pole = pole_rise > 0.1  # עלייה של לפחות 10%
        
        # Flag צריך להיות ירידה קטנה או צדדית
        flag_decline = (flag_prices.iloc[0] - flag_prices.min()) / flag_prices.iloc[0] < 0.08
        
        # בדיקת נפח - נפח גבוה ב-Pole, נמוך ב-Flag
        pole_volume = price_df['volume'].iloc[:pole_length].mean()
        flag_volume = price_df['volume'].iloc[pole_length:].mean()
        volume_pattern = pole_volume > flag_volume * 1.5
        
        is_bull_flag = strong_pole and flag_decline and volume_pattern
        
        strength = 0
        if is_bull_flag:
            pole_score = min(100, pole_rise * 500)  # ציון על בסיס חוזק העלייה
            volume_score = min(100, (pole_volume / flag_volume) * 30)
            strength = (pole_score + volume_score) / 2
        
        return {
            "detected": is_bull_flag,
            "strength": strength,
            "pole_rise": pole_rise,
            "flag_decline": (flag_prices.iloc[0] - flag_prices.min()) / flag_prices.iloc[0] if flag_decline else 0,
            "volume_ratio": pole_volume / flag_volume if volume_pattern else 1
        }

    def _detect_ascending_triangle(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Ascending Triangle"""
        if len(price_df) < 20:
            return {"detected": False, "strength": 0}
        
        # ניתוח תבנית Ascending Triangle
        close_prices = price_df['close'].tail(20)
        high_prices = price_df['high'].tail(20)
        low_prices = price_df['low'].tail(20)
        
        # חיפוש קווי תמיכה והתנגדות
        highs = high_prices.rolling(3).max()
        lows = low_prices.rolling(3).min()
        
        # קו התנגדות אופקי
        resistance_level = highs.mean()
        resistance_variance = highs.std() / resistance_level
        
        # קו תמיכה עולה
        low_trend = np.polyfit(range(len(lows)), lows, 1)[0]
        ascending_support = low_trend > 0
        
        # בדיקת התכנסות
        convergence = resistance_variance < 0.02 and ascending_support
        
        is_ascending_triangle = convergence
        
        strength = 0
        if is_ascending_triangle:
            # חישוב חוזק על בסיס איכות הקווים
            resistance_quality = (1 - resistance_variance) * 100
            support_quality = min(100, low_trend * 1000)
            strength = (resistance_quality + support_quality) / 2
        
        return {
            "detected": is_ascending_triangle,
            "strength": strength,
            "resistance_level": resistance_level,
            "support_slope": low_trend,
            "convergence_quality": 1 - resistance_variance
        }

    def _detect_symmetrical_triangle(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Symmetrical Triangle"""
        if len(price_df) < 20:
            return {"detected": False, "strength": 0}
        
        # ניתוח תבנית Symmetrical Triangle
        close_prices = price_df['close'].tail(20)
        high_prices = price_df['high'].tail(20)
        low_prices = price_df['low'].tail(20)
        
        # חיפוש קווי תמיכה והתנגדות מתכנסים
        highs = high_prices.rolling(3).max()
        lows = low_prices.rolling(3).min()
        
        # מגמות
        high_trend = np.polyfit(range(len(highs)), highs, 1)[0]
        low_trend = np.polyfit(range(len(lows)), lows, 1)[0]
        
        # התכנסות - קו עליון יורד, קו תחתון עולה
        converging = high_trend < 0 and low_trend > 0
        
        # בדיקת איכות ההתכנסות
        convergence_quality = abs(high_trend) + abs(low_trend)
        
        is_symmetrical_triangle = converging and convergence_quality > 0.01
        
        strength = 0
        if is_symmetrical_triangle:
            strength = min(100, convergence_quality * 5000)
        
        return {
            "detected": is_symmetrical_triangle,
            "strength": strength,
            "high_trend": high_trend,
            "low_trend": low_trend,
            "convergence_quality": convergence_quality
        }

    def _detect_double_bottom(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Double Bottom"""
        if len(price_df) < 30:
            return {"detected": False, "strength": 0}
        
        # ניתוח תבנית Double Bottom
        close_prices = price_df['close'].tail(30)
        low_prices = price_df['low'].tail(30)
        
        # חיפוש שני תחתיות
        lows = low_prices.rolling(3).min()
        
        # זיהוי תחתיות מקומיות
        local_mins = []
        for i in range(2, len(lows) - 2):
            if lows.iloc[i] <= lows.iloc[i-1] and lows.iloc[i] <= lows.iloc[i-2] and \
               lows.iloc[i] <= lows.iloc[i+1] and lows.iloc[i] <= lows.iloc[i+2]:
                local_mins.append((i, lows.iloc[i]))
        
        if len(local_mins) < 2:
            return {"detected": False, "strength": 0}
        
        # בדיקת שני תחתיות דומות
        bottom1_idx, bottom1_val = local_mins[-2]
        bottom2_idx, bottom2_val = local_mins[-1]
        
        # התחתיות צריכות להיות דומות (בתוך 3%)
        similar_bottoms = abs(bottom1_val - bottom2_val) / max(bottom1_val, bottom2_val) < 0.03
        
        # בדיקת עלייה בין התחתיות
        middle_high = close_prices.iloc[bottom1_idx:bottom2_idx].max()
        rise_between = (middle_high - min(bottom1_val, bottom2_val)) / min(bottom1_val, bottom2_val)
        sufficient_rise = rise_between > 0.05  # עלייה של לפחות 5%
        
        is_double_bottom = similar_bottoms and sufficient_rise
        
        strength = 0
        if is_double_bottom:
            # חישוב חוזק על בסיס איכות התבנית
            similarity_score = (1 - abs(bottom1_val - bottom2_val) / max(bottom1_val, bottom2_val)) * 100
            rise_score = min(100, rise_between * 1000)
            strength = (similarity_score + rise_score) / 2
        
        return {
            "detected": is_double_bottom,
            "strength": strength,
            "bottom1": bottom1_val,
            "bottom2": bottom2_val,
            "middle_high": middle_high,
            "rise_between": rise_between
        }

    def _detect_inverse_head_shoulders(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Inverse Head & Shoulders"""
        if len(price_df) < 40:
            return {"detected": False, "strength": 0}
        
        # ניתוח תבנית Inverse Head & Shoulders
        close_prices = price_df['close'].tail(40)
        low_prices = price_df['low'].tail(40)
        
        # חיפוש שלושה תחתיות
        lows = low_prices.rolling(3).min()
        
        # זיהוי תחתיות מקומיות
        local_mins = []
        for i in range(2, len(lows) - 2):
            if lows.iloc[i] <= lows.iloc[i-1] and lows.iloc[i] <= lows.iloc[i-2] and \
               lows.iloc[i] <= lows.iloc[i+1] and lows.iloc[i] <= lows.iloc[i+2]:
                local_mins.append((i, lows.iloc[i]))
        
        if len(local_mins) < 3:
            return {"detected": False, "strength": 0}
        
        # בדיקת תבנית H&S הפוכה
        left_shoulder_idx, left_shoulder_val = local_mins[-3]
        head_idx, head_val = local_mins[-2]
        right_shoulder_idx, right_shoulder_val = local_mins[-1]
        
        # הראש צריך להיות נמוך מהכתפיים
        head_lower = head_val < left_shoulder_val and head_val < right_shoulder_val
        
        # הכתפיים צריכות להיות דומות
        shoulders_similar = abs(left_shoulder_val - right_shoulder_val) / max(left_shoulder_val, right_shoulder_val) < 0.05
        
        # בדיקת עלייה מהראש
        rise_from_head = (close_prices.iloc[-1] - head_val) / head_val
        sufficient_rise = rise_from_head > 0.03  # עלייה של לפחות 3%
        
        is_inverse_hs = head_lower and shoulders_similar and sufficient_rise
        
        strength = 0
        if is_inverse_hs:
            # חישוב חוזק על בסיס איכות התבנית
            head_depth = (left_shoulder_val - head_val) / left_shoulder_val
            shoulder_symmetry = (1 - abs(left_shoulder_val - right_shoulder_val) / max(left_shoulder_val, right_shoulder_val)) * 100
            rise_score = min(100, rise_from_head * 1000)
            strength = (head_depth * 100 + shoulder_symmetry + rise_score) / 3
        
        return {
            "detected": is_inverse_hs,
            "strength": strength,
            "left_shoulder": left_shoulder_val,
            "head": head_val,
            "right_shoulder": right_shoulder_val,
            "rise_from_head": rise_from_head
        }

    def _analyze_relative_strength(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח חוזק יחסי לעומת השוק"""
        try:
            # חישוב RSI
            close_prices = price_df['close']
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # חישוב חוזק יחסי
            current_price = close_prices.iloc[-1]
            price_20d_ago = close_prices.iloc[-self.relative_strength_period]
            relative_strength = (current_price / price_20d_ago - 1) * 100
            
            # חישוב Beta (פשט)
            returns = close_prices.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # שנתי
            
            # ניתוח מגמה
            sma_20 = close_prices.rolling(20).mean()
            sma_50 = close_prices.rolling(50).mean()
            
            trend_strength = 0
            if len(sma_20) > 0 and len(sma_50) > 0:
                current_sma_20 = sma_20.iloc[-1]
                current_sma_50 = sma_50.iloc[-1]
                price = close_prices.iloc[-1]
                
                if price > current_sma_20 > current_sma_50:
                    trend_strength = 100  # מגמה חזקה
                elif price > current_sma_20:
                    trend_strength = 70   # מגמה בינונית
                elif price > current_sma_50:
                    trend_strength = 40   # מגמה חלשה
                else:
                    trend_strength = 10   # מגמה שלילית
            
            # ציון כללי
            rsi_score = 50
            if 30 <= rsi.iloc[-1] <= 70:
                rsi_score = 80  # RSI נורמלי
            elif rsi.iloc[-1] < 30:
                rsi_score = 100  # RSI נמוך - פוטנציאל קנייה
            elif rsi.iloc[-1] > 70:
                rsi_score = 20   # RSI גבוה - פוטנציאל מכירה
            
            relative_strength_score = min(100, max(0, relative_strength * 10 + 50))
            
            overall_score = (rsi_score + relative_strength_score + trend_strength) / 3
            
            return {
                "rsi": rsi.iloc[-1],
                "rsi_score": rsi_score,
                "relative_strength": relative_strength,
                "relative_strength_score": relative_strength_score,
                "volatility": volatility,
                "trend_strength": trend_strength,
                "sma_20": current_sma_20 if len(sma_20) > 0 else None,
                "sma_50": current_sma_50 if len(sma_50) > 0 else None,
                "overall_score": overall_score
            }
            
        except Exception as e:
            self.log(f"שגיאה בניתוח חוזק יחסי: {str(e)}")
            return {
                "rsi": 50,
                "rsi_score": 50,
                "relative_strength": 0,
                "relative_strength_score": 50,
                "volatility": 0,
                "trend_strength": 50,
                "overall_score": 50
            }

    def _analyze_advanced_volume(self, price_df: pd.DataFrame, patterns: Dict) -> Dict:
        """ניתוח נפח מתקדם"""
        volume = price_df["volume"]
        
        # ניתוח נפח נוכחי
        current_volume = volume.iloc[-1]
        avg_volume = volume.rolling(20).mean().iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # זיהוי סיגנל נפח
        if volume_ratio > 2:
            volume_signal = "גבוה מאוד"
            volume_score = 100
        elif volume_ratio > 1.5:
            volume_signal = "גבוה"
            volume_score = 80
        elif volume_ratio > 1.2:
            volume_signal = "בינוני-גבוה"
            volume_score = 60
        elif volume_ratio > 0.8:
            volume_signal = "נורמלי"
            volume_score = 40
        else:
            volume_signal = "נמוך"
            volume_score = 20
        
        # מגמת נפח
        recent_volume_trend = volume.tail(5).mean() / volume.tail(20).mean()
        if recent_volume_trend > 1.2:
            volume_trend = "עולה"
        elif recent_volume_trend < 0.8:
            volume_trend = "יורד"
        else:
            volume_trend = "יציב"
        
        # ניתוח נפח מתקדם - Volume Price Trend (VPT)
        close_prices = price_df['close']
        vpt = ((close_prices - close_prices.shift(1)) / close_prices.shift(1) * volume).cumsum()
        vpt_trend = "עולה" if vpt.iloc[-1] > vpt.iloc[-5] else "יורד"
        
        # ניתוח On-Balance Volume (OBV)
        obv = (np.sign(close_prices.diff()) * volume).cumsum()
        obv_trend = "עולה" if obv.iloc[-1] > obv.iloc[-5] else "יורד"
        
        return {
            "current_volume": current_volume,
            "avg_volume": avg_volume,
            "volume_ratio": volume_ratio,
            "volume_signal": volume_signal,
            "volume_score": volume_score,
            "volume_trend": volume_trend,
            "recent_volume_trend": recent_volume_trend,
            "vpt_trend": vpt_trend,
            "obv_trend": obv_trend,
            "volume_confirmation": vpt_trend == "עולה" and obv_trend == "עולה"
        }

    def _calculate_comprehensive_score(self, candlestick_patterns: Dict, complex_patterns: Dict, relative_strength: Dict, volume_analysis: Dict) -> int:
        """חישוב ציון כולל מתקדם"""
        # ציון תבניות קנדלסטיק
        candlestick_score = candlestick_patterns.get("overall_strength", 0) * 100
        
        # ציון תבניות מורכבות (משקל גבוה יותר)
        complex_score = complex_patterns.get("overall_strength", 0) * 100
        
        # ציון חוזק יחסי
        relative_strength_score = relative_strength.get("overall_score", 50)
        
        # ציון נפח
        volume_score = volume_analysis.get("volume_score", 50)
        
        # חישוב סופי עם משקלים
        final_score = int(
            (candlestick_score * 0.2) +      # 20% תבניות קנדלסטיק
            (complex_score * 0.4) +          # 40% תבניות מורכבות
            (relative_strength_score * 0.3) + # 30% חוזק יחסי
            (volume_score * 0.1)             # 10% נפח
        )
        
        return max(1, min(100, final_score))

    def _generate_advanced_summary(self, candlestick_patterns: Dict, complex_patterns: Dict, relative_strength: Dict, volume_analysis: Dict) -> str:
        """יצירת סיכום מתקדם"""
        summary_parts = []
        
        # תבניות קנדלסטיק
        candlestick_detected = []
        for pattern_name, pattern_data in candlestick_patterns.get("individual_patterns", {}).items():
            if pattern_data.get("detected", False):
                candlestick_detected.append(pattern_name.replace("_", " "))
        
        if candlestick_detected:
            summary_parts.append(f"תבניות קנדלסטיק: {', '.join(candlestick_detected)}")
        
        # תבניות מורכבות
        complex_detected = []
        for pattern_name, pattern_data in complex_patterns.get("individual_patterns", {}).items():
            if pattern_data.get("detected", False):
                complex_detected.append(pattern_name.replace("_", " "))
        
        if complex_detected:
            summary_parts.append(f"תבניות מורכבות: {', '.join(complex_detected)}")
        
        # חוזק יחסי
        rsi = relative_strength.get("rsi", 50)
        relative_strength_val = relative_strength.get("relative_strength", 0)
        summary_parts.append(f"RSI: {rsi:.1f}, חוזק יחסי: {relative_strength_val:+.1f}%")
        
        # נפח
        volume_signal = volume_analysis.get("volume_signal", "לא ידוע")
        volume_trend = volume_analysis.get("volume_trend", "לא ידוע")
        summary_parts.append(f"נפח: {volume_signal}, מגמה: {volume_trend}")
        
        # אישור נפח
        if volume_analysis.get("volume_confirmation", False):
            summary_parts.append("אישור נפח: VPT ו-OBV עולים")
        
        return ". ".join(summary_parts)

    def _generate_advanced_recommendations(self, candlestick_patterns: Dict, complex_patterns: Dict, relative_strength: Dict, volume_analysis: Dict) -> List[str]:
        """יצירת המלצות מתקדמות"""
        recommendations = []
        
        # המלצות על בסיס תבניות מורכבות
        complex_patterns_list = []
        for pattern_name, pattern_data in complex_patterns.get("individual_patterns", {}).items():
            if pattern_data.get("detected", False):
                complex_patterns_list.append(pattern_name)
        
        if "cup_and_handle" in complex_patterns_list:
            recommendations.append("תבנית Cup & Handle - סיגנל קנייה חזק לטווח ארוך")
        if "bull_flag" in complex_patterns_list:
            recommendations.append("תבנית Bull Flag - המשך עלייה צפוי")
        if "ascending_triangle" in complex_patterns_list:
            recommendations.append("תבנית Ascending Triangle - פריצה צפויה")
        if "double_bottom" in complex_patterns_list:
            recommendations.append("תבנית Double Bottom - היפוך מגמה צפוי")
        if "inverse_head_shoulders" in complex_patterns_list:
            recommendations.append("תבנית Inverse Head & Shoulders - היפוך מגמה חזק")
        
        # המלצות על בסיס חוזק יחסי
        rsi = relative_strength.get("rsi", 50)
        if rsi < 30:
            recommendations.append("RSI נמוך - פוטנציאל קנייה")
        elif rsi > 70:
            recommendations.append("RSI גבוה - זהירות")
        
        relative_strength_val = relative_strength.get("relative_strength", 0)
        if relative_strength_val > 10:
            recommendations.append("חוזק יחסי גבוה - ביצועים טובים מהשוק")
        elif relative_strength_val < -10:
            recommendations.append("חוזק יחסי נמוך - ביצועים גרועים מהשוק")
        
        # המלצות על בסיס נפח
        if volume_analysis.get("volume_confirmation", False):
            recommendations.append("אישור נפח - סיגנל חזק")
        
        if not recommendations:
            recommendations.append("שמור על עמדה נוכחית - אין סיגנלים חזקים")
        
        return recommendations
