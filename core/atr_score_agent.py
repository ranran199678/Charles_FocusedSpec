import pandas as pd
import numpy as np

class ATRScoreAgent:
    def __init__(self, config=None):
        self.lookback = config.get("lookback", 14) if config else 14
        self.scale = config.get("scale", 15) if config else 15  # קבוע לנירמול

    def analyze(self, price_df):
        if price_df is None or len(price_df) < self.lookback + 1:
            return 1
        # חישוב True Range לכל יום
        high = price_df["high"]
        low = price_df["low"]
        close = price_df["close"]
        prev_close = close.shift(1)
        tr = pd.concat([
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(self.lookback).mean()
        recent_atr = atr.iloc[-1]
        mean_atr = atr.mean()
        # ניקוד: כמה ה-ATR העדכני גבוה מהממוצע
        if mean_atr == 0 or np.isnan(recent_atr):
            score = 1
        else:
            ratio = recent_atr / mean_atr
            score = int(max(1, min(100, 50 + self.scale * (ratio - 1) * 25)))
        return score
