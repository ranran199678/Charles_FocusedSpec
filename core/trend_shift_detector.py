import pandas as pd
import numpy as np
import os
from datetime import datetime
from ta.trend import MACD, ADXIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from utils.data_fetcher import DataFetcher
from core.subagents.macd_rsi_divergence_agent import MACDRSIDivergenceAgent
from core.base.live_executable_agent import LiveExecutableAgent

class TrendShiftDetector(LiveExecutableAgent):
    def __init__(self, symbol, short_window=20, long_window=50, interval="1day", live_mode=False, frequency_sec=60):
        super().__init__(symbol, interval, live_mode, frequency_sec)
        self.short_window = short_window
        self.long_window = long_window
        self.fetcher = DataFetcher()
        self.divergence_agent = MACDRSIDivergenceAgent()
        self.result = {}
        self.log_path = "outputs/forecast_logs/trend_shift_signals.csv"

    def fetch_data(self):
        if self.live_mode:
            df = self.fetcher.fetch_live_prices(self.symbol, interval=self.interval)
        else:
            price_data = self.fetcher.fetch_prices_batch([self.symbol], interval=self.interval)
            df = price_data.get(self.symbol)

        if df is None or df.empty or len(df) < max(self.short_window, self.long_window, 50):
            raise ValueError("❌ לא נמצאו מספיק נתונים עבור הסימבול")
        return df.sort_index()

    def compute_indicators(self, df):
        try:
            df["ema_short"] = EMAIndicator(df["close"], window=self.short_window).ema_indicator()
            df["ema_long"] = EMAIndicator(df["close"], window=self.long_window).ema_indicator()
            df["macd_diff"] = MACD(df["close"]).macd_diff()
            df["rsi"] = RSIIndicator(df["close"]).rsi()
            df["price_slope"] = df["close"].pct_change(periods=3).rolling(window=5).mean()
            df["volume_change"] = df["volume"].pct_change().rolling(window=5).mean()
            if "high" in df.columns and "low" in df.columns:
                df["adx"] = ADXIndicator(df["high"], df["low"], df["close"]).adx()
            else:
                df["adx"] = np.nan
        except Exception as e:
            raise RuntimeError(f"❌ שגיאה בחישוב אינדיקטורים: {e}")
        return df

    def detect_shift(self, df):
        latest = df.iloc[-1]
        score = 0
        explanations = []

        # ניקוד מקסימלי = 100
        if latest["ema_short"] > latest["ema_long"]:
            score += 20
            explanations.append("📈 חיתוך EMA שורי")
        elif latest["ema_short"] < latest["ema_long"]:
            explanations.append("📉 חיתוך EMA דובי")

        if latest["macd_diff"] > 0:
            score += 15
            explanations.append("📈 MACD חיובי")
        else:
            explanations.append("📉 MACD שלילי")

        if not pd.isna(latest["adx"]):
            if latest["adx"] > 25:
                score += 10
                explanations.append("⚡ ADX גבוה – מגמה חזקה")
            elif latest["adx"] < 15:
                explanations.append("😴 ADX נמוך – מגמה חלשה")

        if 50 < latest["rsi"] < 70:
            score += 10
            explanations.append("📊 RSI מצביע על מומנטום בינוני חיובי")
        elif latest["rsi"] < 30:
            score += 5
            explanations.append("🔻 RSI נמוך – מצב מכירות יתר")

        if latest["price_slope"] > 0:
            score += 15
            explanations.append("↗️ שיפוע מחירים עולה")
        else:
            explanations.append("↘️ שיפוע מחירים יורד")

        if latest["volume_change"] > 0.1:
            score += 10
            explanations.append("📊 נפח מסחר בעלייה")
        elif latest["volume_change"] < -0.1:
            explanations.append("📉 נפח מסחר בירידה")

        divergence_result = self.divergence_agent.analyze(df)
        score += divergence_result.get("score_contribution", 0)
        explanations.append(f"📉 Divergence: {divergence_result.get('explanation', '')}")

        score = min(score, 100)
        signal = score >= 60
        shift_category = self.classify_shift(score)

        result = {
            "symbol": self.symbol,
            "trend_shift_score": round(score, 2),
            "shift_category": shift_category,
            "signal": signal,
            "interval": self.interval,
            "explanations": explanations,
            "timestamp": str(datetime.now())
        }

        if signal:
            self.save_signal_log(result)

        self.result = result
        return result

    def classify_shift(self, score):
        if score >= 80:
            return "🔼 מגמת עלייה ברורה"
        elif 60 <= score < 80:
            return "🟢 התחלה של שינוי מגמה חיובי"
        elif 40 <= score < 60:
            return "⚪ אין שינוי מגמה מובהק"
        elif 20 <= score < 40:
            return "🔴 התחלה של שינוי מגמה שלילי"
        else:
            return "⛔ מגמת ירידה ברורה"

    def save_signal_log(self, result):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        row = {
            "timestamp": result["timestamp"],
            "symbol": result["symbol"],
            "score": result["trend_shift_score"],
            "category": result["shift_category"],
            "explanation": " | ".join(result["explanations"])
        }
        df = pd.DataFrame([row])
        if not os.path.exists(self.log_path):
            df.to_csv(self.log_path, index=False, mode="w", encoding="utf-8-sig")
        else:
            df.to_csv(self.log_path, index=False, mode="a", header=False, encoding="utf-8-sig")

    def run(self):
        df = self.fetch_data()
        df = self.compute_indicators(df)
        return self.detect_shift(df)

    def run_once(self):
        return self.run()

    def run_live(self, symbol=None, df=None):
        df = self.fetch_data() if df is None else df
        df = self.compute_indicators(df.sort_index())
        return self.detect_shift(df)

    def analyze(self, symbol, price_df):
        """
        עטיפת analyze תואמת AlphaScoreEngine
        """
        try:
            df = self.compute_indicators(price_df)
            result = self.detect_shift(df)
            score = int(result["trend_shift_score"])
            explanation = result["shift_category"]
            return {
                "score": score,
                "explanation": explanation,
                "details": {"explanations": result["explanations"]}
            }
        except Exception as e:
            return {
                "score": 1,
                "explanation": f"שגיאת TrendShiftDetector: {e}",
                "details": {}
            }
