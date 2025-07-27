import sys
import os
sys.path.append('.')

from core.bullish_pattern_spotter import BullishPatternSpotter
from utils.data_fetcher import DataFetcher
import pandas as pd

def debug_intc_analysis():
    print("=== Debug: ניתוח מפורט של INTC ===")
    
    # יצירת סוכן
    agent = BullishPatternSpotter()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת INTC
    symbol = "INTC"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        print(f"=== נתוני מחיר אחרונים ===")
        print(f"תאריכים: {price_df.index[0]} עד {price_df.index[-1]}")
        print(f"מספר שורות: {len(price_df)}")
        
        # 5 השורות האחרונות
        print(f"\n=== 5 השורות האחרונות ===")
        last_5 = price_df.tail(5)
        for i, (date, row) in enumerate(last_5.iterrows()):
            print(f"{i+1}. {date.strftime('%Y-%m-%d')}: Open={row['open']:.2f}, Close={row['close']:.2f}, High={row['high']:.2f}, Low={row['low']:.2f}, Volume={row['volume']:,.0f}")
        
        # נר אחרון מפורט
        current = price_df.iloc[-1]
        print(f"\n=== נר אחרון מפורט ===")
        print(f"תאריך: {price_df.index[-1].strftime('%Y-%m-%d')}")
        print(f"פתיחה: {current['open']:.2f}")
        print(f"סגירה: {current['close']:.2f}")
        print(f"גבוה: {current['high']:.2f}")
        print(f"נמוך: {current['low']:.2f}")
        print(f"נפח: {current['volume']:,.0f}")
        
        # חישובים
        body = current['close'] - current['open']
        total_range = current['high'] - current['low']
        body_percent = (body / total_range * 100) if total_range > 0 else 0
        
        print(f"\n=== חישובים ===")
        print(f"גוף הנר: {body:.2f}")
        print(f"טווח כולל: {total_range:.2f}")
        print(f"אחוז גוף: {body_percent:.1f}%")
        print(f"סוג נר: {'בולשי' if body > 0 else 'שלילי'}")
        
        # ניתוח תבניות
        print(f"\n=== ניתוח תבניות ===")
        patterns = agent._identify_bullish_patterns(price_df)
        
        print(f"סה\"כ תבניות: {patterns.get('total_patterns', 'N/A')}")
        print(f"חוזק כללי: {patterns.get('overall_strength', 'N/A'):.2f}")
        
        individual_patterns = patterns.get("individual_patterns", {})
        for pattern_name, pattern_data in individual_patterns.items():
            if pattern_data.get("detected", False):
                strength = pattern_data.get("strength", 0)
                print(f"✅ {pattern_name}: {strength:.1f}/100")
                
                # פרטים נוספים לכל תבנית
                if pattern_name == "doji":
                    body = pattern_data.get("body", 0)
                    total_range = pattern_data.get("total_range", 0)
                    print(f"   - גוף: {body:.4f}, טווח: {total_range:.4f}")
                elif pattern_name == "current_candle":
                    candle_type = pattern_data.get("candle_type", "")
                    score = pattern_data.get("score", 0)
                    print(f"   - סוג: {candle_type}, ציון: {score:.1f}")
            else:
                print(f"❌ {pattern_name}: לא זוהה")
        
        # ניתוח נפח
        print(f"\n=== ניתוח נפח ===")
        volume_analysis = agent._analyze_volume_pattern(price_df, patterns)
        
        print(f"נפח נוכחי: {volume_analysis.get('current_volume', 'N/A'):,.0f}")
        print(f"נפח ממוצע (20 ימים): {volume_analysis.get('avg_volume', 'N/A'):,.0f}")
        print(f"יחס נפח: {volume_analysis.get('volume_ratio', 'N/A'):.2f}")
        print(f"סיגנל נפח: {volume_analysis.get('volume_signal', 'N/A')}")
        print(f"ציון נפח: {volume_analysis.get('volume_score', 'N/A')}/100")
        print(f"מגמת נפח: {volume_analysis.get('volume_trend', 'N/A')}")
        
        # חישוב ציון סופי
        print(f"\n=== חישוב ציון סופי ===")
        final_score = agent._calculate_pattern_score(patterns, volume_analysis)
        
        # בדיקה מפורטת של החישוב
        bullish_patterns = []
        for pattern_name, pattern_data in individual_patterns.items():
            if pattern_data.get("detected", False) and pattern_name != "current_candle":
                bullish_patterns.append(pattern_name)
        
        if bullish_patterns:
            pattern_strength = patterns.get("overall_strength", 0)
            pattern_score = min(100, pattern_strength * 100)
            print(f"יש תבניות בולשיות: {bullish_patterns}")
            print(f"ציון תבניות: {pattern_score:.1f}")
        else:
            current_candle = individual_patterns.get("current_candle", {})
            if current_candle.get("detected", False):
                candle_type = current_candle.get("candle_type", "")
                strength = current_candle.get("strength", 50)
                
                if "בולשי" in candle_type:
                    pattern_score = strength
                    print(f"נר בולשי - ציון: {pattern_score:.1f}")
                elif "שלילי" in candle_type:
                    pattern_score = max(1, 100 - strength)
                    print(f"נר שלילי - ציון: {pattern_score:.1f}")
                else:
                    pattern_score = 50
                    print(f"נר ניטרלי - ציון: {pattern_score:.1f}")
            else:
                pattern_score = 30
                print(f"אין נר נוכחי - ציון: {pattern_score}")
        
        volume_score = volume_analysis.get("volume_score", 50)
        price_weight = agent.price_weight
        volume_weight = agent.volume_weight
        
        final_calc = int((pattern_score * price_weight) + (volume_score * volume_weight))
        print(f"חישוב: ({pattern_score:.1f} * {price_weight}) + ({volume_score} * {volume_weight}) = {final_calc}")
        print(f"ציון סופי: {final_score}/100")
        
        # ניתוח מלא
        print(f"\n=== ניתוח מלא ===")
        result = agent.analyze(symbol, price_df)
        print(f"ציון: {result.get('score', 'N/A')}/100")
        print(f"הסבר: {result.get('explanation', 'N/A')}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_intc_analysis() 