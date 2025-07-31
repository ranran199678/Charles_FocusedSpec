#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_qbts_complete():
    """בדיקה מקיפה של QBTS עם המערכת המלאה"""
    try:
        print("🔧 בדיקת QBTS עם המערכת המלאה...")
        print("=" * 60)
        
        # 1. בדיקת EnhancedAdvancedAnalyzer
        print("\n📊 1. בדיקת EnhancedAdvancedAnalyzer...")
        from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
        enhanced_agent = EnhancedAdvancedAnalyzer()
        
        # קבלת נתונים מ-yfinance
        import yfinance as yf
        ticker = yf.Ticker('QBTS')
        hist = ticker.history(period='100d')
        
        if hist.empty:
            print("⚠️ אין נתונים זמינים ל-QBTS מ-yfinance")
            # יצירת נתוני דוגמה
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
            base_price = 10
            prices = []
            for i in range(len(dates)):
                price = base_price + i * 0.1 + np.random.normal(0, 0.5)
                prices.append(max(price, 1))
            
            volumes = []
            for i in range(len(dates)):
                volume = 100000 + np.random.normal(0, 20000)
                volumes.append(max(volume, 10000))
            
            hist = pd.DataFrame({
                'Open': [p * 0.99 for p in prices],
                'High': [p * 1.02 for p in prices],
                'Low': [p * 0.98 for p in prices],
                'Close': prices,
                'Volume': volumes
            }, index=dates)
            print("✅ נוצרו נתוני דוגמה ל-QBTS")
        
        enhanced_result = enhanced_agent.analyze('QBTS', hist)
        print(f"✅ EnhancedAdvancedAnalyzer ציון: {enhanced_result.get('score', 'N/A')}")
        print(f"✅ הסבר: {enhanced_result.get('explanation', 'N/A')[:200]}...")
        
        # 2. בדיקת AlphaScoreEngine
        print("\n📈 2. בדיקת AlphaScoreEngine...")
        from core.alpha_score_engine import AlphaScoreEngine
        engine = AlphaScoreEngine()
        engine_result = engine.evaluate('QBTS', hist)
        
        print(f"✅ AlphaScoreEngine ציון סופי: {engine_result.get('final_score', 'N/A')}")
        print(f"✅ מספר סוכנים פעילים: {engine_result.get('agents_count', 0)}")
        
        # הצגת ציוני סוכנים
        agent_scores = engine_result.get('agent_scores', {})
        if agent_scores:
            print("\n📊 ציוני סוכנים:")
            for agent, score in agent_scores.items():
                print(f"  - {agent}: {score}")
        
        # 3. בדיקת MarketDataConnector
        print("\n🌐 3. בדיקת MarketDataConnector...")
        from core.market_data_connector import MarketDataConnector
        connector = MarketDataConnector()
        connector_result = connector.get_enhanced_market_data('QBTS')
        
        print(f"✅ מספר מקורות נתונים: {connector_result.get('sources_count', 0)}")
        if 'enhanced_data' in connector_result:
            sources = list(connector_result['enhanced_data'].keys())
            print(f"✅ מקורות זמינים: {sources}")
        
        # 4. בדיקת NewsCatalystAgent
        print("\n📰 4. בדיקת NewsCatalystAgent...")
        from core.news_catalyst_agent import NewsCatalystAgent
        news_agent = NewsCatalystAgent()
        news_result = news_agent.analyze('QBTS')
        
        print(f"✅ חדשות קטליסטיות: {news_result}")
        
        # 5. סיכום מפורט
        print("\n" + "=" * 60)
        print("📋 סיכום מפורט ל-QBTS:")
        print("=" * 60)
        
        print(f"🎯 EnhancedAdvancedAnalyzer:")
        print(f"  - ציון: {enhanced_result.get('score', 'N/A')}")
        print(f"  - סטטוס: {'✅ פעיל' if enhanced_result.get('score') else '❌ לא פעיל'}")
        
        print(f"\n🎯 AlphaScoreEngine:")
        print(f"  - ציון סופי: {engine_result.get('final_score', 'N/A')}")
        print(f"  - סוכנים פעילים: {engine_result.get('agents_count', 0)}")
        print(f"  - סטטוס: {'✅ פעיל' if engine_result.get('final_score') else '❌ לא פעיל'}")
        
        print(f"\n🎯 MarketDataConnector:")
        print(f"  - מקורות נתונים: {connector_result.get('sources_count', 0)}")
        print(f"  - סטטוס: {'✅ פעיל' if connector_result.get('sources_count', 0) > 0 else '❌ לא פעיל'}")
        
        print(f"\n🎯 NewsCatalystAgent:")
        print(f"  - חדשות קטליסטיות: {news_result}")
        print(f"  - סטטוס: {'✅ פעיל' if news_result is not None else '❌ לא פעיל'}")
        
        # 6. המלצה
        final_score = engine_result.get('final_score', 50)
        print(f"\n💡 המלצה:")
        if final_score >= 70:
            print(f"  🟢 QBTS - ציון גבוה ({final_score}) - מומלץ לקנייה")
        elif final_score >= 50:
            print(f"  🟡 QBTS - ציון בינוני ({final_score}) - מומלץ לעקוב")
        else:
            print(f"  🔴 QBTS - ציון נמוך ({final_score}) - לא מומלץ")
        
        print("\n✅ בדיקה הושלמה בהצלחה!")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקה: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qbts_complete()
    if success:
        print("\n🎉 QBTS נבדק בהצלחה עם המערכת המלאה!")
    else:
        print("\n⚠️ יש בעיות בבדיקת QBTS") 