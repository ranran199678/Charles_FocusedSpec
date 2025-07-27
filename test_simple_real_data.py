#!/usr/bin/env python3
"""
בדיקה פשוטה עם נתונים אמיתיים עובדים
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_simple_real_data():
    """בדיקה פשוטה עם נתונים אמיתיים"""
    
    print("🔧 בדיקה פשוטה עם נתונים אמיתיים...")
    print("=" * 60)
    
    # יצירת מנוע
    engine = AlphaScoreEngine()
    data_fetcher = DataFetcher()
    
    # רשימת מניות לבדיקה
    test_symbols = [
        "INTC",   # Intel - יציבה
        "AAPL",   # Apple - טכנולוגיה
        "MSFT",   # Microsoft - טכנולוגיה
        "GOOGL",  # Google - טכנולוגיה
        "TSLA"    # Tesla - תנודתית
    ]
    
    results = []
    
    for symbol in test_symbols:
        print(f"\n📊 בדיקת {symbol}...")
        
        try:
            # קבלת נתונים מ-DataFetcher
            print(f"  - מקבל נתונים...")
            price_df = data_fetcher.get_price_history(symbol, "100d")
            
            if price_df is None or price_df.empty:
                print(f"  ❌ אין נתונים ל-{symbol}")
                continue
            
            print(f"  ✅ נתונים זמינים - {len(price_df)} שורות")
            print(f"    - מחיר אחרון: {price_df['close'].iloc[-1]:.2f}")
            print(f"    - טווח: {price_df.index[0].strftime('%Y-%m-%d')} עד {price_df.index[-1].strftime('%Y-%m-%d')}")
            
            # בדיקת AlphaScoreEngine
            print(f"  - מבדיק AlphaScoreEngine...")
            engine_result = engine.evaluate(symbol, price_df)
            engine_score = engine_result.get("final_score", 1)
            agents_count = engine_result.get("agents_count", 0)
            print(f"    - ציון: {engine_score} ({agents_count} סוכנים)")
            
            result = {
                "symbol": symbol,
                "engine_score": engine_score,
                "agents_count": agents_count,
                "data_points": len(price_df),
                "last_price": price_df['close'].iloc[-1],
                "agent_scores": engine_result.get("agent_scores", {})
            }
            
            results.append(result)
            
            # הדפסת פרטים נוספים
            if "agent_scores" in engine_result:
                print(f"    - ציוני סוכנים (10 הראשונים):")
                for agent_name, agent_score in list(engine_result["agent_scores"].items())[:10]:
                    print(f"      * {agent_name}: {agent_score}")
                if len(engine_result["agent_scores"]) > 10:
                    print(f"      * ... ועוד {len(engine_result['agent_scores']) - 10} סוכנים")
            
            # המלצה
            if engine_score >= 60:
                recommendation = "🟢 מומלץ"
            elif engine_score >= 40:
                recommendation = "🟡 ניטרלי"
            else:
                recommendation = "🔴 לא מומלץ"
            
            print(f"    - המלצה: {recommendation}")
            
        except Exception as e:
            print(f"  ❌ שגיאה: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # סיכום כללי
    print("\n" + "=" * 60)
    print("📋 סיכום כללי:")
    print("=" * 60)
    
    if results:
        # חישוב סטטיסטיקות
        avg_engine = sum(r["engine_score"] for r in results) / len(results)
        avg_agents = sum(r["agents_count"] for r in results) / len(results)
        
        print(f"📊 מניות שנבדקו: {len(results)}")
        print(f"📊 ממוצע AlphaScoreEngine: {avg_engine:.1f}")
        print(f"📊 ממוצע סוכנים: {avg_agents:.1f}")
        
        # מיון לפי ציון
        results.sort(key=lambda x: x["engine_score"], reverse=True)
        
        print(f"\n🏆 דירוג מניות לפי ציון:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['symbol']}: {result['engine_score']:.1f} (מחיר: {result['last_price']:.2f})")
        
        # מניות מומלצות
        recommended = [r for r in results if r["engine_score"] >= 60]
        neutral = [r for r in results if 40 <= r["engine_score"] < 60]
        not_recommended = [r for r in results if r["engine_score"] < 40]
        
        print(f"\n💡 המלצות:")
        print(f"🟢 מומלץ ({len(recommended)}): {[r['symbol'] for r in recommended]}")
        print(f"🟡 ניטרלי ({len(neutral)}): {[r['symbol'] for r in neutral]}")
        print(f"🔴 לא מומלץ ({len(not_recommended)}): {[r['symbol'] for r in not_recommended]}")
        
        # ניתוח מפורט של הסוכנים
        print(f"\n🔍 ניתוח מפורט של הסוכנים:")
        all_agent_scores = {}
        for result in results:
            for agent_name, agent_score in result["agent_scores"].items():
                if agent_name not in all_agent_scores:
                    all_agent_scores[agent_name] = []
                all_agent_scores[agent_name].append(agent_score)
        
        if all_agent_scores:
            print(f"📊 ממוצע ציונים לפי סוכן (10 הראשונים):")
            for agent_name, scores in sorted(all_agent_scores.items(), key=lambda x: np.mean(x[1]), reverse=True)[:10]:
                avg_score = np.mean(scores)
                print(f"   - {agent_name}: {avg_score:.1f}")
        
        # ניתוח לפי סוג מניה
        print(f"\n📈 ניתוח לפי סוג מניה:")
        tech_stocks = [r for r in results if r["symbol"] in ["AAPL", "MSFT", "GOOGL"]]
        other_stocks = [r for r in results if r["symbol"] not in ["AAPL", "MSFT", "GOOGL"]]
        
        if tech_stocks:
            tech_avg = sum(r["engine_score"] for r in tech_stocks) / len(tech_stocks)
            print(f"   - מניות טכנולוגיה: {tech_avg:.1f}")
        
        if other_stocks:
            other_avg = sum(r["engine_score"] for r in other_stocks) / len(other_stocks)
            print(f"   - מניות אחרות: {other_avg:.1f}")
        
    else:
        print("❌ לא נבדקו מניות בהצלחה")
    
    print(f"\n✅ בדיקה הושלמה בהצלחה!")
    print(f"🎉 נבדקו {len(results)} מניות עם נתונים אמיתיים!")

if __name__ == "__main__":
    test_simple_real_data() 