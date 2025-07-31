"""
Media Buzz Tracker - מעקב אחר באזז תקשורתי
============================================

סוכן המנטר באזז תקשורתי ומדיה חברתית למניות.
מזהה מניות עם תנופה תקשורתית גבוהה ופוטנציאל לזינוק.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import requests
import json
from collections import defaultdict

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("media_buzz_tracker")

class MediaBuzzTracker:
    """
    סוכן מעקב אחר באזז תקשורתי
    """

    def __init__(self):
        """
        אתחול הסוכן
        """
        self.name = "Media Buzz Tracker"
        self.version = "1.0.0"
        self.description = "מנטר באזז תקשורתי ומדיה חברתית למניות"

        # פרמטרים לניתוח
        self.mention_threshold = 10  # סף מינימלי לאזכורים
        self.sentiment_threshold = 0.6  # סף סנטימנט חיובי
        self.trend_period = 7  # תקופה לניתוח מגמה (ימים)
        self.buzz_spike_threshold = 2.0  # קפיצה של 2x באזכורים
        self.social_weight = 0.4  # משקל מדיה חברתית
        self.news_weight = 0.6  # משקל חדשות

        # מקורות מדיה
        self.news_sources = [
            'reuters', 'bloomberg', 'cnbc', 'yahoo_finance',
            'marketwatch', 'seeking_alpha', 'benzinga', 'street_insider'
        ]
        
        self.social_platforms = [
            'twitter', 'reddit', 'stocktwits', 'discord',
            'telegram', 'youtube', 'tiktok'
        ]

        logger.info(f"Initialized {self.name} v{self.version}")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None,
                news_data: List[Dict] = None,
                social_data: List[Dict] = None,
                historical_buzz: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח באזז תקשורתי למניה

        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            news_data: נתוני חדשות
            social_data: נתוני מדיה חברתית
            historical_buzz: נתוני באזז היסטוריים

        Returns:
            תוצאות הניתוח
        """
        try:
            logger.info(f"Starting media buzz analysis for {symbol}")

            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")

            # ניתוח חדשות
            news_analysis = self._analyze_news_buzz(
                symbol, news_data, historical_buzz
            )

            # ניתוח מדיה חברתית
            social_analysis = self._analyze_social_buzz(
                symbol, social_data, historical_buzz
            )

            # ניתוח מגמות באזז
            buzz_trend_analysis = self._analyze_buzz_trends(
                symbol, news_analysis, social_analysis, historical_buzz
            )

            # ניתוח סנטימנט
            sentiment_analysis = self._analyze_sentiment(
                symbol, news_data, social_data
            )

            # ניתוח השפעה על מחיר
            price_impact_analysis = self._analyze_price_impact(
                symbol, price_df, news_analysis, social_analysis
            )

            # ניתוח קהל יעד
            audience_analysis = self._analyze_audience(
                symbol, social_data, news_data
            )

            # חישוב ציון כללי
            score = self._calculate_buzz_score(
                news_analysis,
                social_analysis,
                buzz_trend_analysis,
                sentiment_analysis,
                price_impact_analysis,
                audience_analysis
            )

            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)

            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)

            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                news_analysis,
                social_analysis,
                buzz_trend_analysis,
                sentiment_analysis,
                price_impact_analysis,
                audience_analysis
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
                    "news_buzz": news_analysis,
                    "social_buzz": social_analysis,
                    "buzz_trends": buzz_trend_analysis,
                    "sentiment": sentiment_analysis,
                    "price_impact": price_impact_analysis,
                    "audience": audience_analysis
                },
                "metadata": {
                    "mention_threshold": self.mention_threshold,
                    "sentiment_threshold": self.sentiment_threshold,
                    "trend_period": self.trend_period,
                    "buzz_spike_threshold": self.buzz_spike_threshold,
                    "social_weight": self.social_weight,
                    "news_weight": self.news_weight
                }
            }

            logger.info(f"Media buzz analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result

        except Exception as e:
            error_msg = f"Error analyzing media buzz for {symbol}: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result(error_msg)

    def _analyze_news_buzz(self, symbol: str, news_data: List[Dict],
                          historical_buzz: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח באזז חדשות
        """
        try:
            if not news_data:
                return self._create_empty_analysis("news")

            # ספירת אזכורים
            mention_count = len(news_data)
            
            # ניתוח מקורות
            source_breakdown = defaultdict(int)
            for news in news_data:
                source = news.get('source', 'unknown')
                source_breakdown[source] += 1

            # ניתוח מגמה
            recent_news = [n for n in news_data if self._is_recent(n.get('date'))]
            recent_count = len(recent_news)
            
            # חישוב קפיצה
            if historical_buzz is not None and not historical_buzz.empty:
                historical_avg = historical_buzz.get('news_mentions', 0)
                buzz_spike = recent_count / max(historical_avg, 1)
            else:
                buzz_spike = 1.0

            # ניתוח כותרות
            headlines = [n.get('title', '') for n in recent_news]
            headline_sentiment = self._analyze_headlines_sentiment(headlines)

            return {
                "mention_count": mention_count,
                "recent_mentions": recent_count,
                "source_breakdown": dict(source_breakdown),
                "buzz_spike": buzz_spike,
                "headline_sentiment": headline_sentiment,
                "trending": buzz_spike > self.buzz_spike_threshold,
                "strength": min(buzz_spike * 10, 100)
            }

        except Exception as e:
            logger.error(f"Error analyzing news buzz: {str(e)}")
            return self._create_empty_analysis("news")

    def _analyze_social_buzz(self, symbol: str, social_data: List[Dict],
                           historical_buzz: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח באזז מדיה חברתית
        """
        try:
            if not social_data:
                return self._create_empty_analysis("social")

            # ספירת פוסטים
            post_count = len(social_data)
            
            # ניתוח פלטפורמות
            platform_breakdown = defaultdict(int)
            engagement_total = 0
            
            for post in social_data:
                platform = post.get('platform', 'unknown')
                platform_breakdown[platform] += 1
                engagement_total += post.get('engagement', 0)

            # ניתוח מגמה
            recent_posts = [p for p in social_data if self._is_recent(p.get('date'))]
            recent_count = len(recent_posts)
            
            # חישוב קפיצה
            if historical_buzz is not None and not historical_buzz.empty:
                historical_avg = historical_buzz.get('social_mentions', 0)
                buzz_spike = recent_count / max(historical_avg, 1)
            else:
                buzz_spike = 1.0

            # ניתוח engagement
            avg_engagement = engagement_total / max(post_count, 1)
            
            # ניתוח hashtags
            hashtags = self._extract_hashtags(social_data)

            return {
                "post_count": post_count,
                "recent_posts": recent_count,
                "platform_breakdown": dict(platform_breakdown),
                "engagement_total": engagement_total,
                "avg_engagement": avg_engagement,
                "buzz_spike": buzz_spike,
                "hashtags": hashtags,
                "trending": buzz_spike > self.buzz_spike_threshold,
                "strength": min(buzz_spike * 10, 100)
            }

        except Exception as e:
            logger.error(f"Error analyzing social buzz: {str(e)}")
            return self._create_empty_analysis("social")

    def _analyze_buzz_trends(self, symbol: str, news_analysis: Dict,
                           social_analysis: Dict,
                           historical_buzz: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח מגמות באזז
        """
        try:
            # חישוב מגמה כללית
            news_trend = news_analysis.get('buzz_spike', 1.0)
            social_trend = social_analysis.get('buzz_spike', 1.0)
            
            overall_trend = (news_trend * self.news_weight + 
                           social_trend * self.social_weight)

            # ניתוח היסטורי
            if historical_buzz is not None and not historical_buzz.empty:
                trend_direction = self._calculate_trend_direction(historical_buzz)
                trend_strength = self._calculate_trend_strength(historical_buzz)
            else:
                trend_direction = "neutral"
                trend_strength = 0.5

            # זיהוי קפיצות
            buzz_spikes = []
            if news_trend > self.buzz_spike_threshold:
                buzz_spikes.append(f"News spike: {news_trend:.2f}x")
            if social_trend > self.buzz_spike_threshold:
                buzz_spikes.append(f"Social spike: {social_trend:.2f}x")

            return {
                "overall_trend": overall_trend,
                "news_trend": news_trend,
                "social_trend": social_trend,
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "buzz_spikes": buzz_spikes,
                "accelerating": overall_trend > 1.5,
                "decelerating": overall_trend < 0.5
            }

        except Exception as e:
            logger.error(f"Error analyzing buzz trends: {str(e)}")
            return {"overall_trend": 1.0, "trend_direction": "neutral"}

    def _analyze_sentiment(self, symbol: str, news_data: List[Dict],
                         social_data: List[Dict]) -> Dict[str, Any]:
        """
        ניתוח סנטימנט
        """
        try:
            all_texts = []
            
            # איסוף טקסטים מחדשות
            if news_data:
                all_texts.extend([n.get('title', '') + ' ' + n.get('content', '') 
                                for n in news_data])
            
            # איסוף טקסטים ממדיה חברתית
            if social_data:
                all_texts.extend([p.get('content', '') for p in social_data])

            if not all_texts:
                return {"overall_sentiment": 0.5, "sentiment_score": 0.5}

            # ניתוח סנטימנט בסיסי
            positive_words = ['bullish', 'buy', 'strong', 'growth', 'positive', 'up', 'gain']
            negative_words = ['bearish', 'sell', 'weak', 'decline', 'negative', 'down', 'loss']
            
            positive_count = sum(1 for text in all_texts 
                               for word in positive_words 
                               if word.lower() in text.lower())
            negative_count = sum(1 for text in all_texts 
                               for word in negative_words 
                               if word.lower() in text.lower())
            
            total_count = positive_count + negative_count
            if total_count == 0:
                sentiment_score = 0.5
            else:
                sentiment_score = positive_count / total_count

            return {
                "overall_sentiment": sentiment_score,
                "sentiment_score": sentiment_score,
                "positive_mentions": positive_count,
                "negative_mentions": negative_count,
                "total_mentions": total_count,
                "sentiment_trend": "positive" if sentiment_score > 0.6 else "negative" if sentiment_score < 0.4 else "neutral"
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"overall_sentiment": 0.5, "sentiment_score": 0.5}

    def _analyze_price_impact(self, symbol: str, price_df: pd.DataFrame,
                            news_analysis: Dict, social_analysis: Dict) -> Dict[str, Any]:
        """
        ניתוח השפעת באזז על מחיר
        """
        try:
            if price_df is None or price_df.empty:
                return {"price_correlation": 0.0, "impact_strength": 0.0}

            # חישוב שינויי מחיר
            price_changes = price_df['close'].pct_change()
            
            # חישוב באזז משוקלל
            news_buzz = news_analysis.get('buzz_spike', 1.0)
            social_buzz = social_analysis.get('buzz_spike', 1.0)
            weighted_buzz = news_buzz * self.news_weight + social_buzz * self.social_weight

            # קורלציה בין באזז למחיר
            if len(price_changes) > 1:
                correlation = np.corrcoef(weighted_buzz, price_changes.dropna())[0, 1]
                if np.isnan(correlation):
                    correlation = 0.0
            else:
                correlation = 0.0

            # ניתוח תגובת מחיר
            recent_price_change = price_changes.iloc[-1] if len(price_changes) > 0 else 0.0
            price_response = "positive" if recent_price_change > 0 else "negative"

            return {
                "price_correlation": correlation,
                "impact_strength": abs(correlation),
                "recent_price_change": recent_price_change,
                "price_response": price_response,
                "buzz_price_alignment": correlation > 0.3
            }

        except Exception as e:
            logger.error(f"Error analyzing price impact: {str(e)}")
            return {"price_correlation": 0.0, "impact_strength": 0.0}

    def _analyze_audience(self, symbol: str, social_data: List[Dict],
                        news_data: List[Dict]) -> Dict[str, Any]:
        """
        ניתוח קהל יעד
        """
        try:
            # ניתוח פלטפורמות
            platforms = defaultdict(int)
            if social_data:
                for post in social_data:
                    platform = post.get('platform', 'unknown')
                    platforms[platform] += 1

            # ניתוח גודל קהל
            total_reach = sum(post.get('reach', 0) for post in social_data)
            avg_reach = total_reach / max(len(social_data), 1)

            # ניתוח engagement rate
            total_engagement = sum(post.get('engagement', 0) for post in social_data)
            engagement_rate = total_engagement / max(total_reach, 1)

            # זיהוי קהל יעד
            audience_type = self._classify_audience(platforms, engagement_rate)

            return {
                "total_reach": total_reach,
                "avg_reach": avg_reach,
                "engagement_rate": engagement_rate,
                "platform_distribution": dict(platforms),
                "audience_type": audience_type,
                "viral_potential": engagement_rate > 0.1
            }

        except Exception as e:
            logger.error(f"Error analyzing audience: {str(e)}")
            return {"total_reach": 0, "audience_type": "unknown"}

    def _calculate_buzz_score(self, news_analysis: Dict, social_analysis: Dict,
                            buzz_trend_analysis: Dict, sentiment_analysis: Dict,
                            price_impact_analysis: Dict, audience_analysis: Dict) -> float:
        """
        חישוב ציון באזז כללי
        """
        try:
            # משקלות
            weights = {
                'news': 0.25,
                'social': 0.25,
                'trend': 0.20,
                'sentiment': 0.15,
                'price_impact': 0.10,
                'audience': 0.05
            }

            # ציונים
            news_score = news_analysis.get('strength', 0)
            social_score = social_analysis.get('strength', 0)
            trend_score = buzz_trend_analysis.get('overall_trend', 1.0) * 50
            sentiment_score = sentiment_analysis.get('sentiment_score', 0.5) * 100
            price_score = price_impact_analysis.get('impact_strength', 0) * 100
            audience_score = audience_analysis.get('viral_potential', False) * 100

            # חישוב ציון משוקלל
            total_score = (
                news_score * weights['news'] +
                social_score * weights['social'] +
                trend_score * weights['trend'] +
                sentiment_score * weights['sentiment'] +
                price_score * weights['price_impact'] +
                audience_score * weights['audience']
            )

            return min(max(total_score, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating buzz score: {str(e)}")
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
            return "Strong Buy - High media buzz with positive sentiment"
        elif score >= 60:
            return "Buy - Good media momentum with positive indicators"
        elif score >= 40:
            return "Hold - Moderate buzz, monitor for changes"
        else:
            return "Sell - Low media interest or negative sentiment"

    def _extract_key_signals(self, news_analysis: Dict, social_analysis: Dict,
                           buzz_trend_analysis: Dict, sentiment_analysis: Dict,
                           price_impact_analysis: Dict, audience_analysis: Dict) -> List[str]:
        """
        חילוץ אותות מפתח
        """
        signals = []

        # אותות חדשות
        if news_analysis.get('trending', False):
            signals.append(f"News trending: {news_analysis.get('buzz_spike', 1.0):.2f}x mentions")

        # אותות מדיה חברתית
        if social_analysis.get('trending', False):
            signals.append(f"Social trending: {social_analysis.get('buzz_spike', 1.0):.2f}x posts")

        # אותות סנטימנט
        sentiment = sentiment_analysis.get('sentiment_trend', 'neutral')
        if sentiment == 'positive':
            signals.append("Positive sentiment trend")
        elif sentiment == 'negative':
            signals.append("Negative sentiment trend")

        # אותות השפעת מחיר
        if price_impact_analysis.get('buzz_price_alignment', False):
            signals.append("Buzz-price correlation detected")

        # אותות קהל
        if audience_analysis.get('viral_potential', False):
            signals.append("High viral potential")

        return signals

    def _is_recent(self, date_str: str) -> bool:
        """
        בדיקה אם תאריך הוא מהזמן האחרון
        """
        try:
            if not date_str:
                return False
            date = pd.to_datetime(date_str)
            cutoff = datetime.now() - timedelta(days=self.trend_period)
            return date > cutoff
        except:
            return False

    def _analyze_headlines_sentiment(self, headlines: List[str]) -> float:
        """
        ניתוח סנטימנט כותרות
        """
        if not headlines:
            return 0.5
        
        positive_words = ['surge', 'jump', 'rise', 'gain', 'positive', 'bullish']
        negative_words = ['drop', 'fall', 'decline', 'negative', 'bearish']
        
        positive_count = sum(1 for headline in headlines 
                           for word in positive_words 
                           if word.lower() in headline.lower())
        negative_count = sum(1 for headline in headlines 
                           for word in negative_words 
                           if word.lower() in headline.lower())
        
        total = positive_count + negative_count
        return positive_count / max(total, 1)

    def _extract_hashtags(self, social_data: List[Dict]) -> List[str]:
        """
        חילוץ hashtags
        """
        hashtags = []
        for post in social_data:
            content = post.get('content', '')
            # חילוץ hashtags בסיסי
            words = content.split()
            hashtags.extend([word for word in words if word.startswith('#')])
        
        return list(set(hashtags))[:10]  # עד 10 hashtags ייחודיים

    def _calculate_trend_direction(self, historical_buzz: pd.DataFrame) -> str:
        """
        חישוב כיוון מגמה
        """
        try:
            if historical_buzz.empty:
                return "neutral"
            
            recent = historical_buzz.tail(5)
            older = historical_buzz.tail(10).head(5)
            
            recent_avg = recent.mean().mean()
            older_avg = older.mean().mean()
            
            if recent_avg > older_avg * 1.2:
                return "increasing"
            elif recent_avg < older_avg * 0.8:
                return "decreasing"
            else:
                return "stable"
        except:
            return "neutral"

    def _calculate_trend_strength(self, historical_buzz: pd.DataFrame) -> float:
        """
        חישוב עוצמת מגמה
        """
        try:
            if historical_buzz.empty:
                return 0.5
            
            # חישוב שונות
            variance = historical_buzz.var().mean()
            return min(variance / 100, 1.0)
        except:
            return 0.5

    def _classify_audience(self, platforms: Dict, engagement_rate: float) -> str:
        """
        סיווג קהל יעד
        """
        if engagement_rate > 0.15:
            return "highly_engaged"
        elif engagement_rate > 0.08:
            return "engaged"
        elif engagement_rate > 0.03:
            return "moderate"
        else:
            return "passive"

    def _create_empty_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """
        יצירת ניתוח ריק
        """
        return {
            "mention_count": 0,
            "recent_mentions": 0,
            "buzz_spike": 1.0,
            "trending": False,
            "strength": 0
        }

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        יצירת תוצאת שגיאה
        """
        return {
            "symbol": "UNKNOWN",
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "version": self.version,
            "score": 0,
            "confidence": "Very Low",
            "recommendation": f"Error: {error_message}",
            "key_signals": [],
            "analysis": {},
            "error": error_message
        } 