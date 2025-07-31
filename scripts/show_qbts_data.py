import sys
import os
sys.path.append('.')

from utils.data_fetcher import DataFetcher
import pandas as pd

def show_qbts_data():
    print("=== נתונים גולמיים של QBTS ===")
    
    # יצירת DataFetcher
    data_fetcher = DataFetcher()
    
    symbol = "QBTS"
    
    try:
        # קבלת נתוני מחיר
        price_df = data_fetcher.get_price_history(symbol, period="100d")
        
        if price_df is None or len(price_df) < 50:
            print(f"אין מספיק נתונים עבור {symbol}")
            return
        
        print(f"סה\"כ ימים: {len(price_df)}")
        print(f"תקופה: {price_df.index[0].strftime('%Y-%m-%d')} עד {price_df.index[-1].strftime('%Y-%m-%d')}")
        
        # סטטיסטיקות בסיסיות
        print(f"\n=== סטטיסטיקות בסיסיות ===")
        print(f"מחיר גבוה ביותר: ${price_df['high'].max():.2f}")
        print(f"מחיר נמוך ביותר: ${price_df['low'].min():.2f}")
        print(f"מחיר נוכחי: ${price_df['close'].iloc[-1]:.2f}")
        print(f"נפח ממוצע: {price_df['volume'].mean():,.0f}")
        print(f"נפח נוכחי: {price_df['volume'].iloc[-1]:,.0f}")
        
        # 10 הימים האחרונים
        print(f"\n=== 10 הימים האחרונים ===")
        recent_data = price_df.tail(10)
        for i, (date, row) in enumerate(recent_data.iterrows(), 1):
            change = (row['close'] / row['open'] - 1) * 100
            body = row['close'] - row['open']
            print(f"{i:2d}. {date.strftime('%Y-%m-%d')}: Open=${row['open']:.2f}, Close=${row['close']:.2f}, Change={change:+.2f}%, Volume={row['volume']:,.0f}")
        
        # חישובי ביצועים
        print(f"\n=== חישובי ביצועים ===")
        current_price = price_df['close'].iloc[-1]
        
        # ביצועים ב-20 ימים
        price_20d_ago = price_df['close'].iloc[-20]
        performance_20d = (current_price / price_20d_ago - 1) * 100
        
        # ביצועים ב-50 ימים
        price_50d_ago = price_df['close'].iloc[-50]
        performance_50d = (current_price / price_50d_ago - 1) * 100
        
        print(f"ביצועים 20 ימים: {performance_20d:+.2f}%")
        print(f"ביצועים 50 ימים: {performance_50d:+.2f}%")
        
        # תנודתיות
        returns = price_df['close'].pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5)  # שנתי
        print(f"תנודתיות שנתית: {volatility:.2%}")
        
        # נרות אחרונים לניתוח תבניות
        print(f"\n=== 5 הנרות האחרונים לניתוח תבניות ===")
        last_5_candles = price_df.tail(5)
        for i, (date, row) in enumerate(last_5_candles.iterrows(), 1):
            body = row['close'] - row['open']
            body_size = abs(body) / row['open'] * 100
            upper_shadow = row['high'] - max(row['open'], row['close'])
            lower_shadow = min(row['open'], row['close']) - row['low']
            
            print(f"נר {i}: {date.strftime('%Y-%m-%d')}")
            print(f"  Open: ${row['open']:.2f}, Close: ${row['close']:.2f}")
            print(f"  High: ${row['high']:.2f}, Low: ${row['low']:.2f}")
            print(f"  Body: {body:+.4f} ({body_size:.2f}%)")
            print(f"  Upper Shadow: {upper_shadow:.4f}")
            print(f"  Lower Shadow: {lower_shadow:.4f}")
            print(f"  Volume: {row['volume']:,.0f}")
            print()
        
        # ניתוח נפח
        print(f"\n=== ניתוח נפח ===")
        volume = price_df['volume']
        avg_volume_20 = volume.rolling(20).mean().iloc[-1]
        current_volume = volume.iloc[-1]
        volume_ratio = current_volume / avg_volume_20
        
        print(f"נפח נוכחי: {current_volume:,.0f}")
        print(f"נפח ממוצע (20 ימים): {avg_volume_20:,.0f}")
        print(f"יחס נפח: {volume_ratio:.2f}")
        
        # ניתוח מגמות
        print(f"\n=== ניתוח מגמות ===")
        close_prices = price_df['close']
        
        # SMA
        sma_20 = close_prices.rolling(20).mean().iloc[-1]
        sma_50 = close_prices.rolling(50).mean().iloc[-1]
        
        print(f"SMA 20: ${sma_20:.2f}")
        print(f"SMA 50: ${sma_50:.2f}")
        print(f"מחיר נוכחי: ${current_price:.2f}")
        
        # מיקום יחסי
        position_vs_sma20 = (current_price / sma_20 - 1) * 100
        position_vs_sma50 = (current_price / sma_50 - 1) * 100
        
        print(f"מיקום יחסי ל-SMA 20: {position_vs_sma20:+.2f}%")
        print(f"מיקום יחסי ל-SMA 50: {position_vs_sma50:+.2f}%")
        
        # RSI
        print(f"\n=== RSI ===")
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        print(f"RSI נוכחי: {current_rsi:.1f}")
        
        # תמיכה והתנגדות
        print(f"\n=== זיהוי רמות תמיכה והתנגדות ===")
        high_prices = price_df['high']
        low_prices = price_df['low']
        
        # חיפוש רמות התנגדות
        resistance_levels = []
        for i in range(2, len(high_prices) - 2):
            if (high_prices.iloc[i] >= high_prices.iloc[i-1] and 
                high_prices.iloc[i] >= high_prices.iloc[i-2] and
                high_prices.iloc[i] >= high_prices.iloc[i+1] and
                high_prices.iloc[i] >= high_prices.iloc[i+2]):
                resistance_levels.append(high_prices.iloc[i])
        
        # חיפוש רמות תמיכה
        support_levels = []
        for i in range(2, len(low_prices) - 2):
            if (low_prices.iloc[i] <= low_prices.iloc[i-1] and 
                low_prices.iloc[i] <= low_prices.iloc[i-2] and
                low_prices.iloc[i] <= low_prices.iloc[i+1] and
                low_prices.iloc[i] <= low_prices.iloc[i+2]):
                support_levels.append(low_prices.iloc[i])
        
        # הסרת כפילויות
        unique_resistance = sorted(list(set(resistance_levels)))
        unique_support = sorted(list(set(support_levels)))
        
        print(f"רמות התנגדות: {[f'${r:.2f}' for r in unique_resistance[-3:]]}")
        print(f"רמות תמיכה: {[f'${s:.2f}' for s in unique_support[-3:]]}")
        
        # מרחק מהרמות הקרובות
        if unique_resistance:
            nearest_resistance = min(unique_resistance, key=lambda x: abs(x - current_price))
            resistance_distance = (nearest_resistance - current_price) / current_price * 100
            print(f"התנגדות הקרובה: ${nearest_resistance:.2f} (מרחק: {resistance_distance:+.2f}%)")
        
        if unique_support:
            nearest_support = min(unique_support, key=lambda x: abs(x - current_price))
            support_distance = (current_price - nearest_support) / current_price * 100
            print(f"תמיכה הקרובה: ${nearest_support:.2f} (מרחק: {support_distance:+.2f}%)")
        
        # סיכום הנתונים
        print(f"\n=== סיכום הנתונים ===")
        print(f"מחיר נוכחי: ${current_price:.2f}")
        print(f"שינוי יומי: {((current_price / price_df['close'].iloc[-2] - 1) * 100):+.2f}%")
        print(f"ביצועים 20 ימים: {performance_20d:+.2f}%")
        print(f"תנודתיות: {volatility:.2%}")
        print(f"RSI: {current_rsi:.1f}")
        print(f"יחס נפח: {volume_ratio:.2f}")
        
    except Exception as e:
        print(f"שגיאה בקבלת נתונים: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_qbts_data() 