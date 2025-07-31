#!/usr/bin/env python3
"""
דשבורד מקיף - Charles FocusedSpec
מחבר את כל המערכת: סוכנים, אלפא סקור, חדשות וניתוחים מתקדמים
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import os
import glob
import sys
import json
import asyncio
from pathlib import Path

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ייבוא מודולים מהמערכת
try:
    from core.alpha_score_engine import AlphaScoreEngine
    from core.adx_score_agent import ADXScoreAgent
    from core.rsi_sniffer import RSISniffer
    from core.bollinger_squeeze import BollingerSqueeze
    from core.macd_momentum_detector import MACDMomentumDetector
    from core.news_catalyst_agent import NewsCatalystAgent
    from core.sentiment_scorer import SentimentScorer
    from core.breakout_screener import BreakoutScreener
    from core.golden_cross_detector import GoldenCrossDetector
    from core.volume_spike_agent import VolumeSpikeAgent
    from core.social_media_hype_scanner import SocialMediaHypeScanner
    from core.trend_detector import TrendDetector
    from core.parabolic_agent import ParabolicAgent
    from core.retail_sentiment_agent import RetailSentimentAgent
    from core.big_money_inflow_agent import BigMoneyInflowAgent
    from core.dark_pool_agent import DarkPoolAgent
    from core.float_pressure_evaluator import FloatPressureEvaluator
    from core.liquidity_trap_agent import LiquidityTrapAgent
    from core.earnings_surprise_tracker import EarningsSurpriseTracker
    from core.analyst_rating_agent import AnalystRatingAgent
    from core.financial_stability_agent import FinancialStabilityAgent
    from core.growth_scanner import GrowthScanner
    from core.valuation_detector import ValuationDetector
    from core.profitability_metrics import ProfitabilityMetrics
    from core.financials_parser import FinancialsParser
    from core.return_forecaster import ReturnForecaster
    from core.midterm_momentum_agent import MidtermMomentumAgent
    from core.vwap_agent import VWAPAgent
    from core.vwap_trend_agent import VWAPTrendAgent
    from core.v_reversal_agent import VReversalAgent
    from core.breakout_retest_recognizer import BreakoutRetestRecognizer
    from core.support_zone_strength_detector import SupportZoneStrengthDetector
    from core.volume_tension_meter import VolumeTensionMeter
    from core.candlestick_agent import CandlestickAgent
    from core.atr_score_agent import ATRScoreAgent
    from core.mean_reversion_detector import MeanReversionDetector
    from core.early_reversal_anticipator import EarlyReversalAnticipator
    from core.sector_momentum_agent import SectorMomentumAgent
    from core.etf_flow_tracker import ETFFlowTracker
    from core.sector_rotation_analyzer import SectorRotationAnalyzer
    from core.insider_activity_monitor import InsiderActivityMonitor
    from core.options_unusual_volume_agent import OptionsUnusualVolumeAgent
    from core.short_interest_spike_agent import ShortInterestSpikeAgent
    from core.ai_event_spotter import AIEventSpotter
    from core.pump_and_dump_detector import PumpAndDumpDetector
    from core.ipo_volume_spike_detector import IPOVolumeSpikeDetector
    from core.macro_event_sensitivity import MacroEventSensitivity
    from core.media_buzz_tracker import MediaBuzzTracker
    from core.forum_monitor import ForumMonitor
    from core.gpt_sentiment_model import GPTSentimentModel
    from core.google_trends import GoogleTrends
    from core.anomaly_detector import AnomalyDetector
    from core.pattern_detector import PatternDetector
    from core.ml_breakout_model import MLBreakoutModel
    from core.relative_strength import RelativeStrength
    from core.trend_shift_detector import TrendShiftDetector
    from core.volatility_score_agent import VolatilityScoreAgent
    from core.gap_detector_ultimate import GapDetectorUltimate
    from core.geopolitical_risk_monitor import GeopoliticalRiskMonitor
    from core.trend_shift_agent import TrendShiftAgent
    from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
    from core.advanced_pattern_analyzer import AdvancedPatternAnalyzer
    from core.bullish_pattern_spotter import BullishPatternSpotter
    from core.moving_average_pressure_bot import MovingAveragePressureBot
    from core.macro_trend_scanner import MacroTrendScanner
    from core.market_data_connector import MarketDataConnector
    from core.event_scanner import EventScanner
    from core.meta_agent import MetaAgent
    from core.high_conviction_orchestrator import HighConvictionOrchestrator
    from core.multi_agent_validator import MultiAgentValidator
    
    # ייבוא SmartDataManager לנתונים חיים
    from utils.smart_data_manager import SmartDataManager
    
    AGENTS_AVAILABLE = True
except ImportError as e:
    st.error(f"שגיאה בייבוא מודולים: {e}")
    AGENTS_AVAILABLE = False

# הגדרת הדף
st.set_page_config(
    page_title="Charles FocusedSpec - מערכת ניתוח מתקדמת",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS מותאם
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .agent-score {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e7d32;
    }
    .warning {
        color: #f57c00;
        font-weight: bold;
    }
    .error {
        color: #d32f2f;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown('<h1 class="main-header">📈 Charles FocusedSpec - מערכת ניתוח מתקדמת</h1>', unsafe_allow_html=True)

# סרגל צד
with st.sidebar:
    st.header("⚙️ הגדרות")
    
    # בחירת מניה
    symbol = st.text_input("סימבול מניה", value="AAPL").upper()
    
    # בחירת תקופה
    days = st.slider("מספר ימים", min_value=30, max_value=365, value=90)
    
    # בחירת סוכנים
    st.subheader("🔍 סוכנים לניתוח")
    
    # סוכנים טכניים
    st.write("**סוכנים טכניים:**")
    use_adx = st.checkbox("ADX Score", value=True)
    use_rsi = st.checkbox("RSI Sniffer", value=True)
    use_bollinger = st.checkbox("Bollinger Squeeze", value=True)
    use_macd = st.checkbox("MACD Momentum", value=True)
    use_breakout = st.checkbox("Breakout Screener", value=True)
    use_golden_cross = st.checkbox("Golden Cross", value=True)
    use_volume_spike = st.checkbox("Volume Spike", value=True)
    
    # סוכני חדשות וסנטימנט
    st.write("**סוכני חדשות וסנטימנט:**")
    use_news = st.checkbox("News Catalyst", value=True)
    use_sentiment = st.checkbox("Sentiment Scorer", value=True)
    use_social = st.checkbox("Social Media Hype", value=True)
    
    # סוכנים מתקדמים
    st.write("**סוכנים מתקדמים:**")
    use_trend = st.checkbox("Trend Detector", value=True)
    use_parabolic = st.checkbox("Parabolic Agent", value=True)
    use_retail = st.checkbox("Retail Sentiment", value=True)
    use_big_money = st.checkbox("Big Money Inflow", value=True)
    use_dark_pool = st.checkbox("Dark Pool", value=True)
    
    # כפתור הרצה
    run_analysis = st.button("🚀 הרץ ניתוח מלא", type="primary")

# פונקציה לטעינת נתונים חיים
@st.cache_data(ttl=300)  # מטמון ל-5 דקות
def load_live_data(symbol: str, days: int):
    """טעינת נתונים חיים מ-SmartDataManager"""
    try:
        # יצירת SmartDataManager
        data_manager = SmartDataManager()
        
        # שליפת נתונים חיים
        st.info(f"🔄 שואב נתונים חיים עבור {symbol}...")
        
        # שליפת נתוני מחירים
        price_data = data_manager.get_stock_data(symbol, days, include_live=True)
        
        if price_data is None or price_data.empty:
            st.error(f"❌ לא הצלחתי לקבל נתונים עבור {symbol}")
            return None
        
        st.success(f"✅ נשלפו {len(price_data)} שורות נתונים עבור {symbol}")
        
        # המרת העמודות לפורמט הנדרש
        if 'close' in price_data.columns:
            price_data = price_data.rename(columns={
                'close': 'Price',
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'volume': 'Volume'
            })
        
        return price_data
        
    except Exception as e:
        st.error(f"❌ שגיאה בטעינת נתונים: {e}")
        return None

# פונקציה להרצת ניתוח סוכן
def run_agent_analysis(df, symbol, agent_type):
    """מריץ ניתוח של סוכן ספציפי עם נתונים חיים"""
    try:
        if df is None or df.empty:
            return {"score": 0, "signal": "No Data", "confidence": 0, "explanation": "אין נתונים זמינים"}
        
        # המרת העמודות לפורמט הנדרש על ידי הסוכנים
        agent_df = df.copy()
        if 'Price' in agent_df.columns:
            agent_df = agent_df.rename(columns={
                'Price': 'close',
                'Open': 'open', 
                'High': 'high',
                'Low': 'low',
                'Volume': 'volume'
            })
        
        # יצירת הסוכן והרצת הניתוח
        if agent_type == "ADX":
            agent = ADXScoreAgent()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "RSI":
            agent = RSISniffer()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "Bollinger":
            agent = BollingerSqueeze()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "MACD":
            agent = MACDMomentumDetector()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "News":
            agent = NewsCatalystAgent()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "Sentiment":
            agent = SentimentScorer()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "Social":
            agent = SocialMediaHypeScanner()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "Breakout":
            agent = BreakoutScreener()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "GoldenCross":
            agent = GoldenCrossDetector()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "VolumeSpike":
            agent = VolumeSpikeAgent()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "Trend":
            agent = TrendDetector()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "Parabolic":
            agent = ParabolicAgent()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "Retail":
            agent = RetailSentimentAgent()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "BigMoney":
            agent = BigMoneyInflowAgent()
            return agent.analyze(symbol, agent_df)
        elif agent_type == "DarkPool":
            agent = DarkPoolAgent()
            return agent.analyze(symbol, agent_df)
        else:
            return {"score": 0, "signal": "Unknown", "confidence": 0, "explanation": "סוכן לא מוכר"}
            
    except Exception as e:
        st.error(f"❌ שגיאה בהרצת {agent_type}: {e}")
        return {"score": 0, "signal": "Error", "confidence": 0, "explanation": f"שגיאה: {e}"}

# פונקציה לחישוב אלפא סקור
def calculate_alpha_score(agent_results):
    """חישוב אלפא סקור כולל"""
    try:
        # יצירת AlphaScoreEngine
        engine = AlphaScoreEngine()
        
        # הכנת נתונים לפורמט הנדרש
        agent_data = {}
        for agent_name, result in agent_results.items():
            if isinstance(result, dict) and 'score' in result:
                agent_data[agent_name] = {
                    'score': result['score'],
                    'signal': result.get('signal', 'neutral'),
                    'confidence': result.get('confidence', 0.5),
                    'explanation': result.get('explanation', '')
                }
        
        # חישוב אלפא סקור
        alpha_score = engine.calculate_alpha_score(agent_data)
        
        return alpha_score
        
    except Exception as e:
        st.error(f"❌ שגיאה בחישוב אלפא סקור: {e}")
        return {"total_score": 0, "signal": "Error", "confidence": 0, "explanation": f"שגיאה: {e}"}

# תוכן ראשי
if not AGENTS_AVAILABLE:
    st.error("❌ לא ניתן לטעון את הסוכנים. בדוק את התקנת המודולים.")
else:
    # טעינת נתונים חיים
    if run_analysis:
        with st.spinner("🔄 טוען נתונים חיים..."):
            price_df = load_live_data(symbol, days)
        
        if price_df is not None:
            # הצגת נתונים
            st.subheader(f"📊 נתוני מחירים - {symbol}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                latest_price = price_df['Price'].iloc[0] if 'Price' in price_df.columns else price_df['close'].iloc[0]
                st.metric("מחיר נוכחי", f"${latest_price:.2f}")
            
            with col2:
                price_change = price_df['Price'].iloc[0] - price_df['Price'].iloc[1] if 'Price' in price_df.columns else price_df['close'].iloc[0] - price_df['close'].iloc[1]
                st.metric("שינוי יומי", f"${price_change:.2f}")
            
            with col3:
                volume = price_df['Volume'].iloc[0] if 'Volume' in price_df.columns else price_df['volume'].iloc[0]
                st.metric("נפח", f"{volume:,.0f}")
            
            with col4:
                days_loaded = len(price_df)
                st.metric("ימים נטענו", days_loaded)
            
            # גרף מחירים
            fig = go.Figure()
            
            if 'Price' in price_df.columns:
                fig.add_trace(go.Scatter(
                    x=price_df.index,
                    y=price_df['Price'],
                    mode='lines',
                    name='מחיר',
                    line=dict(color='#1f77b4', width=2)
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=price_df.index,
                    y=price_df['close'],
                    mode='lines',
                    name='מחיר',
                    line=dict(color='#1f77b4', width=2)
                ))
            
            fig.update_layout(
                title=f"מחיר {symbol} - {days} ימים אחרונים",
                xaxis_title="תאריך",
                yaxis_title="מחיר ($)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # הרצת ניתוחים
            st.subheader("🔍 ניתוחי סוכנים")
            
            agent_results = {}
            
            # רשימת סוכנים לניתוח
            agents_to_run = []
            
            if use_adx:
                agents_to_run.append(("ADX", "ADX Score Agent"))
            if use_rsi:
                agents_to_run.append(("RSI", "RSI Sniffer"))
            if use_bollinger:
                agents_to_run.append(("Bollinger", "Bollinger Squeeze"))
            if use_macd:
                agents_to_run.append(("MACD", "MACD Momentum"))
            if use_breakout:
                agents_to_run.append(("Breakout", "Breakout Screener"))
            if use_golden_cross:
                agents_to_run.append(("GoldenCross", "Golden Cross"))
            if use_volume_spike:
                agents_to_run.append(("VolumeSpike", "Volume Spike"))
            if use_news:
                agents_to_run.append(("News", "News Catalyst"))
            if use_sentiment:
                agents_to_run.append(("Sentiment", "Sentiment Scorer"))
            if use_social:
                agents_to_run.append(("Social", "Social Media Hype"))
            if use_trend:
                agents_to_run.append(("Trend", "Trend Detector"))
            if use_parabolic:
                agents_to_run.append(("Parabolic", "Parabolic Agent"))
            if use_retail:
                agents_to_run.append(("Retail", "Retail Sentiment"))
            if use_big_money:
                agents_to_run.append(("BigMoney", "Big Money Inflow"))
            if use_dark_pool:
                agents_to_run.append(("DarkPool", "Dark Pool"))
            
            # הרצת הסוכנים
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, (agent_type, agent_name) in enumerate(agents_to_run):
                status_text.text(f"🔄 מריץ {agent_name}...")
                
                result = run_agent_analysis(price_df, symbol, agent_type)
                agent_results[agent_type] = result
                
                progress_bar.progress((i + 1) / len(agents_to_run))
            
            status_text.text("✅ הניתוח הושלם!")
            
            # הצגת תוצאות
            st.subheader("📈 תוצאות ניתוח")
            
            # חישוב אלפא סקור
            alpha_score = calculate_alpha_score(agent_results)
            
            # הצגת אלפא סקור
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_score = alpha_score.get('total_score', 0)
                st.metric("אלפא סקור", f"{total_score:.1f}/100")
            
            with col2:
                signal = alpha_score.get('signal', 'neutral')
                signal_color = 'green' if signal == 'buy' else 'red' if signal == 'sell' else 'orange'
                st.markdown(f"<div style='color: {signal_color}; font-size: 1.2rem; font-weight: bold;'>{signal.upper()}</div>", unsafe_allow_html=True)
            
            with col3:
                confidence = alpha_score.get('confidence', 0)
                st.metric("ביטחון", f"{confidence:.1%}")
            
            # הצגת תוצאות סוכנים
            st.subheader("🔍 פירוט סוכנים")
            
            # יצירת DataFrame לתוצאות
            results_data = []
            for agent_type, result in agent_results.items():
                if isinstance(result, dict):
                    results_data.append({
                        'סוכן': agent_type,
                        'ציון': result.get('score', 0),
                        'אות': result.get('signal', 'neutral'),
                        'ביטחון': result.get('confidence', 0),
                        'הסבר': result.get('explanation', '')[:100] + '...' if len(result.get('explanation', '')) > 100 else result.get('explanation', '')
                    })
            
            if results_data:
                results_df = pd.DataFrame(results_data)
                st.dataframe(results_df, use_container_width=True)
                
                # גרף ציונים
                fig = px.bar(
                    results_df,
                    x='סוכן',
                    y='ציון',
                    color='אות',
                    title="ציוני סוכנים",
                    color_discrete_map={'buy': 'green', 'sell': 'red', 'neutral': 'orange'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # הצגת הסבר מפורט
            if 'explanation' in alpha_score:
                st.subheader("📝 הסבר מפורט")
                st.write(alpha_score['explanation'])
        
        else:
            st.error("❌ לא ניתן לטעון נתונים. בדוק את החיבור לאינטרנט ואת הסימבול.")
    
    else:
        st.info("👆 לחץ על 'הרץ ניתוח מלא' כדי להתחיל")
        
        # הצגת מידע על המערכת
        st.subheader("ℹ️ מידע על המערכת")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 מקורות נתונים חיים:**
            - Yahoo Finance API
            - FMP (Financial Modeling Prep)
            - DataFetcher
            - מטמון מקומי חכם
            
            **🔍 סוכני חדשות:**
            - FMP News API
            - Alpha Vantage News
            - Yahoo Finance RSS
            - Google News RSS
            - Seeking Alpha RSS
            - Finnhub News
            - NewsData API
            """)
        
        with col2:
            st.markdown("""
            **📱 סוכני מדיה חברתית:**
            - Reddit
            - Twitter
            - Stocktwits
            - YouTube
            - Google Trends
            
            **🤖 סוכנים טכניים:**
            - ADX Score
            - RSI Sniffer
            - Bollinger Squeeze
            - MACD Momentum
            - Breakout Screener
            - Golden Cross
            - Volume Spike
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Charles FocusedSpec - מערכת ניתוח מתקדמת | נתונים חיים בזמן אמת</p>
</div>
""", unsafe_allow_html=True) 