import sys
import os
sys.path.append('.')

from core.bullish_pattern_spotter import BullishPatternSpotter
from utils.data_fetcher import DataFetcher
import pandas as pd

def test_enhanced_pattern_spotter():
    print("=== בדיקת סוכן תבניות בולשיות מתקדם ===")
    
    # יצירת סוכן
    agent = BullishPatternSpotter()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת INTC
    symbol = "INTC"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        print(f"מנתח {symbol} עם {len(price_df)} ימים של נתונים...")
        
        # ניתוח מתקדם
        result = agent.analyze(symbol, price_df)
        
        print(f"\n=== תוצאות ניתוח מתקדם ===")
        print(f"ציון כללי: {result.get('score', 'N/A')}/100")
        print(f"הסבר: {result.get('explanation', 'N/A')}")
        
        # פרטי תבניות קנדלסטיק
        details = result.get('details', {})
        candlestick_patterns = details.get('candlestick_patterns', {})
        
        print(f"\n=== תבניות קנדלסטיק ===")
        individual_patterns = candlestick_patterns.get('individual_patterns', {})
        for pattern_name, pattern_data in individual_patterns.items():
            if pattern_data.get('detected', False):
                print(f"✅ {pattern_name}: חוזק {pattern_data.get('strength', 0):.1f}")
            else:
                print(f"❌ {pattern_name}: לא זוהה")
        
        print(f"סה\"כ תבניות: {candlestick_patterns.get('total_patterns', 0)}")
        print(f"חוזק כללי: {candlestick_patterns.get('overall_strength', 0):.2f}")
        
        # פרטי תבניות מורכבות
        complex_patterns = details.get('complex_patterns', {})
        
        print(f"\n=== תבניות מורכבות ===")
        complex_individual = complex_patterns.get('individual_patterns', {})
        for pattern_name, pattern_data in complex_individual.items():
            if pattern_data.get('detected', False):
                print(f"✅ {pattern_name}: חוזק {pattern_data.get('strength', 0):.1f}")
                # פרטים נוספים
                if pattern_name == "cup_and_handle":
                    print(f"   Cup: {pattern_data.get('cup_start', 0):.2f} -> {pattern_data.get('cup_end', 0):.2f}")
                    print(f"   Handle decline: {pattern_data.get('handle_decline', 0):.2%}")
                elif pattern_name == "bull_flag":
                    print(f"   Pole rise: {pattern_data.get('pole_rise', 0):.2%}")
                    print(f"   Volume ratio: {pattern_data.get('volume_ratio', 0):.2f}")
                elif pattern_name == "double_bottom":
                    print(f"   Bottoms: {pattern_data.get('bottom1', 0):.2f}, {pattern_data.get('bottom2', 0):.2f}")
                    print(f"   Rise between: {pattern_data.get('rise_between', 0):.2%}")
            else:
                print(f"❌ {pattern_name}: לא זוהה")
        
        print(f"סה\"כ תבניות מורכבות: {complex_patterns.get('total_patterns', 0)}")
        print(f"חוזק כללי: {complex_patterns.get('overall_strength', 0):.2f}")
        
        # ניתוח חוזק יחסי
        relative_strength = details.get('relative_strength', {})
        
        print(f"\n=== ניתוח חוזק יחסי ===")
        print(f"RSI: {relative_strength.get('rsi', 0):.1f} (ציון: {relative_strength.get('rsi_score', 0):.0f})")
        print(f"חוזק יחסי: {relative_strength.get('relative_strength', 0):+.1f}% (ציון: {relative_strength.get('relative_strength_score', 0):.0f})")
        print(f"תנודתיות: {relative_strength.get('volatility', 0):.2%}")
        print(f"חוזק מגמה: {relative_strength.get('trend_strength', 0):.0f}")
        print(f"SMA 20: {relative_strength.get('sma_20', 0):.2f}")
        print(f"SMA 50: {relative_strength.get('sma_50', 0):.2f}")
        print(f"ציון כללי: {relative_strength.get('overall_score', 0):.0f}")
        
        # ניתוח נפח מתקדם
        volume_analysis = details.get('volume_analysis', {})
        
        print(f"\n=== ניתוח נפח מתקדם ===")
        print(f"נפח נוכחי: {volume_analysis.get('current_volume', 0):,.0f}")
        print(f"נפח ממוצע (20 ימים): {volume_analysis.get('avg_volume', 0):,.0f}")
        print(f"יחס נפח: {volume_analysis.get('volume_ratio', 0):.2f}")
        print(f"סיגנל נפח: {volume_analysis.get('volume_signal', 'N/A')}")
        print(f"ציון נפח: {volume_analysis.get('volume_score', 0):.0f}/100")
        print(f"מגמת נפח: {volume_analysis.get('volume_trend', 'N/A')}")
        print(f"יחס מגמה: {volume_analysis.get('recent_volume_trend', 0):.2f}")
        print(f"VPT מגמה: {volume_analysis.get('vpt_trend', 'N/A')}")
        print(f"OBV מגמה: {volume_analysis.get('obv_trend', 'N/A')}")
        print(f"אישור נפח: {'✅' if volume_analysis.get('volume_confirmation', False) else '❌'}")
        
        # המלצות
        recommendations = details.get('recommendations', [])
        
        print(f"\n=== המלצות מתקדמות ===")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        # סיכום כללי
        print(f"\n=== סיכום כללי ===")
        print(f"ציון סופי: {result.get('score', 0)}/100")
        
        if result.get('score', 0) >= 80:
            print("🎯 סיגנל קנייה חזק מאוד")
        elif result.get('score', 0) >= 60:
            print("📈 סיגנל קנייה בינוני")
        elif result.get('score', 0) >= 40:
            print("⚠️ סיגנל מעורב")
        else:
            print("📉 סיגנל שלילי")
        
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_pattern_spotter() 