import pandas as pd
import numpy as np
from datetime import datetime
from core.base.base_agent import BaseAgent
from core.market_data_connector import MarketDataConnector
import logging
from typing import Dict, List

class EnhancedAdvancedAnalyzer(BaseAgent):
    """
    סוכן מתקדם משופר עם חיבור למקורות נתונים מרובים
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        self.lookback_period = cfg.get("lookback_period", 100)
        self.min_pattern_quality = cfg.get("min_pattern_quality", 0.7)
        self.volume_confirmation_weight = cfg.get("volume_confirmation_weight", 0.3)
        self.pattern_weight = cfg.get("pattern_weight", 0.7)
        
        # מחבר נתוני שוק
        self.market_connector = MarketDataConnector(config)
        
        self.log("Enhanced Advanced Analyzer initialized with market data connector")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח מתקדם עם נתוני שוק מקיפים
        """
        try:
            if price_df is None or price_df.empty:
                return self._get_dummy_result("אין נתוני מחיר זמינים")
            
            if len(price_df) < 50:
                return self._get_dummy_result("לא מספיק נתונים לניתוח מתקדם")
            
            # קבלת נתוני שוק מקיפים
            market_data = self.market_connector.get_comprehensive_market_data(symbol)
            
            # ניתוח תבניות מורכבות
            complex_patterns = self._analyze_complex_patterns(price_df)
            
            # ניתוח יחסי לשוק עם נתונים אמיתיים
            market_analysis = self._analyze_market_relative_enhanced(symbol, price_df, market_data)
            
            # ניתוח נפח מתקדם
            volume_analysis = self._analyze_advanced_volume_patterns(price_df)
            
            # ניתוח מגמות מתקדם
            trend_analysis = self._analyze_advanced_trends(price_df)
            
            # ניתוח תמיכה והתנגדות
            support_resistance = self._analyze_support_resistance(price_df)
            
            # ניתוח סנטימנט השוק
            market_sentiment = self.market_connector.get_market_sentiment()
            
            # חישוב ציון כולל משופר
            score = self._calculate_enhanced_score(
                complex_patterns, market_analysis, volume_analysis, 
                trend_analysis, support_resistance, market_sentiment
            )
            
            # יצירת סיכום מתקדם
            summary = self._generate_enhanced_summary(
                complex_patterns, market_analysis, volume_analysis, 
                trend_analysis, support_resistance, market_sentiment
            )
            
            # המלצות מתקדמות
            recommendations = self._generate_enhanced_recommendations(
                complex_patterns, market_analysis, volume_analysis, 
                trend_analysis, support_resistance, market_sentiment
            )
            
            return {
                "score": score,
                "explanation": summary,
                "details": {
                    "complex_patterns": complex_patterns,
                    "market_analysis": market_analysis,
                    "volume_analysis": volume_analysis,
                    "trend_analysis": trend_analysis,
                    "support_resistance": support_resistance,
                    "market_sentiment": market_sentiment,
                    "market_data": market_data,
                    "recommendations": recommendations
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.log(f"שגיאה בניתוח מתקדם משופר: {str(e)}")
            return self._get_dummy_result(f"שגיאה: {str(e)}")

    def _analyze_market_relative_enhanced(self, symbol: str, price_df: pd.DataFrame, market_data: Dict) -> Dict:
        """ניתוח יחסי לשוק משופר עם נתונים אמיתיים"""
        try:
            # נתונים בסיסיים
            close_prices = price_df['close']
            current_price = close_prices.iloc[-1]
            
            # ביצועים יחסיים
            performance_20d = (current_price / close_prices.iloc[-20] - 1) * 100
            performance_50d = (current_price / close_prices.iloc[-50] - 1) * 100 if len(close_prices) >= 50 else 0
            
            # תנודתיות
            returns = close_prices.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            
            # ניתוח יחסי לשוק האמיתי
            market_performance = market_data.get("relative_analysis", {}).get("market_performance", {})
            sector_performance = market_data.get("relative_analysis", {}).get("sector_performance", {})
            volatility_analysis = market_data.get("relative_analysis", {}).get("volatility_analysis", {})
            
            # ניתוח מגמה
            sma_20 = close_prices.rolling(20).mean()
            sma_50 = close_prices.rolling(50).mean()
            
            trend_strength = 0
            if len(sma_20) > 0 and len(sma_50) > 0:
                current_sma_20 = sma_20.iloc[-1]
                current_sma_50 = sma_50.iloc[-1]
                
                if current_price > current_sma_20 > current_sma_50:
                    trend_strength = 100
                elif current_price > current_sma_20:
                    trend_strength = 70
                elif current_price > current_sma_50:
                    trend_strength = 40
                else:
                    trend_strength = 10
            
            # ציונים משופרים
            performance_score = min(100, max(0, performance_20d * 5 + 50))
            volatility_score = max(0, 100 - volatility * 100)
            trend_score = trend_strength
            
            # בונוס על ביצועים יחסיים
            relative_bonus = 0
            if market_performance.get("outperformance", False):
                relative_bonus = 10
            elif sector_performance.get("outperformance", False):
                relative_bonus = 5
            
            overall_score = (performance_score + volatility_score + trend_score) / 3 + relative_bonus
            
            return {
                "performance_20d": performance_20d,
                "performance_50d": performance_50d,
                "volatility": volatility,
                "trend_strength": trend_strength,
                "performance_score": performance_score,
                "volatility_score": volatility_score,
                "trend_score": trend_score,
                "relative_bonus": relative_bonus,
                "overall_score": overall_score,
                "market_performance": market_performance,
                "sector_performance": sector_performance,
                "volatility_analysis": volatility_analysis
            }
            
        except Exception as e:
            self.log(f"שגיאה בניתוח יחסי לשוק משופר: {str(e)}")
            return {
                "performance_20d": 0,
                "performance_50d": 0,
                "volatility": 0,
                "trend_strength": 50,
                "performance_score": 50,
                "volatility_score": 50,
                "trend_score": 50,
                "relative_bonus": 0,
                "overall_score": 50
            }

    def _analyze_complex_patterns(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח תבניות מורכבות (זהה לקודם)"""
        patterns = {
            "cup_and_handle": self._detect_advanced_cup_handle(price_df),
            "bull_flag": self._detect_advanced_bull_flag(price_df),
            "falling_wedge": self._detect_falling_wedge(price_df),
            "channel_breakout": self._detect_channel_breakout(price_df),
            "consolidation_breakout": self._detect_consolidation_breakout(price_df)
        }
        
        detected_patterns = [p for p in patterns.values() if p.get('detected', False)]
        total_strength = sum(p.get('strength', 0) for p in detected_patterns)
        
        return {
            "individual_patterns": patterns,
            "detected_count": len(detected_patterns),
            "total_strength": total_strength,
            "average_strength": total_strength / max(len(detected_patterns), 1),
            "pattern_quality": self._calculate_pattern_quality(patterns)
        }

    def _detect_advanced_cup_handle(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי מתקדם של Cup & Handle"""
        if len(price_df) < 60:
            return {"detected": False, "strength": 0}
        
        close_prices = price_df['close'].tail(60)
        volume = price_df['volume'].tail(60)
        
        cup_length = int(60 * 0.7)
        handle_length = 60 - cup_length
        
        cup_prices = close_prices[:cup_length]
        handle_prices = close_prices[cup_length:]
        
        cup_start = cup_prices.iloc[0]
        cup_end = cup_prices.iloc[-1]
        
        left_cup = cup_prices[:len(cup_prices)//2]
        right_cup = cup_prices[len(cup_prices)//2:]
        
        left_min = left_cup.min()
        right_min = right_cup.min()
        
        symmetry_score = 1 - abs(left_min - right_min) / max(left_min, right_min)
        cup_symmetry = symmetry_score > 0.8
        
        cup_rounded = self._check_rounded_bottom(cup_prices)
        
        handle_decline = (handle_prices.iloc[0] - handle_prices.min()) / handle_prices.iloc[0]
        handle_quality = handle_decline < 0.15 and len(handle_prices) >= 5
        
        cup_volume_pattern = self._analyze_cup_volume_pattern(volume[:cup_length])
        handle_volume_pattern = self._analyze_handle_volume_pattern(volume[cup_length:])
        
        is_cup_handle = cup_symmetry and cup_rounded and handle_quality and cup_volume_pattern['valid']
        
        strength = 0
        if is_cup_handle:
            symmetry_weight = symmetry_score * 30
            rounded_weight = 25 if cup_rounded else 0
            handle_weight = (1 - handle_decline) * 20
            volume_weight = (cup_volume_pattern['score'] + handle_volume_pattern['score']) / 2 * 25
            strength = symmetry_weight + rounded_weight + handle_weight + volume_weight
        
        return {
            "detected": is_cup_handle,
            "strength": strength,
            "symmetry_score": symmetry_score,
            "cup_rounded": cup_rounded,
            "handle_decline": handle_decline
        }

    def _check_rounded_bottom(self, prices: pd.Series) -> bool:
        """בדיקה אם התחתית מעוגלת"""
        if len(prices) < 10:
            return False
        
        min_idx = prices.idxmin()
        min_val = prices.min()
        
        window = 5
        start_idx = max(0, prices.index.get_loc(min_idx) - window)
        end_idx = min(len(prices), prices.index.get_loc(min_idx) + window)
        
        bottom_prices = prices.iloc[start_idx:end_idx]
        
        deviations = []
        for i, price in enumerate(bottom_prices):
            expected_round = min_val + (i - len(bottom_prices)//2)**2 * 0.001
            deviation = abs(price - expected_round) / min_val
            deviations.append(deviation)
        
        avg_deviation = np.mean(deviations)
        return avg_deviation < 0.02

    def _analyze_cup_volume_pattern(self, volume: pd.Series) -> Dict:
        """ניתוח תבנית נפח ב-Cup"""
        if len(volume) < 10:
            return {"valid": False, "score": 0}
        
        first_quarter = volume[:len(volume)//4].mean()
        last_quarter = volume[-len(volume)//4:].mean()
        middle = volume[len(volume)//4:-len(volume)//4].mean()
        
        volume_pattern = first_quarter > middle and last_quarter > middle
        volume_ratio = (first_quarter + last_quarter) / (2 * middle)
        
        score = min(100, volume_ratio * 50) if volume_pattern else 0
        
        return {
            "valid": volume_pattern,
            "score": score,
            "volume_ratio": volume_ratio
        }

    def _analyze_handle_volume_pattern(self, volume: pd.Series) -> Dict:
        """ניתוח תבנית נפח ב-Handle"""
        if len(volume) < 5:
            return {"valid": False, "score": 0}
        
        volume_decline = volume.iloc[0] / volume.mean()
        valid_pattern = volume_decline < 0.8
        
        score = max(0, (1 - volume_decline) * 100) if valid_pattern else 0
        
        return {
            "valid": valid_pattern,
            "score": score,
            "volume_decline": volume_decline
        }

    def _detect_advanced_bull_flag(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי מתקדם של Bull Flag"""
        if len(price_df) < 30:
            return {"detected": False, "strength": 0}
        
        close_prices = price_df['close'].tail(30)
        volume = price_df['volume'].tail(30)
        
        pole_length = int(30 * 0.3)
        flag_length = 30 - pole_length
        
        pole_prices = close_prices[:pole_length]
        flag_prices = close_prices[pole_length:]
        pole_volume = volume[:pole_length]
        flag_volume = volume[pole_length:]
        
        pole_rise = (pole_prices.iloc[-1] - pole_prices.iloc[0]) / pole_prices.iloc[0]
        pole_consistency = self._check_pole_consistency(pole_prices)
        pole_volume_quality = pole_volume.mean() > volume.mean() * 1.5
        
        flag_quality = self._check_flag_quality(flag_prices, flag_volume)
        
        is_bull_flag = pole_rise > 0.1 and pole_consistency and pole_volume_quality and flag_quality['valid']
        
        strength = 0
        if is_bull_flag:
            pole_score = min(100, pole_rise * 300)
            consistency_score = pole_consistency * 30
            volume_score = min(100, (pole_volume.mean() / volume.mean()) * 30)
            flag_score = flag_quality['score']
            strength = (pole_score + consistency_score + volume_score + flag_score) / 4
        
        return {
            "detected": is_bull_flag,
            "strength": strength,
            "pole_rise": pole_rise,
            "pole_consistency": pole_consistency,
            "flag_quality": flag_quality
        }

    def _check_pole_consistency(self, prices: pd.Series) -> float:
        """בדיקת עקביות ה-Pole"""
        if len(prices) < 5:
            return 0
        
        rises = []
        for i in range(1, len(prices)):
            rise = (prices.iloc[i] - prices.iloc[i-1]) / prices.iloc[i-1]
            rises.append(rise)
        
        positive_rises = sum(1 for r in rises if r > 0)
        consistency = positive_rises / len(rises)
        
        return consistency

    def _check_flag_quality(self, prices: pd.Series, volume: pd.Series) -> Dict:
        """בדיקת איכות ה-Flag"""
        if len(prices) < 5:
            return {"valid": False, "score": 0}
        
        flag_decline = (prices.iloc[0] - prices.min()) / prices.iloc[0]
        volume_decline = volume.mean() / volume.iloc[0] if volume.iloc[0] > 0 else 1
        
        valid_flag = flag_decline < 0.1 and volume_decline < 0.8
        
        score = max(0, (1 - flag_decline) * 50 + (1 - volume_decline) * 50) if valid_flag else 0
        
        return {
            "valid": valid_flag,
            "score": score,
            "flag_decline": flag_decline,
            "volume_decline": volume_decline
        }

    def _detect_falling_wedge(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי תבנית Falling Wedge"""
        if len(price_df) < 20:
            return {"detected": False, "strength": 0}
        
        close_prices = price_df['close'].tail(20)
        high_prices = price_df['high'].tail(20)
        low_prices = price_df['low'].tail(20)
        
        highs = high_prices.rolling(3).max()
        lows = low_prices.rolling(3).min()
        
        high_trend = np.polyfit(range(len(highs)), highs, 1)[0]
        low_trend = np.polyfit(range(len(lows)), lows, 1)[0]
        
        is_falling_wedge = high_trend < low_trend and low_trend < 0
        
        strength = 0
        if is_falling_wedge:
            convergence_strength = abs(high_trend - low_trend)
            strength = min(100, convergence_strength * 5000)
        
        return {
            "detected": is_falling_wedge,
            "strength": strength,
            "high_trend": high_trend,
            "low_trend": low_trend
        }

    def _detect_channel_breakout(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי פריצה מתעלה"""
        if len(price_df) < 30:
            return {"detected": False, "strength": 0}
        
        close_prices = price_df['close'].tail(30)
        high_prices = price_df['high'].tail(30)
        low_prices = price_df['low'].tail(30)
        
        channel_high = high_prices.rolling(5).max()
        channel_low = low_prices.rolling(5).min()
        
        in_channel = all(
            channel_low.iloc[i] <= close_prices.iloc[i] <= channel_high.iloc[i]
            for i in range(len(close_prices)-5, len(close_prices)-1)
        )
        
        current_price = close_prices.iloc[-1]
        current_channel_high = channel_high.iloc[-1]
        
        breakout = current_price > current_channel_high * 1.02
        
        is_channel_breakout = in_channel and breakout
        
        strength = 0
        if is_channel_breakout:
            breakout_strength = (current_price - current_channel_high) / current_channel_high
            strength = min(100, breakout_strength * 200)
        
        return {
            "detected": is_channel_breakout,
            "strength": strength,
            "breakout_strength": (current_price - current_channel_high) / current_channel_high if breakout else 0
        }

    def _detect_consolidation_breakout(self, price_df: pd.DataFrame) -> Dict:
        """זיהוי פריצה מקונסולידציה"""
        if len(price_df) < 20:
            return {"detected": False, "strength": 0}
        
        close_prices = price_df['close'].tail(20)
        high_prices = price_df['high'].tail(20)
        low_prices = price_df['low'].tail(20)
        
        price_range = (high_prices.max() - low_prices.min()) / low_prices.min()
        is_consolidation = price_range < 0.1
        
        current_price = close_prices.iloc[-1]
        consolidation_high = high_prices.max()
        consolidation_low = low_prices.min()
        
        breakout_up = current_price > consolidation_high * 1.01
        breakout_down = current_price < consolidation_low * 0.99
        
        is_breakout = is_consolidation and (breakout_up or breakout_down)
        
        strength = 0
        if is_breakout:
            if breakout_up:
                breakout_strength = (current_price - consolidation_high) / consolidation_high
            else:
                breakout_strength = (consolidation_low - current_price) / consolidation_low
            strength = min(100, breakout_strength * 300)
        
        return {
            "detected": is_breakout,
            "strength": strength,
            "consolidation_range": price_range,
            "breakout_direction": "up" if breakout_up else "down" if breakout_down else "none"
        }

    def _analyze_advanced_volume_patterns(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח תבניות נפח מתקדמות"""
        volume = price_df["volume"]
        close_prices = price_df["close"]
        
        current_volume = volume.iloc[-1]
        avg_volume = volume.rolling(20).mean().iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        volume_patterns = {
            "volume_surge": volume_ratio > 2,
            "volume_climax": self._detect_volume_climax(volume),
            "volume_divergence": self._detect_volume_divergence(close_prices, volume),
            "accumulation": self._detect_accumulation(close_prices, volume)
        }
        
        obv = (np.sign(close_prices.diff()) * volume).cumsum()
        obv_trend = "עולה" if obv.iloc[-1] > obv.iloc[-5] else "יורד"
        
        vpt = ((close_prices - close_prices.shift(1)) / close_prices.shift(1) * volume).cumsum()
        vpt_trend = "עולה" if vpt.iloc[-1] > vpt.iloc[-5] else "יורד"
        
        pattern_score = sum(volume_patterns.values()) * 25
        obv_score = 50 if obv_trend == "עולה" else 0
        vpt_score = 50 if vpt_trend == "עולה" else 0
        
        overall_score = (pattern_score + obv_score + vpt_score) / 3
        
        return {
            "current_volume": current_volume,
            "avg_volume": avg_volume,
            "volume_ratio": volume_ratio,
            "volume_patterns": volume_patterns,
            "obv_trend": obv_trend,
            "vpt_trend": vpt_trend,
            "overall_score": overall_score
        }

    def _detect_volume_climax(self, volume: pd.Series) -> bool:
        """זיהוי שיא נפח"""
        if len(volume) < 10:
            return False
        
        current_volume = volume.iloc[-1]
        recent_avg = volume.tail(10).mean()
        
        return current_volume > recent_avg * 2

    def _detect_volume_divergence(self, prices: pd.Series, volume: pd.Series) -> bool:
        """זיהוי אי התאמה בין מחיר לנפח"""
        if len(prices) < 10:
            return False
        
        price_trend = prices.iloc[-1] > prices.iloc[-5]
        volume_trend = volume.iloc[-1] < volume.iloc[-5]
        
        return price_trend and volume_trend

    def _detect_accumulation(self, prices: pd.Series, volume: pd.Series) -> bool:
        """זיהוי הצטברות"""
        if len(prices) < 20:
            return False
        
        recent_prices = prices.tail(10)
        recent_volume = volume.tail(10)
        
        low_price_periods = recent_prices < recent_prices.median()
        high_volume_periods = recent_volume > recent_volume.median()
        
        accumulation_score = sum(low_price_periods & high_volume_periods) / len(recent_prices)
        
        return accumulation_score > 0.6

    def _analyze_advanced_trends(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח מגמות מתקדם"""
        close_prices = price_df['close']
        
        trends = {
            "short_term": self._calculate_trend(close_prices.tail(10)),
            "medium_term": self._calculate_trend(close_prices.tail(20)),
            "long_term": self._calculate_trend(close_prices.tail(50)) if len(close_prices) >= 50 else 0
        }
        
        trend_consistency = self._calculate_trend_consistency(trends)
        trend_strength = self._calculate_trend_strength(close_prices)
        
        return {
            "trends": trends,
            "consistency": trend_consistency,
            "strength": trend_strength,
            "overall_trend": "עולה" if trend_consistency > 0.6 else "יורד" if trend_consistency < -0.6 else "מעורב"
        }

    def _calculate_trend(self, prices: pd.Series) -> float:
        """חישוב מגמה"""
        if len(prices) < 2:
            return 0
        
        x = np.arange(len(prices))
        slope = np.polyfit(x, prices, 1)[0]
        
        return slope / prices.mean()

    def _calculate_trend_consistency(self, trends: Dict) -> float:
        """חישוב עקביות מגמה"""
        values = list(trends.values())
        if not values:
            return 0
        
        positive_trends = sum(1 for v in values if v > 0)
        negative_trends = sum(1 for v in values if v < 0)
        
        if positive_trends == len(values):
            return 1.0
        elif negative_trends == len(values):
            return -1.0
        else:
            return 0.0

    def _calculate_trend_strength(self, prices: pd.Series) -> float:
        """חישוב חוזק מגמה"""
        if len(prices) < 20:
            return 0
        
        x = np.arange(len(prices))
        slope, intercept = np.polyfit(x, prices, 1)
        y_pred = slope * x + intercept
        
        ss_res = np.sum((prices - y_pred) ** 2)
        ss_tot = np.sum((prices - prices.mean()) ** 2)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return r_squared * 100

    def _analyze_support_resistance(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח תמיכה והתנגדות"""
        high_prices = price_df['high']
        low_prices = price_df['low']
        close_prices = price_df['close']
        
        resistance_levels = self._find_resistance_levels(high_prices)
        support_levels = self._find_support_levels(low_prices)
        
        current_price = close_prices.iloc[-1]
        
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price)) if resistance_levels else current_price
        resistance_distance = (nearest_resistance - current_price) / current_price
        
        nearest_support = min(support_levels, key=lambda x: abs(x - current_price)) if support_levels else current_price
        support_distance = (current_price - nearest_support) / current_price
        
        return {
            "resistance_levels": resistance_levels,
            "support_levels": support_levels,
            "nearest_resistance": nearest_resistance,
            "nearest_support": nearest_support,
            "resistance_distance": resistance_distance,
            "support_distance": support_distance,
            "position": "near_resistance" if resistance_distance < 0.05 else "near_support" if support_distance < 0.05 else "middle"
        }

    def _find_resistance_levels(self, high_prices: pd.Series) -> List[float]:
        """מציאת רמות התנגדות"""
        levels = []
        
        for i in range(2, len(high_prices) - 2):
            if (high_prices.iloc[i] >= high_prices.iloc[i-1] and 
                high_prices.iloc[i] >= high_prices.iloc[i-2] and
                high_prices.iloc[i] >= high_prices.iloc[i+1] and
                high_prices.iloc[i] >= high_prices.iloc[i+2]):
                levels.append(high_prices.iloc[i])
        
        unique_levels = list(set(levels))
        unique_levels.sort()
        
        return unique_levels

    def _find_support_levels(self, low_prices: pd.Series) -> List[float]:
        """מציאת רמות תמיכה"""
        levels = []
        
        for i in range(2, len(low_prices) - 2):
            if (low_prices.iloc[i] <= low_prices.iloc[i-1] and 
                low_prices.iloc[i] <= low_prices.iloc[i-2] and
                low_prices.iloc[i] <= low_prices.iloc[i+1] and
                low_prices.iloc[i] <= low_prices.iloc[i+2]):
                levels.append(low_prices.iloc[i])
        
        unique_levels = list(set(levels))
        unique_levels.sort()
        
        return unique_levels

    def _calculate_pattern_quality(self, patterns: Dict) -> float:
        """חישוב איכות התבניות"""
        detected_patterns = [p for p in patterns.values() if p.get('detected', False)]
        
        if not detected_patterns:
            return 0
        
        strengths = [p.get('strength', 0) for p in detected_patterns]
        avg_strength = np.mean(strengths)
        
        pattern_bonus = min(20, len(detected_patterns) * 5)
        
        return min(100, avg_strength + pattern_bonus)

    def _calculate_enhanced_score(self, complex_patterns: Dict, market_analysis: Dict, volume_analysis: Dict, trend_analysis: Dict, support_resistance: Dict, market_sentiment: Dict) -> int:
        """חישוב ציון משופר עם סנטימנט השוק"""
        # משקלים
        pattern_weight = 0.25
        market_weight = 0.25
        volume_weight = 0.15
        trend_weight = 0.15
        support_weight = 0.05
        sentiment_weight = 0.15
        
        # ציונים
        pattern_score = complex_patterns.get('pattern_quality', 0)
        market_score = market_analysis.get('overall_score', 50)
        volume_score = volume_analysis.get('overall_score', 50)
        trend_score = trend_analysis.get('strength', 50)
        
        # ציון תמיכה/התנגדות
        support_score = 50
        position = support_resistance.get('position', 'middle')
        if position == 'near_support':
            support_score = 80
        elif position == 'near_resistance':
            support_score = 20
        
        # ציון סנטימנט
        sentiment_score = 50
        vix_sentiment = market_sentiment.get('vix_sentiment', 'ניטרלי')
        market_trend = market_sentiment.get('market_trend', 'ניטרלי')
        
        if vix_sentiment == 'פחד' and market_trend == 'ברישי':
            sentiment_score = 20
        elif vix_sentiment == 'תאוות בצע' and market_trend == 'בולשי':
            sentiment_score = 80
        elif vix_sentiment == 'ניטרלי' and market_trend == 'מעורב':
            sentiment_score = 50
        else:
            sentiment_score = 40
        
        # חישוב סופי
        final_score = int(
            pattern_score * pattern_weight +
            market_score * market_weight +
            volume_score * volume_weight +
            trend_score * trend_weight +
            support_score * support_weight +
            sentiment_score * sentiment_weight
        )
        
        return max(1, min(100, final_score))

    def _generate_enhanced_summary(self, complex_patterns: Dict, market_analysis: Dict, volume_analysis: Dict, trend_analysis: Dict, support_resistance: Dict, market_sentiment: Dict) -> str:
        """יצירת סיכום משופר"""
        summary_parts = []
        
        # תבניות מורכבות
        detected_patterns = []
        for pattern_name, pattern_data in complex_patterns.get('individual_patterns', {}).items():
            if pattern_data.get('detected', False):
                detected_patterns.append(pattern_name.replace('_', ' '))
        
        if detected_patterns:
            summary_parts.append(f"תבניות מורכבות: {', '.join(detected_patterns)}")
        
        # ניתוח שוק
        performance = market_analysis.get('performance_20d', 0)
        summary_parts.append(f"ביצועים יחסיים: {performance:+.1f}%")
        
        # מגמה
        trend = trend_analysis.get('overall_trend', 'לא ידוע')
        summary_parts.append(f"מגמה: {trend}")
        
        # נפח
        volume_ratio = volume_analysis.get('volume_ratio', 1)
        summary_parts.append(f"יחס נפח: {volume_ratio:.2f}")
        
        # תמיכה/התנגדות
        position = support_resistance.get('position', 'middle')
        if position == 'near_resistance':
            summary_parts.append("קרוב להתנגדות")
        elif position == 'near_support':
            summary_parts.append("קרוב לתמיכה")
        
        # סנטימנט
        vix_sentiment = market_sentiment.get('vix_sentiment', 'לא ידוע')
        summary_parts.append(f"סנטימנט VIX: {vix_sentiment}")
        
        return ". ".join(summary_parts)

    def _generate_enhanced_recommendations(self, complex_patterns: Dict, market_analysis: Dict, volume_analysis: Dict, trend_analysis: Dict, support_resistance: Dict, market_sentiment: Dict) -> List[str]:
        """יצירת המלצות משופרות"""
        recommendations = []
        
        # המלצות על בסיס תבניות
        detected_patterns = []
        for pattern_name, pattern_data in complex_patterns.get('individual_patterns', {}).items():
            if pattern_data.get('detected', False):
                detected_patterns.append(pattern_name)
        
        if "cup_and_handle" in detected_patterns:
            recommendations.append("תבנית Cup & Handle - סיגנל קנייה חזק לטווח ארוך")
        if "bull_flag" in detected_patterns:
            recommendations.append("תבנית Bull Flag - המשך עלייה צפוי")
        if "falling_wedge" in detected_patterns:
            recommendations.append("תבנית Falling Wedge - היפוך מגמה צפוי")
        if "channel_breakout" in detected_patterns:
            recommendations.append("פריצה מתעלה - עלייה חזקה צפויה")
        
        # המלצות על בסיס ביצועים
        performance = market_analysis.get('performance_20d', 0)
        if performance > 10:
            recommendations.append("ביצועים מעולים - המשך עלייה צפוי")
        elif performance < -10:
            recommendations.append("ביצועים גרועים - זהירות")
        
        # המלצות על בסיס מגמה
        trend = trend_analysis.get('overall_trend', '')
        if trend == 'עולה':
            recommendations.append("מגמה עולה - המשך קנייה")
        elif trend == 'יורד':
            recommendations.append("מגמה יורדת - זהירות")
        
        # המלצות על בסיס תמיכה/התנגדות
        position = support_resistance.get('position', '')
        if position == 'near_resistance':
            recommendations.append("קרוב להתנגדות - זהירות מפריצה")
        elif position == 'near_support':
            recommendations.append("קרוב לתמיכה - הזדמנות קנייה")
        
        # המלצות על בסיס סנטימנט
        vix_sentiment = market_sentiment.get('vix_sentiment', '')
        if vix_sentiment == 'פחד':
            recommendations.append("סנטימנט פחד - הזדמנות קנייה")
        elif vix_sentiment == 'תאוות בצע':
            recommendations.append("סנטימנט תאוות בצע - זהירות")
        
        if not recommendations:
            recommendations.append("שמור על עמדה נוכחית - אין סיגנלים חזקים")
        
        return recommendations

    def _get_dummy_result(self, message: str) -> Dict:
        """תוצאה ריקה במקרה של שגיאה"""
        return {
            "score": 50,
            "explanation": message,
            "details": {
                "complex_patterns": {"detected_count": 0, "total_strength": 0},
                "market_analysis": {"overall_score": 50},
                "volume_analysis": {"overall_score": 50},
                "trend_analysis": {"strength": 50},
                "support_resistance": {"position": "middle"},
                "market_sentiment": {"vix_sentiment": "לא ידוע", "market_trend": "לא ידוע"},
                "recommendations": ["אין מספיק נתונים לניתוח"]
            },
            "timestamp": datetime.now().isoformat()
        } 