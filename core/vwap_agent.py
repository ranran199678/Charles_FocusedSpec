import pandas as pd
import numpy as np

class VWAPAgent:
    def __init__(self, config=None):
        """
        אתחול הסוכן, אפשר להגדיר סף z-score חריג (ברירת מחדל: 1.5 סטיות תקן).
        config: {"zscore_threshold": 1.5}
        """
        cfg = config or {}
        self.zscore_threshold = cfg.get("zscore_threshold", 1.5)

    def analyze(self, price_df):
        """
        ניתוח האם המניה נסחרת מעל/מתחת ל-VWAP ברמת חריגה מובהקת.
        מחזיר ציון 1-100: 100=קניה קיצונית, 1=מכירה קיצונית, 50=שוק ניטרלי.
        """
        if len(price_df) < 20:
            return 50  # אין מספיק נתונים

        # חישוב VWAP יומי (volume-weighted average price)
        price_df["TP"] = (price_df["high"] + price_df["low"] + price_df["close"]) / 3
        vwap = (price_df["TP"] * price_df["volume"]).cumsum() / price_df["volume"].cumsum()
        price_df["vwap"] = vwap

        # חישוב סטיית תקן של המרחק מה-VWAP ב-20 הימים האחרונים
        price_df["dist"] = price_df["close"] - price_df["vwap"]
        last_20 = price_df["dist"].tail(20)
        mean = last_20.mean()
        std = last_20.std(ddof=0)
        latest_dist = price_df["dist"].iloc[-1]

        # חישוב Z-score של המרחק מה-VWAP
        if std == 0:
            z = 0
        else:
            z = (latest_dist - mean) / std

        # ציון - סקאלה 1-100 (100 = קניה קיצונית, 1 = מכירה קיצונית, 50 = ניטרלי)
        # חריגה מעל סף --> קניה, מתחת --> מכירה
        if z > self.zscore_threshold:
            score = int(100 - min(40, abs(z * 20)))
        elif z < -self.zscore_threshold:
            score = int(1 + min(40, abs(z * 20)))
        else:
            score = 50 + int(z * 20)  # אזור ניטרלי
        # הגבלת הציון 1-100
        score = max(1, min(100, score))
        return score
