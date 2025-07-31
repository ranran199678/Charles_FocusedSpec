# SYSTEM_ARCHITECTURE - ארכיטקטורת מערכת Charles FocusedSpec

## 📊 סקירה כללית

Charles FocusedSpec היא מערכת רב-סוכנים לחיזוי מניות פורצות המבוססת על ניתוח רב-ממדי של נתונים שוקיים, חדשותיים, סנטימנטליים וטכניים. המערכת כוללת מנוע קונסולידציה מרכזי, אוטומציית חיזוי, תצורת הרצה חיה ומודולי ניתוח מקביליים.

## 🏗️ ארכיטקטורה כללית

```
┌─────────────────────────────────────────────────────────────┐
│                    Charles FocusedSpec                      │
├─────────────────────────────────────────────────────────────┤
│  📊 AlphaScoreEngine (מנוע קונסולידציה מרכזי)              │
├─────────────────────────────────────────────────────────────┤
│  🔧 סוכנים מקצועיים (35 סוכנים)                            │
│  ├── סוכנים טכניים (Technical Agents)                      │
│  ├── סוכנים פונדמנטליים (Fundamental Agents)               │
│  ├── סוכנים חדשותיים (News & Sentiment Agents)             │
│  └── סוכנים מתקדמים (Advanced Agents)                      │
├─────────────────────────────────────────────────────────────┤
│  📡 DataFetcher (אחזור נתונים)                             │
│  ├── FMP API (Financial Modeling Prep)                     │
│  ├── Finnhub API                                           │
│  ├── TwelveData API                                        │
│  ├── MarketAux API                                         │
│  ├── NewsData API                                          │
│  ├── Alpha Vantage API                                     │
│  └── Yahoo Finance RSS                                     │
├─────────────────────────────────────────────────────────────┤
│  🎯 מערכת הרצה חיה (Live Execution)                        │
│  ├── Multi-Agent Runner                                    │
│  ├── Real-time Monitoring                                  │
│  └── Portfolio Management                                  │
└─────────────────────────────────────────────────────────────┘
```

## 📊 סטטוס רכיבים (יולי 2025)

### ✅ רכיבים פעילים (14/35 - 40.0%)

| רכיב | סטטוס | ציון ממוצע | תיאור | תאריך עדכון |
|------|--------|------------|-------|--------------|
| **ADXScoreAgent** | ✅ פעיל | 60/100 | ניתוח ADX (Average Directional Index) | יולי 2025 |
| **RSICompressionSniffer** | ✅ פעיל | 45/100 | זיהוי דחיסת RSI | יולי 2025 |
| **VolumeTensionMeter** | ✅ פעיל | 35/100 | מדידת מתח נפח | יולי 2025 |
| **ParabolicAgent** | ✅ פעיל | 25/100 | זיהוי תנועות פרבוליות | יולי 2025 |
| **BreakoutRetestRecognizer** | ✅ פעיל | 30/100 | זיהוי פריצות ובדיקות חוזרות | יולי 2025 |
| **SupportZoneStrengthDetector** | ✅ פעיל | 40/100 | ניתוח עוצמת אזורי תמיכה | יולי 2025 |
| **EventScanner** | ✅ פעיל | 16/100 | סריקת אירועים חיצוניים | יולי 2025 |
| **NLPAnalyzer** | ✅ פעיל | 88/100 | ניתוח שפה טבעית | יולי 2025 |
| **MacroTrendScanner** | ✅ פעיל | 65/100 | סריקת מגמות מקרו | יולי 2025 |
| **SocialMediaHypeScanner** | ✅ פעיל | 55/100 | סריקת הייפ ברשתות חברתיות | יולי 2025 |
| **MovingAveragePressureBot** | ✅ פעיל | 33/100 | ניתוח לחץ ממוצעים נעים | יולי 2025 |
| **BollingerSqueezeAgent** | ✅ פעיל | 86/100 | זיהוי התכווצות בולינגר | יולי 2025 |
| **GoldenCrossAgent** | ✅ פעיל | 51/100 | זיהוי צלבים מוזהבים וצלבי מוות | יולי 2025 |
| **BullishPatternSpotter** | ✅ פעיל | 100/100 | זיהוי תבניות בולשיות | יולי 2025 |

### ❌ רכיבים טרם מומשו (21/35 - 60.0%)

| רכיב | סטטוס | תיאור | עדיפות |
|------|--------|-------|--------|
| **GapDetectorUltimate** | ❌ שגיאה | זיהוי פערים מתקדם | גבוהה |
| **VolumeSpikeAgent** | ❌ DummyAgent | זיהוי קפיצות נפח | גבוהה |
| **TrendShiftAgent** | ❌ DummyAgent | זיהוי שינויי מגמה | בינונית |
| **ReversalPatternAgent** | ❌ DummyAgent | זיהוי תבניות היפוך | בינונית |
| **VCPSuperPatternAgent** | ❌ DummyAgent | תבניות VCP מתקדמות | בינונית |
| **PatternRecognitionAgent** | ❌ DummyAgent | זיהוי תבניות מתקדם | בינונית |
| **EarningsSurpriseTracker** | ❌ שגיאה | הפתעות רווחים | גבוהה |
| **GrowthConsistencyScanner** | ❌ שגיאה | סריקת צמיחה עקבית | בינונית |
| **ValuationAnomalyDetector** | ❌ שגיאה | אנומליות בהערכה | בינונית |
| **FundamentalAnomalyAgent** | ❌ DummyAgent | אנומליות פונדמנטליות | נמוכה |
| **AnalystRatingAgent** | ❌ DummyAgent | דירוגי אנליסטים | גבוהה |
| **NewsCatalystAgent** | ❌ שגיאה | קטליזטורים חדשותיים | גבוהה |
| **SentimentScorer** | ❌ שגיאה | ניתוח סנטימנט | גבוהה |
| **GeopoliticalRiskMonitor** | ❌ שגיאה | סיכונים גיאופוליטיים | בינונית |
| **FloatPressureEvaluator** | ❌ DummyAgent | הערכת לחץ צף | נמוכה |
| **ShortSqueezePotentialAnalyzer** | ❌ DummyAgent | ניתוח פוטנציאל סקוויז | נמוכה |
| **LiquidityTrapAgent** | ❌ DummyAgent | זיהוי מלכודות נזילות | נמוכה |
| **MarketRegimeAgent** | ❌ DummyAgent | זיהוי משטרי שוק | נמוכה |
| **BigMoneyInflowAgent** | ❌ DummyAgent | זיהוי כסף גדול | נמוכה |
| **RiskEventMonitorAgent** | ❌ DummyAgent | ניטור אירועי סיכון | נמוכה |
| **AnomalyDetectionAgent** | ❌ DummyAgent | זיהוי אנומליות | נמוכה |

## 🔧 רכיבים טכניים

### AlphaScoreEngine
- **תפקיד**: מנוע קונסולידציה מרכזי
- **קלט**: נתוני מחיר, תוצאות סוכנים
- **פלט**: ציון סופי, המלצות, הסברים
- **משקלים**: 35 סוכנים עם משקלים שונים
- **סטטוס**: ✅ פעיל

### DataFetcher
- **תפקיד**: אחזור נתונים ממקורות מרובים
- **מקורות**: FMP, Finnhub, TwelveData, MarketAux, NewsData, Alpha Vantage, Yahoo RSS
- **סוגי נתונים**: מחיר, חדשות, פיננסיים, מקרו
- **Fallback**: מנגנון גיבוי למקורות שונים
- **סטטוס**: ✅ פעיל

### סוכנים מקצועיים
- **מבנה**: יורשים מ-BaseAgent
- **ממשק**: `analyze(symbol, price_df)` -> Dict
- **פלט**: ציון, הסבר, פרטים, המלצות
- **מקבילות**: הרצה במקביל לשיפור ביצועים

## 📡 מקורות נתונים

### APIs נתמכים
| API | סטטוס | שימוש עיקרי | Rate Limit |
|-----|--------|-------------|------------|
| **FMP** | ✅ פעיל | נתוני מחיר, פיננסיים | 250/min |
| **Finnhub** | ✅ פעיל | חדשות, סנטימנט | 60/min |
| **TwelveData** | ✅ פעיל | נתוני מחיר היסטוריים | 800/day |
| **MarketAux** | ✅ פעיל | ניתוח חדשות מתקדם | 1000/day |
| **NewsData** | ✅ פעיל | חדשות גלובליות | 200/day |
| **Alpha Vantage** | ✅ פעיל | נתוני שוק וחדשות | 500/day |
| **Yahoo RSS** | ✅ פעיל | חדשות פיננסיות | ללא הגבלה |

### סוגי נתונים
- **נתוני מחיר**: OHLCV, ממוצעים נעים, אינדיקטורים טכניים
- **נתונים פיננסיים**: רווחים, הכנסות, הערכות אנליסטים
- **חדשות**: כותרות, תוכן, סנטימנט, קטגוריות
- **נתוני מקרו**: GDP, אינפלציה, ריבית, PMI
- **נתוני רשתות חברתיות**: Reddit, Twitter, Stocktwits, YouTube

## 🎯 זרימת עבודה

### 1. איסוף נתונים
```
DataFetcher.get_price_history(symbol, period)
├── FMP API (ראשי)
├── TwelveData API (גיבוי)
└── Finnhub API (גיבוי)
```

### 2. ניתוח מקביל
```
AlphaScoreEngine.evaluate(symbol, price_df)
├── סוכנים טכניים (במקביל)
├── סוכנים פונדמנטליים (במקביל)
├── סוכנים חדשותיים (במקביל)
└── סוכנים מתקדמים (במקביל)
```

### 3. קונסולידציה
```
AlphaScoreEngine
├── חישוב ציון ממוצע משוקלל
├── ניתוח הסברים
├── יצירת המלצות
└── דירוג סופי
```

### 4. פלט
```
{
    "symbol": "AAPL",
    "score": 85.5,
    "signals": {"ADXScoreAgent": 60, ...},
    "explanations": {"ADXScoreAgent": "...", ...},
    "recommendation": "🚀 BUY signal (High Conviction)"
}
```

## 🔄 מערכת הרצה חיה

### Multi-Agent Runner
- **תפקיד**: הרצת סוכנים במקביל
- **ניהול זיכרון**: אופטימיזציה לביצועים
- **Error Handling**: טיפול בשגיאות מבודד
- **Logging**: תיעוד מפורט

### Real-time Monitoring
- **ניטור רציף**: בדיקת מניות ברשימת מעקב
- **התראות**: סיגנלים חזקים
- **דוחות**: סיכומים יומיים/שבועיים

### Portfolio Management
- **ניהול סיכונים**: הגדרת stop-loss
- **אופטימיזציה**: חלוקת הון
- **תחקור**: ניתוח ביצועים

## 📊 ביצועים

### זמני הרצה
- **מניה בודדת**: 2-5 שניות
- **10 מניות**: 15-30 שניות
- **100 מניות**: 2-5 דקות

### דיוק
- **סוכנים פעילים**: 14/35 (40.0%)
- **ציון ממוצע**: 45/100
- **סיגנלים חזקים**: 15-20% מהמניות

### משאבים
- **זיכרון**: 500MB-2GB (תלוי במספר מניות)
- **CPU**: 2-4 cores מומלץ
- **רשת**: חיבור יציב לאינטרנט

## 🔧 תחזוקה ופיתוח

### עדכונים אחרונים
- **יולי 2025**: BullishPatternSpotter, GoldenCrossAgent, BollingerSqueezeAgent, MovingAveragePressureBot
- **יולי 2025**: תיקון DataFetcher לאחזור נתונים מעודכנים
- **יולי 2025**: שיפור EventScanner ו-NLPAnalyzer

### משימות קרובות
1. **תיקון שגיאות**: GapDetectorUltimate, NewsCatalystAgent
2. **פיתוח סוכנים**: VolumeSpikeAgent, EarningsSurpriseTracker
3. **שיפור ביצועים**: אופטימיזציה וקאשינג
4. **הוספת טסטים**: כיסוי מקיף

### ארכיטקטורה עתידית
- **Microservices**: פיצול לרכיבים נפרדים
- **Cloud Deployment**: הרצה בענן
- **API Gateway**: ממשק API חיצוני
- **Database**: אחסון נתונים מתקדם

---

**עדכון אחרון**: יולי 2025
**גרסה**: 1.0.0
**סטטוס**: פיתוח פעיל 