import sys
import os
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import re
from collections import Counter

# הוספת הנתיב לספריות
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.base_agent import BaseAgent

class SocialMediaHypeScanner(BaseAgent):
    """
    Social Media Hype Scanner - ניתוח מתקדם של רשתות חברתיות
    
    מנתח:
    - Reddit (r/wallstreetbets, r/stocks, r/investing)
    - Twitter/FinTwit
    - Stocktwits
    - YouTube comments
    - Google Trends
    - איתור גלי hype וסנטימנט
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # API Keys למקורות רשתות חברתיות
        self.reddit_api_key = os.getenv("REDDIT_API_KEY", "")
        self.twitter_api_key = os.getenv("TWITTER_API_KEY", "")
        self.stocktwits_api_key = os.getenv("STOCKTWITS_API_KEY", "")
        
        # משקלים לניתוח
        self.platform_weights = {
            "reddit": 0.35,
            "twitter": 0.30,
            "stocktwits": 0.20,
            "youtube": 0.10,
            "google_trends": 0.05
        }
        
        # מילות מפתח לזיהוי hype
        self.hype_keywords = {
            "positive": [
                "moon", "rocket", "🚀", "💎", "diamond hands", "hodl", "to the moon",
                "bullish", "buy", "long", "strong", "amazing", "incredible", "breakout",
                "squeeze", "short squeeze", "gamma squeeze", "fomo", "yolo"
            ],
            "negative": [
                "bearish", "sell", "short", "dump", "crash", "bear market", "recession",
                "bubble", "overvalued", "expensive", "sell off", "panic", "fear"
            ],
            "volume": [
                "volume", "high volume", "low volume", "volume spike", "unusual volume",
                "volume surge", "volume explosion", "volume dry up"
            ],
            "technical": [
                "support", "resistance", "breakout", "breakdown", "consolidation",
                "wedge", "triangle", "flag", "pennant", "cup and handle", "double top",
                "double bottom", "head and shoulders", "inverse head and shoulders"
            ]
        }
        
        # ספיי ציונים
        self.score_thresholds = {
            "extreme_hype": 90,
            "high_hype": 75,
            "moderate_hype": 60,
            "low_hype": 40,
            "no_hype": 20
        }
        
        self.log("Social Media Hype Scanner initialized")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח hype ברשתות חברתיות
        
        Args:
            symbol: סמל המניה
            price_df: נתוני מחירים (לא נדרש לניתוח רשתות)
            
        Returns:
            Dict עם ציון, ניתוח ופרטים
        """
        try:
            self.log(f"Starting social media hype analysis for {symbol}")
            
            # 1. איסוף נתונים מרשתות חברתיות
            social_data = self._fetch_social_data(symbol)
            
            # 2. ניתוח סנטימנט
            sentiment_analysis = self._analyze_sentiment(social_data)
            
            # 3. זיהוי hype
            hype_analysis = self._detect_hype(social_data)
            
            # 4. ניתוח מגמות
            trend_analysis = self._analyze_trends(social_data)
            
            # 5. חישוב ציון כולל
            overall_score = self._calculate_hype_score(sentiment_analysis, hype_analysis, trend_analysis)
            
            # 6. יצירת סיכום
            summary = self._generate_hype_summary(sentiment_analysis, hype_analysis, trend_analysis)
            
            result = {
                "score": overall_score,
                "sentiment": self._get_sentiment(overall_score),
                "summary": summary,
                "details": {
                    "social_data": social_data,
                    "sentiment_analysis": sentiment_analysis,
                    "hype_analysis": hype_analysis,
                    "trend_analysis": trend_analysis,
                    "recommendations": self._generate_recommendations(sentiment_analysis, hype_analysis)
                }
            }
            
            self.log(f"Social media hype analysis completed for {symbol}: Score {overall_score}")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return {
                "score": 50,  # ציון ניטרלי במקרה של שגיאה
                "sentiment": "neutral",
                "summary": f"שגיאה בניתוח רשתות חברתיות: {str(e)}",
                "details": {}
            }

    def _fetch_social_data(self, symbol: str) -> Dict:
        """איסוף נתונים מרשתות חברתיות"""
        social_data = {}
        
        try:
            # 1. Reddit
            social_data["reddit"] = self._fetch_reddit_data(symbol)
            
            # 2. Twitter
            social_data["twitter"] = self._fetch_twitter_data(symbol)
            
            # 3. Stocktwits
            social_data["stocktwits"] = self._fetch_stocktwits_data(symbol)
            
            # 4. YouTube
            social_data["youtube"] = self._fetch_youtube_data(symbol)
            
            # 5. Google Trends
            social_data["google_trends"] = self._fetch_google_trends_data(symbol)
            
        except Exception as e:
            self.log(f"Error fetching social data: {e}")
            # נתונים דמו במקרה של שגיאה
            social_data = self._get_demo_social_data(symbol)
        
        return social_data

    def _get_demo_social_data(self, symbol: str) -> Dict:
        """נתוני דמו למקרה שאין גישה ל-API"""
        return {
            "reddit": {
                "mentions": 45,
                "sentiment": "positive",
                "top_posts": [
                    {"title": f"$SYMBOL looking bullish!", "score": 125, "sentiment": "positive"},
                    {"title": f"$SYMBOL earnings beat expectations", "score": 89, "sentiment": "positive"},
                    {"title": f"$SYMBOL technical analysis", "score": 67, "sentiment": "neutral"}
                ],
                "hype_score": 70
            },
            "twitter": {
                "mentions": 234,
                "sentiment": "positive",
                "trending": True,
                "influencers": [
                    {"handle": "@trader_pro", "sentiment": "positive", "followers": 50000},
                    {"handle": "@stock_analyst", "sentiment": "positive", "followers": 75000}
                ],
                "hype_score": 75
            },
            "stocktwits": {
                "mentions": 156,
                "sentiment": "positive",
                "bullish_percentage": 65,
                "bearish_percentage": 35,
                "hype_score": 65
            },
            "youtube": {
                "videos": 12,
                "total_views": 45000,
                "sentiment": "positive",
                "hype_score": 60
            },
            "google_trends": {
                "trend_score": 65,
                "trend_direction": "rising",
                "hype_score": 70
            }
        }

    def _analyze_sentiment(self, social_data: Dict) -> Dict:
        """ניתוח סנטימנט מנתוני הרשתות החברתיות"""
        sentiment_scores = {}
        total_mentions = 0
        
        for platform, data in social_data.items():
            if isinstance(data, dict):
                mentions = data.get("mentions", 0)
                sentiment = data.get("sentiment", "neutral")
                hype_score = data.get("hype_score", 50)
                
                # המרת סנטימנט לציון
                sentiment_score = self._convert_sentiment_to_score(sentiment)
                
                sentiment_scores[platform] = {
                    "mentions": mentions,
                    "sentiment": sentiment,
                    "sentiment_score": sentiment_score,
                    "hype_score": hype_score,
                    "weight": self.platform_weights.get(platform, 0.1)
                }
                
                total_mentions += mentions
        
        # חישוב סנטימנט כולל
        weighted_sentiment = 0
        total_weight = 0
        
        for platform, scores in sentiment_scores.items():
            weight = scores["weight"]
            sentiment_score = scores["sentiment_score"]
            hype_score = scores["hype_score"]
            
            # שילוב סנטימנט עם hype
            combined_score = (sentiment_score * 0.7) + (hype_score * 0.3)
            weighted_sentiment += combined_score * weight
            total_weight += weight
        
        overall_sentiment_score = int(weighted_sentiment / total_weight) if total_weight > 0 else 50
        
        return {
            "platform_scores": sentiment_scores,
            "total_mentions": total_mentions,
            "overall_sentiment_score": overall_sentiment_score,
            "dominant_sentiment": self._get_dominant_sentiment(overall_sentiment_score)
        }

    def _convert_sentiment_to_score(self, sentiment: str) -> int:
        """המרת סנטימנט לציון מספרי"""
        sentiment_map = {
            "very_positive": 90,
            "positive": 75,
            "neutral": 50,
            "negative": 25,
            "very_negative": 10
        }
        return sentiment_map.get(sentiment, 50)

    def _get_dominant_sentiment(self, score: int) -> str:
        """קביעת הסנטימנט הדומיננטי"""
        if score >= 80:
            return "very_positive"
        elif score >= 60:
            return "positive"
        elif score >= 40:
            return "neutral"
        elif score >= 20:
            return "negative"
        else:
            return "very_negative"

    def _detect_hype(self, social_data: Dict) -> Dict:
        """זיהוי גלי hype"""
        hype_indicators = {}
        
        for platform, data in social_data.items():
            if isinstance(data, dict):
                mentions = data.get("mentions", 0)
                hype_score = data.get("hype_score", 50)
                
                # זיהוי רמת hype לפי מספר אזכורים
                if mentions > 100:
                    hype_level = "extreme"
                elif mentions > 50:
                    hype_level = "high"
                elif mentions > 20:
                    hype_level = "moderate"
                elif mentions > 5:
                    hype_level = "low"
                else:
                    hype_level = "none"
                
                # זיהוי מגמות hype
                if hype_score > 80:
                    trend = "exploding"
                elif hype_score > 60:
                    trend = "rising"
                elif hype_score > 40:
                    trend = "stable"
                elif hype_score > 20:
                    trend = "declining"
                else:
                    trend = "dead"
                
                hype_indicators[platform] = {
                    "mentions": mentions,
                    "hype_score": hype_score,
                    "hype_level": hype_level,
                    "trend": trend,
                    "weight": self.platform_weights.get(platform, 0.1)
                }
        
        # חישוב hype כולל
        weighted_hype = 0
        total_weight = 0
        
        for platform, indicators in hype_indicators.items():
            weight = indicators["weight"]
            hype_score = indicators["hype_score"]
            
            weighted_hype += hype_score * weight
            total_weight += weight
        
        overall_hype_score = int(weighted_hype / total_weight) if total_weight > 0 else 50
        
        return {
            "platform_indicators": hype_indicators,
            "overall_hype_score": overall_hype_score,
            "hype_level": self._get_hype_level(overall_hype_score),
            "trend": self._get_hype_trend(overall_hype_score)
        }

    def _get_hype_level(self, score: int) -> str:
        """קביעת רמת hype"""
        if score >= self.score_thresholds["extreme_hype"]:
            return "extreme"
        elif score >= self.score_thresholds["high_hype"]:
            return "high"
        elif score >= self.score_thresholds["moderate_hype"]:
            return "moderate"
        elif score >= self.score_thresholds["low_hype"]:
            return "low"
        else:
            return "none"

    def _get_hype_trend(self, score: int) -> str:
        """קביעת מגמת hype"""
        if score > 80:
            return "exploding"
        elif score > 60:
            return "rising"
        elif score > 40:
            return "stable"
        elif score > 20:
            return "declining"
        else:
            return "dead"

    def _analyze_trends(self, social_data: Dict) -> Dict:
        """ניתוח מגמות ברשתות חברתיות"""
        trends = {}
        
        for platform, data in social_data.items():
            if isinstance(data, dict):
                mentions = data.get("mentions", 0)
                hype_score = data.get("hype_score", 50)
                
                # ניתוח מגמה לפי מספר אזכורים
                if mentions > 100:
                    volume_trend = "exploding"
                elif mentions > 50:
                    volume_trend = "high"
                elif mentions > 20:
                    volume_trend = "moderate"
                elif mentions > 5:
                    volume_trend = "low"
                else:
                    volume_trend = "minimal"
                
                # ניתוח מגמה לפי hype score
                if hype_score > 80:
                    sentiment_trend = "very_bullish"
                elif hype_score > 60:
                    sentiment_trend = "bullish"
                elif hype_score > 40:
                    sentiment_trend = "neutral"
                elif hype_score > 20:
                    sentiment_trend = "bearish"
                else:
                    sentiment_trend = "very_bearish"
                
                trends[platform] = {
                    "volume_trend": volume_trend,
                    "sentiment_trend": sentiment_trend,
                    "overall_trend": self._combine_trends(volume_trend, sentiment_trend)
                }
        
        return trends

    def _combine_trends(self, volume_trend: str, sentiment_trend: str) -> str:
        """שילוב מגמות נפח וסנטימנט"""
        if volume_trend in ["exploding", "high"] and sentiment_trend in ["very_bullish", "bullish"]:
            return "very_bullish"
        elif volume_trend in ["exploding", "high"] and sentiment_trend == "neutral":
            return "bullish"
        elif volume_trend in ["exploding", "high"] and sentiment_trend in ["bearish", "very_bearish"]:
            return "neutral"
        elif volume_trend in ["moderate", "low"] and sentiment_trend in ["very_bullish", "bullish"]:
            return "bullish"
        elif volume_trend in ["moderate", "low"] and sentiment_trend == "neutral":
            return "neutral"
        elif volume_trend in ["moderate", "low"] and sentiment_trend in ["bearish", "very_bearish"]:
            return "bearish"
        else:
            return "neutral"

    def _calculate_hype_score(self, sentiment_analysis: Dict, hype_analysis: Dict, trend_analysis: Dict) -> int:
        """חישוב ציון hype כולל"""
        sentiment_score = sentiment_analysis.get("overall_sentiment_score", 50)
        hype_score = hype_analysis.get("overall_hype_score", 50)
        
        # משקללים סנטימנט ו-hype
        combined_score = (sentiment_score * 0.6) + (hype_score * 0.4)
        
        # התאמה לפי מגמות
        trend_adjustment = 0
        for platform, trend in trend_analysis.items():
            if trend.get("overall_trend") == "very_bullish":
                trend_adjustment += 5
            elif trend.get("overall_trend") == "bullish":
                trend_adjustment += 2
            elif trend.get("overall_trend") == "bearish":
                trend_adjustment -= 2
            elif trend.get("overall_trend") == "very_bearish":
                trend_adjustment -= 5
        
        final_score = int(combined_score + trend_adjustment)
        return max(0, min(100, final_score))

    def _get_sentiment(self, score: int) -> str:
        """קביעת סנטימנט לפי ציון"""
        if score >= 80:
            return "very_bullish"
        elif score >= 60:
            return "bullish"
        elif score >= 40:
            return "neutral"
        elif score >= 20:
            return "bearish"
        else:
            return "very_bearish"

    def _generate_hype_summary(self, sentiment_analysis: Dict, hype_analysis: Dict, trend_analysis: Dict) -> str:
        """יצירת סיכום ניתוח hype"""
        summary_parts = []
        
        # ניתוח סנטימנט
        dominant_sentiment = sentiment_analysis.get("dominant_sentiment", "neutral")
        total_mentions = sentiment_analysis.get("total_mentions", 0)
        
        if dominant_sentiment == "very_positive":
            summary_parts.append("סנטימנט מאוד חיובי ברשתות")
        elif dominant_sentiment == "positive":
            summary_parts.append("סנטימנט חיובי ברשתות")
        elif dominant_sentiment == "negative":
            summary_parts.append("סנטימנט שלילי ברשתות")
        elif dominant_sentiment == "very_negative":
            summary_parts.append("סנטימנט מאוד שלילי ברשתות")
        else:
            summary_parts.append("סנטימנט ניטרלי ברשתות")
        
        # ניתוח hype
        hype_level = hype_analysis.get("hype_level", "none")
        hype_trend = hype_analysis.get("trend", "stable")
        
        if hype_level == "extreme":
            summary_parts.append("רמת hype קיצונית")
        elif hype_level == "high":
            summary_parts.append("רמת hype גבוהה")
        elif hype_level == "moderate":
            summary_parts.append("רמת hype בינונית")
        elif hype_level == "low":
            summary_parts.append("רמת hype נמוכה")
        else:
            summary_parts.append("אין hype משמעותי")
        
        # ניתוח מגמות
        if hype_trend == "exploding":
            summary_parts.append("Hype מתפוצץ")
        elif hype_trend == "rising":
            summary_parts.append("Hype עולה")
        elif hype_trend == "declining":
            summary_parts.append("Hype יורד")
        
        summary_parts.append(f"סה\"כ {total_mentions} אזכורים ברשתות")
        
        return ". ".join(summary_parts)

    def _generate_recommendations(self, sentiment_analysis: Dict, hype_analysis: Dict) -> List[str]:
        """יצירת המלצות על בסיס ניתוח הרשתות"""
        recommendations = []
        
        sentiment_score = sentiment_analysis.get("overall_sentiment_score", 50)
        hype_score = hype_analysis.get("overall_hype_score", 50)
        hype_level = hype_analysis.get("hype_level", "none")
        
        # המלצות לפי סנטימנט
        if sentiment_score > 80:
            recommendations.append("סנטימנט מאוד חיובי - סביבה טובה לקנייה")
        elif sentiment_score > 60:
            recommendations.append("סנטימנט חיובי - אפשרות לקנייה")
        elif sentiment_score < 20:
            recommendations.append("סנטימנט מאוד שלילי - סיכון גבוה")
        elif sentiment_score < 40:
            recommendations.append("סנטימנט שלילי - זהירות")
        
        # המלצות לפי hype
        if hype_level == "extreme":
            recommendations.append("Hype קיצוני - סיכון ל-FOMO")
        elif hype_level == "high":
            recommendations.append("Hype גבוה - הזדמנות אבל עם סיכון")
        elif hype_level == "none":
            recommendations.append("אין hype - הזדמנות לקנייה רגועה")
        
        # המלצות לפי שילוב
        if sentiment_score > 70 and hype_score > 70:
            recommendations.append("שילוב חיובי של סנטימנט ו-hype")
        elif sentiment_score < 30 and hype_score > 70:
            recommendations.append("Hype גבוה עם סנטימנט שלילי - סיכון")
        
        return recommendations

    # פונקציות עזר לשליפת נתונים (דמו)
    def _fetch_reddit_data(self, symbol: str) -> Dict:
        return {"mentions": 45, "sentiment": "positive", "hype_score": 70}
    
    def _fetch_twitter_data(self, symbol: str) -> Dict:
        return {"mentions": 234, "sentiment": "positive", "hype_score": 75}
    
    def _fetch_stocktwits_data(self, symbol: str) -> Dict:
        return {"mentions": 156, "sentiment": "positive", "hype_score": 65}
    
    def _fetch_youtube_data(self, symbol: str) -> Dict:
        return {"mentions": 12, "sentiment": "positive", "hype_score": 60}
    
    def _fetch_google_trends_data(self, symbol: str) -> Dict:
        return {"mentions": 89, "sentiment": "positive", "hype_score": 70}
