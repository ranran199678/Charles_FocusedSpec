#!/usr/bin/env python3
"""
דשבורד פשוט - Charles FocusedSpec
גרסה פשוטה שעובדת עם נתונים חיים
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import os
import sys
import requests
import json

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ייבוא מודולים בסיסיים
try:
    from core.adx_score_agent import ADXScoreAgent
    from core.rsi_sniffer import RSISniffer
    from core.bollinger_squeeze import BollingerSqueeze
    from core.macd_momentum_detector import MACDMomentumDetector
    from core.breakout_screener import BreakoutScreener
    from core.golden_cross_detector import GoldenCrossDetector
    from core.volume_spike_agent import VolumeSpikeAgent
    from core.trend_detector import TrendDetector
    from core.alpha_score_engine import AlphaScoreEngine
    
    AGENTS_AVAILABLE = True
except ImportError as e:
    st.error(f"שגיאה בייבוא מודולים: {e}")
    AGENTS_AVAILABLE = False

# הגדרת הדף
st.set_page_config(
    page_title="Charles FocusedSpec - דשבורד פשוט",
    page_icon="📈",
    layout="wide"
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
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown('<h1 class="main-header">📈 Charles FocusedSpec - דשבורד פשוט</h1>', unsafe_allow_html=True)

# פונקציה לטעינת נתונים חיים מ-Yahoo Finance
@st.cache_data(ttl=300)
def load_live_data_yahoo(symbol: str, days: int):
    """טעינת נתונים חיים מ-Yahoo Finance API"""
    try:
        st.info(f"🔄 שואב נתונים חיים עבור {symbol}...")
        
        # חישוב תאריכים
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 10)
        
        # המרת תאריכים ל-timestamp
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        
        # URL של Yahoo Finance
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                
                # חילוץ נתונים
                timestamps = result['timestamp']
                quotes = result['indicators']['quote'][0]
                
                # יצירת DataFrame
                df_data = {
                    'date': [datetime.fromtimestamp(ts) for ts in timestamps],
                    'open': quotes.get('open', []),
                    'high': quotes.get('high', []),
                    'low': quotes.get('low', []),
                    'close': quotes.get('close', []),
                    'volume': quotes.get('volume', [])
                }
                
                df = pd.DataFrame(df_data)
                df = df.set_index('date')
                
                # הסרת שורות עם ערכים חסרים
                df = df.dropna()
                
                if not df.empty:
                    # מיון מהחדש לישן
                    df = df.sort_index(ascending=False)
                    st.success(f"✅ נשלפו {len(df)} שורות נתונים עבור {symbol}")
                    return df
        
        st.error(f"❌ לא הצלחתי לקבל נתונים עבור {symbol}")
        return None
        
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
        agent_df = agent_df.rename(columns={
            'close': 'close',
            'open': 'open', 
            'high': 'high',
            'low': 'low',
            'volume': 'volume'
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

# סרגל צד
with st.sidebar:
    st.header("⚙️ הגדרות")
    
    # בחירת מניה
    symbol = st.text_input("סימבול מניה", value="AAPL").upper()
    
    # בחירת תקופה
    days = st.slider("מספר ימים", min_value=30, max_value=365, value=90)
    
    # בחירת סוכנים
    st.subheader("🔍 סוכנים לניתוח")
    
    use_adx = st.checkbox("ADX Score", value=True)
    use_rsi = st.checkbox("RSI Sniffer", value=True)
    use_bollinger = st.checkbox("Bollinger Squeeze", value=True)
    use_macd = st.checkbox("MACD Momentum", value=True)
    use_breakout = st.checkbox("Breakout Screener", value=True)
    use_golden_cross = st.checkbox("Golden Cross", value=True)
    use_volume_spike = st.checkbox("Volume Spike", value=True)
    use_trend = st.checkbox("Trend Detector", value=True)
    
    # כפתור הרצה
    run_analysis = st.button("🚀 הרץ ניתוח", type="primary")

# תוכן ראשי
if not AGENTS_AVAILABLE:
    st.error("❌ לא ניתן לטעון את הסוכנים. בדוק את התקנת המודולים.")
else:
    # טעינת נתונים חיים
    if run_analysis:
        with st.spinner("🔄 טוען נתונים חיים..."):
            price_df = load_live_data_yahoo(symbol, days)
        
        if price_df is not None:
            # הצגת נתונים
            st.subheader(f"📊 נתוני מחירים - {symbol}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                latest_price = price_df['close'].iloc[0]
                st.metric("מחיר נוכחי", f"${latest_price:.2f}")
            
            with col2:
                price_change = price_df['close'].iloc[0] - price_df['close'].iloc[1]
                st.metric("שינוי יומי", f"${price_change:.2f}")
            
            with col3:
                volume = price_df['volume'].iloc[0]
                st.metric("נפח", f"{volume:,.0f}")
            
            with col4:
                days_loaded = len(price_df)
                st.metric("ימים נטענו", days_loaded)
            
            # גרף מחירים
            fig = go.Figure()
            
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
            if use_trend:
                agents_to_run.append(("Trend", "Trend Detector"))
            
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
        st.info("👆 לחץ על 'הרץ ניתוח' כדי להתחיל")
        
        # הצגת מידע על המערכת
        st.subheader("ℹ️ מידע על המערכת")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 מקורות נתונים חיים:**
            - Yahoo Finance API
            - נתונים בזמן אמת
            - מטמון חכם
            
            **🔍 סוכנים טכניים:**
            - ADX Score
            - RSI Sniffer
            - Bollinger Squeeze
            - MACD Momentum
            - Breakout Screener
            - Golden Cross
            - Volume Spike
            - Trend Detector
            """)
        
        with col2:
            st.markdown("""
            **🚀 תכונות:**
            - נתונים חיים מ-Yahoo Finance
            - ניתוח טכני מתקדם
            - אלפא סקור כולל
            - גרפים אינטראקטיביים
            - תוצאות בזמן אמת
            
            **⚡ ביצועים:**
            - טעינה מהירה
            - מטמון חכם
            - עדכונים אוטומטיים
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Charles FocusedSpec - דשבורד פשוט | נתונים חיים בזמן אמת</p>
</div>
""", unsafe_allow_html=True) 