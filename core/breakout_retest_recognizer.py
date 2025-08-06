import numpy as np
import pandas as pd
from core.base.base_agent import BaseAgent

class BreakoutRetestRecognizer(BaseAgent):
    def __init__(self, symbol=None, config=None):
        super().__init__(config)
        self.symbol = symbol
        cfg = config or {}
        self.lookback = cfg.get("lookback", 120)
        self.breakout_window = cfg.get("breakout_window", 10)
        self.retest_window = cfg.get("retest_window", 10)
        self.min_breakout_volume_ratio = cfg.get("min_breakout_volume_ratio", 1.5)
        self.gap_percent = cfg.get("gap_percent", 0.015)
        self.retest_margin = cfg.get("retest_margin", 0.02)
        self.success_return = cfg.get("success_return", 0.05)
        self.momentum_window = cfg.get("momentum_window", 7)
        self.momentum_return = cfg.get("momentum_return", 0.3)
        self.momentum_volume_ratio = cfg.get("momentum_volume_ratio", 1.5)
        self.debug = cfg.get("debug", False)

    def get_major_highs(self, highs, window, num=2):
        sorted_highs = highs[-window-1:-1].sort_values(ascending=False).unique()
        return sorted_highs[:num]

    def detect_breakouts(self, df, major_high, window, gap_percent, min_breakout_volume_ratio):
        closes = df['close']
        highs = df['high']
        lows = df['low']
        volumes = df['volume']
        breakouts = []
        avg_volume = volumes.rolling(window=20, min_periods=1).mean()
        for i in range(-window, 0):
            if closes.iloc[i] > major_high and highs.iloc[i] > major_high:
                prev_close = closes.iloc[i-1] if i-1 >= -len(df) else closes.iloc[0]
                gap = (closes.iloc[i] - prev_close) / (prev_close + 1e-8)
                is_gap = gap > gap_percent
                is_high_vol = volumes.iloc[i] > avg_volume.iloc[i] * min_breakout_volume_ratio
                breakouts.append({
                    "idx": i,
                    "price": float(closes.iloc[i]),
                    "volume": float(volumes.iloc[i]),
                    "is_gap": bool(is_gap),
                    "is_high_vol": bool(is_high_vol),
                    "gap_percent": float(gap),
                })
        return breakouts

    def detect_retest(self, df, breakout, margin=0.02, window=10):
        closes = df['close']
        lows = df['low']
        idx = breakout["idx"]
        price = breakout["price"]
        retest_range = (price * (1 - margin), price * (1 + margin))
        for j in range(idx+1, idx+1+window):
            if j >= len(closes): break
            if retest_range[0] <= lows.iloc[j] <= retest_range[1]:
                support_held = closes.iloc[j] >= price * 0.99
                return True, support_held, j
        return False, False, None

    def pattern_before_breakout(self, df, idx, pattern_window=15):
        if idx - pattern_window < 0:
            return False, None
        closes = df['close'].iloc[idx-pattern_window:idx]
        highs = df['high'].iloc[idx-pattern_window:idx]
        lows = df['low'].iloc[idx-pattern_window:idx]
        flag = ((highs.max() - lows.min()) / closes.mean()) < 0.07
        if flag:
            return True, "Flag/Consolidation"
        is_triangle = (highs.diff().mean() < 0) and (lows.diff().mean() > 0)
        if is_triangle:
            return True, "Triangle"
        return False, None

    def momentum_after_breakout(self, df, breakout, window=10, success_return=0.05):
        closes = df['close']
        idx = breakout["idx"]
        if idx+window >= len(closes): return False, 0
        ret = (closes.iloc[idx+window] - closes.iloc[idx]) / closes.iloc[idx]
        return ret > success_return, ret

    def false_breakout(self, df, breakout, major_high, window=10):
        lows = df['low']
        idx = breakout["idx"]
        after_lows = lows.iloc[idx+1:idx+1+window]
        return (after_lows < major_high).any()

    def volume_profile(self, df, price, window=60, band=0.03):
        price_range = (price * (1 - band), price * (1 + band))
        sel = df[(df['close'] >= price_range[0]) & (df['close'] <= price_range[1])]
        total_vol = df['volume'][-window:].sum()
        band_vol = sel['volume'].sum()
        if total_vol == 0: return 0
        return band_vol / total_vol

    def analyze_weekly(self, df):
        df_w = df.copy()
        df_w['week'] = pd.to_datetime(df_w['date']).dt.to_period('W')
        grouped = df_w.groupby('week').agg({'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}).reset_index()
        high = grouped['high'][-30:-7].max()
        breakouts = (grouped['close'][-7:] > high).sum()
        return breakouts

    def analyze(self, symbol, price_df=None):
        """Standard analyze method for AlphaScoreEngine compatibility"""
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=180)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            self.symbol = symbol
            return self._analyze_internal(price_df)
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()

    def _analyze_internal(self, df):
        df = df[-self.lookback:].reset_index(drop=True).copy()
        details = {}
        triggers = 0
        reasons = []
        patterns = []

        major_highs = self.get_major_highs(df['high'], self.lookback-self.breakout_window, num=2)
        details["major_highs"] = [float(h) for h in major_highs]
        all_breakouts = []
        for high in major_highs:
            b_list = self.detect_breakouts(df, high, self.breakout_window, self.gap_percent, self.min_breakout_volume_ratio)
            for b in b_list:
                b["major_high"] = float(high)
                all_breakouts.append(b)
        details["all_breakouts"] = all_breakouts

        successful_breakouts = 0
        best_score = 10
        for b in all_breakouts:
            pattern_flag, pattern_name = self.pattern_before_breakout(df, b["idx"])
            if pattern_flag:
                triggers += 1
                reasons.append(f"{pattern_name} before breakout")
                patterns.append(pattern_name)
            retest_found, retest_held, retest_idx = self.detect_retest(df, b, self.retest_margin, self.retest_window)
            details_key = f"breakout_{b['idx']}"
            details[details_key] = {
                "breakout": b,
                "pattern": pattern_name,
                "retest_found": retest_found,
                "retest_held": retest_held,
                "retest_idx": retest_idx,
            }
            if b["is_gap"]:
                triggers += 1
                reasons.append("Gap breakout")
            if b["is_high_vol"]:
                triggers += 1
                reasons.append("Breakout on high volume")
            if retest_found:
                triggers += 1
                reasons.append("Retest found")
                if retest_held:
                    triggers += 1
                    reasons.append("Retest support held")
            is_false = self.false_breakout(df, b, b["major_high"], self.retest_window)
            if not is_false:
                triggers += 1
                reasons.append("No false breakout after event")
            good_momentum, mret = self.momentum_after_breakout(df, b, self.retest_window, self.success_return)
            details[details_key]["momentum"] = mret
            if good_momentum:
                triggers += 1
                reasons.append(f"Strong momentum: {mret:.1%} return after breakout")
                successful_breakouts += 1
            profile_ratio = self.volume_profile(df, b["price"])
            details[details_key]["profile_ratio"] = profile_ratio
            if profile_ratio > 0.12:
                triggers += 1
                reasons.append("High volume concentration around breakout")
            event_score = 10 + triggers*15
            if event_score > best_score:
                best_score = event_score
            triggers = 0

        # ✅ תיקון עמודת date לפני ניתוח weekly
        if 'date' not in df.columns:
            df['date'] = df.index

        try:
            weekly_breakouts = self.analyze_weekly(df)
            details["weekly_breakouts"] = int(weekly_breakouts)
            if weekly_breakouts > 0:
                best_score = min(best_score+10, 100)
                reasons.append("Weekly breakout detected")
        except Exception as e:
            details["weekly_breakouts"] = "Error: " + str(e)

        details["successful_breakouts"] = successful_breakouts
        details["total_breakouts"] = len(all_breakouts)

        recent_closes = df['close'].tail(self.momentum_window)
        recent_vols = df['volume'].tail(self.momentum_window)
        mom_return = (recent_closes.iloc[-1] - recent_closes.iloc[0]) / (recent_closes.iloc[0] + 1e-8)
        avg_recent_vol = recent_vols.mean()
        avg_vol_all = df['volume'].mean()
        momentum_breakout = False
        mom_score = 0
        if mom_return > self.momentum_return and avg_recent_vol > avg_vol_all * self.momentum_volume_ratio:
            momentum_breakout = True
            mom_score = min(int(mom_return * 180), 95)
            reasons.append(f"Momentum breakout: {mom_return*100:.1f}% in {self.momentum_window} days")
            best_score = max(best_score, mom_score)
        details["momentum_breakout"] = momentum_breakout
        details["momentum_return"] = mom_return
        details["momentum_avg_recent_vol"] = avg_recent_vol

        best_score = max(min(int(best_score), 100), 10)
        explanation = f"{successful_breakouts}/{len(all_breakouts)} breakout(s) with strong signals. " + ", ".join(reasons) \
            if all_breakouts or momentum_breakout else "No significant breakout detected."

        if self.debug:
            print(f"[BreakoutRetestRecognizer] {self.symbol=} score={best_score} details={details}")

        return {
            "symbol": self.symbol,
            "score": best_score,
            "explanation": explanation,
            "details": details
        }

    def run(self, price_df):
        return self.analyze(price_df)

    def run_live(self, price_df):
        return self.analyze(price_df)
