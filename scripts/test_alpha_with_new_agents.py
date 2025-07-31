import sys
import os
sys.path.append('.')

from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

def test_alpha_with_new_agents():
    print("=== בדיקת AlphaScoreEngine עם סוכנים חדשים ===")
    
    # יצירת AlphaScoreEngine
    engine = AlphaScoreEngine()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניה
    symbol = "INTC"  # נבדוק INTC כי ראינו שיש לו התכווצות חזקה
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        # הרצת ניתוח
        result = engine.evaluate(symbol, price_df)
        
        print(f"ציון כולל: {result.get('score', 'N/A')}/100")
        print(f"המלצה: {result.get('recommendation', 'N/A')}")
        
        # בדיקת תוצאות סוכנים ספציפיים
        if 'signals' in result:
            print(f"\nתוצאות סוכנים:")
            for agent_name, score in result['signals'].items():
                if 'MovingAveragePressureBot' in agent_name or 'BollingerSqueezeAgent' in agent_name:
                    print(f"  {agent_name}: {score}/100")
        
        # בדיקת הסברים
        if 'explanations' in result:
            print(f"\nהסברים:")
            for agent_name, explanation in result['explanations'].items():
                if 'MovingAveragePressureBot' in agent_name or 'BollingerSqueezeAgent' in agent_name:
                    print(f"  {agent_name}: {explanation[:100]}...")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alpha_with_new_agents() 