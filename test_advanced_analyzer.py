import sys
import os
sys.path.append('.')

from core.advanced_pattern_analyzer import AdvancedPatternAnalyzer
from utils.data_fetcher import DataFetcher
import pandas as pd

def test_advanced_analyzer():
    print("=== בדיקת סוכן ניתוח מתקדם ===")
    
    # יצירת סוכן
    agent = AdvancedPatternAnalyzer()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניות שונות
    symbols = ["INTC", "AAPL", "TSLA", "NVDA"]
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"מנתח {symbol} - ניתוח מתקדם")
        print(f"{'='*60}")
        
        try:
            # קבלת נתוני מחיר
            price_df = data_fetcher.get_price_history(symbol, period="100d")
            
            if price_df is None or len(price_df) < 50:
                print(f"❌ אין מספיק נתונים עבור {symbol}")
                continue
            
            # ניתוח מתקדם
            result = agent.analyze(symbol, price_df)
            
            print(f"ציון מתקדם: {result.get('score', 0)}/100")
            print(f"הסבר: {result.get('explanation', 'N/A')}")
            
            # פרטי תבניות מורכבות
            details = result.get('details', {})
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
                        print(f"   סימטריה: {symmetry:.2f}")
                    elif pattern_name == "bull_flag":
                        pole_rise = pattern_data.get('pole_rise', 0)
                        print(f"   עליית Pole: {pole_rise:.2%}")
                    elif pattern_name == "falling_wedge":
                        high_trend = pattern_data.get('high_trend', 0)
                        low_trend = pattern_data.get('low_trend', 0)
                        print(f"   מגמה עליונה: {high_trend:.4f}, תחתונה: {low_trend:.4f}")
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
            
            # סיכום
            print(f"\n=== סיכום ===")
            score = result.get('score', 0)
            
            if score >= 80:
                print("🎯 סיגנל קנייה חזק מאוד")
            elif score >= 60:
                print("📈 סיגנל קנייה בינוני")
            elif score >= 40:
                print("⚠️ סיגנל מעורב")
            else:
                print("📉 סיגנל שלילי")
            
        except Exception as e:
            print(f"❌ שגיאה בניתוח {symbol}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_advanced_analyzer() 