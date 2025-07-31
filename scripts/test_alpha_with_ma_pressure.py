import sys
import os
sys.path.append('.')

from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

def test_alpha_with_ma_pressure():
    print("=== בדיקת AlphaScoreEngine עם Moving Average Pressure Bot ===")
    
    # יצירת AlphaScoreEngine
    engine = AlphaScoreEngine()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניה
    symbol = "AAPL"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        # הרצת ניתוח
        result = engine.evaluate(symbol, price_df)
        
        print(f"ציון כולל: {result.get('score', 'N/A')}/100")
        print(f"המלצה: {result.get('recommendation', 'N/A')}")
        print(f"הסבר: {result.get('explanation', 'N/A')}")
        
        # בדיקת תוצאות סוכנים ספציפיים
        if 'agent_results' in result:
            print(f"\nתוצאות סוכנים:")
            for agent_name, agent_result in result['agent_results'].items():
                if 'MovingAveragePressureBot' in agent_name:
                    print(f"  {agent_name}: {agent_result.get('score', 'N/A')}/100")
                    print(f"    הסבר: {agent_result.get('explanation', 'N/A')}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alpha_with_ma_pressure() 