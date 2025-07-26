# Charles_FocusedSpec – תיעוד מלא ומעמיק

מערכת רב-סוכנים לחיזוי מניות פורצות (טרם הפריצה החזקה שלהם כלפי מעלה), מבוססת ניתוח רב-ממדי של נתונים שוקיים, חדשותיים, סנטימנטליים וטכניים. כוללת מנוע קונסולידציה מרכזי, אוטומציית חיזוי, תצורת הרצה חיה ומודולי ניתוח מקביליים. המערכת נועדה לאתר ולחזות מניות פורצות שיכולות להניב עשרות עד מאות אחוזי תשואה בהשקעה לטווח קצר ולהניב מאות עד אלפי אחוזי תשואה לטווח בינוני קצר.

**סטטוס נוכחי (יולי 2025):** 10/35 סוכנים פעילים (28.6% הצלחה), עם שיפורים משמעותיים לאחרונה.

---

## תוכן עניינים
- [סקירה ומבנה כללי](#סקירה-ומבנה-כללי)
- [טבלת רכיבים ותתי-מודולים](#טבלת-רכיבים-ותתי-מודולים)
- [פירוט רכיבים עיקריים](#פירוט-רכיבים-עיקריים)
- [דוגמאות שימוש (Workflows)](#דוגמאות-שימוש-workflows)
- [תצורה וקונפיגורציה](#תצורה-וקונפיגורציה)
- [פיצ'רים עתידיים ואתגרים](#פיצרים-עתידיים-ואתגרים)
- [הפניות למקורות](#הפניות-למקורות)
- [הערות והמלצות](#הערות-והמלצות)

---

## סקירה ומבנה כללי
- **חזון:** מערכת רב-סוכנים (Multi-Agent) לחיזוי, דירוג, וסינון מניות פורצות, עם שילוב ניתוח טכני, פונדמנטלי, חדשות, סנטימנט, ML, דאטה חיצוני, ואוטומציה מלאה.
- **מבנה:** עשרות סוכנים/מודולים, תתי-מודולים, מנועי חיזוי, תהליכי עיבוד מסמכים, ניהול ידע, תצורה דינמית, אינטגרציות API, תשתית טסטים, ודשבורד עתידי.
- **מקורות:** מפרטים, אפיונים, CSV, דוקומנטציה, דוגמאות שימוש – בתיקיית `project_docs/`.

### תרשים מבנה (היי-לבל)
```
Charles_FocusedSpec/
├── core/ (agents, engines, subagents)
├── charles_architect_env/ (GPT, ingest, logs, project_docs)
├── utils/ (data_fetcher, credentials, helpers)
├── config/ (config.yaml)
├── live/ (multi_agent_runner, outputs)
├── tests/ (unit/integration)
├── outputs/, models/, vectorstore/
└── project_docs/ (מפרטים, CSV, דוקומנטציה)
```

---

## טבלת רכיבים ותתי-מודולים
| רכיב/מודול/סוכן | תפקיד | קלט/פלט | תלויות | סטטוס |
|-----------------|--------|---------|--------|--------|
| **ADX Score Agent** | מדידת עוצמת מגמה | price_df → score | data_fetcher, ta.trend | ✅ פעיל |
| **RSI Sniffer** | זיהוי דחיסה וסיגנלים | price_df → score | data_fetcher, numpy | ✅ פעיל |
| **Volume Tension Meter** | מדידת מתח נפח | price_df → score | data_fetcher, ta.volume | ✅ פעיל |
| **Parabolic Agent** | זיהוי תנועות פראבוליות | price_df → score | data_fetcher, numpy | ✅ פעיל |
| **Breakout Retest Recognizer** | זיהוי פריצות ובדיקות | price_df → score | data_fetcher, ta.volatility | ✅ פעיל |
| **Support Zone Strength Detector** | ניתוח אזורי תמיכה | price_df → score | data_fetcher, ta.support_resistance | ✅ פעיל |
| **Event Scanner** | סורק אירועים (גיאופוליטי, כלכלי, רגולטורי) | feeds → signals | APIs, NLP | ✅ פעיל |
| **NLP Analyzer** | ניתוח טקסט חופשי, רגשות, ישויות | טקסט → תובנות | transformers, BERT | ✅ פעיל |
| **Macro Trend Scanner** | ניתוח מגמות מקרו-כלכליות | macro_data → score | FRED API, World Bank | ✅ פעיל |
| **Social Media Hype Scanner** | מעקב הייפ ברשתות חברתיות | social_data → score | Reddit API, Twitter | ✅ פעיל |
| **Moving Average Pressure Bot** | זיהוי לחץ ממוצעים נעים | price_df → score | data_fetcher, ta.trend | ❌ Dummy |
| **Bullish Pattern Spotter** | זיהוי תבניות בולשיות | price_df → score | data_fetcher, pattern_recognition | ❌ Dummy |
| **Float Pressure Evaluator** | הערכת לחץ צף | float_data → score | data_fetcher, calculations | ❌ Dummy |
| **Short Squeeze Potential Analyzer** | ניתוח פוטנציאל סקוויז | short_data → score | data_fetcher, calculations | ❌ Dummy |
| **Earnings Surprise Tracker** | הפתעות רווחים | earnings_data → score | fmp_api, yahoo_finance | ❌ Dummy |
| **Growth Consistency Scanner** | סריקת צמיחה עקבית | financial_data → score | fmp_api, yahoo_finance | ❌ Dummy |
| **Valuation Anomaly Detector** | אנומליות בהערכה | financial_data → score | fmp_api, yahoo_finance | ❌ Dummy |
| **Sentiment Scorer** | ניתוח סנטימנט | text_data → score | nlp_analyzer, gpt_client | ❌ Dummy |
| **Geopolitical Risk Monitor** | סיכונים גיאופוליטיים | news_feeds → score | news_api, nlp_analyzer | ❌ Dummy |
| **Gap Detector Ultimate** | זיהוי פערים מתקדם | price_df → score | data_fetcher, ta.gaps | ❌ Dummy |
| **Analyst Rating Agent** | דירוגי אנליסטים | analyst_data → score | finnhub_api, fmp_api | ❌ Dummy |
| **News Catalyst Agent** | קטליזטורים חדשותיים | news_feeds → score | news_api, nlp_analyzer | ❌ Dummy |
| **Pattern Recognition Agent** | זיהוי תבניות מתקדם | price_df → score | CNN, rule_based | ❌ Dummy |
| **Anomaly Detection Agent** | זיהוי אנומליות | price_df → anomaly | ML, Isolation Forest | ❌ Dummy |
| **Liquidity Trap Agent** | זיהוי מלכודות נזילות | liquidity_data → score | data_fetcher, calculations | ❌ Dummy |
| **Bollinger Squeeze Agent** | זיהוי דחיסה בולינגר | price_df → score | data_fetcher, ta.volatility | ❌ Dummy |
| **Volume Spike Agent** | זיהוי קפיצות נפח | price_df → score | data_fetcher, ta.volume | ❌ Dummy |
| **Golden Cross Agent** | זיהוי צלבים מוזהבים | price_df → score | data_fetcher, ta.trend | ❌ Dummy |
| **VCP Super Pattern Agent** | תבניות VCP מתקדמות | price_df → score | data_fetcher, pattern_recognition | ❌ Dummy |
| **Reversal Pattern Agent** | זיהוי תבניות היפוך | price_df → score | data_fetcher, pattern_recognition | ❌ Dummy |
| **Fundamental Anomaly Agent** | אנומליות פונדמנטליות | financial_data → score | fmp_api, calculations | ❌ Dummy |
| **Market Regime Agent** | זיהוי משטרי שוק | market_data → score | data_fetcher, calculations | ❌ Dummy |
| **Big Money Inflow Agent** | זיהוי כסף גדול | volume_data → score | data_fetcher, calculations | ❌ Dummy |
| **Risk Event Monitor Agent** | ניטור אירועי סיכון | risk_data → score | news_api, calculations | ❌ Dummy |
| **Trend Shift Agent** | זיהוי שינויי מגמה | price_df → score | data_fetcher, ta.trend | ❌ Dummy |

> **הערה:** ✅ פעיל = עובד ומחזיר ציונים אמיתיים, ❌ Dummy = עדיין לא מומש

---

## פירוט רכיבים עיקריים
### דוגמה: ADX Score Agent (core/adx_score_agent.py) ✅ פעיל
- **תפקיד:** חישוב עוצמת מגמה (ADX) לזיהוי שוק טרנדי/צדדי
- **קלט:** price_df (High, Low, Close)
- **פלט:** score (1-100), explanation, details
- **תלויות:** data_fetcher.py, ta.trend, numpy
- **שימוש:**
  ```python
  agent = ADXScoreAgent(); result = agent.analyze("AAPL", price_df)
  print(result['score'], result['explanation'])
  ```
- **סטטוס:** פעיל, עם טסטים (tests/test_adx_score_agent.py)
- **הערות:** מחזיר ציונים אמיתיים (60/100 לדוגמה)

### דוגמה: Event Scanner (core/event_scanner.py) ✅ פעיל
- **תפקיד:** סריקת אירועים חיצוניים (חדשות, רגולציה, גיאופוליטי)
- **קלט:** feeds (API, RSS, טקסט)
- **פלט:** signals, score
- **תלויות:** APIs, NLP Analyzer
- **סטטוס:** פעיל, מחזיר ציונים אמיתיים
- **הערות:** מזהה אירועים דרמטיים כמו דוחות כספיים

### דוגמה: NLP Analyzer (core/nlp_analyzer.py) ✅ פעיל
- **תפקיד:** ניתוח טקסט מתקדם, סנטימנט, ישויות
- **קלט:** טקסט, חדשות, דיווחים
- **פלט:** sentiment_score, entities, analysis
- **תלויות:** transformers, BERT, textblob
- **סטטוס:** פעיל, עם ניתוח מתקדם
- **הערות:** כולל סינון רלוונטיות וניתוח מגמות

### דוגמה: Macro Trend Scanner (core/macro_trend_scanner.py) ✅ פעיל
- **תפקיד:** ניתוח מגמות מקרו-כלכליות
- **קלט:** נתונים כלכליים (GDP, אינפלציה, ריבית)
- **פלט:** macro_score, trend_analysis
- **תלויות:** FRED API, World Bank API
- **סטטוס:** פעיל, עם נתוני דמו
- **הערות:** מנתח השפעה על סקטורים

### דוגמה: Social Media Hype Scanner (core/social_media_hype_scanner.py) ✅ פעיל
- **תפקיד:** מעקב הייפ ברשתות חברתיות
- **קלט:** נתונים מרשתות חברתיות
- **פלט:** hype_score, sentiment_analysis
- **תלויות:** Reddit API, Twitter API, Stocktwits
- **סטטוס:** פעיל, עם נתוני דמו
- **הערות:** מזהה מגמות ויראליות

---

## דוגמאות שימוש (Workflows)
### תרחיש: ניתוח מניה בודדת
1. טעינת נתונים: data_fetcher.py → price_df
2. הרצת סוכנים: core/agents (לפי config)
3. אינטגרציה: alpha_score_engine.py → overall_score
4. תוצאה: dict (score, explanation, details)

### תרחיש: עיבוד מסמכים
1. ingest_documents.py → טעינת מסמכים מ־project_docs
2. עיבוד ב־GPT (gpt_client.py)
3. שמירה ל־vectorstore

### תרחיש: הרצה חיה (Live)
1. live/multi_agent_runner.py → הרצה בלולאה
2. שמירת תוצאות ל־outputs/

---

## תצורה וקונפיגורציה
- **config/config.yaml** – משקלים עיקריים (technical, fundamental, news, sentiment)
- **utils/constants.py** – משקלי סוכנים ספציפיים
- **.env** – משתני סביבה (API keys, פרמטרים רגישים)
- **דינמיקה:** ניתן להפעיל/לכבות סוכנים, לשנות משקלים, להוסיף תלויות

---

## פיצ'רים עתידיים ואתגרים
- השלמת פיתוח רכיבים חסרים (25 סוכנים נוספים)
- פיתוח Dashboard ויזואלי (Streamlit/Plotly)
- הרחבת אינטגרציות (APIs, דאטה חיצוני, פורומים, sentiment)
- אופטימיזציה להרצה מקבילית, ניהול זיכרון, ניטור
- הרחבות: Backtesting, Portfolio Management, Risk Management
- תיעוד ודוגמאות שימוש נוספים

---

## תרשים מבנה (היי-לבל + פירוט עיקרי)
```
Charles_FocusedSpec/
├── core/
│   ├── adx_score_agent.py                # סוכן ADX (עוצמת מגמה) ✅
│   ├── rsi_sniffer.py                    # סוכן RSI ודחיסות ✅
│   ├── volume_tension_meter.py           # מדידת מתח נפח ✅
│   ├── parabolic_agent.py                # זיהוי תנועות פראבוליות ✅
│   ├── breakout_retest_recognizer.py     # זיהוי פריצות ובדיקות ✅
│   ├── support_zone_strength_detector.py # ניתוח אזורי תמיכה ✅
│   ├── event_scanner.py                  # סורק אירועים ✅
│   ├── nlp_analyzer.py                   # ניתוח טקסט מתקדם ✅
│   ├── macro_trend_scanner.py            # ניתוח מגמות מקרו ✅
│   ├── social_media_hype_scanner.py      # מעקב הייפ ברשתות ✅
│   ├── alpha_score_engine.py             # מנוע דירוג אלפא מרכזי ✅
│   ├── meta_agent.py                     # סוכן-על (ניהול) ❌
│   └── subagents/                        # תתי-סוכנים (לדוג' MACD-RSI Divergence) ❌
├── charles_architect_env/
│   ├── ingest_documents.py               # טעינת מסמכים וידע
│   ├── main.py                           # ממשק GPT אינטראקטיבי
│   ├── gpt_interface/gpt_client.py       # חיבור ל־OpenAI
│   ├── project_docs/                     # מפרטים, CSV, דוקומנטציה
│   └── ...
├── utils/
│   ├── data_fetcher.py                   # שליפת נתונים שוקיים ✅
│   ├── credentials.py                    # ניהול הרשאות/API ✅
│   └── ...
├── config/
│   └── config.yaml                       # קונפיגורציה (משקלים, פרמטרים)
├── live/
│   ├── multi_agent_runner.py             # הרצה חיה של סוכנים
│   └── outputs/                          # תוצאות ריצה חיה
├── tests/                                # בדיקות יחידה/אינטגרציה
├── outputs/, models/, vectorstore/       # תוצרים, מודלים, בסיסי נתונים
└── README.md, TODO.md, SYSTEM_ARCHITECTURE.md
```
> **הערה:** ✅ = פעיל ועובד, ❌ = עדיין לא מומש

---

## הפניות למקורות
- [system_components_summary.csv](project_docs/system_components_summary.csv) – מיפוי מלא של כל הרכיבים, תתי-מודולים, תלויות, סטטוס
- [פירוט קבצי מערכת_טרם הוקמו במערכת .csv](project_docs/פירוט%20קבצי%20מערכת_טרם%20הוקמו%20במערכת%20.csv) – רשימת רכיבים/מודולים חסרים/בתכנון
- [מערכת חיזוי מניות פורצות – מפרט טכני מפורט (1).txt](project_docs/מערכת%20חיזוי%20מניות%20פורצות%20–%20מפרט%20טכני%20מפורט%20(1).txt) – מסמך אפיון עקרוני, תרחישים, דגשים
- [project_knowledge_base.md](project_docs/project_knowledge_base.md) – ידע מרוכז, דגשים, דוגמאות
- [system_components_summary.xlsx](project_docs/system_components_summary.xlsx) – טבלת רכיבים מפורטת
- [פירוט קבצי מערכת_*.csv](project_docs/) – תיעוד רכיבים/קבצים/בדיקות/קונפיגורציה
- [מערכת רב־סוכנים לחיזוי מניות פורצות – ניתוח טכני מקיף.txt](project_docs/מערכת%20רב־סוכנים%20לחיזוי%20מניות%20פורצות%20–%20ניתוח%20טכני%20מקיף.txt) – תיעוד טכני, דגשים, דוגמאות
- [פירוט קבצי מערכת.xlsx](project_docs/פירוט%20קבצי%20מערכת.xlsx) – טבלת קבצים מלאה
- [README.md, TODO.md, SYSTEM_ARCHITECTURE.md] – תיעוד מרכזי

---

## הערות והמלצות
- יש להשלים פיתוח רכיבים חסרים, להרחיב דוקומנטציה, להוסיף דוגמאות שימוש, ולבצע בדיקות אינטגרציה
- מומלץ לעיין ב־system_components_summary.csv וב־project_knowledge_base.md לכל פיתוח/שיפור
- כל שינוי/פיתוח – לעדכן תיעוד, טסטים, ודוגמאות

---

אם יש שאלות, הערות, או דרישה להרחבה – פנו אלינו! 