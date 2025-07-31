import sys
sys.path.append('.')

from utils.data_fetcher import DataFetcher

# בדיקת המקורות החדשים
symbol = "INTC"

print(f"=== בדיקת מקורות חדשות מתקדמים עבור {symbol} ===")

data_fetcher = DataFetcher()

print(f"\n=== 1. MarketAux (מקור ראשי) ===")
try:
    marketaux_key = "Dx8X1gzfxklRC5WETItJAncifB4bXp98EnSqzT6P"
    url = f"https://api.marketaux.com/v1/news/all?symbols={symbol}&language=en&limit=5&api_token={marketaux_key}"
    response = data_fetcher._safe_request(url)
    
    if response.get("data"):
        articles = response["data"]
        print(f"נמצאו {len(articles)} מאמרים:")
        for i, article in enumerate(articles, 1):
            title = article.get("title", "")
            source = article.get("source", "Unknown")
            sentiment = article.get("sentiment", "neutral")
            relevance = data_fetcher._calculate_news_relevance(title, article.get("description", ""), symbol)
            
            print(f"{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   סנטימנט: {sentiment}")
            print(f"   רלוונטיות: {relevance:.2f}")
    else:
        print("לא נמצאו מאמרים")
except Exception as e:
    print(f"שגיאה: {e}")

print(f"\n=== 2. Alpha Vantage News ===")
try:
    alpha_articles = data_fetcher.fetch_alpha_vantage_news(symbol, 3)
    if alpha_articles:
        print(f"נמצאו {len(alpha_articles)} מאמרים:")
        for i, article in enumerate(alpha_articles, 1):
            title = article.get("title", "")
            source = article.get("source", "Unknown")
            sentiment = article.get("sentiment", "neutral")
            relevance = data_fetcher._calculate_news_relevance(title, article.get("summary", ""), symbol)
            
            print(f"{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   סנטימנט: {sentiment}")
            print(f"   רלוונטיות: {relevance:.2f}")
    else:
        print("לא נמצאו מאמרים (אולי אין API key)")
except Exception as e:
    print(f"שגיאה: {e}")

print(f"\n=== 3. Finnhub News ===")
try:
    finnhub_articles = data_fetcher.fetch_finnhub_news(symbol, 3)
    if finnhub_articles:
        print(f"נמצאו {len(finnhub_articles)} מאמרים:")
        for i, article in enumerate(finnhub_articles, 1):
            title = article.get("title", "")
            source = article.get("source", "Unknown")
            relevance = data_fetcher._calculate_news_relevance(title, article.get("summary", ""), symbol)
            
            print(f"{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   רלוונטיות: {relevance:.2f}")
    else:
        print("לא נמצאו מאמרים (אולי אין API key)")
except Exception as e:
    print(f"שגיאה: {e}")

print(f"\n=== 4. Yahoo Finance RSS ===")
try:
    yahoo_articles = data_fetcher.fetch_yahoo_finance_rss(symbol, 3)
    if yahoo_articles:
        print(f"נמצאו {len(yahoo_articles)} מאמרים:")
        for i, article in enumerate(yahoo_articles, 1):
            title = article.get("title", "")
            source = article.get("source", "Unknown")
            relevance = data_fetcher._calculate_news_relevance(title, article.get("summary", ""), symbol)
            
            print(f"{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   רלוונטיות: {relevance:.2f}")
    else:
        print("לא נמצאו מאמרים")
except Exception as e:
    print(f"שגיאה: {e}")

print(f"\n=== 5. Enhanced News Batch (כל המקורות) ===")
try:
    enhanced_news = data_fetcher.fetch_enhanced_news_batch([symbol], 5)
    if symbol in enhanced_news:
        articles = enhanced_news[symbol]
        print(f"נמצאו {len(articles)} מאמרים רלוונטיים:")
        for i, article in enumerate(articles, 1):
            title = article.get("title", "")
            source = article.get("source", "Unknown")
            sentiment = article.get("sentiment", {})
            relevance = article.get("relevance_score", 0)
            
            print(f"{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   סנטימנט: {sentiment}")
            print(f"   רלוונטיות: {relevance:.2f}")
    else:
        print("לא נמצאו מאמרים")
except Exception as e:
    print(f"שגיאה: {e}")

print(f"\n=== 6. השוואה בין מקורות ===")
print("MarketAux:")
print("✅ סנטימנט מובנה")
print("✅ מקורות אמינים")
print("✅ חדשות פיננסיות")
print("❌ כמות מוגבלת")

print(f"\nAlpha Vantage:")
print("✅ סנטימנט מתקדם")
print("✅ חדשות מקצועיות")
print("❌ דורש API key")
print("❌ מגבלות בקשות")

print(f"\nFinnhub:")
print("✅ חדשות מגוונות")
print("✅ מקורות אמינים")
print("❌ ללא סנטימנט")
print("❌ דורש API key")

print(f"\nYahoo Finance RSS:")
print("✅ חדשות עדכניות")
print("✅ ללא מגבלות")
print("❌ ללא סנטימנט")
print("❌ איכות משתנה")

print(f"\n=== 7. המלצות לשיפור ===")
print("1. הוספת API keys:")
print("   - Alpha Vantage API key")
print("   - Finnhub API key")

print(f"\n2. התקנת feedparser:")
print("   pip install feedparser")

print(f"\n3. שיפור סינון:")
print("   - בדיקת תאריך פרסום")
print("   - סינון לפי מקור")
print("   - משקל לפי אמינות") 