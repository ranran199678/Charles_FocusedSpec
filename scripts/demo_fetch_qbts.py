import sys
sys.path.append('.')

from utils.smart_data_manager import smart_data_manager
from utils.data_fetcher import DataFetcher
from utils.fmp_utils import fmp_client


def main():
    symbol = 'QBTS'
    src = None
    df = None

    # 1) נסיון דרך SmartDataManager (מקומי+API משולב)
    try:
        df = smart_data_manager.get_stock_data(symbol, days=180, include_live=True)
        src = 'SmartDataManager'
    except Exception:
        df = None

    # 2) Polygon (אם זמין)
    if df is None or df.empty:
        try:
            df = DataFetcher()._fallback_polygon_prices(symbol, '1day')
            src = 'Polygon'
        except Exception:
            df = None

    # 3) FMP (אם זמין)
    if df is None or df.empty:
        try:
            df = fmp_client.fmp_get_price_ohlcv_df(symbol, verify_ssl=False, limit_days=180)
            src = 'FMP'
        except Exception:
            df = None

    # 4) TwelveData (אם זמין)
    if df is None or df.empty:
        try:
            df = DataFetcher()._fallback_twelve_prices(symbol, '1day')
            src = 'TwelveData'
        except Exception:
            df = None

    print('source:', src)
    if df is None or df.empty:
        print('no data returned')
        return

    try:
        # ודא סדר עמודות סטנדרטי אם קיימות
        cols = [c for c in ['open','high','low','close','volume'] if c in df.columns]
        if cols:
            df = df[cols]
    except Exception:
        pass

    print('rows:', len(df))
    # הדפסה מצומצמת
    try:
        print('head:')
        print(df.head(3).to_string())
        print('tail:')
        print(df.tail(3).to_string())
        # תקציר אחרון
        last = df.iloc[0] if df.index.is_monotonic_decreasing else df.iloc[-1]
        last_ts = df.index[0] if df.index.is_monotonic_decreasing else df.index[-1]
        print('last_bar:', last_ts, {k: float(last[k]) for k in df.columns if k in ['open','high','low','close','volume']})
    except Exception as e:
        print('print_error:', e)


if __name__ == '__main__':
    main()


