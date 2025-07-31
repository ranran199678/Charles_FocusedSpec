#!/usr/bin/env python3
"""
דשבורד משופר עם נתונים אמיתיים
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import os

# הגדרת דף
st.set_page_config(
    page_title="Charles FocusedSpec - דשבורד ניתוח מניות",
    page_icon="📈",
    layout="wide"
)

# CSS מותאם אישית
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
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
</style>
""", unsafe_allow_html=True)

def load_aapl_data():
    """טוען נתוני AAPL מהקובץ"""
    try:
        # קריאת הקובץ
        file_path = "data/raw_price_data/AAPL Stock Price History.csv"
        if not os.path.exists(file_path):
            st.error(f"קובץ לא נמצא: {file_path}")
            return None
        
        # קריאת הנתונים
        df = pd.read_csv(file_path)
        
        # המרת עמודת התאריך
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
        
        # המרת עמודות מספריות
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
        df['High'] = pd.to_numeric(df['High'], errors='coerce')
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
        
        # ניקוי עמודת נפח
        df['Volume'] = df['Vol.'].str.replace('"', '').str.replace(',', '')
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
        
        # ניקוי עמודת שינוי
        df['Change_Pct'] = df['Change %'].str.replace('%', '')
        df['Change_Pct'] = pd.to_numeric(df['Change_Pct'], errors='coerce')
        
        # מיון לפי תאריך
        df = df.sort_values('Date').reset_index(drop=True)
        
        return df
        
    except Exception as e:
        st.error(f"שגיאה בטעינת הנתונים: {str(e)}")
        return None

def calculate_technical_indicators(df):
    """מחשב אינדיקטורים טכניים"""
    if df is None or df.empty:
        return df
    
    # SMA 20
    df['SMA_20'] = df['Price'].rolling(window=20).mean()
    
    # SMA 50
    df['SMA_50'] = df['Price'].rolling(window=50).mean()
    
    # RSI
    delta = df['Price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['Price'].rolling(window=20).mean()
    bb_std = df['Price'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    return df

def create_price_chart(df, symbol="AAPL"):
    """יוצר גרף מחירים מתקדם"""
    if df is None or df.empty:
        return None
    
    # בחירת נתונים אחרונים
    recent_data = df.tail(100)
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'מחירי {symbol}', 'נפח מסחר'),
        row_width=[0.7, 0.3]
    )
    
    # גרף מחירים
    fig.add_trace(
        go.Scatter(
            x=recent_data['Date'],
            y=recent_data['Price'],
            mode='lines',
            name='מחיר סגירה',
            line=dict(color='#1f77b4', width=2)
        ),
        row=1, col=1
    )
    
    # Bollinger Bands
    if 'BB_Upper' in recent_data.columns:
        fig.add_trace(
            go.Scatter(
                x=recent_data['Date'],
                y=recent_data['BB_Upper'],
                mode='lines',
                name='Bollinger Upper',
                line=dict(color='rgba(255,0,0,0.3)', width=1),
                showlegend=False
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=recent_data['Date'],
                y=recent_data['BB_Lower'],
                mode='lines',
                name='Bollinger Lower',
                line=dict(color='rgba(255,0,0,0.3)', width=1),
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.1)',
                showlegend=False
            ),
            row=1, col=1
        )
    
    # SMA
    if 'SMA_20' in recent_data.columns:
        fig.add_trace(
            go.Scatter(
                x=recent_data['Date'],
                y=recent_data['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
    
    # גרף נפח
    fig.add_trace(
        go.Bar(
            x=recent_data['Date'],
            y=recent_data['Volume'],
            name='נפח',
            marker_color='rgba(0,128,0,0.5)'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title=f"ניתוח טכני - {symbol}",
        height=600,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_rsi_chart(df, symbol="AAPL"):
    """יוצר גרף RSI"""
    if df is None or df.empty or 'RSI' not in df.columns:
        return None
    
    recent_data = df.tail(100)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=recent_data['Date'],
            y=recent_data['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='purple', width=2)
        )
    )
    
    # קווים של רמות RSI
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
    fig.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral (50)")
    
    fig.update_layout(
        title=f"RSI - {symbol}",
        height=400,
        yaxis_title="RSI",
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def main():
    # כותרת
    st.markdown('<h1 class="main-header">📈 Charles FocusedSpec - דשבורד ניתוח מניות</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # טעינת נתונים
    with st.spinner("טוען נתונים..."):
        df = load_aapl_data()
        if df is not None:
            df = calculate_technical_indicators(df)
    
    if df is None:
        st.error("לא ניתן לטעון נתונים")
        return
    
    # מידע כללי
    col1, col2, col3, col4 = st.columns(4)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    with col1:
        st.metric(
            "מחיר נוכחי",
            f"${latest['Price']:.2f}",
            f"{latest['Change_Pct']:.2f}%"
        )
    
    with col2:
        st.metric(
            "נפח מסחר",
            f"{latest['Volume']:,.0f}",
            f"{(latest['Volume'] - prev['Volume']) / prev['Volume'] * 100:.1f}%"
        )
    
    with col3:
        rsi_value = latest.get('RSI', 0)
        rsi_color = "normal"
        if rsi_value > 70:
            rsi_color = "inverse"
        elif rsi_value < 30:
            rsi_color = "normal"
        
        st.metric(
            "RSI",
            f"{rsi_value:.1f}",
            delta_color=rsi_color
        )
    
    with col4:
        sma_20 = latest.get('SMA_20', 0)
        price_vs_sma = ((latest['Price'] - sma_20) / sma_20) * 100
        st.metric(
            "מחיר vs SMA 20",
            f"{price_vs_sma:.1f}%",
            delta_color="normal" if price_vs_sma > 0 else "inverse"
        )
    
    # גרפים
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 גרף מחירים וטכני")
        price_fig = create_price_chart(df)
        if price_fig:
            st.plotly_chart(price_fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 RSI")
        rsi_fig = create_rsi_chart(df)
        if rsi_fig:
            st.plotly_chart(rsi_fig, use_container_width=True)
    
    # טבלת נתונים אחרונים
    st.subheader("📋 נתונים אחרונים")
    display_cols = ['Date', 'Price', 'Open', 'High', 'Low', 'Volume', 'Change_Pct']
    available_cols = [col for col in display_cols if col in df.columns]
    
    recent_data = df[available_cols].tail(10).copy()
    recent_data['Date'] = recent_data['Date'].dt.strftime('%Y-%m-%d')
    recent_data['Price'] = recent_data['Price'].round(2)
    recent_data['Open'] = recent_data['Open'].round(2)
    recent_data['High'] = recent_data['High'].round(2)
    recent_data['Low'] = recent_data['Low'].round(2)
    recent_data['Volume'] = recent_data['Volume'].apply(lambda x: f"{x:,.0f}")
    recent_data['Change_Pct'] = recent_data['Change_Pct'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(recent_data, use_container_width=True)
    
    # סטטיסטיקות
    st.subheader("📊 סטטיסטיקות")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**מחיר הגבוה ביותר:**")
        st.write(f"${df['High'].max():.2f}")
        
        st.write("**מחיר הנמוך ביותר:**")
        st.write(f"${df['Low'].min():.2f}")
    
    with col2:
        st.write("**מחיר ממוצע:**")
        st.write(f"${df['Price'].mean():.2f}")
        
        st.write("**סטיית תקן:**")
        st.write(f"${df['Price'].std():.2f}")
    
    with col3:
        st.write("**נפח ממוצע:**")
        st.write(f"{df['Volume'].mean():,.0f}")
        
        st.write("**תקופה:**")
        st.write(f"{df['Date'].min().strftime('%Y-%m-%d')} עד {df['Date'].max().strftime('%Y-%m-%d')}")
    
    # הודעת הצלחה
    st.success("✅ הדשבורד פועל בהצלחה עם נתונים אמיתיים!")
    st.info("💡 הדשבורד מציג נתונים אמיתיים של AAPL עם ניתוח טכני מתקדם.")

if __name__ == "__main__":
    main() 