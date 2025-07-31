import sys
sys.path.append('.')

from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

# בדיקת Alpha Score Engine
print("=== בדיקת Alpha Score Engine ===")

# יצירת מופעים
data_fetcher = DataFetcher()
engine = AlphaScoreEngine()

# בדיקת מניה
symbol = "AAPL"
print(f"\n=== ניתוח {symbol} ===")

try:
    # איסוף נתוני מחירים
    price_df = data_fetcher.get_price_history(symbol, period="1y")
    print(f"נאספו {len(price_df)} נקודות נתונים")
    
    # ניתוח עם Alpha Score Engine
    result = engine.evaluate(symbol, price_df)
    
    print(f"ציון כולל: {result.get('score', 0)}/100")
    print(f"המלצה: {result.get('recommendation', 'Unknown')}")
    
    # פירוט ציוני הסוכנים
    print(f"\n=== פירוט ציוני סוכנים ===")
    signals = result.get('signals', {})
    for agent, score in signals.items():
        print(f"{agent:30}: {score}/100")
    
    # ניתוח הבעיה
    print(f"\n=== ניתוח הבעיה ===")
    low_scores = [(agent, score) for agent, score in signals.items() if score < 10]
    high_scores = [(agent, score) for agent, score in signals.items() if score > 50]
    
    print(f"סוכנים עם ציון נמוך (<10): {len(low_scores)}")
    for agent, score in low_scores[:5]:  # רק 5 הראשונים
        print(f"  {agent}: {score}/100")
    
    print(f"סוכנים עם ציון גבוה (>50): {len(high_scores)}")
    for agent, score in high_scores[:5]:  # רק 5 הראשונים
        print(f"  {agent}: {score}/100")
    
    # חישוב ממוצע
    all_scores = list(signals.values())
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    print(f"ממוצע ציונים: {avg_score:.2f}/100")
    
except Exception as e:
    print(f"שגיאה: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== סיום בדיקה ===") 