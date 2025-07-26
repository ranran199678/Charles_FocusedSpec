from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

symbol = "AMZN"
data_fetcher = DataFetcher()
price_df = data_fetcher.get_price_history(symbol, period="1y")
engine = AlphaScoreEngine()
result = engine.evaluate(symbol, price_df)
print(result)
