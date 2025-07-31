"""
דוגמאות שימוש ב-Smart Data Manager
מדגים את כל התכונות והאפשרויות של המערכת
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.smart_data_manager import smart_data_manager, SmartDataManager

def example_basic_usage():
    """דוגמה לשימוש בסיסי"""
    print("🔍 דוגמה לשימוש בסיסי")
    print("=" * 40)
    
    # שליפת נתונים בסיסית
    data = smart_data_manager.get_stock_data('AAPL', days=30)
    
    if data is not None and not data.empty:
        print(f"✅ התקבלו נתונים עבור AAPL")
        print(f"   שורות: {len(data)}")
        print(f"   תאריך ראשון: {data.index[-1]}")
        print(f"   תאריך אחרון: {data.index[0]}")
        print(f"   מחיר אחרון: ${data['close'].iloc[0]:.2f}")
    else:
        print("❌ לא הצלחנו לקבל נתונים")

def example_multiple_stocks():
    """דוגמה לשליפת מספר מניות"""
    print("\n📊 דוגמה לשליפת מספר מניות")
    print("=" * 40)
    
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    
    # שליפה מרובה
    all_data = smart_data_manager.get_multiple_stocks(symbols, days=60)
    
    print(f"📈 נתונים עבור {len(all_data)} מניות:")
    for symbol, data in all_data.items():
        if data is not None and not data.empty:
            current_price = data['close'].iloc[0]
            start_price = data['close'].iloc[-1]
            change_pct = ((current_price - start_price) / start_price) * 100
            print(f"   {symbol}: ${current_price:.2f} ({change_pct:+.2f}%)")
        else:
            print(f"   {symbol}: אין נתונים")

def example_technical_analysis():
    """דוגמה לניתוח טכני"""
    print("\n📈 דוגמה לניתוח טכני")
    print("=" * 40)
    
    # שליפת אינדיקטורים טכניים
    technical_data = smart_data_manager.get_technical_indicators('AAPL', 'all', days=90)
    
    if technical_data is not None and not technical_data.empty:
        print("✅ אינדיקטורים טכניים:")
        
        # RSI
        if 'rsi' in technical_data.columns:
            current_rsi = technical_data['rsi'].iloc[0]
            print(f"   RSI נוכחי: {current_rsi:.2f}")
            
            if current_rsi > 70:
                print("   ⚠️  RSI גבוה - יתכן overbought")
            elif current_rsi < 30:
                print("   ⚠️  RSI נמוך - יתכן oversold")
        
        # Bollinger Bands
        if 'bb_upper' in technical_data.columns and 'bb_lower' in technical_data.columns:
            current_price = technical_data['close'].iloc[0]
            bb_upper = technical_data['bb_upper'].iloc[0]
            bb_lower = technical_data['bb_lower'].iloc[0]
            
            print(f"   Bollinger Bands:")
            print(f"     עליון: ${bb_upper:.2f}")
            print(f"     תחתון: ${bb_lower:.2f}")
            
            if current_price > bb_upper:
                print("   ⚠️  מחיר מעל הפס העליון")
            elif current_price < bb_lower:
                print("   ⚠️  מחיר מתחת לפס התחתון")

def example_news_sentiment():
    """דוגמה לניתוח חדשות ורגשות"""
    print("\n📰 דוגמה לניתוח חדשות ורגשות")
    print("=" * 40)
    
    # שליפת חדשות
    news_data = smart_data_manager.get_news_sentiment('AAPL', days=7)
    
    if news_data is not None and not news_data.empty:
        print(f"✅ התקבלו {len(news_data)} חדשות:")
        
        # הצגת החדשות האחרונות
        for i, (idx, row) in enumerate(news_data.head(3).iterrows()):
            title = row.get('title', 'אין כותרת')
            sentiment = row.get('sentiment', 0)
            
            print(f"   {i+1}. {title[:60]}...")
            print(f"      רגש: {sentiment:.2f}")
    else:
        print("❌ לא התקבלו חדשות")

def example_fundamentals():
    """דוגמה לנתונים פונדמנטליים"""
    print("\n💰 דוגמה לנתונים פונדמנטליים")
    print("=" * 40)
    
    # שליפת נתונים פונדמנטליים
    income_data = smart_data_manager.get_fundamentals('AAPL', 'income')
    ratios_data = smart_data_manager.get_fundamentals('AAPL', 'ratios')
    
    if income_data is not None and not income_data.empty:
        print("✅ נתוני הכנסות:")
        print(f"   שורות: {len(income_data)}")
        
        # הצגת הנתונים האחרונים
        latest = income_data.iloc[0]
        print(f"   הכנסות: ${latest.get('revenue', 0):,.0f}")
        print(f"   רווח נקי: ${latest.get('netIncome', 0):,.0f}")
    
    if ratios_data is not None and not ratios_data.empty:
        print("\n✅ יחסים פיננסיים:")
        latest_ratios = ratios_data.iloc[0]
        print(f"   P/E Ratio: {latest_ratios.get('peRatio', 0):.2f}")
        print(f"   ROE: {latest_ratios.get('roe', 0):.2%}")

def example_comprehensive_analysis():
    """דוגמה לניתוח מקיף"""
    print("\n🎯 דוגמה לניתוח מקיף")
    print("=" * 40)
    
    # שליפת כל סוגי הנתונים
    comprehensive = smart_data_manager.get_comprehensive_data(
        'AAPL',
        days=90,
        include_technical=True,
        include_news=True,
        include_fundamentals=True
    )
    
    print("📊 ניתוח מקיף עבור AAPL:")
    
    # נתוני מחירים
    if 'price_data' in comprehensive and comprehensive['price_data'] is not None:
        price_data = comprehensive['price_data']
        current_price = price_data['close'].iloc[0]
        volatility = price_data['close'].pct_change().std() * (252 ** 0.5)
        print(f"   מחיר נוכחי: ${current_price:.2f}")
        print(f"   תנודתיות שנתית: {volatility:.2%}")
    
    # אינדיקטורים טכניים
    if 'technical_indicators' in comprehensive and comprehensive['technical_indicators'] is not None:
        tech_data = comprehensive['technical_indicators']
        if 'rsi' in tech_data.columns:
            rsi = tech_data['rsi'].iloc[0]
            print(f"   RSI: {rsi:.2f}")
    
    # חדשות
    if 'news_sentiment' in comprehensive and comprehensive['news_sentiment'] is not None:
        news_count = len(comprehensive['news_sentiment'])
        print(f"   חדשות אחרונות: {news_count}")

def example_performance_monitoring():
    """דוגמה למעקב ביצועים"""
    print("\n⚡ דוגמה למעקב ביצועים")
    print("=" * 40)
    
    # סטטיסטיקות ביצועים
    performance = smart_data_manager.get_performance_stats()
    
    print("📈 סטטיסטיקות ביצועים:")
    print(f"   פגיעות במטמון: {performance['cache_hits']}")
    print(f"   החטאות מטמון: {performance['cache_misses']}")
    print(f"   אחוז פגיעות: {performance['cache_hit_rate']:.2%}")
    print(f"   גודל מטמון: {performance['cache_size']}")
    print(f"   דחיסה מופעלת: {performance['compression_enabled']}")
    
    # דוח שימוש
    usage_report = smart_data_manager.usage_tracker.get_usage_report()
    
    print("\n📊 דוח שימוש:")
    print(f"   בקשות מטמון: {usage_report['cache_efficiency']['total_requests']}")
    print(f"   יעילות מטמון: {usage_report['cache_efficiency']['hit_rate']:.2%}")
    
    # מניות המבוקשות ביותר
    if usage_report['top_requested_symbols']:
        print("\n🏆 מניות המבוקשות ביותר:")
        for symbol, stats in usage_report['top_requested_symbols'][:5]:
            print(f"   {symbol}: {stats['total_requests']} בקשות")

def example_batch_processing():
    """דוגמה לעיבוד מרובה"""
    print("\n🔄 דוגמה לעיבוד מרובה")
    print("=" * 40)
    
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX']
    
    # עיבוד במקביל
    results = smart_data_manager.batch_process(
        symbols, 
        days=30, 
        max_workers=4
    )
    
    print(f"📊 עיבוד {len(symbols)} מניות במקביל:")
    
    successful = 0
    for symbol, data in results.items():
        if data is not None and not data.empty:
            successful += 1
            current_price = data['close'].iloc[0]
            print(f"   ✅ {symbol}: ${current_price:.2f}")
        else:
            print(f"   ❌ {symbol}: כישלון")
    
    print(f"\n🎯 הצלחה: {successful}/{len(symbols)} ({successful/len(symbols):.1%})")

def example_custom_manager():
    """דוגמה למופע מותאם אישית"""
    print("\n⚙️ דוגמה למופע מותאם אישית")
    print("=" * 40)
    
    # יצירת מופע מותאם אישית
    custom_manager = SmartDataManager(
        data_dir="custom_data",
        enable_compression=True,
        cache_size=50,
        enable_indexing=True
    )
    
    print("🔧 הגדרות מותאמות אישית:")
    print(f"   תיקיית נתונים: {custom_manager.data_dir}")
    print(f"   גודל מטמון: {custom_manager.cache_size}")
    print(f"   דחיסה: {custom_manager.enable_compression}")
    print(f"   אינדקס: {custom_manager.enable_indexing}")
    
    # שימוש במופע המותאם
    data = custom_manager.get_stock_data('AAPL', days=7)
    if data is not None:
        print(f"   ✅ נתונים התקבלו: {len(data)} שורות")

def example_data_optimization():
    """דוגמה לאופטימיזציה"""
    print("\n🔧 דוגמה לאופטימיזציה")
    print("=" * 40)
    
    print("📦 אופטימיזציה של אחסון...")
    
    # אופטימיזציה
    smart_data_manager.optimize_storage()
    
    print("🧹 ניקוי נתונים ישנים...")
    
    # ניקוי נתונים ישנים
    smart_data_manager.cleanup_old_data(days_to_keep=365)
    
    print("✅ אופטימיזציה הושלמה")

def main():
    """הרצת כל הדוגמאות"""
    print("🚀 Smart Data Manager - דוגמאות שימוש")
    print("=" * 50)
    
    try:
        # דוגמאות בסיסיות
        example_basic_usage()
        example_multiple_stocks()
        
        # דוגמאות מתקדמות
        example_technical_analysis()
        example_news_sentiment()
        example_fundamentals()
        example_comprehensive_analysis()
        
        # דוגמאות ביצועים
        example_performance_monitoring()
        example_batch_processing()
        example_custom_manager()
        example_data_optimization()
        
        print("\n🎉 כל הדוגמאות הושלמו בהצלחה!")
        
    except Exception as e:
        print(f"\n❌ שגיאה בהרצת דוגמאות: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 