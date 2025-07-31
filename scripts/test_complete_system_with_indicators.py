import os
import pandas as pd
import sys
from datetime import datetime

# הוספת הנתיב למערכת
sys.path.append('.')

def load_stock_data_with_indicators(symbol):
    """טעינת נתוני מניה עם אינדיקטורים"""
    
    # טעינת נתוני מחירים
    price_file = f"data/historical_prices/daily/{symbol}.csv"
    if not os.path.exists(price_file):
        print(f"❌ קובץ מחירים לא נמצא: {price_file}")
        return None
    
    df = pd.read_csv(price_file)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df.set_index('Date', inplace=True)
    
    # טעינת אינדיקטורים
    indicators = {}
    
    # RSI
    rsi_file = f"data/technical_indicators/rsi/daily/{symbol}_rsi_daily.csv"
    if os.path.exists(rsi_file):
        rsi_df = pd.read_csv(rsi_file)
        rsi_df['date'] = pd.to_datetime(rsi_df['date'])
        rsi_df.set_index('date', inplace=True)
        indicators['rsi'] = rsi_df['value']
    
    # MACD
    macd_file = f"data/technical_indicators/macd/daily/{symbol}_macd_daily.csv"
    if os.path.exists(macd_file):
        macd_df = pd.read_csv(macd_file)
        macd_df['date'] = pd.to_datetime(macd_df['date'])
        macd_df.set_index('date', inplace=True)
        indicators['macd'] = macd_df['value']
    
    # Bollinger Bands
    bb_upper_file = f"data/technical_indicators/bollinger/daily/{symbol}_bollinger_upper_daily.csv"
    bb_lower_file = f"data/technical_indicators/bollinger/daily/{symbol}_bollinger_lower_daily.csv"
    
    if os.path.exists(bb_upper_file) and os.path.exists(bb_lower_file):
        bb_upper_df = pd.read_csv(bb_upper_file)
        bb_lower_df = pd.read_csv(bb_lower_file)
        
        bb_upper_df['date'] = pd.to_datetime(bb_upper_df['date'])
        bb_lower_df['date'] = pd.to_datetime(bb_lower_df['date'])
        
        bb_upper_df.set_index('date', inplace=True)
        bb_lower_df.set_index('date', inplace=True)
        
        indicators['bb_upper'] = bb_upper_df['value']
        indicators['bb_lower'] = bb_lower_df['value']
    
    # SMA
    sma_file = f"data/technical_indicators/sma/daily/{symbol}_sma_20_daily.csv"
    if os.path.exists(sma_file):
        sma_df = pd.read_csv(sma_file)
        sma_df['date'] = pd.to_datetime(sma_df['date'])
        sma_df.set_index('date', inplace=True)
        indicators['sma_20'] = sma_df['value']
    
    # הוספת אינדיקטורים ל-DataFrame הראשי
    for indicator_name, indicator_values in indicators.items():
        df[indicator_name] = indicator_values
    
    return df

def test_enhanced_analysis(symbol):
    """בדיקת ניתוח מתקדם עם אינדיקטורים"""
    
    print(f"\n{'='*60}")
    print(f"📈 ניתוח מתקדם עבור {symbol}")
    print(f"{'='*60}")
    
    # טעינת נתונים עם אינדיקטורים
    df = load_stock_data_with_indicators(symbol)
    
    if df is None:
        print(f"❌ לא ניתן לטעון נתונים עבור {symbol}")
        return None
    
    print(f"📊 נתונים נטענו: {len(df)} שורות")
    print(f"💰 מחיר אחרון: ${df['Price'].iloc[-1]:.2f}")
    
    # בדיקת אינדיקטורים זמינים
    available_indicators = [col for col in df.columns if col not in ['Price', 'Open', 'High', 'Low', 'Vol.', 'Change %']]
    print(f"📊 אינדיקטורים זמינים: {', '.join(available_indicators)}")
    
    # ניתוח RSI
    if 'rsi' in df.columns:
        current_rsi = df['rsi'].iloc[-1]
        print(f"📊 RSI נוכחי: {current_rsi:.2f}")
        
        if current_rsi < 30:
            print(f"   📉 מצב oversold - הזדמנות קנייה")
        elif current_rsi > 70:
            print(f"   📈 מצב overbought - הזדמנות מכירה")
        else:
            print(f"   📊 RSI בטווח נורמלי")
    
    # ניתוח MACD
    if 'macd' in df.columns:
        current_macd = df['macd'].iloc[-1]
        print(f"📊 MACD נוכחי: {current_macd:.4f}")
        
        if current_macd > 0:
            print(f"   📈 MACD חיובי - מגמה עולה")
        else:
            print(f"   📉 MACD שלילי - מגמה יורדת")
    
    # ניתוח Bollinger Bands
    if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
        current_price = df['Price'].iloc[-1]
        current_upper = df['bb_upper'].iloc[-1]
        current_lower = df['bb_lower'].iloc[-1]
        
        print(f"📊 Bollinger Bands:")
        print(f"   📈 עליון: ${current_upper:.2f}")
        print(f"   📉 תחתון: ${current_lower:.2f}")
        print(f"   💰 מחיר נוכחי: ${current_price:.2f}")
        
        if current_price > current_upper:
            print(f"   📈 מחיר מעל הפס העליון - יתכן overbought")
        elif current_price < current_lower:
            print(f"   📉 מחיר מתחת לפס התחתון - יתכן oversold")
        else:
            print(f"   📊 מחיר בטווח נורמלי")
    
    # ניתוח SMA
    if 'sma_20' in df.columns:
        current_price = df['Price'].iloc[-1]
        current_sma = df['sma_20'].iloc[-1]
        
        print(f"📊 SMA 20: ${current_sma:.2f}")
        
        if current_price > current_sma:
            print(f"   📈 מחיר מעל SMA - מגמה חיובית")
        else:
            print(f"   📉 מחיר מתחת ל-SMA - מגמה שלילית")
    
    return {
        'symbol': symbol,
        'rows': len(df),
        'last_price': df['Price'].iloc[-1],
        'indicators': available_indicators,
        'rsi': df['rsi'].iloc[-1] if 'rsi' in df.columns else None,
        'macd': df['macd'].iloc[-1] if 'macd' in df.columns else None,
        'sma_20': df['sma_20'].iloc[-1] if 'sma_20' in df.columns else None
    }

def create_enhanced_report(results_list):
    """יצירת דוח ניתוח מתקדם"""
    
    report_file = f"enhanced_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    report = f"""# דוח ניתוח מתקדם עם אינדיקטורים - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## סיכום ניתוחים

"""
    
    successful_results = [r for r in results_list if r is not None]
    
    for result in successful_results:
        report += f"""### {result['symbol']}

- **שורות נתונים**: {result['rows']:,}
- **מחיר אחרון**: ${result['last_price']:.2f}
- **אינדיקטורים זמינים**: {', '.join(result['indicators'])}
- **RSI נוכחי**: {result['rsi']:.2f if result['rsi'] else 'N/A'}
- **MACD נוכחי**: {result['macd']:.4f if result['macd'] else 'N/A'}
- **SMA 20**: ${result['sma_20']:.2f if result['sma_20'] else 'N/A'}

"""
    
    if successful_results:
        report += f"""
## סיכום כללי

- **מניות שנבדקו**: {len(successful_results)}
- **סך שורות נתונים**: {sum(r['rows'] for r in successful_results):,}
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
    
    print(f"✅ דוח ניתוח מתקדם נוצר: {report_file}")
    return report_file

def main():
    """הפונקציה הראשית"""
    
    print("🚀 מתחיל ניתוח מתקדם עם אינדיקטורים...")
    print("=" * 60)
    
    # רשימת המניות לבדיקה
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    results_list = []
    
    for symbol in symbols:
        result = test_enhanced_analysis(symbol)
        results_list.append(result)
    
    # יצירת דוח
    report_file = create_enhanced_report(results_list)
    
    # סיכום
    print(f"\n{'='*60}")
    print("📊 סיכום ניתוח מתקדם:")
    print(f"{'='*60}")
    
    successful_analyses = [r for r in results_list if r]
    print(f"✅ ניתוחים הושלמו: {len(successful_analyses)}/{len(symbols)}")
    
    if successful_analyses:
        avg_price = sum(r['last_price'] for r in successful_analyses) / len(successful_analyses)
        print(f"💰 מחיר ממוצע: ${avg_price:.2f}")
        
        # ניתוח RSI ממוצע
        rsi_values = [r['rsi'] for r in successful_analyses if r['rsi']]
        if rsi_values:
            avg_rsi = sum(rsi_values) / len(rsi_values)
            print(f"📊 RSI ממוצע: {avg_rsi:.2f}")
    
    print(f"📄 דוח: {report_file}")
    print("\n🎉 הניתוח המתקדם הושלם בהצלחה!")

if __name__ == "__main__":
    main() 