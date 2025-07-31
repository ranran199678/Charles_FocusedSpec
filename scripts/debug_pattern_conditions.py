import sys
import os
sys.path.append('.')

from core.bullish_pattern_spotter import BullishPatternSpotter
from utils.data_fetcher import DataFetcher
import pandas as pd

def debug_pattern_conditions():
    print("=== Debug: בדיקת תנאים לתבניות 2-3 נרות ===")
    
    # יצירת סוכן
    agent = BullishPatternSpotter()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת INTC
    symbol = "INTC"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        # 3 הנרות האחרונים
        current = price_df.iloc[-1]
        previous = price_df.iloc[-2]
        third = price_df.iloc[-3]
        
        print(f"=== 3 הנרות האחרונים ===")
        print(f"נר 3 (קודם): {price_df.index[-3].strftime('%Y-%m-%d')}")
        print(f"  Open: {third['open']:.2f}, Close: {third['close']:.2f}, Body: {third['close'] - third['open']:.4f}")
        
        print(f"נר 2 (קודם): {price_df.index[-2].strftime('%Y-%m-%d')}")
        print(f"  Open: {previous['open']:.2f}, Close: {previous['close']:.2f}, Body: {previous['close'] - previous['open']:.4f}")
        
        print(f"נר 1 (נוכחי): {price_df.index[-1].strftime('%Y-%m-%d')}")
        print(f"  Open: {current['open']:.2f}, Close: {current['close']:.2f}, Body: {current['close'] - current['open']:.4f}")
        
        # בדיקת Bullish Engulfing
        print(f"\n=== בדיקת Bullish Engulfing ===")
        current_body = current['close'] - current['open']
        previous_body = previous['close'] - previous['open']
        
        print(f"גוף נוכחי: {current_body:.4f}")
        print(f"גוף קודם: {previous_body:.4f}")
        print(f"נר קודם שלילי: {previous_body < 0}")
        print(f"נר נוכחי חיובי: {current_body > 0}")
        print(f"פתיחה מתחת לסגירה הקודמת: {current['open'] < previous['close']} ({current['open']:.2f} < {previous['close']:.2f})")
        print(f"סגירה מעל הפתיחה הקודמת: {current['close'] > previous['open']} ({current['close']:.2f} > {previous['open']:.2f})")
        
        is_bullish_engulfing = (
            previous_body < 0 and
            current_body > 0 and
            current['open'] < previous['close'] and
            current['close'] > previous['open']
        )
        print(f"תנאי Bullish Engulfing: {is_bullish_engulfing}")
        
        # בדיקת Piercing
        print(f"\n=== בדיקת Piercing ===")
        print(f"נר קודם שלילי: {previous_body < 0}")
        print(f"נר נוכחי חיובי: {current_body > 0}")
        print(f"פתיחה מתחת לסגירה הקודמת: {current['open'] < previous['close']}")
        print(f"סגירה מעל אמצע הנר הקודם: {current['close'] > previous['close'] + previous_body * 0.5}")
        print(f"  אמצע הנר הקודם: {previous['close'] + previous_body * 0.5:.2f}")
        print(f"  סגירה נוכחית: {current['close']:.2f}")
        
        is_piercing = (
            previous_body < 0 and
            current_body > 0 and
            current['open'] < previous['close'] and
            current['close'] > previous['close'] + previous_body * 0.5
        )
        print(f"תנאי Piercing: {is_piercing}")
        
        # בדיקת Morning Star
        print(f"\n=== בדיקת Morning Star ===")
        first_body = third['close'] - third['open']
        second_body = previous['close'] - previous['open']
        third_body = current['close'] - current['open']
        
        print(f"גוף ראשון: {first_body:.4f}")
        print(f"גוף שני: {second_body:.4f}")
        print(f"גוף שלישי: {third_body:.4f}")
        
        print(f"נר ראשון שלילי: {first_body < 0}")
        print(f"נר שני קטן: {abs(second_body) < abs(first_body) * 0.3}")
        print(f"  נדרש: {abs(first_body) * 0.3:.4f}, יש: {abs(second_body):.4f}")
        print(f"נר שלישי חיובי: {third_body > 0}")
        
        mid_first = (third['open'] + third['close']) / 2
        print(f"סגירה מעל אמצע הנר הראשון: {current['close'] > mid_first}")
        print(f"  אמצע הנר הראשון: {mid_first:.2f}")
        print(f"  סגירה נוכחית: {current['close']:.2f}")
        
        is_morning_star = (
            first_body < 0 and
            abs(second_body) < abs(first_body) * 0.3 and
            third_body > 0 and
            current['close'] > mid_first
        )
        print(f"תנאי Morning Star: {is_morning_star}")
        
        # בדיקת Three White Soldiers
        print(f"\n=== בדיקת Three White Soldiers ===")
        candles = [third, previous, current]
        bodies = [candle['close'] - candle['open'] for candle in candles]
        
        print(f"גופי הנרות: {[f'{b:.4f}' for b in bodies]}")
        
        all_bullish = all(body > 0 for body in bodies)
        print(f"כל הנרות חיוביים: {all_bullish}")
        
        increasing = all(bodies[i] <= bodies[i+1] for i in range(len(bodies)-1))
        print(f"נרות גדלים: {increasing}")
        print(f"  {bodies[0]:.4f} <= {bodies[1]:.4f}: {bodies[0] <= bodies[1]}")
        print(f"  {bodies[1]:.4f} <= {bodies[2]:.4f}: {bodies[1] <= bodies[2]}")
        
        opens_within_previous = all(
            candles[i]['open'] >= candles[i-1]['open'] and
            candles[i]['open'] <= candles[i-1]['close']
            for i in range(1, len(candles))
        )
        print(f"פתיחות בתוך גוף הנר הקודם: {opens_within_previous}")
        print(f"  {candles[1]['open']:.2f} >= {candles[0]['open']:.2f} ו- <= {candles[0]['close']:.2f}: {candles[1]['open'] >= candles[0]['open'] and candles[1]['open'] <= candles[0]['close']}")
        print(f"  {candles[2]['open']:.2f} >= {candles[1]['open']:.2f} ו- <= {candles[1]['close']:.2f}: {candles[2]['open'] >= candles[1]['open'] and candles[2]['open'] <= candles[1]['close']}")
        
        is_three_white_soldiers = all_bullish and increasing and opens_within_previous
        print(f"תנאי Three White Soldiers: {is_three_white_soldiers}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pattern_conditions() 