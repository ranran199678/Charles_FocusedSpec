# TO-DO: תיקיית Utils

## תקציר מטרת התיקייה
תיקיית `utils/` מכילה קבצי עזר ופונקציות שימושיות המשותפות לכל המערכת. הקבצים כאן מספקים פונקציונליות בסיסית כמו ניהול הרשאות, קבועים, לוגים ופונקציות עזר כלליות.

## טבלת קבצים ↔ תפקיד ↔ תלות עיקרית

| קובץ | תפקיד | תלות עיקרית |
|------|-------|-------------|
| `__init__.py` | הגדרת חבילה | - |
| `constants.py` | קבועים גלובליים | - |
| `credentials.py` | ניהול הרשאות ו-API keys | `config/config.yaml` |
| `data_fetcher.py` | הורדת נתונים מ-APIs | `requests`, `pandas` |
| `file_utils.py` | פונקציות עזר לקבצים | `os`, `shutil` |
| `logger.py` | מערכת לוגים | `logging` |
| `validators.py` | אימות נתונים | `pandas`, `numpy` |

## דוגמאות שימוש / פקודות הפעלה

```python
# שימוש בקבועים
from utils.constants import DEFAULT_TIMEFRAME, SUPPORTED_SYMBOLS

# ניהול הרשאות
from utils.credentials import get_api_key
api_key = get_api_key('yahoo_finance')

# לוגים
from utils.logger import setup_logger
logger = setup_logger('my_module')
logger.info('התחלת עיבוד נתונים')

# אימות נתונים
from utils.validators import validate_stock_data
is_valid = validate_stock_data(df)
```

## רשימת משימות מדורגת

### 🔴 Highest Priority

#### 1. שיפור מערכת ההרשאות (2-3 שעות)
- **תיאור**: הוספת תמיכה ב-API keys מרובים ורוטציה
- **קבצים**: `credentials.py`
- **תלות**: `config/config.yaml`
- **סטטוס**: ⏳ ממתין

#### 2. הוספת אימות נתונים מקיף (3-4 שעות)
- **תיאור**: יצירת מערכת אימות חזקה לנתוני מניות
- **קבצים**: `validators.py` (חדש)
- **תלות**: `pandas`, `numpy`
- **סטטוס**: ❌ לא התחיל

#### 3. שיפור מערכת הלוגים (2 שעות)
- **תיאור**: הוספת רמות לוג שונות וניהול קבצי לוג
- **קבצים**: `logger.py`
- **תלות**: `logging`
- **סטטוס**: ⏳ ממתין

### 🟡 Important

#### 4. הוספת פונקציות עזר לקבצים (2 שעות)
- **תיאור**: פונקציות לניהול קבצים, גיבוי ומחיקה
- **קבצים**: `file_utils.py` (חדש)
- **תלות**: `os`, `shutil`
- **סטטוס**: ❌ לא התחיל

#### 5. הרחבת קבועים (1 שעה)
- **תיאור**: הוספת קבועים נוספים למערכת
- **קבצים**: `constants.py`
- **תלות**: -
- **סטטוס**: ⏳ ממתין

#### 6. שיפור data_fetcher (3 שעות)
- **תיאור**: הוספת retry logic ו-error handling
- **קבצים**: `data_fetcher.py`
- **תלות**: `requests`, `pandas`
- **סטטוס**: ⏳ ממתין

### 🟢 Nice to Have

#### 7. הוספת cache manager (4 שעות)
- **תיאור**: מערכת cache לנתונים שהורדו
- **קבצים**: `cache_manager.py` (חדש)
- **תלות**: `pickle`, `os`
- **סטטוס**: ❌ לא התחיל

#### 8. הוספת performance profiler (3 שעות)
- **תיאור**: מדידת ביצועים של פונקציות
- **קבצים**: `profiler.py` (חדש)
- **תלות**: `time`, `functools`
- **סטטוס**: ❌ לא התחיל

#### 9. הוספת configuration validator (2 שעות)
- **תיאור**: אימות קבצי config
- **קבצים**: `config_validator.py` (חדש)
- **תלות**: `yaml`
- **סטטוס**: ❌ לא התחיל

## תלות בין משימות

```
1. שיפור מערכת ההרשאות
   ↓
2. הוספת אימות נתונים מקיף
   ↓
3. שיפור מערכת הלוגים
   ↓
4. הוספת פונקציות עזר לקבצים
   ↓
5. הרחבת קבועים
   ↓
6. שיפור data_fetcher
   ↓
7. הוספת cache manager
   ↓
8. הוספת performance profiler
   ↓
9. הוספת configuration validator
```

## הערות נוספות

- **זמן כולל משוער**: 22 שעות
- **עדיפות ראשונה**: מערכת ההרשאות והאימות
- **תלות חיצונית**: רוב המשימות תלויות בקבצי config קיימים
- **בדיקות נדרשות**: כל פונקציה חדשה צריכה unit tests