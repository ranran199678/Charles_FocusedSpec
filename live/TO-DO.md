# TO-DO: תיקיית Live

## תקציר מטרת התיקייה
תיקיית `live/` מכילה את כל הכלים להרצת המערכת בזמן אמת. היא כוללת הרצת סוכנים בודדים, הרצה מרובת סוכנים, ניהול תוצאות וניטור ביצועים בזמן אמת.

## טבלת קבצים ↔ תפקיד ↔ תלות עיקרית

| קובץ | תפקיד | תלות עיקרית |
|------|-------|-------------|
| `__init__.py` | הגדרת חבילה | - |
| `agent_runner.py` | הרצת סוכן בודד | `core/` |
| `multi_agent_runner.py` | הרצה מרובת סוכנים | `core/`, `asyncio` |
| `outputs/` | תוצאות הרצות | `json`, `csv` |
| `monitoring.py` | ניטור ביצועים | `psutil`, `logging` |
| `scheduler.py` | תזמון הרצות | `schedule`, `datetime` |

## דוגמאות שימוש / פקודות הפעלה

```python
# הרצת סוכן בודד
python live/agent_runner.py --agent adx_score --symbol AAPL

# הרצה מרובת סוכנים
python live/multi_agent_runner.py --symbols AAPL,MSFT,GOOGL

# ניטור ביצועים
python live/monitoring.py --watch

# תזמון הרצות
python live/scheduler.py --schedule daily --time 09:00
```

## רשימת משימות מדורגת

### 🔴 Highest Priority

#### 1. יצירת agent_runner מתקדם (4-5 שעות)
- **תיאור**: מערכת הרצה מתקדמת עם error handling ו-logging
- **קבצים**: `agent_runner.py` (שיפור)
- **תלות**: `core/`, `utils/`
- **סטטוס**: ⏳ ממתין

#### 2. יצירת multi_agent_runner (5-6 שעות)
- **תיאור**: הרצה מקבילה של מספר סוכנים
- **קבצים**: `multi_agent_runner.py` (חדש)
- **תלות**: `asyncio`, `concurrent.futures`
- **סטטוס**: ❌ לא התחיל

#### 3. יצירת מערכת ניטור (3-4 שעות)
- **תיאור**: ניטור ביצועים וזיכרון בזמן אמת
- **קבצים**: `monitoring.py` (חדש)
- **תלות**: `psutil`, `matplotlib`
- **סטטוס**: ❌ לא התחיל

### 🟡 Important

#### 4. יצירת scheduler (3 שעות)
- **תיאור**: תזמון הרצות אוטומטי
- **קבצים**: `scheduler.py` (חדש)
- **תלות**: `schedule`, `cron`
- **סטטוס**: ❌ לא התחיל

#### 5. שיפור ניהול תוצאות (2-3 שעות)
- **תיאור**: ארגון ושימור תוצאות הרצות
- **קבצים**: `outputs/` (שיפור)
- **תלות**: `json`, `csv`, `sqlite3`
- **סטטוס**: ⏳ ממתין

#### 6. הוספת real-time alerts (3 שעות)
- **תיאור**: התראות בזמן אמת על אירועים חשובים
- **קבצים**: `alerts.py` (חדש)
- **תלות**: `smtplib`, `slack_sdk`
- **סטטוס**: ❌ לא התחיל

#### 7. יצירת dashboard בזמן אמת (4-5 שעות)
- **תיאור**: דשבורד להצגת תוצאות בזמן אמת
- **קבצים**: `dashboard.py` (חדש)
- **תלות**: `streamlit`, `plotly`
- **סטטוס**: ❌ לא התחיל

### 🟢 Nice to Have

#### 8. הוספת load balancing (4 שעות)
- **תיאור**: איזון עומס בין מספר תהליכים
- **קבצים**: `load_balancer.py` (חדש)
- **תלות**: `multiprocessing`
- **סטטוס**: ❌ לא התחיל

#### 9. יצירת backup אוטומטי (2 שעות)
- **תיאור**: גיבוי אוטומטי של תוצאות
- **קבצים**: `backup_manager.py` (חדש)
- **תלות**: `shutil`, `zipfile`
- **סטטוס**: ❌ לא התחיל

#### 10. הוספת API endpoints (5 שעות)
- **תיאור**: REST API להרצת סוכנים
- **קבצים**: `api_server.py` (חדש)
- **תלות**: `fastapi`, `uvicorn`
- **סטטוס**: ❌ לא התחיל

#### 11. יצירת CLI מתקדם (3 שעות)
- **תיאור**: ממשק שורת פקודה מתקדם
- **קבצים**: `cli.py` (חדש)
- **תלות**: `click`, `rich`
- **סטטוס**: ❌ לא התחיל

## תלות בין משימות

```
1. יצירת agent_runner מתקדם
   ↓
2. יצירת multi_agent_runner
   ↓
3. יצירת מערכת ניטור
   ↓
4. יצירת scheduler
   ↓
5. שיפור ניהול תוצאות
   ↓
6. הוספת real-time alerts
   ↓
7. יצירת dashboard בזמן אמת
   ↓
8. הוספת load balancing
   ↓
9. יצירת backup אוטומטי
   ↓
10. הוספת API endpoints
    ↓
11. יצירת CLI מתקדם
```

## קבצים נדרשים

### קיימים:
- `agent_runner.py` ✅ קיים
- `multi_agent_runner.py` ✅ קיים
- `outputs/` ✅ קיים

### חסרים:
- `monitoring.py` ❌ חסר
- `scheduler.py` ❌ חסר
- `alerts.py` ❌ חסר
- `dashboard.py` ❌ חסר
- `load_balancer.py` ❌ חסר
- `backup_manager.py` ❌ חסר
- `api_server.py` ❌ חסר
- `cli.py` ❌ חסר

## קריטריוני הצלחה

### ביצועים:
- הרצה של סוכן בודד: פחות מ-30 שניות
- הרצה מרובת סוכנים: פחות מ-2 דקות ל-10 מניות
- זיכרון מקסימלי: פחות מ-1GB

### אמינות:
- 99% uptime
- error recovery אוטומטי
- logging מלא של כל פעולה

### נוחות שימוש:
- CLI אינטואיטיבי
- דשבורד ברור ונגיש
- התראות בזמן אמת

## הערות נוספות

- **זמן כולל משוער**: 38 שעות
- **עדיפות ראשונה**: מערכת הרצה יציבה וניטור
- **תלות חיצונית**: רוב המשימות תלויות במודולי core
- **בדיקות נדרשות**: כל רכיב חדש צריך integration tests
- **תיעוד נדרש**: API documentation לכל endpoint חדש