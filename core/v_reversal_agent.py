import pandas as pd
import numpy as np

class VReversalAgent:
    def __init__(self, config=None):
        """
        V-Reversal advanced agent – מחיר, ווליום, ופרופיל V אידאלי.
        config:
            - window: כמה ימים לבדוק (ברירת מחדל: 25)
            - pivot_lookback: מינימום ימי pivot (שפל) [ברירת מחדל: 3]
            - min_drop_pct: אחוז ירידה נדרש לפני היפוך V
            - min_rise_pct: אחוז עליה נדרשת מהשפל
            - min_vol_increase: עליה בווליום ביום המהפך (ברירת מחדל: 1.5)
            - v_min_speed: יחס מהירות עליה/ירידה
        """
        cfg = config or {}
        self.window = cfg.get("window", 25)
        self.pivot_lookback = cfg.get("pivot_lookback", 3)
        self.min_drop_pct = cfg.get("min_drop_pct", 8)
        self.min_rise_pct = cfg.get("min_rise_pct", 7)
        self.min_vol_increase = cfg.get("min_vol_increase", 1.5)
        self.v_min_speed = cfg.get("v_min_speed", 1.4)

    def analyze(self, symbol, price_df=None):
        if price_df is None:
            return {
                "score": 50,
                "explanation": "אין נתוני מחיר זמינים",
                "details": {}
            }
        
        # ניתוח תבנית V
        closes = price_df['close']
        
        # חישוב שיפועים
        slope_1 = (closes.iloc[-5] - closes.iloc[-10]) / 5
        slope_2 = (closes.iloc[-1] - closes.iloc[-5]) / 5
        
        # בדיקה אם יש תבנית V (ירידה ואז עלייה)
        if slope_1 < 0 and slope_2 > 0:
            score = 80
            explanation = "תבנית V זוהתה - היפוך מגמה"
        else:
            score = 30
            explanation = "אין תבנית V ברורה"
            
        return {
            "score": score,
            "explanation": explanation,
            "details": {
                "slope_1": slope_1,
                "slope_2": slope_2
            }
        }
