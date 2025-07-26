import pandas as pd
import numpy as np

class MACDRSIDivergenceAgent:
    def __init__(self, lookback=20):
        self.lookback = lookback

    def analyze(self, df):
        """
        df חייב להכיל את העמודות: close, macd_diff, rsi
        """
        df = df.copy().dropna(subset=["close", "macd_diff", "rsi"])
        if len(df) < self.lookback + 5:
            return {
                "divergence_detected": False,
                "type": None,
                "score_contribution": 0,
                "explanation": "📉 לא מספיק נתונים לניתוח divergence"
            }

        # שליפת חלון הסתכלות אחרון
        window = df.iloc[-self.lookback:]
        price_trend = np.polyfit(range(len(window)), window["close"], deg=1)[0]
        macd_trend = np.polyfit(range(len(window)), window["macd_diff"], deg=1)[0]
        rsi_trend = np.polyfit(range(len(window)), window["rsi"], deg=1)[0]

        explanations = []

        # הגדרה: מחיר עולה אבל MACD/RSI יורדים → Divergence שלילי
        if price_trend > 0 and (macd_trend < 0 or rsi_trend < 0):
            explanations.append("⚠️ Divergence שלילי: המחיר עולה אבל האינדיקטורים יורדים")
            return {
                "divergence_detected": True,
                "type": "negative",
                "score_contribution": -1.5,
                "explanation": explanations[-1]
            }

        # הגדרה: מחיר יורד אבל MACD/RSI עולים → Divergence חיובי
        elif price_trend < 0 and (macd_trend > 0 or rsi_trend > 0):
            explanations.append("📈 Divergence חיובי: המחיר יורד אבל האינדיקטורים עולים")
            return {
                "divergence_detected": True,
                "type": "positive",
                "score_contribution": 1.5,
                "explanation": explanations[-1]
            }

        else:
            return {
                "divergence_detected": False,
                "type": None,
                "score_contribution": 0,
                "explanation": "🔍 לא זוהתה סטייה בין המחיר לאינדיקטורים"
            }
