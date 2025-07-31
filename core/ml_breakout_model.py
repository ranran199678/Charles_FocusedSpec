"""
ML Breakout Model - מודל חיזוי פריצה מבוסס ML
==============================================

סוכן המנבא פריצות מניות באמצעות למידת מכונה.
משתמש באלגוריתמים מתקדמים לחיזוי פריצות.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.feature_selection import SelectKBest, f_classif
import joblib
import pickle

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("ml_breakout_model")

class MLBreakoutModel:
    """
    סוכן חיזוי פריצה מבוסס למידת מכונה
    """

    def __init__(self, config=None):
        """
        אתחול הסוכן
        """
        self.name = "ML Breakout Model"
        self.version = "1.0.0"
        self.description = "מנבא פריצות מניות באמצעות למידת מכונה"

        # הגדרות ML
        self.config = config or {}
        self.model_type = self.config.get("model_type", "ensemble")
        self.lookback_period = self.config.get("lookback_period", 60)
        self.prediction_horizon = self.config.get("prediction_horizon", 5)
        self.breakout_threshold = self.config.get("breakout_threshold", 0.05)
        self.min_samples = self.config.get("min_samples", 100)

        # מודלים
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.is_trained = False

        # פרמטרים לניתוח
        self.feature_columns = []
        self.target_column = 'breakout'
        self.confidence_threshold = 0.7

        logger.info(f"Initialized {self.name} v{self.version}")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None,
                volume_df: pd.DataFrame = None,
                technical_data: pd.DataFrame = None,
                market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח חיזוי פריצה למניה

        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            volume_df: נתוני נפח
            technical_data: נתונים טכניים
            market_data: נתוני שוק

        Returns:
            תוצאות הניתוח
        """
        try:
            logger.info(f"Starting ML breakout analysis for {symbol}")

            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")

            if price_df is None or price_df.empty:
                return self._create_error_result("No price data available")

            # הכנת נתונים
            df = self._prepare_data(price_df, volume_df, technical_data, market_data)

            # יצירת תכונות
            features_df = self._create_features(df)

            # אימון מודל אם נדרש
            if not self.is_trained:
                self._train_models(features_df)

            # חיזוי פריצה
            prediction_analysis = self._predict_breakout(features_df)

            # ניתוח תכונות חשובות
            feature_importance_analysis = self._analyze_feature_importance(features_df)

            # ניתוח ביטחון
            confidence_analysis = self._analyze_prediction_confidence(prediction_analysis)

            # ניתוח תנאי שוק
            market_condition_analysis = self._analyze_market_conditions(features_df)

            # חישוב ציון כללי
            score = self._calculate_ml_score(
                prediction_analysis,
                feature_importance_analysis,
                confidence_analysis,
                market_condition_analysis
            )

            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)

            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)

            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                prediction_analysis,
                feature_importance_analysis,
                confidence_analysis,
                market_condition_analysis
            )

            result = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "version": self.version,
                "score": score,
                "confidence": confidence,
                "recommendation": recommendation,
                "key_signals": key_signals,
                "analysis": {
                    "prediction": prediction_analysis,
                    "feature_importance": feature_importance_analysis,
                    "confidence": confidence_analysis,
                    "market_conditions": market_condition_analysis
                },
                "metadata": {
                    "model_type": self.model_type,
                    "lookback_period": self.lookback_period,
                    "prediction_horizon": self.prediction_horizon,
                    "breakout_threshold": self.breakout_threshold,
                    "is_trained": self.is_trained
                }
            }

            logger.info(f"ML breakout analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result

        except Exception as e:
            error_msg = f"Error analyzing ML breakout for {symbol}: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result(error_msg)

    def _prepare_data(self, price_df: pd.DataFrame, volume_df: pd.DataFrame,
                     technical_data: pd.DataFrame, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        הכנת נתונים לניתוח
        """
        df = price_df.copy()
        
        # הוספת נתוני נפח
        if volume_df is not None and not volume_df.empty:
            df['volume'] = volume_df['volume']
        elif 'volume' not in df.columns:
            df['volume'] = 1000  # ערך ברירת מחדל

        # הוספת נתונים טכניים
        if technical_data is not None and not technical_data.empty:
            for col in technical_data.columns:
                if col not in df.columns:
                    df[col] = technical_data[col]

        # הוספת נתוני שוק
        if market_data is not None and not market_data.empty:
            for col in market_data.columns:
                if col not in df.columns:
                    df[col] = market_data[col]

        # חישוב תכונות בסיסיות
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        df['volatility'] = df['returns'].rolling(window=20).std()
        
        # חישוב ממוצעים נעים
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # חישוב RSI
        df['rsi'] = self._calculate_rsi(df['close'])
        
        # חישוב MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # חישוב Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # חישוב תכונות נפח
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        df['volume_sma'] = df['volume'].rolling(window=20).std()
        
        # חישוב תכונות מחיר
        df['price_range'] = (df['high'] - df['low']) / df['close']
        df['body_size'] = np.abs(df['close'] - df['open']) / df['close']
        
        return df

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        יצירת תכונות למודל
        """
        features_df = df.copy()
        
        # תכונות טכניות
        features_df['sma_ratio'] = features_df['sma_20'] / features_df['sma_50']
        features_df['ema_ratio'] = features_df['ema_12'] / features_df['ema_26']
        features_df['price_vs_sma20'] = features_df['close'] / features_df['sma_20']
        features_df['price_vs_sma50'] = features_df['close'] / features_df['sma_50']
        
        # תכונות נפח
        features_df['volume_trend'] = features_df['volume'].rolling(window=5).mean().pct_change()
        features_df['volume_volatility'] = features_df['volume'].rolling(window=20).std() / features_df['volume_ma']
        
        # תכונות תנודתיות
        features_df['volatility_ratio'] = features_df['volatility'] / features_df['volatility'].rolling(window=60).mean()
        features_df['volatility_trend'] = features_df['volatility'].rolling(window=5).mean().pct_change()
        
        # תכונות RSI
        features_df['rsi_trend'] = features_df['rsi'].rolling(window=5).mean().pct_change()
        features_df['rsi_position'] = (features_df['rsi'] - 30) / (70 - 30)  # נרמול ל-0-1
        
        # תכונות MACD
        features_df['macd_trend'] = features_df['macd'].rolling(window=5).mean().pct_change()
        features_df['macd_signal_trend'] = features_df['macd_signal'].rolling(window=5).mean().pct_change()
        
        # תכונות Bollinger Bands
        features_df['bb_squeeze'] = features_df['bb_width'] < features_df['bb_width'].rolling(window=60).quantile(0.2)
        features_df['bb_position_trend'] = features_df['bb_position'].rolling(window=5).mean().pct_change()
        
        # תכונות מחיר
        features_df['price_momentum'] = features_df['close'].pct_change(periods=5)
        features_df['price_acceleration'] = features_df['price_momentum'].pct_change()
        features_df['price_range_trend'] = features_df['price_range'].rolling(window=5).mean().pct_change()
        
        # יצירת תכונות אינטראקציה
        features_df['volume_price_correlation'] = features_df['volume_ratio'] * features_df['price_momentum']
        features_df['volatility_price_correlation'] = features_df['volatility_ratio'] * features_df['price_momentum']
        
        # הסרת NaN
        features_df = features_df.dropna()
        
        # יצירת מטרה (target)
        features_df[self.target_column] = self._create_target(features_df)
        
        return features_df

    def _create_target(self, df: pd.DataFrame) -> pd.Series:
        """
        יצירת משתנה מטרה
        """
        # חישוב שינויי מחיר עתידיים
        future_returns = df['close'].shift(-self.prediction_horizon) / df['close'] - 1
        
        # הגדרת פריצה
        breakout = (future_returns > self.breakout_threshold).astype(int)
        
        return breakout

    def _train_models(self, features_df: pd.DataFrame):
        """
        אימון מודלים
        """
        try:
            if len(features_df) < self.min_samples:
                logger.warning(f"Insufficient data for training: {len(features_df)} samples")
                return

            # בחירת תכונות
            feature_columns = [col for col in features_df.columns 
                             if col not in [self.target_column, 'open', 'high', 'low', 'close', 'volume']]
            
            X = features_df[feature_columns]
            y = features_df[self.target_column]
            
            # הסרת NaN
            mask = ~(X.isna().any(axis=1) | y.isna())
            X = X[mask]
            y = y[mask]
            
            if len(X) < self.min_samples:
                logger.warning(f"Insufficient clean data for training: {len(X)} samples")
                return

            # חלוקה לאימון ובדיקה
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # נרמול נתונים
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # בחירת תכונות
            feature_selector = SelectKBest(score_func=f_classif, k=min(20, len(feature_columns)))
            X_train_selected = feature_selector.fit_transform(X_train_scaled, y_train)
            X_test_selected = feature_selector.transform(X_test_scaled)

            # שמירת תכונות נבחרות
            selected_features = [feature_columns[i] for i in feature_selector.get_support(indices=True)]
            self.feature_columns = selected_features

            # אימון מודלים
            models = {
                'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
                'svm': SVC(probability=True, random_state=42)
            }

            for name, model in models.items():
                try:
                    model.fit(X_train_selected, y_train)
                    y_pred = model.predict(X_test_selected)
                    
                    # חישוב מדדי ביצוע
                    accuracy = accuracy_score(y_test, y_pred)
                    precision = precision_score(y_test, y_pred, zero_division=0)
                    recall = recall_score(y_test, y_pred, zero_division=0)
                    f1 = f1_score(y_test, y_pred, zero_division=0)
                    
                    logger.info(f"{name} - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
                    
                    self.models[name] = model
                    
                except Exception as e:
                    logger.error(f"Error training {name}: {str(e)}")

            # שמירת scaler ו-feature selector
            self.scalers['standard'] = scaler
            self.feature_selectors['kbest'] = feature_selector
            
            self.is_trained = True
            logger.info("Models trained successfully")

        except Exception as e:
            logger.error(f"Error in model training: {str(e)}")

    def _predict_breakout(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        חיזוי פריצה
        """
        try:
            if not self.is_trained or not self.feature_columns:
                return {"prediction": 0.5, "confidence": 0.0, "model_predictions": {}}

            # הכנת נתונים לחיזוי
            latest_data = features_df[self.feature_columns].iloc[-1:]
            
            # נרמול
            scaler = self.scalers.get('standard')
            feature_selector = self.feature_selectors.get('kbest')
            
            if scaler is None or feature_selector is None:
                return {"prediction": 0.5, "confidence": 0.0, "model_predictions": {}}

            latest_scaled = scaler.transform(latest_data)
            latest_selected = feature_selector.transform(latest_scaled)

            # חיזוי מכל המודלים
            model_predictions = {}
            probabilities = []
            
            for name, model in self.models.items():
                try:
                    if hasattr(model, 'predict_proba'):
                        prob = model.predict_proba(latest_selected)[0][1]  # הסתברות לפריצה
                        pred = model.predict(latest_selected)[0]
                    else:
                        pred = model.predict(latest_selected)[0]
                        prob = pred  # פישוט
                    
                    model_predictions[name] = {
                        'prediction': int(pred),
                        'probability': float(prob)
                    }
                    probabilities.append(prob)
                    
                except Exception as e:
                    logger.error(f"Error predicting with {name}: {str(e)}")

            # חישוב חיזוי ממוצע
            if probabilities:
                avg_probability = np.mean(probabilities)
                avg_prediction = 1 if avg_probability > 0.5 else 0
                
                # חישוב ביטחון
                confidence = 1 - np.std(probabilities) if len(probabilities) > 1 else 0.5
            else:
                avg_probability = 0.5
                avg_prediction = 0
                confidence = 0.0

            return {
                "prediction": avg_prediction,
                "probability": avg_probability,
                "confidence": confidence,
                "model_predictions": model_predictions,
                "breakout_likelihood": avg_probability,
                "prediction_horizon": self.prediction_horizon
            }

        except Exception as e:
            logger.error(f"Error in breakout prediction: {str(e)}")
            return {"prediction": 0.5, "confidence": 0.0, "model_predictions": {}}

    def _analyze_feature_importance(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח חשיבות תכונות
        """
        try:
            if not self.is_trained or 'random_forest' not in self.models:
                return {"top_features": [], "importance_scores": {}}

            # קבלת חשיבות תכונות מ-Random Forest
            rf_model = self.models['random_forest']
            feature_selector = self.feature_selectors.get('kbest')
            
            if feature_selector is None:
                return {"top_features": [], "importance_scores": {}}

            # מיפוי אינדקסים לתכונות
            all_features = [col for col in features_df.columns 
                          if col not in [self.target_column, 'open', 'high', 'low', 'close', 'volume']]
            selected_indices = feature_selector.get_support(indices=True)
            selected_features = [all_features[i] for i in selected_indices]
            
            # קבלת חשיבות תכונות
            importances = rf_model.feature_importances_
            
            # יצירת מילון חשיבות
            importance_dict = dict(zip(selected_features, importances))
            
            # מיון לפי חשיבות
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            top_features = [feature for feature, importance in sorted_features[:10]]

            return {
                "top_features": top_features,
                "importance_scores": importance_dict,
                "total_features": len(selected_features),
                "max_importance": max(importances) if len(importances) > 0 else 0,
                "avg_importance": np.mean(importances) if len(importances) > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error analyzing feature importance: {str(e)}")
            return {"top_features": [], "importance_scores": {}}

    def _analyze_prediction_confidence(self, prediction_analysis: Dict) -> Dict[str, Any]:
        """
        ניתוח ביטחון החיזוי
        """
        try:
            confidence = prediction_analysis.get('confidence', 0.0)
            model_predictions = prediction_analysis.get('model_predictions', {})
            
            # חישוב הסכמה בין מודלים
            predictions = [pred['prediction'] for pred in model_predictions.values()]
            agreement_ratio = sum(predictions) / len(predictions) if predictions else 0.5
            
            # חישוב פיזור הסתברויות
            probabilities = [pred['probability'] for pred in model_predictions.values()]
            probability_std = np.std(probabilities) if len(probabilities) > 1 else 0
            
            # קביעת רמת ביטחון
            if confidence > 0.8 and agreement_ratio in [0, 1]:
                confidence_level = "Very High"
            elif confidence > 0.6 and probability_std < 0.2:
                confidence_level = "High"
            elif confidence > 0.4:
                confidence_level = "Medium"
            else:
                confidence_level = "Low"

            return {
                "confidence_score": confidence,
                "agreement_ratio": agreement_ratio,
                "probability_std": probability_std,
                "confidence_level": confidence_level,
                "model_count": len(model_predictions),
                "consensus": agreement_ratio == 1.0 or agreement_ratio == 0.0
            }

        except Exception as e:
            logger.error(f"Error analyzing prediction confidence: {str(e)}")
            return {"confidence_score": 0.0, "confidence_level": "Low"}

    def _analyze_market_conditions(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        ניתוח תנאי שוק
        """
        try:
            latest = features_df.iloc[-1]
            
            # ניתוח תנאי שוק
            market_conditions = {}
            
            # תנאי נפח
            if latest['volume_ratio'] > 2.0:
                market_conditions['volume'] = "High"
            elif latest['volume_ratio'] > 1.5:
                market_conditions['volume'] = "Above Average"
            elif latest['volume_ratio'] < 0.5:
                market_conditions['volume'] = "Low"
            else:
                market_conditions['volume'] = "Normal"
            
            # תנאי תנודתיות
            if latest['volatility_ratio'] > 1.5:
                market_conditions['volatility'] = "High"
            elif latest['volatility_ratio'] < 0.5:
                market_conditions['volatility'] = "Low"
            else:
                market_conditions['volatility'] = "Normal"
            
            # תנאי RSI
            if latest['rsi'] > 70:
                market_conditions['rsi'] = "Overbought"
            elif latest['rsi'] < 30:
                market_conditions['rsi'] = "Oversold"
            else:
                market_conditions['rsi'] = "Neutral"
            
            # תנאי Bollinger Bands
            if latest['bb_squeeze']:
                market_conditions['bollinger'] = "Squeeze"
            elif latest['bb_position'] > 0.8:
                market_conditions['bollinger'] = "Upper Band"
            elif latest['bb_position'] < 0.2:
                market_conditions['bollinger'] = "Lower Band"
            else:
                market_conditions['bollinger'] = "Normal"
            
            # תנאי מגמה
            if latest['sma_ratio'] > 1.02:
                market_conditions['trend'] = "Bullish"
            elif latest['sma_ratio'] < 0.98:
                market_conditions['trend'] = "Bearish"
            else:
                market_conditions['trend'] = "Sideways"

            return {
                "market_conditions": market_conditions,
                "favorable_conditions": sum(1 for condition in market_conditions.values() 
                                         if condition in ["High", "Bullish", "Squeeze"]) / len(market_conditions),
                "unfavorable_conditions": sum(1 for condition in market_conditions.values() 
                                            if condition in ["Low", "Bearish", "Overbought"]) / len(market_conditions)
            }

        except Exception as e:
            logger.error(f"Error analyzing market conditions: {str(e)}")
            return {"market_conditions": {}, "favorable_conditions": 0.5}

    def _calculate_ml_score(self, prediction_analysis: Dict, feature_importance_analysis: Dict,
                          confidence_analysis: Dict, market_condition_analysis: Dict) -> float:
        """
        חישוב ציון ML כללי
        """
        try:
            # משקלות
            weights = {
                'prediction': 0.4,
                'confidence': 0.3,
                'market_conditions': 0.2,
                'feature_importance': 0.1
            }

            # ציון חיזוי
            probability = prediction_analysis.get('probability', 0.5)
            prediction_score = probability * 100
            
            # ציון ביטחון
            confidence_score = confidence_analysis.get('confidence_score', 0.0) * 100
            
            # ציון תנאי שוק
            favorable_ratio = market_condition_analysis.get('favorable_conditions', 0.5)
            market_score = favorable_ratio * 100
            
            # ציון חשיבות תכונות
            max_importance = feature_importance_analysis.get('max_importance', 0.0)
            feature_score = min(max_importance * 100, 100)

            # חישוב ציון משוקלל
            total_score = (
                prediction_score * weights['prediction'] +
                confidence_score * weights['confidence'] +
                market_score * weights['market_conditions'] +
                feature_score * weights['feature_importance']
            )

            return min(max(total_score, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating ML score: {str(e)}")
            return 50.0

    def _determine_confidence_level(self, score: float) -> str:
        """
        קביעת רמת ביטחון
        """
        if score >= 80:
            return "High"
        elif score >= 60:
            return "Medium"
        elif score >= 40:
            return "Low"
        else:
            return "Very Low"

    def _generate_recommendation(self, score: float, confidence: str) -> str:
        """
        יצירת המלצה
        """
        if score >= 80:
            return "Strong Buy - High ML prediction with favorable conditions"
        elif score >= 60:
            return "Buy - Good ML prediction with positive indicators"
        elif score >= 40:
            return "Hold - Moderate ML prediction, monitor for changes"
        else:
            return "Sell - Low ML prediction with unfavorable conditions"

    def _extract_key_signals(self, prediction_analysis: Dict, feature_importance_analysis: Dict,
                           confidence_analysis: Dict, market_condition_analysis: Dict) -> List[str]:
        """
        חילוץ אותות מפתח
        """
        signals = []

        # אותות חיזוי
        probability = prediction_analysis.get('probability', 0.5)
        if probability > 0.7:
            signals.append(f"High breakout probability: {probability:.2f}")
        elif probability < 0.3:
            signals.append(f"Low breakout probability: {probability:.2f}")

        # אותות ביטחון
        confidence_level = confidence_analysis.get('confidence_level', 'Low')
        if confidence_level in ['High', 'Very High']:
            signals.append(f"High prediction confidence: {confidence_level}")

        # אותות תנאי שוק
        market_conditions = market_condition_analysis.get('market_conditions', {})
        if market_conditions.get('volume') == 'High':
            signals.append("High volume conditions")
        if market_conditions.get('bollinger') == 'Squeeze':
            signals.append("Bollinger Band squeeze detected")

        # אותות חשיבות תכונות
        top_features = feature_importance_analysis.get('top_features', [])
        if top_features:
            signals.append(f"Key features: {', '.join(top_features[:3])}")

        return signals

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        חישוב RSI
        """
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return pd.Series([50] * len(prices), index=prices.index)

    def save_model(self, filepath: str):
        """
        שמירת מודל
        """
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'feature_selectors': self.feature_selectors,
                'feature_columns': self.feature_columns,
                'is_trained': self.is_trained,
                'config': self.config
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")

    def load_model(self, filepath: str):
        """
        טעינת מודל
        """
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.feature_selectors = model_data['feature_selectors']
            self.feature_columns = model_data['feature_columns']
            self.is_trained = model_data['is_trained']
            self.config.update(model_data['config'])
            
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        יצירת תוצאת שגיאה
        """
        return {
            "symbol": "UNKNOWN",
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "version": self.version,
            "score": 0,
            "confidence": "Very Low",
            "recommendation": f"Error: {error_message}",
            "key_signals": [],
            "analysis": {},
            "error": error_message
        } 