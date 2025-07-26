import sys
sys.path.append('.')

from core.macro_trend_scanner import MacroTrendScanner

# בדיקת Macro Trend Scanner
print("=== בדיקת Macro Trend Scanner ===")

# יצירת מופע
macro_scanner = MacroTrendScanner()

# בדיקת מניות שונות
test_symbols = ["AAPL", "JPM", "XOM", "JNJ", "PG"]

for symbol in test_symbols:
    print(f"\n=== ניתוח מאקרו עבור {symbol} ===")
    
    try:
        result = macro_scanner.analyze(symbol)
        
        print(f"ציון מאקרו: {result['score']}/100")
        print(f"סנטימנט: {result['sentiment']}")
        print(f"סיכום: {result['summary']}")
        
        # פרטים נוספים
        details = result.get('details', {})
        
        if 'trend_analysis' in details:
            trends = details['trend_analysis']
            print(f"\nניתוח מגמות:")
            for indicator, trend_data in trends.items():
                direction = trend_data.get('trend_direction', 'stable')
                strength = trend_data.get('trend_strength', 'weak')
                impact = trend_data.get('impact', 'neutral')
                current = trend_data.get('current_value', 0)
                previous = trend_data.get('previous_value', 0)
                
                print(f"  {indicator}: {direction} ({strength}) - השפעה: {impact}")
                print(f"    ערך נוכחי: {current}, ערך קודם: {previous}")
        
        if 'sector_impact' in details:
            sector_impact = details['sector_impact']
            sector = sector_impact.get('sector', 'unknown')
            overall_impact = sector_impact.get('overall_impact', 'neutral')
            positive_factors = sector_impact.get('positive_factors', 0)
            negative_factors = sector_impact.get('negative_factors', 0)
            
            print(f"\nהשפעה על סקטור:")
            print(f"  סקטור: {sector}")
            print(f"  השפעה כוללת: {overall_impact}")
            print(f"  גורמים חיוביים: {positive_factors}")
            print(f"  גורמים שליליים: {negative_factors}")
        
        if 'recommendations' in details:
            recommendations = details['recommendations']
            if recommendations:
                print(f"\nהמלצות:")
                for rec in recommendations:
                    print(f"  - {rec}")
        
    except Exception as e:
        print(f"שגיאה בניתוח {symbol}: {e}")

# השוואה בין מניות
print(f"\n=== השוואה בין מניות ===")
comparison_data = {}

for symbol in test_symbols:
    try:
        result = macro_scanner.analyze(symbol)
        comparison_data[symbol] = {
            'score': result['score'],
            'sentiment': result['sentiment'],
            'sector': result.get('details', {}).get('sector_impact', {}).get('sector', 'unknown')
        }
    except Exception as e:
        print(f"שגיאה ב-{symbol}: {e}")

print(f"\nסיכום השוואה:")
for symbol, data in comparison_data.items():
    print(f"{symbol:6}: ציון {data['score']:3d}/100, סנטימנט: {data['sentiment']:12}, סקטור: {data['sector']}")

# ניתוח מגמות כללי
print(f"\n=== ניתוח מגמות מאקרו כללי ===")
try:
    # בדיקה עם מניה כללית
    general_result = macro_scanner.analyze("SPY")
    
    print(f"ציון מאקרו כללי: {general_result['score']}/100")
    print(f"סנטימנט כללי: {general_result['sentiment']}")
    print(f"סיכום כללי: {general_result['summary']}")
    
    # ניתוח המלצות
    recommendations = general_result.get('details', {}).get('recommendations', [])
    if recommendations:
        print(f"\nהמלצות מאקרו:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
except Exception as e:
    print(f"שגיאה בניתוח כללי: {e}")

print(f"\n=== סיום בדיקת Macro Trend Scanner ===") 