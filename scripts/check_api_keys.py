import sys
import os
import requests
sys.path.append('.')

from utils.credentials import APICredentials
from utils.data_fetcher import DataFetcher
from utils.fmp_utils import fmp_client


def exists_label(val):
    return 'קיים' if val else 'חסר'


def test_fmp():
    try:
        df = fmp_client.fmp_get_price_ohlcv_df('AAPL', verify_ssl=False, limit_days=5)
        return df is not None and not df.empty
    except Exception:
        return False


def test_finnhub():
    try:
        df = DataFetcher()._fallback_finnhub_prices('AAPL', '1day')
        return df is not None and not df.empty
    except Exception:
        return False


def test_twelvedata():
    try:
        df = DataFetcher()._fallback_twelve_prices('AAPL', '1day')
        return df is not None and not df.empty
    except Exception:
        return False


def test_polygon():
    try:
        df = DataFetcher()._fallback_polygon_prices('AAPL', '1day')
        return df is not None and not df.empty
    except Exception:
        return False


def test_marketaux():
    try:
        key = APICredentials.get_marketaux_key()
        if not key:
            return None
        url = f"https://api.marketaux.com/v1/news/all?symbols=AAPL&language=en&limit=1&api_token={key}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        return bool(data.get('data'))
    except Exception:
        return False


def test_newsdata():
    try:
        key = APICredentials.get_newsdata_key()
        if not key:
            return None
        url = f"https://newsdata.io/api/1/news?apikey={key}&q=AAPL&language=en&category=business"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        return bool(data.get('results'))
    except Exception:
        return False


def test_twitter():
    try:
        out = DataFetcher().fetch_twitter_news('AAPL', limit=1)
        if out:
            return True
        key = APICredentials.get_twitter_key()
        return None if not key else False
    except Exception:
        return False


def test_reddit():
    try:
        out = DataFetcher().fetch_reddit_posts('AAPL', limit=1)
        return bool(out)
    except Exception:
        return False


def main():
    print("=== בדיקת זמינות מפתחות (.env) ===")
    print(f"FMP_API_KEY: {exists_label(APICredentials.get_fmp_key())}")
    print(f"FINNHUB_API_KEY: {exists_label(APICredentials.get_finnhub_key())}")
    print(f"TWELVE_API_KEY: {exists_label(APICredentials.get_twelve_key())}")
    print(f"MARKETAUX_API_KEY/Marketaux: {exists_label(APICredentials.get_marketaux_key())}")
    print(f"NEWSDATA_API_KEY/NEWS_API: {exists_label(APICredentials.get_newsdata_key())}")
    print(f"POLYGON_API_KEY/Polygon.io: {exists_label(APICredentials.get_polygon_key())}")
    print(f"TWITTER_API_KEY/TWITTER_BEARER_TOKEN/Twitter_API: {exists_label(APICredentials.get_twitter_key())}")
    print(f"REDDIT creds (any): {exists_label(any(APICredentials.get_reddit_credentials().values()))}")
    print(f"OPENAI_API_KEY: {exists_label(APICredentials.get_openai_key())}")

    print("\n=== בדיקות רשת קצרות (אם קיים מפתח) ===")
    print(f"FMP: {'OK' if test_fmp() else 'FAIL'}")
    print(f"Finnhub: {'OK' if test_finnhub() else 'FAIL'}")
    print(f"TwelveData: {'OK' if test_twelvedata() else 'FAIL'}")
    res_marketaux = test_marketaux(); print(f"Marketaux: {'OK' if res_marketaux else ('SKIP' if res_marketaux is None else 'FAIL')}")
    res_newsdata = test_newsdata(); print(f"NewsData: {'OK' if res_newsdata else ('SKIP' if res_newsdata is None else 'FAIL')}")
    print(f"Polygon: {'OK' if test_polygon() else 'FAIL'}")
    tw = test_twitter(); print(f"Twitter: {'OK' if tw else 'SKIP' if tw is None else 'FAIL'}")
    print(f"Reddit: {'OK' if test_reddit() else 'FAIL'} (חיפוש ציבורי)")
    print("OpenAI: בדיקת נוכחות מפתח בלבד (ללא קריאה חיה)")


if __name__ == "__main__":
    main()