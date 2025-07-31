"""
בדיקה מקיפה של 7 הסוכנים המשודרגים עם נתונים אמיתיים
=======================================================
סקריפט זה בודק את כל הסוכנים המשודרגים על מניה אמיתית
ומציג את התוצאות בפורמט ברור ומובנה.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

# Import all upgraded agents
from core.news_catalyst_agent import NewsCatalystAgent
from core.gap_detector_ultimate import GapDetectorUltimate
from core.earnings_surprise_tracker import EarningsSurpriseTracker
from core.growth_scanner import GrowthConsistencyScanner
from core.valuation_detector import ValuationAnomalyDetector
from core.sentiment_scorer import SentimentScorer
from core.geopolitical_risk_monitor import GeopoliticalRiskMonitor

def fetch_real_stock_data(symbol: str, days: int = 252) -> pd.DataFrame:
    """
    שליפת נתוני מניה אמיתיים מ-Yahoo Finance
    """
    try:
        print(f"📊 שולף נתונים עבור {symbol}...")
        stock = yf.Ticker(symbol)
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"❌ לא ניתן לקבל נתונים עבור {symbol}")
            return None
        
        # Ensure we have required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df.columns:
                print(f"❌ חסר עמודה {col} בנתונים")
                return None
        
        # Rename columns to match our system
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        print(f"✅ התקבלו {len(df)} שורות נתונים עבור {symbol}")
        return df
        
    except Exception as e:
        print(f"❌ שגיאה בשליפת נתונים: {e}")
        return None

def test_agent(agent, agent_name: str, symbol: str, price_df: pd.DataFrame):
    """
    בדיקת סוכן בודד והצגת התוצאות
    """
    print(f"\n{'='*60}")
    print(f"🔍 בדיקת {agent_name}")
    print(f"{'='*60}")
    
    try:
        # Run agent analysis
        start_time = datetime.now()
        result = agent.analyze(symbol, price_df)
        end_time = datetime.now()
        
        analysis_time = (end_time - start_time).total_seconds()
        
        # Display results
        print(f"📈 תוצאות {agent_name}:")
        print(f"   Score: {result.get('score', 'N/A')}/100")
        print(f"   Explanation: {result.get('explanation', 'N/A')}")
        print(f"   Analysis Time: {analysis_time:.2f} seconds")
        
        # Display signal structure
        if 'signal' in result:
            signal = result['signal']
            print(f"   Signal Type: {signal.get('type', 'N/A')}")
            print(f"   Signal Score: {signal.get('score', 'N/A')}")
            print(f"   Signal Reason: {signal.get('reason', 'N/A')[:100]}...")
        
        # Display key details
        if 'details' in result:
            details = result['details']
            print(f"   Key Metrics:")
            for key, value in details.items():
                if isinstance(value, (int, float)):
                    print(f"     {key}: {value}")
                elif isinstance(value, dict):
                    print(f"     {key}: {len(value)} items")
                elif isinstance(value, list):
                    print(f"     {key}: {len(value)} items")
        
        return result
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקת {agent_name}: {e}")
        return None

def test_auto_triggers(agent, symbol: str):
    """
    בדיקת Auto-Triggers (אם קיים)
    """
    if hasattr(agent, 'get_auto_triggers'):
        print(f"\n🔔 בדיקת Auto-Triggers עבור {symbol}:")
        try:
            triggers = agent.get_auto_triggers(symbol)
            if 'auto_triggers' in triggers:
                auto_triggers = triggers['auto_triggers']
                print(f"   Active Triggers: {auto_triggers.get('triggers_active', False)}")
                if auto_triggers.get('triggers_active'):
                    trigger_types = auto_triggers.get('trigger_types', {})
                    for trigger_type, active in trigger_types.items():
                        if active:
                            print(f"     ✅ {trigger_type}")
        except Exception as e:
            print(f"   ❌ שגיאה בבדיקת Auto-Triggers: {e}")

def test_sector_comparison(agent, symbol: str):
    """
    בדיקת השוואה סקטורית (אם קיים)
    """
    if hasattr(agent, 'get_sector_peers_comparison'):
        print(f"\n🏢 בדיקת השוואה סקטורית עבור {symbol}:")
        try:
            # This would need growth_metrics, so we'll skip for now
            print("   (דורש נתונים פיננסיים נוספים)")
        except Exception as e:
            print(f"   ❌ שגיאה בהשוואה סקטורית: {e}")

def run_comprehensive_test(symbol: str = "AAPL"):
    """
    הרצת בדיקה מקיפה על כל הסוכנים
    """
    print(f"🚀 בדיקה מקיפה של 7 הסוכנים המשודרגים")
    print(f"📊 מניה: {symbol}")
    print(f"⏰ זמן בדיקה: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fetch real stock data
    price_df = fetch_real_stock_data(symbol)
    if price_df is None:
        print("❌ לא ניתן להמשיך ללא נתוני מניה")
        return
    
    # Initialize all agents
    agents = {
        "NewsCatalystAgent": NewsCatalystAgent(),
        "GapDetectorUltimate": GapDetectorUltimate(),
        "EarningsSurpriseTracker": EarningsSurpriseTracker(),
        "GrowthConsistencyScanner": GrowthConsistencyScanner(),
        "ValuationAnomalyDetector": ValuationAnomalyDetector(),
        "SentimentScorer": SentimentScorer(),
        "GeopoliticalRiskMonitor": GeopoliticalRiskMonitor()
    }
    
    # Test each agent
    results = {}
    for agent_name, agent in agents.items():
        result = test_agent(agent, agent_name, symbol, price_df)
        results[agent_name] = result
        
        # Test additional features if available
        if agent_name == "EarningsSurpriseTracker":
            test_auto_triggers(agent, symbol)
        elif agent_name == "GrowthConsistencyScanner":
            test_sector_comparison(agent, symbol)
    
    # Summary report
    print(f"\n{'='*60}")
    print(f"📋 דוח סיכום - {symbol}")
    print(f"{'='*60}")
    
    successful_agents = 0
    total_score = 0
    
    for agent_name, result in results.items():
        if result and 'score' in result:
            score = result['score']
            total_score += score
            successful_agents += 1
            
            status = "✅" if score >= 70 else "⚠️" if score >= 40 else "❌"
            print(f"{status} {agent_name}: {score}/100")
        else:
            print(f"❌ {agent_name}: לא זמין")
    
    if successful_agents > 0:
        avg_score = total_score / successful_agents
        print(f"\n📊 ממוצע כללי: {avg_score:.1f}/100")
        print(f"🎯 סוכנים פעילים: {successful_agents}/7")
        
        if avg_score >= 70:
            print("🌟 מערכת ברמה מעולה!")
        elif avg_score >= 50:
            print("👍 מערכת ברמה טובה")
        else:
            print("⚠️ מערכת דורשת שיפור")
    
    return results

def test_multiple_stocks():
    """
    בדיקה על מספר מניות שונות
    """
    test_stocks = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]
    
    print(f"🔍 בדיקה על {len(test_stocks)} מניות שונות")
    
    for symbol in test_stocks:
        print(f"\n{'#'*80}")
        print(f"📈 בדיקת {symbol}")
        print(f"{'#'*80}")
        
        try:
            results = run_comprehensive_test(symbol)
            
            # Quick summary for this stock
            if results:
                scores = [r['score'] for r in results.values() if r and 'score' in r]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    print(f"📊 ממוצע {symbol}: {avg_score:.1f}/100")
            
        except Exception as e:
            print(f"❌ שגיאה בבדיקת {symbol}: {e}")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    print("🧪 בדיקת סוכנים משודרגים עם נתונים אמיתיים")
    print("="*80)
    
    # Test single stock
    print("1️⃣ בדיקה על מניה בודדת (AAPL)")
    run_comprehensive_test("AAPL")
    
    # Ask user if they want to test multiple stocks
    print(f"\n{'='*80}")
    response = input("האם תרצה לבדוק על מניות נוספות? (y/n): ")
    
    if response.lower() in ['y', 'yes', 'כן']:
        print("\n2️⃣ בדיקה על מספר מניות")
        test_multiple_stocks()
    
    print("\n✅ בדיקה הושלמה!") 