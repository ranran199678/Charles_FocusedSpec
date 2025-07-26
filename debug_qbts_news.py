import sys
sys.path.append('.')

import requests
import json

# בדיקת החדשות הגולמיות של QBTS
symbol = "QBTS"

print(f"=== בדיקת החדשות הגולמיות של {symbol} ===")

# API Keys
marketaux_key = "Dx8X1gzfxklRC5WETItJAncifB4bXp98EnSqzT6P"
newsdata_key = "pub_a54510d1206a48d39dd48b3b3b624a2f"

print(f"\n=== 1. MarketAux API ===")
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
            description = article.get('description', '')
            
            print(f"\n{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   סנטימנט: {sentiment}")
            print(f"   תיאור: {description[:200]}...")
            
    else:
        print(f"שגיאה: {response1.text}")
        
except Exception as e:
    print(f"שגיאה ב-MarketAux: {e}")

print(f"\n=== 2. NewsData API ===")
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
            description = article.get('description', '')
            
            print(f"\n{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   תיאור: {description[:200]}...")
            
    else:
        print(f"שגיאה: {response2.text}")
        
except Exception as e:
    print(f"שגיאה ב-NewsData: {e}")

print(f"\n=== 3. ניתוח QBTS ===")
print("QBTS - D-Wave Quantum Inc.")
print("- חברת מחשוב קוונטי קנדית")
print("- מתמחה במחשבים קוונטיים")
print("- תעשייה: טכנולוגיה קוונטית")
print("- מתחרים: IBM, Google, Microsoft (בתחום הקוונטי)")

print(f"\n=== 4. הסבר התוצאות ===")
print("NLP Score: 60/100 - ציון בינוני")
print("- סנטימנט ניטרלי")
print("- זוהו אירועי דוחות כספיים")
print("- זוהו אירועי השקת מוצרים")

print(f"\nEvent Scanner Score: 12/100 - ציון נמוך")
print("- מעט אירועים דרמטיים")
print("- בעיקר אירועים כלכליים")

print(f"\nAlpha Score Engine: 6.6/100 - ציון נמוך מאוד")
print("- רוב הסוכנים נותנים ציון נמוך")
print("- רק NLP Analyzer נותן ציון גבוה (60)")
print("- Event Scanner נותן ציון נמוך (12)")

print(f"\n=== 5. המלצות ===")
print("🔴 המלצה: מכירה חזקה")
print("- ציון כולל נמוך מאוד (6.6/100)")
print("- רוב הסוכנים נותנים ציון נמוך")
print("- למרות NLP Score בינוני, המערכת לא ממליצה")
print("- סיכון גבוה במניית טכנולוגיה קוונטית") 