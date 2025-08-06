"""
Short Interest Spike Agent - זיהוי קפיצות בשורט אינטרסט
=======================================================

סוכן המזהה קפיצות בשורט אינטרסט ומזהה הזדמנויות Short Squeeze.
מבוסס על ניתוח נתוני שורט אינטרסט, תבניות נפח ותנועות מחיר.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from core.base.base_agent import BaseAgent
from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("ShortInterestSpikeAgent")

class ShortInterestSpikeAgent(BaseAgent):
    """
    סוכן לזיהוי קפיצות בשורט אינטרסט
    """
    
    def __init__(self, config=None):
        """
        אתחול הסוכן
        """
        super().__init__(config)
        self.name = "Short Interest Spike Agent"
        self.version = "1.0.0"
        self.description = "מזהה קפיצות בשורט אינטרסט וזיהוי הזדמנויות Short Squeeze"
        
        # פרמטרים לניתוח
        self.short_interest_threshold = 0.15  # 15% שינוי בשורט אינטרסט
        self.volume_spike_threshold = 2.0  # נפח 2x מהממוצע
        self.price_momentum_threshold = 0.05  # 5% מומנטום מחיר
        self.days_to_cover_threshold = 5.0  # ימי כיסוי מינימליים
        self.correlation_threshold = 0.7  # קורלציה מינימלית
        
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def analyze(self, symbol: str, price_df: pd.DataFrame,
                short_interest_data: pd.DataFrame = None,
                volume_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח קפיצות בשורט אינטרסט
        
        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            short_interest_data: נתוני שורט אינטרסט
            volume_data: נתוני נפח
            
        Returns:
            תוצאות הניתוח
        """
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=90)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            logger.info(f"Starting analysis for {symbol}")
            
            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")
            
            if not validate_stock_data(price_df):
                return self._create_error_result("Invalid price data")
            
            # ניתוח קפיצות שורט אינטרסט
            short_interest_analysis = self._analyze_short_interest_spikes(
                short_interest_data
            )
            
            # ניתוח תבניות נפח
            volume_analysis = self._analyze_volume_patterns(
                price_df, volume_data
            )
            
            # ניתוח מומנטום מחיר
            price_analysis = self._analyze_price_momentum(price_df)
            
            # ניתוח ימי כיסוי
            days_to_cover_analysis = self._analyze_days_to_cover(
                short_interest_data, volume_data
            )
            
            # ניתוח קורלציה
            correlation_analysis = self._analyze_correlation(
                price_df, short_interest_data, volume_data
            )
            
            # חישוב ציון כללי
            score = self._calculate_short_interest_score(
                short_interest_analysis,
                volume_analysis,
                price_analysis,
                days_to_cover_analysis,
                correlation_analysis
            )
            
            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)
            
            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)
            
            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                short_interest_analysis,
                volume_analysis,
                price_analysis,
                days_to_cover_analysis,
                correlation_analysis
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
                    "short_interest_spikes": short_interest_analysis,
                    "volume_patterns": volume_analysis,
                    "price_momentum": price_analysis,
                    "days_to_cover": days_to_cover_analysis,
                    "correlation": correlation_analysis
                },
                "metadata": {
                    "short_interest_threshold": self.short_interest_threshold,
                    "volume_spike_threshold": self.volume_spike_threshold,
                    "price_momentum_threshold": self.price_momentum_threshold,
                    "days_to_cover_threshold": self.days_to_cover_threshold,
                    "correlation_threshold": self.correlation_threshold
                }
            }
            
            logger.info(f"Analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()
    
    def _analyze_short_interest_spikes(self, short_interest_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח קפיצות בשורט אינטרסט"""
        try:
            if short_interest_data is None or short_interest_data.empty:
                return {
                    "has_data": False,
                    "spike_detected": False,
                    "change_percentage": 0.0,
                    "current_short_interest": 0.0,
                    "previous_short_interest": 0.0,
                    "spike_magnitude": 0.0
                }
            
            # חישוב שינוי בשורט אינטרסט
            if len(short_interest_data) >= 2:
                current_si = short_interest_data.iloc[-1]['short_interest']
                previous_si = short_interest_data.iloc[-2]['short_interest']
                
                change_pct = ((current_si - previous_si) / previous_si) * 100
                spike_magnitude = abs(change_pct)
                
                spike_detected = spike_magnitude > (self.short_interest_threshold * 100)
                
                return {
                    "has_data": True,
                    "spike_detected": spike_detected,
                    "change_percentage": change_pct,
                    "current_short_interest": current_si,
                    "previous_short_interest": previous_si,
                    "spike_magnitude": spike_magnitude,
                    "threshold_exceeded": spike_detected
                }
            else:
                return {
                    "has_data": True,
                    "spike_detected": False,
                    "change_percentage": 0.0,
                    "current_short_interest": short_interest_data.iloc[-1]['short_interest'],
                    "previous_short_interest": 0.0,
                    "spike_magnitude": 0.0
                }
                
        except Exception as e:
            logger.error(f"Error analyzing short interest spikes: {str(e)}")
            return {
                "has_data": False,
                "spike_detected": False,
                "error": str(e)
            }
    
    def _analyze_volume_patterns(self, price_df: pd.DataFrame,
                                volume_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח תבניות נפח"""
        try:
            volume_series = volume_data['volume'] if volume_data is not None else price_df['volume']
            
            # חישוב ממוצע נפח
            avg_volume = volume_series.rolling(window=20).mean()
            current_volume = volume_series.iloc[-1]
            volume_ratio = current_volume / avg_volume.iloc[-1]
            
            # זיהוי קפיצות נפח
            volume_spike = volume_ratio > self.volume_spike_threshold
            
            # ניתוח מגמת נפח
            volume_trend = self._calculate_trend(volume_series.tail(10))
            
            return {
                "current_volume": current_volume,
                "average_volume": avg_volume.iloc[-1],
                "volume_ratio": volume_ratio,
                "volume_spike_detected": volume_spike,
                "volume_trend": volume_trend,
                "threshold_exceeded": volume_spike
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume patterns: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_price_momentum(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח מומנטום מחיר"""
        try:
            prices = price_df['close']
            
            # חישוב מומנטום
            momentum_5d = (prices.iloc[-1] - prices.iloc[-6]) / prices.iloc[-6]
            momentum_10d = (prices.iloc[-1] - prices.iloc[-11]) / prices.iloc[-11]
            
            # זיהוי מומנטום חיובי
            positive_momentum = momentum_5d > self.price_momentum_threshold
            
            # ניתוח תנודתיות
            volatility = prices.pct_change().std() * np.sqrt(252)
            
            return {
                "momentum_5d": momentum_5d,
                "momentum_10d": momentum_10d,
                "positive_momentum": positive_momentum,
                "volatility": volatility,
                "threshold_exceeded": positive_momentum
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price momentum: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_days_to_cover(self, short_interest_data: pd.DataFrame = None,
                              volume_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח ימי כיסוי"""
        try:
            if short_interest_data is None or volume_data is None:
                return {
                    "has_data": False,
                    "days_to_cover": 0.0,
                    "high_cover_days": False
                }
            
            current_si = short_interest_data.iloc[-1]['short_interest']
            avg_daily_volume = volume_data['volume'].rolling(window=20).mean().iloc[-1]
            
            days_to_cover = current_si / avg_daily_volume
            high_cover_days = days_to_cover > self.days_to_cover_threshold
            
            return {
                "has_data": True,
                "days_to_cover": days_to_cover,
                "high_cover_days": high_cover_days,
                "threshold_exceeded": high_cover_days
            }
            
        except Exception as e:
            logger.error(f"Error analyzing days to cover: {str(e)}")
            return {
                "has_data": False,
                "error": str(e)
            }
    
    def _analyze_correlation(self, price_df: pd.DataFrame,
                           short_interest_data: pd.DataFrame = None,
                           volume_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח קורלציה בין שורט אינטרסט למחיר"""
        try:
            if short_interest_data is None or len(short_interest_data) < 10:
                return {
                    "has_data": False,
                    "correlation": 0.0,
                    "strong_correlation": False
                }
            
            # התאמת נתונים לתקופה זהה
            common_dates = price_df.index.intersection(short_interest_data.index)
            if len(common_dates) < 10:
                return {
                    "has_data": False,
                    "correlation": 0.0,
                    "strong_correlation": False
                }
            
            price_series = price_df.loc[common_dates, 'close']
            si_series = short_interest_data.loc[common_dates, 'short_interest']
            
            # חישוב קורלציה
            correlation = price_series.corr(si_series)
            strong_correlation = abs(correlation) > self.correlation_threshold
            
            return {
                "has_data": True,
                "correlation": correlation,
                "strong_correlation": strong_correlation,
                "threshold_exceeded": strong_correlation
            }
            
        except Exception as e:
            logger.error(f"Error analyzing correlation: {str(e)}")
            return {
                "has_data": False,
                "error": str(e)
            }
    
    def _calculate_short_interest_score(self, short_interest_analysis: Dict,
                                       volume_analysis: Dict,
                                       price_analysis: Dict,
                                       days_to_cover_analysis: Dict,
                                       correlation_analysis: Dict) -> float:
        """חישוב ציון כללי"""
        try:
            score = 0.0
            max_score = 100.0
            
            # ציון קפיצת שורט אינטרסט (30 נקודות)
            if short_interest_analysis.get("spike_detected", False):
                spike_magnitude = short_interest_analysis.get("spike_magnitude", 0)
                score += min(30, (spike_magnitude / 50) * 30)
            
            # ציון קפיצת נפח (25 נקודות)
            if volume_analysis.get("volume_spike_detected", False):
                volume_ratio = volume_analysis.get("volume_ratio", 1.0)
                score += min(25, (volume_ratio / 3) * 25)
            
            # ציון מומנטום מחיר (20 נקודות)
            if price_analysis.get("positive_momentum", False):
                momentum = price_analysis.get("momentum_5d", 0)
                score += min(20, (momentum / 0.1) * 20)
            
            # ציון ימי כיסוי (15 נקודות)
            if days_to_cover_analysis.get("high_cover_days", False):
                days_to_cover = days_to_cover_analysis.get("days_to_cover", 0)
                score += min(15, (days_to_cover / 10) * 15)
            
            # ציון קורלציה (10 נקודות)
            if correlation_analysis.get("strong_correlation", False):
                correlation = abs(correlation_analysis.get("correlation", 0))
                score += min(10, (correlation / 0.8) * 10)
            
            return min(score, max_score)
            
        except Exception as e:
            logger.error(f"Error calculating score: {str(e)}")
            return 0.0
    
    def _determine_confidence_level(self, score: float) -> str:
        """קביעת רמת ביטחון"""
        if score >= 80:
            return "HIGH"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _generate_recommendation(self, score: float, confidence: str) -> str:
        """יצירת המלצה"""
        if score >= 80:
            return "STRONG_BUY - High probability of short squeeze"
        elif score >= 60:
            return "BUY - Potential short squeeze opportunity"
        elif score >= 40:
            return "WATCH - Monitor for short squeeze signals"
        else:
            return "HOLD - No significant short squeeze signals"
    
    def _extract_key_signals(self, short_interest_analysis: Dict,
                            volume_analysis: Dict,
                            price_analysis: Dict,
                            days_to_cover_analysis: Dict,
                            correlation_analysis: Dict) -> List[str]:
        """חילוץ אותות מפתח"""
        signals = []
        
        if short_interest_analysis.get("spike_detected", False):
            change_pct = short_interest_analysis.get("change_percentage", 0)
            signals.append(f"Short interest spike detected: {change_pct:.1f}% change")
        
        if volume_analysis.get("volume_spike_detected", False):
            volume_ratio = volume_analysis.get("volume_ratio", 1.0)
            signals.append(f"Volume spike: {volume_ratio:.1f}x average volume")
        
        if price_analysis.get("positive_momentum", False):
            momentum = price_analysis.get("momentum_5d", 0)
            signals.append(f"Positive price momentum: {momentum:.1%}")
        
        if days_to_cover_analysis.get("high_cover_days", False):
            days_to_cover = days_to_cover_analysis.get("days_to_cover", 0)
            signals.append(f"High days to cover: {days_to_cover:.1f} days")
        
        if correlation_analysis.get("strong_correlation", False):
            correlation = correlation_analysis.get("correlation", 0)
            signals.append(f"Strong price-SI correlation: {correlation:.2f}")
        
        return signals
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """חישוב מגמה"""
        try:
            if len(series) < 2:
                return "NEUTRAL"
            
            slope = np.polyfit(range(len(series)), series, 1)[0]
            
            if slope > 0.01:
                return "UP"
            elif slope < -0.01:
                return "DOWN"
            else:
                return "NEUTRAL"
                
        except Exception:
            return "NEUTRAL"
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """יצירת תוצאת שגיאה"""
        return {
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "version": self.version,
            "score": 0.0,
            "confidence": "ERROR",
            "recommendation": "ERROR",
            "key_signals": [f"Error: {error_message}"]
        }