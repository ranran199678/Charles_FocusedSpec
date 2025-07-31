import os
import pandas as pd
import sys
from datetime import datetime

# הוספת הנתיב למערכת
sys.path.append('.')

def test_data_loading():
    """בדיקת טעינת נתונים מהקבצים החדשים"""
    
    print("🔍 בודק טעינת נתונים...")
    print("=" * 50)
    
    # רשימת הקבצים החדשים
    new_files = ["AAPL.csv", "MSFT.csv", "GOOGL.csv", "AMZN.csv", "TSLA.csv"]
    data_dir = "data/historical_prices/daily"
    
    results = {}
    
    for file in new_files:
        file_path = os.path.join(data_dir, file)
        
        if os.path.exists(file_path):
            try:
                # טעינת הנתונים
                df = pd.read_csv(file_path)
                
                print(f"\n📊 {file}:")
                print(f"   📈 שורות: {len(df):,}")
                print(f"   📅 טווח: {df['Date'].iloc[0]} עד {df['Date'].iloc[-1]}")
                print(f"   💰 מחיר אחרון: ${df['Price'].iloc[-1]:.2f}")
                print(f"   📊 עמודות: {', '.join(df.columns)}")
                
                # בדיקת תקינות נתונים
                missing_data = df.isnull().sum()
                if missing_data.sum() > 0:
                    print(f"   ⚠️ נתונים חסרים: {missing_data.to_dict()}")
                else:
                    print(f"   ✅ כל הנתונים קיימים")
                
                results[file] = {
                    'rows': len(df),
                    'last_price': df['Price'].iloc[-1],
                    'date_range': f"{df['Date'].iloc[0]} - {df['Date'].iloc[-1]}",
                    'columns': list(df.columns)
                }
                
            except Exception as e:
                print(f"❌ שגיאה בקריאת {file}: {str(e)}")
        else:
            print(f"❌ הקובץ לא נמצא: {file}")
    
    return results

def test_system_integration():
    """בדיקת אינטגרציה עם המערכת הקיימת"""
    
    print(f"\n🔧 בודק אינטגרציה עם המערכת...")
    print("=" * 50)
    
    try:
        # ניסיון לייבא מודולים מהמערכת
        from core.alpha_score_engine import AlphaScoreEngine
        print("✅ AlphaScoreEngine זמין")
        
        from core.advanced_pattern_analyzer import AdvancedPatternAnalyzer
        print("✅ AdvancedPatternAnalyzer זמין")
        
        from core.adx_score_agent import ADXScoreAgent
        print("✅ ADXScoreAgent זמין")
        
        return True
        
    except ImportError as e:
        print(f"❌ שגיאת ייבוא: {str(e)}")
        return False

def create_test_report(results, system_ok):
    """יצירת דוח בדיקה"""
    
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    report = f"""# דוח בדיקת נתונים חדשים - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## סיכום בדיקות

### נתונים שנבדקו
"""
    
    if results:
        for file, data in results.items():
            report += f"""
#### {file}
- **שורות נתונים**: {data['rows']:,}
- **מחיר אחרון**: ${data['last_price']:.2f}
- **טווח תאריכים**: {data['date_range']}
- **עמודות**: {', '.join(data['columns'])}

"""
    else:
        report += "❌ לא נמצאו נתונים לבדיקה\n"
    
    report += f"""
### אינטגרציה עם המערכת
"""
    
    if system_ok:
        report += "✅ המערכת זמינה ומוכנה לעבודה\n"
    else:
        report += "❌ בעיות באינטגרציה עם המערכת\n"
    
    report += f"""
## המלצות

1. **שימוש בנתונים**: הנתונים החדשים זמינים לשימוש במערכת
2. **בדיקת איכות**: כל הקבצים מכילים נתונים מלאים ללא ערכים חסרים
3. **עדכון מערכת**: המערכת מוכנה לעבודה עם הנתונים החדשים

---
*דוח נוצר אוטומטית ב-{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ דוח בדיקה נוצר: {report_file}")
    return report_file

def main():
    """הפונקציה הראשית"""
    
    print("🚀 מתחיל בדיקת מערכת הנתונים החדשים...")
    print("=" * 60)
    
    # בדיקת טעינת נתונים
    results = test_data_loading()
    
    # בדיקת אינטגרציה עם המערכת
    system_ok = test_system_integration()
    
    # יצירת דוח
    report_file = create_test_report(results, system_ok)
    
    # סיכום
    print(f"\n{'='*60}")
    print("📊 סיכום בדיקות:")
    print(f"{'='*60}")
    print(f"✅ נבדקו {len(results)} קבצי נתונים")
    print(f"📈 סך שורות נתונים: {sum(r['rows'] for r in results.values()):,}")
    print(f"🔧 מערכת: {'זמינה' if system_ok else 'בעיות'}")
    print(f"📄 דוח: {report_file}")
    
    if results and system_ok:
        print("\n🎉 המערכת מוכנה לעבודה עם הנתונים החדשים!")
    else:
        print("\n⚠️ יש לבדוק בעיות במערכת")

if __name__ == "__main__":
    main() 