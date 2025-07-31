# TO-DO: תיקיית Data

## תקציר מטרת התיקייה
תיקיית `data/` היא הלב של מערכת הנתונים. היא מכילה את כל הנתונים הגולמיים, המעובדים, האינדיקטורים הטכניים ומסד הנתונים. התיקייה מאורגנת בצורה היררכית עם תתי-תיקיות לקטגוריות שונות של נתונים.

## טבלת קבצים ↔ תפקיד ↔ תלות עיקרית

| קובץ/תיקייה | תפקיד | תלות עיקרית |
|-------------|-------|-------------|
| `code/` | סקריפטים לעיבוד נתונים | `pandas`, `numpy`, `sqlite3` |
| `database/` | מסד נתונים SQLite | `sqlite3` |
| `historical_prices/` | נתוני מחירים היסטוריים | `pandas` |
| `market_data/` | נתוני שוק כלכליים | `requests` |
| `metadata/` | מטא-דאטה של קבצים | `json` |
| `news_sentiment/` | נתוני חדשות ורגשות | `nltk`, `textblob` |
| `raw_price_data/` | נתונים גולמיים מ-Yahoo Finance | `yfinance` |
| `technical_indicators/` | אינדיקטורים טכניים | `pandas`, `numpy` |

## דוגמאות שימוש / פקודות הפעלה

```python
# הורדת נתונים חדשים
python scripts/yfinance_CSV.PY

# עיבוד נתונים גולמיים
python scripts/enhanced_data_processor.py

# חישוב אינדיקטורים טכניים
python scripts/advanced_indicators_processor.py

# בדיקת מסד נתונים
import sqlite3
conn = sqlite3.connect('data/database/historical.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM historical_prices LIMIT 5")
```

## רשימת משימות מדורגת

### 🔴 Highest Priority

#### 1. תיקון בעיות עיבוד נתונים (4-5 שעות)
- **תיאור**: פתרון בעיות בקבצים ריקים ופורמט נתונים
- **קבצים**: `code/enhanced_data_processor.py`, `code/advanced_indicators_processor.py`
- **תלות**: `pandas`, `numpy`
- **סטטוס**: 🔄 בתהליך

#### 2. יצירת מערכת backup אוטומטית (3 שעות)
- **תיאור**: גיבוי אוטומטי של נתונים ומסד נתונים
- **קבצים**: `code/backup_manager.py` (חדש)
- **תלות**: `shutil`, `sqlite3`
- **סטטוס**: ❌ לא התחיל

#### 3. שיפור ניהול מטא-דאטה (2 שעות)
- **תיאור**: מערכת מטא-דאטה מתקדמת עם versioning
- **קבצים**: `metadata/metadata_manager.py` (חדש)
- **תלות**: `json`, `datetime`
- **סטטוס**: ❌ לא התחיל

### 🟡 Important

#### 4. הוספת data validation pipeline (4 שעות)
- **תיאור**: אימות אוטומטי של איכות נתונים
- **קבצים**: `code/data_validator.py` (חדש)
- **תלות**: `pandas`, `numpy`
- **סטטוס**: ❌ לא התחיל

#### 5. יצירת data migration scripts (3 שעות)
- **תיאור**: סקריפטים להעברת נתונים בין גרסאות
- **קבצים**: `code/migration_scripts/` (חדש)
- **תלות**: `sqlite3`, `pandas`
- **סטטוס**: ❌ לא התחיל

#### 6. הוספת real-time data streaming (6 שעות)
- **תיאור**: קבלת נתונים בזמן אמת
- **קבצים**: `code/streaming_data.py` (חדש)
- **תלות**: `websockets`, `asyncio`
- **סטטוס**: ❌ לא התחיל

#### 7. שיפור performance של עיבוד נתונים (4 שעות)
- **תיאור**: אופטימיזציה של חישובי אינדיקטורים
- **קבצים**: `code/enhanced_data_processor.py`
- **תלות**: `pandas`, `numpy`
- **סטטוס**: ⏳ ממתין

### 🟢 Nice to Have

#### 8. הוספת data compression (3 שעות)
- **תיאור**: דחיסת קבצי CSV גדולים
- **קבצים**: `code/compression_utils.py` (חדש)
- **תלות**: `gzip`, `pickle`
- **סטטוס**: ❌ לא התחיל

#### 9. יצירת data visualization tools (5 שעות)
- **תיאור**: כלים להצגת נתונים וגרפים
- **קבצים**: `code/visualization/` (חדש)
- **תלות**: `matplotlib`, `plotly`
- **סטטוס**: ❌ לא התחיל

#### 10. הוספת data export formats (2 שעות)
- **תיאור**: ייצוא ל-Excel, JSON, Parquet
- **קבצים**: `code/export_utils.py` (חדש)
- **תלות**: `openpyxl`, `pyarrow`
- **סטטוס**: ❌ לא התחיל

#### 11. יצירת data quality dashboard (4 שעות)
- **תיאור**: דשבורד לניטור איכות נתונים
- **קבצים**: `code/quality_dashboard.py` (חדש)
- **תלות**: `streamlit`, `plotly`
- **סטטוס**: ❌ לא התחיל

## תלות בין משימות

```
1. תיקון בעיות עיבוד נתונים
   ↓
2. יצירת מערכת backup אוטומטית
   ↓
3. שיפור ניהול מטא-דאטה
   ↓
4. הוספת data validation pipeline
   ↓
5. יצירת data migration scripts
   ↓
6. הוספת real-time data streaming
   ↓
7. שיפור performance של עיבוד נתונים
   ↓
8. הוספת data compression
   ↓
9. יצירת data visualization tools
   ↓
10. הוספת data export formats
    ↓
11. יצירת data quality dashboard
```

## קבצים לבדיקה למחיקה

### קבצים כפולים/מיותרים:
- `data/historical_prices/daily/` - קבצי QBTS כפולים
- `data/raw_price_data/` - קבצים ישנים עם פורמט שונה
- קבצי CSV ריקים או פגומים

### קבצים זמניים:
- קבצי `.tmp` או `.temp`
- קבצי backup ישנים
- קבצי log גדולים

## הערות נוספות

- **זמן כולל משוער**: 41 שעות
- **עדיפות ראשונה**: תיקון בעיות עיבוד נתונים קיימות
- **תלות חיצונית**: רוב המשימות תלויות בקבצי code קיימים
- **בדיקות נדרשות**: כל pipeline חדש צריך integration tests
- **גיבוי נדרש**: לפני כל שינוי משמעותי במבנה הנתונים