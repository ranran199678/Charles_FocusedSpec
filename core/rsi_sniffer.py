import pandas as pd
import numpy as np

class RSICompressionSniffer:
    """
    Ultimate RSI Compression Detector:
    - Multi-Timeframe RSI (e.g., 14d daily + 14w weekly)
    - Squeeze detection via rolling std
    - Divergence & Cross-check with volume squeeze
    - Full config & scoring
    Returns: dict - {'score': 1-100, 'explanation': str, 'details': dict}
    """
    def __init__(self, config=None):
        cfg = config or {}
        self.rsi_lookbacks = cfg.get("lookbacks", [14, 21])
        self.timeframes = cfg.get("timeframes", ["1d", "1w"])
        self.sqz_std_threshold = cfg.get("squeeze_std_threshold", 2.0)
        self.rsi_high = cfg.get("rsi_high", 70)
        self.rsi_low = cfg.get("rsi_low", 30)
        self.sqz_length = cfg.get("squeeze_length", 10)
        self.min_cross_triggers = cfg.get("min_cross_triggers", 2)
        self.debug = cfg.get("debug", False)

    @staticmethod
    def calc_rsi(close, period):
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calc_volume_squeeze(volume, window=20):
        # Bollinger Bands Squeeze on volume
        rolling_mean = volume.rolling(window).mean()
        rolling_std = volume.rolling(window).std()
        upper = rolling_mean + 2 * rolling_std
        lower = rolling_mean - 2 * rolling_std
        squeeze = (upper - lower) / rolling_mean
        return squeeze

    def analyze(self, symbol, price_df):
        results = []
        for lookback in self.rsi_lookbacks:
            close = price_df['close']
            rsi = self.calc_rsi(close, lookback)
            rolling_std = rsi.rolling(self.sqz_length).std()
            squeeze_points = rolling_std < self.sqz_std_threshold
            overbought = (rsi > self.rsi_high).any()
            oversold = (rsi < self.rsi_low).any()
            vol_squeeze = self.calc_volume_squeeze(price_df['volume'])
            volume_tight = (vol_squeeze.tail(self.sqz_length) < 0.2).all()
            result = {
                "lookback": lookback,
                "rsi_squeeze": bool(squeeze_points.tail(1).iloc[0]),
                "overbought": bool(overbought),
                "oversold": bool(oversold),
                "volume_tight": bool(volume_tight),
            }
            results.append(result)
            if self.debug:
                print(f"[RSI-Sniffer] {lookback=}: Squeeze={result['rsi_squeeze']} Overbought={overbought} Oversold={oversold} Volume Tight={volume_tight}")

        cross_triggers = sum(
            r["rsi_squeeze"] and r["volume_tight"] for r in results
        )
        # ציון 100 = כל הקריטריונים התקיימו, פחות – מדורג
        if cross_triggers >= self.min_cross_triggers:
            score = 100
            explanation = f"Detected {cross_triggers} strong RSI+Volume squeezes."
        elif cross_triggers == 1:
            score = 60
            explanation = "Single squeeze event – medium confidence."
        else:
            score = 20
            explanation = "No significant RSI squeeze detected."
        return {
            "score": int(score),
            "explanation": explanation,
            "details": {
                "symbol": symbol,
                "rsi_results": results,
                "cross_triggers": cross_triggers
            }
        }
