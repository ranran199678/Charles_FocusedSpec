"""
טסט עבור Event Scanner
"""

from core.event_scanner import EventScanner
from utils.data_fetcher import DataFetcher

def test_event_scanner():
    """טסט בסיסי של Event Scanner"""
    
    # יצירת instance
    scanner = EventScanner()
    
    # בדיקה עם מניה ספציפית
    symbol = "AAPL"
    result = scanner.analyze(symbol)
    
    print(f"=== תוצאות Event Scanner עבור {symbol} ===")
    print(f"ציון השפעה: {result['score']}/100")
    print(f"סיכום: {result['summary']}")
    print(f"זמן: {result['timestamp']}")
    
    # הדפסת אירועים לפי קטגוריות
    events = result['events']
    for category, event_list in events.items():
        if event_list:
            print(f"\n{category.upper()}: {len(event_list)} אירועים")
            for i, event in enumerate(event_list[:3]):  # רק 3 הראשונים
                print(f"  {i+1}. {event.get('title', 'No title')}")
    
    # בדיקת פונקציות נוספות
    recent_events = scanner.get_recent_events(symbol, days=7)
    print(f"\nאירועים אחרונים: {len(recent_events)} קטגוריות")
    
    impact_analysis = scanner.get_impact_analysis(symbol)
    print(f"ניתוח השפעה: ציון {impact_analysis['score']}")
    
    return result

if __name__ == "__main__":
    test_event_scanner() 