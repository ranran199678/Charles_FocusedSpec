import sys
sys.path.append('.')

from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

# בדיקת איזה סוכנים עובדים
print("=== בדיקת סוכנים עובדים ===")

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
    
    # בדיקת כל הסוכנים
    print(f"\n=== בדיקת סוכנים ===")
    working_agents = []
    dummy_agents = []
    
    for name, agent in engine.agents.items():
        try:
            output = agent.analyze(symbol, price_df)
            score = output.get("score", 1)
            explanation = output.get("explanation", "")
            
            if "טרם מומש" in explanation or score == 1:
                dummy_agents.append(name)
            else:
                working_agents.append((name, score))
                print(f"✅ {name}: {score}/100")
                
        except Exception as e:
            dummy_agents.append(name)
            print(f"❌ {name}: שגיאה - {str(e)[:50]}...")
    
    print(f"\n=== סיכום ===")
    print(f"סוכנים עובדים: {len(working_agents)}")
    print(f"סוכנים דמי: {len(dummy_agents)}")
    
    if working_agents:
        print(f"\nסוכנים עובדים:")
        for name, score in sorted(working_agents, key=lambda x: x[1], reverse=True):
            print(f"  {name}: {score}/100")
    
    if dummy_agents:
        print(f"\nסוכנים דמי (לא מומשו):")
        for name in dummy_agents[:10]:  # רק 10 הראשונים
            print(f"  {name}")
        if len(dummy_agents) > 10:
            print(f"  ... ועוד {len(dummy_agents) - 10} סוכנים")
    
    # ניתוח עם Alpha Score Engine
    print(f"\n=== ניתוח מלא ===")
    result = engine.evaluate(symbol, price_df)
    
    print(f"ציון כולל: {result.get('score', 0)}/100")
    print(f"המלצה: {result.get('recommendation', 'Unknown')}")
    
    # פירוט ציוני הסוכנים העובדים
    print(f"\n=== ציוני סוכנים עובדים ===")
    signals = result.get('signals', {})
    working_scores = [(agent, score) for agent, score in signals.items() if score > 1]
    
    for agent, score in sorted(working_scores, key=lambda x: x[1], reverse=True):
        print(f"{agent:30}: {score}/100")
    
except Exception as e:
    print(f"שגיאה: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== סיום בדיקה ===") 