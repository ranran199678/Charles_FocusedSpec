"""
AI Event Spotter - זיהוי אירועי AI
===================================

סוכן המזהה אירועי AI ומזהה הזדמנויות השקעה מבוססות AI.
מבוסס על ניתוח סנטימנט חדשות, פעילות רשתות חברתיות ותגובות שוק.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import re

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger()

class AIEventSpotter:
    """
    סוכן לזיהוי אירועי AI
    """
    
    def __init__(self):
        """
        אתחול הסוכן
        """
        self.name = "AI Event Spotter"
        self.version = "1.0.0"
        self.description = "מזהה אירועי AI וזיהוי הזדמנויות השקעה מבוססות AI"
        
        # מילות מפתח AI
        self.ai_keywords = [
            'artificial intelligence', 'AI', 'machine learning', 'ML', 'deep learning',
            'neural network', 'chatgpt', 'gpt', 'openai', 'claude', 'bard',
            'automation', 'robotics', 'computer vision', 'NLP', 'natural language processing',
            'algorithm', 'predictive analytics', 'data science', 'big data',
            'quantum computing', 'edge computing', 'cloud AI', 'AI chip',
            'autonomous', 'self-driving', 'smart contract', 'blockchain AI'
        ]
        
        # פרמטרים לניתוח
        self.sentiment_threshold = 0.6  # סנטימנט חיובי מינימלי
        self.volume_spike_threshold = 1.5  # נפח 1.5x מהממוצע
        self.price_momentum_threshold = 0.03  # 3% מומנטום מחיר
        self.social_activity_threshold = 2.0  # פעילות חברתית 2x מהממוצע
        self.news_frequency_threshold = 3  # מינימום חדשות AI ביום
        
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def analyze(self, symbol: str, price_df: pd.DataFrame,
                news_data: List[Dict] = None,
                social_media_data: List[Dict] = None,
                company_info: Dict = None) -> Dict[str, Any]:
        """
        ניתוח אירועי AI
        
        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            news_data: נתוני חדשות
            social_media_data: נתוני רשתות חברתיות
            company_info: מידע על החברה
            
        Returns:
            תוצאות הניתוח
        """
        try:
            logger.info(f"Starting AI event analysis for {symbol}")
            
            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")
            
            if not validate_stock_data(price_df):
                return self._create_error_result("Invalid price data")
            
            # ניתוח חדשות AI
            news_analysis = self._analyze_ai_news(
                news_data, company_info
            )
            
            # ניתוח פעילות רשתות חברתיות
            social_analysis = self._analyze_social_media_activity(
                social_media_data, company_info
            )
            
            # ניתוח תגובת שוק
            market_analysis = self._analyze_market_reaction(
                price_df, news_analysis, social_analysis
            )
            
            # ניתוח מגמות AI
            trend_analysis = self._analyze_ai_trends(
                news_data, social_media_data
            )
            
            # ניתוח תחרותיות AI
            competitive_analysis = self._analyze_ai_competition(
                company_info, news_data
            )
            
            # חישוב ציון כללי
            score = self._calculate_ai_event_score(
                news_analysis,
                social_analysis,
                market_analysis,
                trend_analysis,
                competitive_analysis
            )
            
            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)
            
            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)
            
            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                news_analysis,
                social_analysis,
                market_analysis,
                trend_analysis,
                competitive_analysis
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
                    "ai_news": news_analysis,
                    "social_media": social_analysis,
                    "market_reaction": market_analysis,
                    "ai_trends": trend_analysis,
                    "ai_competition": competitive_analysis
                },
                "metadata": {
                    "sentiment_threshold": self.sentiment_threshold,
                    "volume_spike_threshold": self.volume_spike_threshold,
                    "price_momentum_threshold": self.price_momentum_threshold,
                    "social_activity_threshold": self.social_activity_threshold,
                    "news_frequency_threshold": self.news_frequency_threshold
                }
            }
            
            logger.info(f"AI event analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result
            
        except Exception as e:
            error_msg = f"Error analyzing AI events for {symbol}: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_ai_news(self, news_data: List[Dict] = None,
                        company_info: Dict = None) -> Dict[str, Any]:
        """ניתוח חדשות AI"""
        try:
            if not news_data:
                return {
                    "has_data": False,
                    "ai_news_count": 0,
                    "sentiment_score": 0.0,
                    "recent_ai_news": [],
                    "ai_news_frequency": 0.0
                }
            
            # סינון חדשות AI
            ai_news = []
            for news in news_data:
                if self._contains_ai_keywords(news.get('title', '') + ' ' + news.get('content', '')):
                    ai_news.append(news)
            
            if not ai_news:
                return {
                    "has_data": True,
                    "ai_news_count": 0,
                    "sentiment_score": 0.0,
                    "recent_ai_news": [],
                    "ai_news_frequency": 0.0
                }
            
            # חישוב סנטימנט
            sentiment_scores = [news.get('sentiment', 0) for news in ai_news]
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.0
            
            # חישוב תדירות חדשות AI
            recent_news = [news for news in ai_news 
                          if self._is_recent_news(news.get('date', ''))]
            ai_news_frequency = len(recent_news)
            
            # חדשות אחרונות
            recent_ai_news = sorted(ai_news, key=lambda x: x.get('date', ''), reverse=True)[:5]
            
            return {
                "has_data": True,
                "ai_news_count": len(ai_news),
                "sentiment_score": avg_sentiment,
                "recent_ai_news": recent_ai_news,
                "ai_news_frequency": ai_news_frequency,
                "positive_sentiment": avg_sentiment > self.sentiment_threshold,
                "high_frequency": ai_news_frequency >= self.news_frequency_threshold
            }
            
        except Exception as e:
            logger.error(f"Error analyzing AI news: {str(e)}")
            return {
                "has_data": False,
                "error": str(e)
            }
    
    def _analyze_social_media_activity(self, social_media_data: List[Dict] = None,
                                     company_info: Dict = None) -> Dict[str, Any]:
        """ניתוח פעילות רשתות חברתיות"""
        try:
            if not social_media_data:
                return {
                    "has_data": False,
                    "ai_mentions": 0,
                    "engagement_rate": 0.0,
                    "sentiment_score": 0.0,
                    "viral_posts": []
                }
            
            # סינון פוסטים AI
            ai_posts = []
            for post in social_media_data:
                if self._contains_ai_keywords(post.get('content', '')):
                    ai_posts.append(post)
            
            if not ai_posts:
                return {
                    "has_data": True,
                    "ai_mentions": 0,
                    "engagement_rate": 0.0,
                    "sentiment_score": 0.0,
                    "viral_posts": []
                }
            
            # חישוב מדדי מעורבות
            engagement_rates = [post.get('engagement_rate', 0) for post in ai_posts]
            avg_engagement = np.mean(engagement_rates) if engagement_rates else 0.0
            
            # חישוב סנטימנט
            sentiment_scores = [post.get('sentiment', 0) for post in ai_posts]
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.0
            
            # פוסטים ויראליים
            viral_posts = sorted(ai_posts, key=lambda x: x.get('engagement_rate', 0), reverse=True)[:3]
            
            return {
                "has_data": True,
                "ai_mentions": len(ai_posts),
                "engagement_rate": avg_engagement,
                "sentiment_score": avg_sentiment,
                "viral_posts": viral_posts,
                "high_engagement": avg_engagement > self.social_activity_threshold,
                "positive_sentiment": avg_sentiment > self.sentiment_threshold
            }
            
        except Exception as e:
            logger.error(f"Error analyzing social media activity: {str(e)}")
            return {
                "has_data": False,
                "error": str(e)
            }
    
    def _analyze_market_reaction(self, price_df: pd.DataFrame,
                               news_analysis: Dict,
                               social_analysis: Dict) -> Dict[str, Any]:
        """ניתוח תגובת שוק"""
        try:
            prices = price_df['close']
            volumes = price_df['volume']
            
            # חישוב מומנטום מחיר
            momentum_5d = (prices.iloc[-1] - prices.iloc[-6]) / prices.iloc[-6]
            momentum_10d = (prices.iloc[-1] - prices.iloc[-11]) / prices.iloc[-11]
            
            # ניתוח נפח
            avg_volume = volumes.rolling(window=20).mean()
            current_volume = volumes.iloc[-1]
            volume_ratio = current_volume / avg_volume.iloc[-1]
            
            # זיהוי תגובת שוק חיובית
            positive_momentum = momentum_5d > self.price_momentum_threshold
            volume_spike = volume_ratio > self.volume_spike_threshold
            
            # ניתוח תנודתיות
            volatility = prices.pct_change().std() * np.sqrt(252)
            
            return {
                "momentum_5d": momentum_5d,
                "momentum_10d": momentum_10d,
                "volume_ratio": volume_ratio,
                "volatility": volatility,
                "positive_momentum": positive_momentum,
                "volume_spike": volume_spike,
                "market_reaction": positive_momentum and volume_spike
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market reaction: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_ai_trends(self, news_data: List[Dict] = None,
                          social_media_data: List[Dict] = None) -> Dict[str, Any]:
        """ניתוח מגמות AI"""
        try:
            if not news_data and not social_media_data:
                return {
                    "has_data": False,
                    "trending_ai_topics": [],
                    "ai_adoption_score": 0.0,
                    "innovation_level": "LOW"
                }
            
            # זיהוי נושאים פופולריים
            all_content = []
            if news_data:
                all_content.extend([news.get('title', '') + ' ' + news.get('content', '') 
                                  for news in news_data])
            if social_media_data:
                all_content.extend([post.get('content', '') for post in social_media_data])
            
            # ניתוח נושאים
            trending_topics = self._extract_ai_topics(all_content)
            
            # חישוב ציון אימוץ AI
            ai_adoption_score = self._calculate_ai_adoption_score(all_content)
            
            # רמת חדשנות
            innovation_level = self._determine_innovation_level(ai_adoption_score)
            
            return {
                "has_data": True,
                "trending_ai_topics": trending_topics,
                "ai_adoption_score": ai_adoption_score,
                "innovation_level": innovation_level
            }
            
        except Exception as e:
            logger.error(f"Error analyzing AI trends: {str(e)}")
            return {
                "has_data": False,
                "error": str(e)
            }
    
    def _analyze_ai_competition(self, company_info: Dict = None,
                              news_data: List[Dict] = None) -> Dict[str, Any]:
        """ניתוח תחרותיות AI"""
        try:
            if not company_info:
                return {
                    "has_data": False,
                    "ai_competitors": [],
                    "competitive_position": "UNKNOWN",
                    "ai_investment_level": 0.0
                }
            
            # זיהוי מתחרים AI
            ai_competitors = self._identify_ai_competitors(company_info, news_data)
            
            # מיקום תחרותי
            competitive_position = self._assess_competitive_position(company_info)
            
            # רמת השקעה ב-AI
            ai_investment_level = self._calculate_ai_investment_level(company_info)
            
            return {
                "has_data": True,
                "ai_competitors": ai_competitors,
                "competitive_position": competitive_position,
                "ai_investment_level": ai_investment_level
            }
            
        except Exception as e:
            logger.error(f"Error analyzing AI competition: {str(e)}")
            return {
                "has_data": False,
                "error": str(e)
            }
    
    def _calculate_ai_event_score(self, news_analysis: Dict,
                                social_analysis: Dict,
                                market_analysis: Dict,
                                trend_analysis: Dict,
                                competitive_analysis: Dict) -> float:
        """חישוב ציון כללי"""
        try:
            score = 0.0
            max_score = 100.0
            
            # ציון חדשות AI (25 נקודות)
            if news_analysis.get("has_data", False):
                if news_analysis.get("positive_sentiment", False):
                    sentiment_score = news_analysis.get("sentiment_score", 0)
                    score += min(15, (sentiment_score / 0.8) * 15)
                
                if news_analysis.get("high_frequency", False):
                    frequency = news_analysis.get("ai_news_frequency", 0)
                    score += min(10, (frequency / 5) * 10)
            
            # ציון פעילות חברתית (20 נקודות)
            if social_analysis.get("has_data", False):
                if social_analysis.get("high_engagement", False):
                    engagement = social_analysis.get("engagement_rate", 0)
                    score += min(10, (engagement / 3) * 10)
                
                if social_analysis.get("positive_sentiment", False):
                    sentiment = social_analysis.get("sentiment_score", 0)
                    score += min(10, (sentiment / 0.8) * 10)
            
            # ציון תגובת שוק (25 נקודות)
            if market_analysis.get("positive_momentum", False):
                momentum = market_analysis.get("momentum_5d", 0)
                score += min(15, (momentum / 0.1) * 15)
            
            if market_analysis.get("volume_spike", False):
                volume_ratio = market_analysis.get("volume_ratio", 1.0)
                score += min(10, (volume_ratio / 3) * 10)
            
            # ציון מגמות AI (20 נקודות)
            if trend_analysis.get("has_data", False):
                adoption_score = trend_analysis.get("ai_adoption_score", 0)
                score += min(20, (adoption_score / 0.8) * 20)
            
            # ציון תחרותיות AI (10 נקודות)
            if competitive_analysis.get("has_data", False):
                investment_level = competitive_analysis.get("ai_investment_level", 0)
                score += min(10, (investment_level / 0.8) * 10)
            
            return min(score, max_score)
            
        except Exception as e:
            logger.error(f"Error calculating AI event score: {str(e)}")
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
            return "STRONG_BUY - Strong AI-driven opportunity"
        elif score >= 60:
            return "BUY - Promising AI event detected"
        elif score >= 40:
            return "WATCH - Monitor AI developments"
        else:
            return "HOLD - No significant AI events"
    
    def _extract_key_signals(self, news_analysis: Dict,
                            social_analysis: Dict,
                            market_analysis: Dict,
                            trend_analysis: Dict,
                            competitive_analysis: Dict) -> List[str]:
        """חילוץ אותות מפתח"""
        signals = []
        
        if news_analysis.get("positive_sentiment", False):
            sentiment = news_analysis.get("sentiment_score", 0)
            signals.append(f"Positive AI news sentiment: {sentiment:.2f}")
        
        if news_analysis.get("high_frequency", False):
            frequency = news_analysis.get("ai_news_frequency", 0)
            signals.append(f"High AI news frequency: {frequency} recent articles")
        
        if social_analysis.get("high_engagement", False):
            engagement = social_analysis.get("engagement_rate", 0)
            signals.append(f"High social media engagement: {engagement:.2f}")
        
        if market_analysis.get("positive_momentum", False):
            momentum = market_analysis.get("momentum_5d", 0)
            signals.append(f"Positive market momentum: {momentum:.1%}")
        
        if market_analysis.get("volume_spike", False):
            volume_ratio = market_analysis.get("volume_ratio", 1.0)
            signals.append(f"Volume spike: {volume_ratio:.1f}x average")
        
        if trend_analysis.get("has_data", False):
            adoption_score = trend_analysis.get("ai_adoption_score", 0)
            signals.append(f"AI adoption score: {adoption_score:.2f}")
        
        return signals
    
    def _contains_ai_keywords(self, text: str) -> bool:
        """בדיקה אם טקסט מכיל מילות מפתח AI"""
        if not text:
            return False
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.ai_keywords)
    
    def _is_recent_news(self, date_str: str) -> bool:
        """בדיקה אם חדשות מהתקופה האחרונה"""
        try:
            if not date_str:
                return False
            
            news_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            days_diff = (datetime.now() - news_date).days
            
            return days_diff <= 7  # חדשות מהשבוע האחרון
            
        except Exception:
            return False
    
    def _extract_ai_topics(self, content_list: List[str]) -> List[str]:
        """חילוץ נושאי AI פופולריים"""
        try:
            topic_counts = {}
            
            for content in content_list:
                for keyword in self.ai_keywords:
                    if keyword.lower() in content.lower():
                        topic_counts[keyword] = topic_counts.get(keyword, 0) + 1
            
            # מיון לפי פופולריות
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            return [topic[0] for topic in sorted_topics[:5]]
            
        except Exception:
            return []
    
    def _calculate_ai_adoption_score(self, content_list: List[str]) -> float:
        """חישוב ציון אימוץ AI"""
        try:
            if not content_list:
                return 0.0
            
            ai_mentions = sum(1 for content in content_list 
                            if self._contains_ai_keywords(content))
            
            total_content = len(content_list)
            return min(1.0, ai_mentions / max(total_content, 1))
            
        except Exception:
            return 0.0
    
    def _determine_innovation_level(self, adoption_score: float) -> str:
        """קביעת רמת חדשנות"""
        if adoption_score >= 0.7:
            return "HIGH"
        elif adoption_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_ai_competitors(self, company_info: Dict,
                               news_data: List[Dict] = None) -> List[str]:
        """זיהוי מתחרים AI"""
        try:
            competitors = company_info.get('competitors', [])
            ai_competitors = []
            
            for competitor in competitors:
                if self._is_ai_company(competitor, news_data):
                    ai_competitors.append(competitor)
            
            return ai_competitors
            
        except Exception:
            return []
    
    def _is_ai_company(self, company_name: str, news_data: List[Dict] = None) -> bool:
        """בדיקה אם חברה היא חברת AI"""
        try:
            if not news_data:
                return False
            
            company_news = [news for news in news_data 
                          if company_name.lower() in news.get('title', '').lower() or
                             company_name.lower() in news.get('content', '').lower()]
            
            ai_news_count = sum(1 for news in company_news 
                              if self._contains_ai_keywords(news.get('title', '') + ' ' + news.get('content', '')))
            
            return ai_news_count >= 2  # לפחות 2 חדשות AI
            
        except Exception:
            return False
    
    def _assess_competitive_position(self, company_info: Dict) -> str:
        """הערכת מיקום תחרותי"""
        try:
            ai_investment = company_info.get('ai_investment', 0)
            market_cap = company_info.get('market_cap', 0)
            
            if market_cap > 0:
                ai_investment_ratio = ai_investment / market_cap
                
                if ai_investment_ratio >= 0.05:
                    return "LEADER"
                elif ai_investment_ratio >= 0.02:
                    return "COMPETITIVE"
                else:
                    return "LAGGING"
            
            return "UNKNOWN"
            
        except Exception:
            return "UNKNOWN"
    
    def _calculate_ai_investment_level(self, company_info: Dict) -> float:
        """חישוב רמת השקעה ב-AI"""
        try:
            ai_investment = company_info.get('ai_investment', 0)
            total_revenue = company_info.get('revenue', 0)
            
            if total_revenue > 0:
                return min(1.0, ai_investment / total_revenue)
            
            return 0.0
            
        except Exception:
            return 0.0
    
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