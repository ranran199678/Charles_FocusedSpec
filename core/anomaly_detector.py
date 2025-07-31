"""
Anomaly Detector - זיהוי אנומליות
==================================

סוכן המזהה אנומליות וחריגות בנתוני מניות.
מזהה דפוסים חריגים במחיר, נפח ונתונים סטטיסטיים.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("anomaly_detector")

class AnomalyDetector:
    """
    סוכן זיהוי אנומליות
    """

    def __init__(self, config=None):
        """
        אתחול הסוכן
        """
        self.name = "Anomaly Detector"
        self.version = "1.0.0"
        self.description = "מזהה אנומליות וחריגות בנתוני מניות"

        # הגדרות זיהוי
        self.config = config or {}
        self.z_score_threshold = self.config.get("z_score_threshold", 3.0)
        self.iqr_multiplier = self.config.get("iqr_multiplier", 1.5)
        self.isolation_forest_contamination = self.config.get("contamination", 0.1)
        self.min_data_points = self.config.get("min_data_points", 30)

        # פרמטרים לניתוח
        self.price_window = 20  # חלון לניתוח מחיר
        self.volume_window = 20  # חלון לניתוח נפח
        self.volatility_window = 10  # חלון לניתוח תנודתיות

        logger.info(f"Initialized {self.name} v{self.version}")

    def analyze(self, symbol: str, price_df: pd.DataFrame = None,
                volume_df: pd.DataFrame = None,
                technical_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח אנומליות למניה

        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            volume_df: נתוני נפח
            technical_data: נתונים טכניים

        Returns:
            תוצאות הניתוח
        """
        try:
            logger.info(f"Starting anomaly analysis for {symbol}")

            # אימות נתונים
            if not validate_symbol(symbol):
                return self._create_error_result("Invalid symbol format")

            if price_df is None or price_df.empty:
                return self._create_error_result("No price data available")

            # ניתוח אנומליות מחיר
            price_anomalies = self._detect_price_anomalies(price_df)

            # ניתוח אנומליות נפח
            volume_anomalies = self._detect_volume_anomalies(price_df)

            # ניתוח אנומליות תנודתיות
            volatility_anomalies = self._detect_volatility_anomalies(price_df)

            # ניתוח אנומליות סטטיסטיות
            statistical_anomalies = self._detect_statistical_anomalies(price_df)

            # ניתוח אנומליות רב-ממדיות
            multivariate_anomalies = self._detect_multivariate_anomalies(price_df)

            # ניתוח אנומליות זמן
            temporal_anomalies = self._detect_temporal_anomalies(price_df)

            # חישוב ציון כללי
            score = self._calculate_anomaly_score(
                price_anomalies,
                volume_anomalies,
                volatility_anomalies,
                statistical_anomalies,
                multivariate_anomalies,
                temporal_anomalies
            )

            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)

            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)

            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                price_anomalies,
                volume_anomalies,
                volatility_anomalies,
                statistical_anomalies,
                multivariate_anomalies,
                temporal_anomalies
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
                    "price_anomalies": price_anomalies,
                    "volume_anomalies": volume_anomalies,
                    "volatility_anomalies": volatility_anomalies,
                    "statistical_anomalies": statistical_anomalies,
                    "multivariate_anomalies": multivariate_anomalies,
                    "temporal_anomalies": temporal_anomalies
                },
                "metadata": {
                    "z_score_threshold": self.z_score_threshold,
                    "iqr_multiplier": self.iqr_multiplier,
                    "contamination": self.isolation_forest_contamination,
                    "price_window": self.price_window,
                    "volume_window": self.volume_window,
                    "volatility_window": self.volatility_window
                }
            }

            logger.info(f"Anomaly analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result

        except Exception as e:
            error_msg = f"Error analyzing anomalies for {symbol}: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result(error_msg)

    def _detect_price_anomalies(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """
        זיהוי אנומליות מחיר
        """
        try:
            if len(price_df) < self.min_data_points:
                return self._create_empty_anomaly_analysis()

            # חישוב שינויי מחיר
            price_df = price_df.copy()
            price_df['returns'] = price_df['close'].pct_change()
            price_df['log_returns'] = np.log(price_df['close'] / price_df['close'].shift(1))

            # זיהוי אנומליות לפי Z-Score
            z_scores = np.abs(stats.zscore(price_df['returns'].dropna()))
            z_score_anomalies = z_scores > self.z_score_threshold

            # זיהוי אנומליות לפי IQR
            q1 = price_df['returns'].quantile(0.25)
            q3 = price_df['returns'].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - self.iqr_multiplier * iqr
            upper_bound = q3 + self.iqr_multiplier * iqr
            iqr_anomalies = (price_df['returns'] < lower_bound) | (price_df['returns'] > upper_bound)

            # זיהוי קפיצות מחיר קיצוניות
            extreme_moves = np.abs(price_df['returns']) > 0.1  # קפיצות של יותר מ-10%

            # זיהוי תבניות חריגות
            price_patterns = self._detect_price_patterns(price_df)

            # חישוב מדדים
            anomaly_count = sum(z_score_anomalies) + sum(iqr_anomalies) + sum(extreme_moves)
            anomaly_ratio = anomaly_count / len(price_df) if len(price_df) > 0 else 0

            return {
                "z_score_anomalies": sum(z_score_anomalies),
                "iqr_anomalies": sum(iqr_anomalies),
                "extreme_moves": sum(extreme_moves),
                "price_patterns": price_patterns,
                "total_anomalies": anomaly_count,
                "anomaly_ratio": anomaly_ratio,
                "max_z_score": np.max(z_scores) if len(z_scores) > 0 else 0,
                "volatility": price_df['returns'].std(),
                "skewness": price_df['returns'].skew(),
                "kurtosis": price_df['returns'].kurtosis(),
                "anomaly_dates": price_df.index[z_score_anomalies | iqr_anomalies | extreme_moves].tolist()
            }

        except Exception as e:
            logger.error(f"Error detecting price anomalies: {str(e)}")
            return self._create_empty_anomaly_analysis()

    def _detect_volume_anomalies(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """
        זיהוי אנומליות נפח
        """
        try:
            if len(price_df) < self.min_data_points or 'volume' not in price_df.columns:
                return self._create_empty_anomaly_analysis()

            # חישוב נפח ממוצע
            volume_ma = price_df['volume'].rolling(window=self.volume_window).mean()
            volume_std = price_df['volume'].rolling(window=self.volume_window).std()

            # זיהוי אנומליות נפח
            volume_ratio = price_df['volume'] / volume_ma
            volume_z_scores = np.abs((price_df['volume'] - volume_ma) / volume_std)
            
            # זיהוי קפיצות נפח
            volume_spikes = volume_ratio > 3.0  # נפח גבוה פי 3 מהממוצע
            volume_drops = volume_ratio < 0.3   # נפח נמוך מ-30% מהממוצע

            # זיהוי אנומליות לפי Z-Score
            volume_z_anomalies = volume_z_scores > self.z_score_threshold

            # זיהוי תבניות נפח חריגות
            volume_patterns = self._detect_volume_patterns(price_df)

            # חישוב מדדים
            anomaly_count = sum(volume_spikes) + sum(volume_drops) + sum(volume_z_anomalies)
            anomaly_ratio = anomaly_count / len(price_df) if len(price_df) > 0 else 0

            return {
                "volume_spikes": sum(volume_spikes),
                "volume_drops": sum(volume_drops),
                "volume_z_anomalies": sum(volume_z_anomalies),
                "volume_patterns": volume_patterns,
                "total_anomalies": anomaly_count,
                "anomaly_ratio": anomaly_ratio,
                "max_volume_ratio": np.max(volume_ratio) if len(volume_ratio) > 0 else 1,
                "min_volume_ratio": np.min(volume_ratio) if len(volume_ratio) > 0 else 1,
                "avg_volume_ratio": np.mean(volume_ratio),
                "volume_volatility": price_df['volume'].std() / price_df['volume'].mean(),
                "anomaly_dates": price_df.index[volume_spikes | volume_drops | volume_z_anomalies].tolist()
            }

        except Exception as e:
            logger.error(f"Error detecting volume anomalies: {str(e)}")
            return self._create_empty_anomaly_analysis()

    def _detect_volatility_anomalies(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """
        זיהוי אנומליות תנודתיות
        """
        try:
            if len(price_df) < self.min_data_points:
                return self._create_empty_anomaly_analysis()

            # חישוב תנודתיות
            price_df = price_df.copy()
            price_df['returns'] = price_df['close'].pct_change()
            price_df['volatility'] = price_df['returns'].rolling(window=self.volatility_window).std()

            # חישוב תנודתיות ממוצעת
            avg_volatility = price_df['volatility'].mean()
            vol_std = price_df['volatility'].std()

            # זיהוי אנומליות תנודתיות
            vol_z_scores = np.abs((price_df['volatility'] - avg_volatility) / vol_std)
            vol_anomalies = vol_z_scores > self.z_score_threshold

            # זיהוי קפיצות תנודתיות
            vol_spikes = price_df['volatility'] > avg_volatility * 2
            vol_drops = price_df['volatility'] < avg_volatility * 0.5

            # זיהוי תבניות תנודתיות
            volatility_patterns = self._detect_volatility_patterns(price_df)

            # חישוב מדדים
            anomaly_count = sum(vol_anomalies) + sum(vol_spikes) + sum(vol_drops)
            anomaly_ratio = anomaly_count / len(price_df) if len(price_df) > 0 else 0

            return {
                "volatility_anomalies": sum(vol_anomalies),
                "volatility_spikes": sum(vol_spikes),
                "volatility_drops": sum(vol_drops),
                "volatility_patterns": volatility_patterns,
                "total_anomalies": anomaly_count,
                "anomaly_ratio": anomaly_ratio,
                "current_volatility": price_df['volatility'].iloc[-1] if len(price_df) > 0 else 0,
                "avg_volatility": avg_volatility,
                "volatility_ratio": price_df['volatility'].iloc[-1] / avg_volatility if avg_volatility > 0 else 1,
                "max_volatility": price_df['volatility'].max(),
                "min_volatility": price_df['volatility'].min(),
                "anomaly_dates": price_df.index[vol_anomalies | vol_spikes | vol_drops].tolist()
            }

        except Exception as e:
            logger.error(f"Error detecting volatility anomalies: {str(e)}")
            return self._create_empty_anomaly_analysis()

    def _detect_statistical_anomalies(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """
        זיהוי אנומליות סטטיסטיות
        """
        try:
            if len(price_df) < self.min_data_points:
                return self._create_empty_anomaly_analysis()

            # חישוב מדדים סטטיסטיים
            returns = price_df['close'].pct_change().dropna()
            
            # בדיקת נורמליות
            normality_test = stats.normaltest(returns)
            is_normal = normality_test.pvalue > 0.05

            # חישוב מדדים
            skewness = returns.skew()
            kurtosis = returns.kurtosis()
            
            # זיהוי אנומליות בהתפלגות
            distribution_anomalies = []
            if abs(skewness) > 2:
                distribution_anomalies.append("high_skewness")
            if abs(kurtosis) > 7:
                distribution_anomalies.append("high_kurtosis")
            if not is_normal:
                distribution_anomalies.append("non_normal")

            # זיהוי outliers לפי שיטות שונות
            outliers_methods = {}
            
            # Z-Score method
            z_scores = np.abs(stats.zscore(returns))
            outliers_methods['z_score'] = sum(z_scores > self.z_score_threshold)
            
            # IQR method
            q1, q3 = np.percentile(returns, [25, 75])
            iqr = q3 - q1
            outliers_methods['iqr'] = sum((returns < q1 - 1.5*iqr) | (returns > q3 + 1.5*iqr))
            
            # Modified Z-Score method
            median = np.median(returns)
            mad = np.median(np.abs(returns - median))
            modified_z_scores = 0.6745 * (returns - median) / mad
            outliers_methods['modified_z_score'] = sum(np.abs(modified_z_scores) > 3.5)

            return {
                "distribution_anomalies": distribution_anomalies,
                "outliers_methods": outliers_methods,
                "total_outliers": sum(outliers_methods.values()),
                "is_normal_distribution": is_normal,
                "normality_p_value": normality_test.pvalue,
                "skewness": skewness,
                "kurtosis": kurtosis,
                "mean": returns.mean(),
                "std": returns.std(),
                "median": returns.median(),
                "mad": np.median(np.abs(returns - returns.median())),
                "anomaly_score": len(distribution_anomalies) + sum(outliers_methods.values())
            }

        except Exception as e:
            logger.error(f"Error detecting statistical anomalies: {str(e)}")
            return self._create_empty_anomaly_analysis()

    def _detect_multivariate_anomalies(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """
        זיהוי אנומליות רב-ממדיות
        """
        try:
            if len(price_df) < self.min_data_points:
                return self._create_empty_anomaly_analysis()

            # הכנת נתונים
            features = []
            
            # תכונות מחיר
            price_df = price_df.copy()
            price_df['returns'] = price_df['close'].pct_change()
            price_df['log_returns'] = np.log(price_df['close'] / price_df['close'].shift(1))
            price_df['price_range'] = (price_df['high'] - price_df['low']) / price_df['close']
            
            if 'volume' in price_df.columns:
                price_df['volume_ratio'] = price_df['volume'] / price_df['volume'].rolling(20).mean()
                features = ['returns', 'log_returns', 'price_range', 'volume_ratio']
            else:
                features = ['returns', 'log_returns', 'price_range']

            # הסרת NaN
            feature_data = price_df[features].dropna()
            
            if len(feature_data) < 10:
                return self._create_empty_anomaly_analysis()

            # נרמול נתונים
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(feature_data)

            # Isolation Forest
            iso_forest = IsolationForest(
                contamination=self.isolation_forest_contamination,
                random_state=42
            )
            iso_predictions = iso_forest.fit_predict(scaled_data)
            iso_anomalies = sum(iso_predictions == -1)

            # Local Outlier Factor (LOF) - אם יש מספיק נתונים
            if len(scaled_data) > 20:
                try:
                    from sklearn.neighbors import LocalOutlierFactor
                    lof = LocalOutlierFactor(contamination=self.isolation_forest_contamination)
                    lof_predictions = lof.fit_predict(scaled_data)
                    lof_anomalies = sum(lof_predictions == -1)
                except:
                    lof_anomalies = 0
            else:
                lof_anomalies = 0

            # חישוב מדדים
            total_anomalies = iso_anomalies + lof_anomalies
            anomaly_ratio = total_anomalies / len(scaled_data) if len(scaled_data) > 0 else 0

            return {
                "isolation_forest_anomalies": iso_anomalies,
                "lof_anomalies": lof_anomalies,
                "total_multivariate_anomalies": total_anomalies,
                "anomaly_ratio": anomaly_ratio,
                "features_used": features,
                "data_points": len(scaled_data),
                "contamination_rate": self.isolation_forest_contamination,
                "anomaly_dates": feature_data.index[iso_predictions == -1].tolist()
            }

        except Exception as e:
            logger.error(f"Error detecting multivariate anomalies: {str(e)}")
            return self._create_empty_anomaly_analysis()

    def _detect_temporal_anomalies(self, price_df: pd.DataFrame) -> Dict[str, Any]:
        """
        זיהוי אנומליות זמן
        """
        try:
            if len(price_df) < self.min_data_points:
                return self._create_empty_anomaly_analysis()

            # חישוב מדדים זמניים
            price_df = price_df.copy()
            price_df['returns'] = price_df['close'].pct_change()
            
            # זיהוי רצפים חריגים
            consecutive_positive = self._find_consecutive_sequences(price_df['returns'] > 0)
            consecutive_negative = self._find_consecutive_sequences(price_df['returns'] < 0)
            
            # זיהוי רצפים חריגים
            max_consecutive_positive = max(consecutive_positive) if consecutive_positive else 0
            max_consecutive_negative = max(consecutive_negative) if consecutive_negative else 0
            
            # זיהוי רצפים חריגים (יותר מ-5 ימים)
            extreme_positive_runs = sum(1 for run in consecutive_positive if run > 5)
            extreme_negative_runs = sum(1 for run in consecutive_negative if run > 5)

            # זיהוי תבניות זמן
            temporal_patterns = self._detect_temporal_patterns(price_df)

            # חישוב מדדים
            total_temporal_anomalies = extreme_positive_runs + extreme_negative_runs
            anomaly_ratio = total_temporal_anomalies / len(price_df) if len(price_df) > 0 else 0

            return {
                "extreme_positive_runs": extreme_positive_runs,
                "extreme_negative_runs": extreme_negative_runs,
                "max_consecutive_positive": max_consecutive_positive,
                "max_consecutive_negative": max_consecutive_negative,
                "temporal_patterns": temporal_patterns,
                "total_temporal_anomalies": total_temporal_anomalies,
                "anomaly_ratio": anomaly_ratio,
                "avg_run_length": np.mean(consecutive_positive + consecutive_negative) if (consecutive_positive + consecutive_negative) else 0,
                "run_volatility": np.std(consecutive_positive + consecutive_negative) if (consecutive_positive + consecutive_negative) else 0
            }

        except Exception as e:
            logger.error(f"Error detecting temporal anomalies: {str(e)}")
            return self._create_empty_anomaly_analysis()

    def _detect_price_patterns(self, price_df: pd.DataFrame) -> List[str]:
        """
        זיהוי תבניות מחיר חריגות
        """
        patterns = []
        
        try:
            # זיהוי תבניות בסיסיות
            returns = price_df['close'].pct_change().dropna()
            
            # תבנית V
            if len(returns) >= 5:
                recent_returns = returns.tail(5)
                if (recent_returns.iloc[0] < -0.05 and 
                    recent_returns.iloc[-1] > 0.05 and
                    recent_returns.iloc[2] < recent_returns.iloc[0]):
                    patterns.append("V_pattern")
            
            # תבנית W
            if len(returns) >= 7:
                recent_returns = returns.tail(7)
                if (recent_returns.iloc[0] < -0.03 and
                    recent_returns.iloc[2] > 0.02 and
                    recent_returns.iloc[4] < -0.03 and
                    recent_returns.iloc[-1] > 0.02):
                    patterns.append("W_pattern")
            
            # תבנית קפיצה
            if len(returns) >= 3:
                recent_returns = returns.tail(3)
                if abs(recent_returns.iloc[-1]) > 0.1:
                    patterns.append("price_jump")
            
            # תבנית תנודתיות גבוהה
            if len(returns) >= 10:
                recent_volatility = returns.tail(10).std()
                if recent_volatility > returns.std() * 2:
                    patterns.append("high_volatility_period")
                    
        except Exception as e:
            logger.error(f"Error detecting price patterns: {str(e)}")
        
        return patterns

    def _detect_volume_patterns(self, price_df: pd.DataFrame) -> List[str]:
        """
        זיהוי תבניות נפח חריגות
        """
        patterns = []
        
        try:
            if 'volume' not in price_df.columns:
                return patterns
            
            volume = price_df['volume']
            volume_ma = volume.rolling(20).mean()
            
            # קפיצת נפח
            if len(volume) >= 3:
                recent_volume_ratio = volume.iloc[-1] / volume_ma.iloc[-1]
                if recent_volume_ratio > 5:
                    patterns.append("volume_spike")
            
            # ירידת נפח
            if len(volume) >= 3:
                recent_volume_ratio = volume.iloc[-1] / volume_ma.iloc[-1]
                if recent_volume_ratio < 0.2:
                    patterns.append("volume_drop")
            
            # תבנית נפח עולה
            if len(volume) >= 5:
                recent_volume_trend = np.polyfit(range(5), volume.tail(5), 1)[0]
                if recent_volume_trend > volume.mean() * 0.1:
                    patterns.append("increasing_volume_trend")
                    
        except Exception as e:
            logger.error(f"Error detecting volume patterns: {str(e)}")
        
        return patterns

    def _detect_volatility_patterns(self, price_df: pd.DataFrame) -> List[str]:
        """
        זיהוי תבניות תנודתיות
        """
        patterns = []
        
        try:
            returns = price_df['close'].pct_change().dropna()
            
            if len(returns) >= 10:
                # תנודתיות עולה
                recent_vol = returns.tail(5).std()
                older_vol = returns.tail(10).head(5).std()
                if recent_vol > older_vol * 1.5:
                    patterns.append("increasing_volatility")
                
                # תנודתיות יורדת
                if recent_vol < older_vol * 0.5:
                    patterns.append("decreasing_volatility")
                
                # תנודתיות גבוהה
                if recent_vol > returns.std() * 2:
                    patterns.append("high_volatility_period")
                    
        except Exception as e:
            logger.error(f"Error detecting volatility patterns: {str(e)}")
        
        return patterns

    def _detect_temporal_patterns(self, price_df: pd.DataFrame) -> List[str]:
        """
        זיהוי תבניות זמן
        """
        patterns = []
        
        try:
            returns = price_df['close'].pct_change().dropna()
            
            if len(returns) >= 10:
                # רצף חיובי ארוך
                positive_streak = self._find_consecutive_sequences(returns > 0)
                if positive_streak and max(positive_streak) > 7:
                    patterns.append("long_positive_streak")
                
                # רצף שלילי ארוך
                negative_streak = self._find_consecutive_sequences(returns < 0)
                if negative_streak and max(negative_streak) > 7:
                    patterns.append("long_negative_streak")
                
                # תנודתיות זמן
                if len(returns) >= 20:
                    early_vol = returns.head(10).std()
                    late_vol = returns.tail(10).std()
                    if late_vol > early_vol * 2:
                        patterns.append("volatility_expansion")
                    elif late_vol < early_vol * 0.5:
                        patterns.append("volatility_contraction")
                        
        except Exception as e:
            logger.error(f"Error detecting temporal patterns: {str(e)}")
        
        return patterns

    def _find_consecutive_sequences(self, condition: pd.Series) -> List[int]:
        """
        מציאת רצפים עוקבים
        """
        sequences = []
        current_length = 0
        
        for value in condition:
            if value:
                current_length += 1
            else:
                if current_length > 0:
                    sequences.append(current_length)
                current_length = 0
        
        if current_length > 0:
            sequences.append(current_length)
        
        return sequences

    def _calculate_anomaly_score(self, price_anomalies: Dict, volume_anomalies: Dict,
                               volatility_anomalies: Dict, statistical_anomalies: Dict,
                               multivariate_anomalies: Dict, temporal_anomalies: Dict) -> float:
        """
        חישוב ציון אנומליות כללי
        """
        try:
            # משקלות
            weights = {
                'price': 0.25,
                'volume': 0.20,
                'volatility': 0.15,
                'statistical': 0.15,
                'multivariate': 0.15,
                'temporal': 0.10
            }

            # ציונים
            price_score = min(price_anomalies.get('anomaly_ratio', 0) * 100, 100)
            volume_score = min(volume_anomalies.get('anomaly_ratio', 0) * 100, 100)
            volatility_score = min(volatility_anomalies.get('anomaly_ratio', 0) * 100, 100)
            statistical_score = min(statistical_anomalies.get('anomaly_score', 0) * 10, 100)
            multivariate_score = min(multivariate_anomalies.get('anomaly_ratio', 0) * 100, 100)
            temporal_score = min(temporal_anomalies.get('anomaly_ratio', 0) * 100, 100)

            # חישוב ציון משוקלל
            total_score = (
                price_score * weights['price'] +
                volume_score * weights['volume'] +
                volatility_score * weights['volatility'] +
                statistical_score * weights['statistical'] +
                multivariate_score * weights['multivariate'] +
                temporal_score * weights['temporal']
            )

            return min(max(total_score, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating anomaly score: {str(e)}")
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
            return "High Alert - Multiple anomalies detected, exercise caution"
        elif score >= 60:
            return "Moderate Alert - Several anomalies detected, monitor closely"
        elif score >= 40:
            return "Low Alert - Some anomalies detected, watch for changes"
        else:
            return "Normal - No significant anomalies detected"

    def _extract_key_signals(self, price_anomalies: Dict, volume_anomalies: Dict,
                           volatility_anomalies: Dict, statistical_anomalies: Dict,
                           multivariate_anomalies: Dict, temporal_anomalies: Dict) -> List[str]:
        """
        חילוץ אותות מפתח
        """
        signals = []

        # אותות מחיר
        if price_anomalies.get('extreme_moves', 0) > 0:
            signals.append(f"Extreme price moves: {price_anomalies['extreme_moves']}")

        # אותות נפח
        if volume_anomalies.get('volume_spikes', 0) > 0:
            signals.append(f"Volume spikes: {volume_anomalies['volume_spikes']}")

        # אותות תנודתיות
        if volatility_anomalies.get('volatility_spikes', 0) > 0:
            signals.append(f"Volatility spikes: {volatility_anomalies['volatility_spikes']}")

        # אותות סטטיסטיים
        if statistical_anomalies.get('distribution_anomalies'):
            signals.append(f"Distribution anomalies: {', '.join(statistical_anomalies['distribution_anomalies'])}")

        # אותות רב-ממדיים
        if multivariate_anomalies.get('total_multivariate_anomalies', 0) > 0:
            signals.append(f"Multivariate anomalies: {multivariate_anomalies['total_multivariate_anomalies']}")

        # אותות זמן
        if temporal_anomalies.get('extreme_positive_runs', 0) > 0:
            signals.append(f"Extreme positive runs: {temporal_anomalies['extreme_positive_runs']}")

        return signals

    def _create_empty_anomaly_analysis(self) -> Dict[str, Any]:
        """
        יצירת ניתוח אנומליות ריק
        """
        return {
            "total_anomalies": 0,
            "anomaly_ratio": 0,
            "anomaly_dates": []
        }

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