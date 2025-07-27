# Charles FocusedSpec - מערכת רב-סוכנים לחיזוי מניות פורצות

מערכת רב-סוכנים לחיזוי מניות פורצות (טרם הפריצה החזקה שלהם כלפי מעלה), מבוססת ניתוח רב-ממדי של נתונים שוקיים, חדשותיים, סנטימנטליים וטכניים. כוללת מנוע קונסולידציה מרכזי, אוטומציית חיזוי, תצורת הרצה חיה ומודולי ניתוח מקביליים. המערכת נועדה לאתר ולחזות מניות פורצות שיכולות להניב עשרות עד מאות אחוזי תשואה בהשקעה לטווח קצר ולהניב מאות עד אלפי אחוזי תשואה לטווח בינוני קצר.

## 📊 סטטוס נוכחי (יולי 2025)

### ✅ סוכנים פעילים (14/35 - 40.0%)
1. **ADXScoreAgent** - ציון: 60/100 ✅
2. **RSICompressionSniffer** - ציון: 45/100 ✅
3. **VolumeTensionMeter** - ציון: 35/100 ✅
4. **ParabolicAgent** - ציון: 25/100 ✅
5. **BreakoutRetestRecognizer** - ציון: 30/100 ✅
6. **SupportZoneStrengthDetector** - ציון: 40/100 ✅
7. **EventScanner** - ציון: 16/100 ✅
8. **NLPAnalyzer** - ציון: 88/100 ✅
9. **MacroTrendScanner** - ציון: 65/100 ✅
10. **SocialMediaHypeScanner** - ציון: 55/100 ✅
11. **MovingAveragePressureBot** - ציון: 33/100 ✅
12. **BollingerSqueezeAgent** - ציון: 86/100 ✅
13. **GoldenCrossAgent** - ציון: 51/100 ✅
14. **BullishPatternSpotter** - ציון: 100/100 ✅

### ❌ סוכנים טרם מומשו (21/35 - 60.0%)
- FloatPressureEvaluator, ShortSqueezePotentialAnalyzer, EarningsSurpriseTracker, GrowthConsistencyScanner, ValuationAnomalyDetector, SentimentScorer, GeopoliticalRiskMonitor, GapDetectorUltimate, AnalystRatingAgent, NewsCatalystAgent, PatternRecognitionAgent, AnomalyDetectionAgent, LiquidityTrapAgent, VolumeSpikeAgent, VCPSuperPatternAgent, ReversalPatternAgent, FundamentalAnomalyAgent, MarketRegimeAgent, BigMoneyInflowAgent, RiskEventMonitorAgent, TrendShiftAgent

## 🚀 התקנה והרצה

### דרישות מערכת
- Python 3.8+
- pip
- API keys למקורות נתונים

### התקנה
```bash
# Clone הפרויקט
git clone <repository-url>
cd Charles_FocusedSpec

# התקנת תלויות
pip install -r requirements.txt

# הגדרת משתני סביבה
cp env.example.txt .env
# ערוך את .env והוסף את מפתחות ה-API שלך
```

### הרצה
```bash
# הרצת AlphaScoreEngine
python example_run.py

# הרצת סוכן ספציפי
python test_single_stock.py

# הרצת טסטים
python -m pytest tests/
```

## 📁 מבנה הפרויקט

```
Charles_FocusedSpec/
├── core/                    # סוכנים מרכזיים
│   ├── alpha_score_engine.py    # מנוע קונסולידציה מרכזי
│   ├── adx_score_agent.py       # ניתוח ADX
│   ├── rsi_sniffer.py           # ניתוח RSI
│   ├── volume_tension_meter.py  # מדידת מתח נפח
│   ├── parabolic_agent.py       # זיהוי תנועות פרבוליות
│   ├── breakout_retest_recognizer.py  # זיהוי פריצות
│   ├── support_zone_strength_detector.py  # ניתוח אזורי תמיכה
│   ├── moving_average_pressure_bot.py  # ניתוח לחץ ממוצעים נעים
│   ├── bollinger_squeeze.py     # זיהוי התכווצות בולינגר
│   ├── golden_cross_detector.py # זיהוי צלבים מוזהבים
│   ├── bullish_pattern_spotter.py  # זיהוי תבניות בולשיות
│   ├── event_scanner.py         # סריקת אירועים
│   ├── nlp_analyzer.py          # ניתוח שפה טבעית
│   ├── macro_trend_scanner.py   # סריקת מגמות מקרו
│   ├── social_media_hype_scanner.py  # סריקת הייפ ברשתות
│   └── base/                   # מחלקות בסיס
├── utils/                   # כלים עזר
│   ├── data_fetcher.py      # אחזור נתונים
│   ├── constants.py         # קבועים
│   └── credentials.py       # ניהול הרשאות
├── tests/                   # טסטים
├── live/                    # הרצה חיה
├── outputs/                 # פלטים
├── config/                  # הגדרות
├── requirements.txt         # תלויות
├── README.md               # תיעוד ראשי
├── SYSTEM_ARCHITECTURE.md  # ארכיטקטורת מערכת
└── TODO.md                 # רשימת משימות
```

## 🔧 מקורות נתונים

### APIs נתמכים
- **FMP (Financial Modeling Prep)** - נתוני מחיר, פיננסיים, חדשות
- **Finnhub** - נתוני שוק, חדשות, סנטימנט
- **TwelveData** - נתוני מחיר היסטוריים
- **MarketAux** - ניתוח חדשות מתקדם
- **NewsData** - חדשות גלובליות
- **Alpha Vantage** - נתוני שוק וחדשות
- **Yahoo Finance RSS** - חדשות פיננסיות

### סוגי נתונים
- **נתוני מחיר**: OHLCV, ממוצעים נעים, אינדיקטורים טכניים
- **נתונים פיננסיים**: רווחים, הכנסות, הערכות אנליסטים
- **חדשות**: כותרות, תוכן, סנטימנט, קטגוריות
- **נתוני מקרו**: GDP, אינפלציה, ריבית, PMI
- **נתוני רשתות חברתיות**: Reddit, Twitter, Stocktwits, YouTube

## 📈 ארכיטקטורת מערכת

### רכיבים מרכזיים
1. **AlphaScoreEngine** - מנוע קונסולידציה מרכזי
2. **DataFetcher** - אחזור נתונים ממקורות מרובים
3. **סוכנים מקצועיים** - ניתוח ספציפי לכל תחום
4. **מערכת הרצה חיה** - ניטור רציף בזמן אמת

### זרימת עבודה
1. **איסוף נתונים** - אחזור נתונים ממקורות מרובים
2. **ניתוח מקביל** - הרצת סוכנים במקביל
3. **קונסולידציה** - שילוב תוצאות הסוכנים
4. **המלצות** - יצירת המלצות מסחר

## 🎯 שימוש

### ניתוח מניה בודדת
```python
from core.alpha_score_engine import AlphaScoreEngine
from utils.data_fetcher import DataFetcher

# יצירת מנוע
engine = AlphaScoreEngine()
data_fetcher = DataFetcher()

# קבלת נתונים
price_df = data_fetcher.get_price_history("AAPL", period="1y")

# ניתוח
result = engine.evaluate("AAPL", price_df)
print(f"ציון: {result['score']}/100")
print(f"המלצה: {result['recommendation']}")
```

### ניתוח מספר מניות
```python
symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
results = {}

for symbol in symbols:
    price_df = data_fetcher.get_price_history(symbol, period="1y")
    results[symbol] = engine.evaluate(symbol, price_df)

# מיון לפי ציון
sorted_results = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)
```

## 📊 דוגמאות תוצאות

### מניה עם פוטנציאל גבוה
```
AAPL - ציון: 85/100
המלצה: 🚀 BUY signal (High Conviction)
סוכנים פעילים: 14/35
זמן ניתוח: 2.3 שניות
```

### מניה עם סיגנל חלש
```
INTC - ציון: 23/100
המלצה: No Signal
סוכנים פעילים: 14/35
זמן ניתוח: 1.8 שניות
```

## 🔄 עדכונים אחרונים

### יולי 2025
- ✅ **BullishPatternSpotter** - זיהוי תבניות בולשיות (Hammer, Doji, Engulfing, Morning Star)
- ✅ **GoldenCrossAgent** - זיהוי צלבים מוזהבים וצלבי מוות
- ✅ **BollingerSqueezeAgent** - זיהוי התכווצות בולינגר
- ✅ **MovingAveragePressureBot** - ניתוח לחץ ממוצעים נעים
- ✅ **DataFetcher** - תיקון אחזור נתונים מעודכנים
- ✅ **EventScanner** - הוספת קטגוריית 'financial'
- ✅ **NLPAnalyzer** - שיפור סינון חדשות וניתוח מתקדם

## 📞 תמיכה

לשאלות ותמיכה:
- פתח Issue ב-GitHub
- צור קשר עם הצוות
- בדוק את התיעוד ב-`SYSTEM_ARCHITECTURE.md`

## 📄 רישיון

MIT License - ראה קובץ LICENSE לפרטים.

---

**הערה**: מערכת זו מיועדת למטרות מחקר ולימוד בלבד. אין להשתמש בה כעצה פיננסית או השקעתית. 