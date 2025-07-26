import pandas as pd
from ta.volatility import BollingerBands
from utils.data_fetcher import DataFetcher

class BollingerSqueezeAgent:
    def __init__(self, symbol, interval="1day", live_mode=False):
        self.symbol = symbol
        self.interval = interval
        self.live_mode = live_mode
        self.fetcher = DataFetcher()

    def fetch_data(self):
        if self.live_mode:
            df = self.fetcher.fetch_live_prices(self.symbol, interval=self.interval)
        else:
            data = self.fetcher.fetch_prices_batch([self.symbol], interval=self.interval)
            df = data.get(self.symbol)

        if df is None or df.empty:
            raise ValueError("❌ לא נמצאו נתונים עבור הסימבול")
        return df.sort_index()

    def analyze(self, df):
        if df is None or df.empty or len(df) < 20:
            return {
                "symbol": self.symbol,
                "interval": self.interval,
                "score": 0,
                "explanation": "❌ לא מספיק נתונים לניתוח",
                "details": {}
            }

        indicator = BollingerBands(close=df["close"], window=20, window_dev=2)
        df["bb_bbm"] = indicator.bollinger_mavg()
        df["bb_bbh"] = indicator.bollinger_hband()
        df["bb_bbl"] = indicator.bollinger_lband()
        df["bb_width"] = df["bb_bbh"] - df["bb_bbl"]

        latest = df.iloc[-1]
        width_now = latest["bb_width"]
        avg_width = df["bb_width"].rolling(window=20).mean().iloc[-1]

        is_squeeze = width_now < avg_width * 0.75
        explanation = "🧪 זוהתה התכווצות בולינגר – ייתכן מהלך חד" if is_squeeze else "📏 אין סימני התכווצות חריגה"
        score = 80 if is_squeeze else 20

        return {
            "symbol": self.symbol,
            "interval": self.interval,
            "score": score,
            "explanation": explanation,
            "details": {
                "bb_width": round(width_now, 5),
                "avg_width": round(avg_width, 5),
                "is_squeeze": is_squeeze
            }
        }

    def run(self):
        df = self.fetch_data()
        return self.analyze(df)

    def run_live(self, price_df=None):
        df = self.fetch_data() if price_df is None else price_df
        return self.analyze(df)
