import sys
import os
sys.path.append('.')

from core.moving_average_pressure_bot import MovingAveragePressureBot
from core.bollinger_squeeze import BollingerSqueezeAgent
from utils.data_fetcher import DataFetcher

def test_qbts_updated():
    print("=== בדיקת QBTS עם נתונים מעודכנים ===")
    
    # יצירת סוכנים
    ma_agent = MovingAveragePressureBot()
    bb_agent = BollingerSqueezeAgent()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניה
    symbol = "QBTS"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        print(f"עמודות זמינות: {list(price_df.columns)}")
        print(f"צורת הנתונים: {price_df.shape}")
        print(f"תאריכים: {price_df.index[0]} עד {price_df.index[-1]}")
        print(f"מחיר אחרון: {price_df['close'].iloc[-1]:.2f}")
        
        # בדיקת Moving Average Pressure Bot
        print(f"\n--- Moving Average Pressure Bot ---")
        ma_result = ma_agent.analyze(symbol, price_df)
        print(f"ציון: {ma_result.get('score', 'N/A')}/100")
        print(f"הסבר: {ma_result.get('explanation', 'N/A')}")
        
        # פרטים נוספים MA
        if 'details' in ma_result and 'pressure_analysis' in ma_result['details']:
            pressure = ma_result['details']['pressure_analysis']
            print(f"סוג לחץ: {pressure.get('pressure_type', 'N/A')}")
            print(f"עוצמת לחץ: {pressure.get('pressure_strength', 'N/A')}")
            
            if 'trend_analysis' in ma_result['details']:
                trend = ma_result['details']['trend_analysis']
                print(f"מגמה קצרה: {trend.get('short_trend', 'N/A')}")
                print(f"מגמה בינונית: {trend.get('medium_trend', 'N/A')}")
                print(f"צלב מוזהב: {trend.get('golden_cross', 'N/A')}")
                print(f"צלב מוות: {trend.get('death_cross', 'N/A')}")
        
        # בדיקת Bollinger Squeeze Agent
        print(f"\n--- Bollinger Squeeze Agent ---")
        bb_result = bb_agent.analyze(symbol, price_df)
        print(f"ציון: {bb_result.get('score', 'N/A')}/100")
        print(f"הסבר: {bb_result.get('explanation', 'N/A')}")
        
        # פרטים נוספים BB
        if 'details' in bb_result and 'squeeze_analysis' in bb_result['details']:
            squeeze = bb_result['details']['squeeze_analysis']
            print(f"התכווצות: {squeeze.get('is_squeeze', 'N/A')}")
            print(f"רמת התכווצות: {squeeze.get('squeeze_level', 'N/A')}")
            print(f"מיקום מחיר: {squeeze.get('price_position', 'N/A')}")
            
            if 'volume_analysis' in bb_result['details'] and bb_result['details']['volume_analysis']:
                volume = bb_result['details']['volume_analysis']
                print(f"נפח: {volume.get('volume_signal', 'N/A')}")
                print(f"מגמת נפח: {volume.get('volume_trend', 'N/A')}")
        
        # המלצות
        if 'details' in ma_result and 'recommendations' in ma_result['details']:
            print(f"\nהמלצות MA: {', '.join(ma_result['details']['recommendations'])}")
        
        if 'details' in bb_result and 'recommendations' in bb_result['details']:
            print(f"המלצות BB: {', '.join(bb_result['details']['recommendations'])}")
        
        # סיכום
        print(f"\n--- סיכום ---")
        total_score = ma_result.get('score', 0) + bb_result.get('score', 0)
        avg_score = total_score / 2
        print(f"ציון ממוצע: {avg_score:.1f}/100")
        
        # ניתוח כללי
        if avg_score >= 70:
            sentiment = "חיובי חזק"
        elif avg_score >= 50:
            sentiment = "חיובי חלש"
        elif avg_score >= 30:
            sentiment = "שלילי חלש"
        else:
            sentiment = "שלילי חזק"
        
        print(f"סנטימנט כללי: {sentiment}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qbts_updated() 