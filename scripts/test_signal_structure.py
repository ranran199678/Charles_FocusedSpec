"""
בדיקת מבנה Signal של כל 7 הסוכנים המשודרגים
==================================================
"""

def test_all_agents():
    """בדיקת כל הסוכנים עם מבנה Signal תקין"""
    
    print("🔍 בדיקת מבנה Signal של כל הסוכנים")
    print("="*50)
    
    # רשימת הסוכנים לבדיקה
    agents_to_test = [
        ("NewsCatalystAgent", "news_catalyst"),
        ("GapDetectorUltimate", "gap_analysis"),
        ("EarningsSurpriseTracker", "earnings_surprise"),
        ("GrowthConsistencyScanner", "growth_consistency"),
        ("ValuationAnomalyDetector", "valuation_anomaly"),
        ("SentimentScorer", "sentiment_analysis"),
        ("GeopoliticalRiskMonitor", "geopolitical_risk")
    ]
    
    results = {}
    
    for agent_name, expected_type in agents_to_test:
        try:
            # Import agent
            if agent_name == "NewsCatalystAgent":
                from core.news_catalyst_agent import NewsCatalystAgent
                agent = NewsCatalystAgent()
                result = agent.analyze('AAPL')
            elif agent_name == "GapDetectorUltimate":
                from core.gap_detector_ultimate import GapDetectorUltimate
                import pandas as pd
                import numpy as np
                agent = GapDetectorUltimate()
                df = pd.DataFrame({
                    'open': np.random.uniform(100, 110, 50),
                    'high': np.random.uniform(110, 120, 50),
                    'low': np.random.uniform(90, 100, 50),
                    'close': np.random.uniform(100, 110, 50),
                    'volume': np.random.uniform(1000000, 5000000, 50)
                })
                result = agent.analyze('AAPL', df)
            elif agent_name == "EarningsSurpriseTracker":
                from core.earnings_surprise_tracker import EarningsSurpriseTracker
                agent = EarningsSurpriseTracker()
                result = agent.analyze('AAPL')
            elif agent_name == "GrowthConsistencyScanner":
                from core.growth_scanner import GrowthConsistencyScanner
                agent = GrowthConsistencyScanner()
                result = agent.analyze('AAPL')
            elif agent_name == "ValuationAnomalyDetector":
                from core.valuation_detector import ValuationAnomalyDetector
                agent = ValuationAnomalyDetector()
                result = agent.analyze('AAPL')
            elif agent_name == "SentimentScorer":
                from core.sentiment_scorer import SentimentScorer
                agent = SentimentScorer()
                result = agent.analyze('AAPL')
            elif agent_name == "GeopoliticalRiskMonitor":
                from core.geopolitical_risk_monitor import GeopoliticalRiskMonitor
                agent = GeopoliticalRiskMonitor()
                result = agent.analyze('AAPL')
            
            # בדיקת מבנה Signal
            has_signal = 'signal' in result
            has_type = has_signal and 'type' in result['signal']
            correct_type = has_type and result['signal']['type'] == expected_type
            has_score = has_signal and 'score' in result['signal']
            has_reason = has_signal and 'reason' in result['signal']
            has_confidence = has_signal and 'confidence' in result['signal']
            
            # תוצאות
            status = "✅" if all([has_signal, has_type, correct_type, has_score, has_reason, has_confidence]) else "❌"
            
            print(f"{status} {agent_name}:")
            print(f"   Signal: {has_signal}")
            print(f"   Type: {has_type} ({result['signal']['type'] if has_type else 'N/A'})")
            print(f"   Correct Type: {correct_type}")
            print(f"   Score: {has_score}")
            print(f"   Reason: {has_reason}")
            print(f"   Confidence: {has_confidence}")
            
            results[agent_name] = {
                "status": status,
                "has_signal": has_signal,
                "has_type": has_type,
                "correct_type": correct_type,
                "has_score": has_score,
                "has_reason": has_reason,
                "has_confidence": has_confidence
            }
            
        except Exception as e:
            print(f"❌ {agent_name}: שגיאה - {e}")
            results[agent_name] = {"status": "❌", "error": str(e)}
    
    # סיכום
    print("\n" + "="*50)
    print("📊 סיכום בדיקת מבנה Signal")
    print("="*50)
    
    successful_agents = 0
    total_agents = len(agents_to_test)
    
    for agent_name, result in results.items():
        if result.get("status") == "✅":
            successful_agents += 1
            print(f"✅ {agent_name}: תקין")
        else:
            print(f"❌ {agent_name}: לא תקין")
    
    print(f"\n🎯 תוצאות: {successful_agents}/{total_agents} סוכנים תקינים")
    
    if successful_agents == total_agents:
        print("🎉 כל הסוכנים תקינים! מבנה Signal מושלם!")
    else:
        print("⚠️ יש סוכנים שדורשים תיקון")
    
    return results

if __name__ == "__main__":
    test_all_agents() 