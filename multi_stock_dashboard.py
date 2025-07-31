#!/usr/bin/env python3
"""
דשבורד מתקדם עם תמיכה במניות מרובות
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

# הגדרת דף
st.set_page_config(
    page_title="Charles FocusedSpec - דשבורד ניתוח מניות מתקדם",
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

def get_available_stocks():
    """מחזיר רשימת מניות זמינות"""
    pattern = "data/raw_price_data/* Stock Price History.csv"
    files = glob.glob(pattern)
    stocks = []
    for file in files:
        stock_name = os.path.basename(file).replace(" Stock Price History.csv", "")
        stocks.append(stock_name)
    return sorted(stocks)

def load_stock_data(symbol):
    """טוען נתוני מניה ספציפית"""
    try:
        file_path = f"data/raw_price_data/{symbol} Stock Price History.csv"
        if not os.path.exists(file_path):
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
        st.error(f"שגיאה בטעינת נתוני {symbol}: {str(e)}")
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
    
    # MACD
    exp1 = df['Price'].ewm(span=12, adjust=False).mean()
    exp2 = df['Price'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    return df

def create_price_chart(df, symbol):
    """יוצר גרף מחירים מתקדם"""
    if df is None or df.empty:
        return None
    
    # בחירת נתונים אחרונים
    recent_data = df.tail(100)
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'מחירי {symbol}', 'נפח מסחר', 'MACD'),
        row_width=[0.5, 0.25, 0.25]
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
    
    if 'SMA_50' in recent_data.columns:
        fig.add_trace(
            go.Scatter(
                x=recent_data['Date'],
                y=recent_data['SMA_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='red', width=1)
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
    
    # MACD
    if 'MACD' in recent_data.columns:
        fig.add_trace(
            go.Scatter(
                x=recent_data['Date'],
                y=recent_data['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=1)
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=recent_data['Date'],
                y=recent_data['MACD_Signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='red', width=1)
            ),
            row=3, col=1
        )
    
    fig.update_layout(
        title=f"ניתוח טכני - {symbol}",
        height=800,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_rsi_chart(df, symbol):
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

def get_stock_analysis(df, symbol):
    """מחזיר ניתוח מניה"""
    if df is None or df.empty:
        return {}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    analysis = {
        'symbol': symbol,
        'current_price': latest['Price'],
        'change_pct': latest['Change_Pct'],
        'volume': latest['Volume'],
        'rsi': latest.get('RSI', 0),
        'sma_20': latest.get('SMA_20', 0),
        'sma_50': latest.get('SMA_50', 0),
        'bb_position': 0,
        'trend': 'Neutral'
    }
    
    # ניתוח Bollinger Bands
    if 'BB_Upper' in latest and 'BB_Lower' in latest:
        bb_range = latest['BB_Upper'] - latest['BB_Lower']
        if bb_range > 0:
            analysis['bb_position'] = (latest['Price'] - latest['BB_Lower']) / bb_range * 100
    
    # ניתוח מגמה
    if analysis['sma_20'] > 0 and analysis['sma_50'] > 0:
        if analysis['sma_20'] > analysis['sma_50']:
            analysis['trend'] = 'Bullish'
        else:
            analysis['trend'] = 'Bearish'
    
    return analysis

def main():
    # כותרת
    st.markdown('<h1 class="main-header">📈 Charles FocusedSpec - דשבורד ניתוח מניות מתקדם</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # סיידבר
    st.sidebar.header("הגדרות")
    
    # בחירת מניות
    available_stocks = get_available_stocks()
    selected_stocks = st.sidebar.multiselect(
        "בחר מניות לניתוח",
        available_stocks,
        default=['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    )
    
    if not selected_stocks:
        st.warning("אנא בחר לפחות מניה אחת")
        return
    
    # טעינת נתונים
    stock_data = {}
    with st.spinner("טוען נתונים..."):
        for symbol in selected_stocks:
            df = load_stock_data(symbol)
            if df is not None:
                df = calculate_technical_indicators(df)
                stock_data[symbol] = df
    
    if not stock_data:
        st.error("לא ניתן לטעון נתונים")
        return
    
    # מידע כללי על כל המניות
    st.subheader("📊 מידע כללי")
    
    # יצירת מטריקות לכל מניה
    cols = st.columns(len(selected_stocks))
    analyses = {}
    
    for i, symbol in enumerate(selected_stocks):
        if symbol in stock_data:
            df = stock_data[symbol]
            analysis = get_stock_analysis(df, symbol)
            analyses[symbol] = analysis
            
            with cols[i]:
                st.metric(
                    f"{symbol}",
                    f"${analysis['current_price']:.2f}",
                    f"{analysis['change_pct']:.2f}%"
                )
                
                # RSI
                rsi_color = "normal"
                if analysis['rsi'] > 70:
                    rsi_color = "inverse"
                elif analysis['rsi'] < 30:
                    rsi_color = "normal"
                
                st.metric(
                    "RSI",
                    f"{analysis['rsi']:.1f}",
                    delta_color=rsi_color
                )
                
                # מגמה
                trend_color = "normal" if analysis['trend'] == 'Bullish' else "inverse"
                st.metric(
                    "מגמה",
                    analysis['trend'],
                    delta_color=trend_color
                )
    
    # גרפים
    st.subheader("📈 גרפים טכניים")
    
    # בחירת מניה לגרפים
    chart_stock = st.selectbox("בחר מניה לגרפים מפורטים", selected_stocks)
    
    if chart_stock in stock_data:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            price_fig = create_price_chart(stock_data[chart_stock], chart_stock)
            if price_fig:
                st.plotly_chart(price_fig, use_container_width=True)
        
        with col2:
            rsi_fig = create_rsi_chart(stock_data[chart_stock], chart_stock)
            if rsi_fig:
                st.plotly_chart(rsi_fig, use_container_width=True)
    
    # טבלת השוואה
    st.subheader("📋 טבלת השוואה")
    
    comparison_data = []
    for symbol in selected_stocks:
        if symbol in analyses:
            analysis = analyses[symbol]
            comparison_data.append({
                'מניה': symbol,
                'מחיר נוכחי': f"${analysis['current_price']:.2f}",
                'שינוי (%)': f"{analysis['change_pct']:.2f}%",
                'RSI': f"{analysis['rsi']:.1f}",
                'מגמה': analysis['trend'],
                'BB מיקום (%)': f"{analysis['bb_position']:.1f}%"
            })
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
    
    # סטטיסטיקות
    st.subheader("📊 סטטיסטיקות")
    
    for symbol in selected_stocks:
        if symbol in stock_data:
            df = stock_data[symbol]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{symbol} - מחירים:**")
                st.write(f"גבוה: ${df['High'].max():.2f}")
                st.write(f"נמוך: ${df['Low'].min():.2f}")
                st.write(f"ממוצע: ${df['Price'].mean():.2f}")
            
            with col2:
                st.write(f"**{symbol} - נפח:**")
                st.write(f"ממוצע: {df['Volume'].mean():,.0f}")
                st.write(f"גבוה: {df['Volume'].max():,.0f}")
                st.write(f"נמוך: {df['Volume'].min():,.0f}")
            
            with col3:
                st.write(f"**{symbol} - תקופה:**")
                st.write(f"מ: {df['Date'].min().strftime('%Y-%m-%d')}")
                st.write(f"עד: {df['Date'].max().strftime('%Y-%m-%d')}")
                st.write(f"ימים: {len(df)}")
            
            st.markdown("---")
    
    # הודעת הצלחה
    st.success("✅ הדשבורד המתקדם פועל בהצלחה!")
    st.info(f"💡 הדשבורד מציג ניתוח טכני מתקדם עבור {len(selected_stocks)} מניות.")

if __name__ == "__main__":
    main() 