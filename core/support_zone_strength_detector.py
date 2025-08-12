import numpy as np
import pandas as pd
from core.base.base_agent import BaseAgent

def compute_volume_profile(price_df, price_step=0.005):
    lows = price_df['low']
    highs = price_df['high']
    volumes = price_df['volume']
    price_min = lows.min()
    price_max = highs.max()
    bins = np.arange(price_min, price_max + price_step, price_step)
    profile = {b: 0 for b in bins}
    for _, row in price_df.iterrows():
        low, high, vol = row['low'], row['high'], row['volume']
        p_lo = int((low - price_min) / price_step)
        p_hi = int((high - price_min) / price_step)
        for j in range(p_lo, p_hi + 1):
            b = price_min + j * price_step
            if b in profile:
                profile[b] += vol / (p_hi - p_lo + 1)
    pf = pd.DataFrame({'price': list(profile.keys()), 'volume': list(profile.values())})
    return pf

def classify_candle(open_, high, low, close, prev_open=None, prev_close=None):
    body = close - open_
    range_ = high - low
    if range_ == 0:
        return ""
    # Hammer
    if body > 0 and (open_ - low) > 2 * abs(body) and (high - close) < 0.3 * range_:
        return "hammer"
    # Bullish engulfing
    if prev_open is not None and prev_close is not None:
        if (prev_close < prev_open) and (close > open_) and (close > prev_open) and (open_ < prev_close):
            return "bullish_engulfing"
    # Doji
    if abs(close - open_) < 0.1 * range_:
        return "doji"
    return ""

def detect_morning_star(df, idx):
    if idx < 2:
        return False
    o1, c1 = df.iloc[idx - 2]['open'], df.iloc[idx - 2]['close']
    o2, c2 = df.iloc[idx - 1]['open'], df.iloc[idx - 1]['close']
    o3, c3 = df.iloc[idx]['open'], df.iloc[idx]['close']
    cond1 = c1 < o1 and (o2 > c1 or c2 > c1)
    cond2 = abs(c2 - o2) < 0.5 * abs(c1 - o1)
    cond3 = c3 > o3 and c3 > ((c1 + o1) / 2)
    return cond1 and cond2 and cond3

def find_double_bottom(lows, threshold=0.01):
    # מזהה אם יש שני שפל קרובים ברמה דומה
    idxs = lows.nsmallest(2).index.values
    if len(idxs) < 2:
        return False, []
    lvl1, lvl2 = lows.iloc[idxs[0]], lows.iloc[idxs[1]]
    if abs(lvl1 - lvl2) < threshold * ((lvl1 + lvl2) / 2):
        return True, idxs
    return False, []

def find_double_top(highs, threshold=0.01):
    idxs = highs.nlargest(2).index.values
    if len(idxs) < 2:
        return False, []
    lvl1, lvl2 = highs.iloc[idxs[0]], highs.iloc[idxs[1]]
    if abs(lvl1 - lvl2) < threshold * ((lvl1 + lvl2) / 2):
        return True, idxs
    return False, []

class SupportZoneStrengthDetector(BaseAgent):
    def __init__(self, config=None):
        super().__init__(config)
        cfg = config or {}
        self.window = cfg.get("window", 50)
        self.sensitivity = cfg.get("sensitivity", 0.012)
        self.min_touches = cfg.get("min_touches", 2)
        self.profile_radius = cfg.get("profile_radius", 0.012)
        self.min_score = cfg.get("min_score", 30)
        self.debug = cfg.get("debug", False)
        self.plot = cfg.get("plot", False)

    def find_local_minima(self, series):
        # ממחזרים את האינדקס לחלון קטן (reset_index)
        series = series.reset_index(drop=True)
        return series[(series.shift(1) > series) & (series.shift(-1) > series)]

    def find_local_maxima(self, series):
        series = series.reset_index(drop=True)
        return series[(series.shift(1) < series) & (series.shift(-1) < series)]

    def advanced_false_break(self, series, closes, lvl, idxs, is_support=True):
        n = 0
        for i in idxs:
            if i < 0 or i >= len(series):
                continue
            if is_support:
                if series.iloc[i] < lvl * (1 - 2 * self.profile_radius) and closes.iloc[i] > lvl:
                    n += 1
            else:
                if series.iloc[i] > lvl * (1 + 2 * self.profile_radius) and closes.iloc[i] < lvl:
                    n += 1
        return n >= 2

    def analyze(self, symbol, price_df=None):
        """Standard analyze method for AlphaScoreEngine compatibility"""
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=180)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            result = self._analyze_internal(symbol, price_df)
            # Convert the result to the expected format
            if isinstance(result, dict) and "support_zones" in result:
                # Calculate a score based on the zones found
                support_zones = result.get("support_zones", [])
                resistance_zones = result.get("resistance_zones", [])
                
                # Calculate score based on number and strength of zones
                score = 10  # Base score
                if support_zones:
                    avg_support_score = sum(zone.get("score", 0) for zone in support_zones) / len(support_zones)
                    score += min(avg_support_score * 0.3, 40)
                if resistance_zones:
                    avg_resistance_score = sum(zone.get("score", 0) for zone in resistance_zones) / len(resistance_zones)
                    score += min(avg_resistance_score * 0.3, 40)
                
                score = min(int(score), 100)
                
                explanation = f"Found {len(support_zones)} support zones and {len(resistance_zones)} resistance zones"
                
                return {
                    "score": score,
                    "explanation": explanation,
                    "details": result
                }
            else:
                return {
                    "score": 1,
                    "explanation": "Error analyzing support/resistance zones",
                    "details": result
                }
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()

    def _analyze_internal(self, symbol, price_df):
        if price_df.shape[0] < self.window + 10:
            return {"score": 0, "support_zones": [], "resistance_zones": [], "zone_strength": 0, "explanation": "Insufficient data."}

        # reset_index ל־window
        window_df = price_df.iloc[-self.window:].reset_index(drop=True)
        lows = window_df['low']
        closes = window_df['close']
        highs = window_df['high']
        opens = window_df['open']
        volumes = window_df['volume']
        volume_profile = compute_volume_profile(price_df)

        # איתור Double Bottom/Top (כל החלון)
        is_double_bottom, db_idxs = find_double_bottom(lows)
        is_double_top, dt_idxs = find_double_top(highs)

        zones_supp, zones_res = [], []

        # --- Support Zones ---
        support_candidates = self.find_local_minima(lows)
        for lvl in support_candidates.unique():
            if np.isnan(lvl): continue
            mask = (lows >= lvl * (1 - self.profile_radius)) & (lows <= lvl * (1 + self.profile_radius))
            touches = mask.sum()
            if touches < self.min_touches: continue
            idxs = np.where(mask)[0]
            vol_near = volumes.iloc[idxs].mean() if len(idxs) > 0 else 0
            avg_vol = volumes.mean()
            prof_vol = volume_profile[
                (volume_profile['price'] >= lvl * (1 - self.profile_radius)) &
                (volume_profile['price'] <= lvl * (1 + self.profile_radius))
            ]['volume'].sum()
            volume_spike = vol_near > avg_vol * 1.3 or prof_vol > volume_profile['volume'].mean() * 1.5
            idx_last = idxs[-1] if len(idxs) > 0 else None
            price_rebound = None
            if idx_last is not None and (idx_last + 3) < len(window_df):
                after_touch = closes.iloc[idx_last + 1:idx_last + 4]
                rebound = (after_touch.max() - lows.iloc[idx_last]) / lows.iloc[idx_last]
                price_rebound = rebound
            false_break = self.advanced_false_break(lows, closes, lvl, idxs, is_support=True)
            candle_type = ""
            if idx_last is not None:
                i = idx_last
                o, h, l, c = opens.iloc[i], highs.iloc[i], lows.iloc[i], closes.iloc[i]
                prev_o, prev_c = (opens.iloc[i - 1], closes.iloc[i - 1]) if i > 0 else (None, None)
                candle_type = classify_candle(o, h, l, c, prev_o, prev_c)
                if detect_morning_star(window_df, i):
                    candle_type = "morning_star"
            # דפוס Double Bottom
            double_bottom = False
            if is_double_bottom and any((abs(lvl - lows.iloc[j]) < 0.01 * lvl for j in db_idxs if 0 <= j < len(lows))):
                double_bottom = True

            score = 25 if touches > 2 else 10
            if volume_spike: score += 20
            if price_rebound and price_rebound > 0.045: score += 15
            if candle_type in ["hammer", "bullish_engulfing", "doji", "morning_star"]: score += 10
            if false_break: score += 15
            if double_bottom: score += 10
            if score > 100: score = 100

            zones_supp.append({
                "type": "support",
                "level": float(lvl),
                "touches": int(touches),
                "volume_near_zone": int(vol_near),
                "profile_vol": int(prof_vol),
                "volume_spike": bool(volume_spike),
                "price_rebound": float(price_rebound) if price_rebound is not None else None,
                "false_break": bool(false_break),
                "candle": candle_type,
                "double_bottom": double_bottom,
                "score": int(score)
            })

        # --- Resistance Zones ---
        resistance_candidates = self.find_local_maxima(highs)
        for lvl in resistance_candidates.unique():
            if np.isnan(lvl): continue
            mask = (highs >= lvl * (1 - self.profile_radius)) & (highs <= lvl * (1 + self.profile_radius))
            touches = mask.sum()
            if touches < self.min_touches: continue
            idxs = np.where(mask)[0]
            vol_near = volumes.iloc[idxs].mean() if len(idxs) > 0 else 0
            avg_vol = volumes.mean()
            prof_vol = volume_profile[
                (volume_profile['price'] >= lvl * (1 - self.profile_radius)) &
                (volume_profile['price'] <= lvl * (1 + self.profile_radius))
            ]['volume'].sum()
            volume_spike = vol_near > avg_vol * 1.3 or prof_vol > volume_profile['volume'].mean() * 1.5
            idx_last = idxs[-1] if len(idxs) > 0 else None
            price_rebound = None
            if idx_last is not None and (idx_last + 3) < len(window_df):
                after_touch = closes.iloc[idx_last + 1:idx_last + 4]
                rebound = (highs.iloc[idx_last] - after_touch.min()) / highs.iloc[idx_last]
                price_rebound = rebound
            false_break = self.advanced_false_break(highs, closes, lvl, idxs, is_support=False)
            candle_type = ""
            if idx_last is not None:
                i = idx_last
                o, h, l, c = opens.iloc[i], highs.iloc[i], lows.iloc[i], closes.iloc[i]
                prev_o, prev_c = (opens.iloc[i - 1], closes.iloc[i - 1]) if i > 0 else (None, None)
                candle_type = classify_candle(o, h, l, c, prev_o, prev_c)
            # דפוס Double Top
            double_top = False
            if is_double_top and any((abs(lvl - highs.iloc[j]) < 0.01 * lvl for j in dt_idxs if 0 <= j < len(highs))):
                double_top = True

            score = 25 if touches > 2 else 10
            if volume_spike: score += 20
            if price_rebound and price_rebound > 0.045: score += 15
            if candle_type in ["hammer", "bullish_engulfing", "doji"]: score += 10
            if false_break: score += 15
            if double_top: score += 10
            if score > 100: score = 100

            zones_res.append({
                "type": "resistance",
                "level": float(lvl),
                "touches": int(touches),
                "volume_near_zone": int(vol_near),
                "profile_vol": int(prof_vol),
                "volume_spike": bool(volume_spike),
                "price_rebound": float(price_rebound) if price_rebound is not None else None,
                "false_break": bool(false_break),
                "candle": candle_type,
                "double_top": double_top,
                "score": int(score)
            })

        # תצוגה
        df_supp = pd.DataFrame(zones_supp)
        df_res = pd.DataFrame(zones_res)
        min_score = self.min_score

        print("\n--- אזורי תמיכה חזקים (score >= {}) ---".format(min_score))
        if not df_supp.empty:
            print(df_supp.loc[df_supp["score"] >= min_score][["level", "touches", "volume_spike", "candle", "double_bottom", "price_rebound", "false_break", "profile_vol", "score"]])
        else:
            print("No strong support zones.")

        print("\n--- אזורי תמיכה חלשים (score < {}) ---".format(min_score))
        if not df_supp.empty:
            print(df_supp.loc[df_supp["score"] < min_score][["level", "touches", "volume_spike", "candle", "double_bottom", "price_rebound", "false_break", "profile_vol", "score"]])
        else:
            print("No weak support zones.")

        print("\n--- אזורי התנגדות חזקים (score >= {}) ---".format(min_score))
        if not df_res.empty:
            print(df_res.loc[df_res["score"] >= min_score][["level", "touches", "volume_spike", "candle", "double_top", "price_rebound", "false_break", "profile_vol", "score"]])
        else:
            print("No strong resistance zones.")

        print("\n--- אזורי התנגדות חלשים (score < {}) ---".format(min_score))
        if not df_res.empty:
            print(df_res.loc[df_res["score"] < min_score][["level", "touches", "volume_spike", "candle", "double_top", "price_rebound", "false_break", "profile_vol", "score"]])
        else:
            print("No weak resistance zones.")

        # plot both
        if self.plot:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(12, 6))
            plt.plot(price_df["date"], price_df["close"], label="Close")
            for _, z in df_supp.loc[df_supp["score"] >= min_score].iterrows():
                plt.axhline(z["level"], color='g', linestyle="--", alpha=0.6, label=f"Support {z['level']:.2f} (score {z['score']})")
                if z["volume_spike"]:
                    plt.scatter(price_df["date"].iloc[-self.window:], [z["level"]] * self.window, marker='v', color='green', s=30, label=f"Spike {z['level']:.2f}")
                if z["candle"] in ["hammer", "bullish_engulfing", "doji", "morning_star"]:
                    plt.scatter(price_df["date"].iloc[-self.window:], [z["level"]] * self.window, marker='*', color='yellow', s=40, label=f"{z['candle']} @ {z['level']:.2f}")
            for _, z in df_res.loc[df_res["score"] >= min_score].iterrows():
                plt.axhline(z["level"], color='r', linestyle="--", alpha=0.6, label=f"Resistance {z['level']:.2f} (score {z['score']})")
            plt.title(f"Support/Resistance Zones for {symbol}")
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.legend()
            plt.tight_layout()
            plt.show()

        return {
            "support_zones": zones_supp,
            "resistance_zones": zones_res
        }
