import pandas as pd

class VolatilityScoreAgent:
    def __init__(self, config=None):
        self.window = config.get("window", 21) if config else 21  # ברירת מחדל: חודש
        self.scale = config.get("scale", 2.5) if config else 2.5  # קבוע לשקלול ניקוד

    def analyze(self, price_df):
        if price_df is None or len(price_df) < self.window + 1:
            return 1

        # חישוב תשואה יומית
        returns = price_df["close"].pct_change().dropna()
        # סטיית תקן בתשואה בחלון נתון
        recent_vol = returns[-self.window:].std()
        # השוואה לממוצע רב-שנתי (או כל התקופה)
        total_vol = returns.std()

        # ניקוד: תנודתיות יחסית לעבר, סקלת 1–100
        if total_vol == 0:
            score = 1
        else:
            ratio = recent_vol / total_vol
            # קידוד: יחס מעל 1 = תנודתיות גוברת
            score = int(max(1, min(100, 50 + self.scale * (ratio - 1) * 25)))
        return score
