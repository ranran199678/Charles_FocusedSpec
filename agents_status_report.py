import os
import pandas as pd

# מילון תיאורים ותיעוד לכל מודול/קובץ עיקרי, כולל תפקיד, רמת נחיצות, מה חסר לגרסת-על
# ניתן להרחיב/לעדכן ידנית בהתאם לשינויים
MANUAL_META = {
    "core/adx_score_agent.py": {
        "Role": "חישוב עוצמת מגמה (ADX) לאיתור איתותי trend, איתור עוצמת מהלך.",
        "Necessity": "ליבה",
        "Missing_for_Pro": (
            "חסר ניתוח רב-טיימפריים, אין שילוב ADX עם אינדיקטורים משלימים (ATR, Volume, RSI), "
            "אין טריגר דינמי, חסר ניהול confidence score לאיתות חזק, אין בדיקת השפעה על סיכון, "
            "חסר threshold חכם לניהול כניסה/יציאה."
        )
    },
    "core/analyst_rating_agent.py": {
        "Role": "סקירת המלצות אנליסטים, השוואת איכות תחזיות, איתור הפתעות אנליסטים.",
        "Necessity": "עזר",
        "Missing_for_Pro": (
            "אין ניתוח קונצנזוס מתקדם, חסר סטטיסטיקת שגיאות אנליסטים, לא מחשב השפעת הפתעות על תנועה, "
            "לא מחשב איכות דירוג מול ביצוע בפועל."
        )
    },
    "core/atr_score_agent.py": {
        "Role": "חישוב ATR ובדיקת תנודתיות יחסית, איתור חריגות תזמון.",
        "Necessity": "ליבה",
        "Missing_for_Pro": (
            "מחשב ATR בלבד, לא מבצע חיתוך עם סטיית תקן/עוצמת מגמה, חסר scoring חוזק תנועה, "
            "אין שילוב עם ניהול סיכונים, לא מזהה trade setup ייחודיים לפי תנודתיות."
        )
    },
    "core/support_zone_strength_detector.py": {
        "Role": "זיהוי אזורי תמיכה/התנגדות, חישוב חוזק טכני, scoring zone.",
        "Necessity": "ליבה",
        "Missing_for_Pro": (
            "אין Order Flow Analysis, חסר volume profile מתקדם (POC, Value Area), "
            "לא מזהה פעילות שחקנים גדולים, אין scoring confidence, לא מנתח false/true breakouts סטטיסטיים, "
            "לא משקלל price action/cross-validation עם דפוסים אחרים."
        )
    },
    "core/rsi_compression_sniffer.py": {
        "Role": "איתור דחיסות/קומפרסיה ב-RSI, בדיקת קצה oversold/overbought.",
        "Necessity": "עזר",
        "Missing_for_Pro": (
            "אין ניתוח multi-timeframe, לא משלב עם ווליום/תבניות מחזור, חסר threshold דינמי, "
            "לא מנתח סף סטטיסטי למחזוריות, לא מתחשב באירועים היסטוריים."
        )
    },
    "core/volume_tension_meter.py": {
        "Role": "מדידת לחצי ווליום, חיפוש Volume Squeeze/Expansion.",
        "Necessity": "ליבה",
        "Missing_for_Pro": (
            "לא מזהה Volume Squeeze/Contraction, אין cross עם Bollinger Bands, לא בודק השפעות breakout, "
            "חסר סטטיסטיקות דינמיות."
        )
    },
    "core/breakout_retest_recognizer.py": {
        "Role": "זיהוי פריצות ומבחני retest, איתור false breakouts.",
        "Necessity": "ליבה",
        "Missing_for_Pro": (
            "מזהה רק בסיס, חסר סטטיסטיקות על retest, אין ניתוח false breakout, לא מחשב quality/סיכוי הצלחה, "
            "לא מבצע קונפיג מחקרי."
        )
    },
    "core/bullish_pattern_spotter.py": {
        "Role": "זיהוי דפוסים שוריים: cup&handle, flag, VCP.",
        "Necessity": "ליבה",
        "Missing_for_Pro": (
            "חסר דפוסים מתקדמים (VCP, Triangle, Bollinger Squeeze, Pennant), אין cross עם volume pattern, "
            "לא מחשב historical hit rate."
        )
    },
    "core/float_pressure_evaluator.py": {
        "Role": "חישוב לחץ float, איתור trigger buyback/split/short interest.",
        "Necessity": "עזר",
        "Missing_for_Pro": (
            "חסר אינטגרציה עם short interest, אין scoring pressure/עוצמה, לא מזהה טריגרים מיוחדים."
        )
    },
    "core/gap_detector_ultimate.py": {
        "Role": "איתור gap&run, ניתוח חוזק gap, סינון false gap.",
        "Necessity": "עזר",
        "Missing_for_Pro": (
            "אין ניתוח volume validation, לא מחשב עוצמת gap, לא מזהה gap&run, אין תיקוף מחקרי."
        )
    },
    "core/geopolitical_risk_monitor.py": {
        "Role": "ניתוח סיכוני גאו-פוליטיקה על ניירות ערך, בדיקת השפעות macro-events.",
        "Necessity": "עזר/נדרש",
        "Missing_for_Pro": (
            "בודק רק headline/event, אין חפיפה לאירועי שוק/סקטור, לא מבצע סימולציות השפעה."
        )
    },
    "core/moving_average_pressure_bot.py": {
        "Role": "איתור לחצי MA, cross/staking, golden/death cross.",
        "Necessity": "עזר",
        "Missing_for_Pro": (
            "לא משלב cross/stacking דינמי, חסר multi-period MA, אין חיתוך עם דפוסים אחרים."
        )
    },
    "core/pattern_recognition.py": {
        "Role": "זיהוי מתקדם של דפוסים טכניים: VCP, Golden Cross, Bollinger Squeeze, Pennant.",
        "Necessity": "ליבה",
        "Missing_for_Pro": (
            "דורש זיהוי דפוסים מורכבים, scoring, תיקוף אוטומטי מול דאטה היסטורית, "
            "אין ניהול false breakout/היטמעות מול מודולים נוספים."
        )
    },
    "core/multi_agent_validator.py": {
        "Role": "ולידציה בין מספר סוכנים, זיהוי קונפליקט/חפיפות בין איתותים.",
        "Necessity": "מערכת",
        "Missing_for_Pro": (
            "לא מבצע scoring מתואם, חסר ניתוח סינרגיות/ניגודים בין סוכנים, לא כולל ניהול קונפליקט."
        )
    },
    "core/sentiment_scorer.py": {
        "Role": "מדידת סנטימנט (חדשות, רשת, אנליסטים), ניתוח עומק השפעה.",
        "Necessity": "ליבה",
        "Missing_for_Pro": (
            "לא מחשב sentiment מרשת (Reddit, FinTwit), חסר חיבור ל־ML, אין ניתוח עומק/הצלבה מול תנועה בפועל."
        )
    },
    "core/short_squeeze_potential_analyzer.py": {
        "Role": "איתור פוטנציאל short squeeze, הצלבה מול ווליום/אירועים.",
        "Necessity": "עזר",
        "Missing_for_Pro": (
            "לא משקלל Volume/Event triggers, חסר scoring cross עם float/short interest."
        )
    },
    "core/earnings_surprise_tracker.py": {
        "Role": "ניתוח הפתעות דוחות, איתור anomalies בתגובת שוק.",
        "Necessity": "עזר",
        "Missing_for_Pro": (
            "לא מחשב רצף/חזרתיות הפתעות, לא בודק השפעת surprise על מהלך מניה, "
            "לא משווה לציפיות אנליסטים."
        )
    },
    "core/growth_scanner.py": {
        "Role": "חישוב עקביות/צמיחה, זיהוי אנומליות.",
        "Necessity": "עזר",
        "Missing_for_Pro": (
            "לא מחשב variance/trend מורכב, אין חיתוך סקטור/מאקרו, חסר scoring."
        )
    },
    "core/valuation_anomaly_detector.py": {
        "Role": "איתור חריגות שווי, השוואת PE/Growth/Innovation.",
        "Necessity": "עזר",
        "Missing_for_Pro": (
            "לא מבצע חיתוך מגזר/סקטור, חסר scoring דינמי, לא משקלל גורמי חדשנות/צמיחה."
        )
    },
    # דוגמאות נוספות לסוכנים עתידיים או קבצי מערכת:
    "core/macro_trend_scanner.py": {
        "Role": "זיהוי מגמות מאקרו (GDP, FED, PMI, CPI, אינפלציה) והשפעתן על השוק.",
        "Necessity": "נדרש (חסר)",
        "Missing_for_Pro": (
            "לא קיים בפועל. דרוש שילוב API לנתוני מאקרו, ניתוח סטטיסטי, תצוגה גרפית, חיבור למנוע התראות."
        )
    },
    "core/social_media_hype_scanner.py": {
        "Role": "מדידת הייפ/סנטימנט מרשתות (Reddit, FinTwit, Stocktwits), איתור גלי hype.",
        "Necessity": "נדרש (חסר)",
        "Missing_for_Pro": (
            "לא קיים בפועל. דורש פיתוח ML לניתוח סנטימנט, אינטגרציה לאינדקסים, איתור שינוי חריג, scoring."
        )
    },
    "dashboard/main_dashboard.py": {
        "Role": "תצוגה גרפית, דוחות, התרעות, ניהול תסריטי אוטומציה, שילוב ML.",
        "Necessity": "מערכת",
        "Missing_for_Pro": (
            "חסר מנוע התראות, אין דוחות ML, לא כולל שילוב כל סוכני הליבה, אין backtesting/real-time."
        )
    },
    # ... אפשר להמשיך ולהוסיף כל קובץ/מודול/Agent לפי הצורך.
}

# בונה רשימה של כל הקבצים במערכת (כולל תתי-תיקיות)
def collect_all_files(root="."):
    all_files = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            # מוסיף רק קבצי py, ipynb, csv, json, md, txt, וגם legacy
            if fname.endswith(('.py', '.ipynb', '.csv', '.json', '.md', '.txt')):
                rel_path = os.path.join(dirpath, fname).replace("\\", "/")
                all_files.append(rel_path)
    return all_files

def get_manual_meta(path):
    if path in MANUAL_META:
        return MANUAL_META[path]
    # קובץ עזר/דוקו/דאטה/ניסוי/תשתית:
    if path.endswith(".md") or "readme" in path.lower():
        return {"Role": "תיעוד/דוקומנטציה", "Necessity": "עזר", "Missing_for_Pro": "אין צורך בפיתוח נוסף."}
    if path.endswith(".csv") or path.endswith(".json"):
        return {"Role": "דאטה/תצוגה", "Necessity": "עזר", "Missing_for_Pro": "קובץ נתונים; לא דורש גרסת על."}
    if path.endswith(".ipynb"):
        return {"Role": "ניסוי/מחקר", "Necessity": "עזר/Deprecated", "Missing_for_Pro": "קובץ ניסוי בלבד."}
    if "legacy" in path.lower():
        return {"Role": "Deprecated/ישן", "Necessity": "Deprecated", "Missing_for_Pro": "לא נדרש, אפשר למחוק."}
    return {"Role": "קובץ אחר", "Necessity": "לא מסווג", "Missing_for_Pro": "דרוש סיווג/סקירה ידנית."}

def build_report():
    files = collect_all_files(".")
    # הוספת קבצים נדרשים שלא קיימים בפועל (מתוך מחקר/תכנית עבודה)
    needed = [
        "core/macro_trend_scanner.py",
        "core/social_media_hype_scanner.py",
        "dashboard/main_dashboard.py",
        "core/news_catalyst_agent.py",
    ]
    for k in needed:
        if k not in files:
            files.append(k)
    records = []
    for path in sorted(files):
        fname = os.path.basename(path)
        meta = get_manual_meta(path)
        agent = fname.replace(".py", "")
        records.append({
            "Agent": agent,
            "Path": path,
            "Exists": os.path.exists(path),
            "Integrated": "TRUE" if meta["Necessity"] in ["ליבה", "עזר", "מערכת"] and os.path.exists(path) else "FALSE",
            "Advanced_Version": "FALSE",  # בודק לפי המילון בלבד; תוכל לסמן TRUE ידנית אחרי שדרוג
            "Role": meta["Role"],
            "Necessity": meta["Necessity"],
            "Missing_for_Pro": meta["Missing_for_Pro"],
        })
    df = pd.DataFrame(records)
    df.to_excel("agents_system_full_report.xlsx", index=False)
    print("דוח סוכנים מלא נוצר: agents_system_full_report.xlsx")

if __name__ == "__main__":
    build_report()
