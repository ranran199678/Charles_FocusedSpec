import pandas as pd
from utils import data_fetcher
from core.alpha_score_engine import AlphaScoreEngine

if __name__ == "__main__":
    symbol = input("הזן סימול מניה לבדיקה (למשל MSFT): ").strip().upper() or "MSFT"
    price_df = data_fetcher.get_price_history(symbol)
    engine = AlphaScoreEngine()
    result = engine.evaluate(symbol, price_df)
    print(f"\n=== ניתוח מניית {symbol} ===")
    print("Score כולל:", result["score"])
    print("המלצה:", result["recommendation"])
    print("\nפירוט ציונים (1-100) של כל הסוכנים:")
    for agent, score in result["signals"].items():
        print(f"{agent:22}: {score}")
