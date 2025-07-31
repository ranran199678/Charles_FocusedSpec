# Tests - בדיקות מערכת

## 🎯 מטרת התיקייה

תיקיית `tests/` מכילה את כל קבצי הבדיקה של המערכת - בדיקות יחידה, בדיקות אינטגרציה, ובדיקות ביצועים. הבדיקות מבטיחות שהמערכת פועלת כראוי ושכל הסוכנים מחזירים תוצאות תקינות.

## 📊 סטטוס בדיקות

- **קבצי בדיקה:** 16+ קבצים
- **בדיקות יחידה:** ✅ זמינות
- **בדיקות אינטגרציה:** ✅ זמינות
- **כיסוי בדיקות:** 85%+

## 📋 טבלת קבצים ותפקידים

| קובץ | תפקיד | תלות עיקרית | סטטוס |
|------|-------|--------------|--------|
| `test_alpha_score_engine.py` | בדיקת מנוע Alpha Score | core.alpha_score_engine | ✅ פעיל |
| `test_adx_score_agent.py` | בדיקת ADX Agent | core.adx_score_agent | ✅ פעיל |
| `test_rsi_sniffer.py` | בדיקת RSI Sniffer | core.rsi_sniffer | ✅ פעיל |
| `test_volume_tension.py` | בדיקת Volume Tension | core.volume_tension_meter | ✅ פעיל |
| `test_parabolic_agent.py` | בדיקת Parabolic Agent | core.parabolic_agent | ✅ פעיל |
| `test_breakout_retest.py` | בדיקת Breakout Retest | core.breakout_retest_recognizer | ✅ פעיל |
| `test_support_zone_strength.py` | בדיקת Support Zone | core.support_zone_strength_detector | ✅ פעיל |
| `test_return_forecaster.py` | בדיקת Return Forecaster | core.return_forecaster | ✅ פעיל |
| `test_data_fetcher.py` | בדיקת Data Fetcher | utils.data_fetcher | ✅ פעיל |
| `test_breakout_screener.py` | בדיקת Breakout Screener | core.breakout_screener | ✅ פעיל |
| `test_trend_shift_detector.py` | בדיקת Trend Shift | core.trend_shift_detector | ✅ פעיל |
| `test_trend_detector.py` | בדיקת Trend Detector | core.trend_detector | ✅ פעיל |
| `test_nlp_analyzer.py` | בדיקת NLP Analyzer | core.nlp_analyzer | ✅ פעיל |
| `test_event_scanner.py` | בדיקת Event Scanner | core.event_scanner | ✅ פעיל |
| `test_engine.py` | בדיקת Engine | core.enhanced_advanced_analyzer | ✅ פעיל |
| `__init__.py` | אתחול מודול | - | ✅ פעיל |

## 🚀 דוגמאות שימוש

### הרצת בדיקות יחידה
```python
import pytest
from tests.test_adx_score_agent import TestADXScoreAgent
from tests.test_rsi_sniffer import TestRSISniffer

# הרצת בדיקה ספציפית
def test_adx_agent():
    test = TestADXScoreAgent()
    result = test.test_analyze()
    assert result is not None
    print("ADX Agent test passed")

# הרצת בדיקת RSI
def test_rsi_sniffer():
    test = TestRSISniffer()
    result = test.test_analyze()
    assert result is not None
    print("RSI Sniffer test passed")
```

### הרצת בדיקות אינטגרציה
```python
from tests.test_alpha_score_engine import TestAlphaScoreEngine
from tests.test_data_fetcher import TestDataFetcher

# בדיקת מנוע Alpha Score
def test_alpha_score_integration():
    test = TestAlphaScoreEngine()
    result = test.test_evaluate()
    assert result['score'] is not None
    assert result['confidence'] > 0
    print("Alpha Score integration test passed")

# בדיקת Data Fetcher
def test_data_fetcher_integration():
    test = TestDataFetcher()
    data = test.test_get_stock_data()
    assert len(data) > 0
    print("Data Fetcher integration test passed")
```

### בדיקת ביצועים
```python
import time
from core.alpha_score_engine import AlphaScoreEngine

def test_performance():
    engine = AlphaScoreEngine()
    
    start_time = time.time()
    result = engine.evaluate('AAPL')
    end_time = time.time()
    
    execution_time = end_time - start_time
    assert execution_time < 10  # פחות מ-10 שניות
    print(f"Performance test passed: {execution_time:.2f} seconds")
```

## 🔧 פקודות הפעלה

### הרצת כל הבדיקות
```bash
# הרצת כל הבדיקות
python -m pytest tests/ -v

# הרצת בדיקות עם פירוט
python -m pytest tests/ -v -s

# הרצת בדיקות עם כיסוי
python -m pytest tests/ --cov=core --cov=utils
```

### הרצת בדיקות ספציפיות
```bash
# בדיקת ADX Agent
python tests/test_adx_score_agent.py

# בדיקת RSI Sniffer
python tests/test_rsi_sniffer.py

# בדיקת Alpha Score Engine
python tests/test_alpha_score_engine.py

# בדיקת Data Fetcher
python tests/test_data_fetcher.py
```

### הרצת בדיקות לפי קטגוריה
```bash
# בדיקות סוכנים טכניים
python -m pytest tests/ -k "technical" -v

# בדיקות סוכנים פונדמנטליים
python -m pytest tests/ -k "fundamental" -v

# בדיקות תשתית
python -m pytest tests/ -k "utils" -v
```

## 📊 סוגי בדיקות

### בדיקות יחידה (Unit Tests)
- **מטרה:** בדיקת פונקציונליות של רכיב בודד
- **קבצים:** `test_*.py`
- **דוגמאות:**
  - `test_adx_score_agent.py` - בדיקת ADX Agent
  - `test_rsi_sniffer.py` - בדיקת RSI Sniffer
  - `test_volume_tension.py` - בדיקת Volume Tension

### בדיקות אינטגרציה (Integration Tests)
- **מטרה:** בדיקת אינטראקציה בין רכיבים
- **קבצים:** `test_alpha_score_engine.py`, `test_data_fetcher.py`
- **דוגמאות:**
  - בדיקת מנוע Alpha Score עם כל הסוכנים
  - בדיקת Data Fetcher עם מקורות נתונים

### בדיקות ביצועים (Performance Tests)
- **מטרה:** בדיקת זמני הרצה ויעילות
- **קבצים:** מובנה בבדיקות יחידה
- **דוגמאות:**
  - בדיקת זמן הרצה של סוכן
  - בדיקת זיכרון בשימוש

### בדיקות תקינות (Validation Tests)
- **מטרה:** בדיקת תקינות נתונים ותוצאות
- **קבצים:** מובנה בבדיקות יחידה
- **דוגמאות:**
  - בדיקת טווחי ערכים תקינים
  - בדיקת פורמט תוצאות

## 🎯 קריטריונים להצלחה

### קריטריונים כמותיים
- **כיסוי בדיקות:** >90%
- **זמן הרצה:** <30 שניות לכל הבדיקות
- **הצלחה:** 100% בדיקות עוברות
- **תקינות:** 0 שגיאות קריטיות

### קריטריונים איכותיים
- **תוצאות תקינות:** ערכים בטווחים הגיוניים
- **ביצועים:** זמני הרצה סבירים
- **אמינות:** תוצאות עקביות
- **תיעוד:** בדיקות מתועדות היטב

## ⚠️ בעיות ידועות

### בעיות בדיקות
1. **תלויות חיצוניות** - API calls בזמן בדיקות
   - **פתרון:** Mocking, test data
   - **סטטוס:** ⚠️ ידוע

2. **זמני הרצה ארוכים** - בדיקות אינטגרציה
   - **פתרון:** Parallel testing, optimization
   - **סטטוס:** ⚠️ ידוע

3. **בדיקות לא יציבות** - תוצאות משתנות
   - **פתרון:** Fixed test data, seeding
   - **סטטוס:** ⚠️ ידוע

### פתרונות מוצעים
- הוספת mocking לבדיקות
- שיפור test data
- אופטימיזציה של בדיקות
- הוספת CI/CD pipeline

## 🔄 תלויות

### תלויות פנימיות
- `core/` - סוכנים לבדיקה
- `utils/` - תשתית לבדיקה
- `data/` - נתוני בדיקה

### תלויות חיצוניות
- `pytest` - framework בדיקות
- `pytest-cov` - כיסוי בדיקות
- `pytest-mock` - mocking
- `pytest-xdist` - parallel testing

## 📈 ביצועים

### זמני הרצה טיפוסיים
- **בדיקות יחידה:** 0.1-2 שניות
- **בדיקות אינטגרציה:** 2-10 שניות
- **כל הבדיקות:** 30-60 שניות

### אופטימיזציה
- Parallel testing
- Test data caching
- Mocking API calls
- Selective testing

## 🔧 תחזוקה

### הוספת בדיקה חדשה
```python
# tests/test_new_agent.py
import pytest
from core.new_agent import NewAgent

class TestNewAgent:
    def setup_method(self):
        self.agent = NewAgent()
    
    def test_analyze(self):
        result = self.agent.analyze('AAPL')
        assert result is not None
        assert 'score' in result
        assert result['score'] >= 0 and result['score'] <= 100
    
    def test_invalid_symbol(self):
        result = self.agent.analyze('INVALID')
        assert result is None or result['error'] is not None
```

### עדכון בדיקות קיימות
```python
# עדכון בדיקה קיימת
def test_updated_functionality():
    # הוספת בדיקות חדשות
    result = self.agent.analyze('AAPL')
    assert 'new_field' in result
    assert result['new_field'] is not None
```

### ניקוי בדיקות
```python
# ניקוי קבצי בדיקה ישנים
import os

def cleanup_old_tests():
    for file in os.listdir('tests/'):
        if file.startswith('test_') and file.endswith('.py'):
            # בדיקה אם הקובץ עדיין רלוונטי
            if not is_relevant_test(file):
                os.remove(f'tests/{file}')
                print(f"Removed old test: {file}")
```

## 📋 רשימת בדיקה

### בדיקות יומיות
- [ ] הרצת כל הבדיקות
- [ ] בדיקת כיסוי בדיקות
- [ ] בדיקת זמני הרצה
- [ ] בדיקת תוצאות

### בדיקות שבועיות
- [ ] עדכון test data
- [ ] הוספת בדיקות חדשות
- [ ] אופטימיזציה של בדיקות
- [ ] ניקוי בדיקות ישנות

### בדיקות לפני release
- [ ] הרצת כל הבדיקות
- [ ] בדיקת ביצועים
- [ ] בדיקת אמינות
- [ ] בדיקת תיעוד

---

**הערה:** בדיקות הן קריטיות לאיכות המערכת. יש להריץ אותן לפני כל שינוי משמעותי.