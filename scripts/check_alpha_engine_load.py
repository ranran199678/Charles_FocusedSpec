import sys
from pprint import pprint
import pandas as pd
import numpy as np
import os


def main():
    # Ensure project root on path
    if '.' not in sys.path:
        sys.path.append('.')

    from core.alpha_score_engine import AlphaScoreEngine

    engine = AlphaScoreEngine()
    loaded = sorted(engine.agents.keys())
    print("loaded_agents:", len(loaded))
    pprint(loaded)

    # Optional: run evaluation preferring real local data, fallback to synthetic
    try:
        df = None
        local_path = os.path.join('data', 'historical_prices', 'daily', 'AAPL.csv.gz')
        if os.path.exists(local_path):
            try:
                raw = pd.read_csv(local_path, compression='infer')
                # normalize columns
                raw.columns = [c.strip().lower() for c in raw.columns]
                if 'date' in raw.columns:
                    raw['date'] = pd.to_datetime(raw['date'])
                    raw = raw.sort_values('date')
                    raw = raw.set_index('date')
                # keep standard columns
                cols = [c for c in ['open','high','low','close','volume'] if c in raw.columns]
                if len(cols) >= 4:
                    df = raw[cols].tail(400).copy()
            except Exception as e:
                print('failed_loading_local_csv:', e)

        if df is None:
            # Fallback to synthetic OHLCV
            dates = pd.date_range(end=pd.Timestamp.today(), periods=200, freq='B')
            base = np.linspace(100, 120, len(dates))
            noise = np.random.normal(0, 1.5, len(dates))
            close = base + noise
            open_ = close + np.random.normal(0, 0.5, len(dates))
            high = np.maximum(open_, close) + np.random.uniform(0, 1.0, len(dates))
            low = np.minimum(open_, close) - np.random.uniform(0, 1.0, len(dates))
            volume = np.random.randint(1_000_000, 2_000_000, len(dates))
            df = pd.DataFrame({
                'open': open_,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume,
            }, index=dates)

        result = engine.evaluate(symbol="AAPL", price_data=df)
        print("evaluation_final_score:", result.get("final_score"))
        print("evaluation_agents_count:", result.get("agents_count"))
    except Exception as e:
        print("evaluation_error:", str(e))


if __name__ == "__main__":
    main()


