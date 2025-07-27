import pandas as pd
import numpy as np

class CandlestickAgent:
    def __init__(self, config=None):
        """
        Candlestick Agent – זיהוי תבניות נרות יפניים ברמת על.
        config: dict עם פרמטרים אופציונליים.
        """
        cfg = config or {}
        self.lookback = cfg.get("lookback", 15)  # כמה ימים לבדוק אחורה
        self.vol_confirm = cfg.get("vol_confirm", 1.3)  # פי כמה מהנפח הממוצע הנדרש לאישור תבנית
        self.ma_period = cfg.get("ma_period", 20)  # ממוצע נע להקשר (תבנית ליד MA חשובה יותר)
        self.strong_patterns = ["Hammer", "Bullish Engulfing", "Morning Star", "Piercing Line",
                                "Shooting Star", "Bearish Engulfing", "Evening Star", "Dark Cloud Cover"]

    def analyze(self, symbol, price_df=None):
        """
        מחזיר ציון 1-100 לפי זיהוי עוצמת תבניות הנר, ווליום יחסי, ומיקום טכני.
        """
        if price_df is None or price_df.empty:
            return {
                "score": 1,
                "explanation": "אין נתוני מחיר זמינים",
                "details": {}
            }
        df = price_df.copy().reset_index(drop=True)
        if len(df) < self.lookback + self.ma_period:
            return 1  # לא מספיק נתונים

        df["body"] = abs(df["close"] - df["open"])
        df["range"] = df["high"] - df["low"]
        df["upper_shadow"] = df["high"] - df[["close", "open"]].max(axis=1)
        df["lower_shadow"] = df[["close", "open"]].min(axis=1) - df["low"]
        df["ma"] = df["close"].rolling(self.ma_period).mean()
        df["vol_mean"] = df["volume"].rolling(self.ma_period).mean()

        patterns_scores = []

        for i in range(len(df) - self.lookback, len(df)):
            row = df.iloc[i]
            pattern, base_score = self._detect_pattern(row, df.iloc[max(0, i-3):i+1])

            if pattern:
                # עוצמת תבנית
                score = base_score
                # תוספת ניקוד אם תבנית חזקה וממוקמת מעל/מתחת MA
                if pattern in self.strong_patterns:
                    if abs(row["close"] - row["ma"]) < 0.015 * row["ma"]:
                        score += 13  # מיקום מושלם
                # תוספת לפי גודל גוף/צל
                if pattern in ["Hammer", "Shooting Star"]:
                    if row["body"] < 0.32 * row["range"]:
                        score += 6  # צל חזק מגוף
                # תוספת לווליום תומך
                if row["volume"] > self.vol_confirm * row["vol_mean"]:
                    score += 15
                # ניקוד עד 100
                patterns_scores.append(min(score, 100))
        
        return int(max(patterns_scores) if patterns_scores else 1)

    def _detect_pattern(self, row, window_df):
        """
        מזהה תבניות מפתח. מחזיר (שם התבנית, בסיס ניקוד)
        """
        body = row["body"]
        rng = row["range"]
        upper = row["upper_shadow"]
        lower = row["lower_shadow"]
        open_ = row["open"]
        close = row["close"]

        # Hammer
        if lower > 2 * body and body > 0.1 * rng and upper < 0.3 * rng and close > open_:
            return "Hammer", 50
        # Shooting Star
        if upper > 2 * body and body > 0.1 * rng and lower < 0.3 * rng and close < open_:
            return "Shooting Star", 47
        # Bullish Engulfing
        if len(window_df) >= 2:
            prev = window_df.iloc[-2]
            if prev["close"] < prev["open"] and close > open_ and close > prev["open"] and open_ < prev["close"]:
                return "Bullish Engulfing", 52
            if prev["close"] > prev["open"] and close < open_ and close < prev["open"] and open_ > prev["close"]:
                return "Bearish Engulfing", 50
        # Doji
        if body < 0.09 * rng and upper > 0.35 * rng and lower > 0.35 * rng:
            return "Doji", 34
        # Marubozu
        if body > 0.9 * rng and upper < 0.04 * rng and lower < 0.04 * rng:
            return "Marubozu", 38
        # Morning Star (3 נרות)
        if len(window_df) >= 3:
            a, b, c = window_df.iloc[-3], window_df.iloc[-2], window_df.iloc[-1]
            if (a["close"] < a["open"] and
                b["body"] < 0.3 * b["range"] and
                c["close"] > c["open"] and c["close"] > ((a["close"] + a["open"])/2)):
                return "Morning Star", 55
            if (a["close"] > a["open"] and
                b["body"] < 0.3 * b["range"] and
                c["close"] < c["open"] and c["close"] < ((a["close"] + a["open"])/2)):
                return "Evening Star", 55
        # Piercing Line
        if len(window_df) >= 2:
            prev = window_df.iloc[-2]
            if prev["close"] < prev["open"] and close > open_ and open_ < prev["close"] and close > (prev["open"] + prev["close"])/2:
                return "Piercing Line", 49
            if prev["close"] > prev["open"] and close < open_ and open_ > prev["close"] and close < (prev["open"] + prev["close"])/2:
                return "Dark Cloud Cover", 49

        return None, 0
