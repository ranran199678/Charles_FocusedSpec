from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

# בדיקה עם INTC
symbol = "INTC"
data_fetcher = DataFetcher()
price_df = data_fetcher.get_price_history(symbol, period="1y")
engine = AlphaScoreEngine()
result = engine.evaluate(symbol, price_df)

print(f"=== ניתוח מניית {symbol} ===")
print(f"Score כולל: {result['score']}")
print(f"המלצה: {result['recommendation']}")

print(f"\nפירוט ציונים של כל הסוכנים:")
for agent, score in result['signals'].items():
    print(f"{agent:25}: {score}")

# בדיקת Event Scanner בנפרד
from core.event_scanner import EventScanner
scanner = EventScanner()
event_result = scanner.analyze(symbol)
print(f"\nEvent Scanner Score: {event_result['score']}")
print(f"Event Summary: {event_result['summary']}") 