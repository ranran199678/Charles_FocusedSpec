import sys
import os
sys.path.append('.')

from core.moving_average_pressure_bot import MovingAveragePressureBot
from utils.data_fetcher import DataFetcher

def test_ma_pressure_simple():
    print("=== בדיקה פשוטה של Moving Average Pressure Bot ===")
    
    # יצירת סוכן
    agent = MovingAveragePressureBot()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניה
    symbol = "AAPL"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        print(f"עמודות זמינות: {list(price_df.columns)}")
        print(f"צורת הנתונים: {price_df.shape}")
        
        # הרצת ניתוח
        result = agent.analyze(symbol, price_df)
        
        print(f"\nתוצאות:")
        print(f"ציון: {result.get('score', 'N/A')}/100")
        print(f"הסבר: {result.get('explanation', 'N/A')}")
        
        if 'details' in result:
            details = result['details']
            if 'pressure_analysis' in details:
                pressure = details['pressure_analysis']
                print(f"סוג לחץ: {pressure.get('pressure_type', 'N/A')}")
                print(f"עוצמת לחץ: {pressure.get('pressure_strength', 'N/A')}")
            
            if 'trend_analysis' in details:
                trend = details['trend_analysis']
                print(f"מגמה קצרה: {trend.get('short_trend', 'N/A')}")
                print(f"מגמה בינונית: {trend.get('medium_trend', 'N/A')}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ma_pressure_simple() 