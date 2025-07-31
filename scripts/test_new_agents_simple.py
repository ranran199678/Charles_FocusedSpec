import sys
import os
sys.path.append('.')

from core.moving_average_pressure_bot import MovingAveragePressureBot
from core.bollinger_squeeze import BollingerSqueezeAgent
from utils.data_fetcher import DataFetcher

def test_new_agents_simple():
    print("=== בדיקה פשוטה של סוכנים חדשים ===")
    
    # יצירת סוכנים
    ma_agent = MovingAveragePressureBot()
    bb_agent = BollingerSqueezeAgent()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניה
    symbol = "INTC"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        print(f"עמודות זמינות: {list(price_df.columns)}")
        print(f"צורת הנתונים: {price_df.shape}")
        
        # בדיקת Moving Average Pressure Bot
        print(f"\n--- Moving Average Pressure Bot ---")
        ma_result = ma_agent.analyze(symbol, price_df)
        print(f"ציון: {ma_result.get('score', 'N/A')}/100")
        print(f"הסבר: {ma_result.get('explanation', 'N/A')}")
        
        # בדיקת Bollinger Squeeze Agent
        print(f"\n--- Bollinger Squeeze Agent ---")
        bb_result = bb_agent.analyze(symbol, price_df)
        print(f"ציון: {bb_result.get('score', 'N/A')}/100")
        print(f"הסבר: {bb_result.get('explanation', 'N/A')}")
        
        # סיכום
        print(f"\n--- סיכום ---")
        total_score = ma_result.get('score', 0) + bb_result.get('score', 0)
        avg_score = total_score / 2
        print(f"ציון ממוצע: {avg_score:.1f}/100")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_agents_simple() 