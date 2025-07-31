#!/usr/bin/env python3
"""
דשבורד מקיף - Charles FocusedSpec
מערכת רב-סוכנים לחיזוי מניות פורצות
מחבר את כל המערכת: סוכנים, אלפא סקור, נתונים חיים וניתוחים מתקדמים
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import os
import sys
import json
import asyncio
from pathlib import Path
import time
import threading
from typing import Dict, List, Optional, Tuple

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ייבוא מודולים מהמערכת
try:
    from core.alpha_score_engine import AlphaScoreEngine
    from utils.smart_data_manager import SmartDataManager
    from utils.data_fetcher import DataFetcher
    from utils.logger import setup_logger
    
    # ייבוא סוכנים ספציפיים
    from core.adx_score_agent import ADXScoreAgent
    from core.rsi_sniffer import RSISniffer
    from core.bollinger_squeeze import BollingerSqueeze
    from core.macd_momentum_detector import MACDMomentumDetector
    from core.news_catalyst_agent import NewsCatalystAgent
    from core.sentiment_scorer import SentimentScorer
    from core.golden_cross_detector import GoldenCrossDetector
    from core.volume_spike_agent import VolumeSpikeAgent
    from core.enhanced_advanced_analyzer import EnhancedAdvancedAnalyzer
    from core.bullish_pattern_spotter import BullishPatternSpotter
    from core.valuation_detector import ValuationDetector
    from core.financial_stability_agent import FinancialStabilityAgent
    from core.social_media_hype_scanner import SocialMediaHypeScanner
    from core.nlp_analyzer import NLPAnalyzer
    from core.earnings_surprise_tracker import EarningsSurpriseTracker
    from core.analyst_rating_agent import AnalystRatingAgent
    from core.geopolitical_risk_monitor import GeopoliticalRiskMonitor
    from core.gap_detector_ultimate import GapDetectorUltimate
    from core.candlestick_agent import CandlestickAgent
    from core.trend_detector import TrendDetector
    from core.trend_shift_detector import TrendShiftDetector
    from core.v_reversal_agent import VReversalAgent
    from core.parabolic_agent import ParabolicAgent
    from core.return_forecaster import ReturnForecaster
    from core.growth_scanner import GrowthScanner
    from core.midterm_momentum_agent import MidtermMomentumAgent
    from core.moving_average_pressure_bot import MovingAveragePressureBot
    from core.atr_score_agent import ATRScoreAgent
    from core.multi_agent_validator import MultiAgentValidator
    from core.high_conviction_orchestrator import HighConvictionOrchestrator
    from core.breakout_retest_recognizer import BreakoutRetestRecognizer
    from core.support_zone_strength_detector import SupportZoneStrengthDetector
    
    SYSTEM_AVAILABLE = True
    st.success("✅ כל המודולים נטענו בהצלחה!")
except ImportError as e:
    st.error(f"❌ שגיאה בטעינת מודולים: {str(e)}")
    SYSTEM_AVAILABLE = False

# הגדרת דף
st.set_page_config(
    page_title="Charles FocusedSpec - מערכת רב-סוכנים לחיזוי מניות פורצות",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS מותאם אישית
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f2f6 0%, #e6e9f0 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .agent-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #e9ecef;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .info-metric {
        border-left-color: #17a2b8;
    }
    .live-indicator {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# אתחול מערכות
@st.cache_resource
def initialize_systems():
    """אתחול המערכות הראשיות"""
    try:
        # אתחול מנהל הנתונים
        data_manager = SmartDataManager()
        
        # אתחול מנוע האלפא סקור
        alpha_engine = AlphaScoreEngine()
        
        # אתחול לוגר
        logger = setup_logger()
        
        return data_manager, alpha_engine, logger
    except Exception as e:
        st.error(f"שגיאה באתחול המערכות: {e}")
        return None, None, None

# קבלת רשימת מניות זמינות
@st.cache_data(ttl=300)  # רענון כל 5 דקות
def get_available_stocks():
    """קבלת רשימת מניות זמינות"""
    try:
        # בדיקת תיקיית הנתונים
        data_dir = Path("data/raw_price_data")
        if data_dir.exists():
            csv_files = list(data_dir.glob("*.csv"))
            symbols = [f.stem.replace(" Stock Price History", "") for f in csv_files]
            return sorted(symbols)
        
        # אם אין נתונים מקומיים, נחזיר רשימה בסיסית
        return ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN", "META", "NFLX"]
    except Exception as e:
        st.error(f"שגיאה בקבלת רשימת מניות: {e}")
        return ["AAPL", "GOOGL", "MSFT"]

# טעינת נתוני מניה
def load_stock_data(symbol: str, days: int = 90, include_live: bool = True):
    """טעינת נתוני מניה עם תמיכה בנתונים חיים"""
    try:
        data_manager, _, _ = initialize_systems()
        if data_manager:
            return data_manager.get_stock_data(symbol, days, include_live)
        return None
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים עבור {symbol}: {e}")
        return None

# הרצת ניתוח סוכן
def run_agent_analysis(df: pd.DataFrame, symbol: str, agent_type: str):
    """הרצת ניתוח של סוכן ספציפי"""
    try:
        if df is None or df.empty:
            return None
        
        # יצירת אובייקט הסוכן
        agent_map = {
            "ADX": ADXScoreAgent,
            "RSI": RSISniffer,
            "Bollinger": BollingerSqueeze,
            "MACD": MACDMomentumDetector,
            "News": NewsCatalystAgent,
            "Sentiment": SentimentScorer,
            "GoldenCross": GoldenCrossDetector,
            "Volume": VolumeSpikeAgent,
            "Enhanced": EnhancedAdvancedAnalyzer,
            "Pattern": BullishPatternSpotter,
            "Valuation": ValuationDetector,
            "Financial": FinancialStabilityAgent,
            "Social": SocialMediaHypeScanner,
            "NLP": NLPAnalyzer,
            "Earnings": EarningsSurpriseTracker,
            "Analyst": AnalystRatingAgent,
            "Geopolitical": GeopoliticalRiskMonitor,
            "Gap": GapDetectorUltimate,
            "Candlestick": CandlestickAgent,
            "Trend": TrendDetector,
            "TrendShift": TrendShiftDetector,
            "VReversal": VReversalAgent,
            "Parabolic": ParabolicAgent,
            "Return": ReturnForecaster,
            "Growth": GrowthScanner,
            "Momentum": MidtermMomentumAgent,
            "MAPressure": MovingAveragePressureBot,
            "ATR": ATRScoreAgent,
            "Validator": MultiAgentValidator,
            "Orchestrator": HighConvictionOrchestrator,
            "Breakout": BreakoutRetestRecognizer,
            "Support": SupportZoneStrengthDetector
        }
        
        if agent_type in agent_map:
            agent = agent_map[agent_type]()
            result = agent.analyze(df, symbol)
            return result
        
        return None
    except Exception as e:
        st.error(f"שגיאה בהרצת סוכן {agent_type}: {e}")
        return None

# חישוב אלפא סקור
def calculate_alpha_score(df: pd.DataFrame, symbol: str):
    """חישוב אלפא סקור מלא"""
    try:
        _, alpha_engine, _ = initialize_systems()
        if alpha_engine and df is not None:
            result = alpha_engine.evaluate(symbol, df)
            return result
        return None
    except Exception as e:
        st.error(f"שגיאה בחישוב אלפא סקור: {e}")
        return None

# יצירת גרף מתקדם
def create_advanced_chart(df: pd.DataFrame, symbol: str, alpha_result: dict = None):
    """יצירת גרף מתקדם עם אינדיקטורים"""
    if df is None or df.empty:
        return None
    
    try:
        # יצירת subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('מחיר ונפח', 'RSI', 'MACD', 'Bollinger Bands'),
            row_heights=[0.4, 0.2, 0.2, 0.2]
        )
        
        # גרף מחיר ונפח
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='מחיר',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )
        
        # נפח
        colors = ['red' if close < open else 'green' for close, open in zip(df['Close'], df['Open'])]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='נפח',
                marker_color=colors,
                opacity=0.6
            ),
            row=1, col=1
        )
        
        # ממוצעים נעים
        if 'SMA_20' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['SMA_20'],
                    name='SMA 20',
                    line=dict(color='blue', width=1)
                ),
                row=1, col=1
            )
        
        if 'SMA_50' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['SMA_50'],
                    name='SMA 50',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
        
        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    name='RSI',
                    line=dict(color='purple', width=2)
                ),
                row=2, col=1
            )
            
            # קווים של 30 ו-70
            fig.add_hline(y=30, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        
        # MACD
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD'],
                    name='MACD',
                    line=dict(color='blue', width=2)
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD_Signal'],
                    name='Signal',
                    line=dict(color='red', width=2)
                ),
                row=3, col=1
            )
            
            # MACD Histogram
            if 'MACD_Histogram' in df.columns:
                colors = ['green' if x >= 0 else 'red' for x in df['MACD_Histogram']]
                fig.add_trace(
                    go.Bar(
                        x=df.index,
                        y=df['MACD_Histogram'],
                        name='MACD Histogram',
                        marker_color=colors,
                        opacity=0.6
                    ),
                    row=3, col=1
                )
        
        # Bollinger Bands
        if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_Upper'],
                    name='BB Upper',
                    line=dict(color='gray', width=1, dash='dash'),
                    fill=None
                ),
                row=4, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_Lower'],
                    name='BB Lower',
                    line=dict(color='gray', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(128,128,128,0.1)'
                ),
                row=4, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    name='מחיר',
                    line=dict(color='black', width=1)
                ),
                row=4, col=1
            )
        
        # עדכון layout
        fig.update_layout(
            title=f'ניתוח טכני מתקדם - {symbol}',
            xaxis_title='תאריך',
            yaxis_title='מחיר',
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        # עדכון צירים
        fig.update_xaxes(title_text="תאריך", row=4, col=1)
        fig.update_yaxes(title_text="מחיר", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="Bollinger", row=4, col=1)
        
        return fig
    except Exception as e:
        st.error(f"שגיאה ביצירת גרף: {e}")
        return None

# יצירת דשבורד סוכן
def create_agent_dashboard(symbol: str, df: pd.DataFrame):
    """יצירת דשבורד מפורט לכל סוכן"""
    if df is None or df.empty:
        st.warning("אין נתונים זמינים לניתוח")
        return
    
    # רשימת הסוכנים הזמינים
    agents = {
        "ADX": "ניתוח מגמות",
        "RSI": "ניתוח RSI",
        "Bollinger": "ניתוח Bollinger Bands",
        "MACD": "ניתוח MACD",
        "News": "ניתוח חדשות",
        "Sentiment": "ניתוח סנטימנט",
        "GoldenCross": "זיהוי צלב זהב",
        "Volume": "ניתוח נפח",
        "Enhanced": "ניתוח מתקדם",
        "Pattern": "זיהוי תבניות",
        "Valuation": "הערכה",
        "Financial": "יציבות פיננסית",
        "Social": "מדיה חברתית",
        "NLP": "ניתוח NLP",
        "Earnings": "הפתעות רווחים",
        "Analyst": "דירוג אנליסטים",
        "Geopolitical": "סיכונים גיאופוליטיים",
        "Gap": "זיהוי פערים",
        "Candlestick": "ניתוח נרות",
        "Trend": "זיהוי מגמות",
        "TrendShift": "שינויי מגמה",
        "VReversal": "היפוכי V",
        "Parabolic": "תנועות פרבוליות",
        "Return": "חיזוי תשואות",
        "Growth": "סריקת צמיחה",
        "Momentum": "מומנטום",
        "MAPressure": "לחץ ממוצעים נעים",
        "ATR": "ניתוח ATR",
        "Validator": "אימות רב-סוכן",
        "Orchestrator": "אורכיסטרטור",
        "Breakout": "זיהוי פריצות",
        "Support": "אזורי תמיכה"
    }
    
    # יצירת tabs לכל סוכן
    tabs = st.tabs(list(agents.values()))
    
    for i, (agent_key, agent_name) in enumerate(agents.items()):
        with tabs[i]:
            st.subheader(f"🔍 {agent_name} - {symbol}")
            
            # הרצת הניתוח
            with st.spinner(f"מנתח {agent_name}..."):
                result = run_agent_analysis(df, symbol, agent_key)
            
            if result:
                # הצגת התוצאות
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**תוצאות הניתוח:**")
                    st.json(result)
                
                with col2:
                    # הצגת מדדים עיקריים
                    if 'score' in result:
                        score = result['score']
                        if score > 70:
                            st.metric("ציון", f"{score:.1f}", "מצוין", delta_color="normal")
                        elif score > 50:
                            st.metric("ציון", f"{score:.1f}", "טוב", delta_color="normal")
                        else:
                            st.metric("ציון", f"{score:.1f}", "נמוך", delta_color="inverse")
                    
                    if 'signal' in result:
                        signal = result['signal']
                        if signal == 'BUY':
                            st.success("📈 אות קנייה")
                        elif signal == 'SELL':
                            st.error("📉 אות מכירה")
                        else:
                            st.info("⏸️ המתנה")
            else:
                st.warning(f"לא ניתן להריץ ניתוח {agent_name}")

# פונקציה ראשית
def main():
    # כותרת ראשית
    st.markdown('<h1 class="main-header">🚀 Charles FocusedSpec</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #666;">מערכת רב-סוכנים לחיזוי מניות פורצות</h2>', unsafe_allow_html=True)
    
    # בדיקת זמינות המערכת
    if not SYSTEM_AVAILABLE:
        st.error("❌ המערכת לא זמינה. אנא בדוק את התקנת המודולים.")
        return
    
    # סיידבר
    st.sidebar.header("⚙️ הגדרות")
    
    # בחירת מניה
    available_stocks = get_available_stocks()
    symbol = st.sidebar.selectbox("בחר מניה", available_stocks, index=0)
    
    # הגדרות נוספות
    days = st.sidebar.slider("מספר ימים", min_value=30, max_value=365, value=90)
    include_live = st.sidebar.checkbox("כלול נתונים חיים", value=True)
    
    # כפתור רענון
    if st.sidebar.button("🔄 רענן נתונים"):
        st.cache_data.clear()
        st.rerun()
    
    # מצב לייב
    if include_live:
        st.sidebar.markdown('<div class="live-indicator">📡 מצב לייב פעיל</div>', unsafe_allow_html=True)
    
    # טעינת נתונים
    with st.spinner(f"טוען נתונים עבור {symbol}..."):
        df = load_stock_data(symbol, days, include_live)
    
    if df is None or df.empty:
        st.error(f"לא ניתן לטעון נתונים עבור {symbol}")
        return
    
    # יצירת tabs ראשיים
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 ניתוח כללי", 
        "🤖 סוכנים", 
        "🎯 אלפא סקור", 
        "📈 גרפים מתקדמים",
        "📋 סטטיסטיקות"
    ])
    
    # Tab 1: ניתוח כללי
    with tab1:
        st.header(f"📊 ניתוח כללי - {symbol}")
        
        # מידע בסיסי
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            
            st.metric(
                "מחיר נוכחי",
                f"${current_price:.2f}",
                f"{change_pct:+.2f}%",
                delta_color="normal" if change >= 0 else "inverse"
            )
        
        with col2:
            volume = df['Volume'].iloc[-1]
            avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
            volume_ratio = volume / avg_volume
            
            st.metric(
                "נפח מסחר",
                f"{volume:,.0f}",
                f"{volume_ratio:.1f}x ממוצע",
                delta_color="normal" if volume_ratio > 1 else "inverse"
            )
        
        with col3:
            high_52w = df['High'].max()
            low_52w = df['Low'].min()
            current_price = df['Close'].iloc[-1]
            range_52w = ((current_price - low_52w) / (high_52w - low_52w)) * 100
            
            st.metric(
                "טווח 52 שבועות",
                f"{range_52w:.1f}%",
                f"${low_52w:.2f} - ${high_52w:.2f}"
            )
        
        with col4:
            volatility = df['Close'].pct_change().std() * np.sqrt(252) * 100
            
            st.metric(
                "תנודתיות שנתית",
                f"{volatility:.1f}%",
                "מחושב על בסיס יומי"
            )
        
        # גרף מחיר בסיסי
        st.subheader("📈 גרף מחיר")
        fig = px.line(df, x=df.index, y='Close', title=f'מחיר מניה - {symbol}')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: סוכנים
    with tab2:
        st.header(f"🤖 ניתוח סוכנים - {symbol}")
        create_agent_dashboard(symbol, df)
    
    # Tab 3: אלפא סקור
    with tab3:
        st.header(f"🎯 אלפא סקור - {symbol}")
        
        with st.spinner("מחשב אלפא סקור..."):
            alpha_result = calculate_alpha_score(df, symbol)
        
        if alpha_result:
            # הצגת הציון הכללי
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 תוצאות אלפא סקור")
                
                if 'total_score' in alpha_result:
                    total_score = alpha_result['total_score']
                    
                    # מדד ויזואלי
                    st.progress(total_score / 100)
                    st.metric("ציון כללי", f"{total_score:.1f}/100")
                    
                    # המלצה
                    if total_score >= 80:
                        st.success("🎯 המלצה: קנייה חזקה")
                    elif total_score >= 60:
                        st.info("📈 המלצה: קנייה")
                    elif total_score >= 40:
                        st.warning("⏸️ המלצה: המתנה")
                    else:
                        st.error("📉 המלצה: מכירה")
            
            with col2:
                st.subheader("📋 פירוט סוכנים")
                if 'agent_scores' in alpha_result:
                    agent_scores = alpha_result['agent_scores']
                    
                    for agent, score in agent_scores.items():
                        if isinstance(score, (int, float)):
                            st.metric(agent, f"{score:.1f}")
            
            # הצגת פירוט מלא
            st.subheader("📄 פירוט מלא")
            st.json(alpha_result)
        else:
            st.warning("לא ניתן לחשב אלפא סקור")
    
    # Tab 4: גרפים מתקדמים
    with tab4:
        st.header(f"📈 גרפים מתקדמים - {symbol}")
        
        # חישוב אלפא סקור לגרף
        alpha_result = calculate_alpha_score(df, symbol)
        
        # יצירת גרף מתקדם
        fig = create_advanced_chart(df, symbol, alpha_result)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("לא ניתן ליצור גרף מתקדם")
    
    # Tab 5: סטטיסטיקות
    with tab5:
        st.header(f"📋 סטטיסטיקות - {symbol}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 סטטיסטיקות מחיר")
            
            # סטטיסטיקות בסיסיות
            stats = {
                "מחיר מקסימלי": f"${df['High'].max():.2f}",
                "מחיר מינימלי": f"${df['Low'].min():.2f}",
                "מחיר ממוצע": f"${df['Close'].mean():.2f}",
                "סטיית תקן": f"${df['Close'].std():.2f}",
                "שינוי יומי ממוצע": f"{df['Close'].pct_change().mean()*100:.2f}%",
                "תנודתיות יומית": f"{df['Close'].pct_change().std()*100:.2f}%"
            }
            
            for key, value in stats.items():
                st.metric(key, value)
        
        with col2:
            st.subheader("📈 מדדים טכניים")
            
            # חישוב מדדים טכניים
            if 'RSI' in df.columns:
                current_rsi = df['RSI'].iloc[-1]
                st.metric("RSI נוכחי", f"{current_rsi:.1f}")
            
            if 'MACD' in df.columns:
                current_macd = df['MACD'].iloc[-1]
                st.metric("MACD נוכחי", f"{current_macd:.4f}")
            
            # נפח מסחר
            avg_volume = df['Volume'].mean()
            current_volume = df['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume
            
            st.metric("יחס נפח", f"{volume_ratio:.1f}x")
        
        # טבלת נתונים
        st.subheader("📊 נתונים גולמיים")
        st.dataframe(df.tail(20), use_container_width=True)

if __name__ == "__main__":
    main() 