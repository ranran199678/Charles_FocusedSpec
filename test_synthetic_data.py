#!/usr/bin/env python3
"""
בדיקת המערכת עם נתונים סינתטיים
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.alpha_score_engine import AlphaScoreEngine
from core.market_data_connector import MarketDataConnector
from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
from core.news_catalyst_agent import NewsCatalystAgent
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_synthetic_data(symbol, days=180):
    """יצירת נתונים סינתטיים למניה"""
    
    # יצירת תאריכים
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # יצירת מחירים סינתטיים עם מגמה ותנודתיות
    np.random.seed(42)  # לקבלת תוצאות עקביות
    
    # מחיר התחלתי
    base_price = 100.0
    
    # יצירת מחירים עם מגמה ותנודתיות
    returns = np.random.normal(0.001, 0.02, len(dates))  # תשואה יומית ממוצעת 0.1% עם סטיית תקן 2%
    
    # הוספת מגמה
    trend = np.linspace(0, 0.3, len(dates))  # מגמה חיובית של 30%
    returns += trend / len(dates)
    
    # חישוב מחירים
    prices = [base_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # יצירת OHLCV
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        # יצירת OHLC סביב המחיר
        volatility = price * 0.02  # תנודתיות של 2%
        
        open_price = price + np.random.normal(0, volatility * 0.5)
        high_price = max(open_price, price) + abs(np.random.normal(0, volatility * 0.3))
        low_price = min(open_price, price) - abs(np.random.normal(0, volatility * 0.3))
        close_price = price + np.random.normal(0, volatility * 0.5)
        
        # נפח מסחר
        base_volume = 1000000
        volume = base_volume + np.random.normal(0, base_volume * 0.3)
        volume = max(volume, 100000)  # נפח מינימלי
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    
    return df

def test_synthetic_stocks():
    """בדיקת מניות סינתטיות"""
    
    # רשימת מניות לבדיקה
    test_symbols = [
        "SYNTH_GROWTH",    # מניה עם מגמה חזקה
        "SYNTH_VOLATILE",  # מניה תנודתית
        "SYNTH_STABLE",    # מניה יציבה
        "SYNTH_DECLINE",   # מניה בירידה
        "SYNTH_SIDEWAYS"   # מניה בצד
    ]
    
    print("🔧 בדיקת מניות סינתטיות עם המערכת המשופרת...")
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
            # יצירת נתונים סינתטיים
            price_df = create_synthetic_data(symbol)
            
            # המרה לפורמט הנדרש
            price_df_reset = price_df.reset_index()
            price_df_reset.columns = [col.lower() for col in price_df_reset.columns]
            
            # בדיקת EnhancedAdvancedAnalyzer
            enhanced_result = enhanced_analyzer.analyze(symbol, price_df_reset)
            enhanced_score = enhanced_result.get("score", 1)
            
            # בדיקת AlphaScoreEngine
            engine_result = engine.evaluate(symbol, price_df_reset)
            engine_score = engine_result.get("final_score", 1)
            agents_count = engine_result.get("agents_count", 0)
            
            # בדיקת MarketDataConnector
            market_data = market_connector.get_market_data(symbol)
            market_sources = len(market_data) if market_data else 0
            
            # בדיקת NewsCatalystAgent
            news_result = news_agent.analyze(symbol, price_df_reset)
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
            
            # הדפסת פרטים נוספים
            if "agent_scores" in engine_result:
                print(f"   - ציוני סוכנים:")
                for agent_name, agent_score in list(engine_result["agent_scores"].items())[:5]:
                    print(f"     * {agent_name}: {agent_score}")
                if len(engine_result["agent_scores"]) > 5:
                    print(f"     * ... ועוד {len(engine_result['agent_scores']) - 5} סוכנים")
            
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
            print(f"{i}. {result['symbol']}: {result['avg_score']:.1f}")
        
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
            if "agent_scores" in engine_result:
                for agent_name, agent_score in engine_result["agent_scores"].items():
                    if agent_name not in all_agent_scores:
                        all_agent_scores[agent_name] = []
                    all_agent_scores[agent_name].append(agent_score)
        
        if all_agent_scores:
            print(f"📊 ממוצע ציונים לפי סוכן:")
            for agent_name, scores in sorted(all_agent_scores.items(), key=lambda x: np.mean(x[1]), reverse=True)[:10]:
                avg_score = np.mean(scores)
                print(f"   - {agent_name}: {avg_score:.1f}")
        
    else:
        print("❌ לא נבדקו מניות בהצלחה")
    
    print(f"\n✅ בדיקה הושלמה בהצלחה!")
    print(f"🎉 נבדקו {len(results)} מניות עם המערכת המשופרת!")

if __name__ == "__main__":
    test_synthetic_stocks() 