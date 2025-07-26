# core/adx_score_agent.py

import pandas as pd
import numpy as np
from ta.trend import ADXIndicator
from datetime import datetime, timezone

# קבועים ברירת מחדל (אם לא יועברו ב-config)
DEFAULTS = {
    "ADX_COL": "adx",
    "HIGH_COL": "high",
    "LOW_COL": "low",
    "CLOSE_COL": "close",
    "ADX_LOOKBACK_PERIOD": 14,
    "ADX_STRONG_THRESHOLD": 30,
    "ADX_MEDIUM_THRESHOLD": 20,
    "AGENT_NAME": "ADXScoreAgent"
}

class ADXScoreAgent:
    def __init__(self, config=None):
        self.config = config or {}
        # קונפיגורציה דינמית
        self.ADX_COL = self.config.get("ADX_COL", DEFAULTS["ADX_COL"])
        self.HIGH_COL = self.config.get("HIGH_COL", DEFAULTS["HIGH_COL"])
        self.LOW_COL = self.config.get("LOW_COL", DEFAULTS["LOW_COL"])
        self.CLOSE_COL = self.config.get("CLOSE_COL", DEFAULTS["CLOSE_COL"])
        self.ADX_LOOKBACK_PERIOD = self.config.get("ADX_LOOKBACK_PERIOD", DEFAULTS["ADX_LOOKBACK_PERIOD"])
        self.ADX_STRONG_THRESHOLD = self.config.get("ADX_STRONG_THRESHOLD", DEFAULTS["ADX_STRONG_THRESHOLD"])
        self.ADX_MEDIUM_THRESHOLD = self.config.get("ADX_MEDIUM_THRESHOLD", DEFAULTS["ADX_MEDIUM_THRESHOLD"])
        self.AGENT_NAME = self.config.get("AGENT_NAME", DEFAULTS["AGENT_NAME"])

    def analyze(self, symbol, price_df, price_df_weekly=None):
        results = {}
        try:
            # ניתוח טיימפריים עיקרי (יומי)
            results["daily"] = self._analyze_single(symbol, price_df, timeframe="daily")
        except Exception as e:
            results["daily"] = {
                "score": 1,
                "explanation": f"שגיאה בחישוב ADX (daily): {str(e)}",
                "details": {}
            }
        if price_df_weekly is not None:
            try:
                results["weekly"] = self._analyze_single(symbol, price_df_weekly, timeframe="weekly")
            except Exception as e:
                results["weekly"] = {
                    "score": 1,
                    "explanation": f"שגיאה בחישוב ADX (weekly): {str(e)}",
                    "details": {}
                }
        # בחר את הציון הגבוה ביותר (או עשה שקלול בעתיד)
        main_result = results.get("daily")
        # פלט אחיד
        return {
            "symbol": symbol,
            "agent_name": self.AGENT_NAME,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "score": main_result["score"],
            "explanation": main_result["explanation"],
            "details": main_result["details"],
            "all_timeframes": results
        }

    def _analyze_single(self, symbol, df, timeframe="daily"):
        # בדיקת עמודות
        if not all(col in df.columns for col in [self.HIGH_COL, self.LOW_COL, self.CLOSE_COL]):
            return {
                "score": 1,
                "explanation": f"נתוני {self.HIGH_COL}/{self.LOW_COL}/{self.CLOSE_COL} חסרים לחישוב ADX.",
                "details": {"timeframe": timeframe}
            }
        if len(df) < self.ADX_LOOKBACK_PERIOD:
            return {
                "score": 1,
                "explanation": f"אין מספיק נתונים לחישוב ADX (נדרשים לפחות {self.ADX_LOOKBACK_PERIOD}, יש {len(df)})",
                "details": {"timeframe": timeframe}
            }
        adx_indicator = ADXIndicator(
            high=df[self.HIGH_COL],
            low=df[self.LOW_COL],
            close=df[self.CLOSE_COL],
            window=self.ADX_LOOKBACK_PERIOD,
            fillna=False
        )
        df[self.ADX_COL] = adx_indicator.adx()
        adx_series = df[self.ADX_COL].dropna()
        if adx_series.empty:
            return {
                "score": 1,
                "explanation": "לא ניתן לחשב ADX (סדרה ריקה)",
                "details": {"timeframe": timeframe}
            }
        latest_adx = adx_series.iloc[-1]
        prev_adx = adx_series.iloc[-2] if len(adx_series) > 1 else latest_adx
        adx_trend = "עולה" if latest_adx > prev_adx else ("יורד" if latest_adx < prev_adx else "יציב")
        adx_change = latest_adx - prev_adx
        # הסבריות מורחבת
        if latest_adx >= self.ADX_STRONG_THRESHOLD:
            score = 90
            explanation = f"ADX גבוה ({latest_adx:.2f}) - טרנד חזק בזיהוי. המגמה {adx_trend} ({adx_change:+.2f})"
        elif latest_adx >= self.ADX_MEDIUM_THRESHOLD:
            score = 60
            explanation = f"ADX בינוני ({latest_adx:.2f}) - יתכן טרנד מתפתח. המגמה {adx_trend} ({adx_change:+.2f})"
        else:
            score = 20
            explanation = f"ADX נמוך ({latest_adx:.2f}) - שוק דשדוש. המגמה {adx_trend} ({adx_change:+.2f})"
        # חריגות/התרעות
        if abs(adx_change) > 10:
            explanation += " | שינוי חד ב-ADX!"
        return {
            "score": score,
            "explanation": explanation,
            "details": {
                "latest_adx": float(latest_adx),
                "prev_adx": float(prev_adx),
                "adx_trend": adx_trend,
                "adx_change": float(adx_change),
                "adx_series": adx_series.round(2).tail(5).to_dict(),
                "timeframe": timeframe
            }
        }
