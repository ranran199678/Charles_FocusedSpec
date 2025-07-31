import sys
import os
sys.path.append('.')

from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

def test_golden_cross_simple():
    print("=== בדיקת GoldenCrossAgent ב-AlphaScoreEngine ===")
    
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
        
        # בדיקה ישירה של GoldenCrossAgent
        golden_agent = engine.agents.get("GoldenCrossAgent")
        if golden_agent:
            print("✅ GoldenCrossAgent נמצא ב-AlphaScoreEngine")
            
            # בדיקת הסוכן
            result = golden_agent.analyze(symbol, price_df)
            print(f"ציון GoldenCrossAgent: {result.get('score', 'N/A')}/100")
            print(f"הסבר: {result.get('explanation', 'N/A')}")
            
            # בדיקה אם זה לא DummyAgent
            if result.get('score', 0) > 1:
                print("✅ GoldenCrossAgent עובד (לא DummyAgent)")
            else:
                print("❌ GoldenCrossAgent לא עובד (DummyAgent)")
        else:
            print("❌ GoldenCrossAgent לא נמצא ב-AlphaScoreEngine")
        
        # בדיקת כל הסוכנים הפעילים
        print(f"\n--- סוכנים פעילים ---")
        active_count = 0
        for name, agent in engine.agents.items():
            try:
                result = agent.analyze(symbol, price_df)
                score = result.get('score', 0)
                if score > 1:  # לא DummyAgent
                    active_count += 1
                    print(f"✅ {name}: {score}/100")
                else:
                    print(f"❌ {name}: DummyAgent")
            except Exception as e:
                print(f"❌ {name}: שגיאה - {str(e)}")
        
        print(f"\nסה\"כ סוכנים פעילים: {active_count}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_golden_cross_simple() 