import pandas as pd
import numpy as np

class ATRScoreAgent:
    def __init__(self, config=None):
        self.lookback = config.get("lookback", 14) if config else 14
        self.scale = config.get("scale", 15) if config else 15  # קבוע לנירמול

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
        score = int(max(1, min(100, 50 + self.scale * (ratio - 1) * 25)))
        
        return {
            "score": score,
            "explanation": f"ATR יחסי: {ratio:.2f}",
            "details": {
                "current_atr": current_atr,
                "avg_atr": avg_atr,
                "ratio": ratio
            }
        }
