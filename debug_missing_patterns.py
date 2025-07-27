import sys
import os
sys.path.append('.')

from core.bullish_pattern_spotter import BullishPatternSpotter
from utils.data_fetcher import DataFetcher
import pandas as pd

def debug_missing_patterns():
    print("=== Debug: למה לא מוצגות תבניות 2-3 נרות ופרטי נפח ===")
    
    # יצירת סוכן
    agent = BullishPatternSpotter()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת INTC
    symbol = "INTC"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        print(f"=== בדיקת תבניות 2-3 נרות ===")
        
        # בדיקה ישירה של כל תבנית
        print(f"\n1. Bullish Engulfing:")
        engulfing_result = agent._detect_bullish_engulfing(price_df)
        print(f"   זוהה: {engulfing_result.get('detected', False)}")
        if engulfing_result.get('detected', False):
            print(f"   חוזק: {engulfing_result.get('strength', 0):.1f}")
            print(f"   גוף נוכחי: {engulfing_result.get('current_body', 0):.4f}")
            print(f"   גוף קודם: {engulfing_result.get('previous_body', 0):.4f}")
        
        print(f"\n2. Piercing:")
        piercing_result = agent._detect_piercing(price_df)
        print(f"   זוהה: {piercing_result.get('detected', False)}")
        if piercing_result.get('detected', False):
            print(f"   חוזק: {piercing_result.get('strength', 0):.1f}")
            print(f"   גוף נוכחי: {piercing_result.get('current_body', 0):.4f}")
            print(f"   גוף קודם: {piercing_result.get('previous_body', 0):.4f}")
        
        print(f"\n3. Morning Star:")
        morning_star_result = agent._detect_morning_star(price_df)
        print(f"   זוהה: {morning_star_result.get('detected', False)}")
        if morning_star_result.get('detected', False):
            print(f"   חוזק: {morning_star_result.get('strength', 0):.1f}")
            print(f"   גוף ראשון: {morning_star_result.get('first_body', 0):.4f}")
            print(f"   גוף שני: {morning_star_result.get('second_body', 0):.4f}")
            print(f"   גוף שלישי: {morning_star_result.get('third_body', 0):.4f}")
        
        print(f"\n4. Three White Soldiers:")
        three_soldiers_result = agent._detect_three_white_soldiers(price_df)
        print(f"   זוהה: {three_soldiers_result.get('detected', False)}")
        if three_soldiers_result.get('detected', False):
            print(f"   חוזק: {three_soldiers_result.get('strength', 0):.1f}")
            print(f"   גופים: {three_soldiers_result.get('bodies', [])}")
        
        # בדיקת נרות אחרונים
        print(f"\n=== 3 הנרות האחרונים ===")
        for i in range(3):
            idx = -(i+1)
            candle = price_df.iloc[idx]
            date = price_df.index[idx]
            body = candle['close'] - candle['open']
            print(f"{i+1}. {date.strftime('%Y-%m-%d')}: Open={candle['open']:.2f}, Close={candle['close']:.2f}, Body={body:.4f}")
        
        # בדיקת ניתוח נפח מפורט
        print(f"\n=== ניתוח נפח מפורט ===")
        patterns = agent._identify_bullish_patterns(price_df)
        volume_analysis = agent._analyze_volume_pattern(price_df, patterns)
        
        print(f"נפח נוכחי: {volume_analysis.get('current_volume', 'N/A'):,.0f}")
        print(f"נפח ממוצע (20 ימים): {volume_analysis.get('avg_volume', 'N/A'):,.0f}")
        print(f"יחס נפח: {volume_analysis.get('volume_ratio', 'N/A'):.2f}")
        print(f"סיגנל נפח: {volume_analysis.get('volume_signal', 'N/A')}")
        print(f"ציון נפח: {volume_analysis.get('volume_score', 'N/A')}/100")
        print(f"מגמת נפח: {volume_analysis.get('volume_trend', 'N/A')}")
        print(f"יחס מגמה: {volume_analysis.get('recent_volume_trend', 'N/A'):.2f}")
        
        # בדיקת נפחים אחרונים
        print(f"\n=== 5 הנפחים האחרונים ===")
        volume = price_df["volume"]
        for i in range(5):
            idx = -(i+1)
            vol = volume.iloc[idx]
            date = price_df.index[idx]
            print(f"{i+1}. {date.strftime('%Y-%m-%d')}: {vol:,.0f}")
        
        # בדיקת ממוצע נפח
        avg_volume_20 = volume.rolling(20).mean().iloc[-1]
        recent_avg_5 = volume.tail(5).mean()
        recent_avg_20 = volume.tail(20).mean()
        
        print(f"\n=== חישובי נפח ===")
        print(f"ממוצע 20 ימים: {avg_volume_20:,.0f}")
        print(f"ממוצע 5 ימים אחרונים: {recent_avg_5:,.0f}")
        print(f"ממוצע 20 ימים אחרונים: {recent_avg_20:,.0f}")
        print(f"יחס 5/20: {recent_avg_5/recent_avg_20:.2f}")
        
        # בדיקת ניתוח מלא
        print(f"\n=== ניתוח מלא ===")
        result = agent.analyze(symbol, price_df)
        print(f"ציון: {result.get('score', 'N/A')}/100")
        print(f"הסבר: {result.get('explanation', 'N/A')}")
        
        # בדיקת פרטים
        if 'details' in result and 'volume_analysis' in result['details']:
            vol_details = result['details']['volume_analysis']
            print(f"\nפרטי נפח מהתוצאה:")
            for key, value in vol_details.items():
                if isinstance(value, (int, float)):
                    if 'volume' in key and value > 1000:
                        print(f"  {key}: {value:,.0f}")
                    else:
                        print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_missing_patterns() 