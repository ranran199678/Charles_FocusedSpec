# Charles FocusedSpec - מערכת חיזוי מניות פורצות

# טבלת סטטוס מרכזית

| תיקיה         | סטטוס         | בעיות/חסרים עיקריים                | תלויות בין צוותים/מודולים         |
|---------------|---------------|-------------------------------------|------------------------------------|
| core          | 100% הושלם    | 4 סוכנים דורשים תיקון/אופטימיזציה  | utils (לוגים, אימות), data        |
| utils         | 77%           | חסרים: validators, logger, file_utils | config, core, data                |
| data          | 90%           | חסרים: backup, metadata manager, validation pipeline | scripts, core, utils              |
| tests         | 85% כיסוי     | חסרים: בדיקות אינטגרציה, ביצועים, error handling | core, utils, data                 |
| live          | בסיסי         | שיפור ניהול זיכרון, parallel, ניטור ביצועים | core, utils, data                 |
| dashboard     | בסיסי         | חסרים: רכיבי גרפים, ויזואליזציה, ניטור ביצועים | data, models                      |
| config        | בסיסי         | חסרים: config validator, manager, templates, encryption | utils, core, data                 |
| models        | לא התחיל      | חסרים: כל המודלים (חיזוי, רגשות, דפוסים) | data, core, vectorstore           |
| vectorstore   | לא התחיל      | חסרים: embedding generator, vector manager, search engine | models, data                      |

## 🎯 סקירה כללית

**Charles FocusedSpec** היא מערכת רב-סוכנים מתקדמת לחיזוי מניות פורצות המבוססת על ניתוח טכני ופונדמנטלי מתקדם. המערכת כוללת 49 סוכנים פעילים המנתחים מגוון רחב של אינדיקטורים ושוקלים.

### 📊 סטטוס פרויקט
- **סוכנים קיימים:** 49/60 (82%)
- **תשתית:** 69% הושלמה
- **מקורות נתונים:** 4/8 פעילים
- **בדיקות:** 16+ קבצי בדיקה

## 🏗️ ארכיטקטורה

```
Charles_FocusedSpec/
├── core/                    # 49 סוכני ניתוח
│   ├── base/               # סוכנים בסיסיים
│   ├── subagents/          # סוכני משנה
│   └── *.py               # סוכנים מתמחים
├── utils/                  # תשתית ותחזוקה
├── config/                 # הגדרות מערכת
├── data/                   # נתונים ומסד נתונים
│   ├── raw_price_data/     # נתונים גולמיים
│   ├── historical_prices/  # נתונים מעובדים
│   └── technical_indicators/ # אינדיקטורים טכניים
├── tests/                  # בדיקות מערכת
├── live/                   # הרצה בזמן אמת
├── dashboard/              # ממשק משתמש
├── models/                 # מודלי למידת מכונה
├── vectorstore/            # מאגר וקטורי
└── outputs/                # תוצאות ודוחות
```

## 📁 מבנה תיקיות מפורט

### 🔴 Core - סוכני הניתוח
**📄 קובץ מלא:** [`core/README.md`](core/README.md)

**סטטוס:** 49/60 סוכנים (82%)
**תפקיד:** כל הסוכנים המנתחים מניות ואינדיקטורים

**סוכנים עיקריים:**
- **סוכנים טכניים (29):** ניתוח מחירים, נפח, מגמות
- **סוכנים פונדמנטליים (8):** ניתוח פיננסי, חדשות, סנטימנט
- **סוכני ארכיטקטורה (4):** ניהול וסינתזה
- **סוכנים נוספים (8):** ניתוחים מתמחים

**דוגמאות שימוש:**
```python
from core.alpha_score_engine import AlphaScoreEngine
engine = AlphaScoreEngine()
result = engine.evaluate('AAPL')

from core.adx_score_agent import ADXScoreAgent
agent = ADXScoreAgent()
analysis = agent.analyze('TSLA')
```

---

### 🔴 Utils - תשתית ותחזוקה
**📄 קובץ מלא:** [`utils/README.md`](utils/README.md)

**סטטוס:** 7/13 קבצים (54%)
**תפקיד:** פונקציות עזר, ניהול API, לוגים

**קבצים עיקריים:**
- `data_fetcher.py` - איסוף נתונים ממקורות שונים
- `credentials.py` - ניהול API keys
- `constants.py` - קבועים מערכת
- `fmp_utils.py`, `twelve_utils.py`, `finnhub_utils.py` - ממשקי API

**דוגמאות שימוש:**
```python
from utils.credentials import get_api_key
api_key = get_api_key('yahoo_finance')

from utils.data_fetcher import DataFetcher
fetcher = DataFetcher()
data = fetcher.get_stock_data('AAPL')
```

---

### 🔴 Data - ניהול נתונים
**📄 קובץ מלא:** [`data/README.md`](data/README.md)

**סטטוס:** מערכת בסיסית קיימת
**תפקיד:** אחסון, עיבוד וניהול כל הנתונים

**מבנה נתונים:**
- `raw_price_data/` - נתונים גולמיים מ-Yahoo Finance
- `historical_prices/` - נתונים מעובדים (יומי/שבועי/חודשי)
- `technical_indicators/` - אינדיקטורים מחושבים
- `database/` - מסד נתונים SQLite

**דוגמאות שימוש:**
```python
# הורדת נתונים חדשים
python scripts/yfinance_CSV.PY

# עיבוד נתונים גולמיים
python scripts/enhanced_data_processor.py

# חישוב אינדיקטורים טכניים
python scripts/advanced_indicators_processor.py
```

---

### 🔴 Tests - בדיקות מערכת
**📄 קובץ מלא:** [`tests/README.md`](tests/README.md)

**סטטוס:** בדיקות בסיסיות קיימות
**תפקיד:** בדיקות יחידה, אינטגרציה וביצועים

**סוגי בדיקות:**
- Unit tests לכל סוכן
- Integration tests
- Performance tests
- Error handling tests

**דוגמאות שימוש:**
```bash
# הרצת כל הבדיקות
python -m pytest tests/

# בדיקה ספציפית
python -m pytest tests/test_alpha_score_engine.py

# בדיקות כיסוי
python -m pytest tests/ --cov=core
```

---

### 🔴 Live - הרצה בזמן אמת
**📄 קובץ מלא:** [`live/README.md`](live/README.md)

**סטטוס:** מערכת בסיסית קיימת
**תפקיד:** הרצת סוכנים, ניטור ותזמון

**קבצים עיקריים:**
- `agent_runner.py` - הרצת סוכן בודד
- `multi_agent_runner.py` - הרצה מרובת סוכנים
- `outputs/` - תוצאות הרצות

**דוגמאות שימוש:**
```python
from live.multi_agent_runner import MultiAgentRunner
runner = MultiAgentRunner()
results = runner.run_analysis(['AAPL', 'MSFT', 'GOOGL'])
```

---

### 🔴 Config - הגדרות מערכת
**📄 קובץ מלא:** [`config/README.md`](config/README.md)

**סטטוס:** קבצי config בסיסיים קיימים
**תפקיד:** ניהול הגדרות, API keys ותצורות

**קבצים עיקריים:**
- `config.yaml` - הגדרות ראשיות
- `gap_config.yaml` - הגדרות GAP analysis
- `api_keys.yaml` - מפתחות API

**דוגמאות שימוש:**
```python
import yaml
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

api_key = config['api_keys']['yahoo_finance']
```

---

### 🟡 Dashboard - ממשק משתמש
**📄 קובץ מלא:** [`dashboard/README.md`](dashboard/README.md)

**סטטוס:** דשבורד בסיסי קיים
**תפקיד:** ויזואליזציה, גרפים וממשק משתמש

**רכיבים עיקריים:**
- `main_dashboard.py` - דשבורד ראשי
- `charts/` - רכיבי גרפים
- `data_visualizer.py` - ויזואליזציה נתונים

**דוגמאות שימוש:**
```bash
# הרצת דשבורד ראשי
streamlit run dashboard/main_dashboard.py

# הרצת ויזואליזציה נתונים
python dashboard/data_visualizer.py --symbol AAPL
```

---

### 🟡 Models - מודלי למידת מכונה
**📄 קובץ מלא:** [`models/README.md`](models/README.md)

**סטטוס:** לא התחיל
**תפקיד:** מודלי חיזוי, ניתוח רגשות וזיהוי דפוסים

**מודלים עיקריים:**
- `price_predictor.py` - חיזוי מחירי מניות
- `sentiment_analyzer.py` - ניתוח רגשות חדשות
- `pattern_detector.py` - זיהוי דפוסים טכניים

**דוגמאות שימוש:**
```python
from models.price_predictor import PricePredictor
predictor = PricePredictor()
prediction = predictor.predict('AAPL', days=30)

from models.sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer()
sentiment = analyzer.analyze_news('AAPL news text')
```

---

### 🟡 Vectorstore - מאגר וקטורי
**📄 קובץ מלא:** [`vectorstore/README.md`](vectorstore/README.md)

**סטטוס:** לא התחיל
**תפקיד:** אחסון וחיפוש מידע טקסטואלי וקטורי

**רכיבים עיקריים:**
- `embedding_generator.py` - יצירת embeddings
- `vector_manager.py` - ניהול וקטורים
- `search_engine.py` - מנוע חיפוש

**דוגמאות שימוש:**
```python
from vectorstore.embedding_generator import EmbeddingGenerator
generator = EmbeddingGenerator()
embeddings = generator.generate('AAPL news text')

from vectorstore.search_engine import SearchEngine
engine = SearchEngine()
results = engine.search('AAPL earnings', top_k=10)
```

---

## 🔄 זרימת נתונים

```
1. איסוף נתונים
   ├── Yahoo Finance (מחירים היסטוריים)
   ├── FMP (נתונים פיננסיים)
   ├── TwelveData (אינדיקטורים טכניים)
   └── Finnhub (חדשות וסנטימנט)

2. עיבוד נתונים
   ├── ניקוי ונרמול
   ├── חישוב אינדיקטורים טכניים
   ├── אגרגציה יומית/שבועית/חודשית
   └── שמירה למסד נתונים

3. ניתוח סוכנים
   ├── 29 סוכנים טכניים
   ├── 8 סוכנים פונדמנטליים
   ├── 4 סוכני ארכיטקטורה
   └── 8 סוכנים נוספים

4. סינתזה ותוצאות
   ├── Alpha Score Engine
   ├── Meta Agent
   ├── High Conviction Orchestrator
   └── Multi-Agent Validator
```

## 🚀 התקנה והפעלה

### דרישות מערכת
- Python 3.8+
- pip
- SQLite3
- חיבור אינטרנט

### התקנה
```bash
# שכפול הפרויקט
git clone <repository-url>
cd Charles_FocusedSpec

# התקנת תלויות
pip install -r requirements.txt

# הגדרת API Keys
cp config/config.yaml.example config/config.yaml
# ערוך את config.yaml והוסף את ה-API Keys שלך
```

### API Keys נדרשים
```yaml
# config/config.yaml
api_keys:
  finnhub: "YOUR_FINNHUB_API_KEY"
  fmp: "YOUR_FMP_API_KEY"
  twelve_data: "YOUR_TWELVE_API_KEY"
  # אופציונלי:
  alpha_vantage: "YOUR_ALPHA_VANTAGE_API_KEY"
  marketaux: "YOUR_MARKETAUX_API_KEY"
```

### הפעלה בסיסית
```bash
# הרצת בדיקה פשוטה
python simple_test.py

# הרצת מנוע Alpha Score
python -c "from core.alpha_score_engine import AlphaScoreEngine; engine = AlphaScoreEngine(); result = engine.evaluate('AAPL')"

# הרצת סוכן בודד
python -c "from core.adx_score_agent import ADXScoreAgent; agent = ADXScoreAgent(); result = agent.analyze('AAPL')"

# הרצה מרובת סוכנים
python live/multi_agent_runner.py
```

## 🎯 שימוש ב-Cursor

### הגדרת סביבת עבודה
1. פתח את הפרויקט ב-Cursor
2. הגדר Python interpreter (3.8+)
3. התקן תלויות: `pip install -r requirements.txt`
4. הגדר API keys ב-`config/config.yaml`

### דוגמאות קוד
```python
# ניתוח מניה בודדת
from core.alpha_score_engine import AlphaScoreEngine
engine = AlphaScoreEngine()
result = engine.evaluate('AAPL')
print(f"Alpha Score: {result}")

# ניתוח טכני מתקדם
from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
analyzer = EnhancedAdvancedAnalyzer()
analysis = analyzer.analyze('TSLA')
print(analysis)

# הרצה מרובת סוכנים
from live.multi_agent_runner import MultiAgentRunner
runner = MultiAgentRunner()
results = runner.run_analysis(['AAPL', 'MSFT', 'GOOGL'])
```

### דיבוג ובדיקות
```bash
# הרצת כל הבדיקות
python -m pytest tests/

# בדיקה ספציפית
python tests/test_alpha_score_engine.py

# בדיקת נתונים
python scripts/enhanced_data_processor.py
```

## 📊 אינדיקטורים טכניים נתמכים

### אינדיקטורי מגמה
- SMA, EMA (20, 50, 200)
- MACD, MACD Signal
- ADX, DI+, DI-
- VWAP, VWAP Trend

### אינדיקטורי מומנטום
- RSI (14)
- Stochastic %K, %D
- Williams %R
- CCI (Commodity Channel Index)

### אינדיקטורי נפח
- Volume Surge Detection
- Volume Tension Meter
- Classic Volume Surge
- Volume Spike Agent

### אינדיקטורי תנודתיות
- ATR (Average True Range)
- Bollinger Bands
- Bollinger Squeeze
- Volatility Score

### תבניות מחירים
- Candlestick Patterns
- Bullish Patterns
- Breakout & Retest
- V Reversal
- Golden Cross

## 🔧 תחזוקה ופיתוח

### הוספת סוכן חדש
1. צור קובץ ב-`core/`
2. ירש מ-`base_agent.py`
3. מימוש `analyze()` method
4. הוסף בדיקות ב-`tests/`
5. עדכן תיעוד

### הוספת מקור נתונים
1. צור קובץ ב-`utils/`
2. מימוש ממשק API
3. הוסף ל-`data_fetcher.py`
4. עדכן `config.yaml`

### הרצת בדיקות
```bash
# בדיקות יחידה
python -m pytest tests/ -v

# בדיקות כיסוי
python -m pytest tests/ --cov=core

# בדיקות ביצועים
python tests/performance_test.py
```

## 📈 ביצועים וניטור

### לוגים
- `log/` - קבצי לוג מערכת
- `outputs/` - תוצאות ודוחות
- `forecast_log.csv` - היסטוריית תחזיות

### ניטור API
- מעקב אחר שימוש ב-API keys
- Fallback למקורות חלופיים
- טיפול בשגיאות 429/403

### אופטימיזציה
- Caching נתונים
- Parallel processing
- Database indexing

## 🤝 תרומה לפיתוח

### הנחיות קוד
- PEP 8 compliance
- Type hints
- Docstrings בעברית
- Error handling מקיף

### תהליך פיתוח
1. Fork repository
2. צור branch חדש
3. פיתוח עם בדיקות
4. Pull request עם תיעוד

## 📞 תמיכה וקשר

### בעיות ידועות
- Yahoo Finance: HTTP 429 (Too Many Requests)
- FMP: שגיאות 403 (API key issues)
- Alpha Vantage: לא זמין (אין API key)

### פתרונות
- Rate limiting
- API key rotation
- Fallback sources
- Caching strategies

## 📋 תוכנית פיתוח

**📄 קובץ מלא:** [`TO-DO.md`](TO-DO.md)

**סטטוס כללי:** 82% הושלמה
**זמן משוער להשלמה:** 4-6 שבועות

### עדיפויות קריטיות:
1. **השלמת סוכנים חסרים** (11 סוכנים)
2. **שיפור תשתית** (utils, config)
3. **תיקון בעיות API**
4. **הוספת בדיקות מקיפות**

### תיקיות עם משימות מפורטות:
- **Core:** [`core/TO-DO.md`](core/TO-DO.md) - סוכנים חסרים ותיקונים
- **Utils:** [`utils/TO-DO.md`](utils/TO-DO.md) - פונקציות עזר חסרות
- **Data:** [`data/TO-DO.md`](data/TO-DO.md) - עיבוד נתונים וגיבוי
- **Tests:** [`tests/TO-DO.md`](tests/TO-DO.md) - בדיקות מקיפות
- **Live:** [`live/TO-DO.md`](live/TO-DO.md) - הרצה וניטור
- **Config:** [`config/TO-DO.md`](config/TO-DO.md) - הגדרות ואבטחה
- **Dashboard:** [`dashboard/TO-DO.md`](dashboard/TO-DO.md) - ממשק משתמש
- **Models:** [`models/TO-DO.md`](models/TO-DO.md) - מודלי ML
- **Vectorstore:** [`vectorstore/TO-DO.md`](vectorstore/TO-DO.md) - מאגר וקטורי

## 📄 רישיון

MIT License - ראה `LICENSE` לפרטים.

---

**הערה:** מערכת זו מיועדת למטרות מחקר ולימוד בלבד. אין להשתמש בה לקבלת החלטות השקעה ללא ייעוץ מקצועי.