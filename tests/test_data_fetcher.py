# tests/test_data_fetcher.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_fetcher import DataFetcher

fetcher = DataFetcher()
symbols = ["AAPL", "TSLA"]

# בדיקה: טעינת מחירי סגירה ונפח עם fallback
print("--- מחירים (Price Batch) ---")
try:
    price_data = fetcher.fetch(symbols, datatype="price")
    for symbol, df in price_data.items():
        print(f"\n📊 {symbol}:\n{df.tail() if df is not None else '❌ No data'}")
except Exception as e:
    print(f"שגיאה במחירים: {e}")

# בדיקה: נתונים פונדמנטליים
print("\n--- פונדמנטלי (Fundamentals Batch) ---")
try:
    fundamentals_data = fetcher.fetch(symbols, datatype="fundamentals")
    for symbol, data in fundamentals_data.items():
        print(f"\n🧾 {symbol}:\n{data if data else '❌ No data'}")
except Exception as e:
    print(f"שגיאה בפונדמנטלי: {e}")

# בדיקה: חדשות מדומות
print("\n--- חדשות (News Batch) ---")
try:
    news_data = fetcher.fetch(symbols, datatype="news")
    for symbol, news_list in news_data.items():
        print(f"\n📰 {symbol}:")
        for item in news_list:
            print(f"- {item['title']}")
except Exception as e:
    print(f"שגיאה בחדשות: {e}")

# בדיקה: סיכום טקסט
print("\n--- סיכום טקסט (OpenAI) ---")
try:
    text = "Apple stock surges after earnings beat expectations and iPhone demand remains strong."
    summary = fetcher.summarize_text(text)
    print(f"✍️ סיכום:\n{summary}")
except Exception as e:
    print(f"שגיאה בסיכום: {e}")
