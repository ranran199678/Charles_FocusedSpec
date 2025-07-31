#!/usr/bin/env python3
"""
בדיקת מניות אמיתיות עם המערכת המשופרת
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.alpha_score_engine import AlphaScoreEngine
from core.market_data_connector import MarketDataConnector
from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
from core.news_catalyst_agent import NewsCatalystAgent
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def test_real_stocks():
    """בדיקת מניות אמיתיות עם נתונים זמינים"""
    
    # רשימת מניות לבדיקה
    test_symbols = [
        "AAPL",   # Apple - מניה גדולה ויציבה
        "TSLA",   # Tesla - מניה עם תנודתיות גבוהה
        "NVDA",   # NVIDIA - מניה טכנולוגית חזקה
        "MSFT",   # Microsoft - מניה גדולה ויציבה
        "GOOGL",  # Google - מניה טכנולוגית
        "AMZN",   # Amazon - מניה טכנולוגית
        "META",   # Meta - מניה טכנולוגית
        "NFLX",   # Netflix - מניה טכנולוגית
        "AMD",    # AMD - מניה טכנולוגית
        "CRM"     # Salesforce - מניה טכנולוגית
    ]
    
    print("🔧 בדיקת מניות אמיתיות עם המערכת המשופרת...")
    print("=" * 60)
    
    # יצירת מנוע
    engine = AlphaScoreEngine()
    market_connector = MarketDataConnector()
    enhanced_analyzer = EnhancedAdvancedAnalyzer()
    news_agent = NewsCatalystAgent()
    
    results = []
    
    for symbol in test_symbols:
        print(f"\n📊 בדיקת {symbol}...")
        
        try:
            # קבלת נתונים מ-yfinance
            stock = yf.Ticker(symbol)
            hist = stock.history(period="6mo")
            
            if hist.empty:
                print(f"⚠️ אין נתונים זמינים ל-{symbol}")
                continue
            
            # המרה לפורמט הנדרש
            price_df = hist.reset_index()
            price_df.columns = [col.lower() for col in price_df.columns]
            
            # בדיקת EnhancedAdvancedAnalyzer
            enhanced_result = enhanced_analyzer.analyze(symbol, price_df)
            enhanced_score = enhanced_result.get("score", 1)
            
            # בדיקת AlphaScoreEngine
            engine_result = engine.evaluate(symbol, price_df)
            engine_score = engine_result.get("final_score", 1)
            agents_count = engine_result.get("agents_count", 0)
            
            # בדיקת MarketDataConnector
            market_data = market_connector.get_market_data(symbol)
            market_sources = len(market_data) if market_data else 0
            
            # בדיקת NewsCatalystAgent
            news_result = news_agent.analyze(symbol, price_df)
            news_score = news_result.get("score", 1)
            
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
                "data_points": len(price_df)
            }
            
            results.append(result)
            
            # הדפסת תוצאות
            print(f"✅ {symbol}:")
            print(f"   - EnhancedAdvancedAnalyzer: {enhanced_score}")
            print(f"   - AlphaScoreEngine: {engine_score} ({agents_count} סוכנים)")
            print(f"   - NewsCatalystAgent: {news_score}")
            print(f"   - ציון ממוצע: {avg_score:.1f}")
            print(f"   - מקורות נתונים: {market_sources}")
            print(f"   - נקודות נתונים: {len(price_df)}")
            
            # המלצה
            if avg_score >= 60:
                recommendation = "🟢 מומלץ"
            elif avg_score >= 40:
                recommendation = "🟡 ניטרלי"
            else:
                recommendation = "🔴 לא מומלץ"
            
            print(f"   - המלצה: {recommendation}")
            
        except Exception as e:
            print(f"❌ שגיאה בבדיקת {symbol}: {e}")
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
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result['symbol']}: {result['avg_score']:.1f}")
        
        # מניות מומלצות
        recommended = [r for r in results if r["avg_score"] >= 60]
        neutral = [r for r in results if 40 <= r["avg_score"] < 60]
        not_recommended = [r for r in results if r["avg_score"] < 40]
        
        print(f"\n💡 המלצות:")
        print(f"🟢 מומלץ ({len(recommended)}): {[r['symbol'] for r in recommended]}")
        print(f"🟡 ניטרלי ({len(neutral)}): {[r['symbol'] for r in neutral]}")
        print(f"🔴 לא מומלץ ({len(not_recommended)}): {[r['symbol'] for r in not_recommended]}")
        
    else:
        print("❌ לא נבדקו מניות בהצלחה")
    
    print(f"\n✅ בדיקה הושלמה בהצלחה!")
    print(f"🎉 נבדקו {len(results)} מניות עם המערכת המשופרת!")

if __name__ == "__main__":
    test_real_stocks() 