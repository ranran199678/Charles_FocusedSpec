# Utils - תשתית ותחזוקה

## 🎯 מטרת התיקייה

תיקיית `utils/` מכילה את כל הקבצים והפונקציות התשתיתיות של המערכת - ניהול API keys, איסוף נתונים, קבועים, ותחזוקה כללית. קבצים אלה מספקים את התשתית לכל הסוכנים והמערכות.

## 📊 סטטוס קבצים

- **קבצים קיימים:** 9/13 (69%)
- **קבצים חסרים:** 4
- **קבצים פעילים:** 9
- **קבצים עם בעיות:** 0

## 📋 טבלת קבצים ותפקידים

| קובץ | תפקיד | תלות עיקרית | סטטוס |
|------|-------|--------------|--------|
| `data_fetcher.py` | מקור נתונים ראשי | requests, pandas | ✅ פעיל |
| `credentials.py` | ניהול API keys | os, json | ✅ פעיל |
| `constants.py` | קבועים מערכת | - | ✅ פעיל |
| `fmp_utils.py` | Financial Modeling Prep | requests, pandas | ✅ פעיל |
| `twelve_utils.py` | TwelveData API | requests, pandas | ✅ פעיל |
| `finnhub_utils.py` | Finnhub API | requests, pandas | ✅ פעיל |
| `fix_cert.py` | תיקון SSL | ssl | ✅ פעיל |
| `forecast_logger.py` | לוגים | logging, pandas | ✅ פעיל |
| `__init__.py` | אתחול מודול | - | ✅ פעיל |
| `data_loader.py` | ייבוא נתונים סטטיים | pandas, sqlite3 | ❌ חסר |
| `utils.py` | פונקציות עזר כלליות | - | ❌ חסר |
| `logging_utils.py` | ניהול לוגים מתקדם | logging | ❌ חסר |
| `scheduler.py` | הפעלה אוטומטית | schedule, threading | ❌ חסר |

## 🚀 דוגמאות שימוש

### איסוף נתונים
```python
from utils.data_fetcher import DataFetcher
from utils.fmp_utils import FMPUtils
from utils.twelve_utils import TwelveUtils

# איסוף נתוני מחירים
fetcher = DataFetcher()
price_data = fetcher.get_stock_data('AAPL', period='1y')
print(f"Price data shape: {price_data.shape}")

# איסוף נתונים פיננסיים
fmp = FMPUtils()
financial_data = fmp.get_financial_ratios('AAPL')
print(f"Financial ratios: {financial_data}")

# איסוף אינדיקטורים טכניים
twelve = TwelveUtils()
technical_data = twelve.get_technical_indicators('AAPL', 'RSI')
print(f"RSI data: {technical_data}")
```

### ניהול API Keys
```python
from utils.credentials import Credentials

# טעינת API keys
creds = Credentials()
api_keys = creds.load_api_keys()

# בדיקת זמינות
if creds.check_api_key('finnhub'):
    print("Finnhub API key זמין")
else:
    print("Finnhub API key חסר")

# הוספת API key חדש
creds.add_api_key('alpha_vantage', 'YOUR_NEW_KEY')
```

### שימוש בקבועים
```python
from utils.constants import *

# קבועי אינדיקטורים
print(f"RSI period: {RSI_PERIOD}")
print(f"MACD fast: {MACD_FAST}")
print(f"Bollinger period: {BOLLINGER_PERIOD}")

# קבועי API
print(f"FMP base URL: {FMP_BASE_URL}")
print(f"Finnhub base URL: {FINNHUB_BASE_URL}")
```

### לוגים ותיעוד
```python
from utils.forecast_logger import ForecastLogger

# יצירת לוגר
logger = ForecastLogger()

# תיעוד תחזית
logger.log_forecast(
    symbol='AAPL',
    prediction='BUY',
    confidence=0.85,
    agents_used=['ADX', 'RSI', 'Volume']
)

# קריאת היסטוריית תחזיות
history = logger.get_forecast_history('AAPL')
print(f"Forecast history: {history}")
```

## 🔧 פקודות הפעלה

### בדיקת API Keys
```bash
# בדיקת זמינות API keys
python -c "from utils.credentials import Credentials; c = Credentials(); print(c.check_all_keys())"

# בדיקת חיבור ל-FMP
python -c "from utils.fmp_utils import FMPUtils; fmp = FMPUtils(); print(fmp.test_connection())"

# בדיקת חיבור ל-Finnhub
python -c "from utils.finnhub_utils import FinnhubUtils; fh = FinnhubUtils(); print(fh.test_connection())"
```

### איסוף נתונים
```bash
# איסוף נתוני AAPL
python -c "from utils.data_fetcher import DataFetcher; df = DataFetcher(); data = df.get_stock_data('AAPL'); print(data.head())"

# איסוף אינדיקטורים טכניים
python -c "from utils.twelve_utils import TwelveUtils; tt = TwelveUtils(); rsi = tt.get_technical_indicators('AAPL', 'RSI'); print(rsi)"
```

### בדיקת לוגים
```bash
# בדיקת מערכת לוגים
python -c "from utils.forecast_logger import ForecastLogger; fl = ForecastLogger(); fl.log_forecast('TEST', 'HOLD', 0.5, ['TEST']); print('Log test successful')"
```

## 📊 מקורות נתונים נתמכים

### מקורות פעילים
1. **Yahoo Finance** - נתוני מחירים היסטוריים
   - **קובץ:** `data_fetcher.py`
   - **סטטוס:** ✅ פעיל (עם בעיות 429)

2. **FMP (Financial Modeling Prep)** - נתונים פיננסיים
   - **קובץ:** `fmp_utils.py`
   - **סטטוס:** ✅ פעיל (עם בעיות 403)

3. **TwelveData** - אינדיקטורים טכניים
   - **קובץ:** `twelve_utils.py`
   - **סטטוס:** ✅ פעיל

4. **Finnhub** - חדשות ונתונים
   - **קובץ:** `finnhub_utils.py`
   - **סטטוס:** ✅ פעיל

### מקורות חסרים
1. **Alpha Vantage** - נתונים טכניים מתקדמים
2. **MarketAux** - ניתוח סנטימנט
3. **NewsData** - חדשות פיננסיות
4. **Reuters** - חדשות איכותיות

## 🔑 ניהול API Keys

### API Keys זמינים
```python
# config/config.yaml
api_keys:
  finnhub: "YOUR_FINNHUB_API_KEY"      # ✅ זמין
  fmp: "YOUR_FMP_API_KEY"             # ✅ זמין
  twelve_data: "YOUR_TWELVE_API_KEY"  # ✅ זמין
```

### API Keys חסרים
```python
# config/config.yaml
api_keys:
  alpha_vantage: "YOUR_ALPHA_VANTAGE_API_KEY"  # ❌ חסר
  marketaux: "YOUR_MARKETAUX_API_KEY"          # ❌ חסר
  newsdata: "YOUR_NEWSDATA_API_KEY"            # ❌ חסר
  reuters: "YOUR_REUTERS_API_KEY"              # ❌ חסר
```

## ⚠️ בעיות ידועות

### בעיות API
1. **Yahoo Finance 429** - Too Many Requests
   - **פתרון:** Rate limiting, caching
   - **סטטוס:** ⚠️ ידוע

2. **FMP 403** - Forbidden
   - **פתרון:** API key validation
   - **סטטוס:** ⚠️ ידוע

### פתרונות מוצעים
- הוספת retry logic
- שיפור error handling
- Fallback sources
- Caching strategies

## 🔄 תלויות

### תלויות פנימיות
- `config/` - הגדרות מערכת
- `data/` - נתונים ומסד נתונים

### תלויות חיצוניות
- `requests` - קריאות HTTP
- `pandas` - עיבוד נתונים
- `logging` - ניהול לוגים
- `ssl` - אבטחה
- `schedule` - הפעלה אוטומטית (עתידי)
- `threading` - עיבוד מקביל (עתידי)

## 📈 ביצועים

### זמני תגובה טיפוסיים
- **Yahoo Finance:** 0.5-2 שניות
- **FMP:** 1-3 שניות
- **TwelveData:** 0.5-1.5 שניות
- **Finnhub:** 0.3-1 שניות

### אופטימיזציה
- Connection pooling
- Request caching
- Parallel requests
- Error retry logic

## 🔧 תחזוקה

### ניקוי לוגים
```python
from utils.forecast_logger import ForecastLogger

logger = ForecastLogger()
logger.cleanup_old_logs(days=30)  # מחיקת לוגים ישנים
```

### גיבוי נתונים
```python
from utils.data_fetcher import DataFetcher

fetcher = DataFetcher()
fetcher.backup_data()  # גיבוי נתונים
```

### עדכון API keys
```python
from utils.credentials import Credentials

creds = Credentials()
creds.update_api_key('finnhub', 'NEW_KEY')
creds.save_api_keys()
```

## 📋 רשימת בדיקה

### בדיקות יומיות
- [ ] בדיקת זמינות API keys
- [ ] בדיקת חיבור למקורות נתונים
- [ ] בדיקת לוגים
- [ ] ניקוי קבצים זמניים

### בדיקות שבועיות
- [ ] גיבוי נתונים
- [ ] עדכון dependencies
- [ ] בדיקת ביצועים
- [ ] ניקוי לוגים ישנים

---

**הערה:** קבצי utils הם הבסיס לכל המערכת ויש לוודא שהם פועלים כראוי לפני הרצת סוכנים.