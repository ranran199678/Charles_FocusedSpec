import sys
import os
sys.path.append('.')

from core.advanced_pattern_analyzer import AdvancedPatternAnalyzer
from core.bullish_pattern_spotter import BullishPatternSpotter
from utils.data_fetcher import DataFetcher
import pandas as pd

def test_qbts():
    print("=== בדיקת QBTS עם סוכן מתקדם ===")
    
    # יצירת סוכנים
    advanced_agent = AdvancedPatternAnalyzer()
    basic_agent = BullishPatternSpotter()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    symbol = "QBTS"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        if price_df is None or len(price_df) < 50:
            print(f"❌ אין מספיק נתונים עבור {symbol}")
            return
        
        print(f"מנתח {symbol} עם {len(price_df)} ימים של נתונים...")
        
        # ניתוח מתקדם
        print(f"\n{'='*60}")
        print(f"ניתוח מתקדם - QBTS")
        print(f"{'='*60}")
        
        advanced_result = advanced_agent.analyze(symbol, price_df)
        
        print(f"ציון מתקדם: {advanced_result.get('score', 0)}/100")
        print(f"הסבר: {advanced_result.get('explanation', 'N/A')}")
        
        # פרטי תבניות מורכבות
        details = advanced_result.get('details', {})
        complex_patterns = details.get('complex_patterns', {})
        
        print(f"\n=== תבניות מורכבות ===")
        individual_patterns = complex_patterns.get('individual_patterns', {})
        detected_count = 0
        
        for pattern_name, pattern_data in individual_patterns.items():
            if pattern_data.get('detected', False):
                detected_count += 1
                strength = pattern_data.get('strength', 0)
                print(f"✅ {pattern_name}: חוזק {strength:.1f}")
                
                # פרטים נוספים
                if pattern_name == "cup_and_handle":
                    symmetry = pattern_data.get('symmetry_score', 0)
                    handle_decline = pattern_data.get('handle_decline', 0)
                    print(f"   סימטריה: {symmetry:.2f}")
                    print(f"   ירידת Handle: {handle_decline:.2%}")
                elif pattern_name == "bull_flag":
                    pole_rise = pattern_data.get('pole_rise', 0)
                    print(f"   עליית Pole: {pole_rise:.2%}")
                elif pattern_name == "falling_wedge":
                    high_trend = pattern_data.get('high_trend', 0)
                    low_trend = pattern_data.get('low_trend', 0)
                    print(f"   מגמה עליונה: {high_trend:.4f}, תחתונה: {low_trend:.4f}")
                elif pattern_name == "channel_breakout":
                    breakout_strength = pattern_data.get('breakout_strength', 0)
                    print(f"   חוזק פריצה: {breakout_strength:.2%}")
                elif pattern_name == "consolidation_breakout":
                    consolidation_range = pattern_data.get('consolidation_range', 0)
                    direction = pattern_data.get('breakout_direction', 'none')
                    print(f"   טווח קונסולידציה: {consolidation_range:.2%}")
                    print(f"   כיוון פריצה: {direction}")
            else:
                print(f"❌ {pattern_name}: לא זוהה")
        
        print(f"סה\"כ תבניות מורכבות: {detected_count}")
        print(f"איכות תבניות: {complex_patterns.get('pattern_quality', 0):.1f}")
        
        # ניתוח שוק
        market_analysis = details.get('market_analysis', {})
        
        print(f"\n=== ניתוח יחסי לשוק ===")
        performance_20d = market_analysis.get('performance_20d', 0)
        performance_50d = market_analysis.get('performance_50d', 0)
        volatility = market_analysis.get('volatility', 0)
        trend_strength = market_analysis.get('trend_strength', 0)
        
        print(f"ביצועים 20 ימים: {performance_20d:+.1f}%")
        print(f"ביצועים 50 ימים: {performance_50d:+.1f}%")
        print(f"תנודתיות: {volatility:.2%}")
        print(f"חוזק מגמה: {trend_strength:.0f}")
        print(f"ציון כללי: {market_analysis.get('overall_score', 0):.0f}")
        
        # ניתוח נפח מתקדם
        volume_analysis = details.get('volume_analysis', {})
        
        print(f"\n=== ניתוח נפח מתקדם ===")
        volume_ratio = volume_analysis.get('volume_ratio', 1)
        volume_patterns = volume_analysis.get('volume_patterns', {})
        obv_trend = volume_analysis.get('obv_trend', 'N/A')
        vpt_trend = volume_analysis.get('vpt_trend', 'N/A')
        
        print(f"יחס נפח: {volume_ratio:.2f}")
        print(f"שיא נפח: {'✅' if volume_patterns.get('volume_surge', False) else '❌'}")
        print(f"אי התאמה: {'✅' if volume_patterns.get('volume_divergence', False) else '❌'}")
        print(f"הצטברות: {'✅' if volume_patterns.get('accumulation', False) else '❌'}")
        print(f"OBV מגמה: {obv_trend}")
        print(f"VPT מגמה: {vpt_trend}")
        print(f"ציון נפח: {volume_analysis.get('overall_score', 0):.0f}")
        
        # ניתוח מגמות
        trend_analysis = details.get('trend_analysis', {})
        
        print(f"\n=== ניתוח מגמות ===")
        trends = trend_analysis.get('trends', {})
        consistency = trend_analysis.get('consistency', 0)
        strength = trend_analysis.get('strength', 0)
        overall_trend = trend_analysis.get('overall_trend', 'N/A')
        
        print(f"מגמה קצרה: {trends.get('short_term', 0):.4f}")
        print(f"מגמה בינונית: {trends.get('medium_term', 0):.4f}")
        print(f"מגמה ארוכה: {trends.get('long_term', 0):.4f}")
        print(f"עקביות: {consistency:.2f}")
        print(f"חוזק: {strength:.0f}")
        print(f"מגמה כללית: {overall_trend}")
        
        # תמיכה והתנגדות
        support_resistance = details.get('support_resistance', {})
        
        print(f"\n=== תמיכה והתנגדות ===")
        position = support_resistance.get('position', 'middle')
        resistance_distance = support_resistance.get('resistance_distance', 0)
        support_distance = support_resistance.get('support_distance', 0)
        
        print(f"מיקום: {position}")
        print(f"מרחק מהתנגדות: {resistance_distance:.2%}")
        print(f"מרחק מתמיכה: {support_distance:.2%}")
        
        # המלצות
        recommendations = details.get('recommendations', [])
        
        print(f"\n=== המלצות מתקדמות ===")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        # ניתוח בסיסי להשוואה
        print(f"\n{'='*60}")
        print(f"ניתוח בסיסי - QBTS")
        print(f"{'='*60}")
        
        basic_result = basic_agent.analyze(symbol, price_df)
        
        print(f"ציון בסיסי: {basic_result.get('score', 0)}/100")
        print(f"הסבר: {basic_result.get('explanation', 'N/A')}")
        
        # השוואה
        print(f"\n{'='*60}")
        print(f"השוואה בין הניתוחים")
        print(f"{'='*60}")
        
        advanced_score = advanced_result.get('score', 0)
        basic_score = basic_result.get('score', 0)
        
        print(f"ציון מתקדם: {advanced_score}/100")
        print(f"ציון בסיסי: {basic_score}/100")
        print(f"הבדל: {advanced_score - basic_score:+d} נקודות")
        
        # סיכום
        print(f"\n=== סיכום QBTS ===")
        
        if advanced_score >= 80:
            print("🎯 סיגנל קנייה חזק מאוד")
        elif advanced_score >= 60:
            print("📈 סיגנל קנייה בינוני")
        elif advanced_score >= 40:
            print("⚠️ סיגנל מעורב")
        else:
            print("📉 סיגנל שלילי")
        
        # פרטי מחיר
        current_price = price_df['close'].iloc[-1]
        price_change = (current_price / price_df['close'].iloc[-2] - 1) * 100
        print(f"מחיר נוכחי: ${current_price:.2f} ({price_change:+.2f}%)")
        
    except Exception as e:
        print(f"❌ שגיאה בניתוח {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qbts() 