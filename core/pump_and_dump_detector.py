"""
Pump and Dump Detector - זיהוי Pump & Dump
===========================================

סוכן המזהה תכניות Pump & Dump ומזהה פעילות מניפולטיבית בשוק.
מבוסס על ניתוח תבניות נפח, תנועות מחיר, פעילות רשתות חברתיות ואינדיקטורים למניפולציה.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import re

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("PumpAndDumpDetector")

class PumpAndDumpDetector:
    """
    סוכן לזיהוי Pump & Dump
    """
    
    def __init__(self):
        """
        אתחול הסוכן
        """
        self.name = "Pump and Dump Detector"
        self.version = "1.0.0"
        self.description = "מזהה תכניות Pump & Dump ופעילות מניפולטיבית בשוק"
        
        # מילות מפתח חשודות
        self.suspicious_keywords = [
            'moon', 'rocket', 'to the moon', '🚀', '💎', 'diamond hands',
            'hodl', 'hold', 'buy the dip', 'next tesla', 'next bitcoin',
            '100x', '1000x', 'millionaire', 'get rich quick', 'easy money',
            'guaranteed', 'sure thing', 'can\'t lose', 'next big thing',
            'pump', 'dump', 'manipulation', 'fake news', 'fud'
        ]
        
        # פרמטרים לניתוח
        self.volume_spike_threshold = 3.0  # נפח 3x מהממוצע
        self.price_spike_threshold = 0.15  # 15% קפיצת מחיר
        self.volatility_threshold = 0.5  # תנודתיות גבוהה
        self.social_activity_threshold = 5.0  # פעילות חברתית 5x מהממוצע
        self.news_sentiment_threshold = -0.3  # סנטימנט שלילי
        self.market_cap_threshold = 1000000000  # שווי שוק נמוך (1B)
        
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def analyze(self, symbol: str, price_df: pd.DataFrame,
                volume_data: pd.DataFrame = None,
                social_media_data: List[Dict] = None,
                news_data: List[Dict] = None,
                company_info: Dict = None) -> Dict[str, Any]:
        """
        ניתוח זיהוי Pump & Dump
        
        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            volume_data: נתוני נפח
            social_media_data: נתוני רשתות חברתיות
            news_data: נתוני חדשות
            company_info: מידע על החברה
            
        Returns:
            תוצאות הניתוח
        """
        try:
            logger.info(f"Starting pump and dump analysis for {symbol}")
            
            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")
            
            if not validate_stock_data(price_df):
                return self._create_error_result("Invalid price data")
            
            # ניתוח תבניות נפח חשודות
            volume_analysis = self._analyze_suspicious_volume_patterns(
                price_df, volume_data
            )
            
            # ניתוח תנועות מחיר חשודות
            price_analysis = self._analyze_suspicious_price_movements(price_df)
            
            # ניתוח פעילות רשתות חברתיות חשודה
            social_analysis = self._analyze_suspicious_social_activity(
                social_media_data
            )
            
            # ניתוח חדשות וסנטימנט
            news_analysis = self._analyze_news_sentiment(news_data)
            
            # ניתוח מאפיינים בסיסיים
            fundamental_analysis = self._analyze_fundamental_red_flags(
                company_info, price_df
            )
            
            # ניתוח תבניות מניפולטיביות
            manipulation_analysis = self._analyze_manipulation_patterns(
                price_df, volume_data, social_media_data
            )
            
            # חישוב ציון סיכון
            risk_score = self._calculate_pump_dump_risk_score(
                volume_analysis,
                price_analysis,
                social_analysis,
                news_analysis,
                fundamental_analysis,
                manipulation_analysis
            )
            
            # קביעת רמת סיכון
            risk_level = self._determine_risk_level(risk_score)
            
            # יצירת המלצה
            recommendation = self._generate_recommendation(risk_score, risk_level)
            
            # חילוץ אותות אזהרה
            warning_signals = self._extract_warning_signals(
                volume_analysis,
                price_analysis,
                social_analysis,
                news_analysis,
                fundamental_analysis,
                manipulation_analysis
            )
            
            result = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "version": self.version,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "recommendation": recommendation,
                "warning_signals": warning_signals,
                "analysis": {
                    "suspicious_volume": volume_analysis,
                    "suspicious_price": price_analysis,
                    "suspicious_social": social_analysis,
                    "news_sentiment": news_analysis,
                    "fundamental_red_flags": fundamental_analysis,
                    "manipulation_patterns": manipulation_analysis
                },
                "metadata": {
                    "volume_spike_threshold": self.volume_spike_threshold,
                    "price_spike_threshold": self.price_spike_threshold,
                    "volatility_threshold": self.volatility_threshold,
                    "social_activity_threshold": self.social_activity_threshold,
                    "news_sentiment_threshold": self.news_sentiment_threshold,
                    "market_cap_threshold": self.market_cap_threshold
                }
            }
            
            logger.info(f"Pump and dump analysis completed for {symbol} - Risk Score: {risk_score:.2f}, Risk Level: {risk_level}")
            return result
            
        except Exception as e:
            error_msg = f"Error analyzing pump and dump for {symbol}: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_suspicious_volume_patterns(self, price_df: pd.DataFrame,
                                          volume_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח תבניות נפח חשודות"""
        try:
            volume_series = volume_data['volume'] if volume_data is not None else price_df['volume']
            
            # חישוב ממוצע נפח
            avg_volume = volume_series.rolling(window=20).mean()
            current_volume = volume_series.iloc[-1]
            volume_ratio = current_volume / avg_volume.iloc[-1]
            
            # זיהוי קפיצות נפח חריגות
            extreme_volume_spike = volume_ratio > self.volume_spike_threshold
            
            # ניתוח תבניות נפח
            volume_patterns = self._detect_volume_patterns(volume_series)
            
            # ניתוח נפח ביחס למחיר
            volume_price_correlation = self._analyze_volume_price_correlation(
                price_df['close'], volume_series
            )
            
            return {
                "current_volume": current_volume,
                "average_volume": avg_volume.iloc[-1],
                "volume_ratio": volume_ratio,
                "extreme_volume_spike": extreme_volume_spike,
                "volume_patterns": volume_patterns,
                "volume_price_correlation": volume_price_correlation,
                "suspicious_pattern": extreme_volume_spike and volume_patterns.get("irregular", False)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing suspicious volume patterns: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_suspicious_price_movements(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח תנועות מחיר חשודות"""
        try:
            prices = price_df['close']
            
            # חישוב קפיצות מחיר
            price_changes = prices.pct_change()
            recent_price_change = price_changes.tail(5).sum()
            
            # זיהוי קפיצות חריגות
            extreme_price_spike = abs(recent_price_change) > self.price_spike_threshold
            
            # ניתוח תנודתיות
            volatility = prices.pct_change().std() * np.sqrt(252)
            high_volatility = volatility > self.volatility_threshold
            
            # ניתוח תבניות מחיר חשודות
            price_patterns = self._detect_suspicious_price_patterns(prices)
            
            # ניתוח מגמות מחיר
            price_trend = self._analyze_price_trend(prices)
            
            return {
                "recent_price_change": recent_price_change,
                "volatility": volatility,
                "extreme_price_spike": extreme_price_spike,
                "high_volatility": high_volatility,
                "price_patterns": price_patterns,
                "price_trend": price_trend,
                "suspicious_movement": extreme_price_spike or high_volatility
            }
            
        except Exception as e:
            logger.error(f"Error analyzing suspicious price movements: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_suspicious_social_activity(self, social_media_data: List[Dict] = None) -> Dict[str, Any]:
        """ניתוח פעילות רשתות חברתיות חשודה"""
        try:
            if not social_media_data:
                return {
                    "has_data": False,
                    "suspicious_posts": 0,
                    "suspicious_keywords_found": [],
                    "activity_spike": False
                }
            
            # סינון פוסטים חשודים
            suspicious_posts = []
            suspicious_keywords = []
            
            for post in social_media_data:
                content = post.get('content', '').lower()
                if self._contains_suspicious_keywords(content):
                    suspicious_posts.append(post)
                    # חילוץ מילות מפתח חשודות
                    found_keywords = [kw for kw in self.suspicious_keywords if kw.lower() in content]
                    suspicious_keywords.extend(found_keywords)
            
            # ניתוח קפיצת פעילות
            activity_spike = self._detect_activity_spike(social_media_data)
            
            # חישוב אחוז פוסטים חשודים
            suspicious_percentage = len(suspicious_posts) / len(social_media_data) if social_media_data else 0
            
            return {
                "has_data": True,
                "suspicious_posts": len(suspicious_posts),
                "suspicious_keywords_found": list(set(suspicious_keywords)),
                "suspicious_percentage": suspicious_percentage,
                "activity_spike": activity_spike,
                "high_suspicious_activity": suspicious_percentage > 0.3 or activity_spike
            }
            
        except Exception as e:
            logger.error(f"Error analyzing suspicious social activity: {str(e)}")
            return {
                "has_data": False,
                "error": str(e)
            }
    
    def _analyze_news_sentiment(self, news_data: List[Dict] = None) -> Dict[str, Any]:
        """ניתוח סנטימנט חדשות"""
        try:
            if not news_data:
                return {
                    "has_data": False,
                    "sentiment_score": 0.0,
                    "negative_news_count": 0,
                    "suspicious_news_count": 0
                }
            
            # חישוב סנטימנט ממוצע
            sentiment_scores = [news.get('sentiment', 0) for news in news_data]
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.0
            
            # ספירת חדשות שליליות
            negative_news = [news for news in news_data if news.get('sentiment', 0) < self.news_sentiment_threshold]
            
            # ספירת חדשות חשודות
            suspicious_news = [news for news in news_data 
                             if self._contains_suspicious_keywords(news.get('title', '') + ' ' + news.get('content', ''))]
            
            return {
                "has_data": True,
                "sentiment_score": avg_sentiment,
                "negative_news_count": len(negative_news),
                "suspicious_news_count": len(suspicious_news),
                "negative_sentiment": avg_sentiment < self.news_sentiment_threshold,
                "high_suspicious_news": len(suspicious_news) > len(news_data) * 0.2
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {str(e)}")
            return {
                "has_data": False,
                "error": str(e)
            }
    
    def _analyze_fundamental_red_flags(self, company_info: Dict = None,
                                     price_df: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח דגלים אדומים בסיסיים"""
        try:
            if not company_info:
                return {
                    "has_data": False,
                    "market_cap": 0,
                    "revenue": 0,
                    "profitability": "UNKNOWN"
                }
            
            market_cap = company_info.get('market_cap', 0)
            revenue = company_info.get('revenue', 0)
            net_income = company_info.get('net_income', 0)
            
            # בדיקת שווי שוק נמוך
            low_market_cap = market_cap < self.market_cap_threshold
            
            # בדיקת רווחיות
            profitability = "PROFITABLE" if net_income > 0 else "LOSS_MAKING"
            
            # בדיקת יחס P/E
            pe_ratio = company_info.get('pe_ratio', 0)
            high_pe = pe_ratio > 50 if pe_ratio > 0 else False
            
            # בדיקת חובות
            debt_ratio = company_info.get('debt_ratio', 0)
            high_debt = debt_ratio > 0.7 if debt_ratio > 0 else False
            
            return {
                "has_data": True,
                "market_cap": market_cap,
                "revenue": revenue,
                "net_income": net_income,
                "pe_ratio": pe_ratio,
                "debt_ratio": debt_ratio,
                "low_market_cap": low_market_cap,
                "profitability": profitability,
                "high_pe": high_pe,
                "high_debt": high_debt,
                "red_flags_count": sum([low_market_cap, net_income < 0, high_pe, high_debt])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing fundamental red flags: {str(e)}")
            return {
                "has_data": False,
                "error": str(e)
            }
    
    def _analyze_manipulation_patterns(self, price_df: pd.DataFrame,
                                     volume_data: pd.DataFrame = None,
                                     social_media_data: List[Dict] = None) -> Dict[str, Any]:
        """ניתוח תבניות מניפולטיביות"""
        try:
            prices = price_df['close']
            volumes = volume_data['volume'] if volume_data is not None else price_df['volume']
            
            # זיהוי תבניות מחיר חשודות
            price_manipulation = self._detect_price_manipulation(prices)
            
            # זיהוי תבניות נפח חשודות
            volume_manipulation = self._detect_volume_manipulation(volumes)
            
            # ניתוח קורלציה בין מחיר לנפח
            price_volume_correlation = self._analyze_price_volume_correlation(prices, volumes)
            
            # ניתוח תבניות זמן
            time_patterns = self._analyze_time_patterns(price_df)
            
            return {
                "price_manipulation": price_manipulation,
                "volume_manipulation": volume_manipulation,
                "price_volume_correlation": price_volume_correlation,
                "time_patterns": time_patterns,
                "manipulation_indicators": sum([
                    price_manipulation.get("suspicious", False),
                    volume_manipulation.get("suspicious", False),
                    abs(price_volume_correlation) > 0.8
                ])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing manipulation patterns: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _calculate_pump_dump_risk_score(self, volume_analysis: Dict,
                                      price_analysis: Dict,
                                      social_analysis: Dict,
                                      news_analysis: Dict,
                                      fundamental_analysis: Dict,
                                      manipulation_analysis: Dict) -> float:
        """חישוב ציון סיכון Pump & Dump"""
        try:
            score = 0.0
            max_score = 100.0
            
            # ציון נפח חשוד (25 נקודות)
            if volume_analysis.get("suspicious_pattern", False):
                volume_ratio = volume_analysis.get("volume_ratio", 1.0)
                score += min(25, (volume_ratio / 5) * 25)
            
            # ציון תנועות מחיר חשודות (25 נקודות)
            if price_analysis.get("suspicious_movement", False):
                volatility = price_analysis.get("volatility", 0)
                score += min(25, (volatility / 1.0) * 25)
            
            # ציון פעילות חברתית חשודה (20 נקודות)
            if social_analysis.get("high_suspicious_activity", False):
                suspicious_percentage = social_analysis.get("suspicious_percentage", 0)
                score += min(20, (suspicious_percentage / 0.5) * 20)
            
            # ציון חדשות חשודות (15 נקודות)
            if news_analysis.get("high_suspicious_news", False):
                suspicious_count = news_analysis.get("suspicious_news_count", 0)
                score += min(15, (suspicious_count / 5) * 15)
            
            # ציון דגלים אדומים בסיסיים (10 נקודות)
            red_flags = fundamental_analysis.get("red_flags_count", 0)
            score += min(10, red_flags * 2.5)
            
            # ציון אינדיקטורים למניפולציה (5 נקודות)
            manipulation_indicators = manipulation_analysis.get("manipulation_indicators", 0)
            score += min(5, manipulation_indicators * 1.67)
            
            return min(score, max_score)
            
        except Exception as e:
            logger.error(f"Error calculating pump and dump risk score: {str(e)}")
            return 0.0
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """קביעת רמת סיכון"""
        if risk_score >= 80:
            return "EXTREME"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_recommendation(self, risk_score: float, risk_level: str) -> str:
        """יצירת המלצה"""
        if risk_score >= 80:
            return "AVOID - High probability of pump and dump scheme"
        elif risk_score >= 60:
            return "CAUTION - Significant pump and dump risk detected"
        elif risk_score >= 40:
            return "WATCH - Monitor for suspicious activity"
        elif risk_score >= 20:
            return "LOW_RISK - Minimal pump and dump indicators"
        else:
            return "SAFE - No significant pump and dump risk"
    
    def _extract_warning_signals(self, volume_analysis: Dict,
                               price_analysis: Dict,
                               social_analysis: Dict,
                               news_analysis: Dict,
                               fundamental_analysis: Dict,
                               manipulation_analysis: Dict) -> List[str]:
        """חילוץ אותות אזהרה"""
        signals = []
        
        if volume_analysis.get("extreme_volume_spike", False):
            volume_ratio = volume_analysis.get("volume_ratio", 1.0)
            signals.append(f"Extreme volume spike: {volume_ratio:.1f}x average")
        
        if price_analysis.get("extreme_price_spike", False):
            price_change = price_analysis.get("recent_price_change", 0)
            signals.append(f"Extreme price movement: {price_change:.1%}")
        
        if price_analysis.get("high_volatility", False):
            volatility = price_analysis.get("volatility", 0)
            signals.append(f"High volatility: {volatility:.1%}")
        
        if social_analysis.get("high_suspicious_activity", False):
            suspicious_percentage = social_analysis.get("suspicious_percentage", 0)
            signals.append(f"High suspicious social activity: {suspicious_percentage:.1%}")
        
        if news_analysis.get("high_suspicious_news", False):
            suspicious_count = news_analysis.get("suspicious_news_count", 0)
            signals.append(f"High suspicious news count: {suspicious_count}")
        
        if fundamental_analysis.get("red_flags_count", 0) > 2:
            red_flags = fundamental_analysis.get("red_flags_count", 0)
            signals.append(f"Multiple fundamental red flags: {red_flags}")
        
        if manipulation_analysis.get("manipulation_indicators", 0) > 1:
            indicators = manipulation_analysis.get("manipulation_indicators", 0)
            signals.append(f"Multiple manipulation indicators: {indicators}")
        
        return signals
    
    def _contains_suspicious_keywords(self, text: str) -> bool:
        """בדיקה אם טקסט מכיל מילות מפתח חשודות"""
        if not text:
            return False
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.suspicious_keywords)
    
    def _detect_volume_patterns(self, volume_series: pd.Series) -> Dict[str, Any]:
        """זיהוי תבניות נפח"""
        try:
            # חישוב סטיית תקן
            volume_std = volume_series.std()
            volume_mean = volume_series.mean()
            
            # בדיקת תבניות לא סדירות
            irregular_pattern = volume_std > volume_mean * 2
            
            return {
                "irregular": irregular_pattern,
                "std_dev": volume_std,
                "mean": volume_mean
            }
            
        except Exception:
            return {"irregular": False}
    
    def _detect_suspicious_price_patterns(self, prices: pd.Series) -> Dict[str, Any]:
        """זיהוי תבניות מחיר חשודות"""
        try:
            # חישוב שינויים יומיים
            daily_changes = prices.pct_change()
            
            # זיהוי תבניות קפיצות
            large_jumps = abs(daily_changes) > 0.1
            jump_count = large_jumps.sum()
            
            # זיהוי תבניות חזרתיות
            repetitive_pattern = self._detect_repetitive_pattern(prices)
            
            return {
                "large_jumps": jump_count,
                "repetitive_pattern": repetitive_pattern,
                "suspicious": jump_count > 3 or repetitive_pattern
            }
            
        except Exception:
            return {"suspicious": False}
    
    def _detect_repetitive_pattern(self, prices: pd.Series) -> bool:
        """זיהוי תבניות חזרתיות"""
        try:
            # בדיקה פשוטה לתבניות חזרתיות
            if len(prices) < 10:
                return False
            
            # חישוב קורלציה בין תקופות
            half_length = len(prices) // 2
            first_half = prices[:half_length]
            second_half = prices[half_length:2*half_length]
            
            if len(first_half) == len(second_half):
                correlation = first_half.corr(second_half)
                return correlation > 0.8
            
            return False
            
        except Exception:
            return False
    
    def _detect_activity_spike(self, social_media_data: List[Dict]) -> bool:
        """זיהוי קפיצת פעילות חברתית"""
        try:
            if len(social_media_data) < 10:
                return False
            
            # חישוב פעילות יומית
            daily_activity = {}
            for post in social_media_data:
                date = post.get('date', '')[:10]  # YYYY-MM-DD
                daily_activity[date] = daily_activity.get(date, 0) + 1
            
            if not daily_activity:
                return False
            
            avg_activity = np.mean(list(daily_activity.values()))
            max_activity = max(daily_activity.values())
            
            return max_activity > avg_activity * self.social_activity_threshold
            
        except Exception:
            return False
    
    def _detect_price_manipulation(self, prices: pd.Series) -> Dict[str, Any]:
        """זיהוי מניפולציה במחיר"""
        try:
            # חישוב תנודתיות
            volatility = prices.pct_change().std()
            
            # זיהוי תבניות חשודות
            suspicious = volatility > self.volatility_threshold
            
            return {
                "suspicious": suspicious,
                "volatility": volatility
            }
            
        except Exception:
            return {"suspicious": False}
    
    def _detect_volume_manipulation(self, volumes: pd.Series) -> Dict[str, Any]:
        """זיהוי מניפולציה בנפח"""
        try:
            # חישוב נפח ממוצע
            avg_volume = volumes.mean()
            current_volume = volumes.iloc[-1]
            
            # זיהוי נפח חריג
            suspicious = current_volume > avg_volume * self.volume_spike_threshold
            
            return {
                "suspicious": suspicious,
                "volume_ratio": current_volume / avg_volume if avg_volume > 0 else 1.0
            }
            
        except Exception:
            return {"suspicious": False}
    
    def _analyze_price_volume_correlation(self, prices: pd.Series, volumes: pd.Series) -> float:
        """ניתוח קורלציה בין מחיר לנפח"""
        try:
            return prices.corr(volumes)
        except Exception:
            return 0.0
    
    def _analyze_time_patterns(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """ניתוח תבניות זמן"""
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
    
    def _analyze_price_trend(self, prices: pd.Series) -> str:
        """ניתוח מגמת מחיר"""
        try:
            if len(prices) < 5:
                return "NEUTRAL"
            
            recent_trend = prices.tail(5).pct_change().mean()
            
            if recent_trend > 0.02:
                return "STRONG_UP"
            elif recent_trend > 0:
                return "UP"
            elif recent_trend < -0.02:
                return "STRONG_DOWN"
            elif recent_trend < 0:
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
            "risk_score": 0.0,
            "risk_level": "ERROR",
            "recommendation": "ERROR",
            "warning_signals": [f"Error: {error_message}"]
        }