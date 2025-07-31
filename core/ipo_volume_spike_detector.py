"""
IPO Volume Spike Detector - זיהוי קפיצות נפח ב-IPOs
====================================================

סוכן המזהה קפיצות נפח ב-IPOs ומניות חדשות ומזהה הזדמנויות מסחר.
מבוסס על ניתוח נפח מסחר בימי ה-IPO הראשונים ותבניות חריגות.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger()

class IPOVolumeSpikeDetector:
    """
    סוכן לזיהוי קפיצות נפח ב-IPOs
    """
    
    def __init__(self):
        """
        אתחול הסוכן
        """
        self.name = "IPO Volume Spike Detector"
        self.version = "1.0.0"
        self.description = "מזהה קפיצות נפח ב-IPOs ומניות חדשות"
        
        # פרמטרים לניתוח
        self.volume_spike_threshold = 2.5  # נפח 2.5x מהממוצע
        self.price_volatility_threshold = 0.3  # תנודתיות מחיר 30%
        self.ipo_age_threshold = 30  # גיל מקסימלי בימים לניתוח IPO
        self.volume_trend_threshold = 1.5  # מגמת נפח 1.5x מהממוצע
        self.price_momentum_threshold = 0.1  # מומנטום מחיר 10%
        self.relative_volume_threshold = 3.0  # נפח יחסי 3x מהשוק
        
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def analyze(self, symbol: str, price_df: pd.DataFrame,
                volume_data: pd.DataFrame = None,
                ipo_info: Dict = None,
                market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח קפיצות נפח ב-IPO
        
        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            volume_data: נתוני נפח
            ipo_info: מידע על ה-IPO
            market_data: נתוני שוק להשוואה
            
        Returns:
            תוצאות הניתוח
        """
        try:
            logger.info(f"Starting IPO volume spike analysis for {symbol}")
            
            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")
            
            if not validate_stock_data(price_df):
                return self._create_error_result("Invalid price data")
            
            # ניתוח נפח IPO
            volume_analysis = self._analyze_ipo_volume_patterns(
                price_df, volume_data, ipo_info
            )
            
            # ניתוח תנודתיות מחיר
            volatility_analysis = self._analyze_price_volatility(
                price_df, ipo_info
            )
            
            # ניתוח מגמות נפח
            volume_trend_analysis = self._analyze_volume_trends(
                price_df, volume_data
            )
            
            # ניתוח מומנטום מחיר
            momentum_analysis = self._analyze_price_momentum(price_df)
            
            # ניתוח נפח יחסי לשוק
            relative_volume_analysis = self._analyze_relative_volume(
                price_df, volume_data, market_data
            )
            
            # ניתוח תבניות מסחר
            trading_pattern_analysis = self._analyze_trading_patterns(
                price_df, volume_data, ipo_info
            )
            
            # חישוב ציון כללי
            score = self._calculate_ipo_volume_score(
                volume_analysis,
                volatility_analysis,
                volume_trend_analysis,
                momentum_analysis,
                relative_volume_analysis,
                trading_pattern_analysis
            )
            
            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)
            
            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)
            
            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                volume_analysis,
                volatility_analysis,
                volume_trend_analysis,
                momentum_analysis,
                relative_volume_analysis,
                trading_pattern_analysis
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
                    "ipo_volume_patterns": volume_analysis,
                    "price_volatility": volatility_analysis,
                    "volume_trends": volume_trend_analysis,
                    "price_momentum": momentum_analysis,
                    "relative_volume": relative_volume_analysis,
                    "trading_patterns": trading_pattern_analysis
                },
                "metadata": {
                    "volume_spike_threshold": self.volume_spike_threshold,
                    "price_volatility_threshold": self.price_volatility_threshold,
                    "ipo_age_threshold": self.ipo_age_threshold,
                    "volume_trend_threshold": self.volume_trend_threshold,
                    "price_momentum_threshold": self.price_momentum_threshold,
                    "relative_volume_threshold": self.relative_volume_threshold
                }
            }
            
            logger.info(f"IPO volume analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result
            
        except Exception as e:
            error_msg = f"Error analyzing IPO volume for {symbol}: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_ipo_volume_patterns(self, price_df: pd.DataFrame,
                                   volume_data: pd.DataFrame = None,
                                   ipo_info: Dict = None) -> Dict[str, Any]:
        """ניתוח תבניות נפח IPO"""
        try:
            volume_series = volume_data['volume'] if volume_data is not None else price_df['volume']
            
            # חישוב ממוצע נפח
            avg_volume = volume_series.rolling(window=5).mean()
            current_volume = volume_series.iloc[-1]
            volume_ratio = current_volume / avg_volume.iloc[-1]
            
            # זיהוי קפיצות נפח
            volume_spike = volume_ratio > self.volume_spike_threshold
            
            # ניתוח נפח יומי
            daily_volume_stats = self._calculate_daily_volume_stats(volume_series)
            
            # ניתוח נפח ביחס לגיל ה-IPO
            ipo_age_analysis = self._analyze_ipo_age_volume(
                volume_series, ipo_info
            )
            
            return {
                "current_volume": current_volume,
                "average_volume": avg_volume.iloc[-1],
                "volume_ratio": volume_ratio,
                "volume_spike_detected": volume_spike,
                "daily_volume_stats": daily_volume_stats,
                "ipo_age_analysis": ipo_age_analysis,
                "threshold_exceeded": volume_spike
            }
            
        except Exception as e:
            logger.error(f"Error analyzing IPO volume patterns: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_price_volatility(self, price_df: pd.DataFrame,
                                ipo_info: Dict = None) -> Dict[str, Any]:
        """ניתוח תנודתיות מחיר"""
        try:
            prices = price_df['close']
            
            # חישוב תנודתיות יומית
            daily_returns = prices.pct_change()
            volatility = daily_returns.std() * np.sqrt(252)
            
            # זיהוי תנודתיות גבוהה
            high_volatility = volatility > self.price_volatility_threshold
            
            # ניתוח תנודתיות ביחס לגיל ה-IPO
            ipo_volatility_analysis = self._analyze_ipo_age_volatility(
                prices, ipo_info
            )
            
            # ניתוח תנודתיות יחסית
            relative_volatility = self._calculate_relative_volatility(prices)
            
            return {
                "volatility": volatility,
                "high_volatility": high_volatility,
                "ipo_volatility_analysis": ipo_volatility_analysis,
                "relative_volatility": relative_volatility,
                "threshold_exceeded": high_volatility
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price volatility: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_volume_trends(self, price_df: pd.DataFrame,
                             volume_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח מגמות נפח"""
        try:
            volume_series = volume_data['volume'] if volume_data is not None else price_df['volume']
            
            # חישוב מגמת נפח
            volume_trend = self._calculate_volume_trend(volume_series)
            
            # ניתוח תבניות נפח
            volume_patterns = self._detect_volume_patterns(volume_series)
            
            # ניתוח נפח ביחס למחיר
            volume_price_correlation = self._analyze_volume_price_correlation(
                price_df['close'], volume_series
            )
            
            return {
                "volume_trend": volume_trend,
                "volume_patterns": volume_patterns,
                "volume_price_correlation": volume_price_correlation,
                "trending_volume": volume_trend > self.volume_trend_threshold
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume trends: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_price_momentum(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח מומנטום מחיר"""
        try:
            prices = price_df['close']
            
            # חישוב מומנטום
            momentum_1d = (prices.iloc[-1] - prices.iloc[-2]) / prices.iloc[-2]
            momentum_5d = (prices.iloc[-1] - prices.iloc[-6]) / prices.iloc[-6]
            momentum_10d = (prices.iloc[-1] - prices.iloc[-11]) / prices.iloc[-11]
            
            # זיהוי מומנטום חיובי
            positive_momentum = momentum_5d > self.price_momentum_threshold
            
            # ניתוח מגמת מומנטום
            momentum_trend = self._analyze_momentum_trend(prices)
            
            return {
                "momentum_1d": momentum_1d,
                "momentum_5d": momentum_5d,
                "momentum_10d": momentum_10d,
                "positive_momentum": positive_momentum,
                "momentum_trend": momentum_trend,
                "threshold_exceeded": positive_momentum
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price momentum: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_relative_volume(self, price_df: pd.DataFrame,
                               volume_data: pd.DataFrame = None,
                               market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח נפח יחסי לשוק"""
        try:
            if market_data is None:
                return {
                    "has_market_data": False,
                    "relative_volume": 1.0,
                    "high_relative_volume": False
                }
            
            stock_volume = volume_data['volume'] if volume_data is not None else price_df['volume']
            market_volume = market_data['volume']
            
            # חישוב נפח יחסי
            stock_avg_volume = stock_volume.rolling(window=5).mean().iloc[-1]
            market_avg_volume = market_volume.rolling(window=5).mean().iloc[-1]
            
            relative_volume = stock_avg_volume / market_avg_volume if market_avg_volume > 0 else 1.0
            high_relative_volume = relative_volume > self.relative_volume_threshold
            
            return {
                "has_market_data": True,
                "relative_volume": relative_volume,
                "high_relative_volume": high_relative_volume,
                "threshold_exceeded": high_relative_volume
            }
            
        except Exception as e:
            logger.error(f"Error analyzing relative volume: {str(e)}")
            return {
                "has_market_data": False,
                "error": str(e)
            }
    
    def _analyze_trading_patterns(self, price_df: pd.DataFrame,
                                volume_data: pd.DataFrame = None,
                                ipo_info: Dict = None) -> Dict[str, Any]:
        """ניתוח תבניות מסחר"""
        try:
            prices = price_df['close']
            volumes = volume_data['volume'] if volume_data is not None else price_df['volume']
            
            # זיהוי תבניות מסחר חשודות
            suspicious_patterns = self._detect_suspicious_trading_patterns(
                prices, volumes
            )
            
            # ניתוח תבניות זמן
            time_patterns = self._analyze_trading_time_patterns(price_df)
            
            # ניתוח תבניות נפח-מחיר
            volume_price_patterns = self._analyze_volume_price_patterns(
                prices, volumes
            )
            
            return {
                "suspicious_patterns": suspicious_patterns,
                "time_patterns": time_patterns,
                "volume_price_patterns": volume_price_patterns,
                "has_suspicious_patterns": len(suspicious_patterns) > 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trading patterns: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _calculate_ipo_volume_score(self, volume_analysis: Dict,
                                  volatility_analysis: Dict,
                                  volume_trend_analysis: Dict,
                                  momentum_analysis: Dict,
                                  relative_volume_analysis: Dict,
                                  trading_pattern_analysis: Dict) -> float:
        """חישוב ציון כללי"""
        try:
            score = 0.0
            max_score = 100.0
            
            # ציון קפיצת נפח (25 נקודות)
            if volume_analysis.get("volume_spike_detected", False):
                volume_ratio = volume_analysis.get("volume_ratio", 1.0)
                score += min(25, (volume_ratio / 4) * 25)
            
            # ציון תנודתיות (20 נקודות)
            if volatility_analysis.get("high_volatility", False):
                volatility = volatility_analysis.get("volatility", 0)
                score += min(20, (volatility / 0.5) * 20)
            
            # ציון מגמת נפח (20 נקודות)
            if volume_trend_analysis.get("trending_volume", False):
                volume_trend = volume_trend_analysis.get("volume_trend", 1.0)
                score += min(20, (volume_trend / 2) * 20)
            
            # ציון מומנטום מחיר (15 נקודות)
            if momentum_analysis.get("positive_momentum", False):
                momentum = momentum_analysis.get("momentum_5d", 0)
                score += min(15, (momentum / 0.2) * 15)
            
            # ציון נפח יחסי (15 נקודות)
            if relative_volume_analysis.get("high_relative_volume", False):
                relative_volume = relative_volume_analysis.get("relative_volume", 1.0)
                score += min(15, (relative_volume / 4) * 15)
            
            # ציון תבניות מסחר (5 נקודות)
            if trading_pattern_analysis.get("has_suspicious_patterns", False):
                score += 5
            
            return min(score, max_score)
            
        except Exception as e:
            logger.error(f"Error calculating IPO volume score: {str(e)}")
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
            return "STRONG_BUY - High IPO volume spike detected"
        elif score >= 60:
            return "BUY - Significant IPO volume activity"
        elif score >= 40:
            return "WATCH - Monitor IPO volume patterns"
        else:
            return "HOLD - No significant IPO volume signals"
    
    def _extract_key_signals(self, volume_analysis: Dict,
                            volatility_analysis: Dict,
                            volume_trend_analysis: Dict,
                            momentum_analysis: Dict,
                            relative_volume_analysis: Dict,
                            trading_pattern_analysis: Dict) -> List[str]:
        """חילוץ אותות מפתח"""
        signals = []
        
        if volume_analysis.get("volume_spike_detected", False):
            volume_ratio = volume_analysis.get("volume_ratio", 1.0)
            signals.append(f"IPO volume spike: {volume_ratio:.1f}x average")
        
        if volatility_analysis.get("high_volatility", False):
            volatility = volatility_analysis.get("volatility", 0)
            signals.append(f"High price volatility: {volatility:.1%}")
        
        if volume_trend_analysis.get("trending_volume", False):
            volume_trend = volume_trend_analysis.get("volume_trend", 1.0)
            signals.append(f"Strong volume trend: {volume_trend:.1f}x")
        
        if momentum_analysis.get("positive_momentum", False):
            momentum = momentum_analysis.get("momentum_5d", 0)
            signals.append(f"Positive price momentum: {momentum:.1%}")
        
        if relative_volume_analysis.get("high_relative_volume", False):
            relative_volume = relative_volume_analysis.get("relative_volume", 1.0)
            signals.append(f"High relative volume: {relative_volume:.1f}x market")
        
        if trading_pattern_analysis.get("has_suspicious_patterns", False):
            signals.append("Suspicious trading patterns detected")
        
        return signals
    
    def _calculate_daily_volume_stats(self, volume_series: pd.Series) -> Dict[str, Any]:
        """חישוב סטטיסטיקות נפח יומיות"""
        try:
            return {
                "mean": volume_series.mean(),
                "std": volume_series.std(),
                "max": volume_series.max(),
                "min": volume_series.min(),
                "current": volume_series.iloc[-1]
            }
        except Exception:
            return {}
    
    def _analyze_ipo_age_volume(self, volume_series: pd.Series,
                              ipo_info: Dict = None) -> Dict[str, Any]:
        """ניתוח נפח ביחס לגיל ה-IPO"""
        try:
            if not ipo_info:
                return {"has_ipo_info": False}
            
            ipo_date = ipo_info.get('ipo_date')
            if not ipo_date:
                return {"has_ipo_info": False}
            
            # חישוב גיל ה-IPO
            ipo_date = pd.to_datetime(ipo_date)
            current_date = pd.Timestamp.now()
            ipo_age_days = (current_date - ipo_date).days
            
            # ניתוח נפח לפי גיל
            if ipo_age_days <= self.ipo_age_threshold:
                recent_volume = volume_series.tail(5).mean()
                return {
                    "has_ipo_info": True,
                    "ipo_age_days": ipo_age_days,
                    "recent_volume": recent_volume,
                    "is_recent_ipo": ipo_age_days <= 30
                }
            else:
                return {
                    "has_ipo_info": True,
                    "ipo_age_days": ipo_age_days,
                    "is_recent_ipo": False
                }
                
        except Exception:
            return {"has_ipo_info": False}
    
    def _analyze_ipo_age_volatility(self, prices: pd.Series,
                                  ipo_info: Dict = None) -> Dict[str, Any]:
        """ניתוח תנודתיות ביחס לגיל ה-IPO"""
        try:
            if not ipo_info:
                return {"has_ipo_info": False}
            
            ipo_date = ipo_info.get('ipo_date')
            if not ipo_date:
                return {"has_ipo_info": False}
            
            # חישוב תנודתיות לפי גיל
            ipo_date = pd.to_datetime(ipo_date)
            current_date = pd.Timestamp.now()
            ipo_age_days = (current_date - ipo_date).days
            
            if ipo_age_days <= self.ipo_age_threshold:
                recent_volatility = prices.pct_change().tail(10).std() * np.sqrt(252)
                return {
                    "has_ipo_info": True,
                    "ipo_age_days": ipo_age_days,
                    "recent_volatility": recent_volatility,
                    "is_recent_ipo": ipo_age_days <= 30
                }
            else:
                return {
                    "has_ipo_info": True,
                    "ipo_age_days": ipo_age_days,
                    "is_recent_ipo": False
                }
                
        except Exception:
            return {"has_ipo_info": False}
    
    def _calculate_relative_volatility(self, prices: pd.Series) -> float:
        """חישוב תנודתיות יחסית"""
        try:
            # חישוב תנודתיות יחסית לתקופה
            volatility = prices.pct_change().std() * np.sqrt(252)
            avg_volatility = prices.pct_change().rolling(window=20).std().mean() * np.sqrt(252)
            
            return volatility / avg_volatility if avg_volatility > 0 else 1.0
            
        except Exception:
            return 1.0
    
    def _calculate_volume_trend(self, volume_series: pd.Series) -> float:
        """חישוב מגמת נפח"""
        try:
            if len(volume_series) < 5:
                return 1.0
            
            recent_avg = volume_series.tail(5).mean()
            previous_avg = volume_series.tail(10).head(5).mean()
            
            return recent_avg / previous_avg if previous_avg > 0 else 1.0
            
        except Exception:
            return 1.0
    
    def _detect_volume_patterns(self, volume_series: pd.Series) -> List[str]:
        """זיהוי תבניות נפח"""
        try:
            patterns = []
            
            # זיהוי תבניות בסיסיות
            if len(volume_series) >= 5:
                recent_volumes = volume_series.tail(5)
                
                # זיהוי מגמה עולה
                if recent_volumes.is_monotonic_increasing:
                    patterns.append("INCREASING_TREND")
                
                # זיהוי מגמה יורדת
                if recent_volumes.is_monotonic_decreasing:
                    patterns.append("DECREASING_TREND")
                
                # זיהוי תבנית V
                if recent_volumes.iloc[0] > recent_volumes.iloc[2] < recent_volumes.iloc[-1]:
                    patterns.append("V_PATTERN")
                
                # זיהוי תבנית הפוכה V
                if recent_volumes.iloc[0] < recent_volumes.iloc[2] > recent_volumes.iloc[-1]:
                    patterns.append("INVERTED_V_PATTERN")
            
            return patterns
            
        except Exception:
            return []
    
    def _analyze_volume_price_correlation(self, prices: pd.Series,
                                        volumes: pd.Series) -> float:
        """ניתוח קורלציה בין נפח למחיר"""
        try:
            return prices.corr(volumes)
        except Exception:
            return 0.0
    
    def _analyze_momentum_trend(self, prices: pd.Series) -> str:
        """ניתוח מגמת מומנטום"""
        try:
            if len(prices) < 10:
                return "NEUTRAL"
            
            momentum_5d = (prices.iloc[-1] - prices.iloc[-6]) / prices.iloc[-6]
            momentum_10d = (prices.iloc[-1] - prices.iloc[-11]) / prices.iloc[-11]
            
            if momentum_5d > 0.05 and momentum_10d > 0.05:
                return "STRONG_UP"
            elif momentum_5d > 0:
                return "UP"
            elif momentum_5d < -0.05 and momentum_10d < -0.05:
                return "STRONG_DOWN"
            elif momentum_5d < 0:
                return "DOWN"
            else:
                return "NEUTRAL"
                
        except Exception:
            return "NEUTRAL"
    
    def _detect_suspicious_trading_patterns(self, prices: pd.Series,
                                          volumes: pd.Series) -> List[str]:
        """זיהוי תבניות מסחר חשודות"""
        try:
            patterns = []
            
            if len(prices) < 5:
                return patterns
            
            # זיהוי תבניות חשודות
            recent_prices = prices.tail(5)
            recent_volumes = volumes.tail(5)
            
            # זיהוי קפיצות מחיר עם נפח נמוך
            price_changes = recent_prices.pct_change()
            volume_ratios = recent_volumes / recent_volumes.mean()
            
            for i in range(1, len(price_changes)):
                if abs(price_changes.iloc[i]) > 0.1 and volume_ratios.iloc[i] < 0.5:
                    patterns.append("LOW_VOLUME_PRICE_SPIKE")
            
            # זיהוי תבניות נפח חשודות
            if volume_ratios.max() > 5:
                patterns.append("EXTREME_VOLUME_SPIKE")
            
            return patterns
            
        except Exception:
            return []
    
    def _analyze_trading_time_patterns(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח תבניות זמן מסחר"""
        try:
            # ניתוח תבניות יומיות
            price_df['day_of_week'] = price_df.index.dayofweek
            daily_returns = price_df.groupby('day_of_week')['close'].pct_change().mean()
            
            # זיהוי ימים עם תנודתיות גבוהה
            high_volatility_days = daily_returns[daily_returns.abs() > 0.05]
            
            return {
                "high_volatility_days": list(high_volatility_days.index),
                "suspicious_timing": len(high_volatility_days) > 2
            }
            
        except Exception:
            return {"suspicious_timing": False}
    
    def _analyze_volume_price_patterns(self, prices: pd.Series,
                                     volumes: pd.Series) -> List[str]:
        """ניתוח תבניות נפח-מחיר"""
        try:
            patterns = []
            
            if len(prices) < 5:
                return patterns
            
            # זיהוי תבניות נפח-מחיר
            price_changes = prices.pct_change()
            volume_changes = volumes.pct_change()
            
            # זיהוי עליית מחיר עם נפח גבוה
            high_volume_up = (price_changes > 0.05) & (volume_changes > 1.0)
            if high_volume_up.any():
                patterns.append("HIGH_VOLUME_PRICE_UP")
            
            # זיהוי ירידת מחיר עם נפח גבוה
            high_volume_down = (price_changes < -0.05) & (volume_changes > 1.0)
            if high_volume_down.any():
                patterns.append("HIGH_VOLUME_PRICE_DOWN")
            
            return patterns
            
        except Exception:
            return []
    
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