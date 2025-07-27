from core.multi_agent_validator import MultiAgentValidator

class HighConvictionOrchestrator:
    def __init__(self, config=None):
        """אתחול האורקסטרטור עם מודול הולידציה לחצייה."""
        self.config = config or {}
        self.validator = MultiAgentValidator()

    def decide(self, analysis_result):
        """
        קבלת החלטה לגבי Conviction גבוה.
        analysis_result - מילון התוצאה ממנוע הניקוד (המכיל "score", "signals", "recommendation").
        מחזיר True אם האיתות נחשב בעל ביטחון גבוה, False אם לא.
        """
        score = analysis_result["score"]
        signals = analysis_result["signals"]
        recommendation = analysis_result["recommendation"]
        # תחילה, בדוק אם המערכת המליצה על HIGH conviction על סמך ציון
        high_score_flag = (score >= 4 and "HIGH" in recommendation)
        if not high_score_flag:
            return False  # אם גם ככה לא סווג כ-High במנוע, ודאי לא נסמן ככזה
        # אם כן, נבדוק אם יש סתירות מהותיות בין הסיגנלים או סיכונים:
        conflict = self.validator.detect_conflicts(signals)
        if conflict:
            # אם יש קונפליקט משמעותי, לא נגדיר כביטחון גבוה
            return False
        # בנוסף, אם יש סיכון גיאופוליטי פעיל, נזהר:
        if signals.get("Geo_risk"):
            return False
        # אם עבר את כל הבדיקות - זה אות בעל ביטחון גבוה באמת
        return True
