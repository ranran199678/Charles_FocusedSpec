"""
MACDMomentumDetector - מנתח MACD מתקדם
=======================================

סוכן מתקדם לניתוח MACD (Moving Average Convergence Divergence) עם יכולות:
- ניתוח MACD מתקדם
- זיהוי דיברגנציות
- ניתוח מומנטום רב-ממדי
- זיהוי סיגנלים מתקדמים
- ניתוח היסטורי
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
class MACDMetrics:
    """מבנה נתונים למדדי MACD"""
    macd_line: float
    signal_line: float
    histogram: float
    momentum_strength: float
    divergence_detected: bool
    signal_type: str
    trend_strength: float
    historical_percentile: float

class MACDMomentumDetector(BaseAgent):
    """
    סוכן מתקדם לניתוח MACD
    
    תכונות מתקדמות:
    - ניתוח MACD מתקדם
    - זיהוי דיברגנציות
    - ניתוח מומנטום רב-ממדי
    - זיהוי סיגנלים מתקדמים
    - ניתוח היסטורי
    - אינדיקטורים טכניים מתקדמים
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        
        # פרמטרים בסיסיים
        self.fast = cfg.get("fast", 12)
        self.slow = cfg.get("slow", 26)
        self.signal = cfg.get("signal", 9)
        self.freshness_days = cfg.get("freshness_days", 5)
        
        # פרמטרים מתקדמים
        self.divergence_threshold = cfg.get("divergence_threshold", 0.1)
        self.momentum_threshold = cfg.get("momentum_threshold", 0.05)
        self.trend_period = cfg.get("trend_period", 20)
        
        # משקלים לניתוח
        self.weights = {
            'histogram_value': 0.30,
            'momentum_trend': 0.25,
            'signal_strength': 0.20,
            'divergence_analysis': 0.15,
            'historical_comparison': 0.10
        }
        
        # סוגי סיגנלים
        self.signal_types = {
            'strong_bullish': 'סיגנל בולי חזק',
            'bullish': 'סיגנל בולי',
            'weak_bullish': 'סיגנל בולי חלש',
            'neutral': 'סיגנל ניטרלי',
            'weak_bearish': 'סיגנל בריש חלש',
            'bearish': 'סיגנל בריש',
            'strong_bearish': 'סיגנל בריש חזק'
        }
        
        self.log("MACDMomentumDetector initialized with advanced configuration")

    def _calculate_macd_indicators(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """חישוב אינדיקטורי MACD מתקדמים"""
        df = price_df.copy()
        
        # MACD בסיסי
        df["ema_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()
        df["macd_line"] = df["ema_fast"] - df["ema_slow"]
        df["macd_signal"] = df["macd_line"].ewm(span=self.signal, adjust=False).mean()
        df["macd_histogram"] = df["macd_line"] - df["macd_signal"]
        
        # MACD מתקדם
        df["macd_histogram_ma"] = df["macd_histogram"].rolling(window=9).mean()
        df["macd_histogram_std"] = df["macd_histogram"].rolling(window=20).std()
        
        # מומנטום MACD
        df["macd_momentum"] = df["macd_histogram"].diff()
        df["macd_momentum_ma"] = df["macd_momentum"].rolling(window=5).mean()
        
        # אחוזון היסטורי
        df["histogram_percentile"] = df["macd_histogram"].rolling(window=50).apply(
            lambda x: (x < x.iloc[-1]).mean()
        )
        
        return df

    def _analyze_macd_momentum(self, df: pd.DataFrame) -> Dict:
        """ניתוח מומנטום MACD מתקדם"""
        if len(df) < 50:
            return self._get_default_macd_metrics()
        
        # ערכים נוכחיים
        current_histogram = df["macd_histogram"].iloc[-1]
        current_macd = df["macd_line"].iloc[-1]
        current_signal = df["macd_signal"].iloc[-1]
        current_momentum = df["macd_momentum"].iloc[-1]
        
        # ניתוח מגמה
        recent_histogram = df["macd_histogram"].tail(self.trend_period)
        histogram_trend = (recent_histogram.iloc[-1] - recent_histogram.iloc[0]) / abs(recent_histogram.iloc[0]) if abs(recent_histogram.iloc[0]) > 0 else 0
        
        # חישוב עוצמת מומנטום
        momentum_strength = abs(current_momentum) / df["macd_histogram_std"].iloc[-1] if df["macd_histogram_std"].iloc[-1] > 0 else 0
        
        # זיהוי סיגנל
        if current_histogram > 0 and histogram_trend > 0.1:
            if momentum_strength > 2.0:
                signal_type = 'strong_bullish'
            elif momentum_strength > 1.0:
                signal_type = 'bullish'
            else:
                signal_type = 'weak_bullish'
        elif current_histogram < 0 and histogram_trend < -0.1:
            if momentum_strength > 2.0:
                signal_type = 'strong_bearish'
            elif momentum_strength > 1.0:
                signal_type = 'bearish'
            else:
                signal_type = 'weak_bearish'
        else:
            signal_type = 'neutral'
        
        # אחוזון היסטורי
        historical_percentile = df["histogram_percentile"].iloc[-1]
        
        return {
            'macd_line': current_macd,
            'signal_line': current_signal,
            'histogram': current_histogram,
            'momentum': current_momentum,
            'momentum_strength': momentum_strength,
            'histogram_trend': histogram_trend,
            'signal_type': signal_type,
            'historical_percentile': historical_percentile
        }

    def _detect_divergences(self, df: pd.DataFrame) -> List[Dict]:
        """זיהוי דיברגנציות MACD"""
        divergences = []
        
        if len(df) < 30:
            return divergences
        
        # חישוב נקודות קיצון במחיר וב-MACD
        price_highs = df['close'].rolling(window=5, center=True).apply(lambda x: x.iloc[2] == x.max())
        price_lows = df['close'].rolling(window=5, center=True).apply(lambda x: x.iloc[2] == x.min())
        macd_highs = df['macd_line'].rolling(window=5, center=True).apply(lambda x: x.iloc[2] == x.max())
        macd_lows = df['macd_line'].rolling(window=5, center=True).apply(lambda x: x.iloc[2] == x.min())
        
        # זיהוי דיברגנציה בולית (מחיר יורד, MACD עולה)
        for i in range(20, len(df)):
            if price_lows.iloc[i] and macd_lows.iloc[i-10:i].any():
                # בדיקה אם המחיר ירד אבל MACD עלה
                price_change = df['close'].iloc[i] - df['close'].iloc[i-10]
                macd_change = df['macd_line'].iloc[i] - df['macd_line'].iloc[i-10]
                
                if price_change < -self.divergence_threshold and macd_change > self.divergence_threshold:
                    divergences.append({
                        'type': 'bullish_divergence',
                        'date': df.index[i] if hasattr(df.index[i], 'date') else i,
                        'price_change': price_change,
                        'macd_change': macd_change,
                        'strength': abs(macd_change) / abs(price_change) if price_change != 0 else 0
                    })
        
        # זיהוי דיברגנציה ברישה (מחיר עולה, MACD יורד)
        for i in range(20, len(df)):
            if price_highs.iloc[i] and macd_highs.iloc[i-10:i].any():
                # בדיקה אם המחיר עלה אבל MACD ירד
                price_change = df['close'].iloc[i] - df['close'].iloc[i-10]
                macd_change = df['macd_line'].iloc[i] - df['macd_line'].iloc[i-10]
                
                if price_change > self.divergence_threshold and macd_change < -self.divergence_threshold:
                    divergences.append({
                        'type': 'bearish_divergence',
                        'date': df.index[i] if hasattr(df.index[i], 'date') else i,
                        'price_change': price_change,
                        'macd_change': macd_change,
                        'strength': abs(macd_change) / abs(price_change) if price_change != 0 else 0
                    })
        
        return divergences[-5:]  # רק 5 הדיברגנציות האחרונות

    def _analyze_signal_strength(self, df: pd.DataFrame) -> Dict:
        """ניתוח עוצמת סיגנל"""
        if len(df) < 20:
            return {'signal_strength': 0, 'signal_quality': 'poor'}
        
        # ניתוח עקביות הסיגנל
        recent_histogram = df["macd_histogram"].tail(self.freshness_days)
        positive_days = (recent_histogram > 0).sum()
        negative_days = (recent_histogram < 0).sum()
        
        # חישוב עוצמת סיגנל
        if positive_days > negative_days:
            signal_strength = (positive_days / self.freshness_days) * 100
            signal_quality = 'bullish'
        elif negative_days > positive_days:
            signal_strength = (negative_days / self.freshness_days) * 100
            signal_quality = 'bearish'
        else:
            signal_strength = 50
            signal_quality = 'neutral'
        
        # ניתוח יציבות הסיגנל
        histogram_std = recent_histogram.std()
        signal_stability = max(0, 100 - (histogram_std * 100))
        
        return {
            'signal_strength': signal_strength,
            'signal_quality': signal_quality,
            'signal_stability': signal_stability,
            'positive_days': positive_days,
            'negative_days': negative_days
        }

    def _analyze_historical_comparison(self, df: pd.DataFrame) -> Dict:
        """השוואה היסטורית"""
        if len(df) < 100:
            return {'historical_percentile': 50, 'historical_trend': 'neutral'}
        
        # אחוזון היסטורי של היסטוגרמה
        current_histogram = df["macd_histogram"].iloc[-1]
        historical_percentile = (df["macd_histogram"] < current_histogram).mean() * 100
        
        # מגמה היסטורית
        long_term_trend = df["macd_histogram"].tail(50).mean()
        if long_term_trend > 0.01:
            historical_trend = 'bullish'
        elif long_term_trend < -0.01:
            historical_trend = 'bearish'
        else:
            historical_trend = 'neutral'
        
        return {
            'historical_percentile': historical_percentile,
            'historical_trend': historical_trend,
            'long_term_average': long_term_trend
        }

    def _get_default_macd_metrics(self) -> Dict:
        """החזרת מדדי MACD ברירת מחדל"""
        return {
            'macd_line': 0.0,
            'signal_line': 0.0,
            'histogram': 0.0,
            'momentum': 0.0,
            'momentum_strength': 0.0,
            'histogram_trend': 0.0,
            'signal_type': 'neutral',
            'historical_percentile': 50.0
        }

    def _calculate_composite_score(self, macd_metrics: Dict, signal_analysis: Dict, 
                                 divergences: List[Dict], historical: Dict) -> int:
        """חישוב ציון מורכב"""
        scores = {}
        
        # ציון ערך היסטוגרמה
        histogram_value = macd_metrics['histogram']
        if histogram_value > 0.05:
            hist_score = 90
        elif histogram_value > 0.02:
            hist_score = 75
        elif histogram_value > 0:
            hist_score = 60
        elif histogram_value > -0.02:
            hist_score = 40
        elif histogram_value > -0.05:
            hist_score = 25
        else:
            hist_score = 10
        scores['histogram_value'] = hist_score
        
        # ציון מגמת מומנטום
        momentum_trend = macd_metrics['histogram_trend']
        if momentum_trend > 0.2:
            momentum_score = 90
        elif momentum_trend > 0.1:
            momentum_score = 75
        elif momentum_trend > 0:
            momentum_score = 60
        elif momentum_trend > -0.1:
            momentum_score = 40
        elif momentum_trend > -0.2:
            momentum_score = 25
        else:
            momentum_score = 10
        scores['momentum_trend'] = momentum_score
        
        # ציון עוצמת סיגנל
        signal_strength = signal_analysis.get('signal_strength', 50)
        scores['signal_strength'] = signal_strength
        
        # ציון דיברגנציות
        if divergences:
            # דיברגנציה בולית מעלה את הציון
            bullish_divs = [d for d in divergences if d['type'] == 'bullish_divergence']
            bearish_divs = [d for d in divergences if d['type'] == 'bearish_divergence']
            
            if bullish_divs:
                divergence_score = 80
            elif bearish_divs:
                divergence_score = 20
            else:
                divergence_score = 50
        else:
            divergence_score = 50
        scores['divergence_analysis'] = divergence_score
        
        # ציון השוואה היסטורית
        historical_percentile = historical.get('historical_percentile', 50)
        scores['historical_comparison'] = historical_percentile
        
        # חישוב ציון מורכב
        composite_score = sum(scores[component] * self.weights[component] 
                            for component in scores.keys())
        
        return int(composite_score)

    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח MACD מתקדם
        
        Args:
            symbol: סימול המניה
            price_df: DataFrame עם נתוני מחיר
            
        Returns:
            Dict עם score, explanation, details
        """
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=90)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            if len(price_df) < 30:
                return self.fallback()
            
            # חישוב אינדיקטורי MACD
            df = self._calculate_macd_indicators(price_df)
            
            # ניתוח מומנטום MACD
            macd_metrics = self._analyze_macd_momentum(df)
            
            # זיהוי דיברגנציות
            divergences = self._detect_divergences(df)
            
            # ניתוח עוצמת סיגנל
            signal_analysis = self._analyze_signal_strength(df)
            
            # השוואה היסטורית
            historical = self._analyze_historical_comparison(df)
            
            # חישוב ציון מורכב
            score = self._calculate_composite_score(
                macd_metrics, signal_analysis, divergences, historical
            )
            
            # יצירת הסבר
            explanation_parts = []
            signal_name = self.signal_types.get(macd_metrics['signal_type'], macd_metrics['signal_type'])
            explanation_parts.append(f"סיגנל: {signal_name}")
            explanation_parts.append(f"היסטוגרמה: {macd_metrics['histogram']:.4f}")
            
            if divergences:
                div_types = [d['type'] for d in divergences]
                explanation_parts.append(f"דיברגנציות: {len(divergences)}")
            
            if signal_analysis.get('signal_stability', 0) > 70:
                explanation_parts.append("סיגנל יציב")
            
            explanation = " | ".join(explanation_parts)
            
            # יצירת פרטים מפורטים
            details = {
                'symbol': symbol,
                'macd_metrics': macd_metrics,
                'signal_analysis': signal_analysis,
                'divergences': divergences,
                'historical_comparison': historical,
                'analysis_date': datetime.now().isoformat(),
                'data_points': len(price_df)
            }
            
            return {
                "score": score,
                "explanation": explanation,
                "details": details
            }
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()
