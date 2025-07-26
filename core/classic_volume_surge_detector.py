import pandas as pd

class ClassicVolumeSurgeDetector:
    def __init__(self, config=None):
        self.window = config.get("window", 20) if config else 20
        self.threshold_sigma = config.get("threshold_sigma", 2) if config else 2
        self.freshness_days = config.get("freshness_days", 5) if config else 5

    def analyze(self, price_df):
        df = price_df.copy()
        df["vol_ma"] = df["volume"].rolling(self.window).mean()
        df["vol_std"] = df["volume"].rolling(self.window).std()
        df["vol_sigma"] = (df["volume"] - df["vol_ma"]) / df["vol_std"]
        last = df.iloc[-self.freshness_days:]
        max_sigma = last["vol_sigma"].max()
        # ניקוד לפי חריגות: כל סטיית תקן = 15 נק', capped
        if max_sigma < self.threshold_sigma:
            return 1
        score = min(100, int((max_sigma - self.threshold_sigma) * 15 + 50))
        return max(1, score)
