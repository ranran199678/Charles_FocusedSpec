import sys
import os
sys.path.append('.')

from core.bullish_pattern_spotter import BullishPatternSpotter
from utils.data_fetcher import DataFetcher
import pandas as pd

def test_multiple_stocks():
    print("=== בדיקת תבניות מורכבות במניות שונות ===")
    
    # יצירת סוכן
    agent = BullishPatternSpotter()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # רשימת מניות לבדיקה
    symbols = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT"]
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"מנתח {symbol}")
        print(f"{'='*60}")
        
        try:
            # קבלת נתוני מחיר
            price_df = data_fetcher.get_price_history(symbol, period="100d")
            
            if price_df is None or len(price_df) < 30:
                print(f"❌ אין מספיק נתונים עבור {symbol}")
                continue
            
            # ניתוח מתקדם
            result = agent.analyze(symbol, price_df)
            
            print(f"ציון: {result.get('score', 0)}/100")
            print(f"הסבר: {result.get('explanation', 'N/A')}")
            
            # בדיקת תבניות מורכבות
            details = result.get('details', {})
            complex_patterns = details.get('complex_patterns', {})
            complex_individual = complex_patterns.get('individual_patterns', {})
            
            detected_complex = []
            for pattern_name, pattern_data in complex_individual.items():
                if pattern_data.get('detected', False):
                    detected_complex.append(f"{pattern_name} ({pattern_data.get('strength', 0):.0f})")
            
            if detected_complex:
                print(f"✅ תבניות מורכבות: {', '.join(detected_complex)}")
            else:
                print("❌ אין תבניות מורכבות")
            
            # בדיקת חוזק יחסי
            relative_strength = details.get('relative_strength', {})
            rsi = relative_strength.get('rsi', 50)
            relative_strength_val = relative_strength.get('relative_strength', 0)
            
            print(f"RSI: {rsi:.1f}, חוזק יחסי: {relative_strength_val:+.1f}%")
            
            # בדיקת נפח
            volume_analysis = details.get('volume_analysis', {})
            volume_signal = volume_analysis.get('volume_signal', 'N/A')
            volume_confirmation = volume_analysis.get('volume_confirmation', False)
            
            print(f"נפח: {volume_signal} {'✅' if volume_confirmation else '❌'}")
            
            # המלצות
            recommendations = details.get('recommendations', [])
            if recommendations:
                print(f"המלצה: {recommendations[0]}")
            
        except Exception as e:
            print(f"❌ שגיאה בניתוח {symbol}: {str(e)}")

if __name__ == "__main__":
    test_multiple_stocks() 