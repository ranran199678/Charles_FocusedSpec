import pandas as pd

class ClassicVolumeSurgeDetector:
    def __init__(self, config=None):
        self.window = config.get("window", 20) if config else 20
        self.threshold_sigma = config.get("threshold_sigma", 2) if config else 2
        self.freshness_days = config.get("freshness_days", 5) if config else 5

    def analyze(self, symbol, price_df=None):
        if price_df is None:
            return {
                "score": 50,
                "explanation": "אין נתוני מחיר זמינים",
                "details": {}
            }
        
        # חישוב נפח ממוצע
        avg_volume = price_df['volume'].mean()
        current_volume = price_df['volume'].iloc[-1]
        
        # חישוב יחס נפח
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # חישוב ציון
        if volume_ratio > 2:
            score = 90
        elif volume_ratio > 1.5:
            score = 70
        elif volume_ratio > 1.2:
            score = 50
        else:
            score = 30
            
        return {
            "score": score,
            "explanation": f"יחס נפח: {volume_ratio:.2f}x",
            "details": {
                "volume_ratio": volume_ratio,
                "current_volume": current_volume,
                "avg_volume": avg_volume
            }
        }
