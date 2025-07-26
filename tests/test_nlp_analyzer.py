"""
טסט עבור NLP Analyzer
"""

from core.nlp_analyzer import NLPAnalyzer

def test_nlp_analyzer():
    """טסט בסיסי עבור NLP Analyzer"""
    analyzer = NLPAnalyzer()
    symbol = "AAPL"
    
    print(f"=== בדיקת NLP Analyzer עבור {symbol} ===")
    
    result = analyzer.analyze(symbol)
    
    print(f"ציון כולל: {result['score']}/100")
    print(f"סנטימנט: {result['sentiment']}")
    print(f"סיכום: {result['summary']}")
    
    print(f"\nנושאים זוהו:")
    for topic in result['topics']:
        print(f"  - {topic['category']}: {topic['keywords']}")
    
    print(f"\nביטויים מפתח:")
    for phrase in result['key_phrases'][:3]:  # רק 3 הראשונים
        print(f"  - {phrase}")
    
    print(f"\nפרטים נוספים:")
    details = result['details']
    if 'sentiment_analysis' in details:
        sent = details['sentiment_analysis']
        print(f"  ביטחון סנטימנט: {sent.get('confidence', 0):.1%}")
        print(f"  טקסטים חיוביים: {sent.get('positive_count', 0)}")
        print(f"  טקסטים שליליים: {sent.get('negative_count', 0)}")
    
    if 'impact_analysis' in details:
        impact = details['impact_analysis']
        print(f"  ציון השפעה: {impact.get('impact_score', 0)}")
        print(f"  כמות טקסטים: {impact.get('text_count', 0)}")
    
    return result

def test_nlp_sentiment_only():
    """טסט לניתוח סנטימנט בלבד"""
    analyzer = NLPAnalyzer()
    symbol = "TSLA"
    
    print(f"\n=== ניתוח סנטימנט בלבד עבור {symbol} ===")
    
    sentiment_result = analyzer.get_sentiment_analysis(symbol)
    
    print(f"סנטימנט: {sentiment_result['sentiment']}")
    print(f"פרטים: {sentiment_result['details']}")
    
    return sentiment_result

def test_nlp_topics_only():
    """טסט לניתוח נושאים בלבד"""
    analyzer = NLPAnalyzer()
    symbol = "NVDA"
    
    print(f"\n=== ניתוח נושאים בלבד עבור {symbol} ===")
    
    topics_result = analyzer.get_topic_analysis(symbol)
    
    print(f"נושאים זוהו: {len(topics_result)}")
    for topic in topics_result:
        print(f"  - {topic['category']}: {topic['keywords']} (חשיבות: {topic['importance']})")
    
    return topics_result

if __name__ == "__main__":
    # הרצת כל הטסטים
    test_nlp_analyzer()
    test_nlp_sentiment_only()
    test_nlp_topics_only() 