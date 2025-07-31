import requests
import json

# בדיקת החדשות של INTC
symbol = "INTC"
api_key = "Dx8X1gzfxklRC5WETItJAncifB4bXp98EnSqzT6P"

print(f"=== בדיקת חדשות עבור {symbol} ===")

try:
    url = f"https://api.marketaux.com/v1/news/all?symbols={symbol}&language=en&limit=10&api_token={api_key}"
    response = requests.get(url, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('data', [])
        
        print(f"נמצאו {len(articles)} מאמרים")
        
        for i, article in enumerate(articles):
            title = article.get('title', '')
            sentiment = article.get('sentiment', 'neutral')
            published_at = article.get('published_at', '')
            
            print(f"\n{i+1}. {title}")
            print(f"   Sentiment: {sentiment}")
            print(f"   Published: {published_at}")
            
            # בדיקה אם יש מילות מפתח לדוחות כספיים
            title_lower = title.lower()
            if any(keyword in title_lower for keyword in ['earnings', 'quarterly', 'financial', 'results', 'report']):
                print(f"   ⚠️  דוחות כספיים זוהו!")
                
    else:
        print(f"שגיאה: {response.text}")
        
except Exception as e:
    print(f"שגיאה: {e}")

print("\n=== בדיקת מילות מפתח ===")
keywords = ['earnings', 'quarterly', 'financial', 'results', 'report', 'revenue', 'profit', 'loss']
print(f"מילות מפתח לדוחות כספיים: {keywords}") 