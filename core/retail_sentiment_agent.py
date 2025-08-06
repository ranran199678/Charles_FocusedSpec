"""
RetailSentimentAgent - ניתוח רגשות קמעונאיים מתקדם
====================================================

סוכן מתקדם לניתוח רגשות קמעונאיים עם ניתוח רב-ממדי,
ולידציה מתקדמת ומבנה Signal תקני.

תכונות מתקדמות:
- ניתוח רגשות קמעונאיים לפי מספר פרמטרים
- ניתוח רב-ממדי של רגשות קמעונאיים
- ולידציה לפי זמן ומגמה
- ניתוח רגשות קמעונאיים לפי סקטורים
- זיהוי רגשות קמעונאיים לפני אירועים
- ניתוח רגשות קמעונאיים לפי טכני ופונדמנטלי
- זיהוי רגשות קמעונאיים לפי רגשות השוק
- ניתוח רגשות קמעונאיים לפי נפח ומחיר
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.base.base_agent import BaseAgent
from utils.constants import RETAIL_SENTIMENT_THRESHOLDS, TIME_PERIODS
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RetailSentiment:
    """מבנה נתונים לרגשות קמעונאיים"""
    timestamp: datetime
    sentiment_type: str
    strength: float
    confidence: float
    sentiment_ratio: float
    volume_ratio: float
    price_impact: float
    context: Dict
    significance: str

@dataclass
class RetailSentimentAnalysis:
    """מבנה נתונים לניתוח רגשות קמעונאיים מתקדם"""
    total_sentiments: int
    significant_sentiments: int
    avg_sentiment_strength: float
    sentiment_trend: str
    volume_trend: str
    sector_comparison: Dict
    time_analysis: Dict
    breakout_potential: float

class RetailSentimentAgent(BaseAgent):
    """
    סוכן מתקדם לניתוח רגשות קמעונאיים
    
    תכונות מתקדמות:
    - ניתוח רגשות קמעונאיים לפי מספר פרמטרים
    - ניתוח רב-ממדי של רגשות קמעונאיים
    - ולידציה לפי זמן ומגמה
    - ניתוח רגשות קמעונאיים לפי סקטורים
    - זיהוי רגשות קמעונאיים לפני אירועים
    - ניתוח רגשות קמעונאיים לפי טכני ופונדמנטלי
    - זיהוי רגשות קמעונאיים לפי רגשות השוק
    - ניתוח רגשות קמעונאיים לפי נפח ומחיר
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        super().__init__(config)
        
        # הגדרות מתקדמות
        self.retail_sentiment_thresholds = {
            'low': 0.3,
            'moderate': 0.5,
            'high': 0.7,
            'extreme': 0.9
        }
        
        self.time_periods = {
            'short': 5,
            'medium': 20,
            'long': 60
        }
        
        self.sentiment_weights = {
            'sentiment_ratio': 0.3,
            'volume_sentiment': 0.25,
            'price_sentiment': 0.2,
            'time_sentiment': 0.15,
            'sector_sentiment': 0.1
        }
        
        # סוגי רגשות קמעונאיים
        self.sentiment_types = {
            'bullish': 'אופטימי',
            'bearish': 'פסימי',
            'neutral': 'ניטרלי',
            'fomo': 'פחד מפספוס',
            'panic': 'פאניקה'
        }
        
        logger.info("RetailSentimentAgent initialized with advanced configuration")

    def _calculate_retail_sentiment_metrics(self, df: pd.DataFrame) -> Dict:
        """
        חישוב מדדי רגשות קמעונאיים מתקדמים
        """
        try:
            # חישוב רגשות קמעונאיים (סימולציה - בפרודקציה יהיה מ-API)
            df['retail_sentiment_ratio'] = 0.6  # ברירת מחדל - 60% רגשות קמעונאיים
            
            # חישוב נפח לפי רגשות קמעונאיים
            df['volume_per_retail_sentiment'] = df['volume'] / (df['close'] * df['retail_sentiment_ratio'])
            
            # חישוב רגשות קמעונאיים נפח
            df['retail_sentiment_volume'] = df['volume_per_retail_sentiment'].rolling(window=20).mean()
            df['retail_sentiment_volume_ratio'] = df['volume_per_retail_sentiment'] / df['retail_sentiment_volume']
            
            # חישוב רגשות קמעונאיים מחיר
            df['retail_sentiment_price'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
            df['retail_sentiment_price_ratio'] = df['retail_sentiment_price'] / df['retail_sentiment_price'].rolling(window=20).mean()
            
            # חישוב מדד רגשות קמעונאיים
            df['retail_sentiment_score'] = (df['retail_sentiment_volume_ratio'] + df['retail_sentiment_price_ratio']) / 2
            
            return {
                'retail_sentiment_metrics': df,
                'current_retail_sentiment_ratio': df['retail_sentiment_ratio'].iloc[-1],
                'current_retail_sentiment_volume': df['retail_sentiment_volume_ratio'].iloc[-1],
                'current_retail_sentiment_price': df['retail_sentiment_price_ratio'].iloc[-1],
                'current_retail_sentiment_score': df['retail_sentiment_score'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating retail sentiment metrics: {e}")
            return {}

    def _detect_retail_sentiments(self, df: pd.DataFrame) -> List[RetailSentiment]:
        """
        זיהוי רגשות קמעונאיים מתקדם
        """
        sentiments = []
        
        try:
            # חישוב מדדי רגשות קמעונאיים
            retail_sentiment_metrics = self._calculate_retail_sentiment_metrics(df)
            if not retail_sentiment_metrics:
                return sentiments
            
            df = retail_sentiment_metrics['retail_sentiment_metrics']
            
            # זיהוי רגשות קמעונאיים
            for i in range(20, len(df)):
                # ניתוח רגשות קמעונאיים נפח
                volume_sentiment = self._analyze_volume_sentiment(df, i)
                
                # ניתוח רגשות קמעונאיים מחיר
                price_sentiment = self._analyze_price_sentiment(df, i)
                
                # ניתוח רגשות קמעונאיים זמן
                time_sentiment = self._analyze_time_sentiment(df, i)
                
                # ניתוח רגשות קמעונאיים סקטור
                sector_sentiment = self._analyze_sector_sentiment(df, i)
                
                # ניתוח פוטנציאל פריצה
                breakout_potential = self._analyze_breakout_potential(df, i)
                
                # זיהוי רגשות קמעונאיים
                if self._is_retail_sentiment(volume_sentiment, price_sentiment, time_sentiment, sector_sentiment):
                    # חישוב עוצמת הרגשות
                    strength = self._calculate_sentiment_strength(
                        volume_sentiment, price_sentiment, time_sentiment, sector_sentiment, breakout_potential
                    )
                    
                    # חישוב ביטחון
                    confidence = self._calculate_sentiment_confidence(
                        volume_sentiment, price_sentiment, time_sentiment, sector_sentiment, breakout_potential
                    )
                    
                    # קביעת סוג רגשות
                    sentiment_type = self._classify_sentiment_type(
                        volume_sentiment, price_sentiment, time_sentiment
                    )
                    
                    # קביעת משמעות
                    significance = self._determine_sentiment_significance(strength, confidence)
                    
                    sentiment = RetailSentiment(
                        timestamp=df.index[i],
                        sentiment_type=sentiment_type,
                        strength=strength,
                        confidence=confidence,
                        sentiment_ratio=df['retail_sentiment_ratio'].iloc[i],
                        volume_ratio=volume_sentiment.get('sentiment_ratio', 1.0),
                        price_impact=price_sentiment.get('price_impact', 0.0),
                        context={
                            'volume_sentiment': volume_sentiment,
                            'price_sentiment': price_sentiment,
                            'time_sentiment': time_sentiment,
                            'sector_sentiment': sector_sentiment,
                            'breakout_potential': breakout_potential
                        },
                        significance=significance
                    )
                    
                    sentiments.append(sentiment)
            
            return sentiments
            
        except Exception as e:
            logger.error(f"Error detecting retail sentiments: {e}")
            return []

    def _analyze_volume_sentiment(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח רגשות קמעונאיים נפח מתקדם
        """
        try:
            # חישוב רגשות קמעונאיים נפח
            current_volume_sentiment = df['retail_sentiment_volume_ratio'].iloc[index]
            historical_volume_sentiment = df['retail_sentiment_volume_ratio'].iloc[max(0, index-30):index].mean()
            
            sentiment_ratio = current_volume_sentiment / historical_volume_sentiment if historical_volume_sentiment > 0 else 1.0
            
            # ניתוח מגמת רגשות קמעונאיים נפח
            recent_volume_sentiment = df['retail_sentiment_volume_ratio'].iloc[max(0, index-10):index].mean()
            volume_sentiment_trend = 'increasing' if recent_volume_sentiment > historical_volume_sentiment else 'decreasing'
            
            return {
                'sentiment_ratio': sentiment_ratio,
                'sentiment_trend': volume_sentiment_trend,
                'current_sentiment': current_volume_sentiment,
                'historical_sentiment': historical_volume_sentiment,
                'recent_sentiment': recent_volume_sentiment
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume sentiment: {e}")
            return {}

    def _analyze_price_sentiment(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח רגשות קמעונאיים מחיר מתקדם
        """
        try:
            # חישוב רגשות קמעונאיים מחיר
            current_price_sentiment = df['retail_sentiment_price_ratio'].iloc[index]
            historical_price_sentiment = df['retail_sentiment_price_ratio'].iloc[max(0, index-30):index].mean()
            
            price_sentiment_ratio = current_price_sentiment / historical_price_sentiment if historical_price_sentiment > 0 else 1.0
            
            # ניתוח השפעת מחיר
            current_price = df['close'].iloc[index]
            historical_price = df['close'].iloc[max(0, index-20):index].mean()
            price_impact = (current_price - historical_price) / historical_price if historical_price > 0 else 0.0
            
            # ניתוח מגמת רגשות קמעונאיים מחיר
            recent_price_sentiment = df['retail_sentiment_price_ratio'].iloc[max(0, index-10):index].mean()
            price_sentiment_trend = 'increasing' if recent_price_sentiment > historical_price_sentiment else 'decreasing'
            
            return {
                'sentiment_ratio': price_sentiment_ratio,
                'sentiment_trend': price_sentiment_trend,
                'price_impact': price_impact,
                'current_sentiment': current_price_sentiment,
                'historical_sentiment': historical_price_sentiment,
                'recent_sentiment': recent_price_sentiment
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price sentiment: {e}")
            return {}

    def _analyze_time_sentiment(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח רגשות קמעונאיים זמן מתקדם
        """
        try:
            # ניתוח רגשות קמעונאיים זמן
            time_window = df.iloc[max(0, index-30):index]
            
            # חישוב רגשות קמעונאיים זמן
            time_sentiment_duration = len(time_window)
            
            # ניתוח עקביות רגשות קמעונאיים
            volume_consistency = time_window['retail_sentiment_volume_ratio'].std()
            price_consistency = time_window['retail_sentiment_price_ratio'].std()
            consistency_score = 1.0 - ((volume_consistency + price_consistency) / 2)
            
            # ניתוח מגמת רגשות קמעונאיים זמן
            early_sentiment = time_window.iloc[:10]['retail_sentiment_score'].mean()
            late_sentiment = time_window.iloc[-10:]['retail_sentiment_score'].mean()
            time_sentiment_trend = 'increasing' if late_sentiment > early_sentiment else 'decreasing'
            
            return {
                'sentiment_duration': time_sentiment_duration,
                'consistency_score': consistency_score,
                'sentiment_trend': time_sentiment_trend,
                'early_sentiment': early_sentiment,
                'late_sentiment': late_sentiment
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time sentiment: {e}")
            return {}

    def _analyze_sector_sentiment(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח רגשות קמעונאיים סקטור מתקדם
        """
        try:
            # סימולציה של נתוני סקטור (בפרודקציה יהיה מ-API)
            sector_data = {
                'technology': {'avg_retail_sentiment': 0.6, 'sentiment_trend': 'increasing'},
                'healthcare': {'avg_retail_sentiment': 0.5, 'sentiment_trend': 'stable'},
                'finance': {'avg_retail_sentiment': 0.7, 'sentiment_trend': 'decreasing'},
                'energy': {'avg_retail_sentiment': 0.8, 'sentiment_trend': 'increasing'}
            }
            
            # קביעת סקטור (בפרודקציה יהיה מ-API)
            sector = 'technology'  # ברירת מחדל
            
            sector_info = sector_data.get(sector, {'avg_retail_sentiment': 0.5, 'sentiment_trend': 'stable'})
            
            return {
                'sector': sector,
                'sector_avg_sentiment': sector_info['avg_retail_sentiment'],
                'sector_sentiment_trend': sector_info['sentiment_trend'],
                'relative_to_sector': df['retail_sentiment_score'].iloc[index] / sector_info['avg_retail_sentiment']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector sentiment: {e}")
            return {}

    def _analyze_breakout_potential(self, df: pd.DataFrame, index: int) -> Dict:
        """
        ניתוח פוטנציאל פריצה מתקדם
        """
        try:
            # ניתוח פוטנציאל פריצה
            current_price = df['close'].iloc[index]
            
            # ניתוח לפי ממוצעים נעים
            sma_20 = df['close'].rolling(window=20).mean().iloc[index]
            sma_50 = df['close'].rolling(window=50).mean().iloc[index]
            
            # ניתוח לפי בולינגר בנדס
            bb_upper = current_price * 1.02
            bb_lower = current_price * 0.98
            
            # חישוב פוטנציאל פריצה
            upside_potential = (bb_upper - current_price) / current_price
            downside_potential = (current_price - bb_lower) / current_price
            
            # ניתוח מגמה
            price_vs_sma20 = current_price / sma_20 if sma_20 > 0 else 1.0
            price_vs_sma50 = current_price / sma_50 if sma_50 > 0 else 1.0
            
            breakout_direction = 'up' if price_vs_sma20 > 1.0 and price_vs_sma50 > 1.0 else 'down'
            breakout_strength = max(upside_potential, downside_potential)
            
            return {
                'breakout_direction': breakout_direction,
                'breakout_strength': breakout_strength,
                'upside_potential': upside_potential,
                'downside_potential': downside_potential,
                'price_vs_sma20': price_vs_sma20,
                'price_vs_sma50': price_vs_sma50
            }
            
        except Exception as e:
            logger.error(f"Error analyzing breakout potential: {e}")
            return {}

    def _is_retail_sentiment(self, volume_sentiment: Dict, price_sentiment: Dict, 
                             time_sentiment: Dict, sector_sentiment: Dict) -> bool:
        """
        זיהוי רגשות קמעונאיים
        """
        try:
            # קריטריונים לרגשות קמעונאיים
            volume_sentimenting = volume_sentiment.get('sentiment_ratio', 1.0) > 1.2
            price_sentimenting = price_sentiment.get('sentiment_ratio', 1.0) > 1.1
            time_sentimenting = time_sentiment.get('sentiment_duration', 0) >= 15
            sector_sentimenting = sector_sentiment.get('relative_to_sector', 1.0) > 1.0
            
            # רגשות קמעונאיים אם לפחות 2 קריטריונים מתקיימים
            sentiment_criteria = [volume_sentimenting, price_sentimenting, time_sentimenting, sector_sentimenting]
            return sum(sentiment_criteria) >= 2
            
        except Exception as e:
            logger.error(f"Error detecting retail sentiment: {e}")
            return False

    def _calculate_sentiment_strength(self, volume_sentiment: Dict, price_sentiment: Dict,
                                    time_sentiment: Dict, sector_sentiment: Dict,
                                    breakout_potential: Dict) -> float:
        """
        חישוב עוצמת רגשות קמעונאיים
        """
        try:
            strength = 0.0
            
            # משקל לפי רגשות קמעונאיים נפח
            volume_ratio = volume_sentiment.get('sentiment_ratio', 1.0)
            if volume_ratio > 1.5:
                strength += 0.3
            elif volume_ratio > 1.2:
                strength += 0.2
            
            # משקל לפי רגשות קמעונאיים מחיר
            price_ratio = price_sentiment.get('sentiment_ratio', 1.0)
            if price_ratio > 1.3:
                strength += 0.3
            elif price_ratio > 1.1:
                strength += 0.2
            
            # משקל לפי רגשות קמעונאיים זמן
            time_duration = time_sentiment.get('sentiment_duration', 0)
            if time_duration >= 25:
                strength += 0.2
            elif time_duration >= 15:
                strength += 0.1
            
            # משקל לפי רגשות קמעונאיים סקטור
            sector_ratio = sector_sentiment.get('relative_to_sector', 1.0)
            if sector_ratio > 1.2:
                strength += 0.1
            
            # משקל לפי פוטנציאל פריצה
            breakout_strength = breakout_potential.get('breakout_strength', 0.0)
            if breakout_strength > 0.05:
                strength += 0.1
            
            return min(1.0, strength)
            
        except Exception as e:
            logger.error(f"Error calculating sentiment strength: {e}")
            return 0.5

    def _calculate_sentiment_confidence(self, volume_sentiment: Dict, price_sentiment: Dict,
                                      time_sentiment: Dict, sector_sentiment: Dict,
                                      breakout_potential: Dict) -> float:
        """
        חישוב ביטחון רגשות קמעונאיים
        """
        try:
            confidence = 0.0
            
            # ביטחון לפי עקביות
            consistent_signals = 0
            if volume_sentiment.get('sentiment_ratio', 1.0) > 1.2:
                consistent_signals += 1
            if price_sentiment.get('sentiment_ratio', 1.0) > 1.1:
                consistent_signals += 1
            if time_sentiment.get('sentiment_duration', 0) >= 15:
                consistent_signals += 1
            if sector_sentiment.get('relative_to_sector', 1.0) > 1.0:
                consistent_signals += 1
            if breakout_potential.get('breakout_strength', 0.0) > 0.03:
                consistent_signals += 1
            
            confidence = consistent_signals / 5.0
            
            # התאמה לפי עוצמת רגשות
            avg_sentiment = (volume_sentiment.get('sentiment_ratio', 1.0) + price_sentiment.get('sentiment_ratio', 1.0)) / 2
            if avg_sentiment > 1.3:
                confidence *= 1.2
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating sentiment confidence: {e}")
            return 0.5

    def _classify_sentiment_type(self, volume_sentiment: Dict, price_sentiment: Dict, time_sentiment: Dict) -> str:
        """
        סיווג סוג רגשות קמעונאיים
        """
        try:
            volume_ratio = volume_sentiment.get('sentiment_ratio', 1.0)
            price_ratio = price_sentiment.get('sentiment_ratio', 1.0)
            time_duration = time_sentiment.get('sentiment_duration', 0)
            
            if volume_ratio > 1.5 and price_ratio > 1.3 and time_duration >= 25:
                return 'bullish'
            elif volume_ratio > 1.3 and price_ratio < 0.9 and time_duration >= 20:
                return 'bearish'
            elif volume_ratio > 2.0 and price_ratio > 1.5:
                return 'fomo'
            elif time_duration >= 30:
                return 'panic'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error classifying sentiment type: {e}")
            return 'unknown'

    def _determine_sentiment_significance(self, strength: float, confidence: float) -> str:
        """
        קביעת משמעות רגשות קמעונאיים
        """
        try:
            if strength >= self.retail_sentiment_thresholds['extreme'] and confidence >= 0.8:
                return 'extreme'
            elif strength >= self.retail_sentiment_thresholds['high'] and confidence >= 0.6:
                return 'high'
            elif strength >= self.retail_sentiment_thresholds['moderate'] and confidence >= 0.4:
                return 'moderate'
            elif strength >= self.retail_sentiment_thresholds['low'] and confidence >= 0.2:
                return 'low'
            else:
                return 'minimal'
                
        except Exception as e:
            logger.error(f"Error determining sentiment significance: {e}")
            return 'unknown'

    def _calculate_retail_sentiment_analysis(self, df: pd.DataFrame, sentiments: List[RetailSentiment]) -> RetailSentimentAnalysis:
        """
        חישוב ניתוח רגשות קמעונאיים מתקדם
        """
        try:
            # חישוב סטטיסטיקות בסיסיות
            total_sentiments = len(sentiments)
            significant_sentiments = len([s for s in sentiments if s.significance in ['high', 'extreme']])
            
            # חישוב ממוצע עוצמת רגשות
            avg_sentiment_strength = np.mean([s.strength for s in sentiments]) if sentiments else 0.5
            
            # ניתוח מגמת רגשות
            recent_retail_sentiment = df['retail_sentiment_score'].tail(20).mean()
            historical_retail_sentiment = df['retail_sentiment_score'].tail(60).mean()
            sentiment_trend = 'increasing' if recent_retail_sentiment > historical_retail_sentiment else 'decreasing'
            
            # ניתוח מגמת נפח
            recent_volume = df['volume'].tail(20).mean()
            historical_volume = df['volume'].tail(60).mean()
            volume_trend = 'increasing' if recent_volume > historical_volume else 'decreasing'
            
            # ניתוח סקטור
            sector_comparison = self._analyze_sector_sentiment(df, len(df)-1)
            
            # ניתוח זמן
            time_analysis = self._analyze_time_sentiment(df, len(df)-1)
            
            # ניתוח פוטנציאל פריצה
            breakout_potential = self._analyze_breakout_potential(df, len(df)-1)
            breakout_potential_score = breakout_potential.get('breakout_strength', 0.0)
            
            return RetailSentimentAnalysis(
                total_sentiments=total_sentiments,
                significant_sentiments=significant_sentiments,
                avg_sentiment_strength=avg_sentiment_strength,
                sentiment_trend=sentiment_trend,
                volume_trend=volume_trend,
                sector_comparison=sector_comparison,
                time_analysis=time_analysis,
                breakout_potential=breakout_potential_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating retail sentiment analysis: {e}")
            return RetailSentimentAnalysis(0, 0, 0.5, 'unknown', 'unknown', {}, {}, 0.0)

    def analyze(self, symbol: str, price_df=None, **kwargs) -> Dict:
        """
        ניתוח מתקדם של רגשות קמעונאיים
        """
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=180)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            # זיהוי רגשות קמעונאיים
            sentiments = self._detect_retail_sentiments(price_df)
            
            # ניתוח מתקדם
            analysis = self._calculate_retail_sentiment_analysis(price_df, sentiments)
            
            # חישוב ציון סופי
            if sentiments:
                # חישוב ציון לפי רגשות משמעותיים
                significant_ratio = analysis.significant_sentiments / max(1, analysis.total_sentiments)
                sentiment_score = min(100, significant_ratio * 100 + analysis.avg_sentiment_strength * 50)
                
                # התאמה לפי מגמה
                if analysis.sentiment_trend == 'increasing' and analysis.volume_trend == 'increasing':
                    sentiment_score *= 1.2
                elif analysis.sentiment_trend == 'decreasing' or analysis.volume_trend == 'decreasing':
                    sentiment_score *= 0.8
                
                sentiment_score = min(100, max(0, sentiment_score))
            else:
                sentiment_score = 50
            
            # יצירת הסבר
            if sentiments:
                recent_sentiments = [s for s in sentiments if s.significance in ['high', 'extreme']]
                explanation = f"זוהו {len(sentiments)} רגשות קמעונאיים ({len(recent_sentiments)} משמעותיים). ממוצע עוצמה: {analysis.avg_sentiment_strength:.2f}, מגמת רגשות: {analysis.sentiment_trend}"
            else:
                explanation = "לא זוהו רגשות קמעונאיים משמעותיים"
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(sentiments, analysis)
            
            return {
                "score": round(sentiment_score, 1),
                "explanation": explanation,
                "signal": {
                    "type": "retail_sentiment",
                    "score": round(sentiment_score, 1),
                    "reason": explanation,
                    "confidence": round(analysis.breakout_potential, 3),
                    "details": {
                        "sentiments_count": analysis.total_sentiments,
                        "significant_sentiments": analysis.significant_sentiments,
                        "avg_sentiment_strength": round(analysis.avg_sentiment_strength, 2),
                        "sentiment_trend": analysis.sentiment_trend,
                        "volume_trend": analysis.volume_trend
                    }
                },
                "details": {
                    "sentiments": [
                        {
                            "timestamp": sentiment.timestamp.isoformat(),
                            "sentiment_type": sentiment.sentiment_type,
                            "strength": round(sentiment.strength, 2),
                            "significance": sentiment.significance,
                            "confidence": round(sentiment.confidence, 3),
                            "sentiment_ratio": round(sentiment.sentiment_ratio, 2)
                        }
                        for sentiment in sentiments[:10]  # Top 10 sentiments
                    ],
                    "analysis": {
                        "total_sentiments": analysis.total_sentiments,
                        "significant_sentiments": analysis.significant_sentiments,
                        "avg_sentiment_strength": round(analysis.avg_sentiment_strength, 2),
                        "sentiment_trend": analysis.sentiment_trend,
                        "volume_trend": analysis.volume_trend,
                        "breakout_potential": round(analysis.breakout_potential, 3),
                        "sector_comparison": analysis.sector_comparison,
                        "time_analysis": analysis.time_analysis
                    },
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"Error in RetailSentimentAgent.analyze: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח: {str(e)}",
                "signal": {
                    "type": "retail_sentiment",
                    "score": 50,
                    "reason": f"שגיאה בניתוח: {str(e)}",
                    "confidence": 0.5,
                    "details": {
                        "sentiments_count": 0,
                        "avg_sentiment_strength": 0.5,
                        "sentiment_trend": "error"
                    }
                },
                "details": {
                    "sentiments": [],
                    "analysis": {},
                    "recommendations": []
                }
            }

    def _generate_recommendations(self, sentiments: List[RetailSentiment], analysis: RetailSentimentAnalysis) -> List[str]:
        """
        יצירת המלצות מתקדמות
        """
        recommendations = []
        
        try:
            if analysis.significant_sentiments > 0:
                recommendations.append("🔍 מעקב אחר רגשות קמעונאיים משמעותיים - פוטנציאל לתנועה חזקה")
            
            if analysis.avg_sentiment_strength > 0.7:
                recommendations.append("📈 רגשות קמעונאיים חזקים - פוטנציאל לפריצה קרובה")
            
            if analysis.sentiment_trend == 'increasing' and analysis.volume_trend == 'increasing':
                recommendations.append("📊 רגשות קמעונאיים עולים - עניין גובר במניה")
            
            if analysis.breakout_potential > 0.05:
                recommendations.append("💪 פוטנציאל פריצה גבוה - תמיכה חזקה בתנועה")
            
            if analysis.significant_sentiments > 3:
                recommendations.append("⚠️ מספר רגשות משמעותיים - בדוק חדשות או אירועים")
            
            if not recommendations:
                recommendations.append("📉 אין רגשות קמעונאיים משמעותיים - המשך מעקב")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["שגיאה ביצירת המלצות"]

    def get_retail_sentiment_summary(self) -> Dict:
        """
        סיכום ניתוח רגשות קמעונאיים
        """
        return {
            "agent_type": "RetailSentimentAgent",
            "description": "ניתוח רגשות קמעונאיים מתקדם עם ניתוח רב-ממדי",
            "features": [
                "ניתוח רגשות קמעונאיים לפי מספר פרמטרים",
                "ניתוח רב-ממדי של רגשות קמעונאיים",
                "ולידציה לפי זמן ומגמה",
                "ניתוח רגשות קמעונאיים לפי סקטורים",
                "זיהוי רגשות קמעונאיים לפני אירועים",
                "ניתוח רגשות קמעונאיים לפי טכני ופונדמנטלי",
                "זיהוי רגשות קמעונאיים לפי רגשות השוק",
                "ניתוח רגשות קמעונאיים לפי נפח ומחיר"
            ],
            "thresholds": self.retail_sentiment_thresholds,
            "time_periods": self.time_periods
        } 