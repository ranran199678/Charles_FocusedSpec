from core.classic_volume_surge_detector import ClassicVolumeSurgeDetector
from utils.data_fetcher import DataFetcher

# בדיקה רגילה על טיקר "חזק"
symbol = "AMZN"
data_fetcher = DataFetcher()
price_df = data_fetcher.get_price_history(symbol, period="1y")
agent = ClassicVolumeSurgeDetector()
result = agent.analyze(symbol, price_df)
print(result)

# בדיקת קצה: מניה בלי הרבה מסחר/נפח קטן
symbol2 = "GOVX"  # דוגמה למניה עם מעט מסחר, אפשר להחליף
price_df2 = data_fetcher.get_price_history(symbol2, period="1y")
result2 = agent.analyze(symbol2, price_df2)
print("=== VolumeTensionMeter ULTIMATE |", symbol2, "===")
print(result2)

# בדיקת קצה: פחות נתונים (תקופה קצרה)
symbol3 = "TSLA"
price_df3 = data_fetcher.get_price_history(symbol3, period="3mo")
result3 = agent.analyze(symbol3, price_df3)
print("=== VolumeTensionMeter ULTIMATE |", symbol3, "===")
print(result3)
