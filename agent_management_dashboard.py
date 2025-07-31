#!/usr/bin/env python3
"""
דשבורד ניהול סוכנים - Charles FocusedSpec
ניהול מתקדם של כל הסוכנים במערכת
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
import time
import threading
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
    from core.volume_spike_agent import VolumeSpikeAgent
    from core.golden_cross_detector import GoldenCrossDetector
    from core.breakout_screener import BreakoutScreener
    from core.news_catalyst_agent import NewsCatalystAgent
    from core.sentiment_scorer import SentimentScorer
    from core.advanced_pattern_analyzer import AdvancedPatternAnalyzer
    from core.bullish_pattern_spotter import BullishPatternSpotter
    from core.trend_shift_agent import TrendShiftAgent
    from core.earnings_surprise_tracker import EarningsSurpriseTracker
    from core.insider_activity_monitor import InsiderActivityMonitor
    from core.options_unusual_volume_agent import OptionsUnusualVolumeAgent
    from utils.smart_data_manager import smart_data_manager
    SYSTEM_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ חלק מהמודולים לא זמינים: {str(e)}")
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
        background: linear-gradient(90deg, #6f42c1, #e83e8c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 2px solid #dee2e6;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .agent-active {
        border-color: #28a745;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    }
    .agent-inactive {
        border-color: #dc3545;
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    }
    .agent-warning {
        border-color: #ffc107;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    }
    .performance-metric {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #6f42c1;
        margin: 0.5rem 0;
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
        background-color: #6f42c1;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'agents_status' not in st.session_state:
    st.session_state.agents_status = {}

if 'agent_performance' not in st.session_state:
    st.session_state.agent_performance = {}

if 'agent_logs' not in st.session_state:
    st.session_state.agent_logs = []

def get_available_stocks():
    """מחזיר רשימת מניות זמינות"""
    pattern = "data/raw_price_data/* Stock Price History.csv"
    files = glob.glob(pattern)
    stocks = []
    for file in files:
        stock_name = os.path.basename(file).replace(" Stock Price History.csv", "")
        stocks.append(stock_name)
    return sorted(stocks)

def get_all_agents():
    """מחזיר רשימת כל הסוכנים הזמינים"""
    agents = {}
    
    # הוספת סוכנים רק אם הם זמינים
    try:
        if 'ADXScoreAgent' in globals():
            agents["ADX Score Agent"] = {
                "class": ADXScoreAgent,
                "description": "מנתח מגמות ADX",
                "category": "Technical",
                "priority": "High"
            }
    except:
        pass
    
    try:
        if 'RSISniffer' in globals():
            agents["RSI Sniffer"] = {
                "class": RSISniffer,
                "description": "מזהה מצבי RSI",
                "category": "Technical",
                "priority": "Medium"
            }
    except:
        pass
    
    try:
        if 'BollingerSqueeze' in globals():
            agents["Bollinger Squeeze"] = {
                "class": BollingerSqueeze,
                "description": "מזהה מצבי Bollinger",
                "category": "Technical",
                "priority": "Medium"
            }
    except:
        pass
    
    try:
        if 'MACDMomentumDetector' in globals():
            agents["MACD Momentum"] = {
                "class": MACDMomentumDetector,
                "description": "מנתח מומנטום MACD",
                "category": "Technical",
                "priority": "High"
            }
    except:
        pass
    
    try:
        if 'VolumeSpikeAgent' in globals():
            agents["Volume Spike"] = {
                "class": VolumeSpikeAgent,
                "description": "מזהה קפיצות נפח",
                "category": "Volume",
                "priority": "Medium"
            }
    except:
        pass
    
    try:
        if 'GoldenCrossDetector' in globals():
            agents["Golden Cross"] = {
                "class": GoldenCrossDetector,
                "description": "מזהה Golden Cross",
                "category": "Technical",
                "priority": "High"
            }
    except:
        pass
    
    try:
        if 'NewsCatalystAgent' in globals():
            agents["News Catalyst"] = {
                "class": NewsCatalystAgent,
                "description": "מנתח חדשות",
                "category": "News",
                "priority": "Medium"
            }
    except:
        pass
    
    try:
        if 'SentimentScorer' in globals():
            agents["Sentiment Scorer"] = {
                "class": SentimentScorer,
                "description": "מנתח סנטימנט",
                "category": "Sentiment",
                "priority": "Medium"
            }
    except:
        pass
    
    return agents

def run_agent_analysis(agent_name, agent_info, symbol):
    """מריץ ניתוח של סוכן ספציפי"""
    try:
        if not SYSTEM_AVAILABLE:
            return {"status": "error", "message": "המערכת לא זמינה"}
        
        agent_class = agent_info["class"]
        agent = agent_class()
        
        # רישום לוג
        log_entry = {
            "timestamp": datetime.now(),
            "agent": agent_name,
            "symbol": symbol,
            "action": "start"
        }
        st.session_state.agent_logs.append(log_entry)
        
        # הרצת הניתוח
        result = agent.analyze(symbol)
        
        # רישום תוצאה
        log_entry = {
            "timestamp": datetime.now(),
            "agent": agent_name,
            "symbol": symbol,
            "action": "complete",
            "result": result
        }
        st.session_state.agent_logs.append(log_entry)
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        error_msg = f"שגיאה בסוכן {agent_name}: {str(e)}"
        log_entry = {
            "timestamp": datetime.now(),
            "agent": agent_name,
            "symbol": symbol,
            "action": "error",
            "error": str(e)
        }
        st.session_state.agent_logs.append(log_entry)
        return {"status": "error", "message": error_msg}

def get_agent_performance(agent_name):
    """מחזיר ביצועי סוכן"""
    if agent_name not in st.session_state.agent_performance:
        st.session_state.agent_performance[agent_name] = {
            "total_runs": 0,
            "successful_runs": 0,
            "error_runs": 0,
            "avg_response_time": 0,
            "last_run": None,
            "signals_generated": 0
        }
    return st.session_state.agent_performance[agent_name]

def update_agent_performance(agent_name, success, response_time, signal_generated=False):
    """מעדכן ביצועי סוכן"""
    perf = get_agent_performance(agent_name)
    perf["total_runs"] += 1
    perf["last_run"] = datetime.now()
    
    if success:
        perf["successful_runs"] += 1
    else:
        perf["error_runs"] += 1
    
    if signal_generated:
        perf["signals_generated"] += 1
    
    # עדכון זמן תגובה ממוצע
    if perf["avg_response_time"] == 0:
        perf["avg_response_time"] = response_time
    else:
        perf["avg_response_time"] = (perf["avg_response_time"] + response_time) / 2

def create_agent_performance_chart():
    """יוצר גרף ביצועי סוכנים"""
    agents = get_all_agents()
    
    # הכנת נתונים
    agent_names = []
    success_rates = []
    response_times = []
    signal_counts = []
    
    for agent_name in agents.keys():
        perf = get_agent_performance(agent_name)
        agent_names.append(agent_name)
        
        if perf["total_runs"] > 0:
            success_rate = (perf["successful_runs"] / perf["total_runs"]) * 100
        else:
            success_rate = 0
        
        success_rates.append(success_rate)
        response_times.append(perf["avg_response_time"])
        signal_counts.append(perf["signals_generated"])
    
    # יצירת גרף
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'אחוז הצלחה',
            'זמן תגובה ממוצע',
            'מספר סיגנלים שנוצרו',
            'סטטוס סוכנים'
        )
    )
    
    # גרף אחוז הצלחה
    fig.add_trace(
        go.Bar(
            x=agent_names,
            y=success_rates,
            name='אחוז הצלחה',
            marker_color='lightblue'
        ),
        row=1, col=1
    )
    
    # גרף זמן תגובה
    fig.add_trace(
        go.Bar(
            x=agent_names,
            y=response_times,
            name='זמן תגובה (שניות)',
            marker_color='lightcoral'
        ),
        row=1, col=2
    )
    
    # גרף סיגנלים
    fig.add_trace(
        go.Bar(
            x=agent_names,
            y=signal_counts,
            name='סיגנלים שנוצרו',
            marker_color='lightgreen'
        ),
        row=2, col=1
    )
    
    # גרף סטטוס
    active_agents = sum(1 for name in agent_names if get_agent_performance(name)["total_runs"] > 0)
    inactive_agents = len(agent_names) - active_agents
    
    fig.add_trace(
        go.Pie(
            labels=['פעילים', 'לא פעילים'],
            values=[active_agents, inactive_agents],
            name='סטטוס סוכנים'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title="ביצועי סוכנים",
        height=800,
        showlegend=True
    )
    
    return fig

def main():
    # כותרת ראשית
    st.markdown('<h1 class="main-header">🤖 Charles FocusedSpec - ניהול סוכנים</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # סיידבר
    st.sidebar.header("⚙️ הגדרות ניהול")
    
    # בחירת מניות
    available_stocks = get_available_stocks()
    selected_stocks = st.sidebar.multiselect(
        "מניות לניתוח",
        available_stocks,
        default=['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    )
    
    # הגדרות כלליות
    auto_run = st.sidebar.checkbox("הרצה אוטומטית", value=False)
    run_interval = st.sidebar.slider("מרווח הרצה (דקות)", 1, 60, 5)
    
    if not selected_stocks:
        st.warning("אנא בחר מניות לניתוח")
        return
    
    # קבלת כל הסוכנים
    all_agents = get_all_agents()
    
    # טאבים ראשיים
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 ניהול סוכנים",
        "📊 ביצועים",
        "📋 לוגים",
        "⚡ הרצה מהירה"
    ])
    
    with tab1:
        st.subheader("🤖 ניהול סוכנים")
        
        # סינון לפי קטגוריה
        categories = list(set([agent["category"] for agent in all_agents.values()]))
        selected_category = st.selectbox("בחר קטגוריה", ["כל הקטגוריות"] + categories)
        
        # הצגת סוכנים
        for agent_name, agent_info in all_agents.items():
            if selected_category == "כל הקטגוריות" or agent_info["category"] == selected_category:
                perf = get_agent_performance(agent_name)
                
                # קביעת סטטוס
                if perf["total_runs"] == 0:
                    status_class = "agent-inactive"
                    status_text = "לא פעיל"
                elif perf["successful_runs"] / perf["total_runs"] > 0.8:
                    status_class = "agent-active"
                    status_text = "פעיל"
                else:
                    status_class = "agent-warning"
                    status_text = "בעיות"
                
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="agent-card {status_class}">
                        <h4>{agent_name}</h4>
                        <p>{agent_info['description']}</p>
                        <small>קטגוריה: {agent_info['category']} | עדיפות: {agent_info['priority']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.write(f"**סטטוס:** {status_text}")
                    st.write(f"**הרצות:** {perf['total_runs']}")
                
                with col3:
                    if perf["total_runs"] > 0:
                        success_rate = (perf["successful_runs"] / perf["total_runs"]) * 100
                        st.write(f"**הצלחה:** {success_rate:.1f}%")
                    else:
                        st.write("**הצלחה:** 0%")
                
                with col4:
                    if st.button(f"הפעל {agent_name.split()[0]}", key=f"run_{agent_name}"):
                        if selected_stocks:
                            symbol = selected_stocks[0]  # רץ על המניה הראשונה
                            start_time = time.time()
                            
                            with st.spinner(f"מריץ {agent_name}..."):
                                result = run_agent_analysis(agent_name, agent_info, symbol)
                            
                            end_time = time.time()
                            response_time = end_time - start_time
                            
                            success = result["status"] == "success"
                            update_agent_performance(agent_name, success, response_time)
                            
                            if success:
                                st.success(f"✅ {agent_name} הופעל בהצלחה!")
                                st.json(result["result"])
                            else:
                                st.error(f"❌ שגיאה ב-{agent_name}: {result['message']}")
                        else:
                            st.error("אנא בחר מניות לניתוח")
                
                st.markdown("---")
    
    with tab2:
        st.subheader("📊 ביצועי סוכנים")
        
        # מטריקות כלליות
        total_agents = len(all_agents)
        active_agents = sum(1 for name in all_agents.keys() if get_agent_performance(name)["total_runs"] > 0)
        total_runs = sum(get_agent_performance(name)["total_runs"] for name in all_agents.keys())
        total_signals = sum(get_agent_performance(name)["signals_generated"] for name in all_agents.keys())
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("סוכנים פעילים", f"{active_agents}/{total_agents}")
        
        with col2:
            st.metric("הרצות כולל", f"{total_runs}")
        
        with col3:
            st.metric("סיגנלים שנוצרו", f"{total_signals}")
        
        with col4:
            avg_success = 0
            if total_runs > 0:
                total_success = sum(get_agent_performance(name)["successful_runs"] for name in all_agents.keys())
                avg_success = (total_success / total_runs) * 100
            st.metric("אחוז הצלחה ממוצע", f"{avg_success:.1f}%")
        
        # גרף ביצועים
        perf_fig = create_agent_performance_chart()
        st.plotly_chart(perf_fig, use_container_width=True)
    
    with tab3:
        st.subheader("📋 לוגי סוכנים")
        
        # סינון לוגים
        col1, col2 = st.columns(2)
        
        with col1:
            selected_agent_log = st.selectbox(
                "בחר סוכן",
                ["כל הסוכנים"] + list(all_agents.keys())
            )
        
        with col2:
            selected_action_log = st.selectbox(
                "בחר פעולה",
                ["כל הפעולות", "start", "complete", "error"]
            )
        
        # הצגת לוגים
        filtered_logs = st.session_state.agent_logs
        
        if selected_agent_log != "כל הסוכנים":
            filtered_logs = [log for log in filtered_logs if log.get("agent") == selected_agent_log]
        
        if selected_action_log != "כל הפעולות":
            filtered_logs = [log for log in filtered_logs if log.get("action") == selected_action_log]
        
        # הצגת לוגים אחרונים
        recent_logs = filtered_logs[-50:]  # 50 לוגים אחרונים
        
        for log in reversed(recent_logs):
            timestamp = log.get("timestamp", datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
            agent = log.get("agent", "Unknown")
            action = log.get("action", "Unknown")
            symbol = log.get("symbol", "N/A")
            
            if action == "start":
                st.info(f"🟡 {timestamp} - {agent} התחיל ניתוח {symbol}")
            elif action == "complete":
                st.success(f"🟢 {timestamp} - {agent} השלים ניתוח {symbol}")
            elif action == "error":
                error_msg = log.get("error", "Unknown error")
                st.error(f"🔴 {timestamp} - {agent} שגיאה: {error_msg}")
    
    with tab4:
        st.subheader("⚡ הרצה מהירה")
        
        # בחירת סוכנים להרצה מהירה
        selected_agents = st.multiselect(
            "בחר סוכנים להרצה מהירה",
            list(all_agents.keys()),
            default=list(all_agents.keys())[:5]
        )
        
        if st.button("הפעל סוכנים נבחרים", type="primary"):
            if selected_stocks and selected_agents:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = {}
                
                for i, agent_name in enumerate(selected_agents):
                    status_text.text(f"מריץ {agent_name}...")
                    
                    agent_info = all_agents[agent_name]
                    symbol = selected_stocks[0]  # רץ על המניה הראשונה
                    
                    start_time = time.time()
                    result = run_agent_analysis(agent_name, agent_info, symbol)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    success = result["status"] == "success"
                    update_agent_performance(agent_name, success, response_time)
                    
                    results[agent_name] = result
                    
                    progress_bar.progress((i + 1) / len(selected_agents))
                
                status_text.text("הרצה הושלמה!")
                
                # הצגת תוצאות
                st.subheader("תוצאות הרצה מהירה")
                
                for agent_name, result in results.items():
                    if result["status"] == "success":
                        st.success(f"✅ {agent_name}: הצלחה")
                        with st.expander(f"תוצאות {agent_name}"):
                            st.json(result["result"])
                    else:
                        st.error(f"❌ {agent_name}: {result['message']}")
            else:
                st.error("אנא בחר סוכנים ומניות")
    
    # הודעת הצלחה
    st.success("✅ מערכת ניהול הסוכנים פועלת בהצלחה!")
    st.info(f"💡 המערכת מנהלת {len(all_agents)} סוכנים מתקדמים.")

if __name__ == "__main__":
    main() 