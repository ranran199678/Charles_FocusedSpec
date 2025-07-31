"""
Forum Monitor - מעקב אחר פורומים
==================================

סוכן המנטר פורומים ופלטפורמות מדיה חברתית למניות.
מזהה מניות עם באזז גבוה בקהילות משקיעים.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import requests
import json
from collections import defaultdict
import re

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("forum_monitor")

class ForumMonitor:
    """
    סוכן מעקב אחר פורומים
    """

    def __init__(self):
        """
        אתחול הסוכן
        """
        self.name = "Forum Monitor"
        self.version = "1.0.0"
        self.description = "מנטר פורומים ופלטפורמות מדיה חברתית למניות"

        # פרמטרים לניתוח
        self.post_threshold = 5  # סף מינימלי לפוסטים
        self.sentiment_threshold = 0.6  # סף סנטימנט חיובי
        self.trend_period = 7  # תקופה לניתוח מגמה (ימים)
        self.buzz_spike_threshold = 2.0  # קפיצה של 2x בפוסטים
        self.engagement_threshold = 0.05  # סף engagement rate

        # פלטפורמות
        self.platforms = {
            'reddit': {
                'subreddits': ['wallstreetbets', 'stocks', 'investing', 'pennystocks'],
                'weight': 0.4
            },
            'stocktwits': {
                'weight': 0.3
            },
            'discord': {
                'weight': 0.2
            },
            'telegram': {
                'weight': 0.1
            }
        }

        # מילות מפתח
        self.bullish_keywords = [
            'moon', 'rocket', 'to the moon', '🚀', '💎', 'diamond hands',
            'hodl', 'buy', 'bullish', 'long', 'call', 'squeeze', 'short squeeze',
            'gamma squeeze', 'fomo', 'yolo', 'tendies', 'gains', 'profit'
        ]
        
        self.bearish_keywords = [
            'dump', 'sell', 'bearish', 'short', 'put', 'crash', 'bear market',
            'paper hands', 'sell the news', 'pump and dump', 'bagholder'
        ]

        logger.info(f"Initialized {self.name} v{self.version}")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None,
                forum_data: List[Dict] = None,
                historical_forum_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח פעילות פורומים למניה

        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            forum_data: נתוני פורומים
            historical_forum_data: נתוני פורומים היסטוריים

        Returns:
            תוצאות הניתוח
        """
        try:
            logger.info(f"Starting forum analysis for {symbol}")

            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")

            # ניתוח פלטפורמות
            platform_analysis = self._analyze_platforms(
                symbol, forum_data, historical_forum_data
            )

            # ניתוח סנטימנט
            sentiment_analysis = self._analyze_forum_sentiment(
                symbol, forum_data
            )

            # ניתוח מגמות
            trend_analysis = self._analyze_forum_trends(
                symbol, forum_data, historical_forum_data
            )

            # ניתוח engagement
            engagement_analysis = self._analyze_engagement(
                symbol, forum_data
            )

            # ניתוח השפעה על מחיר
            price_impact_analysis = self._analyze_price_impact(
                symbol, price_df, platform_analysis, sentiment_analysis
            )

            # ניתוח קהל
            audience_analysis = self._analyze_forum_audience(
                symbol, forum_data
            )

            # חישוב ציון כללי
            score = self._calculate_forum_score(
                platform_analysis,
                sentiment_analysis,
                trend_analysis,
                engagement_analysis,
                price_impact_analysis,
                audience_analysis
            )

            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)

            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)

            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                platform_analysis,
                sentiment_analysis,
                trend_analysis,
                engagement_analysis,
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
                    "platforms": platform_analysis,
                    "sentiment": sentiment_analysis,
                    "trends": trend_analysis,
                    "engagement": engagement_analysis,
                    "price_impact": price_impact_analysis,
                    "audience": audience_analysis
                },
                "metadata": {
                    "post_threshold": self.post_threshold,
                    "sentiment_threshold": self.sentiment_threshold,
                    "trend_period": self.trend_period,
                    "buzz_spike_threshold": self.buzz_spike_threshold,
                    "engagement_threshold": self.engagement_threshold
                }
            }

            logger.info(f"Forum analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result

        except Exception as e:
            error_msg = f"Error analyzing forum activity for {symbol}: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result(error_msg)

    def _analyze_platforms(self, symbol: str, forum_data: List[Dict],
                          historical_forum_data: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח פעילות בפלטפורמות שונות
        """
        try:
            if not forum_data:
                return self._create_empty_platform_analysis()

            # ניתוח לפי פלטפורמה
            platform_breakdown = defaultdict(lambda: {
                'posts': 0,
                'recent_posts': 0,
                'engagement': 0,
                'sentiment': 0.5
            })

            for post in forum_data:
                platform = post.get('platform', 'unknown')
                platform_breakdown[platform]['posts'] += 1
                
                if self._is_recent(post.get('date')):
                    platform_breakdown[platform]['recent_posts'] += 1
                
                platform_breakdown[platform]['engagement'] += post.get('engagement', 0)
                
                # חישוב סנטימנט לפלטפורמה
                sentiment = self._calculate_post_sentiment(post.get('content', ''))
                platform_breakdown[platform]['sentiment'] = (
                    (platform_breakdown[platform]['sentiment'] * 
                     (platform_breakdown[platform]['posts'] - 1) + sentiment) /
                    platform_breakdown[platform]['posts']
                )

            # חישוב ציונים משוקללים
            weighted_scores = {}
            for platform, data in platform_breakdown.items():
                weight = self.platforms.get(platform, {}).get('weight', 0.1)
                score = (
                    data['recent_posts'] * 0.4 +
                    data['engagement'] * 0.3 +
                    data['sentiment'] * 100 * 0.3
                )
                weighted_scores[platform] = score * weight

            total_score = sum(weighted_scores.values())
            dominant_platform = max(platform_breakdown.keys(), 
                                  key=lambda x: platform_breakdown[x]['posts'])

            return {
                "platform_breakdown": dict(platform_breakdown),
                "weighted_scores": weighted_scores,
                "total_score": total_score,
                "dominant_platform": dominant_platform,
                "platform_diversity": len(platform_breakdown),
                "strength": min(total_score / 10, 100)
            }

        except Exception as e:
            logger.error(f"Error analyzing platforms: {str(e)}")
            return self._create_empty_platform_analysis()

    def _analyze_forum_sentiment(self, symbol: str, forum_data: List[Dict]) -> Dict[str, Any]:
        """
        ניתוח סנטימנט בפורומים
        """
        try:
            if not forum_data:
                return {"overall_sentiment": 0.5, "sentiment_score": 0.5}

            bullish_count = 0
            bearish_count = 0
            total_posts = len(forum_data)

            for post in forum_data:
                content = post.get('content', '').lower()
                
                # ספירת מילות מפתח
                bullish_matches = sum(1 for keyword in self.bullish_keywords 
                                    if keyword.lower() in content)
                bearish_matches = sum(1 for keyword in self.bearish_keywords 
                                    if keyword.lower() in content)
                
                if bullish_matches > bearish_matches:
                    bullish_count += 1
                elif bearish_matches > bullish_matches:
                    bearish_count += 1

            # חישוב סנטימנט
            if total_posts == 0:
                sentiment_score = 0.5
            else:
                sentiment_score = bullish_count / total_posts

            # ניתוח מגמה
            recent_posts = [p for p in forum_data if self._is_recent(p.get('date'))]
            recent_bullish = sum(1 for post in recent_posts 
                               if self._calculate_post_sentiment(post.get('content', '')) > 0.6)
            recent_sentiment = recent_bullish / max(len(recent_posts), 1)

            return {
                "overall_sentiment": sentiment_score,
                "sentiment_score": sentiment_score,
                "bullish_posts": bullish_count,
                "bearish_posts": bearish_count,
                "total_posts": total_posts,
                "recent_sentiment": recent_sentiment,
                "sentiment_trend": "positive" if recent_sentiment > sentiment_score else "negative",
                "sentiment_strength": abs(sentiment_score - 0.5) * 2
            }

        except Exception as e:
            logger.error(f"Error analyzing forum sentiment: {str(e)}")
            return {"overall_sentiment": 0.5, "sentiment_score": 0.5}

    def _analyze_forum_trends(self, symbol: str, forum_data: List[Dict],
                            historical_forum_data: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח מגמות בפורומים
        """
        try:
            if not forum_data:
                return {"trend_direction": "neutral", "trend_strength": 0.5}

            # ניתוח מגמה לפי זמן
            recent_posts = [p for p in forum_data if self._is_recent(p.get('date'))]
            older_posts = [p for p in forum_data if not self._is_recent(p.get('date'))]

            recent_count = len(recent_posts)
            older_count = len(older_posts)

            # חישוב קפיצה
            if older_count > 0:
                buzz_spike = recent_count / older_count
            else:
                buzz_spike = 1.0

            # ניתוח מגמה לפי יום
            daily_posts = defaultdict(int)
            for post in forum_data:
                date = post.get('date', '')
                if date:
                    try:
                        day = pd.to_datetime(date).date()
                        daily_posts[day] += 1
                    except:
                        continue

            if len(daily_posts) > 1:
                days = sorted(daily_posts.keys())
                recent_days = days[-3:] if len(days) >= 3 else days
                older_days = days[:-3] if len(days) >= 3 else days[:1]
                
                recent_avg = sum(daily_posts[day] for day in recent_days) / len(recent_days)
                older_avg = sum(daily_posts[day] for day in older_days) / len(older_days)
                
                trend_direction = "increasing" if recent_avg > older_avg * 1.2 else "decreasing" if recent_avg < older_avg * 0.8 else "stable"
                trend_strength = min(abs(recent_avg - older_avg) / max(older_avg, 1), 1.0)
            else:
                trend_direction = "neutral"
                trend_strength = 0.5

            return {
                "buzz_spike": buzz_spike,
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "recent_posts": recent_count,
                "older_posts": older_count,
                "daily_distribution": dict(daily_posts),
                "accelerating": buzz_spike > self.buzz_spike_threshold,
                "decelerating": buzz_spike < 0.5
            }

        except Exception as e:
            logger.error(f"Error analyzing forum trends: {str(e)}")
            return {"trend_direction": "neutral", "trend_strength": 0.5}

    def _analyze_engagement(self, symbol: str, forum_data: List[Dict]) -> Dict[str, Any]:
        """
        ניתוח engagement בפורומים
        """
        try:
            if not forum_data:
                return {"avg_engagement": 0, "engagement_rate": 0}

            total_engagement = sum(post.get('engagement', 0) for post in forum_data)
            total_reach = sum(post.get('reach', 0) for post in forum_data)
            total_posts = len(forum_data)

            avg_engagement = total_engagement / max(total_posts, 1)
            engagement_rate = total_engagement / max(total_reach, 1)

            # ניתוח engagement לפי פלטפורמה
            platform_engagement = defaultdict(list)
            for post in forum_data:
                platform = post.get('platform', 'unknown')
                platform_engagement[platform].append(post.get('engagement', 0))

            avg_platform_engagement = {
                platform: sum(engagements) / len(engagements)
                for platform, engagements in platform_engagement.items()
            }

            # זיהוי פוסטים ויראליים
            viral_posts = [post for post in forum_data 
                          if post.get('engagement', 0) > avg_engagement * 3]

            return {
                "total_engagement": total_engagement,
                "avg_engagement": avg_engagement,
                "engagement_rate": engagement_rate,
                "total_reach": total_reach,
                "viral_posts_count": len(viral_posts),
                "platform_engagement": dict(avg_platform_engagement),
                "high_engagement": engagement_rate > self.engagement_threshold,
                "viral_potential": len(viral_posts) > 0
            }

        except Exception as e:
            logger.error(f"Error analyzing engagement: {str(e)}")
            return {"avg_engagement": 0, "engagement_rate": 0}

    def _analyze_price_impact(self, symbol: str, price_df: pd.DataFrame,
                            platform_analysis: Dict, sentiment_analysis: Dict) -> Dict[str, Any]:
        """
        ניתוח השפעת פעילות פורומים על מחיר
        """
        try:
            if price_df is None or price_df.empty:
                return {"price_correlation": 0.0, "impact_strength": 0.0}

            # חישוב שינויי מחיר
            price_changes = price_df['close'].pct_change()
            
            # חישוב באזז משוקלל
            forum_buzz = platform_analysis.get('total_score', 0)
            sentiment = sentiment_analysis.get('sentiment_score', 0.5)
            weighted_buzz = forum_buzz * sentiment

            # קורלציה בין באזז למחיר
            if len(price_changes) > 1:
                correlation = np.corrcoef([weighted_buzz] * len(price_changes), 
                                        price_changes.dropna())[0, 1]
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
                "forum_price_alignment": correlation > 0.3,
                "weighted_buzz": weighted_buzz
            }

        except Exception as e:
            logger.error(f"Error analyzing price impact: {str(e)}")
            return {"price_correlation": 0.0, "impact_strength": 0.0}

    def _analyze_forum_audience(self, symbol: str, forum_data: List[Dict]) -> Dict[str, Any]:
        """
        ניתוח קהל הפורומים
        """
        try:
            if not forum_data:
                return {"audience_type": "unknown", "total_users": 0}

            # ניתוח משתמשים ייחודיים
            unique_users = set()
            user_posts = defaultdict(int)
            
            for post in forum_data:
                user = post.get('user', 'anonymous')
                unique_users.add(user)
                user_posts[user] += 1

            total_users = len(unique_users)
            total_posts = len(forum_data)
            
            # חישוב engagement per user
            avg_posts_per_user = total_posts / max(total_users, 1)
            
            # זיהוי power users
            power_users = [user for user, count in user_posts.items() if count > 3]
            power_user_ratio = len(power_users) / max(total_users, 1)

            # סיווג קהל
            if power_user_ratio > 0.3:
                audience_type = "power_users"
            elif avg_posts_per_user > 2:
                audience_type = "engaged"
            elif total_users > 100:
                audience_type = "large_community"
            else:
                audience_type = "small_community"

            return {
                "total_users": total_users,
                "total_posts": total_posts,
                "avg_posts_per_user": avg_posts_per_user,
                "power_users": len(power_users),
                "power_user_ratio": power_user_ratio,
                "audience_type": audience_type,
                "community_size": "large" if total_users > 100 else "medium" if total_users > 20 else "small"
            }

        except Exception as e:
            logger.error(f"Error analyzing forum audience: {str(e)}")
            return {"audience_type": "unknown", "total_users": 0}

    def _calculate_forum_score(self, platform_analysis: Dict, sentiment_analysis: Dict,
                             trend_analysis: Dict, engagement_analysis: Dict,
                             price_impact_analysis: Dict, audience_analysis: Dict) -> float:
        """
        חישוב ציון פורומים כללי
        """
        try:
            # משקלות
            weights = {
                'platforms': 0.25,
                'sentiment': 0.20,
                'trends': 0.20,
                'engagement': 0.15,
                'price_impact': 0.10,
                'audience': 0.10
            }

            # ציונים
            platform_score = platform_analysis.get('strength', 0)
            sentiment_score = sentiment_analysis.get('sentiment_score', 0.5) * 100
            trend_score = trend_analysis.get('buzz_spike', 1.0) * 50
            engagement_score = engagement_analysis.get('engagement_rate', 0) * 100
            price_score = price_impact_analysis.get('impact_strength', 0) * 100
            audience_score = 100 if audience_analysis.get('audience_type') == 'large_community' else 50

            # חישוב ציון משוקלל
            total_score = (
                platform_score * weights['platforms'] +
                sentiment_score * weights['sentiment'] +
                trend_score * weights['trends'] +
                engagement_score * weights['engagement'] +
                price_score * weights['price_impact'] +
                audience_score * weights['audience']
            )

            return min(max(total_score, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating forum score: {str(e)}")
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
            return "Strong Buy - High forum activity with positive sentiment"
        elif score >= 60:
            return "Buy - Good forum momentum with positive indicators"
        elif score >= 40:
            return "Hold - Moderate forum activity, monitor for changes"
        else:
            return "Sell - Low forum interest or negative sentiment"

    def _extract_key_signals(self, platform_analysis: Dict, sentiment_analysis: Dict,
                           trend_analysis: Dict, engagement_analysis: Dict,
                           price_impact_analysis: Dict, audience_analysis: Dict) -> List[str]:
        """
        חילוץ אותות מפתח
        """
        signals = []

        # אותות פלטפורמות
        if platform_analysis.get('strength', 0) > 70:
            signals.append(f"High platform activity: {platform_analysis.get('strength', 0):.1f}")

        # אותות סנטימנט
        sentiment = sentiment_analysis.get('sentiment_trend', 'neutral')
        if sentiment == 'positive':
            signals.append("Positive sentiment trend")
        elif sentiment == 'negative':
            signals.append("Negative sentiment trend")

        # אותות מגמה
        if trend_analysis.get('accelerating', False):
            signals.append(f"Accelerating buzz: {trend_analysis.get('buzz_spike', 1.0):.2f}x")

        # אותות engagement
        if engagement_analysis.get('high_engagement', False):
            signals.append("High engagement rate")

        # אותות השפעת מחיר
        if price_impact_analysis.get('forum_price_alignment', False):
            signals.append("Forum-price correlation detected")

        # אותות קהל
        audience_type = audience_analysis.get('audience_type', 'unknown')
        if audience_type == 'large_community':
            signals.append("Large community activity")

        return signals

    def _calculate_post_sentiment(self, content: str) -> float:
        """
        חישוב סנטימנט של פוסט בודד
        """
        if not content:
            return 0.5
        
        content_lower = content.lower()
        
        bullish_matches = sum(1 for keyword in self.bullish_keywords 
                            if keyword.lower() in content_lower)
        bearish_matches = sum(1 for keyword in self.bearish_keywords 
                            if keyword.lower() in content_lower)
        
        total_matches = bullish_matches + bearish_matches
        if total_matches == 0:
            return 0.5
        
        return bullish_matches / total_matches

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

    def _create_empty_platform_analysis(self) -> Dict[str, Any]:
        """
        יצירת ניתוח פלטפורמות ריק
        """
        return {
            "platform_breakdown": {},
            "weighted_scores": {},
            "total_score": 0,
            "dominant_platform": "none",
            "platform_diversity": 0,
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