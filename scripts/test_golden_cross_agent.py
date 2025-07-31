import sys
import os
sys.path.append('.')

from core.golden_cross_detector import GoldenCrossAgent
from utils.data_fetcher import DataFetcher

def test_golden_cross_agent():
    print("=== בדיקת GoldenCrossAgent ===")
    
    # יצירת סוכן
    agent = GoldenCrossAgent()
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    # בדיקת מניות
    symbols = ["INTC", "QBTS", "AAPL"]
    
    for symbol in symbols:
        print(f"\n--- {symbol} ---")
        
        try:
            # קבלת נתוני מחיר
            price_df = data_fetcher.get_price_history(symbol, period="200d")
            
            print(f"מחיר אחרון: {price_df['close'].iloc[-1]:.2f}")
            print(f"תאריכים: {price_df.index[0]} עד {price_df.index[-1]}")
            
            # ניתוח
            result = agent.analyze(symbol, price_df)
            
            print(f"ציון: {result.get('score', 'N/A')}/100")
            print(f"הסבר: {result.get('explanation', 'N/A')}")
            
            # פרטים נוספים
            if 'details' in result and 'cross_analysis' in result['details']:
                cross_analysis = result['details']['cross_analysis']
                current_pos = cross_analysis.get('current_position', {})
                
                print(f"מיקום נוכחי: {current_pos.get('position', 'N/A')}")
                print(f"פער ממוצעים: {current_pos.get('ma_gap_percent', 'N/A'):.1f}%")
                print(f"צלבים מוזהבים: {cross_analysis.get('total_golden_crosses', 'N/A')}")
                print(f"צלבי מוות: {cross_analysis.get('total_death_crosses', 'N/A')}")
                
                # צלב אחרון
                last_golden = cross_analysis.get('last_golden_cross')
                last_death = cross_analysis.get('last_death_cross')
                
                if last_golden:
                    print(f"צלב מוזהב אחרון: {last_golden.get('freshness_level', 'N/A')} ({last_golden.get('days_since', 'N/A')} ימים)")
                
                if last_death:
                    print(f"צלב מוות אחרון: {last_death.get('freshness_level', 'N/A')} ({last_death.get('days_since', 'N/A')} ימים)")
            
            # המלצות
            if 'details' in result and 'recommendations' in result['details']:
                recommendations = result['details']['recommendations']
                print(f"המלצות: {', '.join(recommendations)}")
            
        except Exception as e:
            print(f"שגיאה: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_golden_cross_agent() 