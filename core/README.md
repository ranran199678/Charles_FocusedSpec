# Core - סוכני ניתוח מרכזיים

## 🎯 מטרת התיקייה

תיקיית `core/` מכילה את כל סוכני הניתוח של המערכת - 49 סוכנים המבצעים ניתוח טכני ופונדמנטלי מתקדם לזיהוי מניות פורצות. כל סוכן מתמחה בתחום ספציפי ומספק תובנות ייחודיות.

## 📊 סטטוס סוכנים

- **סוכנים קיימים:** 49/60 (82%)
- **סוכנים חסרים:** 11
- **סוכנים פעילים:** 49
- **סוכנים עם בעיות:** 4

## 📋 טבלת קבצים ותפקידים

| קובץ | תפקיד | תלות עיקרית | סטטוס |
|------|-------|--------------|--------|
| `alpha_score_engine.py` | מנוע ציון מרכזי | כל הסוכנים | ✅ פעיל |
| `enhanced_advanced_analyzer.py` | ניתוח טכני מתקדם | pandas, numpy | ✅ פעיל |
| `adx_score_agent.py` | מדד ADX | pandas, talib | ✅ פעיל |
| `atr_score_agent.py` | ניתוח טווח תנועה | pandas | ✅ פעיל |
| `atr_volatility_agent.py` | מדידת תנודתיות | pandas | ✅ פעיל |
| `bollinger_squeeze.py` | זיהוי Squeeze | pandas, numpy | ✅ פעיל |
| `breakout_retest_recognizer.py` | פריצה + חזרה | pandas | ✅ פעיל |
| `bullish_pattern_spotter.py` | זיהוי תבניות שוריות | pandas, talib | ⚠️ ציון נמוך |
| `candlestick_agent.py` | ניתוח נרות יפניים | pandas | ✅ פעיל |
| `gap_detector_ultimate.py` | איתור גאפים | pandas | ✅ פעיל |
| `macd_momentum_detector.py` | מומנטום MACD | pandas | ✅ פעיל |
| `moving_average_pressure_bot.py` | לחץ ממוצעים נעים | pandas | ⚠️ ציון נמוך |
| `parabolic_agent.py` | זיהוי מהלך פרבולי | pandas | ⚠️ בעיות price_df |
| `rsi_sniffer.py` | ניתוח RSI | pandas | ✅ פעיל |
| `support_zone_strength_detector.py` | חוזק תמיכה | pandas | ✅ פעיל |
| `volume_tension_meter.py` | לחץ נפח | pandas | ✅ פעיל |
| `vwap_agent.py` | ניתוח VWAP | pandas | ✅ פעיל |
| `vwap_trend_agent.py` | מגמת VWAP | pandas | ✅ פעיל |
| `trend_detector.py` | זיהוי מגמות | pandas | ✅ פעיל |
| `trend_shift_detector.py` | מעבר מגמה | pandas | ⚠️ בעיות symbol |
| `v_reversal_agent.py` | זיהוי V Reversal | pandas | ✅ פעיל |
| `volatility_score_agent.py` | מדד תנודתיות | pandas | ✅ פעיל |
| `classic_volume_surge_detector.py` | קפיצה בנפח | pandas | ✅ פעיל |
| `golden_cross_detector.py` | Golden Cross | pandas | ✅ פעיל |
| `midterm_momentum_agent.py` | מומנטום בינוני | pandas | ✅ פעיל |
| `advanced_pattern_analyzer.py` | ניתוח תבניות מתקדם | pandas, numpy | ✅ פעיל |
| `market_data_connector.py` | חיבור נתונים | requests, pandas | ✅ פעיל |
| `event_scanner.py` | סריקת אירועים | requests, pandas | ✅ פעיל |
| `nlp_analyzer.py` | ניתוח טקסט | nltk, pandas | ✅ פעיל |
| `social_media_hype_scanner.py` | הייפ ברשתות | requests, pandas | ✅ פעיל |
| `macro_trend_scanner.py` | מגמות מאקרו | pandas | ✅ פעיל |
| `valuation_detector.py` | תמחור שוק | pandas, requests | ✅ פעיל |
| `financial_stability_agent.py` | יציבות פיננסית | pandas | ✅ פעיל |
| `growth_scanner.py` | ניתוח צמיחה | pandas | ✅ פעיל |
| `analyst_rating_agent.py` | דירוגי אנליסטים | requests, pandas | ✅ פעיל |
| `earnings_surprise_tracker.py` | הפתעות בדוחות | pandas, requests | ✅ פעיל |
| `geopolitical_risk_monitor.py` | סיכונים גיאופוליטיים | requests, pandas | ✅ פעיל |
| `sentiment_scorer.py` | מדידת סנטימנט | nltk, pandas | ✅ פעיל |
| `news_catalyst_agent.py` | אירועי חדשות | requests, pandas | ✅ פעיל |
| `meta_agent.py` | סוכן-על | כל הסוכנים | ✅ פעיל |
| `high_conviction_orchestrator.py` | ניהול איתותים | pandas | ✅ פעיל |
| `multi_agent_validator.py` | הצלבת סוכנים | pandas | ✅ פעיל |
| `return_forecaster.py` | תחזית תשואה | pandas | ✅ פעיל |
| `dark_pool_agent.py` | דארק פולס | pandas, requests | ✅ פעיל |
| `retail_sentiment_agent.py` | סנטימנט ריטל | pandas | ✅ פעיל |
| `big_money_inflow_agent.py` | זרימת כסף גדול | pandas | ✅ פעיל |
| `liquidity_trap_agent.py` | מלכודת נזילות | pandas | ✅ פעיל |
| `float_pressure_evaluator.py` | לחץ פלוט | pandas | ✅ פעיל |
| `vcp_super_pattern_agent.py` | תבנית VCP | pandas | ✅ פעיל |
| `trend_shift_agent.py` | שינוי מגמה | pandas | ✅ פעיל |
| `volume_spike_agent.py` | קפיצה בנפח | pandas | ✅ פעיל |

## 🚀 דוגמאות שימוש

### הרצת סוכן בודד
```python
from core.adx_score_agent import ADXScoreAgent
from core.rsi_sniffer import RSISniffer

# ניתוח ADX
adx_agent = ADXScoreAgent()
adx_result = adx_agent.analyze('AAPL')
print(f"ADX Score: {adx_result}")

# ניתוח RSI
rsi_agent = RSISniffer()
rsi_result = rsi_agent.analyze('TSLA')
print(f"RSI Analysis: {rsi_result}")
```

### הרצת מנוע Alpha Score
```python
from core.alpha_score_engine import AlphaScoreEngine

engine = AlphaScoreEngine()
result = engine.evaluate('AAPL')
print(f"Alpha Score: {result['score']}")
print(f"Confidence: {result['confidence']}")
```

### ניתוח טכני מתקדם
```python
from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer

analyzer = EnhancedAdvancedAnalyzer()
analysis = analyzer.analyze('GOOGL')
print(f"Technical Analysis: {analysis}")
```

### הרצת מספר סוכנים
```python
from core.volume_tension_meter import VolumeTensionMeter
from core.bollinger_squeeze import BollingerSqueeze
from core.gap_detector_ultimate import GapDetectorUltimate

# ניתוח נפח
volume_agent = VolumeTensionMeter()
volume_result = volume_agent.analyze('MSFT')

# ניתוח Bollinger Squeeze
squeeze_agent = BollingerSqueeze()
squeeze_result = squeeze_agent.analyze('MSFT')

# ניתוח גאפים
gap_agent = GapDetectorUltimate()
gap_result = gap_agent.analyze('MSFT')
```

## 🔧 פקודות הפעלה

### בדיקת סוכן ספציפי
```bash
# בדיקת ADX Agent
python -c "from core.adx_score_agent import ADXScoreAgent; agent = ADXScoreAgent(); print(agent.analyze('AAPL'))"

# בדיקת RSI Sniffer
python -c "from core.rsi_sniffer import RSISniffer; agent = RSISniffer(); print(agent.analyze('TSLA'))"

# בדיקת Volume Tension Meter
python -c "from core.volume_tension_meter import VolumeTensionMeter; agent = VolumeTensionMeter(); print(agent.analyze('MSFT'))"
```

### הרצת בדיקות
```bash
# בדיקת כל הסוכנים
python -m pytest tests/ -v

# בדיקת סוכן ספציפי
python tests/test_adx_score_agent.py
python tests/test_rsi_sniffer.py
```

## 📊 אינדיקטורים נתמכים

### אינדיקטורי מגמה
- **ADX (Average Directional Index)** - `adx_score_agent.py`
- **MACD** - `macd_momentum_detector.py`
- **Moving Averages** - `moving_average_pressure_bot.py`
- **VWAP** - `vwap_agent.py`, `vwap_trend_agent.py`

### אינדיקטורי מומנטום
- **RSI (Relative Strength Index)** - `rsi_sniffer.py`
- **Stochastic** - מובנה ב-`enhanced_advanced_analyzer.py`
- **Williams %R** - מובנה ב-`enhanced_advanced_analyzer.py`
- **CCI** - מובנה ב-`enhanced_advanced_analyzer.py`

### אינדיקטורי נפח
- **Volume Tension Meter** - `volume_tension_meter.py`
- **Volume Surge Detection** - `classic_volume_surge_detector.py`
- **Volume Spike** - `volume_spike_agent.py`

### אינדיקטורי תנודתיות
- **ATR (Average True Range)** - `atr_score_agent.py`, `atr_volatility_agent.py`
- **Bollinger Bands** - `bollinger_squeeze.py`
- **Volatility Score** - `volatility_score_agent.py`

### תבניות מחירים
- **Candlestick Patterns** - `candlestick_agent.py`
- **Bullish Patterns** - `bullish_pattern_spotter.py`
- **Breakout & Retest** - `breakout_retest_recognizer.py`
- **V Reversal** - `v_reversal_agent.py`
- **Golden Cross** - `golden_cross_detector.py`

## ⚠️ בעיות ידועות

### סוכנים שדורשים תיקון
1. **`bullish_pattern_spotter.py`** - ציון נמוך
2. **`moving_average_pressure_bot.py`** - ציון נמוך
3. **`trend_shift_detector.py`** - בעיות symbol
4. **`parabolic_agent.py`** - בעיות price_df

### פתרונות מוצעים
- עדכון logics של הסוכנים
- שיפור error handling
- תיקון בעיות נתונים
- הוספת validation

## 🔄 תלויות

### תלויות פנימיות
- `base/base_agent.py` - בסיס לכל הסוכנים
- `utils/` - פונקציות עזר
- `config/` - הגדרות מערכת

### תלויות חיצוניות
- `pandas` - עיבוד נתונים
- `numpy` - חישובים מתמטיים
- `talib` - אינדיקטורים טכניים
- `requests` - קריאות API
- `nltk` - עיבוד טקסט

## 📈 ביצועים

### זמני הרצה טיפוסיים
- **סוכן בודד:** 0.1-2 שניות
- **Alpha Score Engine:** 5-10 שניות
- **Enhanced Advanced Analyzer:** 2-5 שניות
- **Multi-Agent Analysis:** 10-30 שניות

### אופטימיזציה
- Caching של תוצאות
- Parallel processing
- Database indexing
- Memory management

---

**הערה:** כל הסוכנים עוקבים אחרי ממשק אחיד ומחזירים תוצאות בפורמט סטנדרטי.