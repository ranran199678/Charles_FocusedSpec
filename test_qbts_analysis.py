import sys
sys.path.append('.')

from core.nlp_analyzer import NLPAnalyzer
from core.event_scanner import EventScanner
from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

# בדיקת מניית QBTS
symbol = "QBTS"

print(f"=== בדיקת מניית {symbol} עם המערכת המתקדמת ===")

# 1. בדיקת NLP Analyzer
print(f"\n=== 1. NLP Analyzer ===")
nlp_analyzer = NLPAnalyzer()
nlp_result = nlp_analyzer.analyze(symbol)

print(f"ציון NLP: {nlp_result['score']}/100")
print(f"סנטימנט: {nlp_result['sentiment']}")
print(f"סיכום: {nlp_result['summary']}")

# פרטים מתקדמים
details = nlp_result['details']

if 'event_analysis' in details:
    events = details['event_analysis']
    print(f"\nאירועים זוהו:")
    for event_type, event_list in events.get('events', {}).items():
        if event_list:
            print(f"  {event_type}: {len(event_list)} אירועים")
            for event in event_list[:2]:
                print(f"    - {event.get('title', 'No title')}")

if 'market_context' in details:
    market = details['market_context']
    competitors = market.get('competitor_mentions', [])
    if competitors:
        print(f"\nמתחרים זוהו:")
        for comp in competitors:
            print(f"  - {comp.get('competitor', 'Unknown')}")

# 2. בדיקת Event Scanner
print(f"\n=== 2. Event Scanner ===")
event_scanner = EventScanner()
event_result = event_scanner.analyze(symbol)

print(f"ציון Event Scanner: {event_result['score']}/100")
print(f"סיכום: {event_result['summary']}")

if 'events' in event_result:
    events = event_result['events']
    for category, event_list in events.items():
        if event_list:
            print(f"  {category}: {len(event_list)} אירועים")

# 3. בדיקת Alpha Score Engine
print(f"\n=== 3. Alpha Score Engine ===")
data_fetcher = DataFetcher()
price_df = data_fetcher.get_price_history(symbol, period="1y")
engine = AlphaScoreEngine()
engine_result = engine.evaluate(symbol, price_df)

print(f"ציון כולל: {engine_result['score']}/100")
print(f"המלצה: {engine_result['recommendation']}")

print(f"\nפירוט ציונים של כל הסוכנים:")
for agent, score in engine_result['signals'].items():
    print(f"  {agent:25}: {score}")

# 4. השוואה עם מניות אחרות
print(f"\n=== 4. השוואה עם מניות אחרות ===")
comparison_symbols = ["AAPL", "TSLA", "NVDA"]

for comp_symbol in comparison_symbols:
    try:
        comp_nlp = nlp_analyzer.analyze(comp_symbol)
        comp_event = event_scanner.analyze(comp_symbol)
        
        print(f"\n{comp_symbol}:")
        print(f"  NLP Score: {comp_nlp['score']}/100")
        print(f"  Event Score: {comp_event['score']}/100")
        print(f"  NLP Sentiment: {comp_nlp['sentiment']}")
        
    except Exception as e:
        print(f"שגיאה בבדיקת {comp_symbol}: {e}")

# 5. ניתוח מפורט של QBTS
print(f"\n=== 5. ניתוח מפורט של {symbol} ===")

# בדיקת חדשות גולמיות
print(f"\nחדשות אחרונות:")
try:
    enhanced_news = data_fetcher.fetch_enhanced_news_batch([symbol], 5)
    if symbol in enhanced_news:
        articles = enhanced_news[symbol]
        for i, article in enumerate(articles, 1):
            title = article.get('title', '')
            source = article.get('source', 'Unknown')
            relevance = article.get('relevance_score', 0)
            quality = article.get('quality_score', 0)
            
            print(f"{i}. {title}")
            print(f"   מקור: {source}")
            print(f"   רלוונטיות: {relevance:.2f}")
            print(f"   איכות: {quality:.2f}")
    else:
        print("לא נמצאו חדשות")
except Exception as e:
    print(f"שגיאה בשליפת חדשות: {e}")

# 6. סיכום והמלצות
print(f"\n=== 6. סיכום והמלצות ===")
print(f"מניית {symbol}:")
print(f"  ציון NLP: {nlp_result['score']}/100")
print(f"  ציון Event Scanner: {event_result['score']}/100")
print(f"  ציון כולל: {engine_result['score']}/100")

# ניתוח הציון
if engine_result['score'] >= 80:
    print("  🟢 המלצה: קנייה חזקה")
elif engine_result['score'] >= 60:
    print("  🟡 המלצה: קנייה")
elif engine_result['score'] >= 40:
    print("  🟠 המלצה: החזקה")
elif engine_result['score'] >= 20:
    print("  🔴 המלצה: מכירה")
else:
    print("  🔴 המלצה: מכירה חזקה")

print(f"\n=== פרטי החברה ===")
print("QBTS - D-Wave Quantum Inc.")
print("- חברת מחשוב קוונטי")
print("- מתמחה במחשבים קוונטיים")
print("- תעשייה: טכנולוגיה קוונטית")
print("- מתחרים: IBM, Google, Microsoft (בתחום הקוונטי)") 