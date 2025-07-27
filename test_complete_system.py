#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_sample_data():
    """יצירת נתוני דוגמה"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # מחירים עם מגמה עולה
    base_price = 100
    prices = []
    for i in range(len(dates)):
        # מגמה עולה עם תנודתיות
        price = base_price + i * 0.5 + np.random.normal(0, 2)
        prices.append(max(price, 50))  # מינימום מחיר
    
    # נפח עם מגמה
    volumes = []
    for i in range(len(dates)):
        volume = 1000000 + np.random.normal(0, 200000)
        volumes.append(max(volume, 100000))
    
    df = pd.DataFrame({
        'Open': [p * 0.99 for p in prices],
        'High': [p * 1.02 for p in prices],
        'Low': [p * 0.98 for p in prices],
        'Close': prices,
        'Volume': volumes
    }, index=dates)
    
    return df

def test_complete_system():
    """בדיקת המערכת המלאה"""
    try:
        print("🔧 בדיקת המערכת המלאה...")
        
        # יצירת נתוני דוגמה
        sample_data = create_sample_data()
        print(f"✅ נתוני דוגמה נוצרו: {len(sample_data)} שורות")
        
        # בדיקת EnhancedAdvancedAnalyzer
        from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
        enhanced_agent = EnhancedAdvancedAnalyzer()
        enhanced_result = enhanced_agent.analyze('TEST', sample_data)
        print(f"✅ EnhancedAdvancedAnalyzer: ציון {enhanced_result.get('score', 'N/A')}")
        
        # בדיקת AlphaScoreEngine
        from core.alpha_score_engine import AlphaScoreEngine
        engine = AlphaScoreEngine()
        engine_result = engine.evaluate('TEST', sample_data)
        print(f"✅ AlphaScoreEngine: ציון {engine_result.get('final_score', 'N/A')}")
        print(f"✅ AlphaScoreEngine: {engine_result.get('agents_count', 0)} סוכנים פעילים")
        
        # בדיקת MarketDataConnector
        from core.market_data_connector import MarketDataConnector
        connector = MarketDataConnector()
        connector_result = connector.get_enhanced_market_data('TEST')
        print(f"✅ MarketDataConnector: {connector_result.get('sources_count', 0)} מקורות נתונים")
        
        # בדיקת NewsCatalystAgent
        from core.news_catalyst_agent import NewsCatalystAgent
        news_agent = NewsCatalystAgent()
        news_result = news_agent.analyze('TEST')
        print(f"✅ NewsCatalystAgent: {news_result}")
        
        print("\n📊 סיכום המערכת:")
        print(f"- EnhancedAdvancedAnalyzer: ✅ פעיל")
        print(f"- AlphaScoreEngine: ✅ פעיל עם {engine_result.get('agents_count', 0)} סוכנים")
        print(f"- MarketDataConnector: ✅ פעיל עם {connector_result.get('sources_count', 0)} מקורות")
        print(f"- NewsCatalystAgent: ✅ פעיל")
        
        print("\n✅ כל הבדיקות הושלמו בהצלחה!")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקה: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_system()
    if success:
        print("\n🎉 המערכת פועלת במלואו!")
    else:
        print("\n⚠️ יש בעיות שדורשות תיקון") 