from core.breakout_retest_recognizer import BreakoutRetestRecognizer
from utils import data_fetcher
import time

tickers = [
    "SMCI", "NVDA", "META", "CELH", "TSLA", "ARM", "CAVA", "UBER",
    "AMD", "AVGO", "AAPL", "GOOG", "SHOP", "MSTR", "COIN", "DKNG",
    "NFLX", "PLTR", "CRWD", "TSM", "AMZN", "SOUN", "RIVN", "AI"
]

MIN_SCORE = 60
DAYS_AFTER_SIGNAL = 5   # בכמה ימים קדימה למדוד תשואה

agent = BreakoutRetestRecognizer({
    "breakout_window": 15,
    "min_breakout_volume_ratio": 1.1,
    "gap_percent": 0.0,
    "momentum_return": 0.2,
    "momentum_window": 7,
    "momentum_volume_ratio": 1.1
})

results = []

for symbol in tickers:
    try:
        price_df = data_fetcher.get_price_history(symbol, period="9mo")
        result = agent.analyze(symbol, price_df)
        if result["score"] >= MIN_SCORE:
            details = result["details"]
            # זיהוי breakout/momentum
            signal_type = None
            idx_signal = None
            price_signal = None
            date_signal = None

            # Breakout קלאסי
            for k, v in details.items():
                if k.startswith("breakout_") and v.get("breakout"):
                    idx_signal = v["breakout"]["idx"]
                    price_signal = v["breakout"]["price"]
                    date_signal = price_df.iloc[idx_signal]["date"]
                    signal_type = "Breakout"
                    break
            # Momentum breakout (אם אין קלאסי)
            if details.get("momentum_breakout"):
                idx_signal = price_df.index[-1]
                price_signal = price_df.iloc[-1]["close"]
                date_signal = price_df.iloc[-1]["date"]
                signal_type = "Momentum"

            # חישוב תשואה N ימים אחרי האיתות
            price_after = None
            ret_after = None
            if idx_signal is not None and (idx_signal + DAYS_AFTER_SIGNAL) < len(price_df):
                price_after = price_df.iloc[idx_signal + DAYS_AFTER_SIGNAL]["close"]
                ret_after = (price_after - price_signal) / price_signal * 100
            # Spike בנפח
            avg_vol = price_df['volume'].mean()
            vol_signal = price_df.iloc[idx_signal]["volume"] if idx_signal is not None else None
            volume_spike = vol_signal > avg_vol * 1.5 if vol_signal is not None else False

            results.append({
                "symbol": symbol,
                "score": result["score"],
                "signal_type": signal_type,
                "date": date_signal,
                "price": price_signal,
                "ret_after": round(ret_after, 2) if ret_after is not None else None,
                "volume_spike": volume_spike,
                "reason": result["explanation"].split(",")[0]
            })
        print(f"{symbol}: score={result['score']} | {result['explanation']}")
    except Exception as e:
        print(f"Error for {symbol}: {e}")
    time.sleep(1)

print(f"\n--- SIGNAL SUMMARY ({DAYS_AFTER_SIGNAL} days after signal) ---")
print("symbol | score | type | date | price | ret_after_% | vol_spike | reason")
for r in results:
    print(f"{r['symbol']} | {r['score']} | {r['signal_type']} | {r['date']} | {r['price']} | {r['ret_after']}% | {r['volume_spike']} | {r['reason']}")
