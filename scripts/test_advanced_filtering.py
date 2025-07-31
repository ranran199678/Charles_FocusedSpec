import sys
sys.path.append('.')

from utils.data_fetcher import DataFetcher

# בדיקת הסינון המתקדם
symbol = "INTC"

print(f"=== בדיקת סינון מתקדם עבור {symbol} ===")

data_fetcher = DataFetcher()

print(f"\n=== 1. שליפת חדשות עם סינון מתקדם ===")
enhanced_news = data_fetcher.fetch_enhanced_news_batch([symbol], 10)

if symbol in enhanced_news:
    articles = enhanced_news[symbol]
    print(f"נמצאו {len(articles)} מאמרים אחרי סינון:")
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', '')
        source = article.get('source', 'Unknown')
        relevance = article.get('relevance_score', 0)
        quality = article.get('quality_score', 0)
        sentiment = article.get('sentiment', {})
        
        print(f"\n{i}. {title}")
        print(f"   מקור: {source}")
        print(f"   רלוונטיות: {relevance:.2f}")
        print(f"   איכות: {quality:.2f}")
        print(f"   סנטימנט: {sentiment}")
else:
    print("לא נמצאו מאמרים")

print(f"\n=== 2. השוואה עם סינון רגיל ===")
# בדיקה עם הסינון הישן
try:
    marketaux_key = "Dx8X1gzfxklRC5WETItJAncifB4bXp98EnSqzT6P"
    url = f"https://api.marketaux.com/v1/news/all?symbols={symbol}&language=en&limit=10&api_token={marketaux_key}"
    response = data_fetcher._safe_request(url)
    
    if response.get("data"):
        old_articles = response["data"]
        print(f"מאמרים ללא סינון מתקדם: {len(old_articles)}")
        
        for i, article in enumerate(old_articles[:3], 1):
            title = article.get("title", "")
            source = article.get("source", "Unknown")
            relevance = data_fetcher._calculate_news_relevance(title, article.get("description", ""), symbol)
            
            print(f"{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   רלוונטיות: {relevance:.2f}")
except Exception as e:
    print(f"שגיאה: {e}")

print(f"\n=== 3. פרטי הסינון המתקדם ===")
print("הסינון כולל:")
print("1. סינון לפי תאריך (רק חדשות אחרונות - 7 ימים)")
print("2. סינון לפי מקורות אמינים")
print("3. חישוב ציון איכות כולל")
print("4. משקל לחדשות חשובות")
print("5. משקל לחדשות שליליות")

print(f"\n=== 4. מקורות אמינים ===")
trusted_sources = [
    'reuters', 'bloomberg', 'cnbc', 'marketwatch', 'yahoo finance',
    'seeking alpha', 'barrons', 'wall street journal', 'financial times',
    'forbes', 'fortune', 'business insider', 'techcrunch'
]
print("מקורות אמינים:")
for source in trusted_sources:
    print(f"  - {source}")

print(f"\n=== 5. מילות מפתח חשובות ===")
important_keywords = ['earnings', 'revenue', 'profit', 'quarterly', 'financial', 'results', 'guidance']
negative_keywords = ['layoffs', 'restructuring', 'decline', 'miss', 'disappointing', 'dismal']

print("מילות מפתח חשובות:")
for keyword in important_keywords:
    print(f"  - {keyword}")

print("מילות מפתח שליליות (משקל גבוה יותר):")
for keyword in negative_keywords:
    print(f"  - {keyword}")

print(f"\n=== 6. חישוב ציון איכות ===")
print("ציון איכות = רלוונטיות × אמינות מקור × משקל חשיבות × משקל שליליות")
print("מקסימום ציון: 1.0")
print("מינימום לציון: 0.4")

print(f"\n=== 7. יתרונות הסינון המתקדם ===")
print("✅ חדשות עדכניות בלבד")
print("✅ מקורות אמינים בלבד")
print("✅ משקל לחדשות חשובות")
print("✅ משקל לחדשות שליליות")
print("✅ סינון איכות מתקדם")
print("✅ מיון לפי איכות") 