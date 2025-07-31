# Smart Data Manager - מדריך מקיף

## סקירה כללית

Smart Data Manager הוא מערכת מתקדמת לניהול נתונים פיננסיים שמשלבת נתונים מקומיים עם API חיצוניים. המערכת מיועדת לחסוך בשימוש במפתחות API ולשפר ביצועים על ידי אחסון חכם של נתונים היסטוריים.

## ארכיטקטורה

### רכיבים עיקריים

1. **SmartDataManager** - המחלקה הראשית לניהול נתונים
2. **UsageTracker** - מעקב אחר שימוש וביצועים
3. **מערכת מטמון** - זיכרון מטמון עם LRU
4. **דחיסה** - דחיסת נתונים עם gzip
5. **אינדקס** - אינדקס מהיר לקבצי נתונים

### מבנה תיקיות

```
data/
├── historical_prices/
│   └── daily/           # נתוני מחירים יומיים
├── technical_indicators/ # אינדיקטורים טכניים
├── news_sentiment/      # חדשות ורגשות
├── fundamentals/        # נתונים פונדמנטליים
├── metadata/           # מטא-דאטה ואינדקסים
└── cache/              # מטמון זמני
```

## זרימת עבודה

### 1. בדיקת נתונים מקומיים
המערכת בודקת תחילה אם יש נתונים מקומיים עבור המניה המבוקשת.

### 2. הערכת כמות נתונים
אם יש נתונים מקומיים, המערכת בודקת אם יש מספיק נתונים לתקופה המבוקשת.

### 3. השלמה מ-API
אם חסרים נתונים, המערכת משתמשת ב-API לפי סדר עדיפות:
1. **yfinance** (חינמי, ללא מפתח API)
2. **FMP** (Financial Modeling Prep)
3. **DataFetcher** (מקורות נוספים)

### 4. שילוב ואחסון
הנתונים החדשים משולבים עם הנתונים המקומיים ונשמרים אוטומטית.

## שימוש בסיסי

### שליפת נתוני מחירים

```python
from utils.smart_data_manager import smart_data_manager

# שליפת נתונים בסיסית
data = smart_data_manager.get_stock_data('AAPL', days=90)

# שליפת נתונים ללא השלמה מ-API
data = smart_data_manager.get_stock_data('AAPL', days=90, include_live=False)

# שליפת מספר מניות
symbols = ['AAPL', 'MSFT', 'GOOGL']
data_dict = smart_data_manager.get_multiple_stocks(symbols, days=60)
```

### שליפת נתונים מורחבים

```python
# אינדיקטורים טכניים
technical_data = smart_data_manager.get_technical_indicators('AAPL', 'all', days=90)

# חדשות ורגשות
news_data = smart_data_manager.get_news_sentiment('AAPL', days=30)

# נתונים פונדמנטליים
fundamentals = smart_data_manager.get_fundamentals('AAPL', 'income')

# נתונים מקיפים
comprehensive = smart_data_manager.get_comprehensive_data(
    'AAPL', 
    days=90,
    include_technical=True,
    include_news=True,
    include_fundamentals=True
)
```

## שימוש מתקדם

### עיבוד מרובה במקביל

```python
# עיבוד מספר מניות במקביל
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
results = smart_data_manager.batch_process(
    symbols, 
    days=90, 
    max_workers=4
)
```

### אופטימיזציה ואחזור

```python
# סטטיסטיקות ביצועים
performance = smart_data_manager.get_performance_stats()
print(f"Cache hit rate: {performance['cache_hit_rate']:.2%}")

# דוח שימוש
usage_report = smart_data_manager.usage_tracker.get_usage_report()
print(f"API calls: {usage_report['api_calls_summary']}")

# אופטימיזציה של אחסון
smart_data_manager.optimize_storage()

# ניקוי נתונים ישנים
smart_data_manager.cleanup_old_data(days_to_keep=365)
```

### הגדרות מותאמות אישית

```python
# יצירת מופע מותאם אישית
custom_manager = SmartDataManager(
    data_dir="custom_data",
    enable_compression=True,
    cache_size=200,
    enable_indexing=True
)
```

## תכונות מתקדמות

### 1. דחיסה אוטומטית
- דחיסת קבצים עם gzip
- חיסכון של עד 70% במרחב אחסון
- קריאה וכתיבה אוטומטית

### 2. מערכת מטמון חכמה
- LRU Cache עם גודל מותאם
- מעקב אחר פגיעות במטמון
- ניהול זיכרון אוטומטי

### 3. אינדקס מהיר
- אינדקס קבצים עם pickle
- חיפוש מהיר של נתונים
- עדכון אוטומטי

### 4. מעקב שימוש
- תיעוד כל בקשות הנתונים
- סטטיסטיקות API
- מעקב אחר שגיאות

### 5. תמיכה בסוגי נתונים שונים
- נתוני מחירים (OHLCV)
- אינדיקטורים טכניים (RSI, MACD, Bollinger Bands)
- חדשות ורגשות
- נתונים פונדמנטליים

## תחזוקה

### ניקוי נתונים

```python
# ניקוי נתונים ישנים
smart_data_manager.cleanup_old_data(days_to_keep=365)

# בנייה מחדש של אינדקס
smart_data_manager._rebuild_index()
```

### גיבוי ושחזור

```python
# שמירת מטא-דאטה
smart_data_manager._save_metadata()
smart_data_manager._save_index()

# טעינת מטא-דאטה
smart_data_manager._load_metadata()
smart_data_manager._load_index()
```

### מעקב אחר ביצועים

```python
# סטטיסטיקות מטמון
cache_stats = smart_data_manager.get_performance_stats()

# דוח שימוש מפורט
usage_report = smart_data_manager.usage_tracker.get_usage_report()

# ניתוח שגיאות
recent_errors = usage_report['recent_errors']
```

## הגדרות

### משתני סביבה

```bash
# הגדרת תיקיית נתונים
export SMART_DATA_DIR="/path/to/data"

# הגדרת גודל מטמון
export SMART_CACHE_SIZE=200

# הפעלת/כיבוי דחיסה
export SMART_COMPRESSION=true
```

### קובץ הגדרות

```yaml
# config/smart_data_config.yaml
data_directory: "data"
enable_compression: true
cache_size: 100
enable_indexing: true
max_workers: 4
days_to_keep: 365
```

## פתרון בעיות

### בעיות נפוצות

1. **שגיאת ייבוא yfinance**
   ```bash
   pip install yfinance
   ```

2. **שגיאת ייבוא TA-Lib**
   ```bash
   # Windows
   pip install TA-Lib
   
   # Linux/Mac
   conda install -c conda-forge ta-lib
   ```

3. **בעיות הרשאות קבצים**
   ```python
   # בדיקת הרשאות
   import os
   print(os.access("data", os.W_OK))
   ```

### לוגים ודיבוג

```python
import logging

# הגדרת רמת לוג
logging.basicConfig(level=logging.DEBUG)

# בדיקת לוגים
logger = logging.getLogger('utils.smart_data_manager')
```

## ביצועים

### מדדי ביצועים

- **זמן קריאה מקומי**: < 10ms
- **זמן קריאה מ-API**: 100-500ms
- **דחיסה**: חיסכון של 60-80% במרחב
- **מטמון**: שיפור של 90% בזמני קריאה חוזרים

### אופטימיזציות

1. **דחיסה**: הקטנת גודל קבצים
2. **מטמון**: זיכרון מטמון מהיר
3. **אינדקס**: חיפוש מהיר
4. **עיבוד מקביל**: שיפור ביצועים

## פיתוח עתידי

### תכונות מתוכננות

1. **מסד נתונים**: SQLite/PostgreSQL
2. **API REST**: ממשק HTTP
3. **ענן**: תמיכה ב-S3/Azure
4. **מכונה לומדת**: חיזוי צרכים
5. **גרפים**: ממשק ויזואלי

### תרומה

```bash
# פיצול repository
git checkout -b feature/new-feature

# בדיקות
python -m pytest tests/test_smart_data_manager.py

# תיעוד
python -m pydoc utils.smart_data_manager
```

## תמיכה

### משאבים

- [תיעוד API](docs/api.md)
- [דוגמאות קוד](examples/)
- [בדיקות](tests/)
- [דוחות ביצועים](reports/)

### קשר

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: GitHub Wiki

---

*Smart Data Manager - ניהול נתונים חכם למסחר אלגוריתמי* 