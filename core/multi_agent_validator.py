class MultiAgentCrossValidator:
    def __init__(self):
        """אתחול מודול ולידציה חוצה-סוכנים (אין פרמטרים קבועים בשלב זה)."""
        pass

    def detect_conflicts(self, signals):
        """
        בדיקת סתירות בין אותות הסוכנים.
        מקבל מילון signals {שם_סוכן: Boolean} ומחזיר True אם נמצאה סתירה משמעותית, אחרת False.
        """
        conflicts = []
        # דוגמה 1: סנטימנט שלילי (אם היה מדד כזה) מול דפוס טכני חיובי חזק.
        # (במקרה שלנו, אם אין סנטימנט חיובי כלל אבל מספר רב של אותות טכניים חיוביים)
        technical_signals = ["RSI_compression", "Volume_tension", "Breakout_retest", "Support_zone_strength", "MA_pressure", "Bullish_pattern"]
        positive_technicals = sum(1 for sig in technical_signals if signals.get(sig))
        if positive_technicals >= 3 and signals.get("Sentiment") is False:
            conflicts.append("Strong technicals but no positive sentiment")
        # דוגמה 2: אות שלילי טכני מול חיוביים אחרים (למשל Parabolic=True אבל שאר חיוביים)
        if signals.get("Parabolic_move") and positive_technicals >= 2:
            conflicts.append("Overbought technical (parabolic) vs other positive signals")
        # דוגמה 3: הייפ חברתי גבוה אבל יסודות חלשים (לדוגמה Social hype=True אבל Growth/Valuation False)
        if signals.get("Sentiment") and signals.get("Social_hype") and not signals.get("Consistent_growth") and not signals.get("Valuation_anomaly"):
            conflicts.append("High social hype but fundamentals do not support valuation")
        # דוגמה 4: סיכון גיאופוליטי קיים למרות סימנים חיוביים אחרים
        if signals.get("Geo_risk") and positive_technicals >= 2:
            conflicts.append("Geopolitical risk present despite positive signals")
        # אפשר להוסיף עוד כללים כנדרש...
        # החזרת True אם יש לפחות קונפליקט אחד
        return len(conflicts) > 0
