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

    def analyze(self, price_df):
        """
        מחזיר ציון 1-100: 100 = V reversal מושלם (מהירות, עוצמה, ווליום, קרבה לתמיכה).
        60-80 = V reversal חזק, 40-59 = תיקון V סביר, 1-30 = אין V.
        """
        df = price_df.copy().reset_index(drop=True)
        if len(df) < self.window + self.pivot_lookback + 3:
            return 1  # לא מספיק נתונים

        recent = df[-self.window:].copy()
        close = recent["close"].values
        vol = recent["volume"].values

        # מציאת נקודת שפל לוקאלית
        piv_idx = np.argmin(close)
        pivot = close[piv_idx]

        # תנאי: השפל לא צמוד לקצה (לפחות pivot_lookback ימים מכל צד)
        if piv_idx < self.pivot_lookback or piv_idx > len(close) - self.pivot_lookback - 1:
            return 1

        # חלק 1: ירידה לפני השפל
        high_before = np.max(close[:piv_idx+1])
        drop_pct = 100 * (high_before - pivot) / high_before if high_before > 0 else 0

        # חלק 2: עלייה אחרי השפל
        high_after = np.max(close[piv_idx:])
        rise_pct = 100 * (high_after - pivot) / pivot if pivot > 0 else 0

        # מהירות: נרות מהשיא לשפל ומהשפל לשיא
        drop_speed = piv_idx
        rise_speed = len(close) - piv_idx - 1
        speed_ratio = (rise_pct / rise_speed) / (drop_pct / drop_speed) if drop_speed > 0 and rise_speed > 0 else 0

        # ווליום ביום היפוך V לעומת ממוצע 10 ימים קודמים
        vol_before = np.mean(vol[max(0, piv_idx-10):piv_idx]) if piv_idx >= 2 else 1
        vol_ratio = vol[piv_idx] / vol_before if vol_before > 0 else 1

        # הצללת נר (V אמיתי = נר היפוך רחב, נר שאחרי עולה)
        reversal_candle = (
            (recent.iloc[piv_idx]["close"] > recent.iloc[piv_idx]["open"]) and
            (recent.iloc[piv_idx+1]["close"] > recent.iloc[piv_idx+1]["open"]) and
            (recent.iloc[piv_idx+1]["close"] > recent.iloc[piv_idx]["close"])
        )

        # תמיכה: האם השפל קרוב לשפל 60 יום/נמוך שנתי
        try:
            low_60d = df["close"][-60:].min()
            support_proximity = abs(pivot - low_60d) / low_60d < 0.03
        except Exception:
            support_proximity = False

        # ניקוד: כל תנאי מוסיף ניקוד – שילוב חוזק V, ווליום, proximity, reversal candle
        score = 1
        if (drop_pct > self.min_drop_pct and rise_pct > self.min_rise_pct and speed_ratio > self.v_min_speed):
            score += 40 + int(min(drop_pct, rise_pct) * min(1.5, speed_ratio))  # חוזק התבנית
            if vol_ratio > self.min_vol_increase:
                score += 20  # ווליום פורץ
            if reversal_candle:
                score += 18
            if support_proximity:
                score += 12
        elif drop_pct > 0.7 * self.min_drop_pct and rise_pct > 0.7 * self.min_rise_pct:
            score += 25 + int(min(drop_pct, rise_pct) * 0.8)

        # Limit score range
        score = int(min(score, 100))
        return score
