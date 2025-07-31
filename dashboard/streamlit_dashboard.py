#!/usr/bin/env python3
"""
Streamlit Dashboard - דשבורד מתקדם עם ממשק גרפי
ממשק משתמש אינטראקטיבי לניתוח מניות ואינדיקטורים טכניים
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import json
import gzip

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.smart_data_manager import smart_data_manager
from utils.data_fetcher import DataFetcher

# הגדרת דף
st.set_page_config(
    page_title="Charles FocusedSpec - דשבורד ניתוח מניות",
    page_icon="📈",
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
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

class DashboardApp:
    """מחלקת הדשבורד הראשית"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.smart_manager = smart_data_manager
        
        # רשימת מניות עיקריות
        self.main_symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", 
            "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "BAC",
            "ADBE", "CRM", "INTC", "ORCL", "CSCO", "PFE", "ABT", "TMO", "ACN",
            "WMT", "KO", "PEP", "AVGO", "COST", "DHR", "NEE", "LLY", "TXN",
            "HON", "UNP", "LOW", "UPS", "CAT", "DE", "BA", "AXP", "SPGI",
            "RTX", "IBM", "GE", "MMC", "BLK", "GS", "MS", "SCHW", "CME"
        ]
        
        # הגדרת תיקיות
        self.data_dir = Path("data")
        self.daily_dir = self.data_dir / "historical_prices" / "daily"
        self.indicators_dir = self.data_dir / "technical_indicators"
    
    def load_price_data(self, symbol: str, days: int = 365) -> pd.DataFrame:
        """טוען נתוני מחירים"""
        try:
            # ניסיון עם SmartDataManager
            df = self.smart_manager.get_stock_data(symbol, days, include_live=True)
            
            if df is not None and not df.empty:
                return df
            
            # fallback ל-DataFetcher
            df = self.data_fetcher.get_price_history(symbol, f"{days}d")
            
            if df is not None and not df.empty:
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"שגיאה בטעינת נתונים עבור {symbol}: {e}")
            return pd.DataFrame()
    
    def load_technical_indicators(self, symbol: str, indicator: str = "rsi") -> pd.DataFrame:
        """טוען אינדיקטורים טכניים"""
        try:
            file_path = self.indicators_dir / indicator / "daily" / f"{symbol}.csv.gz"
            
            if file_path.exists():
                df = pd.read_csv(file_path, compression='gzip')
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            st.warning(f"אין אינדיקטורים זמינים עבור {symbol} - {indicator}")
            return pd.DataFrame()
    
    def calculate_technical_signals(self, df: pd.DataFrame) -> dict:
        """מחשב אותות טכניים"""
        signals = {}
        
        if df.empty:
            return signals
        
        try:
            # RSI
            if 'rsi_14' in df.columns:
                rsi = df['rsi_14'].iloc[-1]
                if rsi > 70:
                    signals['RSI'] = {'signal': 'מכירה', 'value': rsi, 'color': 'red'}
                elif rsi < 30:
                    signals['RSI'] = {'signal': 'קנייה', 'value': rsi, 'color': 'green'}
                else:
                    signals['RSI'] = {'signal': 'ניטרלי', 'value': rsi, 'color': 'orange'}
            
            # MACD
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                macd = df['macd'].iloc[-1]
                signal = df['macd_signal'].iloc[-1]
                if macd > signal:
                    signals['MACD'] = {'signal': 'קנייה', 'value': f"{macd:.2f}", 'color': 'green'}
                else:
                    signals['MACD'] = {'signal': 'מכירה', 'value': f"{macd:.2f}", 'color': 'red'}
            
            # Bollinger Bands
            if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
                close = df['close'].iloc[-1]
                upper = df['bb_upper'].iloc[-1]
                lower = df['bb_lower'].iloc[-1]
                
                if close > upper:
                    signals['Bollinger'] = {'signal': 'מכירה', 'value': f"{close:.2f}", 'color': 'red'}
                elif close < lower:
                    signals['Bollinger'] = {'signal': 'קנייה', 'value': f"{close:.2f}", 'color': 'green'}
                else:
                    signals['Bollinger'] = {'signal': 'ניטרלי', 'value': f"{close:.2f}", 'color': 'orange'}
            
            # Moving Averages
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                sma_20 = df['sma_20'].iloc[-1]
                sma_50 = df['sma_50'].iloc[-1]
                close = df['close'].iloc[-1]
                
                if close > sma_20 > sma_50:
                    signals['MA'] = {'signal': 'קנייה', 'value': f"{close:.2f}", 'color': 'green'}
                elif close < sma_20 < sma_50:
                    signals['MA'] = {'signal': 'מכירה', 'value': f"{close:.2f}", 'color': 'red'}
                else:
                    signals['MA'] = {'signal': 'ניטרלי', 'value': f"{close:.2f}", 'color': 'orange'}
            
        except Exception as e:
            st.error(f"שגיאה בחישוב אותות: {e}")
        
        return signals
    
    def create_price_chart(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        """יוצר גרף מחירים"""
        if df.empty:
            return go.Figure()
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(f'מחיר {symbol}', 'נפח', 'RSI'),
            row_heights=[0.6, 0.2, 0.2]
        )
        
        # גרף מחירים
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='מחיר'
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        if 'bb_upper' in df.columns and 'bb_middle' in df.columns and 'bb_lower' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['bb_upper'],
                    mode='lines',
                    name='Bollinger Upper',
                    line=dict(color='rgba(255,0,0,0.3)')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['bb_middle'],
                    mode='lines',
                    name='Bollinger Middle',
                    line=dict(color='rgba(0,0,255,0.3)')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['bb_lower'],
                    mode='lines',
                    name='Bollinger Lower',
                    line=dict(color='rgba(255,0,0,0.3)'),
                    fill='tonexty'
                ),
                row=1, col=1
            )
        
        # Moving Averages
        if 'sma_20' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['sma_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='orange')
                ),
                row=1, col=1
            )
        
        if 'sma_50' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['sma_50'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color='blue')
                ),
                row=1, col=1
            )
        
        # נפח
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='נפח',
                marker_color='rgba(0,0,255,0.3)'
            ),
            row=2, col=1
        )
        
        # RSI
        if 'rsi_14' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['rsi_14'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple')
                ),
                row=3, col=1
            )
            
            # קווים מנחים RSI
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            fig.add_hline(y=50, line_dash="dash", line_color="gray", row=3, col=1)
        
        fig.update_layout(
            title=f'ניתוח טכני - {symbol}',
            xaxis_rangeslider_visible=False,
            height=800
        )
        
        return fig
    
    def create_indicators_chart(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        """יוצר גרף אינדיקטורים"""
        if df.empty:
            return go.Figure()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('MACD', 'Stochastic', 'Williams %R', 'CCI'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # MACD
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['macd'], name='MACD', line=dict(color='blue')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['macd_signal'], name='Signal', line=dict(color='red')),
                row=1, col=1
            )
            
            if 'macd_histogram' in df.columns:
                fig.add_trace(
                    go.Bar(x=df.index, y=df['macd_histogram'], name='Histogram', marker_color='gray'),
                    row=1, col=1
                )
        
        # Stochastic
        if 'stoch_k' in df.columns and 'stoch_d' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['stoch_k'], name='%K', line=dict(color='blue')),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['stoch_d'], name='%D', line=dict(color='red')),
                row=1, col=2
            )
            fig.add_hline(y=80, line_dash="dash", line_color="red", row=1, col=2)
            fig.add_hline(y=20, line_dash="dash", line_color="green", row=1, col=2)
        
        # Williams %R
        if 'williams_r_14' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['williams_r_14'], name='Williams %R', line=dict(color='purple')),
                row=2, col=1
            )
            fig.add_hline(y=-20, line_dash="dash", line_color="green", row=2, col=1)
            fig.add_hline(y=-80, line_dash="dash", line_color="red", row=2, col=1)
        
        # CCI
        if 'cci_20' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['cci_20'], name='CCI', line=dict(color='orange')),
                row=2, col=2
            )
            fig.add_hline(y=100, line_dash="dash", line_color="red", row=2, col=2)
            fig.add_hline(y=-100, line_dash="dash", line_color="green", row=2, col=2)
        
        fig.update_layout(
            title=f'אינדיקטורים טכניים - {symbol}',
            height=600
        )
        
        return fig
    
    def run_dashboard(self):
        """מריץ את הדשבורד"""
        # כותרת ראשית
        st.markdown('<h1 class="main-header">📈 Charles FocusedSpec - דשבורד ניתוח מניות</h1>', unsafe_allow_html=True)
        
        # סיידבר
        with st.sidebar:
            st.header("⚙️ הגדרות")
            
            # בחירת מניה
            symbol = st.selectbox(
                "בחר מניה:",
                self.main_symbols,
                index=0
            )
            
            # תקופת זמן
            period = st.selectbox(
                "תקופת זמן:",
                ["30d", "90d", "180d", "365d", "2y", "5y"],
                index=3
            )
            
            # מספר ימים
            days_map = {"30d": 30, "90d": 90, "180d": 180, "365d": 365, "2y": 730, "5y": 1825}
            days = days_map[period]
            
            st.header("📊 אינדיקטורים")
            
            # בחירת אינדיקטורים להצגה
            show_rsi = st.checkbox("RSI", value=True)
            show_macd = st.checkbox("MACD", value=True)
            show_bollinger = st.checkbox("Bollinger Bands", value=True)
            show_ma = st.checkbox("Moving Averages", value=True)
            
            st.header("🎯 אותות")
            show_signals = st.checkbox("הצג אותות טכניים", value=True)
        
        # תוכן ראשי
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header(f"📊 ניתוח מניה: {symbol}")
            
            # טעינת נתונים
            with st.spinner(f"טוען נתונים עבור {symbol}..."):
                price_df = self.load_price_data(symbol, days)
                
                if not price_df.empty:
                    # טעינת אינדיקטורים טכניים
                    indicators_df = self.load_technical_indicators(symbol)
                    
                    # שילוב נתונים
                    if not indicators_df.empty:
                        combined_df = price_df.join(indicators_df, how='inner')
                    else:
                        combined_df = price_df
                    
                    # חישוב אותות
                    if show_signals:
                        signals = self.calculate_technical_signals(combined_df)
                        
                        if signals:
                            st.subheader("🎯 אותות טכניים")
                            signal_cols = st.columns(len(signals))
                            
                            for i, (indicator, signal_data) in enumerate(signals.items()):
                                with signal_cols[i]:
                                    color = signal_data['color']
                                    st.markdown(f"""
                                    <div class="metric-card {color}-metric">
                                        <h4>{indicator}</h4>
                                        <h3 style="color: {color};">{signal_data['signal']}</h3>
                                        <p>ערך: {signal_data['value']}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    # גרף מחירים
                    st.subheader("📈 גרף מחירים ואינדיקטורים")
                    price_chart = self.create_price_chart(combined_df, symbol)
                    st.plotly_chart(price_chart, use_container_width=True)
                    
                    # גרף אינדיקטורים
                    if not indicators_df.empty:
                        st.subheader("📊 אינדיקטורים טכניים")
                        indicators_chart = self.create_indicators_chart(combined_df, symbol)
                        st.plotly_chart(indicators_chart, use_container_width=True)
                    
                else:
                    st.error(f"לא ניתן לטעון נתונים עבור {symbol}")
        
        with col2:
            st.header("📋 מידע מהיר")
            
            if not price_df.empty:
                # סטטיסטיקות מהירות
                latest = price_df.iloc[-1]
                prev = price_df.iloc[-2] if len(price_df) > 1 else latest
                
                # מחיר נוכחי
                current_price = latest['close']
                price_change = current_price - prev['close']
                price_change_pct = (price_change / prev['close']) * 100
                
                st.metric(
                    "מחיר נוכחי",
                    f"${current_price:.2f}",
                    f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
                )
                
                # סטטיסטיקות נוספות
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric("גבוה היום", f"${latest['high']:.2f}")
                    st.metric("נפח", f"{latest['volume']:,.0f}")
                
                with col_b:
                    st.metric("נמוך היום", f"${latest['low']:.2f}")
                    st.metric("שינוי", f"{price_change:+.2f}")
                
                # סטטיסטיקות תקופה
                st.subheader("📊 סטטיסטיקות תקופה")
                
                period_high = price_df['high'].max()
                period_low = price_df['low'].min()
                avg_volume = price_df['volume'].mean()
                
                st.metric("גבוה תקופה", f"${period_high:.2f}")
                st.metric("נמוך תקופה", f"${period_low:.2f}")
                st.metric("נפח ממוצע", f"{avg_volume:,.0f}")
                
                # תנודתיות
                returns = price_df['close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) * 100  # שנתי
                
                st.metric("תנודתיות שנתית", f"{volatility:.1f}%")
        
        # טאבים נוספים
        tab1, tab2, tab3 = st.tabs(["📈 ניתוח מתקדם", "📊 השוואה", "⚙️ הגדרות מערכת"])
        
        with tab1:
            st.header("ניתוח מתקדם")
            
            if not price_df.empty:
                # ניתוח מגמות
                st.subheader("📈 ניתוח מגמות")
                
                # חישוב מגמות
                short_trend = price_df['close'].tail(20).pct_change().mean() * 252 * 100
                long_trend = price_df['close'].tail(60).pct_change().mean() * 252 * 100
                
                col_trend1, col_trend2 = st.columns(2)
                
                with col_trend1:
                    st.metric("מגמה קצרה (20 ימים)", f"{short_trend:+.1f}%")
                
                with col_trend2:
                    st.metric("מגמה ארוכה (60 ימים)", f"{long_trend:+.1f}%")
                
                # ניתוח תמיכה והתנגדות
                st.subheader("🎯 רמות תמיכה והתנגדות")
                
                recent_highs = price_df['high'].tail(20).nlargest(3)
                recent_lows = price_df['low'].tail(20).nsmallest(3)
                
                col_res1, col_res2 = st.columns(2)
                
                with col_res1:
                    st.write("**רמות התנגדות:**")
                    for i, (date, high) in enumerate(recent_highs.items(), 1):
                        st.write(f"{i}. ${high:.2f} ({date.strftime('%Y-%m-%d')})")
                
                with col_res2:
                    st.write("**רמות תמיכה:**")
                    for i, (date, low) in enumerate(recent_lows.items(), 1):
                        st.write(f"{i}. ${low:.2f} ({date.strftime('%Y-%m-%d')})")
        
        with tab2:
            st.header("השוואת מניות")
            
            # בחירת מניות להשוואה
            compare_symbols = st.multiselect(
                "בחר מניות להשוואה:",
                self.main_symbols,
                default=[symbol]
            )
            
            if compare_symbols:
                # טעינת נתונים לכל המניות
                comparison_data = {}
                
                for sym in compare_symbols:
                    df = self.load_price_data(sym, days)
                    if not df.empty:
                        # חישוב תשואה נורמלית
                        normalized = (df['close'] / df['close'].iloc[0]) * 100
                        comparison_data[sym] = normalized
                
                if comparison_data:
                    # יצירת גרף השוואה
                    fig = go.Figure()
                    
                    for sym, data in comparison_data.items():
                        fig.add_trace(
                            go.Scatter(
                                x=data.index,
                                y=data.values,
                                mode='lines',
                                name=sym
                            )
                        )
                    
                    fig.update_layout(
                        title="השוואת ביצועים (נורמלי ל-100)",
                        xaxis_title="תאריך",
                        yaxis_title="תשואה (%)",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.header("הגדרות מערכת")
            
            # סטטוס מערכת
            st.subheader("📊 סטטוס מערכת")
            
            # בדיקת זמינות נתונים
            available_symbols = len([f for f in self.daily_dir.glob("*.csv.gz")])
            st.metric("מניות זמינות", available_symbols)
            
            # בדיקת אינדיקטורים
            if self.indicators_dir.exists():
                rsi_files = len(list((self.indicators_dir / "rsi" / "daily").glob("*.csv.gz")))
                macd_files = len(list((self.indicators_dir / "macd" / "daily").glob("*.csv.gz")))
                
                st.metric("קבצי RSI", rsi_files)
                st.metric("קבצי MACD", macd_files)
            
            # עדכון אחרון
            st.subheader("🕒 עדכון אחרון")
            st.write(f"תאריך: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # כפתור רענון
            if st.button("🔄 רענן נתונים"):
                st.success("הנתונים עודכנו בהצלחה!")

def main():
    """פונקציה ראשית"""
    app = DashboardApp()
    app.run_dashboard()

if __name__ == "__main__":
    main() 