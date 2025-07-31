"""
MidtermMomentumAgent - מנתח מומנטום מתקדם
==========================================

סוכן מתקדם לניתוח מומנטום בינוני עם יכולות:
- ניתוח מומנטום מתקדם
- ניתוח רב-ממדי
- זיהוי דפוסי מומנטום
- השוואה היסטורית
- ניתוח מגמות
- אינדיקטורים טכניים מתקדמים
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.base.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

@dataclass
class MomentumMetrics:
    """מבנה נתונים למדדי מומנטום"""
    short_momentum: float
    long_momentum: float
    momentum_ratio: float
    momentum_trend: str
    momentum_strength: float
    historical_percentile: float
    sector_comparison: float
    market_comparison: float

class MidtermMomentumAgent(BaseAgent):
    """
    סוכן מתקדם לניתוח מומנטום בינוני
    
    תכונות מתקדמות:
    - ניתוח מומנטום מתקדם
    - ניתוח רב-ממדי
    - זיהוי דפוסי מומנטום
    - השוואה היסטורית
    - ניתוח מגמות
    - אינדיקטורים טכניים מתקדמים
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.short_period = cfg.get("short_period", 21)  # חודש
        self.long_period = cfg.get("long_period", 63)    # 3 חודשים
        self.weight_short = cfg.get("weight_short", 0.5)
        
        # פרמטרים מתקדמים
        self.momentum_threshold = cfg.get("momentum_threshold", 0.05)  # 5% לשינוי משמעותי
        self.trend_period = cfg.get("trend_period", 10)                # תקופה לניתוח מגמה
        self.acceleration_period = cfg.get("acceleration_period", 5)   # תקופה לניתוח האצה
        
        # משקלים לניתוח
        self.weights = {
            'short_momentum': 0.30,
            'long_momentum': 0.25,
            'momentum_trend': 0.20,
            'momentum_strength': 0.15,
            'historical_comparison': 0.10
        }
        
        # סוגי מומנטום
        self.momentum_types = {
            'strong_positive': 'מומנטום חיובי חזק',
            'positive': 'מומנטום חיובי',
            'weak_positive': 'מומנטום חיובי חלש',
            'neutral': 'מומנטום ניטרלי',
            'weak_negative': 'מומנטום שלילי חלש',
            'negative': 'מומנטום שלילי',
            'strong_negative': 'מומנטום שלילי חזק'
        }
        
        self.log("MidtermMomentumAgent initialized with advanced configuration")

    def _calculate_momentum_indicators(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """חישוב אינדיקטורי מומנטום מתקדמים"""
        df = price_df.copy()
        
        # חישוב תשואות
        df['returns'] = df['close'].pct_change()
        df['returns_ma'] = df['returns'].rolling(window=5).mean()
        
        # מומנטום קצר טווח
        df['short_momentum'] = (df['close'] - df['close'].shift(self.short_period)) / df['close'].shift(self.short_period) * 100
        df['short_momentum_ma'] = df['short_momentum'].rolling(window=5).mean()
        
        # מומנטום ארוך טווח
        df['long_momentum'] = (df['close'] - df['close'].shift(self.long_period)) / df['close'].shift(self.long_period) * 100
        df['long_momentum_ma'] = df['long_momentum'].rolling(window=10).mean()
        
        # יחס מומנטום
        df['momentum_ratio'] = df['short_momentum'] / df['long_momentum']
        
        # האצת מומנטום
        df['momentum_acceleration'] = df['short_momentum'].diff()
        df['momentum_acceleration_ma'] = df['momentum_acceleration'].rolling(window=self.acceleration_period).mean()
        
        # אחוזון היסטורי
        df['momentum_percentile'] = df['short_momentum'].rolling(window=50).apply(
            lambda x: (x < x.iloc[-1]).mean()
        )
        
        return df

    def _analyze_momentum_metrics(self, df: pd.DataFrame) -> Dict:
        """ניתוח מדדי מומנטום מתקדמים"""
        if len(df) < self.long_period:
            return self._get_default_momentum_metrics()
        
        # ערכים נוכחיים
        current_short_momentum = df['short_momentum'].iloc[-1]
        current_long_momentum = df['long_momentum'].iloc[-1]
        current_momentum_ratio = df['momentum_ratio'].iloc[-1]
        current_acceleration = df['momentum_acceleration'].iloc[-1]
        
        # ניתוח מגמה
        recent_short_momentum = df['short_momentum'].tail(self.trend_period)
        momentum_trend = (recent_short_momentum.iloc[-1] - recent_short_momentum.iloc[0]) / abs(recent_short_momentum.iloc[0]) if abs(recent_short_momentum.iloc[0]) > 0 else 0
        
        # חישוב עוצמת מומנטום
        momentum_strength = abs(current_short_momentum) / df['short_momentum'].std() if df['short_momentum'].std() > 0 else 0
        
        # זיהוי סוג מומנטום
        if current_short_momentum > 10 and momentum_trend > 0.2:
            momentum_type = 'strong_positive'
        elif current_short_momentum > 5 and momentum_trend > 0.1:
            momentum_type = 'positive'
        elif current_short_momentum > 2:
            momentum_type = 'weak_positive'
        elif current_short_momentum < -10 and momentum_trend < -0.2:
            momentum_type = 'strong_negative'
        elif current_short_momentum < -5 and momentum_trend < -0.1:
            momentum_type = 'negative'
        elif current_short_momentum < -2:
            momentum_type = 'weak_negative'
        else:
            momentum_type = 'neutral'
        
        # אחוזון היסטורי
        historical_percentile = df['momentum_percentile'].iloc[-1]
        
        return {
            'short_momentum': current_short_momentum,
            'long_momentum': current_long_momentum,
            'momentum_ratio': current_momentum_ratio,
            'momentum_acceleration': current_acceleration,
            'momentum_trend': momentum_trend,
            'momentum_strength': momentum_strength,
            'momentum_type': momentum_type,
            'historical_percentile': historical_percentile
        }

    def _detect_momentum_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """זיהוי דפוסי מומנטום"""
        patterns = []
        
        if len(df) < 30:
            return patterns
        
        # דפוס 1: האצת מומנטום
        recent_acceleration = df['momentum_acceleration'].tail(5)
        if recent_acceleration.mean() > 0.5:
            patterns.append({
                'pattern': 'האצת מומנטום',
                'signal': 'bullish',
                'confidence': 'high'
            })
        elif recent_acceleration.mean() < -0.5:
            patterns.append({
                'pattern': 'האטת מומנטום',
                'signal': 'bearish',
                'confidence': 'high'
            })
        
        # דפוס 2: דיברגנציה בין מומנטום קצר וארוך
        recent_ratio = df['momentum_ratio'].tail(10)
        if recent_ratio.iloc[-1] > 1.5 and recent_ratio.iloc[0] < 1.0:
            patterns.append({
                'pattern': 'התחזקות מומנטום קצר',
                'signal': 'bullish',
                'confidence': 'medium'
            })
        elif recent_ratio.iloc[-1] < 0.7 and recent_ratio.iloc[0] > 1.0:
            patterns.append({
                'pattern': 'החלשת מומנטום קצר',
                'signal': 'bearish',
                'confidence': 'medium'
            })
        
        # דפוס 3: מומנטום יציב
        recent_momentum = df['short_momentum'].tail(10)
        momentum_std = recent_momentum.std()
        if momentum_std < 2.0:
            patterns.append({
                'pattern': 'מומנטום יציב',
                'signal': 'neutral',
                'confidence': 'medium'
            })
        
        return patterns

    def _analyze_momentum_strength(self, df: pd.DataFrame) -> Dict:
        """ניתוח עוצמת מומנטום"""
        if len(df) < 20:
            return {'strength_score': 50, 'strength_quality': 'neutral'}
        
        # ניתוח עקביות המומנטום
        recent_momentum = df['short_momentum'].tail(10)
        positive_days = (recent_momentum > 0).sum()
        negative_days = (recent_momentum < 0).sum()
        
        # חישוב עוצמת מומנטום
        if positive_days > negative_days:
            strength_score = (positive_days / 10) * 100
            strength_quality = 'positive'
        elif negative_days > positive_days:
            strength_score = (negative_days / 10) * 100
            strength_quality = 'negative'
        else:
            strength_score = 50
            strength_quality = 'neutral'
        
        # ניתוח יציבות המומנטום
        momentum_std = recent_momentum.std()
        stability_score = max(0, 100 - (momentum_std * 10))
        
        return {
            'strength_score': strength_score,
            'strength_quality': strength_quality,
            'stability_score': stability_score,
            'positive_days': positive_days,
            'negative_days': negative_days
        }

    def _get_sector_comparison(self, symbol: str, current_momentum: float) -> float:
        """השוואה למומנטום הסקטור (דמו)"""
        # כאן יהיה חיבור למסד נתונים של מומנטום סקטור
        # כרגע נחזיר ערך דמו
        sector_momentums = {
            'AAPL': 5.2,  # טכנולוגיה
            'MSFT': 4.8,
            'TSLA': 8.5,  # רכב
            'JPM': 2.1,   # בנקאות
            'JNJ': 1.8    # בריאות
        }
        
        sector_momentum = sector_momentums.get(symbol, 4.0)
        return current_momentum / sector_momentum if sector_momentum > 0 else 1.0

    def _get_market_comparison(self, current_momentum: float) -> float:
        """השוואה למומנטום השוק (דמו)"""
        # כאן יהיה חיבור למדד השוק (S&P 500)
        # כרגע נחזיר ערך דמו
        market_momentum = 3.5  # מומנטום ממוצע של השוק
        return current_momentum / market_momentum if market_momentum > 0 else 1.0

    def _get_default_momentum_metrics(self) -> Dict:
        """החזרת מדדי מומנטום ברירת מחדל"""
        return {
            'short_momentum': 0.0,
            'long_momentum': 0.0,
            'momentum_ratio': 1.0,
            'momentum_acceleration': 0.0,
            'momentum_trend': 0.0,
            'momentum_strength': 0.0,
            'momentum_type': 'neutral',
            'historical_percentile': 50.0
        }

    def _calculate_composite_score(self, momentum_metrics: Dict, patterns: List[Dict], 
                                 strength_analysis: Dict, sector_comparison: float, 
                                 market_comparison: float) -> int:
        """חישוב ציון מורכב"""
        scores = {}
        
        # ציון מומנטום קצר
        short_momentum = momentum_metrics['short_momentum']
        if short_momentum > 10:
            short_score = 90
        elif short_momentum > 5:
            short_score = 75
        elif short_momentum > 2:
            short_score = 60
        elif short_momentum > -2:
            short_score = 50
        elif short_momentum > -5:
            short_score = 40
        elif short_momentum > -10:
            short_score = 25
        else:
            short_score = 10
        scores['short_momentum'] = short_score
        
        # ציון מומנטום ארוך
        long_momentum = momentum_metrics['long_momentum']
        if long_momentum > 15:
            long_score = 90
        elif long_momentum > 8:
            long_score = 75
        elif long_momentum > 3:
            long_score = 60
        elif long_momentum > -3:
            long_score = 50
        elif long_momentum > -8:
            long_score = 40
        elif long_momentum > -15:
            long_score = 25
        else:
            long_score = 10
        scores['long_momentum'] = long_score
        
        # ציון מגמת מומנטום
        momentum_trend = momentum_metrics['momentum_trend']
        if momentum_trend > 0.3:
            trend_score = 90
        elif momentum_trend > 0.1:
            trend_score = 70
        elif momentum_trend > -0.1:
            trend_score = 50
        elif momentum_trend > -0.3:
            trend_score = 30
        else:
            trend_score = 10
        scores['momentum_trend'] = trend_score
        
        # ציון עוצמת מומנטום
        strength_score = strength_analysis.get('strength_score', 50)
        scores['momentum_strength'] = strength_score
        
        # ציון השוואה היסטורית
        historical_percentile = momentum_metrics['historical_percentile']
        scores['historical_comparison'] = historical_percentile
        
        # חישוב ציון מורכב
        composite_score = sum(scores[component] * self.weights[component] 
                            for component in scores.keys())
        
        return int(composite_score)

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח מומנטום מתקדם
        
        Args:
            symbol: סימול המניה
            price_df: DataFrame עם נתוני מחיר
            
        Returns:
            Dict עם score, explanation, details
        """
        try:
            if price_df is None or price_df.empty:
                return {
                    "score": 50,
                    "explanation": "אין נתוני מחיר זמינים לניתוח מומנטום",
                    "details": {}
                }
            
            if len(price_df) < self.long_period:
                return {
                    "score": 50,
                    "explanation": "אין מספיק נתונים לניתוח מומנטום מתקדם",
                    "details": {}
                }
            
            # חישוב אינדיקטורי מומנטום
            df = self._calculate_momentum_indicators(price_df)
            
            # ניתוח מדדי מומנטום
            momentum_metrics = self._analyze_momentum_metrics(df)
            
            # זיהוי דפוסים
            patterns = self._detect_momentum_patterns(df)
            
            # ניתוח עוצמה
            strength_analysis = self._analyze_momentum_strength(df)
            
            # השוואות
            sector_comparison = self._get_sector_comparison(symbol, momentum_metrics['short_momentum'])
            market_comparison = self._get_market_comparison(momentum_metrics['short_momentum'])
            
            # חישוב ציון מורכב
            score = self._calculate_composite_score(
                momentum_metrics, patterns, strength_analysis,
                sector_comparison, market_comparison
            )
            
            # יצירת הסבר
            explanation_parts = []
            momentum_name = self.momentum_types.get(momentum_metrics['momentum_type'], momentum_metrics['momentum_type'])
            explanation_parts.append(f"מומנטום: {momentum_name}")
            explanation_parts.append(f"קצר: {momentum_metrics['short_momentum']:.1f}%")
            explanation_parts.append(f"ארוך: {momentum_metrics['long_momentum']:.1f}%")
            
            if patterns:
                pattern_names = [p['pattern'] for p in patterns]
                explanation_parts.append(f"דפוסים: {', '.join(pattern_names)}")
            
            if strength_analysis.get('stability_score', 0) > 70:
                explanation_parts.append("מומנטום יציב")
            
            explanation = " | ".join(explanation_parts)
            
            # יצירת פרטים מפורטים
            details = {
                'symbol': symbol,
                'momentum_metrics': momentum_metrics,
                'patterns': patterns,
                'strength_analysis': strength_analysis,
                'sector_comparison': sector_comparison,
                'market_comparison': market_comparison,
                'analysis_date': datetime.now().isoformat(),
                'data_points': len(price_df)
            }
            
            return {
                "score": score,
                "explanation": explanation,
                "details": details
            }
            
        except Exception as e:
            self.log(f"שגיאה בניתוח מומנטום עבור {symbol}: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח מומנטום: {str(e)}",
                "details": {}
            }
