import sys
import os
sys.path.append('.')

from core.bollinger_squeeze import BollingerSqueezeAgent
from utils.data_fetcher import DataFetcher

def test_bollinger_squeeze():
    print("=== בדיקת Bollinger Squeeze Agent ===")
    
    # יצירת סוכן
    agent = BollingerSqueezeAgent()
    
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
            if 'details' in result and 'squeeze_analysis' in result['details']:
                squeeze = result['details']['squeeze_analysis']
                print(f"התכווצות: {squeeze.get('is_squeeze', 'N/A')}")
                print(f"רמת התכווצות: {squeeze.get('squeeze_level', 'N/A')}")
                print(f"מיקום מחיר: {squeeze.get('price_position', 'N/A')}")
                
                if 'volume_analysis' in result['details'] and result['details']['volume_analysis']:
                    volume = result['details']['volume_analysis']
                    print(f"נפח: {volume.get('volume_signal', 'N/A')}")
                    print(f"מגמת נפח: {volume.get('volume_trend', 'N/A')}")
            
            if 'details' in result and 'recommendations' in result['details']:
                recommendations = result['details']['recommendations']
                print(f"המלצות: {', '.join(recommendations)}")
                
        except Exception as e:
            print(f"שגיאה בבדיקת {symbol}: {str(e)}")

if __name__ == "__main__":
    test_bollinger_squeeze() 