import pandas as pd
from core.rsi_sniffer import RSISniffer
from utils.data_fetcher import DataFetcher

symbol = "AMZN"
data_fetcher = DataFetcher()
price_df = data_fetcher.get_price_history(symbol, period="1y")
agent = RSISniffer()
result = agent.analyze(symbol, price_df)
print(result)
