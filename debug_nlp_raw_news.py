import sys
sys.path.append('.')

from core.nlp_analyzer import NLPAnalyzer
import requests

# בדיקת החדשות הגולמיות
symbol = "INTC"
api_key = "Dx8X1gzfxklRC5WETItJAncifB4bXp98EnSqzT6P"

print(f"=== בדיקת החדשות הגולמיות עבור {symbol} ===")

# שליפת חדשות ישירות
try:
    url = f"https://api.marketaux.com/v1/news/all?symbols={symbol}&language=en&limit=10&api_token={api_key}"
    response = requests.get(url, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('data', [])
        
        print(f"\nנמצאו {len(articles)} מאמרים:")
        print("=" * 80)
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', '')
            description = article.get('description', '')
            sentiment = article.get('sentiment', 'neutral')
            published_at = article.get('published_at', '')
            
            print(f"\n{i}. כותרת: {title}")
            print(f"   תיאור: {description[:200]}...")
            print(f"   סנטימנט: {sentiment}")
            print(f"   תאריך: {published_at}")
            
            # בדיקה אם יש מילות מפתח שליליות
            text_lower = f"{title} {description}".lower()
            negative_words = ['dismal', 'layoffs', 'declines', 'missed', 'disappointing', 'poor', 'weak']
            found_negative = [word for word in negative_words if word in text_lower]
            
            if found_negative:
                print(f"   ⚠️  מילים שליליות זוהו: {found_negative}")
            
            positive_words = ['beat', 'strong', 'growth', 'profit', 'positive', 'excellent']
            found_positive = [word for word in positive_words if word in text_lower]
            
            if found_positive:
                print(f"   ✅ מילים חיוביות זוהו: {found_positive}")
                
    else:
        print(f"שגיאה: {response.text}")
        
except Exception as e:
    print(f"שגיאה: {e}")

print(f"\n" + "=" * 80)
print("הסבר הבעיה:")
print("המערכת אוספת חדשות כלליות על השוק ולא רק על INTC")
print("חלק מהחדשות הן על מניות אחרות או על השוק הכללי")
print("זה גורם לניתוח שגוי כי המערכת לא מבדילה בין חדשות על INTC לחדשות כלליות") 