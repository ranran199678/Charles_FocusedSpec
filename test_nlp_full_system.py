from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

# בדיקה עם AAPL
symbol = "AAPL"
data_fetcher = DataFetcher()
price_df = data_fetcher.get_price_history(symbol, period="1y")
engine = AlphaScoreEngine()
result = engine.evaluate(symbol, price_df)

print(f"=== ניתוח מניית {symbol} עם NLP Analyzer ===")
print(f"Score כולל: {result['score']}")
print(f"המלצה: {result['recommendation']}")

print(f"\nפירוט ציונים של כל הסוכנים:")
for agent, score in result['signals'].items():
    print(f"{agent:25}: {score}")

# בדיקת NLP Analyzer בנפרד
from core.nlp_analyzer import NLPAnalyzer
nlp_analyzer = NLPAnalyzer()
nlp_result = nlp_analyzer.analyze(symbol)
print(f"\nNLP Analyzer Score: {nlp_result['score']}")
print(f"NLP Sentiment: {nlp_result['sentiment']}")
print(f"NLP Summary: {nlp_result['summary']}")

# השוואה עם Event Scanner
from core.event_scanner import EventScanner
event_scanner = EventScanner()
event_result = event_scanner.analyze(symbol)
print(f"\nEvent Scanner Score: {event_result['score']}")
print(f"Event Summary: {event_result['summary']}")

print(f"\n=== השוואה ===")
print(f"NLP Analyzer: {nlp_result['score']}/100")
print(f"Event Scanner: {event_result['score']}/100")
print(f"הבדל: {abs(nlp_result['score'] - event_result['score'])} נקודות") 