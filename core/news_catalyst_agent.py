import requests

class NewsCatalystAgent:
    def __init__(self, keywords=None, lookback_days=7):
        """
        אתחול הסוכן.
        keywords - רשימת מילות מפתח לאיתור חדשות 'טובות' (ברירת מחדל רשימה כללית).
        lookback_days - טווח זמן לבדיקת חדשות אחרונות (7 ימים ברירת מחדל).
        """
        if keywords is None:
            keywords = ["beats earnings", "FDA approval", "acquisition", "merger", "partnership", "upgrade"]
        self.keywords = keywords
        self.lookback_days = lookback_days

    def analyze(self, symbol):
        """
        זיהוי חדשות קטליסטיות עבור הטיקר.
        מחזיר True אם נמצאה ידיעה חיובית משמעותית לאחרונה, אחרת False.
        """
        try:
            # שימוש ב-FMP API לקבלת חדשות אחרונות עבור הטיקר
            api_key = "<FMP_API_KEY>"  # יש להחליף במפתח API אמיתי
            url = (f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}"
                   f"&limit=10&apikey={api_key}")
            resp = requests.get(url, timeout=5)
        except Exception as e:
            return False
        if resp.status_code != 200:
            return False
        news_items = resp.json()
        if not isinstance(news_items, list):
            return False
        # עבור כל כותרת/תוכן חדשות, בדוק אם מכיל אחת ממילות המפתח
        for item in news_items:
            title = item.get("title", "").lower()
            summary = item.get("text", "").lower()
            for kw in self.keywords:
                if kw in title or kw in summary:
                    return True
        return False
