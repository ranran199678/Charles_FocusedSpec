# core/volume_tension_meter.py

import numpy as np
import pandas as pd

class VolumeTensionMeter:
    """
    Ultimate Volume Tension Meter – גרסת מחקר/תוכנית עסקית:
    - זיהוי Volume Contraction Pattern (VCP), Squeeze, Spike.
    - ניתוח multi-timeframe (יומי + שבועי).
    - בדיקת cross עם price action (דשדוש, breakout).
    - ציון חכם 1–100, הסבר, פרטי חישוב מלאים.
    """

    def __init__(self, config=None):
        cfg = config or {}
        self.window = cfg.get("window", 20)
        self.squeeze_threshold = cfg.get("squeeze_threshold", 0.25)
        self.expansion_threshold = cfg.get("expansion_threshold", 0.80)
        self.vcp_cycles = cfg.get("vcp_cycles", 3)  # מס' מחזורי התכווצות
        self.vcp_drop = cfg.get("vcp_drop", 0.7)    # ירידה מובהקת (30%)
        self.spike_zscore = cfg.get("spike_zscore", 2.5)
        self.debug = cfg.get("debug", False)

    def detect_vcp(self, volume, cycles=3, drop=0.7):
        """ מזהה כמה גלי התכווצות מחזוריים (VCP) התרחשו לאחרונה """
        lows = []
        last_mean = volume[-self.window:].mean()
        # עבור כל חלון, בדוק האם המחזור ירד ב-30%+ מהשיא בחלון קודם
        idx = len(volume) - self.window * cycles
        if idx < 0: return 0
        for i in range(cycles):
            window_slice = volume[idx + i*self.window : idx + (i+1)*self.window]
            if len(window_slice) < self.window: break
            max_vol = window_slice.max()
            min_vol = window_slice.min()
            if min_vol < max_vol * drop:
                lows.append(True)
            else:
                lows.append(False)
        return sum(lows)

    def detect_spike(self, volume):
        """ מזהה Spike במחזור (Z-score גבוה) """
        if len(volume) < self.window * 2:
            return False, 0
        mean = volume[-self.window*2:-self.window].mean()
        std = volume[-self.window*2:-self.window].std()
        last = volume.iloc[-1]
        zscore = (last - mean) / (std + 1e-8)
        return (zscore > self.spike_zscore), zscore

    def analyze_price_action(self, price_df, window=20):
        """ בדיקת דשדוש/התכווצות תנועה (Tight Range) """
        close = price_df['close']
        high = price_df['high']
        low = price_df['low']
        range_ = (high - low).rolling(window).mean()
        volatility = close.pct_change().rolling(window).std()
        tight = (range_.iloc[-1] < range_.mean()*0.8) and (volatility.iloc[-1] < volatility.mean()*0.8)
        return tight

    def rolling_bandwidth(self, volume):
        rolling_mean = volume.rolling(self.window).mean()
        rolling_std = volume.rolling(self.window).std()
        upper = rolling_mean + 2 * rolling_std
        lower = rolling_mean - 2 * rolling_std
        band_width = (upper - lower) / (rolling_mean + 1e-8)
        return band_width

    def analyze(self, symbol, price_df):
        volume = price_df['volume']
        # 1. בדיקת Squeeze ו-Expansion (Bollinger)
        band_width = self.rolling_bandwidth(volume)
        last_band = band_width.iloc[-1]
        rolling_mean = volume.rolling(self.window).mean()
        last_volume = volume.iloc[-1]

        # 2. בדיקת VCP (שלושה גלי התכווצות)
        vcp_score = self.detect_vcp(volume, cycles=self.vcp_cycles, drop=self.vcp_drop)

        # 3. Spike במחזור (Z-score)
        spike, spike_z = self.detect_spike(volume)

        # 4. בדיקת Price Action – האם דשדוש/טווח צר
        tight_range = self.analyze_price_action(price_df, window=self.window)

        # 5. multi-timeframe (בדיקה שבועית בסיסית)
        weekly_squeeze = False
        try:
            price_df_week = price_df.copy()
            price_df_week['week'] = pd.to_datetime(price_df_week['date']).dt.to_period('W')
            weekly_volume = price_df_week.groupby('week')['volume'].sum()
            weekly_band = self.rolling_bandwidth(weekly_volume)
            weekly_squeeze = (weekly_band.iloc[-1] < self.squeeze_threshold)
        except Exception:
            pass

        details = {
            "last_band_width": float(last_band) if not np.isnan(last_band) else None,
            "last_volume": int(last_volume) if not np.isnan(last_volume) else None,
            "vcp_score": vcp_score,
            "spike": spike,
            "spike_zscore": float(spike_z),
            "tight_range": tight_range,
            "weekly_squeeze": weekly_squeeze,
            "window": self.window,
        }

        # *** דירוג חכם 1-100 ***
        triggers = 0
        reasons = []

        if last_band < self.squeeze_threshold:
            triggers += 1
            reasons.append("Daily volume squeeze")
        if weekly_squeeze:
            triggers += 1
            reasons.append("Weekly volume squeeze")
        if vcp_score >= self.vcp_cycles:
            triggers += 1
            reasons.append(f"VCP: {vcp_score} contraction cycles")
        if spike:
            triggers += 1
            reasons.append(f"Recent volume spike (z={spike_z:.2f})")
        if tight_range:
            triggers += 1
            reasons.append("Tight price range")

        # חישוב ניקוד מדורג
        score = 20  # בסיס
        if triggers >= 4:
            score = 100
        elif triggers == 3:
            score = 85
        elif triggers == 2:
            score = 65
        elif triggers == 1:
            score = 40
        else:
            score = 10

        explanation = ", ".join(reasons) if reasons else "No significant volume contraction or spike detected."

        if self.debug:
            print(f"[VolumeTensionMeter-ULTIMATE] {symbol=} score={score} triggers={triggers} reasons={reasons} details={details}")

        return {
            "score": int(score),
            "explanation": explanation,
            "details": details
        }
