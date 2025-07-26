import pandas as pd

class MidtermMomentumAgent:
    def __init__(self, config=None):
        self.short_period = config.get("short_period", 21) if config else 21   # חודש
        self.long_period = config.get("long_period", 63) if config else 63     # 3 חודשים
        self.weight_short = config.get("weight_short", 0.5) if config else 0.5

    def analyze(self, price_df):
        if price_df is None or len(price_df) < self.long_period:
            return 1

        # ממוצע נע קצר וארוך
        price_df = price_df.copy()
        price_df["SMA_short"] = price_df["close"].rolling(window=self.short_period).mean()
        price_df["SMA_long"] = price_df["close"].rolling(window=self.long_period).mean()

        # שינוי אחוזי מחיר ל-3 ו-6 חודשים
        last_price = price_df["close"].iloc[-1]
        try:
            change_short = (last_price / price_df["close"].iloc[-self.short_period] - 1) * 100
        except Exception:
            change_short = 0
        try:
            change_long = (last_price / price_df["close"].iloc[-self.long_period] - 1) * 100
        except Exception:
            change_long = 0

        # ניקוד מומנטום: 1-100
        score_short = max(1, min(100, int(change_short + 50)))
        score_long = max(1, min(100, int(change_long + 50)))
        score = int(self.weight_short * score_short + (1 - self.weight_short) * score_long)
        return max(1, min(100, score))
