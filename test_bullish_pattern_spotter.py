import sys
import os
sys.path.append('.')

from core.bullish_pattern_spotter import BullishPatternSpotter
from utils.data_fetcher import DataFetcher

def test_bullish_pattern_spotter():
    print("=== בדיקת BullishPatternSpotter ===")
    
    # יצירת סוכן
    agent = BullishPatternSpotter()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניות
    symbols = ["INTC", "QBTS", "AAPL"]
    
    for symbol in symbols:
        print(f"\n--- {symbol} ---")
        
        try:
            # קבלת נתוני מחיר
            price_df = data_fetcher.get_price_history(symbol, period="100d")
            
            print(f"מחיר אחרון: {price_df['close'].iloc[-1]:.2f}")
            print(f"תאריכים: {price_df.index[0]} עד {price_df.index[-1]}")
            
            # ניתוח
            result = agent.analyze(symbol, price_df)
            
            print(f"ציון: {result.get('score', 'N/A')}/100")
            print(f"הסבר: {result.get('explanation', 'N/A')}")
            
            # פרטים נוספים
            if 'details' in result and 'patterns' in result['details']:
                patterns = result['details']['patterns']
                individual_patterns = patterns.get('individual_patterns', {})
                
                print(f"סה\"כ תבניות: {patterns.get('total_patterns', 'N/A')}")
                print(f"חוזק כללי: {patterns.get('overall_strength', 'N/A'):.2f}")
                
                # תבניות ספציפיות
                for pattern_name, pattern_data in individual_patterns.items():
                    if pattern_data.get('detected', False):
                        strength = pattern_data.get('strength', 0)
                        print(f"✅ {pattern_name}: {strength:.1f}/100")
                    else:
                        print(f"❌ {pattern_name}: לא זוהה")
                
                # נר נוכחי
                current_candle = individual_patterns.get('current_candle', {})
                if current_candle.get('detected', False):
                    candle_type = current_candle.get('candle_type', 'N/A')
                    body_percent = current_candle.get('body_percentage', 0)
                    print(f"נר נוכחי: {candle_type} ({body_percent:.1f}% גוף)")
            
            # המלצות
            if 'details' in result and 'recommendations' in result['details']:
                recommendations = result['details']['recommendations']
                print(f"המלצות: {', '.join(recommendations)}")
            
        except Exception as e:
            print(f"שגיאה: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_bullish_pattern_spotter() 