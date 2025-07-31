import sys
sys.path.append('.')

from core.social_media_hype_scanner import SocialMediaHypeScanner

# בדיקת Social Media Hype Scanner
print("=== בדיקת Social Media Hype Scanner ===")

# יצירת מופע
hype_scanner = SocialMediaHypeScanner()

# בדיקת מניות שונות
test_symbols = ["TSLA", "GME", "AAPL", "NVDA", "AMC"]

for symbol in test_symbols:
    print(f"\n=== ניתוח רשתות חברתיות עבור {symbol} ===")
    
    try:
        result = hype_scanner.analyze(symbol)
        
        print(f"ציון Hype: {result['score']}/100")
        print(f"סנטימנט: {result['sentiment']}")
        print(f"סיכום: {result['summary']}")
        
        # פרטים נוספים
        details = result.get('details', {})
        
        if 'sentiment_analysis' in details:
            sentiment = details['sentiment_analysis']
            print(f"\nניתוח סנטימנט:")
            print(f"  סנטימנט דומיננטי: {sentiment.get('dominant_sentiment', 'unknown')}")
            print(f"  ציון סנטימנט: {sentiment.get('overall_sentiment_score', 0)}/100")
            print(f"  סה\"כ אזכורים: {sentiment.get('total_mentions', 0)}")
            
            platform_scores = sentiment.get('platform_scores', {})
            for platform, scores in platform_scores.items():
                print(f"    {platform}: {scores.get('mentions', 0)} אזכורים, ציון {scores.get('sentiment_score', 0)}/100")
        
        if 'hype_analysis' in details:
            hype = details['hype_analysis']
            print(f"\nניתוח Hype:")
            print(f"  רמת Hype: {hype.get('hype_level', 'unknown')}")
            print(f"  מגמת Hype: {hype.get('trend', 'unknown')}")
            print(f"  ציון Hype: {hype.get('overall_hype_score', 0)}/100")
            
            platform_indicators = hype.get('platform_indicators', {})
            for platform, indicators in platform_indicators.items():
                print(f"    {platform}: רמה {indicators.get('hype_level', 'unknown')}, מגמה {indicators.get('trend', 'unknown')}")
        
        if 'trend_analysis' in details:
            trends = details['trend_analysis']
            print(f"\nניתוח מגמות:")
            for platform, trend_data in trends.items():
                volume_trend = trend_data.get('volume_trend', 'unknown')
                sentiment_trend = trend_data.get('sentiment_trend', 'unknown')
                overall_trend = trend_data.get('overall_trend', 'unknown')
                print(f"  {platform}: נפח {volume_trend}, סנטימנט {sentiment_trend}, כולל {overall_trend}")
        
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
        result = hype_scanner.analyze(symbol)
        comparison_data[symbol] = {
            'score': result['score'],
            'sentiment': result['sentiment'],
            'hype_level': result.get('details', {}).get('hype_analysis', {}).get('hype_level', 'unknown'),
            'total_mentions': result.get('details', {}).get('sentiment_analysis', {}).get('total_mentions', 0)
        }
    except Exception as e:
        print(f"שגיאה ב-{symbol}: {e}")

print(f"\nסיכום השוואה:")
for symbol, data in comparison_data.items():
    print(f"{symbol:6}: ציון {data['score']:3d}/100, סנטימנט: {data['sentiment']:12}, hype: {data['hype_level']:8}, אזכורים: {data['total_mentions']:3d}")

# ניתוח מניות עם hype גבוה
print(f"\n=== מניות עם Hype גבוה ===")
high_hype_stocks = []
for symbol, data in comparison_data.items():
    if data['score'] > 70:
        high_hype_stocks.append((symbol, data['score']))

if high_hype_stocks:
    print("מניות עם hype גבוה:")
    for symbol, score in sorted(high_hype_stocks, key=lambda x: x[1], reverse=True):
        print(f"  {symbol}: {score}/100")
else:
    print("אין מניות עם hype גבוה בבדיקה")

# ניתוח מניות עם סנטימנט שלילי
print(f"\n=== מניות עם סנטימנט שלילי ===")
negative_sentiment_stocks = []
for symbol, data in comparison_data.items():
    if 'bearish' in data['sentiment'] or 'very_bearish' in data['sentiment']:
        negative_sentiment_stocks.append((symbol, data['sentiment']))

if negative_sentiment_stocks:
    print("מניות עם סנטימנט שלילי:")
    for symbol, sentiment in negative_sentiment_stocks:
        print(f"  {symbol}: {sentiment}")
else:
    print("אין מניות עם סנטימנט שלילי בבדיקה")

print(f"\n=== סיום בדיקת Social Media Hype Scanner ===") 