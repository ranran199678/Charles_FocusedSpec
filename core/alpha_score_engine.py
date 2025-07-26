import traceback

class DummyAgent:
    """Agent Placeholder - לסוכנים שעוד לא הוקמו"""
    def __init__(self, config=None):
        pass

    def analyze(self, symbol, price_df):
        return {
            "score": 1,
            "explanation": "Agent זה טרם מומש, יש להשלים את הקוד בעתיד.",
            "details": {},
        }

class AlphaScoreEngine:
    """
    AlphaScoreEngine גרסה סופית - כולל את כל הסוכנים המוגדרים בתוכנית, במחקר, ובקוד
    אין צורך להוסיף/להסיר קוד, רק לממש את הקובץ הספציפי של הסוכן.
    """

    AGENT_WEIGHTS = {
        "RSICompressionSniffer": 2,
        "VolumeTensionMeter": 2,
        "ParabolicAgent": 1,
        "BreakoutRetestRecognizer": 1,
        "SupportZoneStrengthDetector": 1,
        "MovingAveragePressureBot": 1,
        "BullishPatternSpotter": 2,
        "FloatPressureEvaluator": 1,
        "ShortSqueezePotentialAnalyzer": 2,
        "EarningsSurpriseTracker": 2,
        "GrowthConsistencyScanner": 1,
        "ValuationAnomalyDetector": 1,
        "SentimentScorer": 2,
        "GeopoliticalRiskMonitor": 1,
        "GapDetectorUltimate": 2,
        "AnalystRatingAgent": 2,
        "ADXScoreAgent": 1,
        "NewsCatalystAgent": 3,
        "SocialMediaHypeScanner": 2,
        "MacroTrendScanner": 2,
        "PatternRecognitionAgent": 3,
        "AnomalyDetectionAgent": 2,
        "LiquidityTrapAgent": 2,
        "BollingerSqueezeAgent": 2,
        "VolumeSpikeAgent": 2,
        "GoldenCrossAgent": 2,
        "VCPSuperPatternAgent": 3,
        "ReversalPatternAgent": 2,
        "FundamentalAnomalyAgent": 2,
        "MarketRegimeAgent": 1,
        "BigMoneyInflowAgent": 2,
        "RiskEventMonitorAgent": 2,
        "TrendShiftAgent": 2,
        "EventScanner": 3,  # הוספת Event Scanner עם משקל גבוה
        "NLPAnalyzer": 3,  # הוספת NLP Analyzer עם משקל גבוה
    }

    def __init__(self, config=None):
        cfg = config or {}

        def try_import(path, classname):
            try:
                module = __import__(path, fromlist=[classname])
                return getattr(module, classname)
            except Exception:
                return DummyAgent  # תמיד יחזור דמי עד שיהיה קובץ

        self.agents = {
            "RSICompressionSniffer": try_import('core.rsi_sniffer', 'RSICompressionSniffer')(cfg.get("RSICompressionSniffer")),
            "VolumeTensionMeter": try_import('core.volume_tension_meter', 'VolumeTensionMeter')(cfg.get("VolumeTensionMeter")),
            "ParabolicAgent": try_import('core.parabolic_agent', 'ParabolicAgent')(cfg.get("ParabolicAgent")),
            "BreakoutRetestRecognizer": try_import('core.breakout_retest_recognizer', 'BreakoutRetestRecognizer')(cfg.get("BreakoutRetestRecognizer")),
            "SupportZoneStrengthDetector": try_import('core.support_zone_strength_detector', 'SupportResistanceZoneStrengthDetector')(cfg.get("SupportZoneStrengthDetector")),
            "MovingAveragePressureBot": try_import('core.moving_average_pressure_bot', 'MovingAveragePressureBot')(cfg.get("MovingAveragePressureBot")),
            "BullishPatternSpotter": try_import('core.bullish_pattern_spotter', 'BullishPatternSpotter')(cfg.get("BullishPatternSpotter")),
            "FloatPressureEvaluator": try_import('core.float_pressure_evaluator', 'FloatPressureEvaluator')(cfg.get("FloatPressureEvaluator")),
            "ShortSqueezePotentialAnalyzer": try_import('core.short_squeeze_analyzer', 'ShortSqueezePotentialAnalyzer')(cfg.get("ShortSqueezePotentialAnalyzer")),
            "EarningsSurpriseTracker": try_import('core.earnings_surprise_tracker', 'EarningsSurpriseTracker')(cfg.get("EarningsSurpriseTracker")),
            "GrowthConsistencyScanner": try_import('core.growth_scanner', 'GrowthConsistencyScanner')(cfg.get("GrowthConsistencyScanner")),
            "ValuationAnomalyDetector": try_import('core.valuation_detector', 'ValuationAnomalyDetector')(cfg.get("ValuationAnomalyDetector")),
            "SentimentScorer": try_import('core.sentiment_scorer', 'SentimentScorer')(cfg.get("SentimentScorer")),
            "GeopoliticalRiskMonitor": try_import('core.geopolitical_risk_monitor', 'GeopoliticalRiskMonitor')(cfg.get("GeopoliticalRiskMonitor")),
            "GapDetectorUltimate": try_import('core.gap_detector_ultimate', 'GapDetectorUltimate')(cfg.get("GapDetectorUltimate")),
            "AnalystRatingAgent": try_import('core.analyst_rating_agent', 'AnalystRatingAgent')(cfg.get("AnalystRatingAgent")),
            "ADXScoreAgent": try_import('core.adx_score_agent', 'ADXScoreAgent')(cfg.get("ADXScoreAgent")),
            "NewsCatalystAgent": try_import('core.news_catalyst_agent', 'NewsCatalystAgent')(cfg.get("NewsCatalystAgent")),
            "SocialMediaHypeScanner": try_import('core.social_media_hype_scanner', 'SocialMediaHypeScanner')(cfg.get("SocialMediaHypeScanner")),
            "MacroTrendScanner": try_import('core.macro_trend_scanner', 'MacroTrendScanner')(cfg.get("MacroTrendScanner")),
            "PatternRecognitionAgent": try_import('core.pattern_recognition_agent', 'PatternRecognitionAgent')(cfg.get("PatternRecognitionAgent")),
            "AnomalyDetectionAgent": try_import('core.anomaly_detection_agent', 'AnomalyDetectionAgent')(cfg.get("AnomalyDetectionAgent")),
            "LiquidityTrapAgent": try_import('core.liquidity_trap_agent', 'LiquidityTrapAgent')(cfg.get("LiquidityTrapAgent")),
            "BollingerSqueezeAgent": try_import('core.bollinger_squeeze_agent', 'BollingerSqueezeAgent')(cfg.get("BollingerSqueezeAgent")),
            "VolumeSpikeAgent": try_import('core.volume_spike_agent', 'VolumeSpikeAgent')(cfg.get("VolumeSpikeAgent")),
            "GoldenCrossAgent": try_import('core.golden_cross_agent', 'GoldenCrossAgent')(cfg.get("GoldenCrossAgent")),
            "VCPSuperPatternAgent": try_import('core.vcp_super_pattern_agent', 'VCPSuperPatternAgent')(cfg.get("VCPSuperPatternAgent")),
            "ReversalPatternAgent": try_import('core.reversal_pattern_agent', 'ReversalPatternAgent')(cfg.get("ReversalPatternAgent")),
            "FundamentalAnomalyAgent": try_import('core.fundamental_anomaly_agent', 'FundamentalAnomalyAgent')(cfg.get("FundamentalAnomalyAgent")),
            "MarketRegimeAgent": try_import('core.market_regime_agent', 'MarketRegimeAgent')(cfg.get("MarketRegimeAgent")),
            "BigMoneyInflowAgent": try_import('core.big_money_inflow_agent', 'BigMoneyInflowAgent')(cfg.get("BigMoneyInflowAgent")),
            "RiskEventMonitorAgent": try_import('core.risk_event_monitor_agent', 'RiskEventMonitorAgent')(cfg.get("RiskEventMonitorAgent")),
            "TrendShiftAgent": try_import('core.trend_shift_agent', 'TrendShiftAgent')(cfg.get("TrendShiftAgent")),
            "EventScanner": try_import('core.event_scanner', 'EventScanner')(cfg.get("EventScanner")),  # הוספת Event Scanner
            "NLPAnalyzer": try_import('core.nlp_analyzer', 'NLPAnalyzer')(cfg.get("NLPAnalyzer")),  # הוספת NLP Analyzer
        }

    def evaluate(self, symbol, price_df):
        agent_outputs = {}
        for name, agent in self.agents.items():
            try:
                output = agent.analyze(symbol, price_df)
                score = int(output.get("score", 1))
                explanation = output.get("explanation", "")
                details = output.get("details", {})
                agent_outputs[name] = {
                    "score": score,
                    "explanation": explanation,
                    "details": details,
                }
            except Exception as e:
                agent_outputs[name] = {
                    "score": 1,
                    "explanation": f"שגיאת agent: {e}\n{traceback.format_exc()}",
                    "details": {},
                }

        total = 0
        total_weight = 0
        scores = {}
        explanations = {}
        for name, out in agent_outputs.items():
            weight = self.AGENT_WEIGHTS.get(name, 1)
            total += out["score"] * weight
            total_weight += weight
            scores[name] = out["score"]
            explanations[name] = out["explanation"]

        final_score = round(total / total_weight, 2) if total_weight else 0

        return {
            "symbol": symbol,
            "score": final_score,
            "signals": scores,
            "explanations": explanations,
            "recommendation": self.score_to_recommendation(final_score)
        }

    @staticmethod
    def score_to_recommendation(score):
        if score >= 85:
            return "🚀 BUY signal (High Conviction)"
        elif score >= 70:
            return "Strong Setup"
        elif score >= 50:
            return "Watchlist / Medium"
        elif score >= 30:
            return "Weak Signal"
        else:
            return "No Signal"
