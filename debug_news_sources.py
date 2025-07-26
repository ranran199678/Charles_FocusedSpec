import sys
sys.path.append('.')

import requests
import json

# בדיקת מקורות החדשות
symbol = "INTC"

print(f"=== בדיקת מקורות החדשות עבור {symbol} ===")

# API Keys
marketaux_key = "Dx8X1gzfxklRC5WETItJAncifB4bXp98EnSqzT6P"
newsdata_key = "pub_a54510d1206a48d39dd48b3b3b624a2f"

print(f"\n=== 1. MarketAux API ===")
print(f"URL: https://api.marketaux.com/v1/news/all?symbols={symbol}&language=en&limit=10")
print(f"API Key: {marketaux_key[:10]}...")

try:
    url1 = f"https://api.marketaux.com/v1/news/all?symbols={symbol}&language=en&limit=10&api_token={marketaux_key}"
    response1 = requests.get(url1, timeout=10)
    
    print(f"Status Code: {response1.status_code}")
    
    if response1.status_code == 200:
        data1 = response1.json()
        articles1 = data1.get('data', [])
        
        print(f"נמצאו {len(articles1)} מאמרים ב-MarketAux:")
        
        for i, article in enumerate(articles1, 1):
            title = article.get('title', '')
            source = article.get('source', 'Unknown')
            sentiment = article.get('sentiment', 'neutral')
            
            print(f"{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   סנטימנט: {sentiment}")
            
    else:
        print(f"שגיאה: {response1.text}")
        
except Exception as e:
    print(f"שגיאה ב-MarketAux: {e}")

print(f"\n=== 2. NewsData API ===")
print(f"URL: https://newsdata.io/api/1/news?apikey=...&q={symbol}&language=en&category=business")
print(f"API Key: {newsdata_key[:10]}...")

try:
    url2 = f"https://newsdata.io/api/1/news?apikey={newsdata_key}&q={symbol}&language=en&category=business"
    response2 = requests.get(url2, timeout=10)
    
    print(f"Status Code: {response2.status_code}")
    
    if response2.status_code == 200:
        data2 = response2.json()
        articles2 = data2.get('results', [])
        
        print(f"נמצאו {len(articles2)} מאמרים ב-NewsData:")
        
        for i, article in enumerate(articles2[:5], 1):
            title = article.get('title', '')
            source = article.get('source_id', 'Unknown')
            
            print(f"{i}. {title}")
            print(f"   מקור: {source}")
            
    else:
        print(f"שגיאה: {response2.text}")
        
except Exception as e:
    print(f"שגיאה ב-NewsData: {e}")

print(f"\n=== 3. הסבר המקורות ===")
print("MarketAux API:")
print("- מקור: MarketAux (חברת חדשות פיננסיות)")
print("- תכונות: סנטימנט מובנה, מקורות מגוונים")
print("- מגבלות: 1000 בקשות בחודש חינם")

print(f"\nNewsData API:")
print("- מקור: NewsData.io (אגרגטור חדשות)")
print("- תכונות: חדשות כלליות, קטגוריות")
print("- מגבלות: 200 בקשות ביום חינם")

print(f"\n=== 4. איכות החדשות ===")
print("MarketAux:")
print("✅ חדשות פיננסיות מקצועיות")
print("✅ סנטימנט מובנה")
print("✅ מקורות אמינים")
print("❌ כמות מוגבלת")

print(f"\nNewsData:")
print("✅ חדשות כלליות מגוונות")
print("✅ כמות גדולה")
print("❌ ללא סנטימנט מובנה")
print("❌ איכות משתנה")

print(f"\n=== 5. המלצות לשיפור ===")
print("1. הוספת מקורות נוספים:")
print("   - Alpha Vantage News API")
print("   - Finnhub News API")
print("   - Yahoo Finance RSS")
print("   - Reuters API")

print(f"\n2. שיפור סינון:")
print("   - בדיקת תאריך פרסום")
print("   - סינון לפי מקור")
print("   - משקל לפי אמינות")

print(f"\n3. ניתוח מתקדם:")
print("   - ניתוח סנטימנט מתקדם")
print("   - זיהוי אירועים חשובים")
print("   - ניתוח מגמות") 