# Constants for the Charles FocusedSpec system

class AGENT_NAMES:
    """שמות הסוכנים במערכת"""
    RSI_COMPRESSION = "RSISniffer"
    VOLUME_TENSION = "VolumeTensionMeter"
    PARABOLIC = "ParabolicAgent"
    BREAKOUT_RETEST = "BreakoutRetestRecognizer"
    SUPPORT_ZONE = "SupportZoneStrengthDetector"
    MOVING_AVERAGE_PRESSURE = "MovingAveragePressureBot"
    BULLISH_PATTERN = "BullishPatternSpotter"
    FLOAT_PRESSURE = "FloatPressureEvaluator"
    SHORT_SQUEEZE = "ShortSqueezePotentialAnalyzer"
    EARNINGS_SURPRISE = "EarningsSurpriseTracker"
    GROWTH_CONSISTENCY = "GrowthScanner"
    VALUATION_ANOMALY = "ValuationDetector"
    SENTIMENT = "SentimentScorer"
    GEOPOLITICAL_RISK = "GeopoliticalRiskMonitor"
    GAP_DETECTOR = "GapDetectorUltimate"
    ANALYST_RATING = "AnalystRatingAgent"
    ADX_SCORE = "ADXScoreAgent"
    NEWS_CATALYST = "NewsCatalystAgent"
    SOCIAL_MEDIA_HYPE = "SocialMediaHypeScanner"
    MACRO_TREND = "MacroTrendScanner"
    PATTERN_RECOGNITION = "PatternRecognitionAgent"
    ANOMALY_DETECTION = "AnomalyDetectionAgent"
    LIQUIDITY_TRAP = "LiquidityTrapAgent"
    BOLLINGER_SQUEEZE = "BollingerSqueeze"
    VOLUME_SPIKE = "VolumeSpikeAgent"
    GOLDEN_CROSS = "GoldenCrossDetector"
    VCP_SUPER_PATTERN = "VCPSuperPatternAgent"
    REVERSAL_PATTERN = "ReversalPatternAgent"
    FUNDAMENTAL_ANOMALY = "FundamentalAnomalyAgent"
    MARKET_REGIME = "MarketRegimeAgent"
    BIG_MONEY_INFLOW = "BigMoneyInflowAgent"
    RISK_EVENT_MONITOR = "RiskEventMonitorAgent"
    TREND_SHIFT = "TrendShiftDetector"
    CANDLESTICK = "CandlestickAgent"
    VOLUME_SURGE = "ClassicVolumeSurgeDetector"
    TREND_DETECTOR = "TrendDetector"
    V_REVERSAL = "VReversalAgent"
    RETURN_FORECASTER = "ReturnForecaster"
    MIDTERM_MOMENTUM = "MidtermMomentumAgent"
    ATR_SCORE = "ATRScoreAgent"
    ATR_VOLATILITY = "ATRVolatilityAgent"
    MULTI_AGENT_VALIDATOR = "MultiAgentValidator"
    HIGH_CONVICTION_ORCHESTRATOR = "HighConvictionOrchestrator"
    ENHANCED_ADVANCED_ANALYZER = "EnhancedAdvancedAnalyzer"
    FINANCIAL_STABILITY = "FinancialStabilityAgent"
    MACD_MOMENTUM = "MACDMomentumDetector"
    NLP_ANALYZER = "NLPAnalyzer"

# מילון שמות הסוכנים בעברית
AGENT_NAMES_HEBREW = {
    "RSISniffer": "ניתוח RSI",
    "VolumeTensionMeter": "מדידת לחץ נפח",
    "ParabolicAgent": "זיהוי תנועות פרבוליות",
    "BreakoutRetestRecognizer": "זיהוי פריצות ומבחנים",
    "SupportZoneStrengthDetector": "ניתוח אזורי תמיכה",
    "MovingAveragePressureBot": "לחץ ממוצעים נעים",
    "BullishPatternSpotter": "זיהוי תבניות בולשיות",
    "FloatPressureEvaluator": "הערכת לחץ float",
    "ShortSqueezePotentialAnalyzer": "ניתוח פוטנציאל short squeeze",
    "EarningsSurpriseTracker": "מעקב הפתעות רווחים",
    "GrowthScanner": "סריקת צמיחה",
    "ValuationDetector": "ניתוח הערכה",
    "SentimentScorer": "ניתוח סנטימנט",
    "GeopoliticalRiskMonitor": "ניטור סיכונים גיאופוליטיים",
    "GapDetectorUltimate": "זיהוי פערים מתקדם",
    "AnalystRatingAgent": "דירוג אנליסטים",
    "ADXScoreAgent": "ניתוח ADX",
    "NewsCatalystAgent": "חדשות קטליסטיות",
    "SocialMediaHypeScanner": "סריקת הייפ מדיה חברתית",
    "MacroTrendScanner": "סריקת מגמות מאקרו",
    "CandlestickAgent": "ניתוח נרות יפניים",
    "ClassicVolumeSurgeDetector": "זיהוי גלי נפח",
    "GoldenCrossDetector": "זיהוי צלב זהב",
    "BollingerSqueeze": "ניתוח התכווצות בולינגר",
    "TrendDetector": "זיהוי מגמות",
    "TrendShiftDetector": "זיהוי שינויי מגמה",
    "VReversalAgent": "זיהוי היפוכי V",
    "ReturnForecaster": "חיזוי תשואות",
    "MidtermMomentumAgent": "מומנטום בינוני",
    "ATRScoreAgent": "ניתוח ATR",
    "ATRVolatilityAgent": "ניתוח תנודתיות ATR",
    "MultiAgentValidator": "אימות רב-סוכן",
    "HighConvictionOrchestrator": "אורכיסטרטור ביטחון גבוה",
    "EnhancedAdvancedAnalyzer": "ניתוח טכני מתקדם",
    "FinancialStabilityAgent": "יציבות פיננסית",
    "MACDMomentumDetector": "ניתוח מומנטום MACD",
    "NLPAnalyzer": "ניתוח שפה טבעית"
}

# קבועי מגמות
TREND_THRESHOLDS = {
    'strong_uptrend': 0.7,
    'moderate_uptrend': 0.5,
    'weak_uptrend': 0.3,
    'neutral': 0.0,
    'weak_downtrend': -0.3,
    'moderate_downtrend': -0.5,
    'strong_downtrend': -0.7
}

# קבועי נפח מסחר
VOLUME_THRESHOLDS = {
    'low_volume': 0.5,      # נפח נמוך מ-50% מהממוצע
    'normal_volume': 1.0,   # נפח רגיל (100% מהממוצע)
    'high_volume': 2.0,     # נפח גבוה (200% מהממוצע)
    'very_high_volume': 3.0, # נפח גבוה מאוד (300% מהממוצע)
    'extreme_volume': 5.0,   # נפח קיצוני (500% מהממוצע)
    'spike_threshold': 2.5,  # סף לזיהוי קפיצה בנפח
    'surge_threshold': 4.0   # סף לזיהוי גל בנפח
}

# קבועי Dark Pool
DARK_POOL_THRESHOLDS = {
    'low_activity': 0.1,     # פעילות נמוכה (10% מהנפח)
    'normal_activity': 0.3,  # פעילות רגילה (30% מהנפח)
    'high_activity': 0.5,    # פעילות גבוהה (50% מהנפח)
    'very_high_activity': 0.7, # פעילות גבוהה מאוד (70% מהנפח)
    'extreme_activity': 0.9,  # פעילות קיצונית (90% מהנפח)
    'suspicious_threshold': 0.6, # סף לזיהוי פעילות חשודה
    'alert_threshold': 0.8    # סף להתראה
}

# קבועי Big Money
BIG_MONEY_THRESHOLDS = {
    'small_trade': 10000,     # עסקה קטנה ($10K)
    'medium_trade': 100000,   # עסקה בינונית ($100K)
    'large_trade': 1000000,   # עסקה גדולה ($1M)
    'very_large_trade': 10000000, # עסקה גדולה מאוד ($10M)
    'institutional_trade': 50000000, # עסקה מוסדית ($50M)
    'big_money_threshold': 1000000, # סף לזיהוי כסף גדול
    'institutional_threshold': 10000000 # סף לזיהוי פעילות מוסדית
}

# קבועי מלכודת נזילות
LIQUIDITY_TRAP_THRESHOLDS = {
    'low_liquidity': 0.3,     # נזילות נמוכה (30% מהממוצע)
    'normal_liquidity': 1.0,  # נזילות רגילה (100% מהממוצע)
    'high_liquidity': 2.0,    # נזילות גבוהה (200% מהממוצע)
    'trap_threshold': 0.5,    # סף לזיהוי מלכודת נזילות
    'danger_threshold': 0.2,  # סף מסוכן
    'spread_threshold': 0.05, # סף מרווח מסחר
    'volume_drop_threshold': 0.4 # סף ירידה בנפח
}

# קבועי לחץ Float
FLOAT_PRESSURE_THRESHOLDS = {
    'low_pressure': 0.3,      # לחץ נמוך (30% מהממוצע)
    'normal_pressure': 1.0,   # לחץ רגיל (100% מהממוצע)
    'high_pressure': 2.0,     # לחץ גבוה (200% מהממוצע)
    'very_high_pressure': 3.0, # לחץ גבוה מאוד (300% מהממוצע)
    'extreme_pressure': 5.0,  # לחץ קיצוני (500% מהממוצע)
    'pressure_threshold': 1.5, # סף לזיהוי לחץ
    'squeeze_threshold': 2.5  # סף לזיהוי squeeze
}

# קבועי VCP (Volatility Contraction Pattern)
VCP_THRESHOLDS = {
    'low_volatility': 0.5,    # תנודתיות נמוכה (50% מהממוצע)
    'normal_volatility': 1.0, # תנודתיות רגילה (100% מהממוצע)
    'high_volatility': 2.0,   # תנודתיות גבוהה (200% מהממוצע)
    'contraction_threshold': 0.7, # סף לכיווץ תנודתיות
    'expansion_threshold': 1.5,   # סף להתרחבות תנודתיות
    'pattern_threshold': 0.6,     # סף לזיהוי דפוס
    'breakout_threshold': 1.3     # סף לזיהוי breakout
}

# תקופות זמן
TIME_PERIODS = {
    'short_term': 5,
    'medium_term': 20,
    'long_term': 50,
    'very_long_term': 200
} 