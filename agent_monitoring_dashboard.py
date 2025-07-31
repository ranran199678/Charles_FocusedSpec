#!/usr/bin/env python3
"""
דשבורד ניהול סוכנים - Charles FocusedSpec
מציג את הפעילות, הציונים והסיבות של כל סוכן במערכת
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import os
import sys
import json
from pathlib import Path
import time
from typing import Dict, List, Optional

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ייבוא מודולים מהמערכת
try:
    from core.alpha_score_engine import AlphaScoreEngine
    from utils.smart_data_manager import SmartDataManager
    from utils.logger import setup_logger
    
    # ייבוא כל הסוכנים
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
    page_title="Charles FocusedSpec - ניהול סוכנים",
    page_icon="🤖",
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
    .agent-status-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .agent-status-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .agent-active {
        border-left: 5px solid #28a745;
    }
    .agent-inactive {
        border-left: 5px solid #dc3545;
    }
    .agent-warning {
        border-left: 5px solid #ffc107;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
    }
    .signal-buy {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .signal-sell {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .signal-hold {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# הגדרת הסוכנים
AGENTS_CONFIG = {
    "ADXScoreAgent": {
        "name": "ניתוח מגמות ADX",
        "description": "מנתח את עוצמת המגמה באמצעות ADX",
        "category": "טכני",
        "weight": 2,
        "class": ADXScoreAgent
    },
    "RSISniffer": {
        "name": "ניתוח RSI",
        "description": "מזהה מצבי קנייה ומכירה לפי RSI",
        "category": "טכני",
        "weight": 2,
        "class": RSISniffer
    },
    "BollingerSqueeze": {
        "name": "ניתוח Bollinger Bands",
        "description": "מזהה מצבי לחץ ופריצה",
        "category": "טכני",
        "weight": 1,
        "class": BollingerSqueeze
    },
    "MACDMomentumDetector": {
        "name": "ניתוח מומנטום MACD",
        "description": "מנתח מומנטום באמצעות MACD",
        "category": "טכני",
        "weight": 2,
        "class": MACDMomentumDetector
    },
    "NewsCatalystAgent": {
        "name": "ניתוח חדשות",
        "description": "מנתח השפעת חדשות על המניה",
        "category": "חדשות",
        "weight": 2,
        "class": NewsCatalystAgent
    },
    "SentimentScorer": {
        "name": "ניתוח סנטימנט",
        "description": "מנתח את הסנטימנט בשוק",
        "category": "סנטימנט",
        "weight": 2,
        "class": SentimentScorer
    },
    "GoldenCrossDetector": {
        "name": "זיהוי צלב זהב",
        "description": "מזהה צלבי זהב וצלבי מוות",
        "category": "טכני",
        "weight": 1,
        "class": GoldenCrossDetector
    },
    "VolumeSpikeAgent": {
        "name": "ניתוח נפח",
        "description": "מזהה גלי נפח חריגים",
        "category": "טכני",
        "weight": 1,
        "class": VolumeSpikeAgent
    },
    "EnhancedAdvancedAnalyzer": {
        "name": "ניתוח מתקדם",
        "description": "ניתוח טכני מתקדם ומקיף",
        "category": "טכני",
        "weight": 4,
        "class": EnhancedAdvancedAnalyzer
    },
    "BullishPatternSpotter": {
        "name": "זיהוי תבניות בולשיות",
        "description": "מזהה תבניות גרפיות בולשיות",
        "category": "טכני",
        "weight": 2,
        "class": BullishPatternSpotter
    },
    "ValuationDetector": {
        "name": "ניתוח הערכה",
        "description": "מנתח יחסי הערכה פיננסיים",
        "category": "פונדמנטלי",
        "weight": 3,
        "class": ValuationDetector
    },
    "FinancialStabilityAgent": {
        "name": "יציבות פיננסית",
        "description": "מנתח יציבות פיננסית של החברה",
        "category": "פונדמנטלי",
        "weight": 3,
        "class": FinancialStabilityAgent
    },
    "SocialMediaHypeScanner": {
        "name": "סריקת מדיה חברתית",
        "description": "מנתח באזז ברשתות חברתיות",
        "category": "סנטימנט",
        "weight": 1,
        "class": SocialMediaHypeScanner
    },
    "NLPAnalyzer": {
        "name": "ניתוח NLP",
        "description": "ניתוח שפה טבעית של חדשות",
        "category": "חדשות",
        "weight": 2,
        "class": NLPAnalyzer
    },
    "EarningsSurpriseTracker": {
        "name": "מעקב הפתעות רווחים",
        "description": "מזהה הפתעות רווחים",
        "category": "פונדמנטלי",
        "weight": 2,
        "class": EarningsSurpriseTracker
    },
    "AnalystRatingAgent": {
        "name": "דירוג אנליסטים",
        "description": "מנתח המלצות אנליסטים",
        "category": "פונדמנטלי",
        "weight": 2,
        "class": AnalystRatingAgent
    },
    "GeopoliticalRiskMonitor": {
        "name": "ניטור סיכונים גיאופוליטיים",
        "description": "מנתח סיכונים גיאופוליטיים",
        "category": "מאקרו",
        "weight": 1,
        "class": GeopoliticalRiskMonitor
    },
    "GapDetectorUltimate": {
        "name": "זיהוי פערים",
        "description": "מזהה פערי מחיר",
        "category": "טכני",
        "weight": 1,
        "class": GapDetectorUltimate
    },
    "CandlestickAgent": {
        "name": "ניתוח נרות",
        "description": "מנתח תבניות נרות יפניים",
        "category": "טכני",
        "weight": 1,
        "class": CandlestickAgent
    },
    "TrendDetector": {
        "name": "זיהוי מגמות",
        "description": "מזהה מגמות ארוכות טווח",
        "category": "טכני",
        "weight": 1,
        "class": TrendDetector
    },
    "TrendShiftDetector": {
        "name": "זיהוי שינויי מגמה",
        "description": "מזהה שינויים במגמה",
        "category": "טכני",
        "weight": 1,
        "class": TrendShiftDetector
    },
    "VReversalAgent": {
        "name": "זיהוי היפוכי V",
        "description": "מזהה תבניות היפוך V",
        "category": "טכני",
        "weight": 1,
        "class": VReversalAgent
    },
    "ParabolicAgent": {
        "name": "זיהוי תנועות פרבוליות",
        "description": "מזהה תנועות פרבוליות",
        "category": "טכני",
        "weight": 1,
        "class": ParabolicAgent
    },
    "ReturnForecaster": {
        "name": "חיזוי תשואות",
        "description": "מנבא תשואות עתידיות",
        "category": "חיזוי",
        "weight": 1,
        "class": ReturnForecaster
    },
    "GrowthScanner": {
        "name": "סריקת צמיחה",
        "description": "מזהה מניות צמיחה",
        "category": "פונדמנטלי",
        "weight": 1,
        "class": GrowthScanner
    },
    "MidtermMomentumAgent": {
        "name": "מומנטום בינוני",
        "description": "מנתח מומנטום בינוני טווח",
        "category": "טכני",
        "weight": 1,
        "class": MidtermMomentumAgent
    },
    "MovingAveragePressureBot": {
        "name": "לחץ ממוצעים נעים",
        "description": "מנתח לחץ של ממוצעים נעים",
        "category": "טכני",
        "weight": 1,
        "class": MovingAveragePressureBot
    },
    "ATRScoreAgent": {
        "name": "ניתוח ATR",
        "description": "מנתח תנודתיות באמצעות ATR",
        "category": "טכני",
        "weight": 1,
        "class": ATRScoreAgent
    },
    "MultiAgentValidator": {
        "name": "אימות רב-סוכן",
        "description": "מאמת תוצאות של מספר סוכנים",
        "category": "אימות",
        "weight": 1,
        "class": MultiAgentValidator
    },
    "HighConvictionOrchestrator": {
        "name": "אורכיסטרטור ביטחון גבוה",
        "description": "מתאם סוכנים עם ביטחון גבוה",
        "category": "אורכיסטרציה",
        "weight": 1,
        "class": HighConvictionOrchestrator
    },
    "BreakoutRetestRecognizer": {
        "name": "זיהוי פריצות",
        "description": "מזהה פריצות ובדיקות חוזרות",
        "category": "טכני",
        "weight": 1,
        "class": BreakoutRetestRecognizer
    },
    "SupportZoneStrengthDetector": {
        "name": "אזורי תמיכה",
        "description": "מנתח עוצמת אזורי תמיכה",
        "category": "טכני",
        "weight": 1,
        "class": SupportZoneStrengthDetector
    }
}

# אתחול מערכות
@st.cache_resource
def initialize_systems():
    """אתחול המערכות הראשיות"""
    try:
        data_manager = SmartDataManager()
        alpha_engine = AlphaScoreEngine()
        logger = setup_logger()
        return data_manager, alpha_engine, logger
    except Exception as e:
        st.error(f"שגיאה באתחול המערכות: {e}")
        return None, None, None

# קבלת רשימת מניות
@st.cache_data(ttl=300)
def get_available_stocks():
    """קבלת רשימת מניות זמינות"""
    try:
        data_dir = Path("data/raw_price_data")
        if data_dir.exists():
            csv_files = list(data_dir.glob("*.csv"))
            symbols = [f.stem.replace(" Stock Price History", "") for f in csv_files]
            return sorted(symbols)
        return ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN", "META", "NFLX"]
    except Exception as e:
        st.error(f"שגיאה בקבלת רשימת מניות: {e}")
        return ["AAPL", "GOOGL", "MSFT"]

# הרצת סוכן
def run_agent(agent_key: str, df: pd.DataFrame, symbol: str):
    """הרצת סוכן ספציפי"""
    try:
        if agent_key in AGENTS_CONFIG:
            agent_class = AGENTS_CONFIG[agent_key]["class"]
            agent = agent_class()
            result = agent.analyze(df, symbol)
            return result
        return None
    except Exception as e:
        st.error(f"שגיאה בהרצת סוכן {agent_key}: {e}")
        return None

# יצירת כרטיס סוכן
def create_agent_card(agent_key: str, result: dict, status: str = "active"):
    """יצירת כרטיס סוכן"""
    config = AGENTS_CONFIG[agent_key]
    
    # קביעת צבע הכרטיס
    status_class = "agent-active" if status == "active" else "agent-inactive"
    
    st.markdown(f"""
    <div class="agent-status-card {status_class}">
        <h3>🤖 {config['name']}</h3>
        <p><strong>תיאור:</strong> {config['description']}</p>
        <p><strong>קטגוריה:</strong> {config['category']}</p>
        <p><strong>משקל:</strong> {config['weight']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if result:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'score' in result:
                score = result['score']
                if score > 70:
                    st.markdown(f'<p class="score-high">ציון: {score:.1f}</p>', unsafe_allow_html=True)
                elif score > 50:
                    st.markdown(f'<p class="score-medium">ציון: {score:.1f}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="score-low">ציון: {score:.1f}</p>', unsafe_allow_html=True)
        
        with col2:
            if 'signal' in result:
                signal = result['signal']
                if signal == 'BUY':
                    st.markdown('<div class="signal-buy">📈 אות קנייה</div>', unsafe_allow_html=True)
                elif signal == 'SELL':
                    st.markdown('<div class="signal-sell">📉 אות מכירה</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="signal-hold">⏸️ המתנה</div>', unsafe_allow_html=True)
        
        with col3:
            if 'confidence' in result:
                confidence = result['confidence']
                st.progress(confidence / 100)
                st.write(f"ביטחון: {confidence:.1f}%")
        
        # הצגת הסיבות
        if 'reasons' in result:
            st.write("**סיבות:**")
            for reason in result['reasons']:
                st.write(f"• {reason}")
        
        # הצגת נתונים נוספים
        if 'details' in result:
            with st.expander("פירוט נוסף"):
                st.json(result['details'])

# יצירת דשבורד ניהול סוכנים
def create_agent_management_dashboard(symbol: str, df: pd.DataFrame):
    """יצירת דשבורד ניהול סוכנים"""
    if df is None or df.empty:
        st.warning("אין נתונים זמינים לניתוח")
        return
    
    # יצירת tabs לפי קטגוריות
    categories = list(set([config["category"] for config in AGENTS_CONFIG.values()]))
    tabs = st.tabs(categories)
    
    # ריצת כל הסוכנים
    agent_results = {}
    
    with st.spinner("מריץ את כל הסוכנים..."):
        for agent_key in AGENTS_CONFIG.keys():
            result = run_agent(agent_key, df, symbol)
            agent_results[agent_key] = result
    
    # הצגת תוצאות לפי קטגוריות
    for i, category in enumerate(categories):
        with tabs[i]:
            st.header(f"📊 {category} - {symbol}")
            
            # סוכנים בקטגוריה זו
            category_agents = {k: v for k, v in AGENTS_CONFIG.items() if v["category"] == category}
            
            for agent_key, config in category_agents.items():
                st.subheader(f"🤖 {config['name']}")
                
                result = agent_results.get(agent_key)
                if result:
                    create_agent_card(agent_key, result)
                else:
                    st.warning(f"לא ניתן להריץ {config['name']}")
                
                st.markdown("---")

# יצירת דשבורד סיכום
def create_summary_dashboard(symbol: str, df: pd.DataFrame):
    """יצירת דשבורד סיכום"""
    if df is None or df.empty:
        st.warning("אין נתונים זמינים לניתוח")
        return
    
    # ריצת כל הסוכנים
    agent_results = {}
    
    with st.spinner("מחשב סיכום..."):
        for agent_key in AGENTS_CONFIG.keys():
            result = run_agent(agent_key, df, symbol)
            agent_results[agent_key] = result
    
    # חישוב סטטיסטיקות
    active_agents = 0
    total_score = 0
    buy_signals = 0
    sell_signals = 0
    hold_signals = 0
    
    for result in agent_results.values():
        if result:
            active_agents += 1
            if 'score' in result:
                total_score += result['score']
            if 'signal' in result:
                if result['signal'] == 'BUY':
                    buy_signals += 1
                elif result['signal'] == 'SELL':
                    sell_signals += 1
                else:
                    hold_signals += 1
    
    avg_score = total_score / active_agents if active_agents > 0 else 0
    
    # הצגת סטטיסטיקות
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("סוכנים פעילים", active_agents, f"מתוך {len(AGENTS_CONFIG)}")
    
    with col2:
        st.metric("ציון ממוצע", f"{avg_score:.1f}")
    
    with col3:
        st.metric("אותות קנייה", buy_signals)
    
    with col4:
        st.metric("אותות מכירה", sell_signals)
    
    # גרף פיזור ציונים
    scores = [result.get('score', 0) for result in agent_results.values() if result]
    agent_names = [AGENTS_CONFIG[k]["name"] for k, v in agent_results.items() if v]
    
    if scores:
        fig = px.bar(
            x=agent_names,
            y=scores,
            title="ציוני סוכנים",
            labels={'x': 'סוכן', 'y': 'ציון'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # טבלת סיכום
    st.subheader("📋 סיכום סוכנים")
    
    summary_data = []
    for agent_key, result in agent_results.items():
        if result:
            config = AGENTS_CONFIG[agent_key]
            summary_data.append({
                "סוכן": config["name"],
                "קטגוריה": config["category"],
                "ציון": result.get('score', 0),
                "אות": result.get('signal', 'N/A'),
                "ביטחון": result.get('confidence', 0),
                "משקל": config["weight"]
            })
    
    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        df_summary = df_summary.sort_values('ציון', ascending=False)
        st.dataframe(df_summary, use_container_width=True)

# פונקציה ראשית
def main():
    # כותרת ראשית
    st.markdown('<h1 class="main-header">🤖 Charles FocusedSpec</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #666;">ניהול וניטור סוכנים</h2>', unsafe_allow_html=True)
    
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
    
    # טעינת נתונים
    with st.spinner(f"טוען נתונים עבור {symbol}..."):
        data_manager, _, _ = initialize_systems()
        if data_manager:
            df = data_manager.get_stock_data(symbol, days, include_live)
        else:
            df = None
    
    if df is None or df.empty:
        st.error(f"לא ניתן לטעון נתונים עבור {symbol}")
        return
    
    # יצירת tabs ראשיים
    tab1, tab2, tab3 = st.tabs([
        "📊 סיכום כללי", 
        "🤖 ניהול סוכנים", 
        "📈 ניתוח מפורט"
    ])
    
    # Tab 1: סיכום כללי
    with tab1:
        st.header(f"📊 סיכום כללי - {symbol}")
        create_summary_dashboard(symbol, df)
    
    # Tab 2: ניהול סוכנים
    with tab2:
        st.header(f"🤖 ניהול סוכנים - {symbol}")
        create_agent_management_dashboard(symbol, df)
    
    # Tab 3: ניתוח מפורט
    with tab3:
        st.header(f"📈 ניתוח מפורט - {symbol}")
        
        # בחירת סוכן ספציפי
        agent_options = {config["name"]: key for key, config in AGENTS_CONFIG.items()}
        selected_agent_name = st.selectbox("בחר סוכן לניתוח מפורט", list(agent_options.keys()))
        
        if selected_agent_name:
            selected_agent_key = agent_options[selected_agent_name]
            config = AGENTS_CONFIG[selected_agent_key]
            
            st.subheader(f"🔍 {config['name']}")
            st.write(f"**תיאור:** {config['description']}")
            st.write(f"**קטגוריה:** {config['category']}")
            st.write(f"**משקל:** {config['weight']}")
            
            # הרצת הסוכן
            with st.spinner(f"מנתח {config['name']}..."):
                result = run_agent(selected_agent_key, df, symbol)
            
            if result:
                # הצגת תוצאות מפורטות
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📊 תוצאות הניתוח")
                    st.json(result)
                
                with col2:
                    st.subheader("📈 מדדים עיקריים")
                    
                    if 'score' in result:
                        score = result['score']
                        st.metric("ציון", f"{score:.1f}")
                        
                        if score > 70:
                            st.success("מצוין")
                        elif score > 50:
                            st.info("טוב")
                        else:
                            st.warning("נמוך")
                    
                    if 'signal' in result:
                        signal = result['signal']
                        if signal == 'BUY':
                            st.success("📈 אות קנייה")
                        elif signal == 'SELL':
                            st.error("📉 אות מכירה")
                        else:
                            st.info("⏸️ המתנה")
                    
                    if 'confidence' in result:
                        confidence = result['confidence']
                        st.metric("ביטחון", f"{confidence:.1f}%")
                        st.progress(confidence / 100)
                
                # הצגת הסיבות
                if 'reasons' in result:
                    st.subheader("💡 סיבות להחלטה")
                    for i, reason in enumerate(result['reasons'], 1):
                        st.write(f"{i}. {reason}")
                
                # הצגת נתונים נוספים
                if 'details' in result:
                    st.subheader("📄 נתונים נוספים")
                    with st.expander("פירוט מלא"):
                        st.json(result['details'])
            else:
                st.error(f"לא ניתן להריץ {config['name']}")

if __name__ == "__main__":
    main() 