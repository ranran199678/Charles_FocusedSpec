from core.breakout_retest_recognizer import BreakoutRetestRecognizer
from utils.data_fetcher import DataFetcher

# יצירת מופע של DataFetcher
data_fetcher = DataFetcher()

symbol = "AAPL"
price_df = data_fetcher.get_price_history(symbol, period="1y")
agent = BreakoutRetestRecognizer()
result = agent.analyze(symbol, price_df)
print(f"Result: {result}")
print(price_df.tail(15)[['high', 'close', 'volume']])