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
    
    # Test symbols
    symbols = ["AAPL", "INTC", "QBTS"]
    
    for symbol in symbols:
        print(f"\n=== Analyzing {symbol} ===")
        
        try:
            # Get price data
            price_df = data_fetcher.get_price_history(symbol, period="100d")
            
            # Run analysis
            result = alpha_engine.evaluate(symbol, price_df)
            
            print(f"Overall Score: {result['score']}/100")
            print(f"Recommendation: {result['recommendation']}")
            
            # Show top 5 agent scores
            scores = result['signals']
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            print("\nTop 5 Agent Scores:")
            for agent_name, score in sorted_scores[:5]:
                explanation = result['explanations'].get(agent_name, 'No explanation')
                print(f"  {agent_name}: {score}/100 - {explanation[:100]}...")
            
            print(f"\nBottom 5 Agent Scores:")
            for agent_name, score in sorted_scores[-5:]:
                explanation = result['explanations'].get(agent_name, 'No explanation')
                print(f"  {agent_name}: {score}/100 - {explanation[:100]}...")
                
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 