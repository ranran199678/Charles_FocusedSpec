import sys
import os
sys.path.append('.')

from core.bullish_pattern_spotter import BullishPatternSpotter
from utils.data_fetcher import DataFetcher

def debug_candle_analysis():
    print("=== Debug: ניתוח נרות שליליים ===")
    
    # יצירת סוכן
    agent = BullishPatternSpotter()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת QBTS (נר שלילי)
    symbol = "QBTS"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        print(f"מחיר אחרון: {price_df['close'].iloc[-1]:.2f}")
        print(f"מחיר פתיחה: {price_df['open'].iloc[-1]:.2f}")
        print(f"גוף הנר: {price_df['close'].iloc[-1] - price_df['open'].iloc[-1]:.2f}")
        
        # ניתוח ישיר של הנר הנוכחי
        current_candle = agent._analyze_current_candle(price_df)
        
        print(f"\nניתוח נר נוכחי:")
        print(f"סוג נר: {current_candle.get('candle_type', 'N/A')}")
        print(f"חוזק: {current_candle.get('strength', 'N/A')}")
        print(f"ציון: {current_candle.get('score', 'N/A')}")
        print(f"אחוז גוף: {current_candle.get('body_percentage', 'N/A'):.1f}%")
        
        # ניתוח נפח
        volume_analysis = agent._analyze_volume_pattern(price_df, {})
        print(f"\nניתוח נפח:")
        print(f"נפח נוכחי: {volume_analysis.get('current_volume', 'N/A')}")
        print(f"נפח ממוצע: {volume_analysis.get('avg_volume', 'N/A'):.0f}")
        print(f"יחס נפח: {volume_analysis.get('volume_ratio', 'N/A'):.2f}")
        print(f"ציון נפח: {volume_analysis.get('volume_score', 'N/A')}")
        
        # חישוב ציון כולל
        patterns = agent._identify_bullish_patterns(price_df)
        final_score = agent._calculate_pattern_score(patterns, volume_analysis)
        
        print(f"\nחישוב ציון סופי:")
        print(f"ציון תבניות: {patterns.get('overall_strength', 'N/A')}")
        print(f"ציון נפח: {volume_analysis.get('volume_score', 'N/A')}")
        print(f"ציון סופי: {final_score}/100")
        
        # בדיקה מפורטת של החישוב
        current_candle_data = patterns.get("individual_patterns", {}).get("current_candle", {})
        if current_candle_data.get("detected", False):
            candle_type = current_candle_data.get("candle_type", "")
            strength = current_candle_data.get("strength", 50)
            
            print(f"\nבדיקה מפורטת:")
            print(f"סוג נר: {candle_type}")
            print(f"חוזק: {strength}")
            
            if "בולשי" in candle_type:
                pattern_score = strength
                print(f"נר בולשי - ציון: {pattern_score}")
            elif "שלילי" in candle_type:
                pattern_score = max(1, 100 - strength)
                print(f"נר שלילי - ציון: {pattern_score} (100 - {strength})")
            else:
                pattern_score = 50
                print(f"נר ניטרלי - ציון: {pattern_score}")
            
            # חישוב סופי
            volume_score = volume_analysis.get("volume_score", 50)
            price_weight = agent.price_weight
            volume_weight = agent.volume_weight
            
            final_calc = int((pattern_score * price_weight) + (volume_score * volume_weight))
            print(f"חישוב: ({pattern_score} * {price_weight}) + ({volume_score} * {volume_weight}) = {final_calc}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_candle_analysis() 