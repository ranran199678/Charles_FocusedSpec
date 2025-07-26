# מערכת Charles_FocusedSpec - ארכיטקטורה טכנית מפורטת

## 🏗️ מבנה כללי של המערכת

```
Charles_FocusedSpec/
├── core/                    # סוכנים ומנועי ניתוח עיקריים
│   ├── base/               # מחלקות בסיס (BaseAgent, LiveExecutableAgent)
│   ├── subagents/          # סוכנים משניים (MACD-RSI Divergence)
│   ├── adx_score_agent.py  # מדידת עוצמת מגמה ✅
│   ├── rsi_sniffer.py      # זיהוי דחיסה וסיגנלים ✅
│   ├── volume_tension_meter.py # מדידת מתח נפח ✅
│   ├── parabolic_agent.py  # זיהוי תנועות פראבוליות ✅
│   ├── breakout_retest_recognizer.py # זיהוי פריצות ובדיקות ✅
│   ├── support_zone_strength_detector.py # ניתוח אזורי תמיכה ✅
│   ├── event_scanner.py    # סורק אירועים ✅
│   ├── nlp_analyzer.py     # ניתוח טקסט מתקדם ✅
│   ├── macro_trend_scanner.py # ניתוח מגמות מקרו ✅
│   ├── social_media_hype_scanner.py # מעקב הייפ ברשתות ✅
│   ├── alpha_score_engine.py # מנוע דירוג אלפא מרכזי ✅
│   ├── meta_agent.py       # סוכן-על (ניהול) ❌
│   └── [25+ agents]        # סוכנים ספציפיים נוספים (רובם ❌)
├── charles_architect_env/   # סביבת GPT וניהול ידע
│   ├── ingest_documents.py # טעינת מסמכים וידע
│   ├── main.py             # ממשק GPT אינטראקטיבי
│   ├── gpt_interface/      # חיבור ל־OpenAI
│   └── project_docs/       # מפרטים, CSV, דוקומנטציה
├── live/                   # הרצה חיה של סוכנים
│   ├── multi_agent_runner.py # הרצה חיה של סוכנים
│   └── outputs/            # תוצאות ריצה חיה
├── utils/                  # פונקציות עזר וקבועים
│   ├── data_fetcher.py     # שליפת נתונים שוקיים ✅
│   ├── credentials.py      # ניהול הרשאות/API ✅
│   └── constants.py        # קבועים ומשקלים
├── config/                 # קבצי קונפיגורציה
│   └── config.yaml         # משקלים ופרמטרים
├── tests/                  # בדיקות יחידה/אינטגרציה
├── outputs/                # תוצאות ריצה
├── models/                 # מודלים שמורים
├── vectorstore/            # בסיס נתונים וקטורי
└── project_docs/           # דוקומנטציה, מפרטים, CSV, אפיונים
```

---

## 🎯 טבלת סטטוס רכיבים מפורטת

| רכיב/מודול/סוכן | תפקיד | קלט | פלט | תלויות | סטטוס | בדיקות |
|-----------------|--------|------|------|--------|--------|---------|
| **ADX Score Agent** | מדידת עוצמת מגמה | price_df (H,L,C,V) | score (1-100), explanation | data_fetcher, ta.trend | ✅ פעיל | ✅ test_adx_score_agent.py |
| **RSI Sniffer** | זיהוי דחיסה וסיגנלים | price_df (H,L,C) | score, compression_level | data_fetcher, numpy | ✅ פעיל | ✅ test_rsi_sniffer.py |
| **Volume Tension Meter** | מדידת מתח נפח | price_df (H,L,C,V) | score, tension_level | data_fetcher, ta.volume | ✅ פעיל | ✅ test_volume_tension.py |
| **Parabolic Agent** | זיהוי תנועות פראבוליות | price_df (H,L,C,V) | score, parabolic_level | data_fetcher, numpy | ✅ פעיל | ✅ test_parabolic_agent.py |
| **Breakout Retest Recognizer** | זיהוי פריצות ובדיקות | price_df (H,L,C,V) | score, breakout_type | data_fetcher, ta.volatility | ✅ פעיל | ✅ test_breakout_retest.py |
| **Support Zone Strength Detector** | ניתוח אזורי תמיכה | price_df (H,L,C) | score, zones_list | data_fetcher, ta.support_resistance | ✅ פעיל | ✅ test_support_zone.py |
| **Event Scanner** | סורק אירועים (גיאופוליטי, כלכלי, רגולטורי) | news_feeds, events | event_signals, impact_score | news_api, nlp_analyzer | ✅ פעיל | ✅ test_event_scanner.py |
| **NLP Analyzer** | ניתוח טקסט מתקדם, סנטימנט, ישויות | text_data | sentiment_score, entities | transformers, BERT | ✅ פעיל | ✅ test_nlp_analyzer.py |
| **Macro Trend Scanner** | ניתוח מגמות מקרו-כלכליות | macro_data | macro_score, trend_analysis | FRED API, World Bank | ✅ פעיל | ✅ test_macro_trend_scanner.py |
| **Social Media Hype Scanner** | מעקב הייפ ברשתות חברתיות | social_data | hype_score, sentiment_analysis | Reddit API, Twitter | ✅ פעיל | ✅ test_social_media_hype.py |
| **MACD Momentum Detector** | זיהוי מומנטום | price_df (H,L,C) | score, momentum_type | data_fetcher, ta.trend | ❌ Dummy | ❌ חסר |
| **Bollinger Squeeze** | זיהוי דחיסה | price_df (H,L,C,V) | score, squeeze_level | data_fetcher, ta.volatility | ❌ Dummy | ❌ חסר |
| **Golden Cross Detector** | זיהוי צלבים מוזהבים | price_df (H,L,C) | score, cross_type | data_fetcher, ta.trend | ❌ Dummy | ❌ חסר |
| **Trend Shift Detector** | זיהוי שינויי מגמה | price_df (H,L,C) | score, shift_probability | data_fetcher, ta.trend | ❌ Dummy | ❌ חסר |
| **Analyst Rating Agent** | דירוגי אנליסטים | analyst_data | score, rating_change | finnhub_api, fmp_api | ❌ Dummy | ❌ חסר |
| **Earnings Surprise Tracker** | הפתעות רווחים | earnings_data | score, surprise_level | fmp_api, yahoo_finance | ❌ Dummy | ❌ חסר |
| **Growth Scanner** | סריקת צמיחה | financial_data | score, growth_metrics | fmp_api, yahoo_finance | ❌ Dummy | ❌ חסר |
| **Valuation Detector** | אנומליות בהערכה | financial_data | score, valuation_metrics | fmp_api, yahoo_finance | ❌ Dummy | ❌ חסר |
| **Financial Stability Agent** | יציבות פיננסית | financial_data | score, stability_metrics | fmp_api, yahoo_finance | ❌ Dummy | ❌ חסר |
| **News Catalyst Agent** | קטליזטורים חדשותיים | news_feeds | score, catalyst_type | news_api, nlp_analyzer | ❌ Dummy | ❌ חסר |
| **Sentiment Scorer** | ניתוח סנטימנט | text_data | score, sentiment_type | nlp_analyzer, gpt_client | ❌ Dummy | ❌ חסר |
| **Geopolitical Risk Monitor** | סיכונים גיאופוליטיים | news_feeds | score, risk_level | news_api, nlp_analyzer | ❌ Dummy | ❌ חסר |
| **Bullish Pattern Spotter** | תבניות בולשיות | price_df (H,L,C) | score, pattern_type | data_fetcher, pattern_recognition | ❌ Dummy | ❌ חסר |
| **Candlestick Agent** | תבניות נרות | price_df (H,L,C) | score, candlestick_type | data_fetcher, ta.candlestick | ❌ Dummy | ❌ חסר |
| **Gap Detector Ultimate** | זיהוי פערים | price_df (H,L,C) | score, gap_type | data_fetcher, ta.gaps | ❌ Dummy | ❌ חסר |
| **V-Reversal Agent** | תבניות V | price_df (H,L,C) | score, reversal_probability | data_fetcher, pattern_recognition | ❌ Dummy | ❌ חסר |
| **Classic Volume Surge Detector** | גלי נפח | price_df (H,L,C,V) | score, surge_level | data_fetcher, ta.volume | ❌ Dummy | ❌ חסר |
| **High Conviction Orchestrator** | אורכיסטרטור סיגנלים חזקים | agent_signals | conviction_score, signals | strong_agents, config | ❌ Dummy | ❌ חסר |
| **Multi Agent Validator** | אימות רב-סוכני | agent_results | validation_score, conflicts | all_agents, validation_logic | ❌ Dummy | ❌ חסר |
| **Meta Agent** | סוכן מטא לניהול אחרים | all_agent_results | meta_score, orchestration | all_agents, meta_logic | ❌ Dummy | ❌ חסר |
| **Moving Average Pressure Bot** | זיהוי לחץ ממוצעים נעים | price_df (H,L,C) | score, pressure_level | data_fetcher, ta.trend | ❌ Dummy | ❌ חסר |
| **Float Pressure Evaluator** | הערכת לחץ צף | float_data | score, pressure_metrics | data_fetcher, calculations | ❌ Dummy | ❌ חסר |
| **Short Squeeze Potential Analyzer** | ניתוח פוטנציאל סקוויז | short_data | score, squeeze_potential | data_fetcher, calculations | ❌ Dummy | ❌ חסר |
| **Growth Consistency Scanner** | סריקת צמיחה עקבית | financial_data | score, consistency_metrics | fmp_api, yahoo_finance | ❌ Dummy | ❌ חסר |
| **Valuation Anomaly Detector** | אנומליות בהערכה | financial_data | score, anomaly_metrics | fmp_api, yahoo_finance | ❌ Dummy | ❌ חסר |
| **Pattern Recognition Agent** | זיהוי תבניות מתקדם | price_df (H,L,C) | score, pattern_type | CNN, rule_based | ❌ Dummy | ❌ חסר |
| **Anomaly Detection Agent** | זיהוי אנומליות | price_df, volume_data | anomaly_score, anomaly_type | ML, Isolation Forest | ❌ Dummy | ❌ חסר |
| **Liquidity Trap Agent** | זיהוי מלכודות נזילות | liquidity_data | score, trap_metrics | data_fetcher, calculations | ❌ Dummy | ❌ חסר |
| **Bollinger Squeeze Agent** | זיהוי דחיסה בולינגר | price_df (H,L,C,V) | score, squeeze_level | data_fetcher, ta.volatility | ❌ Dummy | ❌ חסר |
| **Volume Spike Agent** | זיהוי קפיצות נפח | price_df (H,L,C,V) | score, spike_level | data_fetcher, ta.volume | ❌ Dummy | ❌ חסר |
| **Golden Cross Agent** | זיהוי צלבים מוזהבים | price_df (H,L,C) | score, cross_type | data_fetcher, ta.trend | ❌ Dummy | ❌ חסר |
| **VCP Super Pattern Agent** | תבניות VCP מתקדמות | price_df (H,L,C) | score, vcp_pattern | data_fetcher, pattern_recognition | ❌ Dummy | ❌ חסר |
| **Reversal Pattern Agent** | זיהוי תבניות היפוך | price_df (H,L,C) | score, reversal_type | data_fetcher, pattern_recognition | ❌ Dummy | ❌ חסר |
| **Fundamental Anomaly Agent** | אנומליות פונדמנטליות | financial_data | score, anomaly_metrics | fmp_api, calculations | ❌ Dummy | ❌ חסר |
| **Market Regime Agent** | זיהוי משטרי שוק | market_data | score, regime_type | data_fetcher, calculations | ❌ Dummy | ❌ חסר |
| **Big Money Inflow Agent** | זיהוי כסף גדול | volume_data | score, inflow_metrics | data_fetcher, calculations | ❌ Dummy | ❌ חסר |
| **Risk Event Monitor Agent** | ניטור אירועי סיכון | risk_data | score, risk_level | news_api, calculations | ❌ Dummy | ❌ חסר |
| **Trend Shift Agent** | זיהוי שינויי מגמה | price_df (H,L,C) | score, shift_type | data_fetcher, ta.trend | ❌ Dummy | ❌ חסר |
| **Dashboard / Web UI** | ממשק משתמש מתקדם | all_scores, data | visual_dashboard | Streamlit, Plotly | ❌ חסר | ❌ לא קיים |

**סיכום:** ✅ 10 סוכנים פעילים, ❌ 25 סוכנים עדיין Dummy (28.6% הצלחה)

---

## 🔄 זרימת עבודה מפורטת (Workflow)

### תרחיש 1: ניתוח מניה בודדת
```
1. איסוף נתונים
   ├── data_fetcher.py → price_df (H,L,C,V) ✅
   ├── finnhub_utils.py → analyst_data ❌
   ├── fmp_utils.py → financial_data ❌
   └── news_api → news_feeds ✅

2. הרצת סוכנים (מקביל)
   ├── Technical Agents (ADX ✅, RSI ✅, Volume Tension ✅, Parabolic ✅, Breakout ✅, Support ✅)
   ├── News/Sentiment Agents (Event Scanner ✅, NLP Analyzer ✅, Social Media ✅)
   ├── Macro Agents (Macro Trend ✅)
   └── Pattern Agents (רובם ❌)

3. אינטגרציה וסינתזה
   ├── alpha_score_engine.py → overall_score ✅
   ├── meta_agent.py → meta_score ❌
   └── high_conviction_orchestrator.py → conviction_score ❌

4. תוצאה סופית
   └── dict: {symbol, overall_score, recommendation, agent_scores, timestamp} ✅
```

### תרחיש 2: עיבוד מסמכים וידע
```
1. טעינת מסמכים
   ├── ingest_documents.py → project_docs/ ✅
   ├── document_loader.py → PDF, TXT, CSV ✅
   └── gpt_client.py → OpenAI processing ✅

2. עיבוד וקטוריזציה
   ├── vectorstore/ → embeddings ✅
   └── memory_log.py → knowledge base ✅

3. שאילתות וידע
   └── query_engine.py → intelligent responses ✅
```

### תרחיש 3: הרצה חיה (Live)
```
1. הגדרת פרמטרים
   ├── symbol = "AAPL"
   ├── interval = "1d"
   └── delay = 300 (seconds)

2. הרצה חוזרת
   ├── multi_agent_runner.py → loop ✅
   ├── agent_runner.py → single agent ✅
   └── save_live_output() → JSON files ✅

3. ניטור ותוצאות
   └── live/outputs/ → timestamped results ✅
```

---

## 🎛️ ניהול קונפיגורציה מפורט

### config/config.yaml
```yaml
weights:
  technical: 0.4       # סוכנים טכניים (6/10 פעילים)
  fundamental: 0.2     # סוכנים פונדמנטליים (0/10 פעילים)
  news: 0.2            # סוכנים מבוססי חדשות (3/5 פעילים)
  sentiment: 0.2       # סוכני סנטימנט (1/3 פעילים)

thresholds:
  minimum_score: 7.0   # ציון מינימלי להמלצה
  conviction_threshold: 8.5  # סף לסיגנלים חזקים
```

### utils/constants.py
```python
AGENT_WEIGHTS = {
    'ADXScoreAgent': 0.8,           # ✅ פעיל
    'RSISniffer': 0.7,              # ✅ פעיל
    'VolumeTensionMeter': 0.9,      # ✅ פעיל
    'ParabolicAgent': 0.6,          # ✅ פעיל
    'BreakoutRetestRecognizer': 0.7, # ✅ פעיל
    'SupportZoneStrengthDetector': 0.8, # ✅ פעיל
    'EventScanner': 0.9,            # ✅ פעיל
    'NLPAnalyzer': 0.9,             # ✅ פעיל
    'MacroTrendScanner': 0.8,       # ✅ פעיל
    'SocialMediaHypeScanner': 0.7,  # ✅ פעיל
    # ... ועוד (רובם Dummy)
}
```

### .env
```env
OPENAI_API_KEY=your_openai_api_key
FINNHUB_API_KEY=your_finnhub_api_key
FMP_API_KEY=your_fmp_api_key
```

---

## 📊 מבנה נתונים מפורט

### תוצאות סוכן בודד
```python
{
    'score': 60,                     # ציון 1-100 (אמיתי)
    'explanation': 'ADX בינוני (23.91) - יתכן טרנד מתפתח. המגמה עולה (+1.75)',
    'details': {
        'latest_adx': 23.91,
        'prev_adx': 22.16,
        'adx_trend': 'עולה',
        'adx_change': 1.75,
        'timeframe': 'daily'
    },
    'timestamp': '2025-01-24T10:30:00Z'
}
```

### תוצאה סופית (Alpha Score Engine)
```python
{
    'symbol': 'AAPL',
    'overall_score': 13.57,         # ציון משולב (עדיין נמוך בגלל Dummy agents)
    'recommendation': 'No Signal',
    'agent_scores': {
        'ADXScoreAgent': 60,         # ✅ פעיל
        'RSISniffer': 20,            # ✅ פעיל
        'VolumeTensionMeter': 40,    # ✅ פעיל
        'ParabolicAgent': 20,        # ✅ פעיל
        'BreakoutRetestRecognizer': 10, # ✅ פעיל
        'SupportZoneStrengthDetector': 31, # ✅ פעיל
        'EventScanner': 12,          # ✅ פעיל
        'NLPAnalyzer': 80,           # ✅ פעיל
        'MacroTrendScanner': 71,     # ✅ פעיל
        'SocialMediaHypeScanner': 88, # ✅ פעיל
        # ... ועוד (רובם 1 - Dummy)
    },
    'conviction_level': 'LOW',       # עדיין נמוך בגלל Dummy agents
    'timestamp': '2025-01-24T10:30:00Z',
    'details': {
        'technical_score': 8.3,      # רק הסוכנים הפעילים
        'fundamental_score': 1.0,    # כולם Dummy
        'news_score': 8.1,           # חלקם פעילים
        'sentiment_score': 8.0       # חלקם פעילים
    }
}
```

---

## 🚀 מצבי הרצה מפורטים

### מצב אינטראקטיבי (charles_architect_env/main.py)
```python
# דוגמת שימוש
from charles_architect_env.main import main_menu

# תפריט ראשי
main_menu()
# 1. Send custom prompt to GPT
# 2. Show memory
# 3. Clear memory
# 4. Exit
```

### מצב לייב (live/multi_agent_runner.py)
```python
# דוגמת שימוש
from live.multi_agent_runner import run_agent_live

# הרצה חיה
run_agent_live("AAPL", "1d", 300)
# - מחזיר תוצאות כל 5 דקות
# - שומר ל־live/outputs/
```

### מצב בדיקות (tests/)
```bash
# הרצת כל הבדיקות
pytest

# בדיקה ספציפית
pytest tests/test_adx_score_agent.py

# בדיקת אינטגרציה
pytest tests/test_alpha_score_engine.py
```

---

## 🧩 פיצ'רים עתידיים ואתגרים מפורטים

### רכיבים חסרים (לפי system_components_summary.csv)
- **25 סוכנים נוספים** – דורשים פיתוח מלא
- **Dashboard** – דורש Streamlit, Plotly, web UI
- **Backtesting** – מערכת backtesting
- **Portfolio Management** – ניהול תיק השקעות
- **Risk Management** – ניהול סיכונים
- **Broker Integration** – אינטגרציה לברוקרים
- **News APIs** – הוספת מקורות חדשות נוספים
- **Social Media APIs** – הוספת מקורות רשתות חברתיות
- **Economic Data** – הוספת נתונים כלכליים
- **Machine Learning** – הוספת מודלים של למידת מכונה
- **AutoML** – למידת מכונה אוטומטית
- **Reinforcement Learning** – למידה חיזוקית
- **Natural Language Processing** – שיפור עיבוד שפה טבעית
- **Computer Vision** – הוספת זיהוי תמונות

### אתגרים טכניים
- **ביצועים** – הרצה מקבילית של סוכנים, ניהול זיכרון
- **אינטגרציה** – חיבור APIs מרובים, ניהול שגיאות
- **דיוק** – שיפור אלגוריתמים, בדיקות מקיפות
- **סקלביליות** – תמיכה במניות רבות, עיבוד מקבילי

### הרחבות עתידיות
- **Backtesting** – בדיקת ביצועים היסטוריים
- **Portfolio Management** – ניהול תיק השקעות
- **Risk Management** – ניהול סיכונים
- **Machine Learning** – מודלים מתקדמים
- **Cloud Deployment** – פריסה בענן
- **Microservices** – ארכיטקטורה מבוזרת

---

## 📁 דוקומנטציה ומקורות מפורטים

### קבצי מפרט ואפיון
- [system_components_summary.csv](project_docs/system_components_summary.csv) – מיפוי מלא של כל הרכיבים
- [פירוט קבצי מערכת_טרם הוקמו במערכת .csv](project_docs/פירוט%20קבצי%20מערכת_טרם%20הוקמו%20במערכת%20.csv) – רשימת רכיבים חסרים
- [מערכת חיזוי מניות פורצות – מפרט טכני מפורט (1).txt](project_docs/מערכת%20חיזוי%20מניות%20פורצות%20–%20מפרט%20טכני%20מפורט%20(1).txt) – מסמך אפיון עקרוני
- [מערכת רב־סוכנים לחיזוי מניות פורצות – ניתוח טכני מקיף.txt](project_docs/מערכת%20רב־סוכנים%20לחיזוי%20מניות%20פורצות%20–%20ניתוח%20טכני%20מקיף.txt) – תיעוד טכני מפורט

### קבצי תיעוד רכיבים
- [project_knowledge_base.md](project_docs/project_knowledge_base.md) – ידע מרוכז ודגשים
- [system_components_summary.xlsx](project_docs/system_components_summary.xlsx) – טבלת רכיבים מפורטת
- [פירוט קבצי מערכת.xlsx](project_docs/פירוט%20קבצי%20מערכת.xlsx) – טבלת קבצים מלאה

### קבצי תיעוד ספציפיים
- [פירוט קבצי מערכת_*.csv](project_docs/) – תיעוד רכיבים/קבצים/בדיקות/קונפיגורציה
- [סוכני_המערכת_המלאים (9).xlsx](project_docs/סוכני_המערכת_המלאים%20(9).xlsx) – מיפוי סוכנים מלא

---

## 🔧 דוגמאות קוד ושימוש

### הרצת סוכן בודד
```python
from core.adx_score_agent import ADXScoreAgent
from utils.data_fetcher import DataFetcher

# טעינת נתונים
fetcher = DataFetcher()
price_df = fetcher.get_price_history("AAPL", "100d")

# הרצת סוכן
agent = ADXScoreAgent()
result = agent.analyze("AAPL", price_df)
print(f"Score: {result['score']}, Explanation: {result['explanation']}")
```

### הרצת מנוע אלפא
```python
from core.alpha_score_engine import AlphaScoreEngine

# הרצת מנוע
engine = AlphaScoreEngine()
result = engine.evaluate("AAPL", price_df)
print(f"Overall Score: {result['score']}")
print(f"Recommendation: {result['recommendation']}")
```

### הרצה חיה
```python
from live.multi_agent_runner import run_agent_live

# הרצה חיה
run_agent_live("AAPL", "1d", 300)  # symbol, interval, delay
```

---

*עודכן לפי הצלבת מצב בפועל מול מפרטים ותכנון עתידי (יולי 2025)* 