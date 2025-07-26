import traceback
from utils.constants import AGENT_NAMES
from core.dummy_agent import DummyAgent

class AlphaScoreEngine:
    """
    AlphaScoreEngine גרסה סופית - כולל את כל הסוכנים המוגדרים בתוכנית, במחקר, ובקוד
    אין צורך להוסיף/להסיר קוד, רק לממש את הקובץ הספציפי של הסוכן.
    """

    AGENT_WEIGHTS = {
        AGENT_NAMES.RSI_COMPRESSION: 2,
        AGENT_NAMES.VOLUME_TENSION: 2,
        AGENT_NAMES.PARABOLIC: 1,
        AGENT_NAMES.BREAKOUT_RETEST: 1,
        AGENT_NAMES.SUPPORT_ZONE: 1,
        AGENT_NAMES.MOVING_AVERAGE_PRESSURE: 1,
        AGENT_NAMES.BULLISH_PATTERN: 2,
        AGENT_NAMES.FLOAT_PRESSURE: 1,
        AGENT_NAMES.SHORT_SQUEEZE: 2,
        AGENT_NAMES.EARNINGS_SURPRISE: 2,
        AGENT_NAMES.GROWTH_CONSISTENCY: 1,
        AGENT_NAMES.VALUATION_ANOMALY: 1,
        AGENT_NAMES.SENTIMENT: 2,
        AGENT_NAMES.GEOPOLITICAL_RISK: 1,
        AGENT_NAMES.GAP_DETECTOR: 2,
        AGENT_NAMES.ANALYST_RATING: 2,
        AGENT_NAMES.ADX_SCORE: 1,
        AGENT_NAMES.NEWS_CATALYST: 3,
        AGENT_NAMES.SOCIAL_MEDIA_HYPE: 2,
        AGENT_NAMES.MACRO_TREND: 2,
        AGENT_NAMES.PATTERN_RECOGNITION: 3,
        AGENT_NAMES.ANOMALY_DETECTION: 2,
        AGENT_NAMES.LIQUIDITY_TRAP: 2,
        AGENT_NAMES.BOLLINGER_SQUEEZE: 2,
        AGENT_NAMES.VOLUME_SPIKE: 2,
        AGENT_NAMES.GOLDEN_CROSS: 2,
        AGENT_NAMES.VCP_SUPER_PATTERN: 3,
        AGENT_NAMES.REVERSAL_PATTERN: 2,
        AGENT_NAMES.FUNDAMENTAL_ANOMALY: 2,
        AGENT_NAMES.MARKET_REGIME: 1,
        AGENT_NAMES.BIG_MONEY_INFLOW: 2,
        AGENT_NAMES.RISK_EVENT_MONITOR: 2,
        AGENT_NAMES.TREND_SHIFT: 2,
    }

    def __init__(self, config=None):
        cfg = config or {}

        def try_import(path, classname):
            try:
                module = __import__(path, fromlist=[classname])
                return getattr(module, classname)
            except Exception:
                return DummyAgent

        self.agents = {
            AGENT_NAMES.RSI_COMPRESSION: try_import('core.rsi_sniffer', 'RSICompressionSniffer')(cfg.get(AGENT_NAMES.RSI_COMPRESSION)),
            AGENT_NAMES.VOLUME_TENSION: try_import('core.volume_tension_meter', 'VolumeTensionMeter')(cfg.get(AGENT_NAMES.VOLUME_TENSION)),
            AGENT_NAMES.PARABOLIC: try_import('core.parabolic_agent', 'ParabolicAgent')(cfg.get(AGENT_NAMES.PARABOLIC)),
            AGENT_NAMES.BREAKOUT_RETEST: try_import('core.breakout_retest_recognizer', 'BreakoutRetestRecognizer')(cfg.get(AGENT_NAMES.BREAKOUT_RETEST)),
            AGENT_NAMES.SUPPORT_ZONE: try_import('core.support_zone_strength_detector', 'SupportZoneStrengthDetector')(cfg.get(AGENT_NAMES.SUPPORT_ZONE)),
            AGENT_NAMES.MOVING_AVERAGE_PRESSURE: try_import('core.moving_average_pressure_bot', 'MovingAveragePressureBot')(cfg.get(AGENT_NAMES.MOVING_AVERAGE_PRESSURE)),
            AGENT_NAMES.BULLISH_PATTERN: try_import('core.bullish_pattern_spotter', 'BullishPatternSpotter')(cfg.get(AGENT_NAMES.BULLISH_PATTERN)),
            AGENT_NAMES.FLOAT_PRESSURE: try_import('core.float_pressure_evaluator', 'FloatPressureEvaluator')(cfg.get(AGENT_NAMES.FLOAT_PRESSURE)),
            AGENT_NAMES.SHORT_SQUEEZE: try_import('core.short_squeeze_analyzer', 'ShortSqueezePotentialAnalyzer')(cfg.get(AGENT_NAMES.SHORT_SQUEEZE)),
            AGENT_NAMES.EARNINGS_SURPRISE: try_import('core.earnings_surprise_tracker', 'EarningsSurpriseTracker')(cfg.get(AGENT_NAMES.EARNINGS_SURPRISE)),
            AGENT_NAMES.GROWTH_CONSISTENCY: try_import('core.growth_scanner', 'GrowthConsistencyScanner')(cfg.get(AGENT_NAMES.GROWTH_CONSISTENCY)),
            AGENT_NAMES.VALUATION_ANOMALY: try_import('core.valuation_detector', 'ValuationAnomalyDetector')(cfg.get(AGENT_NAMES.VALUATION_ANOMALY)),
            AGENT_NAMES.SENTIMENT: try_import('core.sentiment_scorer', 'SentimentScorer')(cfg.get(AGENT_NAMES.SENTIMENT)),
            AGENT_NAMES.GEOPOLITICAL_RISK: try_import('core.geopolitical_risk_monitor', 'GeopoliticalRiskMonitor')(cfg.get(AGENT_NAMES.GEOPOLITICAL_RISK)),
            AGENT_NAMES.GAP_DETECTOR: try_import('core.gap_detector_ultimate', 'GapDetectorUltimate')(cfg.get(AGENT_NAMES.GAP_DETECTOR)),
            AGENT_NAMES.ANALYST_RATING: try_import('core.analyst_rating_agent', 'AnalystRatingAgent')(cfg.get(AGENT_NAMES.ANALYST_RATING)),
            AGENT_NAMES.ADX_SCORE: try_import('core.adx_score_agent', 'ADXScoreAgent')(cfg.get(AGENT_NAMES.ADX_SCORE)),
            AGENT_NAMES.NEWS_CATALYST: try_import('core.news_catalyst_agent', 'NewsCatalystAgent')(cfg.get(AGENT_NAMES.NEWS_CATALYST)),
            AGENT_NAMES.SOCIAL_MEDIA_HYPE: try_import('core.social_media_hype_scanner', 'SocialMediaHypeScanner')(cfg.get(AGENT_NAMES.SOCIAL_MEDIA_HYPE)),
            AGENT_NAMES.MACRO_TREND: try_import('core.macro_trend_scanner', 'MacroTrendScanner')(cfg.get(AGENT_NAMES.MACRO_TREND)),
            AGENT_NAMES.PATTERN_RECOGNITION: try_import('core.pattern_recognition_agent', 'PatternRecognitionAgent')(cfg.get(AGENT_NAMES.PATTERN_RECOGNITION)),
            AGENT_NAMES.ANOMALY_DETECTION: try_import('core.anomaly_detection_agent', 'AnomalyDetectionAgent')(cfg.get(AGENT_NAMES.ANOMALY_DETECTION)),
            AGENT_NAMES.LIQUIDITY_TRAP: try_import('core.liquidity_trap_agent', 'LiquidityTrapAgent')(cfg.get(AGENT_NAMES.LIQUIDITY_TRAP)),
            AGENT_NAMES.BOLLINGER_SQUEEZE: try_import('core.bollinger_squeeze_agent', 'BollingerSqueezeAgent')(cfg.get(AGENT_NAMES.BOLLINGER_SQUEEZE)),
            AGENT_NAMES.VOLUME_SPIKE: try_import('core.volume_spike_agent', 'VolumeSpikeAgent')(cfg.get(AGENT_NAMES.VOLUME_SPIKE)),
            AGENT_NAMES.GOLDEN_CROSS: try_import('core.golden_cross_agent', 'GoldenCrossAgent')(cfg.get(AGENT_NAMES.GOLDEN_CROSS)),
            AGENT_NAMES.VCP_SUPER_PATTERN: try_import('core.vcp_super_pattern_agent', 'VCPSuperPatternAgent')(cfg.get(AGENT_NAMES.VCP_SUPER_PATTERN)),
            AGENT_NAMES.REVERSAL_PATTERN: try_import('core.reversal_pattern_agent', 'ReversalPatternAgent')(cfg.get(AGENT_NAMES.REVERSAL_PATTERN)),
            AGENT_NAMES.FUNDAMENTAL_ANOMALY: try_import('core.fundamental_anomaly_agent', 'FundamentalAnomalyAgent')(cfg.get(AGENT_NAMES.FUNDAMENTAL_ANOMALY)),
            AGENT_NAMES.MARKET_REGIME: try_import('core.market_regime_agent', 'MarketRegimeAgent')(cfg.get(AGENT_NAMES.MARKET_REGIME)),
            AGENT_NAMES.BIG_MONEY_INFLOW: try_import('core.big_money_inflow_agent', 'BigMoneyInflowAgent')(cfg.get(AGENT_NAMES.BIG_MONEY_INFLOW)),
            AGENT_NAMES.RISK_EVENT_MONITOR: try_import('core.risk_event_monitor_agent', 'RiskEventMonitorAgent')(cfg.get(AGENT_NAMES.RISK_EVENT_MONITOR)),
            AGENT_NAMES.TREND_SHIFT: try_import('core.trend_shift_detector', 'TrendShiftDetector')(cfg.get(AGENT_NAMES.TREND_SHIFT)),
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
