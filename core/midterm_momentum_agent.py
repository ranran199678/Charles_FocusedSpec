import pandas as pd

class MidtermMomentumAgent:
    def __init__(self, config=None):
        self.short_period = config.get("short_period", 21) if config else 21   # חודש
        self.long_period = config.get("long_period", 63) if config else 63     # 3 חודשים
        self.weight_short = config.get("weight_short", 0.5) if config else 0.5

    def analyze(self, symbol, price_df=None):
        if price_df is None:
            return {
                "score": 50,
                "explanation": "אין נתוני מחיר זמינים",
                "details": {}
            }
        
        closes = price_df['close']
        
        # חישוב שינויי מחיר
        change_short = (closes.iloc[-1] - closes.iloc[-10]) / closes.iloc[-10] * 100
        change_long = (closes.iloc[-1] - closes.iloc[-20]) / closes.iloc[-20] * 100
        
        # חישוב ציונים
        score_short = max(1, min(100, int(change_short + 50)))
        score_long = max(1, min(100, int(change_long + 50)))
        
        # ציון ממוצע
        score = int((score_short + score_long) / 2)
        
        return {
            "score": score,
            "explanation": f"שינוי קצר: {change_short:.1f}%, שינוי ארוך: {change_long:.1f}%",
            "details": {
                "change_short": change_short,
                "change_long": change_long,
                "score_short": score_short,
                "score_long": score_long
            }
        }
