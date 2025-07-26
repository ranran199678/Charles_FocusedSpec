from core.breakout_retest_recognizer import BreakoutRetestRecognizer
from utils.data_fetcher import DataFetcher

symbol = "AMZN"
data_fetcher = DataFetcher()
price_df = data_fetcher.get_price_history(symbol, period="1y")
agent = BreakoutRetestRecognizer(symbol, {
    "breakout_window": 15,
    "min_breakout_volume_ratio": 1.1,
    "gap_percent": 0.0})
result = agent.analyze(price_df)
print(result)
print(price_df.tail(15)[['high', 'close', 'volume']])