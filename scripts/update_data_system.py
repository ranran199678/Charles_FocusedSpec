import os
import shutil
import pandas as pd
from datetime import datetime

def move_csv_files_to_data_directory():
    """העברת קבצי CSV החדשים לתיקיית הנתונים"""
    
    # תיקיית הנתונים
    data_dir = "data/historical_prices/daily"
    
    # יצירת התיקייה אם לא קיימת
    os.makedirs(data_dir, exist_ok=True)
    
    # רשימת קבצי CSV שנוצרו
    csv_files = [
        "AAPL Stock Price History.csv",
        "MSFT Stock Price History.csv", 
        "GOOGL Stock Price History.csv",
        "AMZN Stock Price History.csv",
        "TSLA Stock Price History.csv"
    ]
    
    moved_files = []
    
    for file in csv_files:
        if os.path.exists(file):
            # שם קובץ חדש (בפורמט של המערכת)
            new_name = file.replace(" Stock Price History.csv", ".csv")
            new_path = os.path.join(data_dir, new_name)
            
            try:
                # העתקת הקובץ
                shutil.copy2(file, new_path)
                print(f"✅ הועבר: {file} -> {new_path}")
                moved_files.append(new_name)
                
                # מחיקת הקובץ המקורי
                os.remove(file)
                print(f"🗑️ נמחק הקובץ המקורי: {file}")
                
            except Exception as e:
                print(f"❌ שגיאה בהעברת {file}: {str(e)}")
        else:
            print(f"⚠️ הקובץ לא נמצא: {file}")
    
    return moved_files

def update_metadata():
    """עדכון מטא-דאטה של הנתונים"""
    
    metadata_file = "data/metadata/processed_files.json"
    
    # יצירת תיקיית מטא-דאטה אם לא קיימת
    os.makedirs("data/metadata", exist_ok=True)
    
    # קריאת מטא-דאטה קיים או יצירת חדש
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # עדכון מטא-דאטה
    current_time = datetime.now().isoformat()
    
    new_files = [
        "AAPL.csv", "MSFT.csv", "GOOGL.csv", "AMZN.csv", "TSLA.csv"
    ]
    
    for file in new_files:
        file_path = f"data/historical_prices/daily/{file}"
        if os.path.exists(file_path):
            # קריאת הקובץ לקבלת מידע
            df = pd.read_csv(file_path)
            
            metadata[file] = {
                "upload_date": current_time,
                "rows": len(df),
                "date_range": {
                    "start": df['Date'].iloc[0],
                    "end": df['Date'].iloc[-1]
                },
                "columns": list(df.columns),
                "source": "Yahoo Finance API",
                "format": "CSV"
            }
    
    # שמירת מטא-דאטה
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ מטא-דאטה עודכן: {metadata_file}")

def create_data_summary():
    """יצירת סיכום נתונים"""
    
    summary_file = "DATA_SOURCES_STATUS.md"
    
    data_dir = "data/historical_prices/daily"
    
    if not os.path.exists(data_dir):
        print("❌ תיקיית הנתונים לא קיימת")
        return
    
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    summary = f"""# סטטוס מקורות נתונים - מעודכן {datetime.now().strftime('%Y-%m-%d %H:%M')}

## קבצי נתונים זמינים

"""
    
    for file in sorted(files):
        file_path = os.path.join(data_dir, file)
        try:
            df = pd.read_csv(file_path)
            summary += f"""### {file}
- **שורות נתונים**: {len(df):,}
- **טווח תאריכים**: {df['Date'].iloc[0]} עד {df['Date'].iloc[-1]}
- **עמודות**: {', '.join(df.columns)}
- **גודל קובץ**: {os.path.getsize(file_path) / 1024:.1f} KB

"""
        except Exception as e:
            summary += f"""### {file}
- **שגיאה בקריאה**: {str(e)}

"""
    
    # כתיבת הסיכום
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✅ סיכום נתונים נוצר: {summary_file}")

def main():
    """הפונקציה הראשית"""
    
    print("🚀 מתחיל עדכון מערכת הנתונים...")
    print("=" * 50)
    
    # העברת קבצים
    moved_files = move_csv_files_to_data_directory()
    
    if moved_files:
        print(f"\n✅ הועברו {len(moved_files)} קבצים")
        
        # עדכון מטא-דאטה
        update_metadata()
        
        # יצירת סיכום
        create_data_summary()
        
        print(f"\n🎉 עדכון המערכת הושלם בהצלחה!")
        print(f"📊 קבצים זמינים: {', '.join(moved_files)}")
    else:
        print("❌ לא הועברו קבצים")

if __name__ == "__main__":
    import json
    main() 