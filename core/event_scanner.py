"""
Event Scanner - סורק אירועים גיאופוליטיים, כלכליים ורגולטוריים
========================================================================

מזהה אירועים חיצוניים שעלולים להשפיע על מניות ספציפיות או השוק הכללי.
כולל:
- אירועים גיאופוליטיים (מלחמות, סנקציות, מתחים בינלאומיים)
- אירועים כלכליים (שינויי ריבית, אינפלציה, צמיחה)
- אירועים רגולטוריים (שינויי רגולציה, אישורים, חקיקה)

מחזיר ציון השפעה (1-100) ופרטים על האירועים הרלוונטיים.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import re

from utils.credentials import APICredentials
from utils.data_fetcher import compute_sentiment_label_score

class EventScanner:
    def __init__(self, config=None):
        """
        אתחול Event Scanner
        
        Args:
            config: מילון קונפיגורציה עם פרמטרים
        """
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.lookback_days = cfg.get("lookback_days", 7)
        self.min_impact_score = cfg.get("min_impact_score", 0.3)
        self.max_events_per_category = cfg.get("max_events_per_category", 5)
        
        # מילות מפתח לאירועים גיאופוליטיים
        self.geopolitical_keywords = cfg.get("geopolitical_keywords", [
            "war", "conflict", "sanctions", "embargo", "tension", "crisis",
            "invasion", "attack", "protest", "revolution", "coup", "election",
            "diplomatic", "trade war", "tariffs", "boycott"
        ])
        
        # מילות מפתח לאירועים כלכליים
        self.economic_keywords = cfg.get("economic_keywords", [
            "interest rate", "inflation", "recession", "growth", "GDP",
            "unemployment", "consumer spending", "manufacturing", "trade deficit",
            "federal reserve", "central bank", "monetary policy", "fiscal policy"
        ])
        
        # מילות מפתח לאירועים רגולטוריים
        self.regulatory_keywords = cfg.get("regulatory_keywords", [
            "FDA approval", "SEC investigation", "antitrust", "regulation",
            "compliance", "lawsuit", "legal action", "government action",
            "policy change", "legislation", "oversight", "enforcement"
        ])
        
        # מילות מפתח לאירועים פיננסיים (דוחות כספיים)
        self.financial_keywords = cfg.get("financial_keywords", [
            "earnings", "quarterly", "financial", "results", "report", "revenue", 
            "profit", "loss", "declines", "dismal", "layoffs", "restructuring",
            "guidance", "forecast", "outlook", "missed", "beat", "expectations"
        ])
        
        # API keys (נטענים מקובץ הסביבה דרך APICredentials)
        self.marketaux_key = APICredentials.get_marketaux_key()
        
        # Cache לתוצאות
        self.event_cache = {}
        self.cache_duration = timedelta(hours=1)
        
    def analyze(self, symbol: str, price_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        ניתוח אירועים עבור מניה ספציפית
        
        Args:
            symbol: סימבול המניה
            price_df: נתוני מחירים (לא נדרש כרגע)
            
        Returns:
            מילון עם ציון השפעה ופרטי אירועים
        """
        try:
            # בדיקה אם יש תוצאות ב-cache
            cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H')}"
            if cache_key in self.event_cache:
                cached_result = self.event_cache[cache_key]
                if datetime.now() - cached_result['timestamp'] < self.cache_duration:
                    return cached_result['data']
            
            # איסוף אירועים
            events = self._collect_events(symbol)
            
            # ניתוח השפעה
            impact_score = self._calculate_impact_score(events, symbol)
            
            # בניית תוצאה
            result = {
                'score': impact_score,
                'events': events,
                'summary': self._generate_summary(events, impact_score),
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol
            }
            
            # שמירה ב-cache
            self.event_cache[cache_key] = {
                'data': result,
                'timestamp': datetime.now()
            }
            
            return result
            
        except Exception as e:
            print(f"שגיאה בניתוח אירועים עבור {symbol}: {e}")
            return {
                'score': 1,
                'events': [],
                'summary': f"שגיאה בניתוח: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol
            }
    
    def _collect_events(self, symbol: str) -> Dict[str, List]:
        """
        איסוף אירועים ממוקדים במניה
        
        Args:
            symbol: סימבול המניה
            
        Returns:
            מילון עם אירועים לפי קטגוריות
        """
        events = {
            'geopolitical': [],
            'economic': [],
            'financial': [],
            'regulatory': [],
            'company_specific': []
        }
        
        try:
            # איסוף חדשות על המניה
            company_news = self._fetch_company_news(symbol)
            
            # סיווג אירועים
            for news_item in company_news:
                event_type = self._classify_event(news_item)
                if event_type:
                    events[event_type].append(news_item)
            
            # איסוף אירועים כלליים (שוק)
            market_events = self._fetch_market_events()
            for event in market_events:
                event_type = self._classify_event(event)
                if event_type:
                    events[event_type].append(event)
                    
        except Exception as e:
            print(f"שגיאה באיסוף אירועים: {e}")
        
        return events
    
    def _fetch_company_news(self, symbol: str) -> List[Dict]:
        """
        שליפת חדשות על מניה ספציפית
        """
        news_items = []
        
        try:
            # שימוש ב-MarketAux API (אם יש מפתח)
            if self.marketaux_key:
                url = (
                    f"https://api.marketaux.com/v1/news/all?symbols={symbol}"
                    f"&language=en&limit=10&api_token={self.marketaux_key}"
                )
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('data', [])
                    for article in articles:
                        title = article.get('title', '')
                        desc = article.get('description', '')
                        sent = compute_sentiment_label_score(f"{title}. {desc}") if (title or desc) else {"label": "neutral", "score": 0.0}
                        news_items.append({
                            'title': title,
                            'description': desc,
                            'url': article.get('url', ''),
                            'published_at': article.get('published_at', ''),
                            'source': article.get('source', ''),
                            'sentiment': sent.get('label', 'neutral')
                        })
        except Exception as e:
            print(f"שגיאה בשליפת חדשות עבור {symbol}: {e}")
        
        return news_items
    
    def _fetch_market_events(self) -> List[Dict]:
        """
        שליפת אירועים כלליים בשוק
        """
        events = []
        
        try:
            # אירועים כלכליים ידועים (דוגמה)
            economic_events = [
                {
                    'title': 'Federal Reserve Interest Rate Decision',
                    'description': 'Fed expected to maintain current rates',
                    'category': 'economic',
                    'impact': 'medium'
                },
                {
                    'title': 'Inflation Data Release',
                    'description': 'CPI data shows inflation trends',
                    'category': 'economic',
                    'impact': 'high'
                }
            ]
            
            events.extend(economic_events)
            
        except Exception as e:
            print(f"שגיאה בשליפת אירועי שוק: {e}")
        
        return events
    
    def _classify_event(self, event: Dict) -> Optional[str]:
        """
        סיווג אירוע לפי מילות מפתח
        """
        title = event.get('title', '').lower()
        description = event.get('description', '').lower()
        text = f"{title} {description}"
        
        # בדיקת אירועים גיאופוליטיים
        for keyword in self.geopolitical_keywords:
            if keyword in text:
                return 'geopolitical'
        
        # בדיקת אירועים כלכליים
        for keyword in self.economic_keywords:
            if keyword in text:
                return 'economic'
        
        # בדיקת אירועים רגולטוריים
        for keyword in self.regulatory_keywords:
            if keyword in text:
                return 'regulatory'
        
        # בדיקת אירועים פיננסיים (דוחות כספיים)
        for keyword in self.financial_keywords:
            if keyword in text:
                return 'financial'
        
        return 'company_specific'
    
    def _calculate_impact_score(self, events: Dict, symbol: str) -> int:
        """
        חישוב ציון השפעה (1-100)
        """
        base_score = 1
        
        # משקלים לפי סוג אירוע
        weights = {
            'geopolitical': 0.4,
            'economic': 0.3,
            'financial': 0.5,  # משקל גבוה לדוחות כספיים
            'regulatory': 0.2,
            'company_specific': 0.1
        }
        
        total_impact = 0
        
        for event_type, event_list in events.items():
            if event_list:
                # חישוב השפעה לפי כמות ואיכות אירועים
                event_count = len(event_list)
                avg_sentiment = self._calculate_avg_sentiment(event_list)
                
                # ציון לפי כמות אירועים (1-30)
                count_score = min(30, event_count * 5)
                
                # ציון לפי סנטימנט (1-40)
                sentiment_score = max(1, int(avg_sentiment * 40))
                
                # ציון לפי משקל סוג האירוע (1-30)
                type_score = int(weights.get(event_type, 0.1) * 30)
                
                # חישוב ציון קטגוריה - ממוצע של 3 הציונים
                category_score = count_score + sentiment_score + type_score
                
                # הוספה לטוטאל עם משקל
                total_impact += category_score * weights.get(event_type, 0.1)
        
        # הגבלה ל-1-100
        final_score = int(max(1, min(100, base_score + total_impact)))
        
        return final_score
    
    def _calculate_avg_sentiment(self, events: List[Dict]) -> float:
        """
        חישוב סנטימנט ממוצע
        """
        if not events:
            return 0.5  # ניטרלי
        
        sentiment_scores = []
        for event in events:
            sentiment = event.get('sentiment', 'neutral')
            
            # המרה לציון מספרי
            if sentiment == 'positive':
                sentiment_scores.append(0.8)
            elif sentiment == 'negative':
                sentiment_scores.append(0.2)
            else:
                sentiment_scores.append(0.5)
        
        return np.mean(sentiment_scores) if sentiment_scores else 0.5
    
    def _generate_summary(self, events: Dict, impact_score: int) -> str:
        """
        יצירת סיכום אירועים
        """
        total_events = sum(len(event_list) for event_list in events.values())
        
        if total_events == 0:
            return "לא נמצאו אירועים משמעותיים"
        
        summary_parts = []
        
        if events['geopolitical']:
            summary_parts.append(f"אירועים גיאופוליטיים: {len(events['geopolitical'])}")
        
        if events['economic']:
            summary_parts.append(f"אירועים כלכליים: {len(events['economic'])}")
        
        if events['regulatory']:
            summary_parts.append(f"אירועים רגולטוריים: {len(events['regulatory'])}")
        
        if events['financial']:
            summary_parts.append(f"אירועים פיננסיים: {len(events['financial'])}")
        
        if events['company_specific']:
            summary_parts.append(f"אירועים ספציפיים לחברה: {len(events['company_specific'])}")
        
        impact_level = "נמוכה" if impact_score < 30 else "בינונית" if impact_score < 70 else "גבוהה"
        
        return f"ציון השפעה: {impact_score}/100 ({impact_level}). {', '.join(summary_parts)}"
    
    def get_recent_events(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        קבלת אירועים אחרונים עבור מניה
        """
        result = self.analyze(symbol)
        return result.get('events', {})
    
    def get_impact_analysis(self, symbol: str) -> Dict:
        """
        ניתוח השפעה מפורט
        """
        return self.analyze(symbol)


# יצירת instance גלובלי לשימוש
event_scanner = EventScanner() 