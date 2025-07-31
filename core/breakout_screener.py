# core/breakout_screener.py

import numpy as np
import pandas as pd
from .breakout_retest_recognizer import BreakoutRetestRecognizer
from .volume_tension_meter import VolumeTensionMeter

class BreakoutScreener:
    """
    סוכן סינון פריצות - מזהה מניות בפריצה או לפני פריצה
    משתמש ב-BreakoutRetestRecognizer ו-VolumeTensionMeter לניתוח מקיף
    """

    def __init__(self, config=None):
        cfg = config or {}
        self.lookback_days = cfg.get("lookback_days", 120)
        self.breakout_threshold = cfg.get("breakout_threshold", 0.02)  # 2% מעל התנגדות
        self.volume_threshold = cfg.get("volume_threshold", 1.5)  # נפח 1.5x מהממוצע
        self.momentum_threshold = cfg.get("momentum_threshold", 0.05)  # 5% מומנטום
        self.consolidation_days = cfg.get("consolidation_days", 20)  # ימי דשדוש מינימליים
        self.debug = cfg.get("debug", False)
        
        # אתחול סוכני המשנה
        self.breakout_recognizer = BreakoutRetestRecognizer(config=cfg)
        self.volume_meter = VolumeTensionMeter(config=cfg)

    def detect_resistance_levels(self, df, window=20):
        """מזהה רמות התנגדות משמעותיות"""
        highs = df['high']
        resistance_levels = []
        
        # חיפוש peaks מקומיים
        for i in range(window, len(df) - window):
            if highs.iloc[i] == highs.iloc[i-window:i+window+1].max():
                resistance_levels.append({
                    'price': float(highs.iloc[i]),
                    'date': df['date'].iloc[i],
                    'index': i
                })
        
        # מיון לפי מחיר וסינון רמות קרובות
        resistance_levels.sort(key=lambda x: x['price'], reverse=True)
        filtered_levels = []
        for level in resistance_levels:
            # בדיקה שאין רמה דומה כבר ברשימה
            is_unique = True
            for existing in filtered_levels:
                if abs(level['price'] - existing['price']) / existing['price'] < 0.02:
                    is_unique = False
                    break
            if is_unique:
                filtered_levels.append(level)
        
        return filtered_levels[:5]  # 5 רמות התנגדות חזקות ביותר

    def detect_consolidation(self, df, days=20):
        """מזהה תקופות דשדוש/התכווצות"""
        if len(df) < days:
            return False, 0
        
        recent_data = df.tail(days)
        highs = recent_data['high']
        lows = recent_data['low']
        closes = recent_data['close']
        
        # חישוב טווח המחירים
        price_range = (highs.max() - lows.min()) / closes.mean()
        
        # חישוב תנודתיות
        volatility = closes.pct_change().std()
        
        # בדיקה אם הטווח צר והתנודתיות נמוכה
        is_consolidation = (price_range < 0.1) and (volatility < 0.02)
        consolidation_strength = 1 - (price_range / 0.1)  # ציון 0-1
        
        return is_consolidation, consolidation_strength

    def detect_breakout_candidates(self, df):
        """מזהה מועמדים לפריצה"""
        candidates = []
        resistance_levels = self.detect_resistance_levels(df)
        
        current_price = df['close'].iloc[-1]
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].tail(20).mean()
        
        for level in resistance_levels:
            distance_to_resistance = (level['price'] - current_price) / current_price
            
            # בדיקה אם המחיר קרוב לרמת התנגדות
            if 0 < distance_to_resistance < 0.05:  # עד 5% מההתנגדות
                # בדיקת דשדוש
                is_consolidation, consolidation_strength = self.detect_consolidation(df)
                
                # בדיקת נפח
                volume_ratio = current_volume / avg_volume
                
                candidates.append({
                    'resistance_price': level['price'],
                    'current_price': current_price,
                    'distance_to_breakout': distance_to_resistance,
                    'is_consolidation': is_consolidation,
                    'consolidation_strength': consolidation_strength,
                    'volume_ratio': volume_ratio,
                    'breakout_probability': self.calculate_breakout_probability(
                        distance_to_resistance, consolidation_strength, volume_ratio
                    )
                })
        
        return candidates

    def detect_active_breakouts(self, df):
        """מזהה פריצות פעילות"""
        active_breakouts = []
        resistance_levels = self.detect_resistance_levels(df)
        
        current_price = df['close'].iloc[-1]
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].tail(20).mean()
        
        for level in resistance_levels:
            # בדיקה אם המחיר פרץ מעל ההתנגדות
            if current_price > level['price']:
                # בדיקת נפח
                volume_ratio = current_volume / avg_volume
                
                # בדיקת מומנטום
                momentum = (current_price - df['close'].iloc[-5]) / df['close'].iloc[-5]
                
                # בדיקת retest
                retest_info = self.breakout_recognizer.detect_retest(
                    df, {'idx': -1, 'price': level['price']}
                )
                
                active_breakouts.append({
                    'resistance_price': level['price'],
                    'breakout_price': current_price,
                    'breakout_percentage': (current_price - level['price']) / level['price'],
                    'volume_ratio': volume_ratio,
                    'momentum': momentum,
                    'has_retest': retest_info[0],
                    'support_held': retest_info[1] if retest_info[0] else None,
                    'breakout_strength': self.calculate_breakout_strength(
                        current_price, level['price'], volume_ratio, momentum
                    )
                })
        
        return active_breakouts

    def calculate_breakout_probability(self, distance, consolidation_strength, volume_ratio):
        """מחשב הסתברות לפריצה"""
        # ככל שהמחיר קרוב יותר להתנגדות - הסתברות גבוהה יותר
        distance_score = max(0, 1 - (distance / 0.05))
        
        # ככל שהדשדוש חזק יותר - הסתברות גבוהה יותר
        consolidation_score = consolidation_strength
        
        # ככל שהנפח גבוה יותר - הסתברות גבוהה יותר
        volume_score = min(1, volume_ratio / 2)
        
        # ממוצע משוקלל
        probability = (distance_score * 0.4 + consolidation_score * 0.4 + volume_score * 0.2)
        return min(1, probability)

    def calculate_breakout_strength(self, current_price, resistance_price, volume_ratio, momentum):
        """מחשב חוזק הפריצה"""
        # אחוז הפריצה
        breakout_percentage = (current_price - resistance_price) / resistance_price
        
        # ציון נפח
        volume_score = min(1, volume_ratio / 2)
        
        # ציון מומנטום
        momentum_score = min(1, max(0, momentum / 0.1))
        
        # ממוצע משוקלל
        strength = (breakout_percentage * 0.4 + volume_score * 0.3 + momentum_score * 0.3)
        return min(1, strength)

    def analyze(self, symbol, price_df):
        """ניתוח מקיף של פריצות ומועמדים לפריצה"""
        try:
            if price_df is None or len(price_df) < self.lookback_days:
                return {
                    'symbol': symbol,
                    'score': 0,
                    'status': 'insufficient_data',
                    'message': 'נתונים לא מספיקים לניתוח'
                }
            
            # ניתוח volume tension
            volume_analysis = self.volume_meter.analyze(symbol, price_df)
            
            # זיהוי מועמדים לפריצה
            breakout_candidates = self.detect_breakout_candidates(price_df)
            
            # זיהוי פריצות פעילות
            active_breakouts = self.detect_active_breakouts(price_df)
            
            # ניתוח breakout retest
            retest_analysis = self.breakout_recognizer.analyze(symbol, price_df)
            
            # חישוב ציון כללי
            total_score = 0
            score_components = {}
            
            # ציון מועמדים לפריצה
            if breakout_candidates:
                best_candidate = max(breakout_candidates, key=lambda x: x['breakout_probability'])
                score_components['breakout_candidates'] = best_candidate['breakout_probability'] * 40
                total_score += score_components['breakout_candidates']
            
            # ציון פריצות פעילות
            if active_breakouts:
                best_breakout = max(active_breakouts, key=lambda x: x['breakout_strength'])
                score_components['active_breakouts'] = best_breakout['breakout_strength'] * 50
                total_score += score_components['active_breakouts']
            
            # ציון volume tension
            if 'score' in volume_analysis:
                score_components['volume_tension'] = volume_analysis['score'] * 0.1
                total_score += score_components['volume_tension']
            
            # ציון retest
            if 'score' in retest_analysis:
                score_components['retest'] = retest_analysis['score'] * 0.1
                total_score += score_components['retest']
            
            # קביעת סטטוס
            if active_breakouts:
                status = 'active_breakout'
                message = f"פריצה פעילה עם חוזק {best_breakout['breakout_strength']:.2f}"
            elif breakout_candidates:
                status = 'breakout_candidate'
                message = f"מועמד לפריצה עם הסתברות {best_candidate['breakout_probability']:.2f}"
            else:
                status = 'no_breakout'
                message = "אין פריצות או מועמדים לפריצה"
            
            return {
                'symbol': symbol,
                'score': min(100, total_score),
                'status': status,
                'message': message,
                'breakout_candidates': breakout_candidates,
                'active_breakouts': active_breakouts,
                'volume_analysis': volume_analysis,
                'retest_analysis': retest_analysis,
                'score_components': score_components
            }
            
        except Exception as e:
            if self.debug:
                print(f"שגיאה בניתוח {symbol}: {e}")
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