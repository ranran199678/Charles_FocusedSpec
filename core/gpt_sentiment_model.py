"""
GPT Sentiment Model - ניתוח סנטימנט באמצעות GPT
================================================

סוכן המנתח סנטימנט טקסט באמצעות GPT/OpenAI.
מזהה רגשות וטון בטקסטים פיננסיים.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
import json
import openai
from collections import defaultdict

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_text_data

logger = get_agent_logger("gpt_sentiment_model")

class GPTSentimentModel:
    """
    סוכן ניתוח סנטימנט באמצעות GPT
    """

    def __init__(self, config=None):
        """
        אתחול הסוכן
        """
        self.name = "GPT Sentiment Model"
        self.version = "1.0.0"
        self.description = "מנתח סנטימנט טקסט באמצעות GPT/OpenAI"

        # הגדרות OpenAI
        self.config = config or {}
        self.api_key = self.config.get("openai_api_key")
        self.model = self.config.get("model", "gpt-3.5-turbo")
        self.max_tokens = self.config.get("max_tokens", 150)
        self.temperature = self.config.get("temperature", 0.3)

        # פרמטרים לניתוח
        self.sentiment_threshold = 0.6  # סף סנטימנט חיובי
        self.confidence_threshold = 0.7  # סף ביטחון
        self.batch_size = 10  # גודל batch לניתוח

        # מילות מפתח פיננסיות
        self.financial_keywords = {
            'positive': ['bullish', 'buy', 'strong', 'growth', 'positive', 'up', 'gain', 'profit', 'revenue', 'earnings'],
            'negative': ['bearish', 'sell', 'weak', 'decline', 'negative', 'down', 'loss', 'debt', 'risk', 'volatility'],
            'neutral': ['stable', 'hold', 'maintain', 'steady', 'consistent', 'balanced']
        }

        logger.info(f"Initialized {self.name} v{self.version}")

    def analyze(self, symbol: str, text_data: List[str] = None,
                news_data: List[Dict] = None,
                social_data: List[Dict] = None) -> Dict[str, Any]:
        """
        ניתוח סנטימנט באמצעות GPT

        Args:
            symbol: סמל המניה
            text_data: רשימת טקסטים לניתוח
            news_data: נתוני חדשות
            social_data: נתוני מדיה חברתית

        Returns:
            תוצאות הניתוח
        """
        try:
            logger.info(f"Starting GPT sentiment analysis for {symbol}")

            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")

            # איסוף טקסטים
            all_texts = self._collect_texts(text_data, news_data, social_data)
            
            if not all_texts:
                return self._create_error_result("No text data available")

            # ניתוח סנטימנט
            sentiment_analysis = self._analyze_sentiment_batch(all_texts)

            # ניתוח רגשות
            emotion_analysis = self._analyze_emotions(all_texts)

            # ניתוח מילות מפתח
            keyword_analysis = self._analyze_keywords(all_texts)

            # ניתוח מגמות
            trend_analysis = self._analyze_sentiment_trends(sentiment_analysis)

            # ניתוח ביטחון
            confidence_analysis = self._analyze_confidence(sentiment_analysis)

            # חישוב ציון כללי
            score = self._calculate_sentiment_score(
                sentiment_analysis,
                emotion_analysis,
                keyword_analysis,
                trend_analysis,
                confidence_analysis
            )

            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)

            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)

            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                sentiment_analysis,
                emotion_analysis,
                keyword_analysis,
                trend_analysis,
                confidence_analysis
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
                    "sentiment": sentiment_analysis,
                    "emotions": emotion_analysis,
                    "keywords": keyword_analysis,
                    "trends": trend_analysis,
                    "confidence": confidence_analysis
                },
                "metadata": {
                    "model": self.model,
                    "texts_analyzed": len(all_texts),
                    "sentiment_threshold": self.sentiment_threshold,
                    "confidence_threshold": self.confidence_threshold
                }
            }

            logger.info(f"GPT sentiment analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result

        except Exception as e:
            error_msg = f"Error analyzing sentiment for {symbol}: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result(error_msg)

    def _collect_texts(self, text_data: List[str], news_data: List[Dict],
                      social_data: List[Dict]) -> List[str]:
        """
        איסוף טקסטים מכל המקורות
        """
        texts = []
        
        # טקסטים ישירים
        if text_data:
            texts.extend(text_data)
        
        # טקסטים מחדשות
        if news_data:
            for news in news_data:
                title = news.get('title', '')
                content = news.get('content', '')
                if title:
                    texts.append(title)
                if content:
                    texts.append(content)
        
        # טקסטים ממדיה חברתית
        if social_data:
            for post in social_data:
                content = post.get('content', '')
                if content:
                    texts.append(content)
        
        return texts

    def _analyze_sentiment_batch(self, texts: List[str]) -> Dict[str, Any]:
        """
        ניתוח סנטימנט ב-batch
        """
        try:
            if not self.api_key:
                return self._fallback_sentiment_analysis(texts)

            # חלוקה ל-batches
            batches = [texts[i:i + self.batch_size] 
                      for i in range(0, len(texts), self.batch_size)]
            
            all_sentiments = []
            
            for batch in batches:
                batch_text = "\n".join(batch)
                
                # יצירת prompt
                prompt = self._create_sentiment_prompt(batch_text)
                
                # קריאה ל-API
                response = self._call_openai_api(prompt)
                
                # ניתוח התגובה
                batch_sentiments = self._parse_sentiment_response(response)
                all_sentiments.extend(batch_sentiments)

            # חישוב ממוצעים
            if all_sentiments:
                avg_sentiment = np.mean([s['sentiment'] for s in all_sentiments])
                avg_confidence = np.mean([s['confidence'] for s in all_sentiments])
                sentiment_distribution = self._calculate_sentiment_distribution(all_sentiments)
            else:
                avg_sentiment = 0.5
                avg_confidence = 0.5
                sentiment_distribution = {'positive': 0, 'neutral': 0, 'negative': 0}

            return {
                "average_sentiment": avg_sentiment,
                "average_confidence": avg_confidence,
                "sentiment_distribution": sentiment_distribution,
                "total_texts": len(texts),
                "analyzed_texts": len(all_sentiments),
                "individual_sentiments": all_sentiments
            }

        except Exception as e:
            logger.error(f"Error in batch sentiment analysis: {str(e)}")
            return self._fallback_sentiment_analysis(texts)

    def _create_sentiment_prompt(self, text: str) -> str:
        """
        יצירת prompt לניתוח סנטימנט
        """
        return f"""
        Analyze the sentiment of the following financial text. 
        Consider the context of stock market and financial analysis.
        
        Text: {text}
        
        Please provide a JSON response with the following structure:
        {{
            "sentiment": <float between 0 and 1, where 0=very negative, 0.5=neutral, 1=very positive>,
            "confidence": <float between 0 and 1, indicating confidence in the analysis>,
            "reasoning": "<brief explanation of the sentiment analysis>"
        }}
        
        Focus on financial context, market sentiment, and investment implications.
        """

    def _call_openai_api(self, prompt: str) -> str:
        """
        קריאה ל-OpenAI API
        """
        try:
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial sentiment analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

    def _parse_sentiment_response(self, response: str) -> List[Dict]:
        """
        ניתוח תגובת ה-API
        """
        try:
            # ניסיון לפרסר JSON
            if response.strip().startswith('{'):
                data = json.loads(response)
                return [{
                    'sentiment': float(data.get('sentiment', 0.5)),
                    'confidence': float(data.get('confidence', 0.5)),
                    'reasoning': data.get('reasoning', '')
                }]
            else:
                # fallback לניתוח טקסט
                return [self._parse_text_response(response)]
                
        except Exception as e:
            logger.error(f"Error parsing sentiment response: {str(e)}")
            return [{'sentiment': 0.5, 'confidence': 0.5, 'reasoning': 'Parse error'}]

    def _parse_text_response(self, response: str) -> Dict:
        """
        ניתוח תגובה טקסטואלית
        """
        response_lower = response.lower()
        
        # זיהוי סנטימנט בסיסי
        if any(word in response_lower for word in ['positive', 'bullish', 'good', 'strong']):
            sentiment = 0.7
        elif any(word in response_lower for word in ['negative', 'bearish', 'bad', 'weak']):
            sentiment = 0.3
        else:
            sentiment = 0.5
        
        # זיהוי ביטחון
        if any(word in response_lower for word in ['confident', 'clear', 'definite']):
            confidence = 0.8
        elif any(word in response_lower for word in ['uncertain', 'unclear', 'maybe']):
            confidence = 0.4
        else:
            confidence = 0.6
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'reasoning': response
        }

    def _fallback_sentiment_analysis(self, texts: List[str]) -> Dict[str, Any]:
        """
        ניתוח סנטימנט fallback ללא API
        """
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for text in texts:
            text_lower = text.lower()
            
            positive_matches = sum(1 for word in self.financial_keywords['positive'] 
                                 if word in text_lower)
            negative_matches = sum(1 for word in self.financial_keywords['negative'] 
                                 if word in text_lower)
            neutral_matches = sum(1 for word in self.financial_keywords['neutral'] 
                                if word in text_lower)
            
            if positive_matches > negative_matches:
                positive_count += 1
            elif negative_matches > positive_matches:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(texts)
        if total == 0:
            avg_sentiment = 0.5
        else:
            avg_sentiment = (positive_count * 0.8 + neutral_count * 0.5 + negative_count * 0.2) / total
        
        return {
            "average_sentiment": avg_sentiment,
            "average_confidence": 0.6,
            "sentiment_distribution": {
                'positive': positive_count,
                'neutral': neutral_count,
                'negative': negative_count
            },
            "total_texts": total,
            "analyzed_texts": total,
            "individual_sentiments": []
        }

    def _analyze_emotions(self, texts: List[str]) -> Dict[str, Any]:
        """
        ניתוח רגשות
        """
        emotions = {
            'fear': 0,
            'greed': 0,
            'optimism': 0,
            'pessimism': 0,
            'confidence': 0,
            'uncertainty': 0
        }
        
        emotion_keywords = {
            'fear': ['fear', 'panic', 'crash', 'crisis', 'risk', 'danger'],
            'greed': ['greed', 'fomo', 'moon', 'rocket', 'yolo', 'tendies'],
            'optimism': ['hope', 'recovery', 'bounce', 'rally', 'bullish'],
            'pessimism': ['doom', 'bear', 'decline', 'fall', 'crash'],
            'confidence': ['certain', 'sure', 'definite', 'clear', 'strong'],
            'uncertainty': ['maybe', 'uncertain', 'unclear', 'doubt', 'risk']
        }
        
        for text in texts:
            text_lower = text.lower()
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    emotions[emotion] += 1
        
        # נרמול
        total_texts = len(texts)
        if total_texts > 0:
            emotions = {k: v / total_texts for k, v in emotions.items()}
        
        return emotions

    def _analyze_keywords(self, texts: List[str]) -> Dict[str, Any]:
        """
        ניתוח מילות מפתח
        """
        keyword_counts = defaultdict(int)
        
        for text in texts:
            text_lower = text.lower()
            for category, keywords in self.financial_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        keyword_counts[keyword] += 1
        
        # מיון לפי תדירות
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "keyword_frequency": dict(sorted_keywords[:20]),
            "positive_keywords": sum(1 for k, v in keyword_counts.items() 
                                   if k in self.financial_keywords['positive']),
            "negative_keywords": sum(1 for k, v in keyword_counts.items() 
                                   if k in self.financial_keywords['negative']),
            "neutral_keywords": sum(1 for k, v in keyword_counts.items() 
                                  if k in self.financial_keywords['neutral'])
        }

    def _analyze_sentiment_trends(self, sentiment_analysis: Dict) -> Dict[str, Any]:
        """
        ניתוח מגמות סנטימנט
        """
        individual_sentiments = sentiment_analysis.get('individual_sentiments', [])
        
        if len(individual_sentiments) < 2:
            return {"trend": "stable", "trend_strength": 0.5}
        
        # חישוב מגמה
        sentiments = [s['sentiment'] for s in individual_sentiments]
        
        # חישוב שיפוע
        x = np.arange(len(sentiments))
        slope = np.polyfit(x, sentiments, 1)[0]
        
        # קביעת מגמה
        if slope > 0.05:
            trend = "improving"
        elif slope < -0.05:
            trend = "declining"
        else:
            trend = "stable"
        
        trend_strength = min(abs(slope) * 10, 1.0)
        
        return {
            "trend": trend,
            "trend_strength": trend_strength,
            "slope": slope,
            "volatility": np.std(sentiments)
        }

    def _analyze_confidence(self, sentiment_analysis: Dict) -> Dict[str, Any]:
        """
        ניתוח ביטחון
        """
        individual_sentiments = sentiment_analysis.get('individual_sentiments', [])
        
        if not individual_sentiments:
            return {"average_confidence": 0.5, "confidence_distribution": {}}
        
        confidences = [s['confidence'] for s in individual_sentiments]
        avg_confidence = np.mean(confidences)
        
        # חלוקת ביטחון
        high_confidence = sum(1 for c in confidences if c > 0.8)
        medium_confidence = sum(1 for c in confidences if 0.5 <= c <= 0.8)
        low_confidence = sum(1 for c in confidences if c < 0.5)
        
        return {
            "average_confidence": avg_confidence,
            "confidence_distribution": {
                "high": high_confidence,
                "medium": medium_confidence,
                "low": low_confidence
            },
            "confidence_std": np.std(confidences)
        }

    def _calculate_sentiment_score(self, sentiment_analysis: Dict, emotion_analysis: Dict,
                                 keyword_analysis: Dict, trend_analysis: Dict,
                                 confidence_analysis: Dict) -> float:
        """
        חישוב ציון סנטימנט כללי
        """
        try:
            # משקלות
            weights = {
                'sentiment': 0.4,
                'emotions': 0.2,
                'keywords': 0.15,
                'trend': 0.15,
                'confidence': 0.1
            }

            # ציונים
            sentiment_score = sentiment_analysis.get('average_sentiment', 0.5) * 100
            
            # ציון רגשות (אופטימיות - פחד)
            emotion_score = (
                emotion_analysis.get('optimism', 0) * 100 +
                emotion_analysis.get('confidence', 0) * 50 -
                emotion_analysis.get('fear', 0) * 50 -
                emotion_analysis.get('pessimism', 0) * 50
            )
            
            # ציון מילות מפתח
            total_keywords = (keyword_analysis.get('positive_keywords', 0) + 
                            keyword_analysis.get('negative_keywords', 0) + 
                            keyword_analysis.get('neutral_keywords', 0))
            
            if total_keywords > 0:
                keyword_score = (keyword_analysis.get('positive_keywords', 0) / total_keywords) * 100
            else:
                keyword_score = 50
            
            # ציון מגמה
            trend_score = 50
            if trend_analysis.get('trend') == 'improving':
                trend_score = 80
            elif trend_analysis.get('trend') == 'declining':
                trend_score = 20
            
            # ציון ביטחון
            confidence_score = confidence_analysis.get('average_confidence', 0.5) * 100

            # חישוב ציון משוקלל
            total_score = (
                sentiment_score * weights['sentiment'] +
                emotion_score * weights['emotions'] +
                keyword_score * weights['keywords'] +
                trend_score * weights['trend'] +
                confidence_score * weights['confidence']
            )

            return min(max(total_score, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating sentiment score: {str(e)}")
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
            return "Strong Buy - Very positive sentiment with high confidence"
        elif score >= 60:
            return "Buy - Positive sentiment with good indicators"
        elif score >= 40:
            return "Hold - Neutral sentiment, monitor for changes"
        else:
            return "Sell - Negative sentiment with concerning indicators"

    def _extract_key_signals(self, sentiment_analysis: Dict, emotion_analysis: Dict,
                           keyword_analysis: Dict, trend_analysis: Dict,
                           confidence_analysis: Dict) -> List[str]:
        """
        חילוץ אותות מפתח
        """
        signals = []

        # אותות סנטימנט
        avg_sentiment = sentiment_analysis.get('average_sentiment', 0.5)
        if avg_sentiment > 0.7:
            signals.append(f"Very positive sentiment: {avg_sentiment:.2f}")
        elif avg_sentiment < 0.3:
            signals.append(f"Very negative sentiment: {avg_sentiment:.2f}")

        # אותות רגשות
        if emotion_analysis.get('optimism', 0) > 0.3:
            signals.append("High optimism detected")
        if emotion_analysis.get('fear', 0) > 0.3:
            signals.append("High fear detected")

        # אותות מגמה
        trend = trend_analysis.get('trend', 'stable')
        if trend == 'improving':
            signals.append("Sentiment trend improving")
        elif trend == 'declining':
            signals.append("Sentiment trend declining")

        # אותות ביטחון
        avg_confidence = confidence_analysis.get('average_confidence', 0.5)
        if avg_confidence > 0.8:
            signals.append("High confidence in analysis")
        elif avg_confidence < 0.4:
            signals.append("Low confidence in analysis")

        return signals

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