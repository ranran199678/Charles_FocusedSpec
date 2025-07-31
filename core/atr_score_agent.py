"""
ATRScoreAgent - מנתח ATR מתקדם
===============================

סוכן מתקדם לניתוח ATR (Average True Range) עם יכולות:
- ניתוח ATR מתקדם
- השוואה היסטורית
- ניתוח מגמות ATR
- זיהוי דפוסי תנודתיות
- השוואה לסקטור ולשוק
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
class ATRMetrics:
    """מבנה נתונים למדדי ATR"""
    current_atr: float
    historical_atr: float
    atr_ratio: float
    atr_trend: str
    atr_percentile: float
    volatility_regime: str
    sector_comparison: float
    market_comparison: float
    extreme_events: List[Dict]

class ATRScoreAgent(BaseAgent):
    """
    סוכן מתקדם לניתוח ATR
    
    תכונות מתקדמות:
    - ניתוח ATR מתקדם
    - השוואה היסטורית
    - ניתוח מגמות ATR
    - זיהוי דפוסי תנודתיות
    - השוואה לסקטור ולשוק
    - אינדיקטורים טכניים מתקדמים
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.lookback = cfg.get("lookback", 14)
        self.scale = cfg.get("scale", 15)
        self.extreme_threshold = cfg.get("extreme_threshold", 2.0)  # סטיות תקן לאירועים קיצוניים
        self.regime_threshold = cfg.get("regime_threshold", 1.5)    # סף לשינוי משטר תנודתיות
        self.trend_period = cfg.get("trend_period", 20)             # תקופה לניתוח מגמה
        
        # משקלים לניתוח
        self.weights = {
            'current_atr': 0.25,
            'historical_comparison': 0.20,
            'atr_trend': 0.15,
            'sector_comparison': 0.15,
            'market_comparison': 0.10,
            'extreme_events': 0.10,
            'volatility_regime': 0.05
        }
        
        # משטרי תנודתיות
        self.volatility_regimes = {
            'low': 'תנודתיות נמוכה',
            'normal': 'תנודתיות רגילה',
            'high': 'תנודתיות גבוהה',
            'extreme': 'תנודתיות קיצונית'
        }
        
        self.log("ATRScoreAgent initialized with advanced configuration")

    def _calculate_true_range(self, price_df: pd.DataFrame) -> pd.Series:
        """חישוב True Range מתקדם"""
        high = price_df['high']
        low = price_df['low']
        close = price_df['close']
        
        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return true_range

    def _calculate_atr(self, price_df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """חישוב ATR מתקדם"""
        true_range = self._calculate_true_range(price_df)
        
        # ATR עם חלונות שונים
        atr_14 = true_range.rolling(window=14).mean()
        atr_21 = true_range.rolling(window=21).mean()
        atr_50 = true_range.rolling(window=50).mean()
        
        return atr_14, atr_21, atr_50

    def _analyze_atr_metrics(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח מדדי ATR מתקדמים"""
        if len(price_df) < 50:
            return self._get_default_atr_metrics()
        
        atr_14, atr_21, atr_50 = self._calculate_atr(price_df)
        
        # ATR נוכחי
        current_atr = atr_14.iloc[-1]
        current_atr_21 = atr_21.iloc[-1]
        current_atr_50 = atr_50.iloc[-1]
        
        # ATR היסטורי
        historical_atr = atr_50.mean()
        
        # יחס ATR
        atr_ratio = current_atr / historical_atr if historical_atr > 0 else 1.0
        atr_ratio_21 = current_atr_21 / historical_atr if historical_atr > 0 else 1.0
        
        # מגמת ATR (שינוי ב-20 ימים)
        if len(atr_14) >= 40:
            atr_20_days_ago = atr_14.iloc[-40:-20].mean()
            atr_trend = (current_atr - atr_20_days_ago) / atr_20_days_ago if atr_20_days_ago > 0 else 0
        else:
            atr_trend = 0
        
        # אחוזון ATR היסטורי
        atr_percentile = (atr_14 < current_atr).mean()
        
        # זיהוי משטר תנודתיות
        if atr_ratio > self.regime_threshold * 2:
            regime = 'extreme'
        elif atr_ratio > self.regime_threshold:
            regime = 'high'
        elif atr_ratio < 1 / self.regime_threshold:
            regime = 'low'
        else:
            regime = 'normal'
        
        return {
            'current_atr': current_atr,
            'current_atr_21': current_atr_21,
            'current_atr_50': current_atr_50,
            'historical_atr': historical_atr,
            'atr_ratio': atr_ratio,
            'atr_ratio_21': atr_ratio_21,
            'atr_trend': atr_trend,
            'atr_percentile': atr_percentile,
            'volatility_regime': regime
        }

    def _detect_extreme_atr_events(self, price_df: pd.DataFrame) -> List[Dict]:
        """זיהוי אירועי ATR קיצוניים"""
        extreme_events = []
        
        if len(price_df) < 30:
            return extreme_events
        
        atr_14, _, _ = self._calculate_atr(price_df)
        
        # חישוב סטטיסטיקות ATR
        atr_mean = atr_14.mean()
        atr_std = atr_14.std()
        
        # זיהוי ימים עם ATR קיצוני
        extreme_days = atr_14 > (atr_mean + self.extreme_threshold * atr_std)
        
        for i, is_extreme in enumerate(extreme_days):
            if is_extreme and i >= 14:
                event = {
                    'date': price_df.index[i] if hasattr(price_df.index[i], 'date') else i,
                    'atr_value': atr_14.iloc[i],
                    'severity': (atr_14.iloc[i] - atr_mean) / atr_std,
                    'price_change': price_df['close'].iloc[i] - price_df['close'].iloc[i-1] if i > 0 else 0
                }
                extreme_events.append(event)
        
        return extreme_events[-10:]  # רק 10 האירועים האחרונים

    def _analyze_atr_patterns(self, price_df: pd.DataFrame) -> Dict:
        """ניתוח דפוסי ATR"""
        if len(price_df) < 50:
            return {'patterns': [], 'pattern_score': 50}
        
        atr_14, atr_21, _ = self._calculate_atr(price_df)
        
        patterns = []
        pattern_score = 50
        
        # דפוס 1: ATR מתכווץ (Volatility Squeeze)
        recent_atr = atr_14.tail(10)
        atr_trend = (recent_atr.iloc[-1] - recent_atr.iloc[0]) / recent_atr.iloc[0]
        
        if atr_trend < -0.2:  # ירידה של יותר מ-20%
            patterns.append({
                'pattern': 'ATR מתכווץ',
                'signal': 'consolidation',
                'confidence': 'high'
            })
            pattern_score += 20
        
        # דפוס 2: ATR מתרחב (Volatility Expansion)
        if atr_trend > 0.3:  # עלייה של יותר מ-30%
            patterns.append({
                'pattern': 'ATR מתרחב',
                'signal': 'breakout',
                'confidence': 'medium'
            })
            pattern_score += 15
        
        # דפוס 3: ATR יציב
        if abs(atr_trend) < 0.1:  # שינוי של פחות מ-10%
            patterns.append({
                'pattern': 'ATR יציב',
                'signal': 'stable',
                'confidence': 'medium'
            })
            pattern_score += 10
        
        return {
            'patterns': patterns,
            'pattern_score': min(100, pattern_score)
        }

    def _get_sector_comparison(self, symbol: str, current_atr: float) -> float:
        """השוואה ל-ATR הסקטור (דמו)"""
        # כאן יהיה חיבור למסד נתונים של ATR סקטור
        # כרגע נחזיר ערך דמו
        sector_atrs = {
            'AAPL': 2.5,  # טכנולוגיה
            'MSFT': 2.3,
            'TSLA': 4.8,  # רכב
            'JPM': 2.1,   # בנקאות
            'JNJ': 1.8    # בריאות
        }
        
        sector_atr = sector_atrs.get(symbol, 2.5)
        return current_atr / sector_atr if sector_atr > 0 else 1.0

    def _get_market_comparison(self, current_atr: float) -> float:
        """השוואה ל-ATR השוק (דמו)"""
        # כאן יהיה חיבור למדד השוק (S&P 500)
        # כרגע נחזיר ערך דמו
        market_atr = 2.2  # ATR ממוצע של השוק
        return current_atr / market_atr if market_atr > 0 else 1.0

    def _get_default_atr_metrics(self) -> Dict:
        """החזרת מדדי ATR ברירת מחדל"""
        return {
            'current_atr': 2.5,
            'current_atr_21': 2.5,
            'current_atr_50': 2.5,
            'historical_atr': 2.5,
            'atr_ratio': 1.0,
            'atr_ratio_21': 1.0,
            'atr_trend': 0.0,
            'atr_percentile': 0.5,
            'volatility_regime': 'normal'
        }

    def _calculate_composite_score(self, metrics: Dict, extreme_events: List[Dict], 
                                 patterns: Dict, sector_comparison: float, 
                                 market_comparison: float) -> int:
        """חישוב ציון מורכב"""
        scores = {}
        
        # ציון ATR נוכחי (1-100)
        current_atr_score = min(100, max(1, int(metrics['current_atr'] * 20)))
        scores['current_atr'] = current_atr_score
        
        # ציון השוואה היסטורית
        if metrics['atr_ratio'] > 2.0:
            hist_score = 100
        elif metrics['atr_ratio'] > 1.5:
            hist_score = 80
        elif metrics['atr_ratio'] > 1.2:
            hist_score = 60
        elif metrics['atr_ratio'] < 0.5:
            hist_score = 20
        else:
            hist_score = 40
        scores['historical_comparison'] = hist_score
        
        # ציון מגמת ATR
        if metrics['atr_trend'] > 0.3:
            trend_score = 90
        elif metrics['atr_trend'] > 0.1:
            trend_score = 70
        elif metrics['atr_trend'] < -0.3:
            trend_score = 10
        elif metrics['atr_trend'] < -0.1:
            trend_score = 30
        else:
            trend_score = 50
        scores['atr_trend'] = trend_score
        
        # ציון השוואה לסקטור
        if sector_comparison > 1.5:
            sector_score = 90
        elif sector_comparison > 1.2:
            sector_score = 70
        elif sector_comparison < 0.7:
            sector_score = 20
        else:
            sector_score = 50
        scores['sector_comparison'] = sector_score
        
        # ציון השוואה לשוק
        if market_comparison > 1.5:
            market_score = 90
        elif market_comparison > 1.2:
            market_score = 70
        elif market_comparison < 0.7:
            market_score = 20
        else:
            market_score = 50
        scores['market_comparison'] = market_score
        
        # ציון אירועים קיצוניים
        if len(extreme_events) > 5:
            extreme_score = 100
        elif len(extreme_events) > 3:
            extreme_score = 80
        elif len(extreme_events) > 1:
            extreme_score = 60
        else:
            extreme_score = 30
        scores['extreme_events'] = extreme_score
        
        # ציון דפוסים
        scores['volatility_regime'] = patterns.get('pattern_score', 50)
        
        # חישוב ציון מורכב
        composite_score = sum(scores[component] * self.weights[component] 
                            for component in scores.keys())
        
        return int(composite_score)

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח ATR מתקדם
        
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
                    "explanation": "אין נתוני מחיר זמינים לניתוח ATR",
                    "details": {}
                }
            
            if len(price_df) < 30:
                return {
                    "score": 50,
                    "explanation": "אין מספיק נתונים לניתוח ATR מתקדם",
                    "details": {}
                }
            
            # ניתוח מדדי ATR
            metrics = self._analyze_atr_metrics(price_df)
            
            # זיהוי אירועים קיצוניים
            extreme_events = self._detect_extreme_atr_events(price_df)
            
            # ניתוח דפוסים
            patterns = self._analyze_atr_patterns(price_df)
            
            # השוואות
            sector_comparison = self._get_sector_comparison(symbol, metrics['current_atr'])
            market_comparison = self._get_market_comparison(metrics['current_atr'])
            
            # חישוב ציון מורכב
            score = self._calculate_composite_score(
                metrics, extreme_events, patterns, 
                sector_comparison, market_comparison
            )
            
            # יצירת הסבר
            explanation_parts = []
            explanation_parts.append(f"ATR: {metrics['current_atr']:.2f}")
            explanation_parts.append(f"יחס להיסטורי: {metrics['atr_ratio']:.2f}x")
            explanation_parts.append(f"משטר: {self.volatility_regimes[metrics['volatility_regime']]}")
            
            if patterns.get('patterns'):
                pattern_names = [p['pattern'] for p in patterns['patterns']]
                explanation_parts.append(f"דפוסים: {', '.join(pattern_names)}")
            
            if len(extreme_events) > 0:
                explanation_parts.append(f"אירועים קיצוניים: {len(extreme_events)}")
            
            explanation = " | ".join(explanation_parts)
            
            # יצירת פרטים מפורטים
            details = {
                'symbol': symbol,
                'atr_metrics': metrics,
                'extreme_events': extreme_events,
                'patterns': patterns,
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
            self.log(f"שגיאה בניתוח ATR עבור {symbol}: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח ATR: {str(e)}",
                "details": {}
            }
