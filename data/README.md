# Data - ניהול נתונים ומסד נתונים

## 🎯 מטרת התיקייה

תיקיית `data/` מכילה את כל הנתונים של המערכת - נתונים גולמיים, נתונים מעובדים, אינדיקטורים טכניים, ומסד נתונים SQLite. התיקייה מאורגנת בצורה היררכית לפי סוגי נתונים וזמנים.

## 📊 סטטוס נתונים

- **נתונים גולמיים:** ✅ זמינים (Yahoo Finance)
- **נתונים מעובדים:** ✅ זמינים (יומי/שבועי/חודשי)
- **אינדיקטורים טכניים:** ✅ זמינים
- **מסד נתונים:** ✅ פעיל (SQLite)

## 📁 מבנה תיקיות

```
data/
├── raw_price_data/           # נתונים גולמיים מ-Yahoo Finance
│   ├── AAPL Stock Price History.csv
│   ├── MSFT Stock Price History.csv
│   └── ...
├── historical_prices/        # נתונים מעובדים
│   ├── daily/               # נתונים יומיים
│   │   ├── AAPL.csv
│   │   ├── MSFT.csv
│   │   └── ...
│   ├── weekly/              # נתונים שבועיים
│   │   ├── AAPL.csv
│   │   ├── MSFT.csv
│   │   └── ...
│   └── monthly/             # נתונים חודשיים
│       ├── AAPL.csv
│       ├── MSFT.csv
│       └── ...
├── technical_indicators/     # אינדיקטורים טכניים
│   ├── rsi/
│   │   ├── daily/
│   │   ├── weekly/
│   │   └── monthly/
│   ├── macd/
│   │   ├── daily/
│   │   ├── weekly/
│   │   └── monthly/
│   ├── bollinger/
│   │   ├── daily/
│   │   ├── weekly/
│   │   └── monthly/
│   ├── sma/
│   │   ├── daily/
│   │   ├── weekly/
│   │   └── monthly/
│   ├── ema/
│   │   ├── daily/
│   │   ├── weekly/
│   │   └── monthly/
│   ├── atr/
│   │   ├── daily/
│   │   ├── weekly/
│   │   └── monthly/
│   ├── stochastic/
│   │   ├── daily/
│   │   ├── weekly/
│   │   └── monthly/
│   ├── williams_r/
│   │   ├── daily/
│   │   ├── weekly/
│   │   └── monthly/
│   ├── cci/
│   │   ├── daily/
│   │   ├── weekly/
│   │   └── monthly/
│   └── adx/
│       ├── daily/
│       ├── weekly/
│       └── monthly/
├── database/                 # מסד נתונים SQLite
│   └── historical.db
├── metadata/                 # מטא-דאטה
│   └── processed_files.json
├── market_data/              # נתוני שוק נוספים
│   ├── economic_indicators/
│   ├── indices/
│   └── sectors/
├── news_sentiment/           # נתוני חדשות וסנטימנט
│   ├── analyst_ratings/
│   ├── financial_news/
│   └── social_media/
└── code/                     # קוד עיבוד נתונים
    ├── yfinance_CSV.PY
    ├── enhanced_data_processor.py
    ├── advanced_indicators_processor.py
    └── smart_data_processor.py
```

## 📋 טבלת קבצים ותפקידים

| קובץ/תיקייה | תפקיד | תלות עיקרית | סטטוס |
|-------------|-------|--------------|--------|
| `raw_price_data/` | נתונים גולמיים | Yahoo Finance | ✅ פעיל |
| `historical_prices/daily/` | נתונים יומיים | pandas, sqlite3 | ✅ פעיל |
| `historical_prices/weekly/` | נתונים שבועיים | pandas, sqlite3 | ✅ פעיל |
| `historical_prices/monthly/` | נתונים חודשיים | pandas, sqlite3 | ✅ פעיל |
| `technical_indicators/` | אינדיקטורים טכניים | pandas, talib | ✅ פעיל |
| `database/historical.db` | מסד נתונים | sqlite3 | ✅ פעיל |
| `metadata/processed_files.json` | מטא-דאטה | json | ✅ פעיל |
| `code/yfinance_CSV.PY` | הורדת נתונים | requests, pandas | ✅ פעיל |
| `code/enhanced_data_processor.py` | עיבוד נתונים | pandas, sqlite3 | ✅ פעיל |
| `code/advanced_indicators_processor.py` | חישוב אינדיקטורים | pandas, talib | ✅ פעיל |
| `code/smart_data_processor.py` | עיבוד חכם | pandas, hashlib | ✅ פעיל |

## 🚀 דוגמאות שימוש

### קריאת נתוני מחירים
```python
import pandas as pd
import sqlite3

# קריאה מקובץ CSV
daily_data = pd.read_csv('data/historical_prices/daily/AAPL.csv')
print(f"Daily data shape: {daily_data.shape}")

# קריאה ממסד נתונים
conn = sqlite3.connect('data/database/historical.db')
query = "SELECT * FROM historical_prices WHERE symbol='AAPL' AND timeframe='daily'"
db_data = pd.read_sql_query(query, conn)
conn.close()
print(f"Database data shape: {db_data.shape}")
```

### קריאת אינדיקטורים טכניים
```python
# קריאת RSI
rsi_data = pd.read_csv('data/technical_indicators/rsi/daily/AAPL_rsi_14_daily.csv')
print(f"RSI data: {rsi_data.head()}")

# קריאת MACD
macd_data = pd.read_csv('data/technical_indicators/macd/daily/AAPL_macd_daily.csv')
print(f"MACD data: {macd_data.head()}")

# קריאת Bollinger Bands
bb_data = pd.read_csv('data/technical_indicators/bollinger/daily/AAPL_bollinger_daily.csv')
print(f"Bollinger data: {bb_data.head()}")
```

### עיבוד נתונים חדשים
```python
# הורדת נתונים חדשים
from data.code.yfinance_CSV import download_stock_data

symbols = ['AAPL', 'MSFT', 'GOOGL']
download_stock_data(symbols, start_date='2020-01-01', end_date='2024-12-31')

# עיבוד נתונים
from data.code.enhanced_data_processor import EnhancedDataProcessor

processor = EnhancedDataProcessor()
processor.process_all_files()

# חישוב אינדיקטורים
from data.code.advanced_indicators_processor import AdvancedIndicatorsProcessor

indicator_processor = AdvancedIndicatorsProcessor()
indicator_processor.process_all_files()
```

### ניהול מטא-דאטה
```python
import json

# קריאת מטא-דאטה
with open('data/metadata/processed_files.json', 'r') as f:
    metadata = json.load(f)

print(f"Processed files: {len(metadata)}")

# הוספת קובץ חדש
metadata['new_file.csv'] = {
    'processed_date': '2024-01-27',
    'rows': 1000,
    'indicators': ['RSI', 'MACD', 'Bollinger']
}

with open('data/metadata/processed_files.json', 'w') as f:
    json.dump(metadata, f, indent=2)
```

## 🔧 פקודות הפעלה

### הורדת נתונים
```bash
# הורדת נתונים מ-Yahoo Finance
python scripts/yfinance_CSV.PY

# הורדת מניות ספציפיות
python -c "from data.code.yfinance_CSV import download_stock_data; download_stock_data(['AAPL', 'MSFT'])"
```

### עיבוד נתונים
```bash
# עיבוד כל הקבצים
python scripts/enhanced_data_processor.py

# עיבוד אינדיקטורים
python scripts/advanced_indicators_processor.py

# עיבוד חכם
python scripts/smart_data_processor.py
```

### בדיקת נתונים
```bash
# בדיקת קבצים זמינים
ls data/historical_prices/daily/ | wc -l

# בדיקת אינדיקטורים
ls data/technical_indicators/rsi/daily/ | wc -l

# בדיקת מסד נתונים
sqlite3 data/database/historical.db "SELECT COUNT(*) FROM historical_prices;"
```

## 📊 אינדיקטורים טכניים נתמכים

### אינדיקטורי מגמה
- **SMA (Simple Moving Average)** - 20, 50, 200 תקופות
- **EMA (Exponential Moving Average)** - 20, 50, 200 תקופות
- **MACD** - 12, 26, 9 תקופות
- **VWAP** - Volume Weighted Average Price

### אינדיקטורי מומנטום
- **RSI (Relative Strength Index)** - 14 תקופות
- **Stochastic %K, %D** - 14, 3 תקופות
- **Williams %R** - 14 תקופות
- **CCI (Commodity Channel Index)** - 20 תקופות

### אינדיקטורי תנודתיות
- **ATR (Average True Range)** - 14 תקופות
- **Bollinger Bands** - 20 תקופות, 2 סטיות תקן

### אינדיקטורי נפח
- **Volume** - נפח מסחר
- **Volume SMA** - ממוצע נפח

## 🔄 זרימת נתונים

### 1. איסוף נתונים גולמיים
```
Yahoo Finance → raw_price_data/ → CSV files
```

### 2. עיבוד נתונים
```
raw_price_data/ → enhanced_data_processor.py → historical_prices/
```

### 3. חישוב אינדיקטורים
```
historical_prices/ → advanced_indicators_processor.py → technical_indicators/
```

### 4. שמירה למסד נתונים
```
historical_prices/ + technical_indicators/ → SQLite database
```

## 📈 סטטיסטיקות נתונים

### נתונים זמינים
- **מניות:** 100+ מניות
- **תקופה:** 2020-2024 (5 שנים)
- **תדירות:** יומי, שבועי, חודשי
- **שורות נתונים:** 1,000,000+ שורות

### אינדיקטורים מחושבים
- **סוגי אינדיקטורים:** 10
- **תדירויות:** 3 (יומי/שבועי/חודשי)
- **קבצים:** 300+ קבצי אינדיקטורים

### ביצועים
- **זמן עיבוד מניה:** 2-5 שניות
- **זמן חישוב אינדיקטורים:** 1-3 שניות
- **גודל מסד נתונים:** 50MB+

## ⚠️ בעיות ידועות

### בעיות נתונים
1. **Yahoo Finance 429** - Too Many Requests
   - **פתרון:** Rate limiting, caching
   - **סטטוס:** ⚠️ ידוע

2. **קבצים ריקים** - נתונים לא מלאים
   - **פתרון:** Re-processing, validation
   - **סטטוס:** ✅ נפתר

3. **אינדיקטורים חסרים** - Williams %R
   - **פתרון:** Manual calculation
   - **סטטוס:** ⚠️ ידוע

### פתרונות מוצעים
- Validation של נתונים
- Error handling משופר
- Fallback sources
- Data quality checks

## 🔧 תחזוקה

### ניקוי נתונים
```python
# ניקוי קבצים ריקים
import os
import pandas as pd

for file in os.listdir('data/historical_prices/daily/'):
    file_path = f'data/historical_prices/daily/{file}'
    df = pd.read_csv(file_path)
    if len(df) < 100:  # פחות מ-100 שורות
        os.remove(file_path)
        print(f"Removed {file}")
```

### גיבוי נתונים
```python
import shutil
import datetime

# גיבוי יומי
backup_dir = f"backup_{datetime.date.today()}"
shutil.copytree('data', backup_dir)
print(f"Backup created: {backup_dir}")
```

### עדכון מטא-דאטה
```python
import json
import os

# עדכון מטא-דאטה
metadata = {}
for file in os.listdir('data/historical_prices/daily/'):
    file_path = f'data/historical_prices/daily/{file}'
    df = pd.read_csv(file_path)
    metadata[file] = {
        'rows': len(df),
        'last_updated': datetime.datetime.now().isoformat()
    }

with open('data/metadata/processed_files.json', 'w') as f:
    json.dump(metadata, f, indent=2)
```

## 📋 רשימת בדיקה

### בדיקות יומיות
- [ ] בדיקת זמינות נתונים חדשים
- [ ] בדיקת איכות נתונים
- [ ] בדיקת אינדיקטורים
- [ ] גיבוי נתונים

### בדיקות שבועיות
- [ ] ניקוי קבצים ישנים
- [ ] עדכון מטא-דאטה
- [ ] בדיקת ביצועים
- [ ] אופטימיזציה מסד נתונים

---

**הערה:** נתונים הם הבסיס לכל הניתוחים. יש לוודא איכות ועדכניות הנתונים לפני הרצת סוכנים.