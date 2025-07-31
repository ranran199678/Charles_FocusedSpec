#!/usr/bin/env python3
"""
דשבורד פשוט לבדיקה
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# הגדרת דף
st.set_page_config(
    page_title="Charles FocusedSpec - דשבורד בדיקה",
    page_icon="📈",
    layout="wide"
)

# כותרת
st.title("📈 Charles FocusedSpec - דשבורד ניתוח מניות")
st.markdown("---")

# סיידבר
st.sidebar.header("הגדרות")
symbol = st.sidebar.text_input("סמל מניה", value="AAPL")
days = st.sidebar.slider("מספר ימים", min_value=30, max_value=365, value=90)

# תוכן ראשי
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 מידע כללי")
    st.write(f"**סמל מניה:** {symbol}")
    st.write(f"**תקופה:** {days} ימים")
    st.write(f"**תאריך:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col2:
    st.subheader("📈 סטטיסטיקות")
    st.metric("מחיר נוכחי", "$150.00", "+2.5%")
    st.metric("נפח מסחר", "50M", "+10%")
    st.metric("RSI", "65", "-5")

# גרף דוגמה
st.subheader("📊 גרף מחירים")
dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
prices = [100 + i * 0.5 + np.random.normal(0, 2) for i in range(days)]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates,
    y=prices,
    mode='lines',
    name='מחיר',
    line=dict(color='blue', width=2)
))

fig.update_layout(
    title=f"מחירי {symbol} - {days} ימים אחרונים",
    xaxis_title="תאריך",
    yaxis_title="מחיר ($)",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# טבלת נתונים
st.subheader("📋 נתונים אחרונים")
data = pd.DataFrame({
    'תאריך': dates[-10:],
    'מחיר': prices[-10:],
    'שינוי (%)': [round((prices[i] - prices[i-1]) / prices[i-1] * 100, 2) for i in range(1, len(prices[-10:]))] + [0]
})

st.dataframe(data, use_container_width=True)

# הודעת הצלחה
st.success("✅ הדשבורד פועל בהצלחה!")
st.info("💡 זהו דשבורד בדיקה פשוט. הדשבורד המלא כולל ניתוחים מתקדמים יותר.") 