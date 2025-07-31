import pandas as pd
from core.rsi_sniffer import RSISniffer
from utils.data_fetcher import DataFetcher

# יצירת מופע של DataFetcher
data_fetcher = DataFetcher()

symbol = "AAPL"
price_df = data_fetcher.get_price_history(symbol, period="1y")
agent = RSISniffer()
result = agent.analyze(price_df)
print(f"Result: {result}")
