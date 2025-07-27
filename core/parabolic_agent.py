# core/parabolic_agent.py

import numpy as np
import pandas as pd

class ParabolicAgent:
    """
    Parabolic Move Detector – גרסת על (מחקר/עסקי)
    מזהה תנועות פראבוליות חדות (run up, climax), בדגש על זוית, רצף, Convexity, נפח.
    """
    def __init__(self, config=None):
        cfg = config or {}
        self.min_days = cfg.get("min_days", 5)  # מינימום ימים לפריצה
        self.max_window = cfg.get("max_window", 30)
        self.convexity_threshold = cfg.get("convexity_threshold", 1.2)  # יחס עקום
        self.angle_threshold = cfg.get("angle_threshold", 65)  # מעלות מינימום
        self.volume_spike_zscore = cfg.get("volume_spike_zscore", 2)
        self.debug = cfg.get("debug", False)

    def _calc_angle(self, closes):
        # חישוב זוית התנועה בגרף log (דינמיקה אמיתית)
        y = np.log(closes.values)
        x = np.arange(len(closes))
        slope = np.polyfit(x, y, 1)[0]
        angle = np.degrees(np.arctan(slope))
        return angle

    def _calc_convexity(self, closes):
        # חישוב קמוריות (convexity) של התנועה
        x = np.arange(len(closes))
        y = closes.values
        coeffs = np.polyfit(x, y, 2)
        convexity = coeffs[0]
        return convexity

    def detect_parabolic_run(self, price_df):
        closes = price_df['close'][-self.max_window:]
        highs = price_df['high'][-self.max_window:]
        lows = price_df['low'][-self.max_window:]
        volumes = price_df['volume'][-self.max_window:]

        # 1. בדוק כמה ימים ברצף עלייה (streak)
        streak = 0
        for i in range(1, len(closes)):
            if closes.iloc[-i] > closes.iloc[-i-1]:
                streak += 1
            else:
                break

        # 2. זוית כללית ב-log scale
        angle = self._calc_angle(closes)
        # 3. קמוריות
        convexity = self._calc_convexity(closes)
        # 4. סף סגולי – קפיצה מינ' ב-X ימים
        price_return = closes.iloc[-1] / closes.iloc[0] - 1
        # 5. Spike במחזור (ימים אחרונים)
        vol = volumes[-self.min_days:]
        mean_vol = volumes[:-self.min_days].mean() if len(volumes) > self.min_days else volumes.mean()
        std_vol = volumes[:-self.min_days].std() if len(volumes) > self.min_days else volumes.std()
        spike_z = (vol.mean() - mean_vol) / (std_vol + 1e-8)
        volume_spike = spike_z > self.volume_spike_zscore

        # סף מחקרי – כל התנאים יחד מעידים על ריצה פראבולית
        triggers = 0
        reasons = []

        if streak >= self.min_days:
            triggers += 1
            reasons.append(f"{streak} days up")
        if angle > self.angle_threshold:
            triggers += 1
            reasons.append(f"Sharp angle {angle:.1f}°")
        if abs(convexity) > self.convexity_threshold:
            triggers += 1
            reasons.append(f"Strong convexity {convexity:.2f}")
        if price_return > 0.20:  # לפחות 20% עלייה בחלון קצר
            triggers += 1
            reasons.append(f"{price_return*100:.1f}% return")
        if volume_spike:
            triggers += 1
            reasons.append(f"Volume spike z={spike_z:.2f}")

        details = {
            "streak": streak,
            "angle": angle,
            "convexity": convexity,
            "price_return": price_return,
            "volume_spike_z": spike_z,
            "volume_spike": volume_spike,
            "max_window": self.max_window
        }

        # דירוג 1–100: כל טריגר חזק – ציון גבוה, רק עם כל התנאים = 100
        score = 20
        if triggers >= 4:
            score = 100
        elif triggers == 3:
            score = 80
        elif triggers == 2:
            score = 60
        elif triggers == 1:
            score = 40

        explanation = ", ".join(reasons) if reasons else "No strong parabolic move detected."

        if self.debug:
            print(f"[ParabolicAgent-ULT] score={score}, triggers={triggers}, reasons={reasons}, details={details}")

        return score, explanation, details

    def analyze(self, symbol, price_df=None):
        try:
            score, explanation, details = self.detect_parabolic_run(price_df)
        except Exception as e:
            return {
                "score": 1,
                "explanation": f"Error: {e}",
                "details": {}
            }
        return {
            "score": int(score),
            "explanation": explanation,
            "details": details
        }
