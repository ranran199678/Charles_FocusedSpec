# core/mean_reversion_detector.py

import numpy as np
import pandas as pd
from .bollinger_squeeze import BollingerSqueeze
from .rsi_sniffer import RSISniffer

class MeanReversionDetector:
    """
    סוכן זיהוי Mean Reversion - מזהה תבניות של חזרה לממוצע
    משתמש ב-BollingerSqueeze ו-RSISniffer לניתוח מקיף
    """

    def __init__(self, config=None):
        cfg = config or {}
        self.lookback_days = cfg.get("lookback_days", 60)
        self.ma_short = cfg.get("ma_short", 20)
        self.ma_long = cfg.get("ma_long", 50)
        self.rsi_period = cfg.get("rsi_period", 14)
        self.rsi_overbought = cfg.get("rsi_overbought", 70)
        self.rsi_oversold = cfg.get("rsi_oversold", 30)
        self.volatility_threshold = cfg.get("volatility_threshold", 0.02)
        self.mean_reversion_strength = cfg.get("mean_reversion_strength", 0.05)
        self.debug = cfg.get("debug", False)
        
        # אתחול סוכני המשנה
        self.bollinger_squeeze = BollingerSqueeze(config=cfg)
        self.rsi_sniffer = RSISniffer(config=cfg)

    def calculate_moving_averages(self, df):
        """מחשב ממוצעים נעים"""
        df = df.copy()
        df['ma_short'] = df['close'].rolling(window=self.ma_short).mean()
        df['ma_long'] = df['close'].rolling(window=self.ma_long).mean()
        df['ma_ratio'] = df['ma_short'] / df['ma_long']
        return df

    def detect_price_deviation(self, df):
        """מזהה סטיית מחיר מהממוצע"""
        if len(df) < self.ma_long:
            return None
        
        current_price = df['close'].iloc[-1]
        ma_long = df['ma_long'].iloc[-1]
        
        # חישוב סטייה מהממוצע
        deviation = (current_price - ma_long) / ma_long
        
        # חישוב סטייה מנורמלת (Z-score)
        price_series = df['close'].tail(self.ma_long)
        z_score = (current_price - price_series.mean()) / price_series.std()
        
        return {
            'deviation': deviation,
            'z_score': z_score,
            'current_price': current_price,
            'ma_long': ma_long,
            'is_extreme': abs(z_score) > 2
        }

    def detect_oversold_overbought(self, df):
        """מזהה מצבי oversold/overbought"""
        if len(df) < self.rsi_period:
            return None
        
        # חישוב RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        return {
            'rsi': current_rsi,
            'is_oversold': current_rsi < self.rsi_oversold,
            'is_overbought': current_rsi > self.rsi_overbought,
            'rsi_trend': 'bullish' if current_rsi > 50 else 'bearish'
        }

    def detect_volatility_contraction(self, df):
        """מזהה התכווצות תנודתיות"""
        if len(df) < 20:
            return None
        
        # חישוב תנודתיות
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=20).std()
        
        current_volatility = volatility.iloc[-1]
        avg_volatility = volatility.tail(60).mean()
        
        # בדיקה אם התנודתיות נמוכה מהממוצע
        volatility_ratio = current_volatility / avg_volatility
        
        return {
            'current_volatility': current_volatility,
            'avg_volatility': avg_volatility,
            'volatility_ratio': volatility_ratio,
            'is_contracted': volatility_ratio < 0.8
        }

    def detect_support_resistance_levels(self, df):
        """מזהה רמות תמיכה והתנגדות"""
        if len(df) < 20:
            return None
        
        highs = df['high'].tail(20)
        lows = df['low'].tail(20)
        current_price = df['close'].iloc[-1]
        
        # רמות התנגדות (peaks)
        resistance_levels = []
        for i in range(1, len(highs) - 1):
            if highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i+1]:
                resistance_levels.append(highs.iloc[i])
        
        # רמות תמיכה (troughs)
        support_levels = []
        for i in range(1, len(lows) - 1):
            if lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i+1]:
                support_levels.append(lows.iloc[i])
        
        # בדיקה אם המחיר קרוב לרמות
        near_resistance = False
        near_support = False
        
        if resistance_levels:
            closest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
            if abs(closest_resistance - current_price) / current_price < 0.02:
                near_resistance = True
        
        if support_levels:
            closest_support = min(support_levels, key=lambda x: abs(x - current_price))
            if abs(closest_support - current_price) / current_price < 0.02:
                near_support = True
        
        return {
            'near_resistance': near_resistance,
            'near_support': near_support,
            'resistance_levels': resistance_levels,
            'support_levels': support_levels
        }

    def detect_mean_reversion_patterns(self, df):
        """מזהה תבניות Mean Reversion"""
        patterns = []
        
        # תבנית 1: מחיר מתחת לממוצע + RSI oversold
        price_deviation = self.detect_price_deviation(df)
        rsi_analysis = self.detect_oversold_overbought(df)
        
        if price_deviation and rsi_analysis:
            if (price_deviation['deviation'] < -0.05 and 
                rsi_analysis['is_oversold']):
                patterns.append({
                    'type': 'oversold_bounce',
                    'strength': abs(price_deviation['deviation']) * 10,
                    'description': 'מחיר מתחת לממוצע עם RSI oversold'
                })
        
        # תבנית 2: מחיר מעל הממוצע + RSI overbought
        if price_deviation and rsi_analysis:
            if (price_deviation['deviation'] > 0.05 and 
                rsi_analysis['is_overbought']):
                patterns.append({
                    'type': 'overbought_reversal',
                    'strength': abs(price_deviation['deviation']) * 10,
                    'description': 'מחיר מעל הממוצע עם RSI overbought'
                })
        
        # תבנית 3: התכווצות תנודתיות + סטייה קיצונית
        volatility_analysis = self.detect_volatility_contraction(df)
        if volatility_analysis and price_deviation:
            if (volatility_analysis['is_contracted'] and 
                price_deviation['is_extreme']):
                patterns.append({
                    'type': 'volatility_expansion',
                    'strength': abs(price_deviation['z_score']) * 5,
                    'description': 'התכווצות תנודתיות עם סטייה קיצונית'
                })
        
        return patterns

    def calculate_mean_reversion_score(self, df):
        """מחשב ציון Mean Reversion"""
        score = 0
        score_components = {}
        
        # ניתוח Bollinger Squeeze
        bb_analysis = self.bollinger_squeeze.analyze(None, df)
        if 'score' in bb_analysis:
            score_components['bollinger_squeeze'] = bb_analysis['score'] * 0.3
            score += score_components['bollinger_squeeze']
        
        # ניתוח RSI
        rsi_analysis = self.rsi_sniffer.analyze(None, df)
        if 'score' in rsi_analysis:
            score_components['rsi_squeeze'] = rsi_analysis['score'] * 0.2
            score += score_components['rsi_squeeze']
        
        # ניתוח סטיית מחיר
        price_deviation = self.detect_price_deviation(df)
        if price_deviation and price_deviation['is_extreme']:
            score_components['price_deviation'] = min(30, abs(price_deviation['z_score']) * 10)
            score += score_components['price_deviation']
        
        # ניתוח תבניות Mean Reversion
        patterns = self.detect_mean_reversion_patterns(df)
        if patterns:
            best_pattern = max(patterns, key=lambda x: x['strength'])
            score_components['mean_reversion_patterns'] = min(20, best_pattern['strength'] * 10)
            score += score_components['mean_reversion_patterns']
        
        return min(100, score), score_components

    def analyze(self, symbol, price_df):
        """ניתוח מקיף של Mean Reversion"""
        try:
            if price_df is None or len(price_df) < self.lookback_days:
                return {
                    'symbol': symbol,
                    'score': 0,
                    'status': 'insufficient_data',
                    'message': 'נתונים לא מספיקים לניתוח'
                }
            
            # חישוב ממוצעים נעים
            df_with_ma = self.calculate_moving_averages(price_df)
            
            # ניתוחים שונים
            price_deviation = self.detect_price_deviation(df_with_ma)
            rsi_analysis = self.detect_oversold_overbought(df_with_ma)
            volatility_analysis = self.detect_volatility_contraction(df_with_ma)
            support_resistance = self.detect_support_resistance_levels(df_with_ma)
            patterns = self.detect_mean_reversion_patterns(df_with_ma)
            
            # חישוב ציון
            score, score_components = self.calculate_mean_reversion_score(df_with_ma)
            
            # קביעת סטטוס
            if score > 70:
                status = 'strong_mean_reversion'
                message = "זיהוי חזק של Mean Reversion"
            elif score > 40:
                status = 'moderate_mean_reversion'
                message = "זיהוי בינוני של Mean Reversion"
            else:
                status = 'no_mean_reversion'
                message = "אין זיהוי Mean Reversion"
            
            return {
                'symbol': symbol,
                'score': score,
                'status': status,
                'message': message,
                'price_deviation': price_deviation,
                'rsi_analysis': rsi_analysis,
                'volatility_analysis': volatility_analysis,
                'support_resistance': support_resistance,
                'patterns': patterns,
                'score_components': score_components
            }
            
        except Exception as e:
            if self.debug:
                print(f"שגיאה בניתוח Mean Reversion {symbol}: {e}")
            return {
                'symbol': symbol,
                'score': 0,
                'status': 'error',
                'message': f'שגיאה בניתוח: {str(e)}'
            }

    def run(self, price_df):
        """הרצה עם נתוני מחירים"""
        return self.analyze(None, price_df)

    def run_live(self, price_df):
        """הרצה בזמן אמת"""
        return self.analyze(None, price_df)