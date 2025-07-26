# trend_detector.py – גרסה מתקדמת

from typing import Dict
import numpy as np
import pandas as pd

class TrendDetector:
    """
    סוכן טכני C1a מתקדם – מזהה מגמה באמצעות חיתוך ממוצעים, עוצמה סטטיסטית, ונפח מסחר.
    מחזיר גם מדד עוצמה ופרטים נוספים להצלבה עתידית.
    """

    def __init__(self, short_window: int = 20, long_window: int = 50, volume_threshold: float = 1.1):
        self.short_window = short_window
        self.long_window = long_window
        self.volume_threshold = volume_threshold  # ווליום נוכחי לעומת ממוצע

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['MA_short'] = df['close'].rolling(window=self.short_window).mean()
        df['MA_long'] = df['close'].rolling(window=self.long_window).mean()
        df['MA_diff'] = df['MA_short'] - df['MA_long']
        df['Volume_MA'] = df['volume'].rolling(window=self.short_window).mean()
        return df

    def detect_trend(self, df: pd.DataFrame) -> Dict[str, object]:
        df = self.calculate_indicators(df)
        last = df.iloc[-1]

        ma_short, ma_long = last['MA_short'], last['MA_long']
        volume_now, volume_avg = last['volume'], last['Volume_MA']

        if np.isnan(ma_short) or np.isnan(ma_long) or np.isnan(volume_avg):
            return {"trend": "unknown", "score": 0.0}

        diff = ma_short - ma_long
        pct_diff = diff / ma_long if ma_long != 0 else 0

        volume_factor = volume_now / volume_avg if volume_avg != 0 else 1.0
        strong_volume = volume_factor >= self.volume_threshold

        if pct_diff > 0.02 and strong_volume:
            return {"trend": "uptrend", "score": 90.0, "volume_boost": True}
        elif pct_diff > 0.02:
            return {"trend": "uptrend_weak", "score": 75.0, "volume_boost": False}
        elif pct_diff < -0.02 and strong_volume:
            return {"trend": "downtrend", "score": 25.0, "volume_boost": True}
        elif pct_diff < -0.02:
            return {"trend": "downtrend_weak", "score": 40.0, "volume_boost": False}
        else:
            return {"trend": "neutral", "score": 50.0, "volume_boost": False}

    def run(self, df: pd.DataFrame) -> Dict[str, object]:
        return self.detect_trend(df)
