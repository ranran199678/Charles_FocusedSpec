import sys
sys.path.append('.')

from utils.data_fetcher import DataFetcher
from utils.smart_data_manager import smart_data_manager
import pandas as pd
from datetime import datetime


def main():
    symbol = 'QBTS'
    df = DataFetcher()

    print('=== fetch_news_batch (עם מקורות מורחבים) ===')
    try:
        res = df.fetch_news_batch([symbol], limit=5)
        items = res.get(symbol, []) if isinstance(res, dict) else []
        print('count:', len(items))
        for i, it in enumerate(items[:5], 1):
            title = it.get('title', '')
            source = it.get('source', 'n/a')
            sent = it.get('sentiment', {})
            label = sent.get('label', 'n/a') if isinstance(sent, dict) else str(sent)
            score = sent.get('score', 0.0) if isinstance(sent, dict) else 0.0
            print(f"{i}. [{source}] {title[:120]} | sentiment={label}:{score}")
    except Exception as e:
        print('error_fetch_news_batch:', e)

    print('\n=== fetch_enhanced_news_batch (סינון ואיכות) ===')
    try:
        res2 = df.fetch_enhanced_news_batch([symbol], limit=5)
        items2 = res2.get(symbol, []) if isinstance(res2, dict) else []
        print('count:', len(items2))
        for i, it in enumerate(items2[:5], 1):
            title = it.get('title', '')
            source = it.get('source', 'n/a')
            sent = it.get('sentiment', {})
            label = sent.get('label', 'n/a') if isinstance(sent, dict) else str(sent)
            score = sent.get('score', 0.0) if isinstance(sent, dict) else 0.0
            print(f"{i}. [{source}] {title[:120]} | sentiment={label}:{score}")
    except Exception as e:
        print('error_fetch_enhanced_news_batch:', e)

    # שמירה לקובץ אחיד תחת data/news_sentiment/financial_news/QBTS.csv.gz
    try:
        all_items = items2 if 'items2' in locals() and items2 else items
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
        else:
            print('no_rows_to_save')
    except Exception as e:
        print('save_error:', e)


if __name__ == '__main__':
    main()


