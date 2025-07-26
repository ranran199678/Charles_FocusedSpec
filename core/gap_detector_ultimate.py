"""
GapDetectorUltimate (Full Research/Production Grade)
-----------------------------------------------------
Agent detects and scores price gaps as early signals of potential breakouts,
with the following features:
- Detects single, multiple, consecutive, and rare gaps (percentile based)
- Analyzes gap direction, magnitude (raw & normalized), volume confirmation,
  trend context (pre/post gap), follow-through, and 'gap & trap' reversals
- Returns full-feature scoring (1-100), feature dictionary, and full event history
- Supports ML feature extraction and graphical visualization for analytics
Based on: 'Early Signs of Large Uptrends in Stocks', business plan, and advanced quant research.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class GapDetectorUltimate:
    def __init__(self, config=None):
        cfg = config or {}
        self.gap_threshold_pct = cfg.get("gap_threshold_pct", 5)
        self.rare_gap_percentile = cfg.get("rare_gap_percentile", 92)
        self.max_gap_days = cfg.get("max_gap_days", 3)
        self.min_volume_ratio = cfg.get("min_volume_ratio", 1.25)
        self.follow_through_days = cfg.get("follow_through_days", 5)
        self.reversal_penalty = cfg.get("reversal_penalty", 0.4)
        self.trend_lookback = cfg.get("trend_lookback", 15)
        self.history_window = cfg.get("history_window", 90)
        self.verbose = cfg.get("verbose", False)

    def _calculate_gap_scores(self, df, verbose=False):
        gap_events = []
        # Historical gap stats for normalization
        historical_gaps = 100 * (df["open"].iloc[1:self.history_window].values - df["close"].iloc[:self.history_window-1].values) / (df["close"].iloc[:self.history_window-1].values + 1e-9)
        rare_gap_thresh = np.percentile(np.abs(historical_gaps), self.rare_gap_percentile)

        for idx in range(1, len(df)):
            prev_close = df.iloc[idx-1]["close"]
            cur_open = df.iloc[idx]["open"]
            cur_close = df.iloc[idx]["close"]
            cur_high = df.iloc[idx]["high"]
            cur_low = df.iloc[idx]["low"]
            cur_vol = df.iloc[idx]["volume"]
            prev_vol = df.iloc[idx-1]["volume"]

            gap_pct = 100 * (cur_open - prev_close) / prev_close

            # Only up-gaps for this agent (modify for down-gap strategy if needed)
            if gap_pct < self.gap_threshold_pct:
                continue

            # Volume confirmation
            avg_vol = df["volume"].iloc[max(0, idx-5):idx].mean() if idx >= 5 else prev_vol
            volume_spike = cur_vol / (avg_vol + 1e-9)

            # Follow-through analysis
            future_closes = df["close"].iloc[idx:min(idx+self.follow_through_days+1, len(df))]
            post_gap_return = ((future_closes.max() - cur_open) / cur_open) * 100 if not future_closes.empty else 0

            # Consecutive gaps check
            cons_gap = 1
            for d in range(1, self.max_gap_days+1):
                if idx-d < 1: break
                prev_gap = 100 * (df.iloc[idx-d]["open"] - df.iloc[idx-d-1]["close"]) / (df.iloc[idx-d-1]["close"] + 1e-9)
                if prev_gap >= self.gap_threshold_pct:
                    cons_gap += 1
                else:
                    break

            # Gap & trap: does price fill the gap soon after?
            gap_filled = 0
            for f in range(1, min(3, len(df)-idx)):
                if df.iloc[idx+f]["low"] < prev_close:
                    gap_filled = 1
                    break

            # Rare gap detection (percentile score)
            gap_rarity = min(1.0, np.abs(gap_pct) / (rare_gap_thresh+1e-9))

            # Trend context (pre-gap and post-gap)
            trend_start = max(0, idx-self.trend_lookback)
            pretrend = (df["close"].iloc[trend_start:idx].mean() - df["close"].iloc[trend_start]) / (df["close"].iloc[trend_start]+1e-9)
            posttrend = (df["close"].iloc[min(len(df)-1, idx+self.follow_through_days)] - cur_open) / (cur_open+1e-9) if idx+self.follow_through_days < len(df) else 0

            # Feature dictionary (for ML, analytics, explainability)
            feat = {
                "date": str(df.iloc[idx].get("date", idx)),
                "gap_pct": gap_pct,
                "gap_rarity": gap_rarity,
                "volume_spike": volume_spike,
                "follow_through_return": post_gap_return,
                "consecutive_gaps": cons_gap,
                "gap_filled": gap_filled,
                "pre_gap_trend": pretrend,
                "post_gap_trend": posttrend,
            }

            # Score composition (all components weighted and explained)
            score = (
                min(gap_pct, 15) / 15 * 30 +                     # Gap magnitude
                gap_rarity * 25 +                                # Rare gaps bonus
                min(1, volume_spike / self.min_volume_ratio) * 15 + # Volume confirmation
                min(1, post_gap_return / 10) * 10 +              # Follow-through (capped at 10%)
                (cons_gap-1)/self.max_gap_days * 10 +            # Consecutive gaps
                (1 if pretrend > 0 else 0) * 5 +                 # Pre-gap uptrend
                (1 if posttrend > 0 else 0) * 5                  # Post-gap uptrend
            )
            if gap_filled: score *= self.reversal_penalty

            feat["score"] = score
            gap_events.append(feat)
            if verbose:
                print(f"Gap@{feat['date']}: gap={gap_pct:.2f}%, rarity={gap_rarity:.2f}, vol_spk={volume_spike:.2f}, post_gap_ret={post_gap_return:.2f}%, cons_gap={cons_gap}, filled={gap_filled}, score={score:.1f}")

        return gap_events

    def analyze(self, symbol, price_df, **kwargs):
        """
        Full gap detection analysis.
        Args:
            symbol: str
            price_df: DataFrame (MUST include: open, close, high, low, volume, [date])
        Returns:
            int: score (1–100), event_features (list of dict)
        """
        if price_df is None or len(price_df) < 20:
            return 1, []

        gap_events = self._calculate_gap_scores(price_df, verbose=self.verbose)
        if not gap_events:
            return 1, []

        # Use max event score (most significant gap), or aggregate as you wish
        final_score = int(max(1, min(100, max(ev["score"] for ev in gap_events))))
        return final_score, gap_events

    def extract_feature_matrix(self, price_df):
        """
        For ML use – returns pd.DataFrame with all feature vectors for detected gaps
        """
        events = self._calculate_gap_scores(price_df)
        return pd.DataFrame(events)

    def plot_gaps(self, price_df, gap_events=None):
        """
        Plots price with detected gaps for visual analytics.
        """
        if gap_events is None:
            _, gap_events = self.analyze("?", price_df)
        plt.figure(figsize=(14, 6))
        plt.plot(price_df["close"].values, label="Close Price")
        gap_idxs = [int(e["date"]) if str(e["date"]).isdigit() else price_df.index.get_loc(pd.to_datetime(e["date"])) for e in gap_events]
        plt.scatter(gap_idxs, price_df["close"].iloc[gap_idxs], color='r', marker='^', s=120, label="Detected Gaps")
        plt.title("Gap Detector Ultimate – Price & Gaps")
        plt.legend()
        plt.show()
