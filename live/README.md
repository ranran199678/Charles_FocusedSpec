# Live - הרצה בזמן אמת

## 🎯 מטרת התיקייה

תיקיית `live/` מכילה את כל הקבצים להרצת המערכת בזמן אמת - הרצת סוכנים בודדים, הרצה מרובת סוכנים, וניהול תוצאות. קבצים אלה מאפשרים הפעלה מעשית של המערכת לניתוח מניות בזמן אמת.

## 📊 סטטוס הרצה

- **קבצי הרצה:** 2 קבצים
- **סוכנים פעילים:** 49 סוכנים
- **הרצה בזמן אמת:** ✅ זמינה
- **ניהול תוצאות:** ✅ זמין

## 📋 טבלת קבצים ותפקידים

| קובץ | תפקיד | תלות עיקרית | סטטוס |
|------|-------|--------------|--------|
| `agent_runner.py` | הרצת סוכן בודד | core.* | ✅ פעיל |
| `multi_agent_runner.py` | הרצה מרובת סוכנים | core.*, utils.* | ✅ פעיל |
| `outputs/` | תוצאות ודוחות | - | ✅ פעיל |

## 🚀 דוגמאות שימוש

### הרצת סוכן בודד
```python
from live.agent_runner import AgentRunner
from core.adx_score_agent import ADXScoreAgent
from core.rsi_sniffer import RSISniffer

# יצירת runner
runner = AgentRunner()

# הרצת ADX Agent
adx_result = runner.run_single_agent(ADXScoreAgent(), 'AAPL')
print(f"ADX Result: {adx_result}")

# הרצת RSI Sniffer
rsi_result = runner.run_single_agent(RSISniffer(), 'TSLA')
print(f"RSI Result: {rsi_result}")
```

### הרצה מרובת סוכנים
```python
from live.multi_agent_runner import MultiAgentRunner
from core.alpha_score_engine import AlphaScoreEngine

# יצירת multi-agent runner
multi_runner = MultiAgentRunner()

# הרצת ניתוח מלא
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
results = multi_runner.run_analysis(symbols)

# הדפסת תוצאות
for symbol, result in results.items():
    print(f"{symbol}: Score={result['score']}, Confidence={result['confidence']}")
```

### הרצת מנוע Alpha Score
```python
from live.multi_agent_runner import MultiAgentRunner

# הרצת Alpha Score Engine
runner = MultiAgentRunner()
alpha_results = runner.run_alpha_score_engine(['AAPL', 'MSFT'])

# ניתוח תוצאות
for symbol, result in alpha_results.items():
    print(f"=== {symbol} ===")
    print(f"Alpha Score: {result['score']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Agents Used: {result['agents_used']}")
    print(f"Recommendation: {result['recommendation']}")
```

### ניהול תוצאות
```python
from live.multi_agent_runner import MultiAgentRunner
import json

# הרצת ניתוח
runner = MultiAgentRunner()
results = runner.run_analysis(['AAPL', 'MSFT'])

# שמירת תוצאות
with open('live/outputs/analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# קריאת תוצאות
with open('live/outputs/analysis_results.json', 'r') as f:
    saved_results = json.load(f)

print(f"Saved results for {len(saved_results)} symbols")
```

## 🔧 פקודות הפעלה

### הרצת סוכן בודד
```bash
# הרצת ADX Agent
python -c "from live.agent_runner import AgentRunner; from core.adx_score_agent import ADXScoreAgent; runner = AgentRunner(); result = runner.run_single_agent(ADXScoreAgent(), 'AAPL'); print(result)"

# הרצת RSI Sniffer
python -c "from live.agent_runner import AgentRunner; from core.rsi_sniffer import RSISniffer; runner = AgentRunner(); result = runner.run_single_agent(RSISniffer(), 'TSLA'); print(result)"
```

### הרצה מרובת סוכנים
```bash
# הרצת ניתוח מלא
python live/multi_agent_runner.py

# הרצת Alpha Score Engine
python -c "from live.multi_agent_runner import MultiAgentRunner; runner = MultiAgentRunner(); results = runner.run_alpha_score_engine(['AAPL', 'MSFT']); print(results)"
```

### הרצת ניתוח מותאם
```bash
# הרצת ניתוח עם פרמטרים מותאמים
python -c "
from live.multi_agent_runner import MultiAgentRunner
runner = MultiAgentRunner()
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
results = runner.run_analysis(symbols, include_technical=True, include_fundamental=True)
for symbol, result in results.items():
    print(f'{symbol}: {result}')
"
```

## 📊 סוגי הרצה

### הרצת סוכן בודד
- **מטרה:** ניתוח מניה אחת עם סוכן אחד
- **קובץ:** `agent_runner.py`
- **דוגמאות:**
  - ניתוח ADX של AAPL
  - ניתוח RSI של TSLA
  - ניתוח Volume של MSFT

### הרצה מרובת סוכנים
- **מטרה:** ניתוח מניות מרובות עם כל הסוכנים
- **קובץ:** `multi_agent_runner.py`
- **דוגמאות:**
  - ניתוח מלא של רשימת מניות
  - Alpha Score Engine
  - ניתוח טכני ופונדמנטלי

### הרצה מותאמת
- **מטרה:** ניתוח עם פרמטרים מותאמים
- **קובץ:** `multi_agent_runner.py`
- **דוגמאות:**
  - ניתוח טכני בלבד
  - ניתוח פונדמנטלי בלבד
  - ניתוח סוכנים ספציפיים

## 🎯 קריטריונים להצלחה

### קריטריונים כמותיים
- **זמן הרצה:** <30 שניות למניה
- **דיוק:** >70% הצלחה בתחזיות
- **אמינות:** 100% הרצות מוצלחות
- **תוצאות:** פורמט אחיד

### קריטריונים איכותיים
- **תוצאות הגיוניות:** ערכים בטווחים תקינים
- **תיעוד מלא:** כל הניתוחים מתועדים
- **ניהול שגיאות:** טיפול בשגיאות
- **ביצועים:** זמני הרצה סבירים

## ⚠️ בעיות ידועות

### בעיות הרצה
1. **זמני הרצה ארוכים** - ניתוח מלא
   - **פתרון:** Parallel processing, caching
   - **סטטוס:** ⚠️ ידוע

2. **תלויות API** - שגיאות חיבור
   - **פתרון:** Retry logic, fallback
   - **סטטוס:** ⚠️ ידוע

3. **ניהול זיכרון** - שימוש גבוה בזיכרון
   - **פתרון:** Memory optimization
   - **סטטוס:** ⚠️ ידוע

### פתרונות מוצעים
- הוספת parallel processing
- שיפור caching
- אופטימיזציה של זיכרון
- שיפור error handling

## 🔄 תלויות

### תלויות פנימיות
- `core/` - כל הסוכנים
- `utils/` - תשתית ותחזוקה
- `data/` - נתונים ומסד נתונים

### תלויות חיצוניות
- `pandas` - עיבוד נתונים
- `numpy` - חישובים מתמטיים
- `requests` - קריאות API
- `sqlite3` - מסד נתונים

## 📈 ביצועים

### זמני הרצה טיפוסיים
- **סוכן בודד:** 0.5-3 שניות
- **Alpha Score Engine:** 5-15 שניות
- **ניתוח מלא:** 10-30 שניות למניה
- **ניתוח מרובה:** 1-5 דקות

### אופטימיזציה
- Parallel processing
- Caching תוצאות
- Memory management
- API rate limiting

## 🔧 תחזוקה

### ניהול תוצאות
```python
import os
import json
from datetime import datetime

def cleanup_old_results():
    """ניקוי תוצאות ישנות"""
    outputs_dir = 'live/outputs/'
    cutoff_date = datetime.now().replace(day=datetime.now().day - 7)
    
    for file in os.listdir(outputs_dir):
        file_path = os.path.join(outputs_dir, file)
        if os.path.getctime(file_path) < cutoff_date.timestamp():
            os.remove(file_path)
            print(f"Removed old result: {file}")
```

### גיבוי תוצאות
```python
import shutil
from datetime import datetime

def backup_results():
    """גיבוי תוצאות"""
    backup_dir = f"backup_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copytree('live/outputs/', backup_dir)
    print(f"Results backed up to: {backup_dir}")
```

### ניהול לוגים
```python
import logging

def setup_logging():
    """הגדרת לוגים"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('live/outputs/run.log'),
            logging.StreamHandler()
        ]
    )
```

## 📋 רשימת בדיקה

### בדיקות יומיות
- [ ] הרצת בדיקות בסיסיות
- [ ] בדיקת זמינות נתונים
- [ ] בדיקת API keys
- [ ] ניקוי תוצאות ישנות

### בדיקות שבועיות
- [ ] הרצת ניתוח מלא
- [ ] בדיקת ביצועים
- [ ] גיבוי תוצאות
- [ ] עדכון תיעוד

### בדיקות לפני release
- [ ] הרצת כל הבדיקות
- [ ] בדיקת אמינות
- [ ] בדיקת ביצועים
- [ ] בדיקת תיעוד

---

**הערה:** הרצה בזמן אמת דורשת תשומת לב מיוחדת לזמני הרצה, ניהול זיכרון, וטיפול בשגיאות.