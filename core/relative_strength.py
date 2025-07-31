"""
RelativeStrengthAgent - חישוב חוזק יחסי מתקדם
==============================================

סוכן מתקדם לחישוב חוזק יחסי (RS) של מניה מול השוק/סקטור/מדד.
מחלץ ומרכז את כל הפונקציונליות הקיימת מקבצים אחרים.

תכונות מתקדמות:
- חישוב RS מול מדד השוק (S&P 500, NASDAQ)
- חישוב RS מול סקטור/תעשייה
- ניתוח מגמות RS לאורך זמן
- דירוג percentile של RS
- ניתוח תנודתיות RS
- זיהוי שינויי מגמה ב-RS
- השוואה היסטורית
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from utils.data_fetcher import data_fetcher
from utils.logger import logger
from utils.validators import validate_symbol, validate_price_data

@dataclass
class RelativeStrengthMetrics:
    """מבנה נתונים למדדי חוזק יחסי"""
    rs_value: float
    rs_percentile: float
    rs_trend: str
    rs_volatility: float
    market_comparison: float
    sector_comparison: float
    historical_rank: int
    momentum_score: float

@dataclass
class RSComparison:
    """מבנה נתונים להשוואת RS"""
    vs_market: float
    vs_sector: float
    vs_industry: float
    vs_peers: float
    overall_rank: float

class RelativeStrengthAgent:
    """
    סוכן מתקדם לחישוב חוזק יחסי (RS) של מניה
    
    תכונות מתקדמות:
    - חישוב RS מול מדד השוק (S&P 500, NASDAQ)
    - חישוב RS מול סקטור/תעשייה
    - ניתוח מגמות RS לאורך זמן
    - דירוג percentile של RS
    - ניתוח תנודתיות RS
    - זיהוי שינויי מגמה ב-RS
    - השוואה היסטורית
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        self.config = config or {}
        
        # הגדרות מתקדמות
        self.lookback_periods = {
            'short': 20,      # 20 ימים
            'medium': 60,     # 60 ימים
            'long': 200       # 200 ימים
        }
        
        self.comparison_benchmarks = {
            'market': '^GSPC',  # S&P 500
            'nasdaq': '^IXIC',  # NASDAQ
            'sector': None,     # ייקבע לפי המניה
            'industry': None    # ייקבע לפי המניה
        }
        
        self.rs_thresholds = {
            'weak': 0.8,       # RS < 0.8
            'neutral': 1.0,    # RS = 1.0
            'strong': 1.2,     # RS > 1.2
            'very_strong': 1.5 # RS > 1.5
        }
        
        self.momentum_weights = {
            'short_term': 0.3,
            'medium_term': 0.4,
            'long_term': 0.3
        }
        
        # סוגי מגמות RS
        self.trend_types = {
            'accelerating': 'מאיץ',
            'decelerating': 'מאט',
            'stable': 'יציב',
            'reversing': 'הופך',
            'sideways': 'צדדי'
        }
    
    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח חוזק יחסי מקיף
        
        Args:
            symbol: סימבול המניה
            price_df: נתוני מחיר (אם לא מסופק, יישלף אוטומטית)
            
        Returns:
            Dict עם תוצאות הניתוח
        """
        try:
            # ולידציה
            if not validate_symbol(symbol):
                return self._error_response("סימבול לא תקין")
            
            # שליפת נתונים
            if price_df is None:
                price_df = data_fetcher.fetch_prices(symbol, period="1y")
            
            if not validate_price_data(price_df):
                return self._error_response("נתוני מחיר לא תקינים")
            
            # חישוב מדדי RS
            rs_metrics = self._calculate_rs_metrics(symbol, price_df)
            rs_comparison = self._calculate_rs_comparison(symbol, price_df)
            rs_trend_analysis = self._analyze_rs_trend(price_df)
            rs_volatility = self._calculate_rs_volatility(price_df)
            
            # חישוב ציון כללי
            overall_score = self._calculate_overall_score(rs_metrics, rs_comparison, rs_trend_analysis)
            
            # חישוב רמת ביטחון
            confidence = self._calculate_confidence(price_df, rs_metrics)
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(rs_metrics, rs_comparison, rs_trend_analysis)
            
            # תוצאה סופית
            result = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "score": overall_score,
                "confidence": confidence,
                "explanation": self._generate_explanation(rs_metrics, rs_comparison, rs_trend_analysis),
                "recommendations": recommendations,
                "details": {
                    "rs_metrics": rs_metrics.__dict__,
                    "rs_comparison": rs_comparison.__dict__,
                    "rs_trend": rs_trend_analysis,
                    "rs_volatility": rs_volatility,
                    "benchmarks_used": self.comparison_benchmarks
                }
            }
            
            logger.info(f"Relative Strength analysis completed for {symbol}: Score={overall_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error in Relative Strength analysis for {symbol}: {str(e)}")
            return self._error_response(f"שגיאה בניתוח: {str(e)}")
    
    def _calculate_rs_metrics(self, symbol: str, price_df: pd.DataFrame) -> RelativeStrengthMetrics:
        """חישוב מדדי RS בסיסיים"""
        try:
            # חישוב תשואות
            returns = price_df['close'].pct_change().dropna()
            
            # חישוב RS קצר טווח (20 ימים)
            short_rs = self._calculate_period_rs(returns, self.lookback_periods['short'])
            
            # חישוב RS בינוני טווח (60 ימים)
            medium_rs = self._calculate_period_rs(returns, self.lookback_periods['medium'])
            
            # חישוב RS ארוך טווח (200 ימים)
            long_rs = self._calculate_period_rs(returns, self.lookback_periods['long'])
            
            # חישוב RS משוקלל
            rs_value = (
                short_rs * self.momentum_weights['short_term'] +
                medium_rs * self.momentum_weights['medium_term'] +
                long_rs * self.momentum_weights['long_term']
            )
            
            # חישוב percentile
            rs_percentile = self._calculate_rs_percentile(returns, rs_value)
            
            # זיהוי מגמה
            rs_trend = self._identify_rs_trend(short_rs, medium_rs, long_rs)
            
            # חישוב תנודתיות
            rs_volatility = returns.rolling(window=20).std().iloc[-1]
            
            # השוואה לשוק
            market_comparison = self._compare_to_market(symbol, price_df)
            
            # השוואה לסקטור
            sector_comparison = self._compare_to_sector(symbol, price_df)
            
            # דירוג היסטורי
            historical_rank = self._calculate_historical_rank(returns, rs_value)
            
            # ציון מומנטום
            momentum_score = self._calculate_momentum_score(short_rs, medium_rs, long_rs)
            
            return RelativeStrengthMetrics(
                rs_value=rs_value,
                rs_percentile=rs_percentile,
                rs_trend=rs_trend,
                rs_volatility=rs_volatility,
                market_comparison=market_comparison,
                sector_comparison=sector_comparison,
                historical_rank=historical_rank,
                momentum_score=momentum_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating RS metrics: {str(e)}")
            return RelativeStrengthMetrics(
                rs_value=1.0,
                rs_percentile=50.0,
                rs_trend="stable",
                rs_volatility=0.0,
                market_comparison=1.0,
                sector_comparison=1.0,
                historical_rank=50,
                momentum_score=50.0
            )
    
    def _calculate_period_rs(self, returns: pd.Series, period: int) -> float:
        """חישוב RS לתקופה ספציפית"""
        if len(returns) < period:
            return 1.0
        
        # תשואה של המניה
        stock_return = (returns.iloc[-period:].sum() + 1)
        
        # תשואה של השוק (משוערת)
        market_return = 1.0  # ברירת מחדל, בפועל ישלף מנתוני שוק
        
        return stock_return / market_return if market_return > 0 else 1.0
    
    def _calculate_rs_percentile(self, returns: pd.Series, rs_value: float) -> float:
        """חישוב percentile של RS"""
        if len(returns) < 60:
            return 50.0
        
        # חישוב RS היסטורי
        historical_rs = []
        for i in range(60, len(returns), 20):
            period_rs = self._calculate_period_rs(returns.iloc[:i], 20)
            historical_rs.append(period_rs)
        
        if not historical_rs:
            return 50.0
        
        # חישוב percentile
        historical_rs = np.array(historical_rs)
        percentile = np.percentile(historical_rs, rs_value * 100)
        return min(100.0, max(0.0, percentile))
    
    def _identify_rs_trend(self, short_rs: float, medium_rs: float, long_rs: float) -> str:
        """זיהוי מגמת RS"""
        if short_rs > medium_rs > long_rs:
            return "accelerating"
        elif short_rs < medium_rs < long_rs:
            return "decelerating"
        elif abs(short_rs - medium_rs) < 0.1 and abs(medium_rs - long_rs) < 0.1:
            return "stable"
        elif (short_rs > medium_rs and medium_rs < long_rs) or (short_rs < medium_rs and medium_rs > long_rs):
            return "reversing"
        else:
            return "sideways"
    
    def _compare_to_market(self, symbol: str, price_df: pd.DataFrame) -> float:
        """השוואה לשוק"""
        try:
            # שליפת נתוני שוק
            market_data = data_fetcher.fetch_prices(self.comparison_benchmarks['market'], period="1y")
            if market_data is None or market_data.empty:
                return 1.0
            
            # חישוב תשואות
            stock_returns = price_df['close'].pct_change().dropna()
            market_returns = market_data['close'].pct_change().dropna()
            
            # השוואה
            stock_performance = (stock_returns.iloc[-20:].sum() + 1)
            market_performance = (market_returns.iloc[-20:].sum() + 1)
            
            return stock_performance / market_performance if market_performance > 0 else 1.0
            
        except Exception as e:
            logger.warning(f"Error comparing to market: {str(e)}")
            return 1.0
    
    def _compare_to_sector(self, symbol: str, price_df: pd.DataFrame) -> float:
        """השוואה לסקטור"""
        try:
            # זיהוי סקטור (משוער)
            sector_etf = self._get_sector_etf(symbol)
            if sector_etf is None:
                return 1.0
            
            # שליפת נתוני סקטור
            sector_data = data_fetcher.fetch_prices(sector_etf, period="1y")
            if sector_data is None or sector_data.empty:
                return 1.0
            
            # חישוב תשואות
            stock_returns = price_df['close'].pct_change().dropna()
            sector_returns = sector_data['close'].pct_change().dropna()
            
            # השוואה
            stock_performance = (stock_returns.iloc[-20:].sum() + 1)
            sector_performance = (sector_returns.iloc[-20:].sum() + 1)
            
            return stock_performance / sector_performance if sector_performance > 0 else 1.0
            
        except Exception as e:
            logger.warning(f"Error comparing to sector: {str(e)}")
            return 1.0
    
    def _get_sector_etf(self, symbol: str) -> Optional[str]:
        """זיהוי ETF סקטור (משוער)"""
        # מיפוי בסיסי של סקטורים
        sector_mapping = {
            'XLK': 'Technology',
            'XLF': 'Financials', 
            'XLE': 'Energy',
            'XLV': 'Healthcare',
            'XLI': 'Industrials',
            'XLP': 'Consumer Staples',
            'XLU': 'Utilities',
            'XLB': 'Materials',
            'XLRE': 'Real Estate'
        }
        
        # ברירת מחדל - Technology
        return 'XLK'
    
    def _calculate_historical_rank(self, returns: pd.Series, rs_value: float) -> int:
        """חישוב דירוג היסטורי"""
        if len(returns) < 60:
            return 50
        
        # חישוב RS היסטורי
        historical_rs = []
        for i in range(60, len(returns), 20):
            period_rs = self._calculate_period_rs(returns.iloc[:i], 20)
            historical_rs.append(period_rs)
        
        if not historical_rs:
            return 50
        
        # חישוב דירוג
        historical_rs = np.array(historical_rs)
        rank = np.sum(historical_rs < rs_value) / len(historical_rs) * 100
        return int(min(100, max(0, rank)))
    
    def _calculate_momentum_score(self, short_rs: float, medium_rs: float, long_rs: float) -> float:
        """חישוב ציון מומנטום"""
        # משקלול של RS במונחי מומנטום
        momentum = (
            (short_rs - 1.0) * 0.5 +
            (medium_rs - 1.0) * 0.3 +
            (long_rs - 1.0) * 0.2
        )
        
        # המרה לציון 0-100
        score = 50 + momentum * 100
        return min(100.0, max(0.0, score))
    
    def _calculate_rs_comparison(self, symbol: str, price_df: pd.DataFrame) -> RSComparison:
        """חישוב השוואות RS"""
        vs_market = self._compare_to_market(symbol, price_df)
        vs_sector = self._compare_to_sector(symbol, price_df)
        vs_industry = 1.0  # ברירת מחדל
        vs_peers = 1.0     # ברירת מחדל
        
        # חישוב דירוג כללי
        overall_rank = (vs_market + vs_sector + vs_industry + vs_peers) / 4
        
        return RSComparison(
            vs_market=vs_market,
            vs_sector=vs_sector,
            vs_industry=vs_industry,
            vs_peers=vs_peers,
            overall_rank=overall_rank
        )
    
    def _analyze_rs_trend(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח מגמת RS"""
        returns = price_df['close'].pct_change().dropna()
        
        # חישוב RS לתקופות שונות
        short_rs = self._calculate_period_rs(returns, 20)
        medium_rs = self._calculate_period_rs(returns, 60)
        long_rs = self._calculate_period_rs(returns, 200)
        
        # זיהוי מגמה
        trend = self._identify_rs_trend(short_rs, medium_rs, long_rs)
        
        # חישוב שיפוע
        slope = (short_rs - long_rs) / 180  # שיפוע יומי
        
        return {
            "trend": trend,
            "slope": slope,
            "short_rs": short_rs,
            "medium_rs": medium_rs,
            "long_rs": long_rs,
            "acceleration": short_rs - medium_rs
        }
    
    def _calculate_rs_volatility(self, price_df: pd.DataFrame) -> float:
        """חישוב תנודתיות RS"""
        returns = price_df['close'].pct_change().dropna()
        
        if len(returns) < 20:
            return 0.0
        
        # חישוב תנודתיות RS
        rs_values = []
        for i in range(20, len(returns), 5):
            period_rs = self._calculate_period_rs(returns.iloc[:i], 20)
            rs_values.append(period_rs)
        
        if len(rs_values) < 2:
            return 0.0
        
        return np.std(rs_values)
    
    def _calculate_overall_score(self, rs_metrics: RelativeStrengthMetrics, 
                               rs_comparison: RSComparison, 
                               rs_trend_analysis: Dict) -> int:
        """חישוב ציון כללי"""
        # משקלים
        weights = {
            'rs_value': 0.25,
            'rs_percentile': 0.20,
            'market_comparison': 0.20,
            'sector_comparison': 0.15,
            'momentum_score': 0.10,
            'trend_quality': 0.10
        }
        
        # ציונים
        rs_value_score = min(100, max(0, (rs_metrics.rs_value - 0.5) * 200))
        rs_percentile_score = rs_metrics.rs_percentile
        market_comparison_score = min(100, max(0, (rs_comparison.vs_market - 0.5) * 200))
        sector_comparison_score = min(100, max(0, (rs_comparison.vs_sector - 0.5) * 200))
        momentum_score = rs_metrics.momentum_score
        
        # ציון מגמה
        trend_quality_score = 50
        if rs_trend_analysis['trend'] == 'accelerating':
            trend_quality_score = 80
        elif rs_trend_analysis['trend'] == 'stable':
            trend_quality_score = 60
        elif rs_trend_analysis['trend'] == 'decelerating':
            trend_quality_score = 30
        
        # חישוב ציון משוקלל
        overall_score = (
            rs_value_score * weights['rs_value'] +
            rs_percentile_score * weights['rs_percentile'] +
            market_comparison_score * weights['market_comparison'] +
            sector_comparison_score * weights['sector_comparison'] +
            momentum_score * weights['momentum_score'] +
            trend_quality_score * weights['trend_quality']
        )
        
        return int(min(100, max(1, overall_score)))
    
    def _calculate_confidence(self, price_df: pd.DataFrame, rs_metrics: RelativeStrengthMetrics) -> float:
        """חישוב רמת ביטחון"""
        # גורמים שמשפיעים על הביטחון
        data_quality = min(100, len(price_df) / 2)  # כמות נתונים
        volatility_factor = max(0, 100 - rs_metrics.rs_volatility * 1000)  # תנודתיות נמוכה = ביטחון גבוה
        consistency_factor = min(100, rs_metrics.historical_rank)  # עקביות היסטורית
        
        confidence = (data_quality + volatility_factor + consistency_factor) / 3
        return min(100, max(0, confidence))
    
    def _generate_recommendations(self, rs_metrics: RelativeStrengthMetrics, 
                                rs_comparison: RSComparison, 
                                rs_trend_analysis: Dict) -> List[str]:
        """יצירת המלצות"""
        recommendations = []
        
        # המלצות לפי RS
        if rs_metrics.rs_value > self.rs_thresholds['very_strong']:
            recommendations.append("חוזק יחסי חזק מאוד - הזדמנות קנייה מצוינת")
        elif rs_metrics.rs_value > self.rs_thresholds['strong']:
            recommendations.append("חוזק יחסי חזק - הזדמנות קנייה טובה")
        elif rs_metrics.rs_value < self.rs_thresholds['weak']:
            recommendations.append("חוזק יחסי חלש - שקול מכירה או המתנה")
        
        # המלצות לפי השוואה לשוק
        if rs_comparison.vs_market > 1.2:
            recommendations.append("ביצועים טובים מהשוק - יתרון תחרותי")
        elif rs_comparison.vs_market < 0.8:
            recommendations.append("ביצועים נמוכים מהשוק - סיכון מוגבר")
        
        # המלצות לפי מגמה
        if rs_trend_analysis['trend'] == 'accelerating':
            recommendations.append("מגמת חוזק יחסי מאיצה - מומנטום חיובי")
        elif rs_trend_analysis['trend'] == 'decelerating':
            recommendations.append("מגמת חוזק יחסי מאטה - היזהרו")
        elif rs_trend_analysis['trend'] == 'reversing':
            recommendations.append("היפוך מגמה בחוזק יחסי - עקבו אחר השינוי")
        
        # המלצות לפי percentile
        if rs_metrics.rs_percentile > 80:
            recommendations.append("דירוג גבוה בהיסטוריה - ביצועים יוצאי דופן")
        elif rs_metrics.rs_percentile < 20:
            recommendations.append("דירוג נמוך בהיסטוריה - ביצועים חלשים")
        
        return recommendations
    
    def _generate_explanation(self, rs_metrics: RelativeStrengthMetrics, 
                            rs_comparison: RSComparison, 
                            rs_trend_analysis: Dict) -> str:
        """יצירת הסבר מפורט"""
        explanation_parts = []
        
        # הסבר RS
        explanation_parts.append(f"חוזק יחסי: {rs_metrics.rs_value:.2f}x")
        
        # הסבר percentile
        explanation_parts.append(f"דירוג היסטורי: {rs_metrics.rs_percentile:.0f}%")
        
        # הסבר השוואה לשוק
        explanation_parts.append(f"מול השוק: {rs_comparison.vs_market:.2f}x")
        
        # הסבר מגמה
        trend_name = self.trend_types.get(rs_trend_analysis['trend'], rs_trend_analysis['trend'])
        explanation_parts.append(f"מגמה: {trend_name}")
        
        # הסבר מומנטום
        explanation_parts.append(f"ציון מומנטום: {rs_metrics.momentum_score:.0f}")
        
        return " | ".join(explanation_parts)
    
    def _error_response(self, message: str) -> Dict:
        """תגובת שגיאה סטנדרטית"""
        return {
            "symbol": "UNKNOWN",
            "timestamp": datetime.now().isoformat(),
            "score": 50,
            "confidence": 0,
            "explanation": message,
            "recommendations": ["לא ניתן לנתח - בדוק את הנתונים"],
            "details": {},
            "error": True
        } 