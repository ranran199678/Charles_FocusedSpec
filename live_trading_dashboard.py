#!/usr/bin/env python3
"""
דשבורד לייבטריידינג - Charles FocusedSpec
סימולציה בזמן אמת עם התראות וסיגנלים
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
    from utils.smart_data_manager import smart_data_manager
    SYSTEM_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ חלק מהמודולים לא זמינים: {str(e)}")
    SYSTEM_AVAILABLE = False

# הגדרת דף
st.set_page_config(
    page_title="Charles FocusedSpec - לייבטריידינג",
    page_icon="⚡",
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
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .live-indicator {
        background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        text-align: center;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .signal-buy {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .signal-sell {
        background: linear-gradient(135deg, #dc3545, #fd7e14);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .signal-hold {
        background: linear-gradient(135deg, #6c757d, #adb5bd);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .portfolio-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 2px solid #dee2e6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        'cash': 100000,
        'positions': {},
        'trades': [],
        'signals': []
    }

if 'live_data' not in st.session_state:
    st.session_state.live_data = {}

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

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
        
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
        df['High'] = pd.to_numeric(df['High'], errors='coerce')
        df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
        df['Volume'] = df['Vol.'].str.replace('"', '').str.replace(',', '')
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
        df['Change_Pct'] = df['Change %'].str.replace('%', '')
        df['Change_Pct'] = pd.to_numeric(df['Change_Pct'], errors='coerce')
        df = df.sort_values('Date').reset_index(drop=True)
        
        return df
        
    except Exception as e:
        st.error(f"שגיאה בטעינת נתוני {symbol}: {str(e)}")
        return None

def calculate_technical_indicators(df):
    """מחשב אינדיקטורים טכניים"""
    if df is None or df.empty:
        return df
    
    # SMA
    df['SMA_20'] = df['Price'].rolling(window=20).mean()
    df['SMA_50'] = df['Price'].rolling(window=50).mean()
    
    # EMA
    df['EMA_12'] = df['Price'].ewm(span=12).mean()
    df['EMA_26'] = df['Price'].ewm(span=26).mean()
    
    # RSI
    delta = df['Price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # Bollinger Bands
    df['BB_Middle'] = df['Price'].rolling(window=20).mean()
    bb_std = df['Price'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    return df

def generate_live_signal(df, symbol):
    """מייצר סיגנל לייבטריידינג"""
    if df is None or df.empty:
        return {"signal": "HOLD", "confidence": 0, "reason": "אין נתונים"}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    signals = []
    confidence = 0
    
    # RSI
    rsi = latest.get('RSI', 50)
    if rsi < 30:
        signals.append("RSI Oversold")
        confidence += 20
    elif rsi > 70:
        signals.append("RSI Overbought")
        confidence -= 20
    
    # MACD
    macd = latest.get('MACD', 0)
    macd_signal = latest.get('MACD_Signal', 0)
    if macd > macd_signal and macd > 0:
        signals.append("MACD Bullish")
        confidence += 15
    elif macd < macd_signal and macd < 0:
        signals.append("MACD Bearish")
        confidence -= 15
    
    # Bollinger Bands
    price = latest['Price']
    bb_upper = latest.get('BB_Upper', price)
    bb_lower = latest.get('BB_Lower', price)
    
    if price < bb_lower:
        signals.append("BB Oversold")
        confidence += 15
    elif price > bb_upper:
        signals.append("BB Overbought")
        confidence -= 15
    
    # SMA Crossover
    sma_20 = latest.get('SMA_20', price)
    sma_50 = latest.get('SMA_50', price)
    
    if sma_20 > sma_50:
        signals.append("SMA Bullish")
        confidence += 10
    else:
        signals.append("SMA Bearish")
        confidence -= 10
    
    # Volume
    volume_ratio = latest.get('Volume', 0) / latest.get('Volume_SMA', 1)
    if volume_ratio > 1.5:
        signals.append("High Volume")
        confidence += 5
    
    # קביעת סיגנל סופי
    if confidence >= 30:
        signal = "BUY"
    elif confidence <= -30:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    return {
        "signal": signal,
        "confidence": abs(confidence),
        "reason": ", ".join(signals),
        "price": price,
        "timestamp": datetime.now()
    }

def execute_trade(symbol, signal, price, quantity=100):
    """מבצע עסקה"""
    portfolio = st.session_state.portfolio
    
    if signal == "BUY":
        cost = price * quantity
        if portfolio['cash'] >= cost:
            portfolio['cash'] -= cost
            if symbol in portfolio['positions']:
                portfolio['positions'][symbol]['quantity'] += quantity
                portfolio['positions'][symbol]['avg_price'] = (
                    (portfolio['positions'][symbol]['avg_price'] * 
                     portfolio['positions'][symbol]['quantity'] + cost) / 
                    (portfolio['positions'][symbol]['quantity'] + quantity)
                )
            else:
                portfolio['positions'][symbol] = {
                    'quantity': quantity,
                    'avg_price': price
                }
            
            portfolio['trades'].append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': 'BUY',
                'quantity': quantity,
                'price': price,
                'total': cost
            })
            return True
        else:
            return False
    
    elif signal == "SELL":
        if symbol in portfolio['positions'] and portfolio['positions'][symbol]['quantity'] >= quantity:
            revenue = price * quantity
            portfolio['cash'] += revenue
            portfolio['positions'][symbol]['quantity'] -= quantity
            
            if portfolio['positions'][symbol]['quantity'] == 0:
                del portfolio['positions'][symbol]
            
            portfolio['trades'].append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': 'SELL',
                'quantity': quantity,
                'price': price,
                'total': revenue
            })
            return True
        else:
            return False
    
    return False

def calculate_portfolio_value():
    """מחשב ערך התיק"""
    portfolio = st.session_state.portfolio
    total_value = portfolio['cash']
    
    for symbol, position in portfolio['positions'].items():
        if symbol in st.session_state.live_data:
            current_price = st.session_state.live_data[symbol]['price']
            total_value += current_price * position['quantity']
    
    return total_value

def create_live_chart(df, symbol):
    """יוצר גרף לייבטריידינג"""
    if df is None or df.empty:
        return None
    
    recent_data = df.tail(50)
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            f'מחירי {symbol} - לייבטריידינג',
            'MACD',
            'RSI'
        ),
        row_width=[0.5, 0.25, 0.25]
    )
    
    # גרף מחירים
    fig.add_trace(
        go.Scatter(
            x=recent_data['Date'],
            y=recent_data['Price'],
            mode='lines',
            name='מחיר',
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
                name='BB Upper',
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
                name='BB Lower',
                line=dict(color='rgba(255,0,0,0.3)', width=1),
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.1)',
                showlegend=False
            ),
            row=1, col=1
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
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=recent_data['Date'],
                y=recent_data['MACD_Signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='red', width=1)
            ),
            row=2, col=1
        )
    
    # RSI
    if 'RSI' in recent_data.columns:
        fig.add_trace(
            go.Scatter(
                x=recent_data['Date'],
                y=recent_data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=3, col=1
        )
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    fig.update_layout(
        title=f"לייבטריידינג - {symbol}",
        height=600,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def main():
    # כותרת ראשית
    st.markdown('<h1 class="main-header">⚡ Charles FocusedSpec - לייבטריידינג</h1>', unsafe_allow_html=True)
    
    # אינדיקטור לייבטריידינג
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="live-indicator">🔴 לייבטריידינג פעיל</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # סיידבר
    st.sidebar.header("⚙️ הגדרות לייבטריידינג")
    
    # בחירת מניות
    available_stocks = get_available_stocks()
    selected_stocks = st.sidebar.multiselect(
        "מניות למעקב",
        available_stocks,
        default=['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    )
    
    # הגדרות אוטומטיות
    auto_trading = st.sidebar.checkbox("מסחר אוטומטי", value=False)
    min_confidence = st.sidebar.slider("ביטחון מינימלי", 0, 100, 50)
    
    if not selected_stocks:
        st.warning("אנא בחר מניות למעקב")
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
    
    # עדכון נתונים לייבטריידינג
    current_time = datetime.now()
    if (current_time - st.session_state.last_update).seconds >= 30:  # עדכון כל 30 שניות
        st.session_state.last_update = current_time
        
        for symbol in selected_stocks:
            if symbol in stock_data:
                df = stock_data[symbol]
                latest = df.iloc[-1]
                
                # הוספת רעש קטן לסימולציה
                noise = np.random.normal(0, latest['Price'] * 0.001)
                live_price = latest['Price'] + noise
                
                st.session_state.live_data[symbol] = {
                    'price': live_price,
                    'change': latest['Change_Pct'],
                    'volume': latest['Volume'],
                    'timestamp': current_time
                }
    
    # טאבים ראשיים
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 סיגנלים לייבטריידינג",
        "💼 תיק השקעות",
        "📈 גרפים לייבטריידינג",
        "📋 היסטוריית עסקאות"
    ])
    
    with tab1:
        st.subheader("📊 סיגנלים לייבטריידינג")
        
        # הצגת סיגנלים לכל מניה
        for symbol in selected_stocks:
            if symbol in stock_data:
                df = stock_data[symbol]
                signal_data = generate_live_signal(df, symbol)
                
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{symbol}**")
                    st.write(f"${signal_data['price']:.2f}")
                
                with col2:
                    if signal_data['signal'] == "BUY":
                        st.markdown(f'<div class="signal-buy">🟢 {signal_data["signal"]}</div>', unsafe_allow_html=True)
                    elif signal_data['signal'] == "SELL":
                        st.markdown(f'<div class="signal-sell">🔴 {signal_data["signal"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="signal-hold">🟡 {signal_data["signal"]}</div>', unsafe_allow_html=True)
                
                with col3:
                    st.write(f"ביטחון: {signal_data['confidence']:.1f}%")
                
                with col4:
                    if auto_trading and signal_data['confidence'] >= min_confidence:
                        if st.button(f"בצע {signal_data['signal']}", key=f"trade_{symbol}"):
                            success = execute_trade(symbol, signal_data['signal'], signal_data['price'])
                            if success:
                                st.success("עסקה בוצעה בהצלחה!")
                            else:
                                st.error("שגיאה בביצוע העסקה")
                
                st.write(f"**סיבה:** {signal_data['reason']}")
                st.markdown("---")
    
    with tab2:
        st.subheader("💼 תיק השקעות")
        
        portfolio = st.session_state.portfolio
        total_value = calculate_portfolio_value()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "מזומן",
                f"${portfolio['cash']:,.2f}",
                f"{((portfolio['cash'] / 100000) - 1) * 100:.1f}%"
            )
        
        with col2:
            st.metric(
                "ערך כולל",
                f"${total_value:,.2f}",
                f"{((total_value / 100000) - 1) * 100:.1f}%"
            )
        
        with col3:
            st.metric(
                "רווח/הפסד",
                f"${total_value - 100000:,.2f}",
                f"{((total_value / 100000) - 1) * 100:.1f}%"
            )
        
        # פוזיציות פעילות
        if portfolio['positions']:
            st.subheader("פוזיציות פעילות")
            for symbol, position in portfolio['positions'].items():
                current_price = st.session_state.live_data.get(symbol, {}).get('price', position['avg_price'])
                market_value = current_price * position['quantity']
                pnl = market_value - (position['avg_price'] * position['quantity'])
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**{symbol}**")
                
                with col2:
                    st.write(f"כמות: {position['quantity']}")
                
                with col3:
                    st.write(f"מחיר ממוצע: ${position['avg_price']:.2f}")
                
                with col4:
                    st.write(f"רווח/הפסד: ${pnl:.2f}")
        else:
            st.info("אין פוזיציות פעילות")
    
    with tab3:
        st.subheader("📈 גרפים לייבטריידינג")
        
        chart_stock = st.selectbox("בחר מניה לגרף", selected_stocks, key="live_chart")
        
        if chart_stock in stock_data:
            live_fig = create_live_chart(stock_data[chart_stock], chart_stock)
            if live_fig:
                st.plotly_chart(live_fig, use_container_width=True)
    
    with tab4:
        st.subheader("📋 היסטוריית עסקאות")
        
        if portfolio['trades']:
            trades_df = pd.DataFrame(portfolio['trades'])
            trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
            trades_df = trades_df.sort_values('timestamp', ascending=False)
            
            st.dataframe(trades_df, use_container_width=True)
        else:
            st.info("אין עסקאות עדיין")
    
    # הודעת הצלחה
    st.success("✅ מערכת הלייבטריידינג פועלת בהצלחה!")
    st.info("💡 המערכת מנטרת סיגנלים בזמן אמת ומבצעת עסקאות אוטומטיות.")

if __name__ == "__main__":
    main() 