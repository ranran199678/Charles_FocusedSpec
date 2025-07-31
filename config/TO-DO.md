# TO-DO: תיקיית Config

## תקציר מטרת התיקייה
תיקיית `config/` מכילה את כל קבצי התצורה של המערכת. היא כוללת הגדרות API, פרמטרים לסוכנים, הגדרות מסד נתונים וקבצי תצורה נוספים הנדרשים לפעולת המערכת.

## טבלת קבצים ↔ תפקיד ↔ תלות עיקרית

| קובץ | תפקיד | תלות עיקרית |
|------|-------|-------------|
| `config.yaml` | הגדרות ראשיות | `yaml` |
| `gap_config.yaml` | הגדרות GAP analysis | `yaml` |
| `api_keys.yaml` | מפתחות API | `yaml` |
| `database_config.yaml` | הגדרות מסד נתונים | `yaml` |
| `logging_config.yaml` | הגדרות לוגים | `yaml` |
| `agents_config.yaml` | הגדרות סוכנים | `yaml` |

## דוגמאות שימוש / פקודות הפעלה

```python
# קריאת הגדרות
import yaml
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# שימוש בהגדרות
api_key = config['api_keys']['yahoo_finance']
timeframe = config['defaults']['timeframe']

# עדכון הגדרות
config['new_setting'] = 'value'
with open('config/config.yaml', 'w') as f:
    yaml.dump(config, f)
```

## רשימת משימות מדורגת

### 🔴 Highest Priority

#### 1. יצירת config validator (2-3 שעות)
- **תיאור**: אימות תקינות קבצי תצורה
- **קבצים**: `config_validator.py` (חדש)
- **תלות**: `yaml`, `jsonschema`
- **סטטוס**: ❌ לא התחיל

#### 2. הוספת environment variables support (2 שעות)
- **תיאור**: תמיכה במשתני סביבה
- **קבצים**: `config.yaml` (שיפור)
- **תלות**: `os.environ`
- **סטטוס**: ❌ לא התחיל

#### 3. יצירת config manager (3 שעות)
- **תיאור**: ניהול מרכזי של תצורות
- **קבצים**: `config_manager.py` (חדש)
- **תלות**: `yaml`, `pathlib`
- **סטטוס**: ❌ לא התחיל

### 🟡 Important

#### 4. הוספת config templates (2 שעות)
- **תיאור**: תבניות תצורה לפריסה מהירה
- **קבצים**: `templates/` (חדש)
- **תלות**: `jinja2`
- **סטטוס**: ❌ לא התחיל

#### 5. יצירת config migration system (3 שעות)
- **תיאור**: מערכת עדכון תצורות בין גרסאות
- **קבצים**: `migration/` (חדש)
- **תלות**: `yaml`, `semver`
- **סטטוס**: ❌ לא התחיל

#### 6. הוספת config encryption (2 שעות)
- **תיאור**: הצפנת מפתחות API רגישים
- **קבצים**: `encryption.py` (חדש)
- **תלות**: `cryptography`
- **סטטוס**: ❌ לא התחיל

#### 7. יצירת config documentation (2 שעות)
- **תיאור**: תיעוד מפורט של כל הגדרה
- **קבצים**: `README.md` (חדש)
- **תלות**: -
- **סטטוס**: ❌ לא התחיל

### 🟢 Nice to Have

#### 8. הוספת config UI (4 שעות)
- **תיאור**: ממשק גרפי לעריכת תצורות
- **קבצים**: `config_ui.py` (חדש)
- **תלות**: `tkinter`, `customtkinter`
- **סטטוס**: ❌ לא התחיל

#### 9. יצירת config backup system (2 שעות)
- **תיאור**: גיבוי אוטומטי של תצורות
- **קבצים**: `backup.py` (חדש)
- **תלות**: `shutil`, `datetime`
- **סטטוס**: ❌ לא התחיל

#### 10. הוספת config versioning (2 שעות)
- **תיאור**: מעקב אחר שינויים בתצורות
- **קבצים**: `versioning.py` (חדש)
- **תלות**: `git`, `datetime`
- **סטטוס**: ❌ לא התחיל

#### 11. יצירת config testing framework (3 שעות)
- **תיאור**: בדיקות אוטומטיות לתצורות
- **קבצים**: `test_config.py` (חדש)
- **תלות**: `pytest`
- **סטטוס**: ❌ לא התחיל

## תלות בין משימות

```
1. יצירת config validator
   ↓
2. הוספת environment variables support
   ↓
3. יצירת config manager
   ↓
4. הוספת config templates
   ↓
5. יצירת config migration system
   ↓
6. הוספת config encryption
   ↓
7. יצירת config documentation
   ↓
8. הוספת config UI
   ↓
9. יצירת config backup system
   ↓
10. הוספת config versioning
    ↓
11. יצירת config testing framework
```

## קבצים נדרשים

### קיימים:
- `config.yaml` ✅ קיים
- `gap_config.yaml` ✅ קיים

### חסרים:
- `api_keys.yaml` ❌ חסר
- `database_config.yaml` ❌ חסר
- `logging_config.yaml` ❌ חסר
- `agents_config.yaml` ❌ חסר
- `config_validator.py` ❌ חסר
- `config_manager.py` ❌ חסר
- `templates/` ❌ חסר
- `migration/` ❌ חסר
- `encryption.py` ❌ חסר
- `README.md` ❌ חסר

## מבנה תצורה מומלץ

### config.yaml:
```yaml
# הגדרות כלליות
app:
  name: "Charles Focused Spec"
  version: "1.0.0"
  debug: false

# הגדרות API
api:
  yahoo_finance:
    base_url: "https://query1.finance.yahoo.com"
    timeout: 30
  alpha_vantage:
    base_url: "https://www.alphavantage.co"
    timeout: 30

# הגדרות ברירת מחדל
defaults:
  timeframe: "daily"
  symbols: ["AAPL", "MSFT", "GOOGL"]
  start_date: "2020-01-01"

# הגדרות עיבוד נתונים
data_processing:
  batch_size: 1000
  max_workers: 4
  cache_enabled: true
```

### api_keys.yaml:
```yaml
# מפתחות API (מוצפנים)
yahoo_finance:
  api_key: "encrypted_key_here"
alpha_vantage:
  api_key: "encrypted_key_here"
```

## קריטריוני הצלחה

### אבטחה:
- מפתחות API מוצפנים
- הרשאות קבצים מתאימות
- לוגים ללא מידע רגיש

### גמישות:
- תמיכה במשתני סביבה
- תבניות לפריסה מהירה
- מערכת עדכון אוטומטית

### נוחות שימוש:
- תיעוד ברור
- ממשק עריכה נוח
- אימות אוטומטי

## הערות נוספות

- **זמן כולל משוער**: 27 שעות
- **עדיפות ראשונה**: אימות תצורות ואבטחה
- **תלות חיצונית**: רוב המשימות עצמאיות
- **בדיקות נדרשות**: כל validator חדש צריך unit tests
- **תיעוד נדרש**: תיעוד מפורט של כל הגדרה