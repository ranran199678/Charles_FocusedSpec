"""
NLP Analyzer - מנתח טקסטים מתקדם
====================================

רכיב מתקדם לניתוח טקסטים, חדשות, וסנטימנט עם יכולות:
- ניתוח סנטימנט מתקדם
- זיהוי מילות מפתח ונושאים
- ניתוח עוצמת השפעה
- סיכום טקסטים
- זיהוי אירועים חשובים
- ניתוח מגמות בשיח
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import re
from collections import Counter
import logging

# ניסיון לטעון מודלים מתקדמים
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from textblob import TextBlob
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    
    # הורדת נתונים נדרשים
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
        
    NLP_AVAILABLE = True
except Exception as e:
    logging.warning(f"⚠️ NLP libraries not available: {e}")
    NLP_AVAILABLE = False

class NLPAnalyzer:
    def __init__(self, config=None):
        """
        אתחול NLP Analyzer
        
        Args:
            config: מילון קונפיגורציה עם פרמטרים
        """
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.max_text_length = cfg.get("max_text_length", 1000)
        self.min_confidence = cfg.get("min_confidence", 0.6)
        self.cache_duration = timedelta(hours=2)
        
        # מילות מפתח פיננסיות
        self.financial_keywords = cfg.get("financial_keywords", [
            "earnings", "revenue", "profit", "loss", "growth", "decline",
            "beat", "miss", "guidance", "forecast", "outlook", "quarterly",
            "annual", "results", "report", "financial", "performance",
            "acquisition", "merger", "partnership", "deal", "investment",
            "dividend", "buyback", "restructuring", "layoffs", "expansion"
        ])
        
        # מילות מפתח טכניות
        self.technical_keywords = cfg.get("technical_keywords", [
            "breakout", "support", "resistance", "trend", "momentum",
            "volume", "volatility", "pattern", "chart", "technical",
            "moving average", "rsi", "macd", "bollinger", "fibonacci"
        ])
        
        # מילות מפתח רגשיות
        self.emotional_keywords = cfg.get("emotional_keywords", {
            "positive": ["bullish", "optimistic", "strong", "growth", "beat", "surge", "rally", "profit", "gain", "rise", "positive", "good", "excellent", "strong", "beat expectations", "exceed", "outperform"],
            "negative": ["bearish", "pessimistic", "weak", "decline", "miss", "drop", "crash", "loss", "fall", "negative", "bad", "poor", "dismal", "layoffs", "restructuring", "cut", "reduce", "decrease", "underperform", "disappoint"],
            "neutral": ["stable", "steady", "maintain", "hold", "neutral", "earnings", "report", "quarterly", "financial"]
        })
        
        # ביטויים שליליים מורכבים
        self.negative_phrases = cfg.get("negative_phrases", [
            "dismal earnings", "missed expectations", "declines", "layoffs", "restructuring", 
            "weak performance", "poor results", "disappointing", "underperformed", "cut jobs",
            "reduced guidance", "lower than expected", "disappointing earnings", "declined",
            "fell short", "disappointed investors", "negative outlook", "weak guidance"
        ])
        
        # ביטויים חיוביים מורכבים
        self.positive_phrases = cfg.get("positive_phrases", [
            "beat earnings", "exceeded expectations", "strong performance", "positive results",
            "excellent quarter", "outperformed", "increased guidance", "higher than expected",
            "impressive earnings", "surged", "rallied", "positive outlook", "strong guidance",
            "record earnings", "strong growth", "excellent performance"
        ])
        
        # API keys
        self.marketaux_key = cfg.get("marketaux_key", "Dx8X1gzfxklRC5WETItJAncifB4bXp98EnSqzT6P")
        self.newsdata_key = cfg.get("newsdata_key", "pub_a54510d1206a48d39dd48b3b3b624a2f")
        
        # Cache
        self.analysis_cache = {}
        
        # אתחול מודלים (אם זמינים)
        self.sentiment_model = None
        self.summarizer_model = None
        self._initialize_models()
        
    def _initialize_models(self):
        """אתחול מודלים מתקדמים"""
        if not NLP_AVAILABLE:
            return
            
        try:
            # מודל סנטימנט מתקדם
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                return_all_scores=True
            )
        except Exception as e:
            logging.warning(f"⚠️ לא ניתן לטעון מודל sentiment: {e}")
            
        try:
            # מודל סיכום
            self.summarizer_model = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6"
            )
        except Exception as e:
            logging.warning(f"⚠️ לא ניתן לטעון מודל summarizer: {e}")
    
    def analyze(self, symbol: str, price_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        ניתוח NLP מקיף עבור מניה
        
        Args:
            symbol: סימבול המניה
            price_df: נתוני מחירים (לא נדרש כרגע)
            
        Returns:
            מילון עם תוצאות הניתוח
        """
        try:
            # בדיקה אם יש תוצאות ב-cache
            cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H')}"
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                if datetime.now() - cached_result['timestamp'] < self.cache_duration:
                    return cached_result['data']
            
            # איסוף טקסטים לניתוח
            texts = self._collect_texts(symbol)
            
            # ניתוח מקיף
            analysis = self._perform_analysis(texts, symbol)
            
            # בניית תוצאה
            result = {
                'score': analysis['overall_score'],
                'sentiment': analysis['sentiment'],
                'topics': analysis['topics'],
                'key_phrases': analysis['key_phrases'],
                'summary': analysis['summary'],
                'details': analysis['details'],
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol
            }
            
            # שמירה ב-cache
            self.analysis_cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }
            
            return result
            
        except Exception as e:
            logging.error(f"שגיאה בניתוח NLP עבור {symbol}: {e}")
            return {
                'score': 1,
                'sentiment': 'neutral',
                'topics': [],
                'key_phrases': [],
                'summary': f"שגיאה בניתוח: {str(e)}",
                'details': {},
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol
            }
    
    def _collect_texts(self, symbol: str) -> List[Dict]:
        """איסוף טקסטים לניתוח"""
        texts = []
        
        try:
            # חדשות מהמניה
            news_texts = self._fetch_news_texts(symbol)
            texts.extend(news_texts)
            
            # טקסטים נוספים (אפשר להוסיף)
            # - רשתות חברתיות
            # - דוחות אנליסטים
            # - פורומים פיננסיים
            
        except Exception as e:
            logging.error(f"שגיאה באיסוף טקסטים: {e}")
        
        return texts
    
    def _fetch_news_texts(self, symbol: str) -> List[Dict]:
        """שליפת טקסטים מחדשות עם סינון רלוונטיות"""
        texts = []
        
        try:
            # שימוש ב-DataFetcher החדש עם כל המקורות
            from utils.data_fetcher import DataFetcher
            data_fetcher = DataFetcher()
            
            # שליפת חדשות מכל המקורות
            enhanced_news = data_fetcher.fetch_enhanced_news_batch([symbol], 5)
            
            if symbol in enhanced_news:
                articles = enhanced_news[symbol]
                
                for article in articles:
                    title = article.get('title', '')
                    summary = article.get('summary', '')
                    source = article.get('source', 'Unknown')
                    relevance_score = article.get('relevance_score', 0)
                    
                    # רק מאמרים רלוונטיים
                    if relevance_score > 0.3:
                        text = f"{title}. {summary}"
                        
                        texts.append({
                            'text': text,
                            'title': title,
                            'source': source,
                            'sentiment': article.get('sentiment', {}).get('label', 'neutral'),
                            'published_at': article.get('published_at', ''),
                            'relevance_score': relevance_score
                        })
            
            # אם לא נמצאו מספיק טקסטים, ננסה את המקורות הישנים
            if len(texts) < 2:
                # MarketAux API (גיבוי)
                url = f"https://api.marketaux.com/v1/news/all?symbols={symbol}&language=en&limit=5&api_token={self.marketaux_key}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('data', [])
                    
                    for article in articles:
                        title = article.get('title', '')
                        description = article.get('description', '')
                        
                        # בדיקת רלוונטיות - האם הכתבה באמת על המניה?
                        if self._is_relevant_to_symbol(title, description, symbol):
                            text = f"{title}. {description}"
                            
                            texts.append({
                                'text': text,
                                'title': title,
                                'source': 'marketaux',
                                'sentiment': article.get('sentiment', 'neutral'),
                                'published_at': article.get('published_at', ''),
                                'relevance_score': self._calculate_relevance_score(title, description, symbol)
                            })
                
                # NewsData API (גיבוי נוסף)
                if len(texts) < 2:
                    url2 = f"https://newsdata.io/api/1/news?apikey={self.newsdata_key}&q={symbol}&language=en&category=business"
                    response2 = requests.get(url2, timeout=10)
                    
                    if response2.status_code == 200:
                        data2 = response2.json()
                        articles2 = data2.get('results', [])
                        
                        for article in articles2[:3]:
                            title = article.get('title', '')
                            description = article.get('description', '')
                            
                            if self._is_relevant_to_symbol(title, description, symbol):
                                text = f"{title}. {description}"
                                
                                texts.append({
                                    'text': text,
                                    'title': title,
                                    'source': 'newsdata',
                                    'sentiment': 'neutral',
                                    'published_at': article.get('pubDate', ''),
                                    'relevance_score': self._calculate_relevance_score(title, description, symbol)
                                })
                        
        except Exception as e:
            logging.error(f"שגיאה בשליפת חדשות: {e}")
        
        # מיון לפי רלוונטיות
        texts.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return texts
    
    def _is_relevant_to_symbol(self, title: str, description: str, symbol: str) -> bool:
        """בדיקה האם הכתבה רלוונטית למניה"""
        text = f"{title} {description}".lower()
        symbol_lower = symbol.lower()
        
        # בדיקה ישירה של שם המניה
        if symbol_lower in text:
            return True
        
        # בדיקת שמות חברות ידועות
        company_names = {
            'INTC': ['intel', 'intel corporation'],
            'AAPL': ['apple', 'apple inc'],
            'TSLA': ['tesla', 'tesla inc'],
            'NVDA': ['nvidia', 'nvidia corporation'],
            'MSFT': ['microsoft', 'microsoft corporation'],
            'GOOGL': ['google', 'alphabet', 'alphabet inc'],
            'AMZN': ['amazon', 'amazon.com'],
            'META': ['meta', 'facebook', 'meta platforms']
        }
        
        if symbol in company_names:
            for name in company_names[symbol]:
                if name in text:
                    return True
        
        # בדיקה של מילות מפתח פיננסיות + שם המניה
        financial_keywords = ['earnings', 'revenue', 'profit', 'stock', 'shares', 'trading']
        has_financial = any(keyword in text for keyword in financial_keywords)
        
        if has_financial and symbol_lower in text:
            return True
        
        return False
    
    def _calculate_relevance_score(self, title: str, description: str, symbol: str) -> float:
        """חישוב ציון רלוונטיות"""
        text = f"{title} {description}".lower()
        symbol_lower = symbol.lower()
        score = 0.0
        
        # נקודות לפי מיקום שם המניה
        if symbol_lower in title.lower():
            score += 3.0  # שם המניה בכותרת
        elif symbol_lower in description.lower():
            score += 2.0  # שם המניה בתיאור
        
        # נקודות לפי מילות מפתח פיננסיות
        financial_keywords = ['earnings', 'revenue', 'profit', 'stock', 'shares', 'trading', 'quarterly', 'results']
        for keyword in financial_keywords:
            if keyword in text:
                score += 0.5
        
        # נקודות לפי מילות מפתח שליליות (חשובות יותר)
        negative_keywords = ['dismal', 'layoffs', 'declines', 'missed', 'disappointing', 'poor']
        for keyword in negative_keywords:
            if keyword in text:
                score += 1.0  # משקל גבוה יותר לחדשות שליליות
        
        return score
    
    def _perform_analysis(self, texts: List[Dict], symbol: str) -> Dict:
        """ביצוע ניתוח NLP מקיף עם יכולות מתקדמות"""
        if not texts:
            return {
                'overall_score': 1,
                'sentiment': 'neutral',
                'topics': [],
                'key_phrases': [],
                'summary': 'לא נמצאו טקסטים לניתוח',
                'details': {}
            }
        
        # ניתוח מתקדם כולל
        advanced_analysis = self._perform_advanced_analysis(texts, symbol)
        
        # ניתוח סנטימנט
        sentiment_analysis = advanced_analysis['sentiment_analysis']
        
        # זיהוי נושאים
        topics = self._extract_topics(texts)
        
        # זיהוי ביטויים מפתח
        key_phrases = self._extract_key_phrases(texts)
        
        # ניתוח עוצמת השפעה
        impact_analysis = advanced_analysis['impact_analysis']
        
        # ניתוח מגמות
        trend_analysis = advanced_analysis['trend_analysis']
        
        # זיהוי אירועים
        event_analysis = advanced_analysis['event_analysis']
        
        # ניתוח הקשר שוק
        market_context = advanced_analysis['market_context']
        
        # סיכום מתקדם
        summary = self._generate_advanced_summary(texts, sentiment_analysis, topics, trend_analysis, event_analysis)
        
        # חישוב ציון כולל עם משקלים מתקדמים
        overall_score = self._calculate_advanced_score(sentiment_analysis, impact_analysis, topics, trend_analysis, event_analysis)
        
        return {
            'overall_score': overall_score,
            'sentiment': sentiment_analysis['dominant_sentiment'],
            'topics': topics,
            'key_phrases': key_phrases,
            'summary': summary,
            'details': {
                'sentiment_analysis': sentiment_analysis,
                'impact_analysis': impact_analysis,
                'trend_analysis': trend_analysis,
                'event_analysis': event_analysis,
                'market_context': market_context,
                'text_count': len(texts)
            }
        }

    def _generate_advanced_summary(self, texts: List[Dict], sentiment_analysis: Dict, topics: List[Dict], trend_analysis: Dict, event_analysis: Dict) -> str:
        """סיכום מתקדם עם ניתוח מגמות ואירועים"""
        summary_parts = []
        
        # סנטימנט דומיננטי
        dominant_sentiment = sentiment_analysis.get('dominant_sentiment', 'neutral')
        confidence = sentiment_analysis.get('confidence', 0)
        summary_parts.append(f"סנטימנט דומיננטי: {dominant_sentiment} (ביטחון: {confidence:.1%})")
        
        # מגמות
        trend_direction = trend_analysis.get('trend_direction', 'stable')
        trend_strength = trend_analysis.get('trend_strength', 0)
        if trend_direction != 'stable':
            summary_parts.append(f"מגמה: {trend_direction} (עוצמה: {trend_strength:.1%})")
        
        # אירועים חשובים
        total_events = event_analysis.get('total_events', 0)
        if total_events > 0:
            important_events = []
            for event_type, events in event_analysis.get('events', {}).items():
                if events:
                    important_events.append(f"{event_type}: {len(events)} אירועים")
            if important_events:
                summary_parts.append(f"אירועים חשובים: {', '.join(important_events)}")
        
        # נושאים
        if topics:
            topic_summary = []
            for topic in topics[:3]:  # רק 3 הראשונים
                category = topic.get('category', 'unknown')
                keywords = topic.get('keywords', [])
                if keywords:
                    topic_summary.append(f"{category}: {', '.join(keywords[:3])}")
            if topic_summary:
                summary_parts.append(f"נושאים: {', '.join(topic_summary)}")
        
        # כמות טקסטים
        summary_parts.append(f"טקסטים נותחו: {len(texts)}")
        
        return '. '.join(summary_parts)

    def _calculate_advanced_score(self, sentiment_analysis: Dict, impact_analysis: Dict, topics: List[Dict], trend_analysis: Dict, event_analysis: Dict) -> int:
        """חישוב ציון מתקדם עם משקלים נוספים"""
        base_score = 50  # ציון בסיס
        
        # משקל סנטימנט
        dominant_sentiment = sentiment_analysis.get('dominant_sentiment', 'neutral')
        if dominant_sentiment == 'positive':
            base_score += 20
        elif dominant_sentiment == 'negative':
            base_score -= 30  # עונש גבוה יותר לסנטימנט שלילי
        
        # משקל מגמות
        trend_direction = trend_analysis.get('trend_direction', 'stable')
        trend_strength = trend_analysis.get('trend_strength', 0)
        if trend_direction == 'improving':
            base_score += int(trend_strength * 15)
        elif trend_direction == 'declining':
            base_score -= int(trend_strength * 20)
        
        # משקל אירועים
        total_events = event_analysis.get('total_events', 0)
        if total_events > 0:
            # בדיקה אם יש אירועים שליליים
            negative_events = 0
            for event_type, events in event_analysis.get('events', {}).items():
                for event in events:
                    if event.get('sentiment') == 'negative':
                        negative_events += 1
            
            if negative_events > 0:
                base_score -= negative_events * 10  # עונש על אירועים שליליים
        
        # משקל נושאים
        if topics:
            important_topics = sum(1 for topic in topics if topic.get('importance') == 'high')
            base_score += important_topics * 5
        
        # הגבלה לטווח 1-100
        return max(1, min(100, base_score))

    def _analyze_sentiment(self, texts: List[Dict]) -> Dict:
        """ניתוח סנטימנט מתקדם"""
        if not NLP_AVAILABLE:
            return self._basic_sentiment_analysis(texts)
        
        try:
            all_scores = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for text_item in texts:
                text = text_item['text']
                
                # ניתוח עם מודל מתקדם
                if self.sentiment_model:
                    result = self.sentiment_model(text[:self.max_text_length])
                    scores = result[0]
                    
                    # חישוב ציון
                    positive_score = scores[1]['score'] if len(scores) > 1 else 0.5
                    negative_score = scores[0]['score'] if len(scores) > 0 else 0.5
                    
                    sentiment_score = positive_score - negative_score
                    all_scores.append(sentiment_score)
                    
                    # סיווג
                    if sentiment_score > 0.2:
                        positive_count += 1
                    elif sentiment_score < -0.2:
                        negative_count += 1
                    else:
                        neutral_count += 1
                else:
                    # ניתוח בסיסי
                    try:
                        from textblob import TextBlob
                        blob = TextBlob(text)
                        sentiment_score = blob.sentiment.polarity
                        all_scores.append(sentiment_score)
                        
                        if sentiment_score > 0.1:
                            positive_count += 1
                        elif sentiment_score < -0.1:
                            negative_count += 1
                        else:
                            neutral_count += 1
                    except ImportError:
                        # ניתוח בסיסי ללא TextBlob
                        sentiment_score = 0
                        all_scores.append(sentiment_score)
                        neutral_count += 1
            
            # חישוב סנטימנט דומיננטי
            import numpy as np
            avg_score = np.mean(all_scores) if all_scores else 0
            total_texts = len(texts)
            
            if positive_count > negative_count and positive_count > neutral_count:
                dominant_sentiment = 'positive'
            elif negative_count > positive_count and negative_count > neutral_count:
                dominant_sentiment = 'negative'
            else:
                dominant_sentiment = 'neutral'
            
            return {
                'dominant_sentiment': dominant_sentiment,
                'average_score': avg_score,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_texts': total_texts,
                'confidence': max(positive_count, negative_count, neutral_count) / total_texts if total_texts > 0 else 0
            }
            
        except Exception as e:
            logging.error(f"שגיאה בניתוח סנטימנט: {e}")
            return self._basic_sentiment_analysis(texts)
    
    def _basic_sentiment_analysis(self, texts: List[Dict]) -> Dict:
        """ניתוח סנטימנט בסיסי משופר"""
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for text_item in texts:
            text = text_item['text'].lower()
            
            # בדיקת ביטויים מורכבים קודם (חשיבות גבוהה יותר)
            pos_phrases = sum(1 for phrase in self.positive_phrases if phrase in text)
            neg_phrases = sum(1 for phrase in self.negative_phrases if phrase in text)
            
            # ספירת מילות מפתח רגשיות
            pos_words = sum(1 for word in self.emotional_keywords['positive'] if word in text)
            neg_words = sum(1 for word in self.emotional_keywords['negative'] if word in text)
            neu_words = sum(1 for word in self.emotional_keywords['neutral'] if word in text)
            
            # משקל גבוה יותר לביטויים מורכבים
            pos_score = pos_phrases * 3 + pos_words
            neg_score = neg_phrases * 3 + neg_words
            
            # בדיקה מיוחדת למילים שליליות חזקות
            strong_negative_words = ['dismal', 'layoffs', 'declines', 'missed', 'disappointing', 'poor']
            strong_neg_count = sum(1 for word in strong_negative_words if word in text)
            neg_score += strong_neg_count * 2
            
            if pos_score > neg_score and pos_score > neu_words:
                positive_count += 1
            elif neg_score > pos_score and neg_score > neu_words:
                negative_count += 1
            else:
                neutral_count += 1
        
        total_texts = len(texts)
        
        if positive_count > negative_count and positive_count > neutral_count:
            dominant_sentiment = 'positive'
        elif negative_count > positive_count and negative_count > neutral_count:
            dominant_sentiment = 'negative'
        else:
            dominant_sentiment = 'neutral'
        
        return {
            'dominant_sentiment': dominant_sentiment,
            'average_score': 0.5,  # ניטרלי
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_texts': total_texts,
            'confidence': max(positive_count, negative_count, neutral_count) / total_texts if total_texts > 0 else 0
        }
    
    def _extract_topics(self, texts: List[Dict]) -> List[Dict]:
        """זיהוי נושאים מרכזיים"""
        if not NLP_AVAILABLE:
            return self._basic_topic_extraction(texts)
        
        try:
            all_words = []
            for text_item in texts:
                text = text_item['text']
                words = word_tokenize(text.lower())
                all_words.extend(words)
            
            # הסרת stop words
            stop_words = set(stopwords.words('english'))
            filtered_words = [word for word in all_words if word.isalnum() and word not in stop_words]
            
            # ספירת מילים
            word_counts = Counter(filtered_words)
            
            # זיהוי נושאים לפי מילות מפתח
            topics = []
            
            # נושאים פיננסיים
            financial_words = [word for word in filtered_words if word in self.financial_keywords]
            if financial_words:
                topics.append({
                    'category': 'financial',
                    'keywords': list(set(financial_words)),
                    'frequency': len(financial_words),
                    'importance': 'high'
                })
            
            # נושאים טכניים
            technical_words = [word for word in filtered_words if word in self.technical_keywords]
            if technical_words:
                topics.append({
                    'category': 'technical',
                    'keywords': list(set(technical_words)),
                    'frequency': len(technical_words),
                    'importance': 'medium'
                })
            
            # נושאים כלליים (מילים נפוצות)
            common_words = word_counts.most_common(10)
            general_topics = [word for word, count in common_words if count > 2]
            if general_topics:
                topics.append({
                    'category': 'general',
                    'keywords': general_topics,
                    'frequency': sum(count for word, count in common_words if word in general_topics),
                    'importance': 'low'
                })
            
            return topics
            
        except Exception as e:
            logging.error(f"שגיאה בזיהוי נושאים: {e}")
            return self._basic_topic_extraction(texts)
    
    def _basic_topic_extraction(self, texts: List[Dict]) -> List[Dict]:
        """זיהוי נושאים בסיסי"""
        topics = []
        
        # זיהוי לפי מילות מפתח ידועות
        for text_item in texts:
            text = text_item['text'].lower()
            
            # נושאים פיננסיים
            financial_found = [word for word in self.financial_keywords if word in text]
            if financial_found:
                topics.append({
                    'category': 'financial',
                    'keywords': financial_found,
                    'frequency': len(financial_found),
                    'importance': 'high'
                })
            
            # נושאים טכניים
            technical_found = [word for word in self.technical_keywords if word in text]
            if technical_found:
                topics.append({
                    'category': 'technical',
                    'keywords': technical_found,
                    'frequency': len(technical_found),
                    'importance': 'medium'
                })
        
        return topics
    
    def _extract_key_phrases(self, texts: List[Dict]) -> List[str]:
        """זיהוי ביטויים מפתח"""
        key_phrases = []
        
        for text_item in texts:
            text = text_item['text']
            
            # זיהוי ביטויים לפי מילות מפתח
            for keyword in self.financial_keywords + self.technical_keywords:
                if keyword in text.lower():
                    # חילוץ משפט שלם
                    sentences = sent_tokenize(text) if NLP_AVAILABLE else text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            key_phrases.append(sentence.strip())
                            break
        
        return list(set(key_phrases))[:5]  # מקסימום 5 ביטויים
    
    def _analyze_impact(self, texts: List[Dict], symbol: str) -> Dict:
        """ניתוח עוצמת השפעה"""
        impact_score = 1
        
        # ניתוח לפי כמות טקסטים
        text_count = len(texts)
        if text_count > 10:
            impact_score += 20
        elif text_count > 5:
            impact_score += 10
        
        # ניתוח לפי מילות מפתח חשובות
        important_keywords = ['earnings', 'revenue', 'profit', 'loss', 'guidance', 'forecast']
        keyword_count = 0
        
        for text_item in texts:
            text = text_item['text'].lower()
            for keyword in important_keywords:
                if keyword in text:
                    keyword_count += 1
        
        if keyword_count > 5:
            impact_score += 30
        elif keyword_count > 2:
            impact_score += 15
        
        # ניתוח לפי סנטימנט
        sentiment_scores = []
        for text_item in texts:
            if text_item.get('sentiment') == 'positive':
                sentiment_scores.append(1)
            elif text_item.get('sentiment') == 'negative':
                sentiment_scores.append(-1)
            else:
                sentiment_scores.append(0)
        
        avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
        impact_score += int(avg_sentiment * 20)
        
        return {
            'impact_score': min(100, max(1, impact_score)),
            'text_count': text_count,
            'keyword_count': keyword_count,
            'sentiment_influence': avg_sentiment
        }
    
    def _generate_summary(self, texts: List[Dict], sentiment_analysis: Dict, topics: List[Dict]) -> str:
        """יצירת סיכום"""
        if not texts:
            return "לא נמצאו טקסטים לניתוח"
        
        summary_parts = []
        
        # סיכום סנטימנט
        sentiment = sentiment_analysis['dominant_sentiment']
        confidence = sentiment_analysis['confidence']
        summary_parts.append(f"סנטימנט דומיננטי: {sentiment} (ביטחון: {confidence:.1%})")
        
        # סיכום נושאים
        if topics:
            topic_summary = []
            for topic in topics:
                topic_summary.append(f"{topic['category']}: {len(topic['keywords'])} מילות מפתח")
            summary_parts.append(f"נושאים: {', '.join(topic_summary)}")
        
        # סיכום כמותי
        summary_parts.append(f"טקסטים נותחו: {len(texts)}")
        
        return ". ".join(summary_parts)
    
    def _calculate_overall_score(self, sentiment_analysis: Dict, impact_analysis: Dict, topics: List[Dict]) -> int:
        """חישוב ציון כולל משופר עם משקל גבוה לחדשות שליליות"""
        score = 1
        
        # בסיס לפי סנטימנט
        sentiment = sentiment_analysis['dominant_sentiment']
        if sentiment == 'positive':
            score += 30
        elif sentiment == 'negative':
            score += 3  # הורדה משמעותית יותר לסנטימנט שלילי
        else:
            score += 20
        
        # תוספת לפי ביטחון
        confidence = sentiment_analysis['confidence']
        score += int(confidence * 20)
        
        # תוספת לפי השפעה
        impact_score = impact_analysis['impact_score']
        score += int(impact_score * 0.3)
        
        # תוספת לפי נושאים חשובים
        important_topics = [topic for topic in topics if topic['importance'] == 'high']
        score += len(important_topics) * 10
        
        # קנס חזק על סנטימנט שלילי
        negative_count = sentiment_analysis.get('negative_count', 0)
        positive_count = sentiment_analysis.get('positive_count', 0)
        
        if negative_count > positive_count:
            score = max(1, score - 40)  # קנס חזק יותר של 40 נקודות
        
        # קנס נוסף על חדשות שליליות חזקות
        if negative_count >= 2:  # אם יש 2 או יותר חדשות שליליות
            score = max(1, score - 30)  # קנס נוסף של 30 נקודות
        
        # בונוס על סנטימנט חיובי חזק
        if positive_count > negative_count and positive_count > 0:
            score = min(100, score + 10)  # בונוס של 10 נקודות
        
        return min(100, max(1, score))
    
    def get_sentiment_analysis(self, symbol: str) -> Dict:
        """קבלת ניתוח סנטימנט בלבד"""
        result = self.analyze(symbol)
        return {
            'sentiment': result['sentiment'],
            'details': result['details'].get('sentiment_analysis', {})
        }
    
    def get_topic_analysis(self, symbol: str) -> List[Dict]:
        """קבלת ניתוח נושאים בלבד"""
        result = self.analyze(symbol)
        return result['topics']
    
    def get_key_phrases(self, symbol: str) -> List[str]:
        """קבלת ביטויים מפתח בלבד"""
        result = self.analyze(symbol)
        return result['key_phrases'] 

    def _analyze_trends(self, texts: List[Dict]) -> Dict:
        """
        ניתוח מגמות לאורך זמן
        """
        try:
            # ניתוח מגמות לפי תאריכים
            from datetime import datetime, timedelta
            
            # חלוקה לפי ימים
            daily_sentiments = {}
            
            for text_data in texts:
                published_at = text_data.get('published_at', '')
                if published_at:
                    try:
                        # ניסיון לפרסר תאריך
                        date_formats = [
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%d',
                            '%d/%m/%Y',
                            '%m/%d/%Y'
                        ]
                        
                        date = None
                        for fmt in date_formats:
                            try:
                                date = datetime.strptime(published_at[:19], fmt)
                                break
                            except ValueError:
                                continue
                        
                        if date:
                            day_key = date.strftime('%Y-%m-%d')
                            if day_key not in daily_sentiments:
                                daily_sentiments[day_key] = {'positive': 0, 'negative': 0, 'neutral': 0}
                            
                            sentiment = text_data.get('sentiment', 'neutral')
                            if sentiment == 'positive':
                                daily_sentiments[day_key]['positive'] += 1
                            elif sentiment == 'negative':
                                daily_sentiments[day_key]['negative'] += 1
                            else:
                                daily_sentiments[day_key]['neutral'] += 1
                                
                    except Exception:
                        continue
            
            # חישוב מגמות
            trend_analysis = {
                'daily_sentiments': daily_sentiments,
                'trend_direction': 'stable',
                'trend_strength': 0.0,
                'recent_change': 0.0
            }
            
            if len(daily_sentiments) >= 2:
                # חישוב מגמה
                dates = sorted(daily_sentiments.keys())
                recent_dates = dates[-3:] if len(dates) >= 3 else dates
                
                recent_positive = sum(daily_sentiments[date]['positive'] for date in recent_dates)
                recent_negative = sum(daily_sentiments[date]['negative'] for date in recent_dates)
                
                if len(dates) >= 4:
                    older_dates = dates[:-3]
                    older_positive = sum(daily_sentiments[date]['positive'] for date in older_dates)
                    older_negative = sum(daily_sentiments[date]['negative'] for date in older_dates)
                    
                    # חישוב שינוי
                    recent_ratio = recent_positive / (recent_positive + recent_negative) if (recent_positive + recent_negative) > 0 else 0.5
                    older_ratio = older_positive / (older_positive + older_negative) if (older_positive + older_negative) > 0 else 0.5
                    
                    trend_analysis['recent_change'] = recent_ratio - older_ratio
                    
                    if trend_analysis['recent_change'] > 0.1:
                        trend_analysis['trend_direction'] = 'improving'
                        trend_analysis['trend_strength'] = min(abs(trend_analysis['recent_change']) * 10, 1.0)
                    elif trend_analysis['recent_change'] < -0.1:
                        trend_analysis['trend_direction'] = 'declining'
                        trend_analysis['trend_strength'] = min(abs(trend_analysis['recent_change']) * 10, 1.0)
            
            return trend_analysis
            
        except Exception as e:
            logging.warning(f"שגיאה בניתוח מגמות: {e}")
            return {
                'daily_sentiments': {},
                'trend_direction': 'stable',
                'trend_strength': 0.0,
                'recent_change': 0.0
            }

    def _analyze_events(self, texts: List[Dict]) -> Dict:
        """
        זיהוי אירועים חשובים
        """
        events = {
            'earnings_reports': [],
            'guidance_changes': [],
            'restructuring': [],
            'management_changes': [],
            'product_launches': [],
            'regulatory_issues': []
        }
        
        event_keywords = {
            'earnings_reports': ['earnings', 'quarterly', 'financial results', 'revenue', 'profit'],
            'guidance_changes': ['guidance', 'forecast', 'outlook', 'expectations'],
            'restructuring': ['layoffs', 'restructuring', 'reorganization', 'cost cutting'],
            'management_changes': ['ceo', 'executive', 'leadership', 'management'],
            'product_launches': ['launch', 'release', 'announcement', 'new product'],
            'regulatory_issues': ['regulatory', 'investigation', 'lawsuit', 'legal']
        }
        
        for text_data in texts:
            text = text_data.get('text', '').lower()
            title = text_data.get('title', '').lower()
            full_text = f"{title} {text}"
            
            for event_type, keywords in event_keywords.items():
                if any(keyword in full_text for keyword in keywords):
                    events[event_type].append({
                        'title': text_data.get('title', ''),
                        'source': text_data.get('source', ''),
                        'sentiment': text_data.get('sentiment', 'neutral'),
                        'relevance_score': text_data.get('relevance_score', 0)
                    })
        
        # חישוב חשיבות אירועים
        event_importance = {}
        for event_type, event_list in events.items():
            if event_list:
                # חישוב חשיבות לפי כמות, רלוונטיות וסנטימנט
                total_relevance = sum(event.get('relevance_score', 0) for event in event_list)
                negative_count = sum(1 for event in event_list if event.get('sentiment') == 'negative')
                
                importance = (total_relevance / len(event_list)) * (1 + negative_count * 0.5)
                event_importance[event_type] = min(importance, 1.0)
            else:
                event_importance[event_type] = 0.0
        
        return {
            'events': events,
            'importance': event_importance,
            'total_events': sum(len(event_list) for event_list in events.values())
        }

    def _analyze_market_context(self, texts: List[Dict], symbol: str) -> Dict:
        """
        ניתוח הקשר שוק
        """
        market_context = {
            'sector_performance': 'neutral',
            'competitor_mentions': [],
            'market_sentiment': 'neutral',
            'industry_trends': []
        }
        
        # זיהוי אזכורי מתחרים
        competitors = {
            'INTC': ['amd', 'nvidia', 'qualcomm', 'broadcom'],
            'AAPL': ['samsung', 'google', 'microsoft', 'amazon'],
            'TSLA': ['ford', 'gm', 'volkswagen', 'toyota'],
            'NVDA': ['amd', 'intel', 'qualcomm', 'broadcom'],
            'MSFT': ['google', 'amazon', 'apple', 'oracle']
        }
        
        if symbol in competitors:
            for text_data in texts:
                text = text_data.get('text', '').lower()
                for competitor in competitors[symbol]:
                    if competitor in text:
                        market_context['competitor_mentions'].append({
                            'competitor': competitor,
                            'context': text_data.get('title', ''),
                            'sentiment': text_data.get('sentiment', 'neutral')
                        })
        
        # זיהוי מגמות תעשייה
        industry_keywords = {
            'AI': ['artificial intelligence', 'ai', 'machine learning', 'deep learning'],
            'Chip': ['semiconductor', 'chip', 'processor', 'silicon'],
            'Cloud': ['cloud computing', 'aws', 'azure', 'google cloud'],
            'EV': ['electric vehicle', 'ev', 'battery', 'autonomous'],
            'Fintech': ['fintech', 'digital payment', 'blockchain', 'cryptocurrency']
        }
        
        for trend, keywords in industry_keywords.items():
            for text_data in texts:
                text = text_data.get('text', '').lower()
                if any(keyword in text for keyword in keywords):
                    market_context['industry_trends'].append({
                        'trend': trend,
                        'context': text_data.get('title', ''),
                        'sentiment': text_data.get('sentiment', 'neutral')
                    })
        
        return market_context

    def _perform_advanced_analysis(self, texts: List[Dict], symbol: str) -> Dict:
        """
        ניתוח מתקדם כולל
        """
        # ניתוח מגמות
        trend_analysis = self._analyze_trends(texts)
        
        # זיהוי אירועים
        event_analysis = self._analyze_events(texts)
        
        # ניתוח הקשר שוק
        market_context = self._analyze_market_context(texts, symbol)
        
        # ניתוח סנטימנט מתקדם
        sentiment_analysis = self._analyze_sentiment(texts)
        
        # ניתוח השפעה
        impact_analysis = self._analyze_impact(texts, symbol)
        
        return {
            'trend_analysis': trend_analysis,
            'event_analysis': event_analysis,
            'market_context': market_context,
            'sentiment_analysis': sentiment_analysis,
            'impact_analysis': impact_analysis
        } 