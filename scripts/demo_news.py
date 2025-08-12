import sys
sys.path.append('.')

from utils.data_fetcher import DataFetcher
from utils.smart_data_manager import smart_data_manager
import pandas as pd
from datetime import datetime


def main():
    symbol = (sys.argv[1] if len(sys.argv) > 1 else 'AAPL').upper()
    df = DataFetcher()

    print(f'=== news for {symbol} ===')
    res = df.fetch_news_batch([symbol], limit=5)
    items = res.get(symbol, []) if isinstance(res, dict) else []
    print('batch_count:', len(items))
    for i, it in enumerate(items[:5], 1):
        sent = it.get('sentiment', {})
        print(f"{i}. [{it.get('source','n/a')}] {it.get('title','')[:100]} | {sent.get('label','n/a')}:{sent.get('score',0.0)}")

    res2 = df.fetch_enhanced_news_batch([symbol], limit=5)
    items2 = res2.get(symbol, []) if isinstance(res2, dict) else []
    print('enhanced_count:', len(items2))
    for i, it in enumerate(items2[:5], 1):
        sent = it.get('sentiment', {})
        print(f"E{i}. [{it.get('source','n/a')}] {it.get('title','')[:100]} | {sent.get('label','n/a')}:{sent.get('score',0.0)}")

    # save
    try:
        all_items = items2 or items
        rows = []
        for it in all_items:
            sent = it.get('sentiment', {}) if isinstance(it.get('sentiment'), dict) else {}
            rows.append({
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'symbol': symbol,
                'headline': it.get('title', ''),
                'summary': it.get('summary', ''),
                'source': it.get('source', 'unknown'),
                'sentiment_label': sent.get('label', ''),
                'sentiment_score': sent.get('score', 0.0)
            })
        if rows:
            news_df = pd.DataFrame(rows)
            smart_data_manager._save_news_data(symbol, news_df)
            print('saved_to:', f'data/news_sentiment/financial_news/{symbol}.csv.gz')
    except Exception as e:
        print('save_error:', e)


if __name__ == '__main__':
    main()


