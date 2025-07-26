import pandas as pd

class VWAPTrendAgent:
    def __init__(self, config=None):
        """
        config: 
            {
                "anchored_event_index": None/מספר (למשל יום דוח),
                "weight_sync": 0.7,   # משקל לפריצה מסונכרנת
                "weight_avwap": 0.3   # משקל לפריצה לעומת anchored vwap
            }
        """
        cfg = config or {}
        self.anchor_idx = cfg.get("anchored_event_index", None)
        self.weight_sync = cfg.get("weight_sync", 0.7)
        self.weight_avwap = cfg.get("weight_avwap", 0.3)

    def _calc_vwap(self, price_df, window):
        price = price_df["close"].iloc[-window:]
        volume = price_df["volume"].iloc[-window:]
        vwap = (price * volume).cumsum() / volume.cumsum()
        # הסדרה תתחיל עם Nan עבור קנדלים קודמים
        full_vwap = pd.Series([None]*(len(price_df)-window) + list(vwap), index=price_df.index)
        return full_vwap

    def _calc_anchored_vwap(self, price_df, anchor_idx):
        # מחושב מהנקודה המוגדרת (למשל יום דוח)
        volume = price_df["volume"].iloc[anchor_idx:]
        pv = (price_df["close"].iloc[anchor_idx:] * volume).cumsum()
        cum_vol = volume.cumsum()
        avwap = pv / cum_vol
        result = pd.Series([None]*anchor_idx + list(avwap), index=price_df.index)
        return result

    def analyze(self, price_df):
        """
        מחזיר ציון 1-100: 
        - 100 = פריצה מתואמת בו זמנית של VWAP יומי/שבועי/חודשי + המחיר מעל Anchored VWAP
        - 1 = מתחת לכולם, או תבנית שלילית (למשל rejection חזק מכל VWAP)
        """
        n = len(price_df)
        if n < 21:
            return 1  # לא מספיק נתונים

        # חישוב VWAP בכמה טווחים (קביעת חלונות לדוגמה)
        vwap_daily   = self._calc_vwap(price_df, window=1)
        vwap_weekly  = self._calc_vwap(price_df, window=5)
        vwap_monthly = self._calc_vwap(price_df, window=21)

        # Anchored VWAP (נק' דוח/שפל/אירוע)
        avwap = None
        if self.anchor_idx is not None and self.anchor_idx < n:
            avwap = self._calc_anchored_vwap(price_df, self.anchor_idx)
        last_idx = price_df.index[-1]

        price = price_df["close"].iloc[-1]

        # סיגנל: המחיר מעל כל VWAP (sync breakout)
        vwap_sync_break = (
            price > vwap_daily.iloc[-1] and 
            price > vwap_weekly.iloc[-1] and 
            price > vwap_monthly.iloc[-1]
        )

        # סיגנל Anchored (אם יש נק' עיגון)
        avwap_signal = False
        if avwap is not None and avwap.iloc[-1] is not None:
            avwap_signal = price > avwap.iloc[-1]
        
        # מדד איכות/רמת breakout: אפשר לכייל גם לפי כמה רחוק מה-vwap
        sync_score = 100 if vwap_sync_break else max(1, int(100 * ((price - min(vwap_daily.iloc[-1], vwap_weekly.iloc[-1], vwap_monthly.iloc[-1])) / price))
        avwap_score = 100 if avwap_signal else 30 if avwap is not None else 1

        # משקלול
        total_score = int(self.weight_sync * sync_score + self.weight_avwap * avwap_score)
        return max(1, min(total_score, 100))

