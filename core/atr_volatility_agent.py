import pandas as pd
import numpy as np

class ATRVolatilityAgent:
    def __init__(self, config=None):
        self.lookback = config.get("lookback", 14) if config else 14

    def analyze(self, price_df):
        if price_df is None or len(price_df) < self.lookback + 2:
            return 1
        high = price_df["high"]
        low = price_df["low"]
        close = price_df["close"]
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(self.lookback).mean()
        # ניקוד יחסי: ATR האחרון ביחס ל־ATR ממוצע (ל־100 יום אחורה)
        recent_atr = atr.iloc[-1] if not atr.empty else 0
        long_term_atr = atr.rolling(100).mean().iloc[-1] if len(atr) >= 100 else atr.mean()
        # היחס (אם אין מספיק היסטוריה)
        ratio = recent_atr / long_term_atr if long_term_atr > 0 else 0
        # נרמל ל־1–100, ערך 1 אם תנודתיות נמוכה, 100 אם חריגה
        score = int(max(1, min(100, ratio * 40 + 60)))  # רגיל סביב 60–80, קפיצה מעל 100%
        return score
