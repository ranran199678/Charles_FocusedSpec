import sys
import os
sys.path.append('.')

from core.moving_average_pressure_bot import MovingAveragePressureBot
from utils.data_fetcher import DataFetcher

def test_moving_average_pressure():
    print("=== בדיקת Moving Average Pressure Bot ===")
    
    # יצירת סוכן
    agent = MovingAveragePressureBot()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניות שונות
    symbols = ["AAPL", "INTC", "QBTS"]
    
    for symbol in symbols:
        print(f"\n--- בדיקת {symbol} ---")
        
        try:
            # קבלת נתוני מחיר
            price_df = data_fetcher.get_price_history(symbol, period="100d")
            
            # הרצת ניתוח
            result = agent.analyze(symbol, price_df)
            
            print(f"ציון: {result['score']}/100")
            print(f"הסבר: {result['explanation']}")
            
            # פרטים נוספים
            if 'details' in result and 'pressure_analysis' in result['details']:
                pressure = result['details']['pressure_analysis']
                print(f"סוג לחץ: {pressure.get('pressure_type', 'לא זמין')}")
                print(f"עוצמת לחץ: {pressure.get('pressure_strength', 'לא זמין')}")
                
                if 'volume_analysis' in pressure and pressure['volume_analysis']:
                    print(f"לחץ נפח: {pressure['volume_analysis'].get('volume_pressure', 'לא זמין')}")
            
            if 'details' in result and 'trend_analysis' in result['details']:
                trend = result['details']['trend_analysis']
                print(f"מגמה קצרה: {trend.get('short_trend', 'לא זמין')}")
                print(f"מגמה בינונית: {trend.get('medium_trend', 'לא זמין')}")
                print(f"יישור מגמות: {trend.get('trend_alignment', 'לא זמין')}")
            
            if 'details' in result and 'recommendations' in result['details']:
                recommendations = result['details']['recommendations']
                print(f"המלצות: {', '.join(recommendations)}")
                
        except Exception as e:
            print(f"שגיאה בבדיקת {symbol}: {str(e)}")

if __name__ == "__main__":
    test_moving_average_pressure() 