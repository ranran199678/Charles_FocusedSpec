"""
Charles_FocusedSpec - Core Module
מערכת חיזוי מניות פורצות - מודול ליבה

מודול זה מכיל את כל הסוכנים והמנועים הראשיים של המערכת
"""

# Base Classes
from .base.base_agent import BaseAgent
from .base.live_executable_agent import LiveExecutableAgent

# Main Engine
from .alpha_score_engine import AlphaScoreEngine

# Core Analysis Agents
from .enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
from .bullish_pattern_spotter import BullishPatternSpotter
from .valuation_detector import ValuationDetector
from .news_catalyst_agent import NewsCatalystAgent
from .sentiment_scorer import SentimentScorer
from .social_media_hype_scanner import SocialMediaHypeScanner
from .nlp_analyzer import NLPAnalyzer
from .macro_trend_scanner import MacroTrendScanner
from .event_scanner import EventScanner

# Technical Analysis Agents
from .adx_score_agent import ADXScoreAgent
from .golden_cross_detector import GoldenCrossDetector
from .bollinger_squeeze import BollingerSqueeze
from .moving_average_pressure_bot import MovingAveragePressureBot
from .gap_detector_ultimate import GapDetectorUltimate
from .breakout_retest_recognizer import BreakoutRetestRecognizer
from .support_zone_strength_detector import SupportZoneStrengthDetector
from .parabolic_agent import ParabolicAgent
from .volume_tension_meter import VolumeTensionMeter

# Advanced Analysis Agents
from .advanced_pattern_analyzer import AdvancedPatternAnalyzer
from .trend_shift_agent import TrendShiftAgent
from .profitability_metrics import ProfitabilityMetrics
from .financials_parser import FinancialsParserAgent
from .pattern_detector import PatternDetector

# Market Intelligence Agents
from .geopolitical_risk_monitor import GeopoliticalRiskMonitor
from .pump_and_dump_detector import PumpAndDumpDetector
from .ipo_volume_spike_detector import IPOVolumeSpikeDetector
from .earnings_surprise_tracker import EarningsSurpriseTracker
from .early_reversal_anticipator import EarlyReversalAnticipator
from .media_buzz_tracker import MediaBuzzTracker
from .forum_monitor import ForumMonitor
from .gpt_sentiment_model import GPTSentimentModel
from .google_trends import GoogleTrendsTracker
from .etf_flow_tracker import ETFFlowTracker
from .market_data_connector import MarketDataConnector
from .macro_event_sensitivity import MacroEventSensitivity

# Options & Derivatives
from .options_unusual_volume_agent import OptionsUnusualVolumeAgent

# Sector Analysis
from .sector_rotation_analyzer import SectorRotationAnalyzer
from .sector_momentum_agent import SectorMomentumAgent
from .relative_strength import RelativeStrengthAgent

# Short Interest & Volume
from .short_interest_spike_agent import ShortInterestSpikeAgent
from .volume_spike_agent import VolumeSpikeAgent

# Trend Analysis
from .trend_detector import TrendDetector
from .vwap_agent import VWAPAgent

# Volatility & Risk
from .volatility_score_agent import VolatilityScoreAgent
from .atr_score_agent import ATRScoreAgent

# Validation & Orchestration
from .multi_agent_validator import MultiAgentValidator
from .breakout_screener import BreakoutScreener
from .v_reversal_agent import VReversalAgent
from .midterm_momentum_agent import MidtermMomentumAgent
from .macd_momentum_detector import MACDMomentumDetector
from .high_conviction_orchestrator import HighConvictionOrchestrator

# AI & ML Models
from .anomaly_detector import AnomalyDetector
from .ml_breakout_model import MLBreakoutModel
from .ai_event_spotter import AIEventSpotter

# Dark Pool & Institutional
from .dark_pool_agent import DarkPoolAgent
from .big_money_inflow_agent import BigMoneyInflowAgent
from .liquidity_trap_agent import LiquidityTrapAgent
from .float_pressure_evaluator import FloatPressureEvaluator

# VCP Patterns
from .vcp_super_pattern_agent import VCPSuperPatternAgent

# Return Forecasting
from .return_forecaster import ReturnForecaster

# Meta Agent
from .meta_agent import MetaAgent

# Subagents
from .subagents.macd_rsi_divergence_agent import MACDRSIDivergenceAgent

# Version
__version__ = "1.0.0"
__author__ = "Charles_FocusedSpec Team"
__description__ = "מערכת חיזוי מניות פורצות מתקדמת"

# Main exports
__all__ = [
    # Base Classes
    'BaseAgent',
    'LiveExecutableAgent',
    
    # Main Engine
    'AlphaScoreEngine',
    
    # Core Analysis
    'EnhancedAdvancedAnalyzer',
    'BullishPatternSpotter',
    'ValuationDetector',
    'NewsCatalystAgent',
    'SentimentScorer',
    'SocialMediaHypeScanner',
    'NLPAnalyzer',
    'MacroTrendScanner',
    'EventScanner',
    
    # Technical Analysis
    'ADXScoreAgent',
    'GoldenCrossDetector',
    'BollingerSqueeze',
    'MovingAveragePressureBot',
    'GapDetectorUltimate',
    'BreakoutRetestRecognizer',
    'SupportZoneStrengthDetector',
    'RSISniffer',
    'ParabolicAgent',
    'VolumeTensionMeter',
    
    # Advanced Analysis
    'AdvancedPatternAnalyzer',
    'TrendShiftAgent',
    'TrendShiftDetector',
    'ProfitabilityMetrics',
    'FinancialsParserAgent',
    'PatternDetector',
    
    # Market Intelligence
    'GeopoliticalRiskMonitor',
    'PumpAndDumpDetector',
    'IPOVolumeSpikeDetector',
    'EarningsSurpriseTracker',
    'EarlyReversalAnticipator',
    'MediaBuzzTracker',
    'ForumMonitor',
    'GPTSentimentModel',
    'GoogleTrendsTracker',
    'ETFFlowTracker',
    'MarketDataConnector',
    'MacroEventSensitivity',
    
    # Options & Derivatives
    'OptionsUnusualVolumeAgent',
    
    # Sector Analysis
    'SectorRotationAnalyzer',
    'SectorMomentumAgent',
    'RelativeStrengthAgent',
    
    # Short Interest & Volume
    'ShortInterestSpikeAgent',
    'VolumeSpikeAgent',
    
    # Trend Analysis
    'TrendDetector',
    'VWAPTrendAgent',
    'VWAPAgent',
    
    # Volatility & Risk
    'VolatilityScoreAgent',
    'ATRScoreAgent',
    
    # Validation & Orchestration
    'MultiAgentValidator',
    'BreakoutScreener',
    'VReversalAgent',
    'MidtermMomentumAgent',
    'MACDMomentumDetector',
    'HighConvictionOrchestrator',
    
    # AI & ML Models
    'AnomalyDetector',
    'MLBreakoutModel',
    'AIEventSpotter',
    
    # Dark Pool & Institutional
    'DarkPoolAgent',
    'BigMoneyInflowAgent',
    'LiquidityTrapAgent',
    'FloatPressureEvaluator',
    
    # VCP Patterns
    'VCPSuperPatternAgent',
    
    # Return Forecasting
    'ReturnForecaster',
    
    # Meta Agent
    'MetaAgent',
    
    # Subagents
    'MACDRSIDivergenceAgent',
]
