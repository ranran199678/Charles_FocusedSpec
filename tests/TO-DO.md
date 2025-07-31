# TO-DO: תיקיית Tests

## תקציר מטרת התיקייה
תיקיית `tests/` מכילה את כל הבדיקות של המערכת - unit tests, integration tests, performance tests ו-end-to-end tests. הבדיקות מבטיחות שהמערכת עובדת כראוי ושינויים לא שוברים פונקציונליות קיימת.

## טבלת קבצים ↔ תפקיד ↔ תלות עיקרית

| קובץ | תפקיד | תלות עיקרית |
|------|-------|-------------|
| `__init__.py` | הגדרת חבילה | - |
| `test_adx_score_agent.py` | בדיקות ADX Score Agent | `core/adx_score_agent.py` |
| `test_alpha_score_engine.py` | בדיקות Alpha Score Engine | `core/alpha_score_engine.py` |
| `test_advanced_pattern_analyzer.py` | בדיקות Pattern Analyzer | `core/advanced_pattern_analyzer.py` |
| `test_data_processor.py` | בדיקות עיבוד נתונים | `scripts/` |
| `test_utils.py` | בדיקות פונקציות עזר | `utils/` |
| `test_integration.py` | בדיקות אינטגרציה | כל המערכת |
| `test_performance.py` | בדיקות ביצועים | `pytest-benchmark` |

## דוגמאות שימוש / פקודות הפעלה

```bash
# הרצת כל הבדיקות
python -m pytest tests/

# הרצת בדיקות ספציפיות
python -m pytest tests/test_adx_score_agent.py

# הרצה עם coverage
python -m pytest tests/ --cov=core --cov=data --cov=utils

# הרצת בדיקות ביצועים
python -m pytest tests/test_performance.py --benchmark-only

# הרצת בדיקות אינטגרציה
python -m pytest tests/test_integration.py -v
```

## רשימת משימות מדורגת

### 🔴 Highest Priority

#### 1. יצירת בדיקות בסיסיות חסרות (6-8 שעות)
- **תיאור**: יצירת unit tests לכל הסוכנים והמודולים
- **קבצים**: `test_*.py` (חדשים)
- **תלות**: `pytest`, `unittest.mock`
- **סטטוס**: ❌ לא התחיל

#### 2. יצירת בדיקות אינטגרציה (4-5 שעות)
- **תיאור**: בדיקות end-to-end של כל pipeline
- **קבצים**: `test_integration.py` (חדש)
- **תלות**: כל המערכת
- **סטטוס**: ❌ לא התחיל

#### 3. יצירת בדיקות נתונים (3-4 שעות)
- **תיאור**: בדיקות עיבוד נתונים ואינדיקטורים
- **קבצים**: `test_data_processor.py` (חדש)
- **תלות**: `scripts/`
- **סטטוס**: ❌ לא התחיל

### 🟡 Important

#### 4. הוספת בדיקות ביצועים (3 שעות)
- **תיאור**: מדידת זמן ריצה וזיכרון
- **קבצים**: `test_performance.py` (חדש)
- **תלות**: `pytest-benchmark`
- **סטטוס**: ❌ לא התחיל

#### 5. יצירת בדיקות error handling (2-3 שעות)
- **תיאור**: בדיקות טיפול בשגיאות
- **קבצים**: `test_error_handling.py` (חדש)
- **תלות**: כל המערכת
- **סטטוס**: ❌ לא התחיל

#### 6. הוספת בדיקות edge cases (3 שעות)
- **תיאור**: בדיקות מקרים קיצוניים
- **קבצים**: `test_edge_cases.py` (חדש)
- **תלות**: כל המערכת
- **סטטוס**: ❌ לא התחיל

#### 7. יצירת בדיקות regression (2 שעות)
- **תיאור**: בדיקות שמונעות regressions
- **קבצים**: `test_regression.py` (חדש)
- **תלות**: כל המערכת
- **סטטוס**: ❌ לא התחיל

### 🟢 Nice to Have

#### 8. הוספת בדיקות stress (3 שעות)
- **תיאור**: בדיקות עומס על המערכת
- **קבצים**: `test_stress.py` (חדש)
- **תלות**: `pytest-xdist`
- **סטטוס**: ❌ לא התחיל

#### 9. יצירת בדיקות security (2 שעות)
- **תיאור**: בדיקות אבטחה בסיסיות
- **קבצים**: `test_security.py` (חדש)
- **תלות**: `bandit`
- **סטטוס**: ❌ לא התחיל

#### 10. הוספת בדיקות API (3 שעות)
- **תיאור**: בדיקות ממשקי API
- **קבצים**: `test_api.py` (חדש)
- **תלות**: `requests-mock`
- **סטטוס**: ❌ לא התחיל

#### 11. יצירת בדיקות database (2 שעות)
- **תיאור**: בדיקות מסד נתונים
- **קבצים**: `test_database.py` (חדש)
- **תלות**: `sqlite3`
- **סטטוס**: ❌ לא התחיל

## תלות בין משימות

```
1. יצירת בדיקות בסיסיות חסרות
   ↓
2. יצירת בדיקות אינטגרציה
   ↓
3. יצירת בדיקות נתונים
   ↓
4. הוספת בדיקות ביצועים
   ↓
5. יצירת בדיקות error handling
   ↓
6. הוספת בדיקות edge cases
   ↓
7. יצירת בדיקות regression
   ↓
8. הוספת בדיקות stress
   ↓
9. יצירת בדיקות security
   ↓
10. הוספת בדיקות API
    ↓
11. יצירת בדיקות database
```

## קבצי בדיקה נדרשים

### Unit Tests:
- `test_adx_score_agent.py` ✅ קיים
- `test_alpha_score_engine.py` ✅ קיים
- `test_advanced_pattern_analyzer.py` ❌ חסר
- `test_data_manager.py` ❌ חסר
- `test_enhanced_data_processor.py` ❌ חסר
- `test_advanced_indicators_processor.py` ❌ חסר
- `test_credentials.py` ❌ חסר
- `test_constants.py` ❌ חסר
- `test_logger.py` ❌ חסר

### Integration Tests:
- `test_full_pipeline.py` ❌ חסר
- `test_data_flow.py` ❌ חסר
- `test_agent_interaction.py` ❌ חסר

### Performance Tests:
- `test_processing_speed.py` ❌ חסר
- `test_memory_usage.py` ❌ חסר
- `test_concurrent_processing.py` ❌ חסר

## קריטריוני הצלחה

### Coverage:
- **Unit Tests**: לפחות 80% coverage
- **Integration Tests**: 100% של pipelines עיקריים
- **Performance Tests**: זמני ריצה מתחת לסף שנקבע

### איכות:
- כל בדיקה צריכה להיות deterministic
- בדיקות צריכות להיות מהירות (< 1 שנייה ליחידה)
- בדיקות צריכות להיות מבודדות

### תחזוקה:
- בדיקות צריכות להיות קלות להבנה
- בדיקות צריכות להיות קלות לתחזוקה
- בדיקות צריכות להיות קלות להרחבה

## הערות נוספות

- **זמן כולל משוער**: 35 שעות
- **עדיפות ראשונה**: בדיקות בסיסיות ובדיקות אינטגרציה
- **תלות חיצונית**: רוב הבדיקות תלויות במודולים קיימים
- **כלים נדרשים**: `pytest`, `pytest-cov`, `pytest-benchmark`
- **CI/CD**: בדיקות צריכות לרוץ אוטומטית ב-CI