import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.base.base_agent import BaseAgent

class CandlestickAgent(BaseAgent):
    def __init__(self, config=None):
        """
        Candlestick Agent – זיהוי תבניות נרות יפניים מתקדם.
        config: dict עם פרמטרים אופציונליים.
        """
        super().__init__(config)
        cfg = config or {}
        self.lookback = cfg.get("lookback", 15)  # כמה ימים לבדוק אחורה
        self.vol_confirm = cfg.get("vol_confirm", 1.3)  # פי כמה מהנפח הממוצע הנדרש לאישור תבנית
        self.ma_period = cfg.get("ma_period", 20)  # ממוצע נע להקשר
        self.rsi_period = cfg.get("rsi_period", 14)  # תקופת RSI
        self.strong_patterns = ["Hammer", "Bullish Engulfing", "Morning Star", "Piercing Line",
                                "Shooting Star", "Bearish Engulfing", "Evening Star", "Dark Cloud Cover",
                                "Three White Soldiers", "Three Black Crows", "Hanging Man", "Inverted Hammer"]
        
        # משקלים לניתוח
        self.pattern_weight = cfg.get("pattern_weight", 0.4)
        self.volume_weight = cfg.get("volume_weight", 0.25)
        self.context_weight = cfg.get("context_weight", 0.2)
        self.confirmation_weight = cfg.get("confirmation_weight", 0.15)

    def analyze(self, symbol, price_df=None):
        """
        מחזיר ציון 1-100 לפי זיהוי עוצמת תבניות הנר, ווליום יחסי, ומיקום טכני.
        """
        try:
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=90)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            df = price_df.copy().reset_index(drop=True)
            if len(df) < self.lookback + self.ma_period:
                return self.fallback()  # לא מספיק נתונים

            # הכנת נתונים לניתוח
            df = self._prepare_data_for_analysis(df)
            
            # ניתוח תבניות נרות
            pattern_analysis = self._analyze_candlestick_patterns(df)
            
            # ניתוח הקשר טכני
            context_analysis = self._analyze_technical_context(df)
            
            # ניתוח אישור תבניות
            confirmation_analysis = self._analyze_pattern_confirmation(df, pattern_analysis)
            
            # ניתוח דיוק היסטורי
            accuracy_analysis = self._analyze_historical_accuracy(symbol, df)
            
            # חישוב ציון סופי משוקלל
            final_score = self._calculate_weighted_score(
                pattern_analysis, context_analysis, confirmation_analysis, accuracy_analysis
            )
            
            explanation = self._build_comprehensive_explanation(
                pattern_analysis, context_analysis, confirmation_analysis, accuracy_analysis, final_score
            )

            return {
                "score": max(1, min(100, int(final_score))),
                "explanation": explanation,
                "details": {
                    "pattern_analysis": pattern_analysis,
                    "context_analysis": context_analysis,
                    "confirmation_analysis": confirmation_analysis,
                    "accuracy_analysis": accuracy_analysis
                }
            }
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()

    def _prepare_data_for_analysis(self, df):
        """הכנת נתונים לניתוח תבניות נרות"""
        # חישוב מאפיינים בסיסיים
        df["body"] = abs(df["close"] - df["open"])
        df["range"] = df["high"] - df["low"]
        df["upper_shadow"] = df["high"] - df[["close", "open"]].max(axis=1)
        df["lower_shadow"] = df[["close", "open"]].min(axis=1) - df["low"]
        df["body_ratio"] = df["body"] / df["range"]
        df["upper_shadow_ratio"] = df["upper_shadow"] / df["range"]
        df["lower_shadow_ratio"] = df["lower_shadow"] / df["range"]
        
        # חישוב ממוצעים נעים
        df["ma_20"] = df["close"].rolling(20).mean()
        df["ma_50"] = df["close"].rolling(50).mean()
        df["ma_200"] = df["close"].rolling(200).mean()
        
        # חישוב נפח ממוצע
        df["vol_mean"] = df["volume"].rolling(self.ma_period).mean()
        df["vol_ratio"] = df["volume"] / df["vol_mean"]
        
        # חישוב RSI
        df["rsi"] = self._calculate_rsi(df["close"], self.rsi_period)
        
        # חישוב תנודתיות
        df["atr"] = self._calculate_atr(df, 14)
        df["volatility"] = df["atr"] / df["close"]
        
        return df

    def _analyze_candlestick_patterns(self, df):
        """ניתוח תבניות נרות מתקדם"""
        patterns_found = []
        pattern_scores = []
        
        for i in range(len(df) - self.lookback, len(df)):
            row = df.iloc[i]
            window_df = df.iloc[max(0, i-5):i+1]  # חלון של 5 נרות
            
            # זיהוי תבניות בודדות
            single_patterns = self._detect_single_patterns(row)
            
            # זיהוי תבניות מרובות נרות
            multi_patterns = self._detect_multi_candle_patterns(window_df)
            
            # זיהוי תבניות מתקדמות
            advanced_patterns = self._detect_advanced_patterns(window_df)
            
            all_patterns = single_patterns + multi_patterns + advanced_patterns
            
            if all_patterns:
                # בחירת התבנית החזקה ביותר
                best_pattern = max(all_patterns, key=lambda x: x["score"])
                patterns_found.append(best_pattern)
                pattern_scores.append(best_pattern["score"])
        
        if not patterns_found:
            return {
                "score": 1,
                "patterns": [],
                "best_pattern": None,
                "pattern_count": 0
            }
        
        # חישוב ציון ממוצע עם משקל לתבניות חזקות
        weighted_score = sum(score * (1 + i * 0.1) for i, score in enumerate(sorted(pattern_scores, reverse=True)))
        avg_score = weighted_score / len(pattern_scores)
        
        return {
            "score": min(100, max(1, int(avg_score))),
            "patterns": patterns_found,
            "best_pattern": max(patterns_found, key=lambda x: x["score"]),
            "pattern_count": len(patterns_found)
        }

    def _detect_single_patterns(self, row):
        """זיהוי תבניות נר בודד"""
        patterns = []
        body = row["body"]
        rng = row["range"]
        upper = row["upper_shadow"]
        lower = row["lower_shadow"]
        open_ = row["open"]
        close = row["close"]
        
        # Hammer
        if (lower > 2 * body and body > 0.1 * rng and upper < 0.3 * rng and 
            close > open_ and lower > 0.6 * rng):
            patterns.append({"name": "Hammer", "score": 60, "type": "bullish"})
        
        # Hanging Man
        if (lower > 2 * body and body > 0.1 * rng and upper < 0.3 * rng and 
            close < open_ and lower > 0.6 * rng):
            patterns.append({"name": "Hanging Man", "score": 58, "type": "bearish"})
        
        # Shooting Star
        if (upper > 2 * body and body > 0.1 * rng and lower < 0.3 * rng and 
            close < open_ and upper > 0.6 * rng):
            patterns.append({"name": "Shooting Star", "score": 55, "type": "bearish"})
        
        # Inverted Hammer
        if (upper > 2 * body and body > 0.1 * rng and lower < 0.3 * rng and 
            close > open_ and upper > 0.6 * rng):
            patterns.append({"name": "Inverted Hammer", "score": 52, "type": "bullish"})
        
        # Doji
        if body < 0.1 * rng and upper > 0.3 * rng and lower > 0.3 * rng:
            patterns.append({"name": "Doji", "score": 40, "type": "neutral"})
        
        # Marubozu
        if body > 0.9 * rng and upper < 0.05 * rng and lower < 0.05 * rng:
            strength = 45 if close > open_ else 42
            pattern_type = "bullish" if close > open_ else "bearish"
            patterns.append({"name": "Marubozu", "score": strength, "type": pattern_type})
        
        return patterns

    def _detect_multi_candle_patterns(self, window_df):
        """זיהוי תבניות מרובות נרות"""
        patterns = []
        
        if len(window_df) < 2:
            return patterns
        
        # Bullish/Bearish Engulfing
        if len(window_df) >= 2:
            prev = window_df.iloc[-2]
            curr = window_df.iloc[-1]
            
            if (prev["close"] < prev["open"] and curr["close"] > curr["open"] and
                curr["close"] > prev["open"] and curr["open"] < prev["close"]):
                patterns.append({"name": "Bullish Engulfing", "score": 65, "type": "bullish"})
            
            if (prev["close"] > prev["open"] and curr["close"] < curr["open"] and
                curr["close"] < prev["open"] and curr["open"] > prev["close"]):
                patterns.append({"name": "Bearish Engulfing", "score": 63, "type": "bearish"})
        
        # Morning/Evening Star
        if len(window_df) >= 3:
            first = window_df.iloc[-3]
            second = window_df.iloc[-2]
            third = window_df.iloc[-1]
            
            if (first["close"] < first["open"] and
                second["body"] < 0.3 * second["range"] and
                third["close"] > third["open"] and 
                third["close"] > (first["close"] + first["open"]) / 2):
                patterns.append({"name": "Morning Star", "score": 70, "type": "bullish"})
            
            if (first["close"] > first["open"] and
                second["body"] < 0.3 * second["range"] and
                third["close"] < third["open"] and 
                third["close"] < (first["close"] + first["open"]) / 2):
                patterns.append({"name": "Evening Star", "score": 68, "type": "bearish"})
        
        return patterns

    def _detect_advanced_patterns(self, window_df):
        """זיהוי תבניות מתקדמות"""
        patterns = []
        
        if len(window_df) < 3:
            return patterns
        
        # Three White Soldiers
        if len(window_df) >= 3:
            last_3 = window_df.iloc[-3:]
            if all(row["close"] > row["open"] for _, row in last_3.iterrows()):
                if all(row["close"] > row.iloc[-1]["close"] for _, row in last_3.iloc[:-1].iterrows()):
                    patterns.append({"name": "Three White Soldiers", "score": 75, "type": "bullish"})
        
        # Three Black Crows
        if len(window_df) >= 3:
            last_3 = window_df.iloc[-3:]
            if all(row["close"] < row["open"] for _, row in last_3.iterrows()):
                if all(row["close"] < row.iloc[-1]["close"] for _, row in last_3.iloc[:-1].iterrows()):
                    patterns.append({"name": "Three Black Crows", "score": 73, "type": "bearish"})
        
        return patterns

    def _analyze_technical_context(self, df):
        """ניתוח הקשר טכני"""
        if df.empty:
            return {"score": 50, "context": "לא ידוע"}
        
        latest = df.iloc[-1]
        
        # ניתוח מיקום יחסי לממוצעים נעים
        ma_score = 50
        if latest["close"] > latest["ma_20"] > latest["ma_50"] > latest["ma_200"]:
            ma_score = 80  # מגמה עולה חזקה
        elif latest["close"] > latest["ma_20"] > latest["ma_50"]:
            ma_score = 65  # מגמה עולה בינונית
        elif latest["close"] < latest["ma_20"] < latest["ma_50"] < latest["ma_200"]:
            ma_score = 20  # מגמה יורדת חזקה
        elif latest["close"] < latest["ma_20"] < latest["ma_50"]:
            ma_score = 35  # מגמה יורדת בינונית
        elif abs(latest["close"] - latest["ma_20"]) / latest["ma_20"] < 0.02:
            ma_score = 60  # קרוב לממוצע - תמיכה/התנגדות
        
        # ניתוח RSI
        rsi_score = 50
        if latest["rsi"] < 30:
            rsi_score = 70  # oversold - פוטנציאל לקנייה
        elif latest["rsi"] > 70:
            rsi_score = 30  # overbought - פוטנציאל למכירה
        elif 40 <= latest["rsi"] <= 60:
            rsi_score = 60  # ניטרלי
        
        # ניתוח תנודתיות
        volatility_score = 50
        avg_volatility = df["volatility"].mean()
        if latest["volatility"] > avg_volatility * 1.5:
            volatility_score = 70  # תנודתיות גבוהה - הזדמנות
        elif latest["volatility"] < avg_volatility * 0.5:
            volatility_score = 30  # תנודתיות נמוכה
        
        # ציון ממוצע
        context_score = (ma_score + rsi_score + volatility_score) / 3
        
        return {
            "score": int(context_score),
            "ma_score": ma_score,
            "rsi_score": rsi_score,
            "volatility_score": volatility_score,
            "rsi": latest["rsi"],
            "volatility": latest["volatility"]
        }

    def _analyze_pattern_confirmation(self, df, pattern_analysis):
        """ניתוח אישור תבניות"""
        if not pattern_analysis["patterns"]:
            return {"score": 50, "confirmation": "אין תבניות לאישור"}
        
        latest = df.iloc[-1]
        best_pattern = pattern_analysis["best_pattern"]
        
        confirmation_score = 50
        
        # אישור נפח
        if latest["vol_ratio"] > self.vol_confirm:
            confirmation_score += 20
        
        # אישור מגמה
        if best_pattern["type"] == "bullish" and latest["close"] > latest["ma_20"]:
            confirmation_score += 15
        elif best_pattern["type"] == "bearish" and latest["close"] < latest["ma_20"]:
            confirmation_score += 15
        
        # אישור RSI
        if best_pattern["type"] == "bullish" and latest["rsi"] < 40:
            confirmation_score += 10
        elif best_pattern["type"] == "bearish" and latest["rsi"] > 60:
            confirmation_score += 10
        
        return {
            "score": min(100, confirmation_score),
            "volume_confirmed": latest["vol_ratio"] > self.vol_confirm,
            "trend_confirmed": (best_pattern["type"] == "bullish" and latest["close"] > latest["ma_20"]) or
                              (best_pattern["type"] == "bearish" and latest["close"] < latest["ma_20"]),
            "rsi_confirmed": (best_pattern["type"] == "bullish" and latest["rsi"] < 40) or
                            (best_pattern["type"] == "bearish" and latest["rsi"] > 60)
        }

    def _analyze_historical_accuracy(self, symbol, df):
        """ניתוח דיוק היסטורי של תבניות"""
        # זה דורש נתונים היסטוריים נוספים - כרגע נחזיר ערך ברירת מחדל
        return {
            "score": 60,
            "accuracy": "בינונית",
            "note": "דיוק היסטורי דורש נתונים נוספים"
        }

    def _calculate_weighted_score(self, pattern, context, confirmation, accuracy):
        """חישוב ציון סופי משוקלל"""
        pattern_score = pattern.get("score", 50)
        context_score = context.get("score", 50)
        confirmation_score = confirmation.get("score", 50)
        accuracy_score = accuracy.get("score", 50)
        
        weighted_score = (
            pattern_score * self.pattern_weight +
            context_score * self.context_weight +
            confirmation_score * self.confirmation_weight +
            accuracy_score * 0.1  # משקל נמוך לדיוק היסטורי
        )
        
        return max(1, min(100, weighted_score))

    def _build_comprehensive_explanation(self, pattern, context, confirmation, accuracy, final_score):
        """בניית הסבר מקיף"""
        explanation = f"🕯️ CandlestickAgent – ניתוח תבניות נרות:\n"
        
        # ניתוח תבניות
        if pattern["patterns"]:
            best_pattern = pattern["best_pattern"]
            explanation += f"📊 תבנית חזקה: {best_pattern['name']} ({best_pattern['type']}) - {pattern['score']} נקודות\n"
            explanation += f"🔍 סה\"כ תבניות: {pattern['pattern_count']}\n"
        else:
            explanation += f"❌ לא זוהו תבניות משמעותיות\n"
        
        # ניתוח הקשר טכני
        context_info = context.get("context", "לא ידוע")
        explanation += f"📈 הקשר טכני: RSI {context.get('rsi', 0):.1f}, תנודתיות {context.get('volatility', 0):.3f} - {context['score']} נקודות\n"
        
        # ניתוח אישור
        if confirmation.get("volume_confirmed"):
            explanation += f"✅ אישור נפח: נפח גבוה מהממוצע\n"
        if confirmation.get("trend_confirmed"):
            explanation += f"✅ אישור מגמה: תמיכה במגמה הכללית\n"
        if confirmation.get("rsi_confirmed"):
            explanation += f"✅ אישור RSI: תמיכה ברמת RSI\n"
        
        # ציון סופי
        if final_score >= 80:
            level = "🚀 תבנית חזקה מאוד"
        elif final_score >= 65:
            level = "✅ תבנית חזקה"
        elif final_score >= 45:
            level = "⚠️ תבנית בינונית"
        else:
            level = "❌ תבנית חלשה"
        
        explanation += f"🎯 ציון סופי: {final_score} - {level}"
        
        return explanation

    def _calculate_rsi(self, prices, period=14):
        """חישוב RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_atr(self, df, period=14):
        """חישוב Average True Range"""
        high = df["high"]
        low = df["low"]
        close = df["close"]
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
