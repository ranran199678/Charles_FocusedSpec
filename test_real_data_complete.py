#!/usr/bin/env python3
"""
בדיקה מלאה עם נתונים אמיתיים עובדים
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.alpha_score_engine import AlphaScoreEngine
from core.market_data_connector import MarketDataConnector
from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
from core.news_catalyst_agent import NewsCatalystAgent
from utils.data_fetcher import DataFetcher
from utils.fmp_utils import fmp_get_price_df
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_real_data_complete():
    """בדיקה מלאה עם נתונים אמיתיים"""
    
    print("🔧 בדיקה מלאה עם נתונים אמיתיים...")
    print("=" * 60)
    
    # יצירת מנועים
    engine = AlphaScoreEngine()
    market_connector = MarketDataConnector()
    enhanced_analyzer = EnhancedAdvancedAnalyzer()
    news_agent = NewsCatalystAgent()
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
            
            # בדיקת EnhancedAdvancedAnalyzer
            print(f"  - מבדיק EnhancedAdvancedAnalyzer...")
            enhanced_result = enhanced_analyzer.analyze(symbol, price_df)
            enhanced_score = enhanced_result.get("score", 1)
            print(f"    - ציון: {enhanced_score}")
            
            # בדיקת AlphaScoreEngine
            print(f"  - מבדיק AlphaScoreEngine...")
            engine_result = engine.evaluate(symbol, price_df)
            engine_score = engine_result.get("final_score", 1)
            agents_count = engine_result.get("agents_count", 0)
            print(f"    - ציון: {engine_score} ({agents_count} סוכנים)")
            
            # בדיקת MarketDataConnector
            print(f"  - מבדיק MarketDataConnector...")
            market_data = market_connector.get_market_data(symbol)
            market_sources = len(market_data) if market_data else 0
            print(f"    - מקורות: {market_sources}")
            
            # בדיקת NewsCatalystAgent
            print(f"  - מבדיק NewsCatalystAgent...")
            news_result = news_agent.analyze(symbol, price_df)
            news_score = news_result.get("score", 1)
            print(f"    - ציון: {news_score}")
            
            # חישוב ציון ממוצע
            avg_score = (enhanced_score + engine_score + news_score) / 3
            
            result = {
                "symbol": symbol,
                "enhanced_score": enhanced_score,
                "engine_score": engine_score,
                "news_score": news_score,
                "avg_score": avg_score,
                "agents_count": agents_count,
                "market_sources": market_sources,
                "data_points": len(price_df),
                "last_price": price_df['close'].iloc[-1],
                "agent_scores": engine_result.get("agent_scores", {})
            }
            
            results.append(result)
            
            # הדפסת פרטים נוספים
            if "agent_scores" in engine_result:
                print(f"    - ציוני סוכנים (5 הראשונים):")
                for agent_name, agent_score in list(engine_result["agent_scores"].items())[:5]:
                    print(f"      * {agent_name}: {agent_score}")
                if len(engine_result["agent_scores"]) > 5:
                    print(f"      * ... ועוד {len(engine_result['agent_scores']) - 5} סוכנים")
            
            # המלצה
            if avg_score >= 60:
                recommendation = "🟢 מומלץ"
            elif avg_score >= 40:
                recommendation = "🟡 ניטרלי"
            else:
                recommendation = "🔴 לא מומלץ"
            
            print(f"    - ציון ממוצע: {avg_score:.1f}")
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
        avg_enhanced = sum(r["enhanced_score"] for r in results) / len(results)
        avg_engine = sum(r["engine_score"] for r in results) / len(results)
        avg_news = sum(r["news_score"] for r in results) / len(results)
        avg_overall = sum(r["avg_score"] for r in results) / len(results)
        avg_agents = sum(r["agents_count"] for r in results) / len(results)
        
        print(f"📊 מניות שנבדקו: {len(results)}")
        print(f"📊 ממוצע EnhancedAdvancedAnalyzer: {avg_enhanced:.1f}")
        print(f"📊 ממוצע AlphaScoreEngine: {avg_engine:.1f}")
        print(f"📊 ממוצע NewsCatalystAgent: {avg_news:.1f}")
        print(f"📊 ממוצע כללי: {avg_overall:.1f}")
        print(f"📊 ממוצע סוכנים: {avg_agents:.1f}")
        
        # מיון לפי ציון
        results.sort(key=lambda x: x["avg_score"], reverse=True)
        
        print(f"\n🏆 דירוג מניות לפי ציון:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['symbol']}: {result['avg_score']:.1f} (מחיר: {result['last_price']:.2f})")
        
        # מניות מומלצות
        recommended = [r for r in results if r["avg_score"] >= 60]
        neutral = [r for r in results if 40 <= r["avg_score"] < 60]
        not_recommended = [r for r in results if r["avg_score"] < 40]
        
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
        
    else:
        print("❌ לא נבדקו מניות בהצלחה")
    
    print(f"\n✅ בדיקה הושלמה בהצלחה!")
    print(f"🎉 נבדקו {len(results)} מניות עם נתונים אמיתיים!")

if __name__ == "__main__":
    test_real_data_complete() 