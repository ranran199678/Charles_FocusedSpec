import os
import pandas as pd
import numpy as np
from datetime import datetime

def check_technical_indicators():
    """בדיקת האינדיקטורים הטכניים שנוצרו"""
    
    print("🔍 בודק אינדיקטורים טכניים...")
    print("=" * 60)
    
    indicators_dir = "data/technical_indicators"
    
    if not os.path.exists(indicators_dir):
        print("❌ תיקיית האינדיקטורים לא קיימת")
        return
    
    # רשימת האינדיקטורים
    indicators = ['rsi', 'macd', 'bollinger', 'sma', 'ema', 'atr', 'stochastic', 'adx', 'cci']
    timeframes = ['daily', 'weekly', 'monthly']
    
    summary = {}
    
    for indicator in indicators:
        indicator_path = os.path.join(indicators_dir, indicator)
        if os.path.exists(indicator_path):
            print(f"\n📊 {indicator.upper()}:")
            
            indicator_summary = {}
            
            for timeframe in timeframes:
                timeframe_path = os.path.join(indicator_path, timeframe)
                if os.path.exists(timeframe_path):
                    files = [f for f in os.listdir(timeframe_path) if f.endswith('.csv')]
                    
                    if files:
                        print(f"   📅 {timeframe}: {len(files)} קבצים")
                        
                        # בדיקת קובץ לדוגמה
                        sample_file = os.path.join(timeframe_path, files[0])
                        try:
                            df = pd.read_csv(sample_file)
                            print(f"      📈 דוגמה: {files[0]} - {len(df)} שורות")
                            
                            indicator_summary[timeframe] = {
                                'files': len(files),
                                'sample_rows': len(df),
                                'columns': list(df.columns)
                            }
                            
                        except Exception as e:
                            print(f"      ❌ שגיאה בקריאת {files[0]}: {str(e)}")
                    else:
                        print(f"   📅 {timeframe}: אין קבצים")
                else:
                    print(f"   📅 {timeframe}: תיקייה לא קיימת")
            
            summary[indicator] = indicator_summary
        else:
            print(f"❌ תיקיית {indicator} לא קיימת")
    
    return summary

def analyze_indicator_data():
    """ניתוח נתוני אינדיקטורים לדוגמה"""
    
    print(f"\n📈 ניתוח נתוני אינדיקטורים לדוגמה...")
    print("=" * 60)
    
    # בדיקת RSI לדוגמה
    rsi_file = "data/technical_indicators/rsi/daily/APPLE_rsi_daily.csv"
    
    if os.path.exists(rsi_file):
        try:
            df = pd.read_csv(rsi_file)
            print(f"\n📊 RSI - APPLE:")
            print(f"   📈 שורות: {len(df)}")
            print(f"   📅 טווח: {df['date'].iloc[0]} עד {df['date'].iloc[-1]}")
            print(f"   📊 עמודות: {', '.join(df.columns)}")
            print(f"   📊 ערך RSI ממוצע: {df['value'].mean():.2f}")
            print(f"   📊 ערך RSI מינימלי: {df['value'].min():.2f}")
            print(f"   📊 ערך RSI מקסימלי: {df['value'].max():.2f}")
            
            # בדיקת ערכי RSI קיצוניים
            oversold = df[df['value'] < 30]
            overbought = df[df['value'] > 70]
            print(f"   📉 מצבי oversold (<30): {len(oversold)} פעמים")
            print(f"   📈 מצבי overbought (>70): {len(overbought)} פעמים")
            
        except Exception as e:
            print(f"❌ שגיאה בניתוח RSI: {str(e)}")
    
    # בדיקת MACD לדוגמה
    macd_file = "data/technical_indicators/macd/daily/APPLE_macd_daily.csv"
    
    if os.path.exists(macd_file):
        try:
            df = pd.read_csv(macd_file)
            print(f"\n📊 MACD - APPLE:")
            print(f"   📈 שורות: {len(df)}")
            print(f"   📊 ערך MACD ממוצע: {df['value'].mean():.4f}")
            print(f"   📊 ערך MACD מינימלי: {df['value'].min():.4f}")
            print(f"   📊 ערך MACD מקסימלי: {df['value'].max():.4f}")
            
            # בדיקת חוצי אפס
            positive_macd = df[df['value'] > 0]
            negative_macd = df[df['value'] < 0]
            print(f"   📈 MACD חיובי: {len(positive_macd)} פעמים")
            print(f"   📉 MACD שלילי: {len(negative_macd)} פעמים")
            
        except Exception as e:
            print(f"❌ שגיאה בניתוח MACD: {str(e)}")
    
    # בדיקת Bollinger Bands לדוגמה
    bb_upper_file = "data/technical_indicators/bollinger/daily/APPLE_bollinger_upper_daily.csv"
    bb_lower_file = "data/technical_indicators/bollinger/daily/APPLE_bollinger_lower_daily.csv"
    
    if os.path.exists(bb_upper_file) and os.path.exists(bb_lower_file):
        try:
            df_upper = pd.read_csv(bb_upper_file)
            df_lower = pd.read_csv(bb_lower_file)
            
            print(f"\n📊 Bollinger Bands - APPLE:")
            print(f"   📈 שורות: {len(df_upper)}")
            print(f"   📊 ערך עליון ממוצע: {df_upper['value'].mean():.2f}")
            print(f"   📊 ערך תחתון ממוצע: {df_lower['value'].mean():.2f}")
            print(f"   📊 רוחב ממוצע: {df_upper['value'].mean() - df_lower['value'].mean():.2f}")
            
        except Exception as e:
            print(f"❌ שגיאה בניתוח Bollinger Bands: {str(e)}")

def create_indicators_report(summary):
    """יצירת דוח אינדיקטורים"""
    
    report_file = f"technical_indicators_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    report = f"""# דוח אינדיקטורים טכניים - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## סיכום אינדיקטורים

"""
    
    for indicator, timeframes in summary.items():
        report += f"""### {indicator.upper()}

"""
        
        for timeframe, data in timeframes.items():
            if data:
                report += f"""#### {timeframe}
- **קבצים**: {data['files']}
- **שורות לדוגמה**: {data['sample_rows']}
- **עמודות**: {', '.join(data['columns'])}

"""
    
    report += f"""
## סיכום כללי

- **אינדיקטורים זמינים**: {len(summary)}
- **פרקי זמן**: {', '.join(timeframes)}
- **סך קבצים**: {sum(len(tf) for ind in summary.values() for tf in ind.values() if tf)}

---
*דוח נוצר אוטומטית ב-{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ דוח אינדיקטורים נוצר: {report_file}")
    return report_file

def main():
    """הפונקציה הראשית"""
    
    print("🚀 מתחיל בדיקת אינדיקטורים טכניים...")
    print("=" * 60)
    
    # בדיקת אינדיקטורים
    summary = check_technical_indicators()
    
    # ניתוח נתונים לדוגמה
    analyze_indicator_data()
    
    # יצירת דוח
    report_file = create_indicators_report(summary)
    
    # סיכום
    print(f"\n{'='*60}")
    print("📊 סיכום בדיקת אינדיקטורים:")
    print(f"{'='*60}")
    
    total_files = sum(len(tf) for ind in summary.values() for tf in ind.values() if tf)
    print(f"✅ אינדיקטורים זמינים: {len(summary)}")
    print(f"📁 סך קבצים: {total_files}")
    print(f"📄 דוח: {report_file}")
    
    print("\n🎉 בדיקת האינדיקטורים הושלמה בהצלחה!")

if __name__ == "__main__":
    main() 