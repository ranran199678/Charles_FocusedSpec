"""
Google Trends Tracker - מעקב אחר חיפושים בגוגל
==============================================

סוכן המנטר חיפושים בגוגל למניות ומילות מפתח.
מזהה מניות עם עניין חיפוש גבוה ופוטנציאל לזינוק.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import requests
import json
from collections import defaultdict
import time

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_date_range

logger = get_agent_logger("google_trends")

class GoogleTrendsTracker:
    """
    סוכן מעקב אחר חיפושים בגוגל
    """

    def __init__(self, config=None):
        """
        אתחול הסוכן
        """
        self.name = "Google Trends Tracker"
        self.version = "1.0.0"
        self.description = "מנטר חיפושים בגוגל למניות ומילות מפתח"

        # הגדרות API
        self.config = config or {}
        self.api_key = self.config.get("google_trends_api_key")
        self.base_url = "https://trends.google.com/trends/api/widgetdata/multiline"
        
        # פרמטרים לניתוח
        self.trend_period = 30  # תקופה לניתוח מגמה (ימים)
        self.spike_threshold = 2.0  # סף קפיצה בחיפושים
        self.interest_threshold = 50  # סף עניין מינימלי
        self.geo_locations = ['US', 'CA', 'GB', 'AU']  # מיקומים גיאוגרפיים

        # מילות מפתח פיננסיות
        self.financial_keywords = [
            'stock', 'invest', 'buy', 'sell', 'earnings', 'dividend',
            'bullish', 'bearish', 'market', 'trading', 'portfolio'
        ]

        logger.info(f"Initialized {self.name} v{self.version}")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None,
                historical_trends: pd.DataFrame = None,
                related_keywords: List[str] = None) -> Dict[str, Any]:
        """
        ניתוח חיפושים בגוגל למניה

        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            historical_trends: נתוני מגמות היסטוריים
            related_keywords: מילות מפתח קשורות

        Returns:
            תוצאות הניתוח
        """
        try:
            logger.info(f"Starting Google Trends analysis for {symbol}")

            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")

            # ניתוח חיפושים עיקריים
            main_search_analysis = self._analyze_main_search(symbol)

            # ניתוח מילות מפתח קשורות
            keyword_analysis = self._analyze_related_keywords(symbol, related_keywords)

            # ניתוח מגמות גיאוגרפיות
            geographic_analysis = self._analyze_geographic_trends(symbol)

            # ניתוח מגמות זמן
            temporal_analysis = self._analyze_temporal_trends(symbol, historical_trends)

            # ניתוח השפעה על מחיר
            price_impact_analysis = self._analyze_price_impact(
                symbol, price_df, main_search_analysis, temporal_analysis
            )

            # ניתוח קהל יעד
            audience_analysis = self._analyze_search_audience(
                symbol, main_search_analysis, geographic_analysis
            )

            # חישוב ציון כללי
            score = self._calculate_trends_score(
                main_search_analysis,
                keyword_analysis,
                geographic_analysis,
                temporal_analysis,
                price_impact_analysis,
                audience_analysis
            )

            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)

            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)

            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                main_search_analysis,
                keyword_analysis,
                geographic_analysis,
                temporal_analysis,
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
                    "main_search": main_search_analysis,
                    "keywords": keyword_analysis,
                    "geographic": geographic_analysis,
                    "temporal": temporal_analysis,
                    "price_impact": price_impact_analysis,
                    "audience": audience_analysis
                },
                "metadata": {
                    "trend_period": self.trend_period,
                    "spike_threshold": self.spike_threshold,
                    "interest_threshold": self.interest_threshold,
                    "geo_locations": self.geo_locations
                }
            }

            logger.info(f"Google Trends analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result

        except Exception as e:
            error_msg = f"Error analyzing Google Trends for {symbol}: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result(error_msg)

    def _analyze_main_search(self, symbol: str) -> Dict[str, Any]:
        """
        ניתוח חיפושים עיקריים למניה
        """
        try:
            # שליפת נתוני חיפוש
            search_data = self._fetch_search_data(symbol)
            
            if not search_data:
                return self._create_empty_search_analysis()

            # ניתוח רמת עניין
            current_interest = search_data.get('current_interest', 0)
            avg_interest = search_data.get('average_interest', 0)
            
            # חישוב קפיצה
            if avg_interest > 0:
                interest_spike = current_interest / avg_interest
            else:
                interest_spike = 1.0

            # ניתוח מגמה
            trend_data = search_data.get('trend_data', [])
            if len(trend_data) > 1:
                trend_direction = self._calculate_trend_direction(trend_data)
                trend_strength = self._calculate_trend_strength(trend_data)
            else:
                trend_direction = "stable"
                trend_strength = 0.5

            return {
                "current_interest": current_interest,
                "average_interest": avg_interest,
                "interest_spike": interest_spike,
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "trend_data": trend_data,
                "is_trending": interest_spike > self.spike_threshold,
                "high_interest": current_interest > self.interest_threshold,
                "strength": min(interest_spike * 25, 100)
            }

        except Exception as e:
            logger.error(f"Error analyzing main search: {str(e)}")
            return self._create_empty_search_analysis()

    def _analyze_related_keywords(self, symbol: str, related_keywords: List[str]) -> Dict[str, Any]:
        """
        ניתוח מילות מפתח קשורות
        """
        try:
            if not related_keywords:
                related_keywords = self._generate_related_keywords(symbol)

            keyword_analysis = {}
            total_interest = 0
            trending_keywords = []

            for keyword in related_keywords:
                keyword_data = self._fetch_search_data(keyword)
                if keyword_data:
                    interest = keyword_data.get('current_interest', 0)
                    keyword_analysis[keyword] = {
                        'interest': interest,
                        'trend': keyword_data.get('trend_direction', 'stable'),
                        'spike': keyword_data.get('interest_spike', 1.0)
                    }
                    total_interest += interest
                    
                    if keyword_data.get('interest_spike', 1.0) > self.spike_threshold:
                        trending_keywords.append(keyword)

            # חישוב ממוצעים
            avg_keyword_interest = total_interest / max(len(keyword_analysis), 1)
            
            return {
                "keyword_analysis": keyword_analysis,
                "total_keywords": len(keyword_analysis),
                "trending_keywords": trending_keywords,
                "average_interest": avg_keyword_interest,
                "total_interest": total_interest,
                "keyword_diversity": len(keyword_analysis),
                "trending_ratio": len(trending_keywords) / max(len(keyword_analysis), 1)
            }

        except Exception as e:
            logger.error(f"Error analyzing related keywords: {str(e)}")
            return {"keyword_analysis": {}, "total_keywords": 0}

    def _analyze_geographic_trends(self, symbol: str) -> Dict[str, Any]:
        """
        ניתוח מגמות גיאוגרפיות
        """
        try:
            geographic_data = {}
            total_interest = 0
            top_locations = []

            for location in self.geo_locations:
                location_data = self._fetch_search_data(symbol, geo=location)
                if location_data:
                    interest = location_data.get('current_interest', 0)
                    geographic_data[location] = {
                        'interest': interest,
                        'trend': location_data.get('trend_direction', 'stable'),
                        'spike': location_data.get('interest_spike', 1.0)
                    }
                    total_interest += interest

            # זיהוי מיקומים מובילים
            if geographic_data:
                sorted_locations = sorted(geographic_data.items(), 
                                        key=lambda x: x[1]['interest'], reverse=True)
                top_locations = [loc[0] for loc in sorted_locations[:3]]

            # חישוב ממוצעים
            avg_geo_interest = total_interest / max(len(geographic_data), 1)
            
            return {
                "geographic_data": geographic_data,
                "total_locations": len(geographic_data),
                "top_locations": top_locations,
                "average_interest": avg_geo_interest,
                "total_interest": total_interest,
                "geographic_diversity": len(geographic_data),
                "global_reach": len(geographic_data) > 2
            }

        except Exception as e:
            logger.error(f"Error analyzing geographic trends: {str(e)}")
            return {"geographic_data": {}, "total_locations": 0}

    def _analyze_temporal_trends(self, symbol: str, historical_trends: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח מגמות זמן
        """
        try:
            # שליפת נתונים היסטוריים
            if historical_trends is None or historical_trends.empty:
                historical_trends = self._fetch_historical_data(symbol)

            if historical_trends.empty:
                return {"trend_direction": "stable", "trend_strength": 0.5}

            # ניתוח מגמה
            trend_values = historical_trends['interest'].values
            
            if len(trend_values) > 1:
                # חישוב שיפוע
                x = np.arange(len(trend_values))
                slope = np.polyfit(x, trend_values, 1)[0]
                
                # קביעת מגמה
                if slope > 1:
                    trend_direction = "increasing"
                elif slope < -1:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
                
                trend_strength = min(abs(slope) / 10, 1.0)
                
                # ניתוח תנודתיות
                volatility = np.std(trend_values)
                
                # זיהוי קפיצות
                spikes = self._detect_trend_spikes(trend_values)
                
            else:
                trend_direction = "stable"
                trend_strength = 0.5
                volatility = 0
                spikes = []

            return {
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "volatility": volatility,
                "spikes": spikes,
                "trend_data": historical_trends.to_dict('records'),
                "accelerating": trend_direction == "increasing" and trend_strength > 0.7,
                "decelerating": trend_direction == "decreasing" and trend_strength > 0.7
            }

        except Exception as e:
            logger.error(f"Error analyzing temporal trends: {str(e)}")
            return {"trend_direction": "stable", "trend_strength": 0.5}

    def _analyze_price_impact(self, symbol: str, price_df: pd.DataFrame,
                            main_search_analysis: Dict, temporal_analysis: Dict) -> Dict[str, Any]:
        """
        ניתוח השפעת חיפושים על מחיר
        """
        try:
            if price_df is None or price_df.empty:
                return {"price_correlation": 0.0, "impact_strength": 0.0}

            # חישוב שינויי מחיר
            price_changes = price_df['close'].pct_change()
            
            # חישוב חיפושים משוקללים
            search_interest = main_search_analysis.get('current_interest', 0)
            search_trend = temporal_analysis.get('trend_strength', 0.5)
            weighted_search = search_interest * search_trend

            # קורלציה בין חיפושים למחיר
            if len(price_changes) > 1:
                correlation = np.corrcoef([weighted_search] * len(price_changes), 
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
                "search_price_alignment": correlation > 0.3,
                "weighted_search": weighted_search
            }

        except Exception as e:
            logger.error(f"Error analyzing price impact: {str(e)}")
            return {"price_correlation": 0.0, "impact_strength": 0.0}

    def _analyze_search_audience(self, symbol: str, main_search_analysis: Dict,
                               geographic_analysis: Dict) -> Dict[str, Any]:
        """
        ניתוח קהל החיפושים
        """
        try:
            # ניתוח גודל קהל
            total_interest = main_search_analysis.get('current_interest', 0)
            geographic_reach = geographic_analysis.get('total_locations', 0)
            
            # סיווג קהל
            if total_interest > 80:
                audience_size = "large"
            elif total_interest > 50:
                audience_size = "medium"
            else:
                audience_size = "small"

            # ניתוח פיזור גיאוגרפי
            if geographic_reach > 3:
                geographic_diversity = "high"
            elif geographic_reach > 1:
                geographic_diversity = "medium"
            else:
                geographic_diversity = "low"

            # זיהוי קהל יעד
            if audience_size == "large" and geographic_diversity == "high":
                audience_type = "global_mass"
            elif audience_size == "large":
                audience_type = "mass_market"
            elif geographic_diversity == "high":
                audience_type = "niche_global"
            else:
                audience_type = "niche_local"

            return {
                "audience_size": audience_size,
                "geographic_diversity": geographic_diversity,
                "audience_type": audience_type,
                "total_interest": total_interest,
                "geographic_reach": geographic_reach,
                "viral_potential": total_interest > 70 and geographic_reach > 2
            }

        except Exception as e:
            logger.error(f"Error analyzing search audience: {str(e)}")
            return {"audience_size": "unknown", "audience_type": "unknown"}

    def _calculate_trends_score(self, main_search_analysis: Dict, keyword_analysis: Dict,
                              geographic_analysis: Dict, temporal_analysis: Dict,
                              price_impact_analysis: Dict, audience_analysis: Dict) -> float:
        """
        חישוב ציון מגמות כללי
        """
        try:
            # משקלות
            weights = {
                'main_search': 0.3,
                'keywords': 0.2,
                'geographic': 0.15,
                'temporal': 0.15,
                'price_impact': 0.1,
                'audience': 0.1
            }

            # ציונים
            main_search_score = main_search_analysis.get('strength', 0)
            keyword_score = keyword_analysis.get('trending_ratio', 0) * 100
            geographic_score = geographic_analysis.get('geographic_diversity', 0) * 20
            temporal_score = temporal_analysis.get('trend_strength', 0.5) * 100
            price_score = price_impact_analysis.get('impact_strength', 0) * 100
            audience_score = 100 if audience_analysis.get('viral_potential', False) else 50

            # חישוב ציון משוקלל
            total_score = (
                main_search_score * weights['main_search'] +
                keyword_score * weights['keywords'] +
                geographic_score * weights['geographic'] +
                temporal_score * weights['temporal'] +
                price_score * weights['price_impact'] +
                audience_score * weights['audience']
            )

            return min(max(total_score, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating trends score: {str(e)}")
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
            return "Strong Buy - High search interest with positive trends"
        elif score >= 60:
            return "Buy - Good search momentum with positive indicators"
        elif score >= 40:
            return "Hold - Moderate search interest, monitor for changes"
        else:
            return "Sell - Low search interest or negative trends"

    def _extract_key_signals(self, main_search_analysis: Dict, keyword_analysis: Dict,
                           geographic_analysis: Dict, temporal_analysis: Dict,
                           price_impact_analysis: Dict, audience_analysis: Dict) -> List[str]:
        """
        חילוץ אותות מפתח
        """
        signals = []

        # אותות חיפוש עיקריים
        if main_search_analysis.get('is_trending', False):
            signals.append(f"Search trending: {main_search_analysis.get('interest_spike', 1.0):.2f}x")

        # אותות מילות מפתח
        trending_keywords = keyword_analysis.get('trending_keywords', [])
        if trending_keywords:
            signals.append(f"Trending keywords: {', '.join(trending_keywords[:3])}")

        # אותות גיאוגרפיים
        if geographic_analysis.get('global_reach', False):
            signals.append("Global search interest detected")

        # אותות מגמה
        if temporal_analysis.get('accelerating', False):
            signals.append("Search interest accelerating")
        elif temporal_analysis.get('decelerating', False):
            signals.append("Search interest decelerating")

        # אותות השפעת מחיר
        if price_impact_analysis.get('search_price_alignment', False):
            signals.append("Search-price correlation detected")

        # אותות קהל
        if audience_analysis.get('viral_potential', False):
            signals.append("High viral potential")

        return signals

    def _fetch_search_data(self, query: str, geo: str = None) -> Dict[str, Any]:
        """
        שליפת נתוני חיפוש
        """
        try:
            # כאן תהיה קריאה אמיתית ל-Google Trends API
            # כרגע נחזיר נתונים מדומים לצורך הדוגמה
            
            # סימולציה של נתונים
            current_interest = np.random.randint(0, 100)
            avg_interest = np.random.randint(20, 80)
            
            # יצירת נתוני מגמה
            trend_data = []
            for i in range(30):
                trend_data.append({
                    'date': (datetime.now() - timedelta(days=30-i)).isoformat(),
                    'interest': np.random.randint(0, 100)
                })
            
            return {
                'current_interest': current_interest,
                'average_interest': avg_interest,
                'interest_spike': current_interest / max(avg_interest, 1),
                'trend_direction': 'increasing' if current_interest > avg_interest else 'decreasing',
                'trend_data': trend_data
            }
            
        except Exception as e:
            logger.error(f"Error fetching search data: {str(e)}")
            return None

    def _generate_related_keywords(self, symbol: str) -> List[str]:
        """
        יצירת מילות מפתח קשורות
        """
        base_keywords = [
            f"{symbol} stock",
            f"{symbol} earnings",
            f"{symbol} news",
            f"{symbol} price",
            f"{symbol} buy",
            f"{symbol} sell"
        ]
        
        # הוספת מילות מפתח פיננסיות
        financial_keywords = [f"{symbol} {kw}" for kw in self.financial_keywords]
        
        return base_keywords + financial_keywords

    def _fetch_historical_data(self, symbol: str) -> pd.DataFrame:
        """
        שליפת נתונים היסטוריים
        """
        try:
            # סימולציה של נתונים היסטוריים
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                                end=datetime.now(), freq='D')
            interests = np.random.randint(0, 100, size=len(dates))
            
            return pd.DataFrame({
                'date': dates,
                'interest': interests
            })
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()

    def _calculate_trend_direction(self, trend_data: List[Dict]) -> str:
        """
        חישוב כיוון מגמה
        """
        try:
            if len(trend_data) < 2:
                return "stable"
            
            interests = [d['interest'] for d in trend_data]
            recent_avg = np.mean(interests[-7:])  # 7 ימים אחרונים
            older_avg = np.mean(interests[:-7])   # ימים קודמים
            
            if recent_avg > older_avg * 1.2:
                return "increasing"
            elif recent_avg < older_avg * 0.8:
                return "decreasing"
            else:
                return "stable"
                
        except Exception:
            return "stable"

    def _calculate_trend_strength(self, trend_data: List[Dict]) -> float:
        """
        חישוב עוצמת מגמה
        """
        try:
            if len(trend_data) < 2:
                return 0.5
            
            interests = [d['interest'] for d in trend_data]
            slope = np.polyfit(range(len(interests)), interests, 1)[0]
            return min(abs(slope) / 10, 1.0)
            
        except Exception:
            return 0.5

    def _detect_trend_spikes(self, trend_values: np.ndarray) -> List[int]:
        """
        זיהוי קפיצות במגמה
        """
        try:
            if len(trend_values) < 3:
                return []
            
            mean = np.mean(trend_values)
            std = np.std(trend_values)
            threshold = mean + 2 * std
            
            spikes = []
            for i, value in enumerate(trend_values):
                if value > threshold:
                    spikes.append(i)
            
            return spikes
            
        except Exception:
            return []

    def _create_empty_search_analysis(self) -> Dict[str, Any]:
        """
        יצירת ניתוח חיפוש ריק
        """
        return {
            "current_interest": 0,
            "average_interest": 0,
            "interest_spike": 1.0,
            "trend_direction": "stable",
            "trend_strength": 0.5,
            "trend_data": [],
            "is_trending": False,
            "high_interest": False,
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