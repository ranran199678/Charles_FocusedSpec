import pandas as pd
import numpy as np

class ATRVolatilityAgent:
    def __init__(self, config=None):
        self.lookback = config.get("lookback", 14) if config else 14

    def analyze(self, symbol, price_df=None):
        if price_df is None:
            return {
                "score": 50,
                "explanation": "אין נתוני מחיר זמינים",
                "details": {}
            }
        
        # חישוב ATR
        high = price_df['high']
        low = price_df['low']
        close = price_df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        
        current_atr = atr.iloc[-1]
        avg_atr = atr.mean()
        
        # חישוב יחס תנודתיות
        ratio = current_atr / avg_atr if avg_atr > 0 else 1
        
        # חישוב ציון
        score = int(max(1, min(100, ratio * 40 + 60)))  # רגיל סביב 60–80, קפיצה מעל 100%
        
        return {
            "score": score,
            "explanation": f"תנודתיות ATR: {ratio:.2f}x",
            "details": {
                "current_atr": current_atr,
                "avg_atr": avg_atr,
                "ratio": ratio
            }
        }
