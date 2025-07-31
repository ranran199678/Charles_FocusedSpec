import os
import sys
import pandas as pd
from datetime import datetime

# הוספת הנתיב למערכת
sys.path.append('.')

def load_stock_data(symbol):
    """טעינת נתוני מניה"""
    file_path = f"data/historical_prices/daily/{symbol}.csv"
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # המרת עמודת התאריך
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
        df.set_index('Date', inplace=True)
        return df
    else:
        print(f"❌ הקובץ לא נמצא: {file_path}")
        return None

def test_alpha_score_engine(symbol, df):
    """בדיקת מנוע Alpha Score"""
    print(f"\n🔍 בודק Alpha Score Engine עבור {symbol}...")
    
    try:
        from core.alpha_score_engine import AlphaScoreEngine
        
        # יצירת מנוע
        engine = AlphaScoreEngine()
        
        # העתקת DataFrame לפורמט הנדרש
        price_data = df.copy()
        price_data.columns = [col.lower() for col in price_data.columns]
        
        # חישוב ציון
        result = engine.evaluate(symbol, price_data)
        
        if result and 'score' in result:
            score = result['score']
            print(f"   📊 Alpha Score: {score:.2f}")
            return score
        else:
            print(f"   ⚠️ לא התקבל ציון תקין")
            return None
        
    except Exception as e:
        print(f"   ❌ שגיאה: {str(e)}")
        return None

def test_pattern_analyzer(symbol, df):
    """בדיקת מנתח תבניות"""
    print(f"\n🔍 בודק Pattern Analyzer עבור {symbol}...")
    
    try:
        from core.advanced_pattern_analyzer import AdvancedPatternAnalyzer
        
        # יצירת מנתח
        analyzer = AdvancedPatternAnalyzer()
        
        # ניתוח תבניות
        patterns = analyzer.analyze(df)
        
        if patterns:
            print(f"   📈 תבניות זוהו: {len(patterns)}")
            
            for pattern in patterns[:3]:  # הצגת 3 הראשונות
                if isinstance(pattern, dict):
                    pattern_type = pattern.get('type', 'Unknown')
                    confidence = pattern.get('confidence', 0)
                    print(f"      - {pattern_type}: {confidence:.2f}")
                else:
                    print(f"      - {pattern}")
        else:
            print(f"   📈 לא זוהו תבניות")
        
        return patterns
        
    except Exception as e:
        print(f"   ❌ שגיאה: {str(e)}")
        return None

def test_adx_agent(symbol, df):
    """בדיקת סוכן ADX"""
    print(f"\n🔍 בודק ADX Agent עבור {symbol}...")
    
    try:
        from core.adx_score_agent import ADXScoreAgent
        
        # יצירת סוכן
        agent = ADXScoreAgent()
        
        # חישוב ציון ADX
        result = agent.analyze(symbol, df)
        
        if result and 'score' in result:
            adx_score = result['score']
            print(f"   📊 ADX Score: {adx_score:.2f}")
            return adx_score
        else:
            print(f"   ⚠️ לא התקבל ציון ADX")
            return None
        
    except Exception as e:
        print(f"   ❌ שגיאה: {str(e)}")
        return None

def run_complete_analysis(symbol):
    """הרצת ניתוח מלא למניה"""
    
    print(f"\n{'='*60}")
    print(f"📈 ניתוח מלא עבור {symbol}")
    print(f"{'='*60}")
    
    # טעינת נתונים
    df = load_stock_data(symbol)
    
    if df is None:
        print(f"❌ לא ניתן לטעון נתונים עבור {symbol}")
        return None
    
    print(f"📊 נתונים נטענו: {len(df)} שורות")
    print(f"💰 מחיר אחרון: ${df['Price'].iloc[-1]:.2f}")
    
    results = {
        'symbol': symbol,
        'data_rows': len(df),
        'last_price': df['Price'].iloc[-1],
        'alpha_score': None,
        'patterns': None,
        'adx_score': None
    }
    
    # בדיקת Alpha Score Engine
    alpha_score = test_alpha_score_engine(symbol, df)
    results['alpha_score'] = alpha_score
    
    # בדיקת Pattern Analyzer
    patterns = test_pattern_analyzer(symbol, df)
    results['patterns'] = patterns
    
    # בדיקת ADX Agent
    adx_score = test_adx_agent(symbol, df)
    results['adx_score'] = adx_score
    
    return results

def create_analysis_report(results_list):
    """יצירת דוח ניתוח"""
    
    report_file = f"complete_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    report = f"""# דוח ניתוח מלא - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## סיכום ניתוחים

"""
    
    successful_results = [r for r in results_list if r is not None]
    
    for result in successful_results:
        report += f"""### {result['symbol']}

- **שורות נתונים**: {result['data_rows']:,}
- **מחיר אחרון**: ${result['last_price']:.2f}
- **Alpha Score**: {result['alpha_score']:.2f if result['alpha_score'] else 'N/A'}
- **ADX Score**: {result['adx_score']:.2f if result['adx_score'] else 'N/A'}
- **תבניות זוהו**: {len(result['patterns']) if result['patterns'] else 0}

"""
    
    if successful_results:
        report += f"""
## סיכום כללי

- **מניות שנבדקו**: {len(successful_results)}
- **סך שורות נתונים**: {sum(r['data_rows'] for r in successful_results):,}
- **מחיר ממוצע**: ${sum(r['last_price'] for r in successful_results) / len(successful_results):.2f}

"""
    else:
        report += "❌ לא הושלמו ניתוחים מוצלחים\n"
    
    report += f"""
---
*דוח נוצר אוטומטית ב-{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ דוח ניתוח נוצר: {report_file}")
    return report_file

def main():
    """הפונקציה הראשית"""
    
    print("🚀 מתחיל ניתוח מלא של המערכת...")
    print("=" * 60)
    
    # רשימת המניות לבדיקה
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    results_list = []
    
    for symbol in symbols:
        result = run_complete_analysis(symbol)
        results_list.append(result)
    
    # יצירת דוח
    report_file = create_analysis_report(results_list)
    
    # סיכום
    print(f"\n{'='*60}")
    print("📊 סיכום ניתוח:")
    print(f"{'='*60}")
    
    successful_analyses = [r for r in results_list if r]
    print(f"✅ ניתוחים הושלמו: {len(successful_analyses)}/{len(symbols)}")
    
    if successful_analyses:
        avg_price = sum(r['last_price'] for r in successful_analyses) / len(successful_analyses)
        print(f"💰 מחיר ממוצע: ${avg_price:.2f}")
        
        alpha_scores = [r['alpha_score'] for r in successful_analyses if r['alpha_score']]
        if alpha_scores:
            avg_alpha = sum(alpha_scores) / len(alpha_scores)
            print(f"📊 Alpha Score ממוצע: {avg_alpha:.2f}")
    
    print(f"📄 דוח: {report_file}")
    print("\n🎉 הניתוח הושלם!")

if __name__ == "__main__":
    main() 