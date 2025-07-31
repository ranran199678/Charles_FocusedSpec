from core.parabolic_agent import ParabolicAgent
from utils.data_fetcher import DataFetcher

# יצירת מופע של DataFetcher
data_fetcher = DataFetcher()

symbol = "AAPL"
symbol2 = "TSLA"
price_df = data_fetcher.get_price_history(symbol, period="1y")
price_df2 = data_fetcher.get_price_history(symbol2, period="1y")

agent = ParabolicAgent()
result = agent.analyze(price_df)
result2 = agent.analyze(price_df2)

print(f"AAPL Result: {result}")
print(f"TSLA Result: {result2}")
