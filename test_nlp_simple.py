import sys
sys.path.append('.')

from core.nlp_analyzer import NLPAnalyzer

# בדיקה פשוטה
analyzer = NLPAnalyzer()
symbol = "AAPL"

print(f"=== NLP Analyzer Test for {symbol} ===")

result = analyzer.analyze(symbol)

print(f"Score: {result['score']}/100")
print(f"Sentiment: {result['sentiment']}")
print(f"Summary: {result['summary']}")

print(f"\nTopics found:")
for topic in result['topics']:
    print(f"  - {topic['category']}: {topic['keywords']}")

print(f"\nKey phrases:")
for phrase in result['key_phrases'][:3]:
    print(f"  - {phrase}") 