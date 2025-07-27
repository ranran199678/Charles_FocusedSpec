import sys
import os
sys.path.append('.')

from core.bullish_pattern_spotter import BullishPatternSpotter
from utils.data_fetcher import DataFetcher

def debug_final_score():
    print("=== Debug: חישוב ציון סופי ===")
    
    # יצירת סוכן
    agent = BullishPatternSpotter()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת QBTS (נר שלילי)
    symbol = "QBTS"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        # ניתוח מלא
        result = agent.analyze(symbol, price_df)
        
        print(f"ציון סופי: {result.get('score', 'N/A')}/100")
        print(f"הסבר: {result.get('explanation', 'N/A')}")
        
        # בדיקה מפורטת
        if 'details' in result and 'patterns' in result['details']:
            patterns = result['details']['patterns']
            volume_analysis = result['details'].get('volume_analysis', {})
            
            print(f"\nפירוט חישוב:")
            print(f"סה\"כ תבניות: {patterns.get('total_patterns', 'N/A')}")
            print(f"חוזק כללי: {patterns.get('overall_strength', 'N/A')}")
            
            current_candle = patterns.get("individual_patterns", {}).get("current_candle", {})
            if current_candle.get("detected", False):
                candle_type = current_candle.get("candle_type", "")
                strength = current_candle.get("strength", 50)
                
                print(f"סוג נר: {candle_type}")
                print(f"חוזק: {strength}")
                
                if "בולשי" in candle_type:
                    pattern_score = strength
                    print(f"נר בולשי - ציון: {pattern_score}")
                elif "שלילי" in candle_type:
                    pattern_score = max(1, 100 - strength)
                    print(f"נר שלילי - ציון: {pattern_score}")
                else:
                    pattern_score = 50
                    print(f"נר ניטרלי - ציון: {pattern_score}")
                
                # חישוב סופי
                volume_score = volume_analysis.get("volume_score", 50)
                price_weight = agent.price_weight
                volume_weight = agent.volume_weight
                
                final_calc = int((pattern_score * price_weight) + (volume_score * volume_weight))
                print(f"חישוב: ({pattern_score} * {price_weight}) + ({volume_score} * {volume_weight}) = {final_calc}")
                print(f"ציון בפועל: {result.get('score', 'N/A')}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_final_score() 