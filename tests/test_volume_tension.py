from core.volume_tension_meter import VolumeTensionMeter
from utils.data_fetcher import DataFetcher

# יצירת מופע של DataFetcher
data_fetcher = DataFetcher()

symbol = "AAPL"
symbol2 = "TSLA"
symbol3 = "NVDA"
price_df = data_fetcher.get_price_history(symbol, period="1y")
price_df2 = data_fetcher.get_price_history(symbol2, period="1y")
price_df3 = data_fetcher.get_price_history(symbol3, period="3mo")

agent = VolumeTensionMeter()
result = agent.analyze(price_df)
result2 = agent.analyze(price_df2)
result3 = agent.analyze(price_df3)

print(f"AAPL Result: {result}")
print(f"TSLA Result: {result2}")
print(f"NVDA Result: {result3}")
