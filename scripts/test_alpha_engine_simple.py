import sys
import os
sys.path.append('.')

from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

def main():
    print("Testing AlphaScoreEngine with Fixed Agents...")
    
    # Initialize components
    data_fetcher = DataFetcher()
    alpha_engine = AlphaScoreEngine()
    
    # Test with AAPL only
    symbol = "AAPL"
    print(f"\n=== Analyzing {symbol} ===")
    
    try:
        # Get price data
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        # Run analysis
        result = alpha_engine.evaluate(symbol, price_df)
        
        print(f"Overall Score: {result['score']}/100")
        print(f"Recommendation: {result['recommendation']}")
        
        # Count working vs dummy agents
        scores = result['signals']
        working_agents = [name for name, score in scores.items() if score > 1]
        dummy_agents = [name for name, score in scores.items() if score == 1]
        
        print(f"\nWorking Agents ({len(working_agents)}):")
        for agent in working_agents[:10]:  # Show first 10
            score = scores[agent]
            print(f"  {agent}: {score}/100")
        
        print(f"\nDummy Agents ({len(dummy_agents)}):")
        for agent in dummy_agents[:10]:  # Show first 10
            print(f"  {agent}")
        
        print(f"\nSuccess Rate: {len(working_agents)}/{len(scores)} agents working ({len(working_agents)/len(scores)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 