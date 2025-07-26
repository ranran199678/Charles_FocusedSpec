from core.parabolic_agent import ParabolicAgent
from utils.data_fetcher import DataFetcher

# בדוק טיקר חזק עם ריצות פראבוליות (למשל NVDA, TSLA, או אחר)
symbol = "AMZN"
data_fetcher = DataFetcher()
price_df = data_fetcher.get_price_history(symbol, period="1y")
agent = ParabolicAgent()
result = agent.analyze(symbol, price_df)
print(result)

# בדוק גם טיקר בלי ריצה פראבולית ברורה
symbol2 = "KO"  # לדוג' קוקה קולה – לרוב דשדוש, פחות פראבולי
price_df2 = data_fetcher.get_price_history(symbol2, period="1y")
result2 = agent.analyze(symbol2, price_df2)
print(f"=== ParabolicAgent | {symbol2} ===")
print(result2)
