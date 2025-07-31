import sys
import os
sys.path.append('.')

from utils.data_fetcher import DataFetcher
from core.adx_score_agent import ADXScoreAgent
from core.rsi_sniffer import RSICompressionSniffer
from core.volume_tension_meter import VolumeTensionMeter
from core.parabolic_agent import ParabolicAgent
from core.breakout_retest_recognizer import BreakoutRetestRecognizer
from core.support_zone_strength_detector import SupportResistanceZoneStrengthDetector

def test_agent(agent_class, agent_name, data_fetcher, symbol="AAPL"):
    """Test a single agent"""
    try:
        print(f"\n=== Testing {agent_name} ===")
        
        # Create agent instance
        if agent_name == "BreakoutRetestRecognizer":
            agent = agent_class(symbol=symbol)
        else:
            agent = agent_class()
        
        # Get price data
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        # Analyze
        result = agent.analyze(symbol, price_df)
        
        print(f"✅ {agent_name} - Score: {result.get('score', 'N/A')}")
        print(f"   Explanation: {result.get('explanation', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ {agent_name} - Error: {str(e)}")
        return False

def main():
    print("Testing Fixed Agents...")
    
    # Initialize data fetcher
    data_fetcher = DataFetcher()
    
    # List of agents to test
    agents_to_test = [
        (ADXScoreAgent, "ADXScoreAgent"),
        (RSICompressionSniffer, "RSICompressionSniffer"),
        (VolumeTensionMeter, "VolumeTensionMeter"),
        (ParabolicAgent, "ParabolicAgent"),
        (BreakoutRetestRecognizer, "BreakoutRetestRecognizer"),
        (SupportResistanceZoneStrengthDetector, "SupportZoneStrengthDetector"),
    ]
    
    success_count = 0
    total_count = len(agents_to_test)
    
    for agent_class, agent_name in agents_to_test:
        if test_agent(agent_class, agent_name, data_fetcher):
            success_count += 1
    
    print(f"\n=== Results ===")
    print(f"Success: {success_count}/{total_count} agents working")
    print(f"Success rate: {success_count/total_count*100:.1f}%")

if __name__ == "__main__":
    main() 