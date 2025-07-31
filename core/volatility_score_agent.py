"""
VolatilityScoreAgent - מנתח תנודתיות מתקדם
===========================================

סוכן מתקדם לניתוח תנודתיות עם יכולות:
- ניתוח תנודתיות היסטורי
- השוואה לסקטור ולשוק
- זיהוי דפוסים תנודתיות
- ניתוח תנודתיות לפי זמן
- זיהוי אירועי תנודתיות חריגים
- ניתוח קורלציה עם נפח
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
class VolatilityMetrics:
    """מבנה נתונים למדדי תנודתיות"""
    current_volatility: float
    historical_volatility: float
    volatility_ratio: float
    volatility_trend: str
    volatility_percentile: float
    sector_comparison: float
    market_comparison: float
    volatility_regime: str
    extreme_events: List[Dict]
    volume_correlation: float

class VolatilityScoreAgent(BaseAgent):
    """
    סוכן מתקדם לניתוח תנודתיות
    
    תכונות מתקדמות:
    - ניתוח תנודתיות היסטורי
    - השוואה לסקטור ולשוק
    - זיהוי דפוסים תנודתיות
    - ניתוח תנודתיות לפי זמן
    - זיהוי אירועי תנודתיות חריגים
    - ניתוח קורלציה עם נפח
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.short_window = cfg.get("short_window", 21)  # חודש
        self.long_window = cfg.get("long_window", 252)   # שנה
        self.extreme_threshold = cfg.get("extreme_threshold", 2.0)  # סטיות תקן לאירועים קיצוניים
        self.regime_threshold = cfg.get("regime_threshold", 1.5)    # סף לשינוי משטר תנודתיות
        
        # משקלים לניתוח
        self.weights = {
            'current_volatility': 0.25,
            'historical_comparison': 0.20,
            'volatility_trend': 0.15,
            'sector_comparison': 0.15,
            'market_comparison': 0.10,
            'extreme_events': 0.10,
            'volume_correlation': 0.05
        }
        
        # משטרי תנודתיות
        self.volatility_regimes = {
            'low': 'תנודתיות נמוכה',
            'normal': 'תנודתיות רגילה',
            'high': 'תנודתיות גבוהה',
            'extreme': 'תנודתיות קיצונית'
        }
        
        self.log("VolatilityScoreAgent initialized with advanced configuration")

    def _calculate_returns(self, price_df: pd.DataFrame) -> pd.Series:
        """חישוב תשואות יומיות"""
        if 'close' in price_df.columns:
            return price_df['close'].pct_change().dropna()
        elif 'Close' in price_df.columns:
            return price_df['Close'].pct_change().dropna()
        else:
            raise ValueError("No 'close' or 'Close' column found in price data")

    def _calculate_volatility_metrics(self, returns: pd.Series) -> Dict:
        """חישוב מדדי תנודתיות מתקדמים"""
        if len(returns) < self.long_window:
            return self._get_default_metrics()
        
        # תנודתיות נוכחית (חודש)
        current_vol = returns[-self.short_window:].std() * np.sqrt(252)
        
        # תנודתיות היסטורית (שנה)
        historical_vol = returns[-self.long_window:].std() * np.sqrt(252)
        
        # יחס תנודתיות
        volatility_ratio = current_vol / historical_vol if historical_vol > 0 else 1.0
        
        # מגמת תנודתיות (שינוי ב-30 ימים)
        if len(returns) >= 50:
            vol_30_days_ago = returns[-50:-20].std() * np.sqrt(252)
            vol_trend = (current_vol - vol_30_days_ago) / vol_30_days_ago if vol_30_days_ago > 0 else 0
        else:
            vol_trend = 0
        
        # אחוזון תנודתיות היסטורי
        rolling_vol = returns.rolling(window=21).std() * np.sqrt(252)
        volatility_percentile = (rolling_vol < current_vol).mean()
        
        # זיהוי משטר תנודתיות
        if volatility_ratio > self.regime_threshold * 2:
            regime = 'extreme'
        elif volatility_ratio > self.regime_threshold:
            regime = 'high'
        elif volatility_ratio < 1 / self.regime_threshold:
            regime = 'low'
        else:
            regime = 'normal'
        
        return {
            'current_volatility': current_vol,
            'historical_volatility': historical_vol,
            'volatility_ratio': volatility_ratio,
            'volatility_trend': vol_trend,
            'volatility_percentile': volatility_percentile,
            'volatility_regime': regime
        }

    def _detect_extreme_events(self, returns: pd.Series) -> List[Dict]:
        """זיהוי אירועי תנודתיות קיצוניים"""
        extreme_events = []
        
        if len(returns) < 30:
            return extreme_events
        
        # חישוב תנודתיות נעה
        rolling_vol = returns.rolling(window=21).std()
        vol_mean = rolling_vol.mean()
        vol_std = rolling_vol.std()
        
        # זיהוי ימים עם תנודתיות קיצונית
        extreme_days = rolling_vol > (vol_mean + self.extreme_threshold * vol_std)
        
        for i, is_extreme in enumerate(extreme_days):
            if is_extreme and i >= 21:
                event = {
                    'date': returns.index[i] if hasattr(returns.index[i], 'date') else i,
                    'volatility': rolling_vol.iloc[i],
                    'return': returns.iloc[i],
                    'severity': (rolling_vol.iloc[i] - vol_mean) / vol_std
                }
                extreme_events.append(event)
        
        return extreme_events[-10:]  # רק 10 האירועים האחרונים

    def _analyze_volume_correlation(self, price_df: pd.DataFrame, returns: pd.Series) -> float:
        """ניתוח קורלציה בין תנודתיות לנפח"""
        if 'volume' not in price_df.columns and 'Volume' not in price_df.columns:
            return 0.0
        
        volume_col = 'volume' if 'volume' in price_df.columns else 'Volume'
        volume = price_df[volume_col]
        
        if len(volume) != len(returns):
            return 0.0
        
        # חישוב תנודתיות נעה
        rolling_vol = returns.rolling(window=21).std()
        
        # קורלציה בין תנודתיות לנפח
        correlation = rolling_vol.corr(volume)
        return correlation if not np.isnan(correlation) else 0.0

    def _get_sector_comparison(self, symbol: str, current_vol: float) -> float:
        """השוואה לתנודתיות הסקטור (דמו)"""
        # כאן יהיה חיבור למסד נתונים של תנודתיות סקטור
        # כרגע נחזיר ערך דמו
        sector_vols = {
            'AAPL': 0.25,  # טכנולוגיה
            'MSFT': 0.24,
            'TSLA': 0.45,  # רכב
            'JPM': 0.22,   # בנקאות
            'JNJ': 0.18    # בריאות
        }
        
        sector_vol = sector_vols.get(symbol, 0.25)
        return current_vol / sector_vol if sector_vol > 0 else 1.0

    def _get_market_comparison(self, current_vol: float) -> float:
        """השוואה לתנודתיות השוק (דמו)"""
        # כאן יהיה חיבור למדד השוק (S&P 500)
        # כרגע נחזיר ערך דמו
        market_vol = 0.20  # תנודתיות ממוצעת של השוק
        return current_vol / market_vol if market_vol > 0 else 1.0

    def _get_default_metrics(self) -> Dict:
        """החזרת מדדים ברירת מחדל"""
        return {
            'current_volatility': 0.25,
            'historical_volatility': 0.25,
            'volatility_ratio': 1.0,
            'volatility_trend': 0.0,
            'volatility_percentile': 0.5,
            'volatility_regime': 'normal'
        }

    def _calculate_composite_score(self, metrics: Dict, extreme_events: List[Dict], 
                                 volume_correlation: float, sector_comparison: float, 
                                 market_comparison: float) -> int:
        """חישוב ציון מורכב"""
        scores = {}
        
        # ציון תנודתיות נוכחית (1-100)
        current_vol_score = min(100, max(1, int(metrics['current_volatility'] * 400)))
        scores['current_volatility'] = current_vol_score
        
        # ציון השוואה היסטורית
        if metrics['volatility_ratio'] > 2.0:
            hist_score = 100
        elif metrics['volatility_ratio'] > 1.5:
            hist_score = 80
        elif metrics['volatility_ratio'] > 1.2:
            hist_score = 60
        elif metrics['volatility_ratio'] < 0.5:
            hist_score = 20
        else:
            hist_score = 40
        scores['historical_comparison'] = hist_score
        
        # ציון מגמת תנודתיות
        if metrics['volatility_trend'] > 0.3:
            trend_score = 90
        elif metrics['volatility_trend'] > 0.1:
            trend_score = 70
        elif metrics['volatility_trend'] < -0.3:
            trend_score = 10
        elif metrics['volatility_trend'] < -0.1:
            trend_score = 30
        else:
            trend_score = 50
        scores['volatility_trend'] = trend_score
        
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
        
        # ציון קורלציה עם נפח
        volume_score = 50 + int(volume_correlation * 50)
        volume_score = max(1, min(100, volume_score))
        scores['volume_correlation'] = volume_score
        
        # חישוב ציון מורכב
        composite_score = sum(scores[component] * self.weights[component] 
                            for component in scores.keys())
        
        return int(composite_score)

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח תנודתיות מתקדם
        
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
                    "explanation": "אין נתוני מחיר זמינים לניתוח תנודתיות",
                    "details": {}
                }
            
            # חישוב תשואות
            returns = self._calculate_returns(price_df)
            
            if len(returns) < 30:
                return {
                    "score": 50,
                    "explanation": "אין מספיק נתונים לניתוח תנודתיות מתקדם",
                    "details": {}
                }
            
            # חישוב מדדי תנודתיות
            metrics = self._calculate_volatility_metrics(returns)
            
            # זיהוי אירועים קיצוניים
            extreme_events = self._detect_extreme_events(returns)
            
            # ניתוח קורלציה עם נפח
            volume_correlation = self._analyze_volume_correlation(price_df, returns)
            
            # השוואות
            sector_comparison = self._get_sector_comparison(symbol, metrics['current_volatility'])
            market_comparison = self._get_market_comparison(metrics['current_volatility'])
            
            # חישוב ציון מורכב
            score = self._calculate_composite_score(
                metrics, extreme_events, volume_correlation, 
                sector_comparison, market_comparison
            )
            
            # יצירת הסבר
            explanation_parts = []
            explanation_parts.append(f"תנודתיות נוכחית: {metrics['current_volatility']:.2%}")
            explanation_parts.append(f"יחס להיסטורי: {metrics['volatility_ratio']:.2f}x")
            explanation_parts.append(f"משטר: {self.volatility_regimes[metrics['volatility_regime']]}")
            
            if len(extreme_events) > 0:
                explanation_parts.append(f"אירועים קיצוניים: {len(extreme_events)}")
            
            if abs(volume_correlation) > 0.3:
                explanation_parts.append(f"קורלציה עם נפח: {volume_correlation:.2f}")
            
            explanation = " | ".join(explanation_parts)
            
            # יצירת פרטים מפורטים
            details = {
                'symbol': symbol,
                'volatility_metrics': metrics,
                'extreme_events': extreme_events,
                'volume_correlation': volume_correlation,
                'sector_comparison': sector_comparison,
                'market_comparison': market_comparison,
                'analysis_date': datetime.now().isoformat(),
                'data_points': len(returns)
            }
            
            return {
                "score": score,
                "explanation": explanation,
                "details": details
            }
            
        except Exception as e:
            self.log(f"שגיאה בניתוח תנודתיות עבור {symbol}: {e}")
            return {
                "score": 50,
                "explanation": f"שגיאה בניתוח תנודתיות: {str(e)}",
                "details": {}
            }
