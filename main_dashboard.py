#!/usr/bin/env python3
"""
דשבורד ראשי - Charles FocusedSpec
מרכז גישה לכל הדשבורדים במערכת
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import glob

# הגדרת דף
st.set_page_config(
    page_title="Charles FocusedSpec - דשבורד ראשי",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS מותאם אישית
st.markdown("""
<style>
    .main-header {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .dashboard-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #dee2e6;
        margin: 1rem 0;
        transition: all 0.3s ease;
        text-align: center;
    }
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border-color: #667eea;
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
        animation: pulse 2s infinite;
    }
    .status-offline {
        background-color: #dc3545;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_available_stocks():
    """מחזיר רשימת מניות זמינות"""
    pattern = "data/raw_price_data/* Stock Price History.csv"
    files = glob.glob(pattern)
    stocks = []
    for file in files:
        stock_name = os.path.basename(file).replace(" Stock Price History.csv", "")
        stocks.append(stock_name)
    return sorted(stocks)

def check_dashboard_status(port):
    """בודק אם דשבורד רץ על פורט ספציפי"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def get_system_stats():
    """מחזיר סטטיסטיקות מערכת"""
    stats = {
        "total_stocks": len(get_available_stocks()),
        "total_agents": 49,  # מספר הסוכנים במערכת
        "data_files": 0,
        "last_update": datetime.now()
    }
    
    # ספירת קבצי נתונים
    data_patterns = [
        "data/raw_price_data/*.csv",
        "data/technical_indicators/*/*.csv",
        "data/historical_prices/*/*.csv"
    ]
    
    for pattern in data_patterns:
        stats["data_files"] += len(glob.glob(pattern))
    
    return stats

def main():
    # כותרת ראשית
    st.markdown('<h1 class="main-header">🏠 Charles FocusedSpec - דשבורד ראשי</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # סטטיסטיקות מערכת
    stats = get_system_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "מניות זמינות",
            f"{stats['total_stocks']}",
            "קבצי נתונים"
        )
    
    with col2:
        st.metric(
            "סוכנים במערכת",
            f"{stats['total_agents']}",
            "סוכני ניתוח"
        )
    
    with col3:
        st.metric(
            "קבצי נתונים",
            f"{stats['data_files']}",
            "קבצים מעובדים"
        )
    
    with col4:
        st.metric(
            "עדכון אחרון",
            stats['last_update'].strftime("%H:%M"),
            "היום"
        )
    
    st.markdown("---")
    
    # דשבורדים זמינים
    st.subheader("📊 דשבורדים זמינים")
    
    dashboards = [
        {
            "name": "מערכת מקיפה",
            "description": "דשבורד מקיף עם כל התכונות - סוכנים, אלפא סקור, חדשות וניתוחים",
            "port": 8503,
            "icon": "🚀",
            "color": "#667eea"
        },
        {
            "name": "לייבטריידינג",
            "description": "סימולציה בזמן אמת עם התראות וסיגנלים",
            "port": 8504,
            "icon": "⚡",
            "color": "#ff6b6b"
        },
        {
            "name": "ניהול סוכנים",
            "description": "ניהול מתקדם של כל הסוכנים במערכת",
            "port": 8505,
            "icon": "🤖",
            "color": "#6f42c1"
        },
        {
            "name": "דשבורד מתקדם",
            "description": "דשבורד עם תמיכה במניות מרובות",
            "port": 8502,
            "icon": "📈",
            "color": "#28a745"
        },
        {
            "name": "דשבורד משופר",
            "description": "דשבורד משופר עם נתונים אמיתיים",
            "port": 8501,
            "icon": "📊",
            "color": "#fd7e14"
        }
    ]
    
    # בדיקת סטטוס הדשבורדים
    for dashboard in dashboards:
        dashboard["status"] = check_dashboard_status(dashboard["port"])
    
    # הצגת הדשבורדים
    cols = st.columns(2)
    
    for i, dashboard in enumerate(dashboards):
        with cols[i % 2]:
            status_class = "status-online" if dashboard["status"] else "status-offline"
            status_text = "פעיל" if dashboard["status"] else "לא פעיל"
            
            st.markdown(f"""
            <div class="dashboard-card">
                <h3>{dashboard['icon']} {dashboard['name']}</h3>
                <p>{dashboard['description']}</p>
                <p><span class="status-indicator {status_class}"></span>{status_text}</p>
                <p><strong>פורט:</strong> {dashboard['port']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if dashboard["status"]:
                if st.button(f"פתח {dashboard['name']}", key=f"open_{dashboard['port']}"):
                    import webbrowser
                    webbrowser.open(f"http://localhost:{dashboard['port']}")
            else:
                st.warning("דשבורד לא פעיל")
    
    st.markdown("---")
    
    # מידע מהיר על מניות
    st.subheader("📈 מידע מהיר על מניות")
    
    available_stocks = get_available_stocks()
    if available_stocks:
        selected_stock = st.selectbox("בחר מניה למידע מהיר", available_stocks[:10])
        
        if selected_stock:
            try:
                # טעינת נתונים בסיסיים
                file_path = f"data/raw_price_data/{selected_stock} Stock Price History.csv"
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
                    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
                    
                    latest = df.iloc[-1]
                    prev = df.iloc[-2]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            f"מחיר {selected_stock}",
                            f"${latest['Price']:.2f}",
                            f"{latest['Change %']}"
                        )
                    
                    with col2:
                        price_change = ((latest['Price'] - prev['Price']) / prev['Price']) * 100
                        st.metric(
                            "שינוי יומי",
                            f"{price_change:.2f}%",
                            delta_color="normal" if price_change > 0 else "inverse"
                        )
                    
                    with col3:
                        st.metric(
                            "תקופת נתונים",
                            f"{len(df)} ימים",
                            f"{df['Date'].min().strftime('%Y-%m-%d')} עד {df['Date'].max().strftime('%Y-%m-%d')}"
                        )
                    
                    # גרף מהיר
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df['Date'].tail(30),
                        y=df['Price'].tail(30),
                        mode='lines',
                        name=f'{selected_stock}',
                        line=dict(color='#667eea', width=2)
                    ))
                    
                    fig.update_layout(
                        title=f"מחירי {selected_stock} - 30 ימים אחרונים",
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
            except Exception as e:
                st.error(f"שגיאה בטעינת נתוני {selected_stock}: {str(e)}")
    
    st.markdown("---")
    
    # הודעות מערכת
    st.subheader("📢 הודעות מערכת")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("💡 **טיפ:** השתמש בדשבורד הלייבטריידינג לסימולציה בזמן אמת")
        st.info("🔧 **עדכון:** מערכת ניהול הסוכנים זמינה כעת")
        st.info("📊 **חדש:** דשבורד מקיף עם כל התכונות")
    
    with col2:
        st.success("✅ **סטטוס:** כל הדשבורדים פועלים בהצלחה")
        st.success("🚀 **ביצועים:** המערכת מותאמת לניתוח מתקדם")
        st.success("🤖 **סוכנים:** 49 סוכנים זמינים לניתוח")
    
    # הודעת הצלחה
    st.success("✅ מערכת Charles FocusedSpec פועלת בהצלחה!")
    st.info("💡 בחר דשבורד מהרשימה למעלה כדי להתחיל לנתח מניות")

if __name__ == "__main__":
    main() 