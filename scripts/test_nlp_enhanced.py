import sys
sys.path.append('.')

from core.nlp_analyzer import NLPAnalyzer

# בדיקת NLP Analyzer עם מקורות חדשים
symbol = "INTC"

print(f"=== בדיקת NLP Analyzer עם מקורות חדשים עבור {symbol} ===")

analyzer = NLPAnalyzer()

print(f"\n=== ניתוח NLP ===")
result = analyzer.analyze(symbol)

print(f"ציון: {result['score']}/100")
print(f"סנטימנט: {result['sentiment']}")
print(f"סיכום: {result['summary']}")

print(f"\n=== פרטים מלאים ===")
details = result['details']

if 'sentiment_analysis' in details:
    sent = details['sentiment_analysis']
    print(f"\nניתוח סנטימנט:")
    print(f"  סנטימנט דומיננטי: {sent.get('dominant_sentiment', 'N/A')}")
    print(f"  ציון ממוצע: {sent.get('average_score', 0):.3f}")
    print(f"  ביטחון: {sent.get('confidence', 0):.1%}")
    print(f"  טקסטים חיוביים: {sent.get('positive_count', 0)}")
    print(f"  טקסטים שליליים: {sent.get('negative_count', 0)}")
    print(f"  טקסטים ניטרליים: {sent.get('neutral_count', 0)}")
    print(f"  סך הכל טקסטים: {sent.get('total_texts', 0)}")

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

print(f"\n=== הסבר הציון {result['score']} ===")
if result['score'] >= 80:
    print("ציון גבוה מאוד - הרבה טקסטים חיוביים עם מילות מפתח חשובות")
elif result['score'] >= 60:
    print("ציון גבוה - טקסטים חיוביים עם נושאים חשובים")
elif result['score'] >= 40:
    print("ציון בינוני - טקסטים מעורבים")
elif result['score'] >= 20:
    print("ציון נמוך - מעט טקסטים או שליליים")
else:
    print("ציון נמוך מאוד - טקסטים שליליים או מעטים")

print(f"\n=== מקורות החדשות ===")
print("המערכת עכשיו משתמשת ב:")
print("1. MarketAux API (חדשות פיננסיות)")
print("2. Yahoo Finance RSS (חדשות עדכניות)")
print("3. Alpha Vantage News (אם זמין)")
print("4. Finnhub News (אם זמין)")
print("5. NewsData API (גיבוי)")

print(f"\n=== שיפורים שהוספנו ===")
print("✅ מקורות חדשות נוספים")
print("✅ סינון רלוונטיות מתקדם")
print("✅ מיון לפי איכות")
print("✅ בדיקת שמות חברות")
print("✅ סינון מילות מפתח פיננסיות") 