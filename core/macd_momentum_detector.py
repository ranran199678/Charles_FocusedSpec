import pandas as pd

class MACDMomentumDetector:
    def __init__(self, config=None):
        self.fast = config.get("fast", 12) if config else 12
        self.slow = config.get("slow", 26) if config else 26
        self.signal = config.get("signal", 9) if config else 9
        self.freshness_days = config.get("freshness_days", 5) if config else 5

    def analyze(self, symbol, price_df=None):
        if price_df is None:
            return {
                "score": 50,
                "explanation": "אין נתוני מחיר זמינים",
                "details": {}
            }
        
        df = price_df.copy()
        df["ema_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()
        df["macd"] = df["ema_fast"] - df["ema_slow"]
        df["macd_signal"] = df["macd"].ewm(span=self.signal, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        # ניתוח המומנטום (חיובי = שורי)
        hist = df["macd_hist"].iloc[-self.freshness_days:]
        pos = (hist > 0).sum()
        neg = (hist < 0).sum()
        last_hist = hist.iloc[-1]

        # חישוב ניקוד
        if last_hist > 0:
            base = 60 + min(40, int(last_hist * 200))   # סיגנל חזק
            score = min(100, base + pos * 5 - neg * 5)
        else:
            score = max(1, 50 + int(last_hist * 100))   # סיגנל שלילי מוחלש

        return {
            "score": int(score),
            "explanation": f"MACD Histogram: {last_hist:.4f}, חיובי: {pos}, שלילי: {neg}",
            "details": {
                "macd_histogram": last_hist,
                "positive_days": pos,
                "negative_days": neg
            }
        }
