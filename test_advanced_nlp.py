import sys
sys.path.append('.')

from core.nlp_analyzer import NLPAnalyzer

# בדיקת NLP Analyzer מתקדם
symbol = "INTC"

print(f"=== בדיקת NLP Analyzer מתקדם עבור {symbol} ===")

analyzer = NLPAnalyzer()

print(f"\n=== ניתוח מתקדם ===")
result = analyzer.analyze(symbol)

print(f"ציון: {result['score']}/100")
print(f"סנטימנט: {result['sentiment']}")
print(f"סיכום: {result['summary']}")

print(f"\n=== פרטים מתקדמים ===")
details = result['details']

# ניתוח מגמות
if 'trend_analysis' in details:
    trend = details['trend_analysis']
    print(f"\nניתוח מגמות:")
    print(f"  כיוון מגמה: {trend.get('trend_direction', 'stable')}")
    print(f"  עוצמת מגמה: {trend.get('trend_strength', 0):.1%}")
    print(f"  שינוי אחרון: {trend.get('recent_change', 0):.3f}")
    
    daily_sentiments = trend.get('daily_sentiments', {})
    if daily_sentiments:
        print(f"  סנטימנט יומי:")
        for date, sentiments in daily_sentiments.items():
            print(f"    {date}: חיובי={sentiments['positive']}, שלילי={sentiments['negative']}, ניטרלי={sentiments['neutral']}")

# זיהוי אירועים
if 'event_analysis' in details:
    events = details['event_analysis']
    print(f"\nזיהוי אירועים:")
    print(f"  סך הכל אירועים: {events.get('total_events', 0)}")
    
    event_importance = events.get('importance', {})
    if event_importance:
        print(f"  חשיבות אירועים:")
        for event_type, importance in event_importance.items():
            if importance > 0:
                print(f"    {event_type}: {importance:.2f}")
    
    all_events = events.get('events', {})
    for event_type, event_list in all_events.items():
        if event_list:
            print(f"  {event_type}:")
            for event in event_list[:2]:  # רק 2 הראשונים
                print(f"    - {event.get('title', 'No title')} ({event.get('sentiment', 'neutral')})")

# ניתוח הקשר שוק
if 'market_context' in details:
    market = details['market_context']
    print(f"\nניתוח הקשר שוק:")
    
    competitors = market.get('competitor_mentions', [])
    if competitors:
        print(f"  אזכורי מתחרים:")
        for comp in competitors:
            print(f"    {comp.get('competitor', 'Unknown')}: {comp.get('context', 'No context')} ({comp.get('sentiment', 'neutral')})")
    
    industry_trends = market.get('industry_trends', [])
    if industry_trends:
        print(f"  מגמות תעשייה:")
        for trend in industry_trends:
            print(f"    {trend.get('trend', 'Unknown')}: {trend.get('context', 'No context')} ({trend.get('sentiment', 'neutral')})")

# ניתוח סנטימנט
if 'sentiment_analysis' in details:
    sent = details['sentiment_analysis']
    print(f"\nניתוח סנטימנט:")
    print(f"  סנטימנט דומיננטי: {sent.get('dominant_sentiment', 'N/A')}")
    print(f"  ציון ממוצע: {sent.get('average_score', 0):.3f}")
    print(f"  ביטחון: {sent.get('confidence', 0):.1%}")
    print(f"  טקסטים חיוביים: {sent.get('positive_count', 0)}")
    print(f"  טקסטים שליליים: {sent.get('negative_count', 0)}")
    print(f"  טקסטים ניטרליים: {sent.get('neutral_count', 0)}")

# ניתוח השפעה
if 'impact_analysis' in details:
    impact = details['impact_analysis']
    print(f"\nניתוח השפעה:")
    print(f"  ציון השפעה: {impact.get('impact_score', 0)}")
    print(f"  כמות טקסטים: {impact.get('text_count', 0)}")
    print(f"  כמות מילות מפתח: {impact.get('keyword_count', 0)}")
    print(f"  השפעת סנטימנט: {impact.get('sentiment_influence', 0):.3f}")

print(f"\n=== נושאים זוהו ===")
for i, topic in enumerate(result['topics'], 1):
    print(f"{i}. קטגוריה: {topic['category']}")
    print(f"   מילות מפתח: {topic['keywords']}")
    print(f"   תדירות: {topic['frequency']}")
    print(f"   חשיבות: {topic['importance']}")

print(f"\n=== ביטויים מפתח ===")
for i, phrase in enumerate(result['key_phrases'][:5], 1):
    print(f"{i}. {phrase}")

print(f"\n=== השוואה עם AAPL ===")
result_aapl = analyzer.analyze("AAPL")

print(f"INTC Score: {result['score']}/100")
print(f"AAPL Score: {result_aapl['score']}/100")
print(f"הבדל: {result['score'] - result_aapl['score']} נקודות")

print(f"INTC Sentiment: {result['sentiment']}")
print(f"AAPL Sentiment: {result_aapl['sentiment']}")

print(f"\n=== יכולות מתקדמות ===")
print("✅ ניתוח מגמות לאורך זמן")
print("✅ זיהוי אירועים חשובים")
print("✅ ניתוח הקשר שוק")
print("✅ זיהוי מתחרים")
print("✅ זיהוי מגמות תעשייה")
print("✅ חישוב ציון מתקדם")
print("✅ סיכום מתקדם")

print(f"\n=== הסבר הציון {result['score']} ===")
if result['score'] >= 80:
    print("ציון גבוה מאוד - הרבה טקסטים חיוביים עם מגמות חיוביות")
elif result['score'] >= 60:
    print("ציון גבוה - טקסטים חיוביים עם נושאים חשובים")
elif result['score'] >= 40:
    print("ציון בינוני - טקסטים מעורבים")
elif result['score'] >= 20:
    print("ציון נמוך - מעט טקסטים או שליליים")
else:
    print("ציון נמוך מאוד - טקסטים שליליים או מעטים") 