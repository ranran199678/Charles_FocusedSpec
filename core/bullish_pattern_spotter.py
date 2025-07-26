import pandas as pd

class BullishPatternSpotter:
    def __init__(self, config=None):
        pass

    def analyze(self, price_df):
        # דמו: יחס נר אחרון לעומת ממוצע נרות – ציון גבוה לנר חזק
        close = price_df["close"]
        open_ = price_df["open"]
        score = int(((close.iloc[-1] - open_.iloc[-1]) / open_.iloc[-1]) * 200 + 50)
        return max(1, min(100, score))
