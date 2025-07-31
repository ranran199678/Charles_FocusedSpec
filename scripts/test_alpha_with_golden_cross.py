import sys
import os
sys.path.append('.')

from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

def test_alpha_with_golden_cross():
    print("=== בדיקת AlphaScoreEngine עם GoldenCrossAgent ===")
    
    # יצירת AlphaScoreEngine
    engine = AlphaScoreEngine()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניה
    symbol = "INTC"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="200d")
        
        print(f"מחיר אחרון: {price_df['close'].iloc[-1]:.2f}")
        print(f"תאריכים: {price_df.index[0]} עד {price_df.index[-1]}")
        
        # ניתוח
        result = engine.evaluate(symbol, price_df)
        
        print(f"\n--- תוצאות AlphaScoreEngine ---")
        print(f"ציון סופי: {result['score']}/100")
        print(f"המלצה: {result['recommendation']}")
        
        # בדיקת סוכנים ספציפיים
        print(f"\n--- סוכנים פעילים ---")
        active_agents = []
        
        for agent_name, score in result['signals'].items():
            if score > 1:  # לא DummyAgent
                active_agents.append((agent_name, score))
                print(f"{agent_name}: {score}/100")
        
        print(f"\nסה\"כ סוכנים פעילים: {len(active_agents)}")
        
        # בדיקת GoldenCrossAgent ספציפית
        if "GoldenCrossAgent" in result['signals']:
            golden_score = result['signals']['GoldenCrossAgent']
            golden_explanation = result['explanations']['GoldenCrossAgent']
            print(f"\n--- GoldenCrossAgent ---")
            print(f"ציון: {golden_score}/100")
            print(f"הסבר: {golden_explanation}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alpha_with_golden_cross() 