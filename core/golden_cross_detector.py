import pandas as pd

class GoldenCrossDetector:
    def __init__(self, config=None):
        self.short_window = config.get("short_window", 50) if config else 50
        self.long_window = config.get("long_window", 200) if config else 200
        self.freshness_days = config.get("freshness_days", 7) if config else 7

    def analyze(self, price_df):
        df = price_df.copy()
        df["ma_short"] = df["close"].rolling(self.short_window).mean()
        df["ma_long"] = df["close"].rolling(self.long_window).mean()

        cross_days = (df["ma_short"] > df["ma_long"])
        cross_events = cross_days & (~cross_days.shift(1, fill_value=False))
        cross_idx = df.index[cross_events].tolist()

        if not cross_idx:
            return 1  # No cross, ציון מינימלי

        last_cross_idx = cross_idx[-1]
        days_since_cross = (df.index[-1] - last_cross_idx).days if hasattr(df.index[-1], "days") else len(df) - df.index.get_loc(last_cross_idx) - 1

        # טריות האירוע
        if days_since_cross <= self.freshness_days:
            base_score = 100
        elif days_since_cross <= self.freshness_days * 4:
            base_score = 70
        else:
            base_score = 40

        # חיזוק לפי עוצמת החצייה (פער היחסי)
        try:
            short_val = df.loc[last_cross_idx, "ma_short"]
            long_val = df.loc[last_cross_idx, "ma_long"]
            gap = abs(short_val - long_val) / long_val * 100
            gap_score = min(30, gap)
        except:
            gap_score = 0

        score = int(min(100, base_score + gap_score))
        return score
