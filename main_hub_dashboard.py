#!/usr/bin/env python3
"""
דשבורד מרכזי - Charles FocusedSpec
מרכז גישה לכל הדשבורדים והמערכות
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys
import json
from pathlib import Path
import subprocess
# import psutil  # לא זמין כרגע
import requests
from typing import Dict, List, Optional

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# הגדרת דף
st.set_page_config(
    page_title="Charles FocusedSpec - מרכז מערכת",
    page_icon="🏠",
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
    .dashboard-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .dashboard-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .dashboard-active {
        border-left: 5px solid #28a745;
    }
    .dashboard-inactive {
        border-left: 5px solid #dc3545;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online {
        background-color: #28a745;
    }
    .status-offline {
        background-color: #dc3545;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f2f6 0%, #e6e9f0 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .system-status {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# הגדרת הדשבורדים הזמינים
DASHBOARDS = {
    "comprehensive_live_dashboard": {
        "name": "דשבורד מקיף - לייב",
        "description": "דשבורד מקיף עם נתונים חיים, סוכנים ואלפא סקור",
        "port": 8501,
        "icon": "🚀",
        "category": "ראשי"
    },
    "agent_monitoring_dashboard": {
        "name": "ניהול סוכנים",
        "description": "ניטור וניהול כל הסוכנים במערכת",
        "port": 8502,
        "icon": "🤖",
        "category": "סוכנים"
    },
    "complete_system_dashboard": {
        "name": "דשבורד מערכת מלא",
        "description": "דשבורד מערכת מקיף עם כל הפונקציות",
        "port": 8503,
        "icon": "📊",
        "category": "ראשי"
    },
    "live_trading_dashboard": {
        "name": "מסחר לייב",
        "description": "סימולציית מסחר לייב עם אותות",
        "port": 8504,
        "icon": "💰",
        "category": "מסחר"
    },
    "agent_management_dashboard": {
        "name": "ניהול סוכנים מתקדם",
        "description": "ניהול מתקדם של כל הסוכנים",
        "port": 8505,
        "icon": "⚙️",
        "category": "סוכנים"
    },
    "main_dashboard": {
        "name": "דשבורד ראשי",
        "description": "דשבורד ראשי של המערכת",
        "port": 8506,
        "icon": "🏠",
        "category": "ראשי"
    }
}

# בדיקת סטטוס דשבורד
def check_dashboard_status(port: int) -> bool:
    """בדיקת סטטוס דשבורד לפי פורט"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        return response.status_code == 200
    except:
        return False

# קבלת מידע על תהליכים
def get_process_info():
    """קבלת מידע על תהליכי Streamlit"""
    # פונקציה פשוטה ללא psutil
    return []

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
        return ["AAPL", "GOOGL", "MSFT"]

# יצירת כרטיס דשבורד
def create_dashboard_card(dashboard_key: str, dashboard_info: dict):
    """יצירת כרטיס דשבורד"""
    is_online = check_dashboard_status(dashboard_info['port'])
    status_class = "dashboard-active" if is_online else "dashboard-inactive"
    status_indicator = "status-online" if is_online else "status-offline"
    
    st.markdown(f"""
    <div class="dashboard-card {status_class}" onclick="window.open('http://localhost:{dashboard_info['port']}', '_blank')">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <span style="font-size: 2rem; margin-right: 1rem;">{dashboard_info['icon']}</span>
            <div>
                <h3 style="margin: 0;">{dashboard_info['name']}</h3>
                <p style="margin: 0; color: #666;">{dashboard_info['description']}</p>
            </div>
            <div style="margin-left: auto;">
                <span class="status-indicator {status_indicator}"></span>
                <span style="font-size: 0.8rem;">{'פעיל' if is_online else 'לא פעיל'}</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.9rem; color: #666;">פורט: {dashboard_info['port']}</span>
            <span style="font-size: 0.9rem; color: #666;">קטגוריה: {dashboard_info['category']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# יצירת סטטיסטיקות מערכת
def create_system_stats():
    """יצירת סטטיסטיקות מערכת"""
    # בדיקת תהליכים
    processes = get_process_info()
    
    # חישוב סטטיסטיקות
    total_dashboards = len(DASHBOARDS)
    active_dashboards = sum(1 for info in DASHBOARDS.values() if check_dashboard_status(info['port']))
    
    # הצגת סטטיסטיקות
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("דשבורדים זמינים", total_dashboards)
    
    with col2:
        st.metric("דשבורדים פעילים", active_dashboards, f"{active_dashboards - total_dashboards}")
    
    with col3:
        st.metric("תהליכי Streamlit", len(processes))
    
    with col4:
        # בדיקת זיכרון
        st.metric("שימוש זיכרון", "N/A")

# יצירת דשבורד מהיר
def create_quick_dashboard():
    """יצירת דשבורד מהיר לניתוח מניה"""
    st.subheader("⚡ ניתוח מהיר")
    
    # בחירת מניה
    available_stocks = get_available_stocks()
    symbol = st.selectbox("בחר מניה לניתוח מהיר", available_stocks, index=0)
    
    if st.button("🔍 הרץ ניתוח מהיר"):
        # כאן נוכל להוסיף ניתוח מהיר
        st.info(f"ניתוח מהיר עבור {symbol} - תכונה תגיע בקרוב!")

# פונקציה ראשית
def main():
    # כותרת ראשית
    st.markdown('<h1 class="main-header">🏠 Charles FocusedSpec</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #666;">מרכז מערכת רב-סוכנים לחיזוי מניות פורצות</h2>', unsafe_allow_html=True)
    
    # סיידבר
    st.sidebar.header("⚙️ הגדרות מערכת")
    
    # כפתור רענון
    if st.sidebar.button("🔄 רענן סטטוס"):
        st.rerun()
    
    # מידע מערכת
    st.sidebar.subheader("📊 מידע מערכת")
    st.sidebar.write(f"**תאריך:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # סטטוס מערכת
    st.sidebar.subheader("🔧 סטטוס מערכת")
    
    # בדיקת מודולים
    try:
        import core.alpha_score_engine
        st.sidebar.success("✅ מנוע אלפא סקור")
    except:
        st.sidebar.error("❌ מנוע אלפא סקור")
    
    try:
        import utils.smart_data_manager
        st.sidebar.success("✅ מנהל נתונים")
    except:
        st.sidebar.error("❌ מנהל נתונים")
    
    # יצירת tabs ראשיים
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 דף הבית", 
        "📊 דשבורדים", 
        "🤖 סוכנים", 
        "⚡ ניתוח מהיר"
    ])
    
    # Tab 1: דף הבית
    with tab1:
        st.header("🏠 ברוכים הבאים למערכת Charles FocusedSpec")
        
        # סטטיסטיקות מערכת
        st.subheader("📊 סטטיסטיקות מערכת")
        create_system_stats()
        
        # מידע על המערכת
        st.subheader("ℹ️ מידע על המערכת")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🚀 מערכת רב-סוכנים מתקדמת:**
            - 30+ סוכנים מתמחים
            - ניתוח טכני מתקדם
            - ניתוח חדשות וסנטימנט
            - חישוב אלפא סקור
            - נתונים חיים בזמן אמת
            """)
        
        with col2:
            st.markdown("""
            **📈 יכולות עיקריות:**
            - זיהוי מניות פורצות
            - ניתוח מגמות מתקדם
            - ניתוח פונדמנטלי
            - ניתוח סיכונים
            - המלצות מסחר
            """)
        
        # סטטוס דשבורדים
        st.subheader("📊 סטטוס דשבורדים")
        
        # קבוצת דשבורדים לפי קטגוריה
        categories = list(set([info['category'] for info in DASHBOARDS.values()]))
        
        for category in categories:
            st.write(f"**{category}:**")
            category_dashboards = {k: v for k, v in DASHBOARDS.items() if v['category'] == category}
            
            for dashboard_key, dashboard_info in category_dashboards.items():
                create_dashboard_card(dashboard_key, dashboard_info)
    
    # Tab 2: דשבורדים
    with tab2:
        st.header("📊 כל הדשבורדים")
        
        # סינון לפי קטגוריה
        category_filter = st.selectbox("סינון לפי קטגוריה", ["הכל"] + categories)
        
        if category_filter == "הכל":
            filtered_dashboards = DASHBOARDS
        else:
            filtered_dashboards = {k: v for k, v in DASHBOARDS.items() if v['category'] == category_filter}
        
        # הצגת דשבורדים
        for dashboard_key, dashboard_info in filtered_dashboards.items():
            create_dashboard_card(dashboard_key, dashboard_info)
    
    # Tab 3: סוכנים
    with tab3:
        st.header("🤖 מידע על סוכנים")
        
        # רשימת סוכנים
        agents_info = {
            "טכני": [
                "ADXScoreAgent - ניתוח מגמות",
                "RSISniffer - ניתוח RSI",
                "BollingerSqueeze - ניתוח Bollinger",
                "MACDMomentumDetector - ניתוח MACD",
                "GoldenCrossDetector - זיהוי צלב זהב",
                "VolumeSpikeAgent - ניתוח נפח",
                "EnhancedAdvancedAnalyzer - ניתוח מתקדם",
                "BullishPatternSpotter - זיהוי תבניות",
                "GapDetectorUltimate - זיהוי פערים",
                "CandlestickAgent - ניתוח נרות",
                "TrendDetector - זיהוי מגמות",
                "TrendShiftDetector - שינויי מגמה",
                "VReversalAgent - היפוכי V",
                "ParabolicAgent - תנועות פרבוליות",
                "MidtermMomentumAgent - מומנטום",
                "MovingAveragePressureBot - לחץ ממוצעים",
                "ATRScoreAgent - ניתוח ATR",
                "BreakoutRetestRecognizer - זיהוי פריצות",
                "SupportZoneStrengthDetector - אזורי תמיכה"
            ],
            "חדשות וסנטימנט": [
                "NewsCatalystAgent - ניתוח חדשות",
                "SentimentScorer - ניתוח סנטימנט",
                "SocialMediaHypeScanner - מדיה חברתית",
                "NLPAnalyzer - ניתוח NLP"
            ],
            "פונדמנטלי": [
                "ValuationDetector - ניתוח הערכה",
                "FinancialStabilityAgent - יציבות פיננסית",
                "EarningsSurpriseTracker - הפתעות רווחים",
                "AnalystRatingAgent - דירוג אנליסטים",
                "GrowthScanner - סריקת צמיחה"
            ],
            "מאקרו וחיזוי": [
                "GeopoliticalRiskMonitor - סיכונים גיאופוליטיים",
                "ReturnForecaster - חיזוי תשואות"
            ],
            "אימות ואורכיסטרציה": [
                "MultiAgentValidator - אימות רב-סוכן",
                "HighConvictionOrchestrator - אורכיסטרטור"
            ]
        }
        
        for category, agents in agents_info.items():
            st.subheader(f"📊 {category}")
            for agent in agents:
                st.write(f"• {agent}")
    
    # Tab 4: ניתוח מהיר
    with tab4:
        st.header("⚡ ניתוח מהיר")
        create_quick_dashboard()
        
        # מידע נוסף
        st.subheader("📋 מידע נוסף")
        st.info("""
        **לניתוח מקיף יותר:**
        1. עבור לטאב "דשבורדים"
        2. בחר דשבורד מתאים
        3. הרץ ניתוח מלא
        """)

if __name__ == "__main__":
    main() 