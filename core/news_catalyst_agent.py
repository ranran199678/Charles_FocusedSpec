"""
NewsCatalystAgent - Advanced News Analysis Agent
==============================================
סוכן מתקדם לניתוח חדשות וזיהוי קטליזטורים פיננסיים.

Features:
- Advanced NLP sentiment analysis
- Catalyst trigger detection (M&A, FDA, Earnings beats, etc.)
- Impact assessment based on historical patterns
- Multi-source news aggregation
- Weighted scoring system based on news importance
- Real-time news monitoring capabilities

Based on: Technical specifications document requirements
"""

import requests
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.base.base_agent import BaseAgent
from utils.credentials import APICredentials
from utils.fmp_utils import fmp_client

@dataclass
class NewsItem:
    """Structure for individual news items"""
    title: str
    summary: str
    source: str
    timestamp: datetime
    url: str
    sentiment_score: float = 0.0
    impact_score: float = 0.0
    catalyst_type: str = "general"

@dataclass
class CatalystTrigger:
    """Definition of catalyst triggers with weights"""
    keywords: List[str]
    weight: float
    category: str
    impact_multiplier: float

class NewsCatalystAgent(BaseAgent):
    def __init__(self, config=None):
        """
        אתחול הסוכן עם מערכת ניקוד משוקללת מתקדמת
        """
        super().__init__(config)
        
        # הוספת credentials
        from utils.credentials import APICredentials
        self.credentials = APICredentials()
        
        # הגדרות בסיסיות
        self.lookback_days = self.config.get("lookback_days", 7)
        self.max_news_items = self.config.get("max_news_items", 20)
        self.sentiment_threshold = self.config.get("sentiment_threshold", 0.1)
        
        # מערכת ניקוד משוקללת לפי קטגוריות
        self.category_weights = {
            "רגולציה": {
                "weight": 1.5,
                "subcategories": {
                    "FDA": 2.0,
                    "SEC": 1.8,
                    "FTC": 1.6,
                    "DOJ": 1.7,
                    "EU_Regulation": 1.4,
                    "China_Regulation": 1.3
                }
            },
            "פיננסים": {
                "weight": 1.3,
                "subcategories": {
                    "Earnings": 1.8,
                    "Revenue": 1.6,
                    "Guidance": 1.7,
                    "Analyst_Ratings": 1.2,
                    "Institutional_Activity": 1.4,
                    "Short_Interest": 1.1
                }
            },
            "תחרות": {
                "weight": 1.2,
                "subcategories": {
                    "Market_Share": 1.5,
                    "Competitive_Advantage": 1.4,
                    "Patent_News": 1.6,
                    "Partnership": 1.3,
                    "Acquisition": 1.8,
                    "Bankruptcy": 1.9
                }
            },
            "טכנולוגיה": {
                "weight": 1.4,
                "subcategories": {
                    "AI_Development": 1.8,
                    "Product_Launch": 1.5,
                    "Security_Breach": 1.7,
                    "Infrastructure": 1.3,
                    "Innovation": 1.6
                }
            },
            "גיאופוליטי": {
                "weight": 1.1,
                "subcategories": {
                    "Trade_War": 1.6,
                    "Sanctions": 1.5,
                    "Political_Instability": 1.4,
                    "Currency_Fluctuation": 1.2
                }
            }
        }
        
        # מודל חיזוי השפעה עתידית
        self.price_impact_model = {
            "short_term": {
                "high_impact": 0.15,  # 15% movement
                "medium_impact": 0.08,  # 8% movement
                "low_impact": 0.03     # 3% movement
            },
            "medium_term": {
                "high_impact": 0.25,   # 25% movement
                "medium_impact": 0.12,  # 12% movement
                "low_impact": 0.05     # 5% movement
            },
            "long_term": {
                "high_impact": 0.40,   # 40% movement
                "medium_impact": 0.20,  # 20% movement
                "low_impact": 0.08     # 8% movement
            }
        }
        
        # היסטוריית השפעות לניתוח מגמות
        self.historical_impacts = {}
        
        # Catalyst triggers מתקדמים
        self.catalyst_triggers = [
            CatalystTrigger(
                keywords=["FDA approval", "FDA clearance", "regulatory approval"],
                weight=2.0,
                category="רגולציה",
                impact_multiplier=1.8
            ),
            CatalystTrigger(
                keywords=["merger", "acquisition", "M&A", "takeover"],
                weight=1.8,
                category="פיננסים",
                impact_multiplier=1.6
            ),
            CatalystTrigger(
                keywords=["earnings beat", "revenue beat", "guidance raise"],
                weight=1.6,
                category="פיננסים",
                impact_multiplier=1.4
            ),
            CatalystTrigger(
                keywords=["partnership", "joint venture", "collaboration"],
                weight=1.3,
                category="תחרות",
                impact_multiplier=1.2
            ),
            CatalystTrigger(
                keywords=["AI breakthrough", "artificial intelligence", "machine learning"],
                weight=1.7,
                category="טכנולוגיה",
                impact_multiplier=1.5
            ),
            CatalystTrigger(
                keywords=["patent", "intellectual property", "IP"],
                weight=1.5,
                category="טכנולוגיה",
                impact_multiplier=1.3
            ),
            CatalystTrigger(
                keywords=["cyber attack", "data breach", "security"],
                weight=1.9,
                category="טכנולוגיה",
                impact_multiplier=1.7
            ),
            CatalystTrigger(
                keywords=["analyst upgrade", "price target", "buy rating"],
                weight=1.2,
                category="פיננסים",
                impact_multiplier=1.1
            ),
            CatalystTrigger(
                keywords=["short squeeze", "short interest", "gamma squeeze"],
                weight=1.8,
                category="פיננסים",
                impact_multiplier=1.6
            ),
            CatalystTrigger(
                keywords=["insider buying", "insider selling", "executive"],
                weight=1.4,
                category="פיננסים",
                impact_multiplier=1.2
            )
        ]
        
        # Negative triggers (reduce score)
        self.negative_triggers = {
            "lawsuit": CatalystTrigger(
                keywords=["lawsuit", "legal action", "investigation", "sec probe"],
                weight=-70.0,
                category="legal",
                impact_multiplier=-2.0
            ),
            "earnings_miss": CatalystTrigger(
                keywords=["misses earnings", "disappointing", "guidance cut", "weak quarter"],
                weight=-80.0,
                category="financial",
                impact_multiplier=-2.2
            ),
            "analyst_downgrade": CatalystTrigger(
                keywords=["downgrade", "lowered target", "underperform", "sell rating"],
                weight=-65.0,
                category="analyst",
                impact_multiplier=-1.8
            )
        }

    def _extract_sentiment_score(self, text: str) -> float:
        """
        Advanced sentiment analysis using keyword-based approach
        (In production, this would use BERT or similar NLP model)
        """
        positive_words = [
            "strong", "growth", "beat", "exceed", "positive", "bullish", "optimistic",
            "success", "breakthrough", "innovative", "profitable", "revenue growth",
            "market share", "expansion", "partnership", "acquisition", "approval"
        ]
        
        negative_words = [
            "weak", "decline", "miss", "disappointing", "negative", "bearish", "pessimistic",
            "loss", "failure", "problem", "issue", "lawsuit", "investigation", "warning",
            "guidance cut", "restructuring", "layoffs", "bankruptcy", "debt"
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Normalize to -1 to 1 scale
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
            
        sentiment = (positive_count - negative_count) / max(total_words * 0.1, 1)
        return max(-1.0, min(1.0, sentiment))

    def _detect_catalyst_triggers(self, news_item: NewsItem) -> Tuple[List[str], float]:
        """
        זיהוי טריגרי קטליזטור בחדשה
        """
        text = f"{news_item.title} {news_item.summary}".lower()
        detected_triggers = []
        total_impact = 0.0
        
        # Check positive triggers
        for trigger in self.catalyst_triggers:
            for keyword in trigger.keywords:
                if keyword in text:
                    detected_triggers.append(f"{trigger.category}:{keyword}")
                    total_impact += trigger.weight * trigger.impact_multiplier
                    break  # Only count each trigger once per news item
        
        # Check negative triggers
        for trigger_name, trigger in self.negative_triggers.items():
            for keyword in trigger.keywords:
                if keyword in text:
                    detected_triggers.append(f"negative_{trigger_name}:{keyword}")
                    total_impact += trigger.weight * trigger.impact_multiplier
                    break
        
        return detected_triggers, total_impact

    def _fetch_news_multi_source(self, symbol: str) -> List[NewsItem]:
        """
        Fetch news from multiple sources (FMP, Alpha Vantage, etc.)
        """
        news_items = []
        
        # FMP News
        try:
            # שימוש במודול fmp_utils המעודכן
            fmp_news = fmp_client.fmp_get_stock_news(tickers=symbol, limit=self.max_news_items, verify_ssl=False)
            
            if fmp_news:
                    for item in fmp_news:
                        if isinstance(item, dict):
                            news_items.append(NewsItem(
                                title=item.get("title", ""),
                                summary=item.get("text", "")[:500],  # Limit summary length
                                source="FMP",
                                timestamp=datetime.fromisoformat(item.get("publishedDate", "").replace("Z", "+00:00")) if item.get("publishedDate") else datetime.now(),
                                url=item.get("url", "")
                            ))
        except Exception as e:
            print(f"Error fetching FMP news: {e}")
        
        # Alpha Vantage News (if available)
        try:
            av_key = self.credentials.get_alpha_vantage_key()
            if av_key and len(news_items) < self.max_news_items:
                url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={av_key}"
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    av_data = resp.json()
                    feed = av_data.get("feed", [])
                    for item in feed[:self.max_news_items - len(news_items)]:
                        news_items.append(NewsItem(
                            title=item.get("title", ""),
                            summary=item.get("summary", "")[:500],
                            source="AlphaVantage",
                            timestamp=datetime.fromisoformat(item.get("time_published", "").replace("T", " ")) if item.get("time_published") else datetime.now(),
                            url=item.get("url", "")
                        ))
        except Exception as e:
            print(f"Error fetching Alpha Vantage news: {e}")
        
        return news_items[:self.max_news_items]

    def _calculate_time_decay_factor(self, news_timestamp: datetime) -> float:
        """
        חישוב פקטור דעיכה לפי זמן - חדשות חדשות יותר חשובות יותר
        """
        now = datetime.now().replace(tzinfo=news_timestamp.tzinfo) if news_timestamp.tzinfo else datetime.now()
        time_diff = now - news_timestamp
        days_old = time_diff.total_seconds() / (24 * 3600)
        
        # Exponential decay: newer news has higher impact
        decay_factor = max(0.1, 1.0 * (0.8 ** days_old))
        return decay_factor

    def _calculate_source_credibility(self, source: str) -> float:
        """
        חישוב אמינות המקור
        """
        credibility_scores = {
            "FMP": 0.9,
            "AlphaVantage": 0.85,
            "Reuters": 1.0,
            "Bloomberg": 1.0,
            "WSJ": 0.95,
            "CNBC": 0.8,
            "MarketWatch": 0.75,
            "default": 0.7
        }
        return credibility_scores.get(source, credibility_scores["default"])

    def _predict_price_impact(self, news_item: NewsItem, catalyst_type: str, impact_score: float) -> Dict:
        """
        חיזוי השפעה עתידית על מחיר המניה
        """
        try:
            # קביעת רמת השפעה לפי קטגוריה
            category_impact = {
                "רגולציה": "high_impact",
                "פיננסים": "medium_impact", 
                "תחרות": "medium_impact",
                "טכנולוגיה": "medium_impact",
                "גיאופוליטי": "low_impact"
            }
            
            impact_level = category_impact.get(catalyst_type, "low_impact")
            
            # חישוב השפעה לפי טווח זמן
            predictions = {}
            for timeframe, impacts in self.price_impact_model.items():
                base_impact = impacts[impact_level]
                
                # התאמה לפי איכות החדשות
                quality_factor = min(2.0, max(0.5, impact_score / 50))  # 0.5-2.0
                adjusted_impact = base_impact * quality_factor
                
                # התאמה לפי זמן החדשות
                hours_old = (datetime.now() - news_item.timestamp.replace(tzinfo=None)).total_seconds() / 3600
                time_decay = max(0.3, 1 - (hours_old / 72))  # Decay over 3 days
                
                final_impact = adjusted_impact * time_decay
                
                predictions[timeframe] = {
                    "expected_movement": round(final_impact * 100, 2),  # Percentage
                    "confidence": round(min(0.9, max(0.1, quality_factor * 0.5)), 3),
                    "impact_level": impact_level,
                    "quality_factor": round(quality_factor, 2),
                    "time_decay": round(time_decay, 2)
                }
            
            return predictions
            
        except Exception as e:
            print(f"שגיאה בחיזוי השפעה: {e}")
            return {}

    def _analyze_historical_impact(self, symbol: str, catalyst_type: str) -> Dict:
        """
        ניתוח השפעות היסטוריות לפי קטגוריה
        """
        try:
            # סימולציה של נתונים היסטוריים (בפרודקציה יהיה מ-API)
            historical_data = {
                "רגולציה": {"avg_impact": 0.12, "success_rate": 0.75, "sample_size": 45},
                "פיננסים": {"avg_impact": 0.08, "success_rate": 0.68, "sample_size": 120},
                "תחרות": {"avg_impact": 0.06, "success_rate": 0.62, "sample_size": 85},
                "טכנולוגיה": {"avg_impact": 0.10, "success_rate": 0.70, "sample_size": 95},
                "גיאופוליטי": {"avg_impact": 0.04, "success_rate": 0.55, "sample_size": 60}
            }
            
            data = historical_data.get(catalyst_type, {"avg_impact": 0.05, "success_rate": 0.50, "sample_size": 30})
            
            return {
                "avg_impact": data["avg_impact"],
                "success_rate": data["success_rate"],
                "sample_size": data["sample_size"],
                "confidence_interval": round(data["avg_impact"] * 0.3, 3),
                "trend": "stable" if data["success_rate"] > 0.6 else "declining"
            }
            
        except Exception as e:
            print(f"שגיאה בניתוח היסטורי: {e}")
            return {}

    def _calculate_weighted_score(self, news_items: List[NewsItem], catalysts: List[str]) -> Dict:
        """
        חישוב ניקוד משוקלל לפי קטגוריות
        """
        try:
            category_scores = {}
            total_weighted_score = 0
            total_weight = 0
            
            for news_item in news_items:
                for catalyst in catalysts:
                    category = catalyst.split(':')[0] if ':' in catalyst else "כללי"
                    
                    # קביעת משקל לפי קטגוריה
                    category_weight = self.category_weights.get(category, {}).get("weight", 1.0)
                    
                    # משקל תת-קטגוריה
                    subcategory = catalyst.split(':')[1] if ':' in catalyst and len(catalyst.split(':')) > 1 else "כללי"
                    subcategory_weight = self.category_weights.get(category, {}).get("subcategories", {}).get(subcategory, 1.0)
                    
                    # משקל סופי
                    final_weight = category_weight * subcategory_weight
                    
                    # ניקוד לפי סנטימנט
                    sentiment_score = news_item.sentiment_score
                    weighted_score = sentiment_score * final_weight
                    
                    if category not in category_scores:
                        category_scores[category] = {
                            "score": 0,
                            "weight": 0,
                            "count": 0,
                            "subcategories": {}
                        }
                    
                    category_scores[category]["score"] += weighted_score
                    category_scores[category]["weight"] += final_weight
                    category_scores[category]["count"] += 1
                    
                    if subcategory not in category_scores[category]["subcategories"]:
                        category_scores[category]["subcategories"][subcategory] = 0
                    category_scores[category]["subcategories"][subcategory] += 1
                    
                    total_weighted_score += weighted_score
                    total_weight += final_weight
            
            # חישוב ממוצע משוקלל
            avg_weighted_score = total_weighted_score / total_weight if total_weight > 0 else 0
            
            # נרמול ל-0-100
            final_score = max(1, min(100, 50 + (avg_weighted_score * 50)))
            
            return {
                "final_score": int(final_score),
                "avg_weighted_score": round(avg_weighted_score, 3),
                "category_breakdown": category_scores,
                "total_weight": round(total_weight, 2)
            }
            
        except Exception as e:
            print(f"שגיאה בחישוב ניקוד משוקלל: {e}")
            return {"final_score": 50, "avg_weighted_score": 0, "category_breakdown": {}, "total_weight": 0}

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של חדשות וקטליזטורים
        """
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=30)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            # Fetch news from multiple sources
            news_items = self._fetch_news_multi_source(symbol)
            
            if not news_items:
                return {
                    "score": 50,
                    "explanation": "לא נמצאו חדשות זמינות",
                    "signal": {
                        "type": "news_catalyst",
                        "score": 50,
                        "reason": "לא נמצאו חדשות זמינות",
                        "confidence": 0.5,
                        "details": {
                            "catalyst_count": 0,
                            "sentiment": 0.0,
                            "sources_count": 0
                        }
                    },
                    "details": {
                        "news_count": 0,
                        "catalysts": [],
                        "sentiment": 0.0,
                        "sources": []
                    }
                }
            
            # Analyze each news item
            total_impact = 0.0
            total_sentiment = 0.0
            all_catalysts = []
            processed_news = []
            
            for news_item in news_items:
                # Extract sentiment
                sentiment = self._extract_sentiment_score(f"{news_item.title} {news_item.summary}")
                news_item.sentiment_score = sentiment
                
                # Detect catalyst triggers
                catalysts, impact = self._detect_catalyst_triggers(news_item)
                news_item.catalyst_type = catalysts[0].split(':')[0] if catalysts else "general"
                
                # Calculate time decay and source credibility
                time_factor = self._calculate_time_decay_factor(news_item.timestamp)
                credibility = self._calculate_source_credibility(news_item.source)
                
                # Calculate weighted impact
                weighted_impact = impact * time_factor * credibility
                news_item.impact_score = weighted_impact
                
                total_impact += weighted_impact
                total_sentiment += sentiment * time_factor * credibility
                all_catalysts.extend(catalysts)
                
                processed_news.append({
                    "title": news_item.title[:100],
                    "sentiment": sentiment,
                    "impact": weighted_impact,
                    "catalysts": catalysts,
                    "source": news_item.source,
                    "age_hours": (datetime.now() - news_item.timestamp.replace(tzinfo=None)).total_seconds() / 3600
                })
            
            # Calculate final score using weighted system
            weighted_analysis = self._calculate_weighted_score(news_items, all_catalysts)
            final_score = weighted_analysis["final_score"]
            
            # Calculate average sentiment
            avg_sentiment = total_sentiment / len(news_items) if news_items else 0
            
            # Predict future price impact
            price_predictions = {}
            if news_items:
                # Use the most impactful news item for prediction
                most_impactful = max(news_items, key=lambda x: x.impact_score)
                catalyst_type = most_impactful.catalyst_type
                price_predictions = self._predict_price_impact(most_impactful, catalyst_type, most_impactful.impact_score)
            
            # Historical impact analysis
            historical_analysis = {}
            if all_catalysts:
                unique_categories = list(set([c.split(':')[0] for c in all_catalysts]))
                for category in unique_categories:
                    historical_analysis[category] = self._analyze_historical_impact(symbol, category)
            
            # Generate enhanced explanation
            if all_catalysts:
                unique_catalysts = list(set([c.split(':')[0] for c in all_catalysts]))
                explanation = f"זוהו קטליזטורים: {', '.join(unique_catalysts)}. סנטימנט ממוצע: {avg_sentiment:.2f}. ניקוד משוקלל: {weighted_analysis['avg_weighted_score']:.2f}"
            else:
                explanation = f"ניתוח {len(news_items)} חדשות. סנטימנט ממוצע: {avg_sentiment:.2f}"
            
            return {
                "score": final_score,
                "explanation": explanation,
                "signal": {
                    "type": "news_catalyst",
                    "score": final_score,
                    "reason": explanation,
                    "confidence": round(weighted_analysis.get("avg_weighted_score", 0.5), 3),
                    "details": {
                        "catalyst_count": len(list(set(all_catalysts))),
                        "sentiment": round(avg_sentiment, 3),
                        "sources_count": len(list(set([n.source for n in news_items]))),
                        "price_predictions": price_predictions,
                        "weighted_analysis": weighted_analysis
                    }
                },
                "details": {
                    "news_count": len(news_items),
                    "catalysts": list(set(all_catalysts)),
                    "sentiment": round(avg_sentiment, 3),
                    "total_impact": round(total_impact, 2),
                    "sources": list(set([n.source for n in news_items])),
                    "processed_news": processed_news[:5],  # Top 5 for details
                    "catalyst_categories": list(set([c.split(':')[0] for c in all_catalysts])),
                    "weighted_analysis": weighted_analysis,
                    "price_predictions": price_predictions,
                    "historical_analysis": historical_analysis
                }
            }
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()

    def get_catalyst_summary(self) -> Dict:
        """
        החזרת סיכום של כל הטריגרים הזמינים
        """
        return {
            "positive_triggers": {name: trigger.keywords for name, trigger in self.catalyst_triggers.items()},
            "negative_triggers": {name: trigger.keywords for name, trigger in self.negative_triggers.items()},
            "total_triggers": len(self.catalyst_triggers) + len(self.negative_triggers)
        }
