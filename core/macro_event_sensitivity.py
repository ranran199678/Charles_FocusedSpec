"""
Macro Event Sensitivity - רגישות מאקרו
========================================

סוכן המזהה רגישות מניות לאירועים מאקרו ומזהה הזדמנויות מסחר.
מבוסס על ניתוח תגובת מניות לאירועים כלכליים וזיהוי קורלציות מאקרו.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from core.base.base_agent import BaseAgent
from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("MacroEventSensitivity")

class MacroEventSensitivity(BaseAgent):
    """
    סוכן לניתוח רגישות מאקרו
    """
    
    def __init__(self, config=None):
        """
        אתחול הסוכן
        """
        super().__init__(config)
        self.name = "Macro Event Sensitivity"
        self.version = "1.0.0"
        self.description = "מזהה רגישות מניות לאירועים מאקרו"
        
        # פרמטרים לניתוח
        self.correlation_threshold = 0.6  # קורלציה מינימלית עם מדדים מאקרו
        self.volatility_threshold = 0.25  # תנודתיות גבוהה 25%
        self.beta_threshold = 1.2  # בטא גבוה 1.2
        self.event_sensitivity_threshold = 0.05  # רגישות לאירועים 5%
        self.sector_correlation_threshold = 0.7  # קורלציה סקטוריאלית 70%
        
        # אירועים מאקרו נפוצים
        self.macro_events = [
            'fomc_meeting', 'fed_rate_decision', 'employment_report',
            'gdp_report', 'inflation_data', 'retail_sales',
            'manufacturing_pmi', 'services_pmi', 'housing_data',
            'trade_balance', 'consumer_confidence', 'business_sentiment'
        ]
        
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def analyze(self, symbol: str, price_df: pd.DataFrame = None, **kwargs) -> Dict[str, Any]:
        """
        ניתוח רגישות מאקרו
        
        Args:
            symbol: סמל המניה
            price_df: נתוני מחיר
            **kwargs: פרמטרים נוספים
            
        Returns:
            תוצאות הניתוח
        """
        try:
            self.log(f"Starting macro event sensitivity analysis for {symbol}")
            
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=180)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            # אימות נתונים
            if not validate_symbol(symbol):
                return self.fallback()
            
            if not validate_stock_data(price_df):
                return self.fallback()
            
            # קבלת נתונים נוספים מ-kwargs
            market_data = kwargs.get('market_data')
            sector_data = kwargs.get('sector_data')
            macro_events_data = kwargs.get('macro_events_data')
            economic_indicators = kwargs.get('economic_indicators')
            
            # ניתוח קורלציה עם שוק
            market_correlation_analysis = self._analyze_market_correlation(
                price_df, market_data
            )
            
            # ניתוח בטא
            beta_analysis = self._analyze_beta(price_df, market_data)
            
            # ניתוח רגישות לאירועים
            event_sensitivity_analysis = self._analyze_event_sensitivity(
                price_df, macro_events_data
            )
            
            # ניתוח קורלציה סקטוריאלית
            sector_correlation_analysis = self._analyze_sector_correlation(
                price_df, sector_data
            )
            
            # ניתוח תנודתיות מאקרו
            macro_volatility_analysis = self._analyze_macro_volatility(
                price_df, economic_indicators
            )
            
            # ניתוח רגישות כלכלית
            economic_sensitivity_analysis = self._analyze_economic_sensitivity(
                price_df, economic_indicators
            )
            
            # חישוב ציון כללי
            score = self._calculate_macro_sensitivity_score(
                market_correlation_analysis,
                beta_analysis,
                event_sensitivity_analysis,
                sector_correlation_analysis,
                macro_volatility_analysis,
                economic_sensitivity_analysis
            )
            
            # קביעת רמת ביטחון
            confidence = self._determine_confidence_level(score)
            
            # יצירת המלצה
            recommendation = self._generate_recommendation(score, confidence)
            
            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                market_correlation_analysis,
                beta_analysis,
                event_sensitivity_analysis,
                sector_correlation_analysis,
                macro_volatility_analysis,
                economic_sensitivity_analysis
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
                    "market_correlation": market_correlation_analysis,
                    "beta_analysis": beta_analysis,
                    "event_sensitivity": event_sensitivity_analysis,
                    "sector_correlation": sector_correlation_analysis,
                    "macro_volatility": macro_volatility_analysis,
                    "economic_sensitivity": economic_sensitivity_analysis
                },
                "metadata": {
                    "correlation_threshold": self.correlation_threshold,
                    "volatility_threshold": self.volatility_threshold,
                    "beta_threshold": self.beta_threshold,
                    "event_sensitivity_threshold": self.event_sensitivity_threshold,
                    "sector_correlation_threshold": self.sector_correlation_threshold
                }
            }
            
            self.log(f"Macro sensitivity analysis completed for {symbol} - Score: {score:.2f}, Confidence: {confidence}")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()
    
    def _analyze_market_correlation(self, price_df: pd.DataFrame,
                                  market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח קורלציה עם שוק"""
        try:
            if market_data is None:
                return {
                    "has_market_data": False,
                    "correlation": 0.0,
                    "high_correlation": False
                }
            
            stock_returns = price_df['close'].pct_change()
            market_returns = market_data['close'].pct_change()
            
            # התאמת נתונים לתקופה זהה
            common_dates = stock_returns.index.intersection(market_returns.index)
            if len(common_dates) < 30:
                return {
                    "has_market_data": True,
                    "correlation": 0.0,
                    "high_correlation": False,
                    "insufficient_data": True
                }
            
            stock_series = stock_returns.loc[common_dates]
            market_series = market_returns.loc[common_dates]
            
            # חישוב קורלציה
            correlation = stock_series.corr(market_series)
            high_correlation = abs(correlation) > self.correlation_threshold
            
            return {
                "has_market_data": True,
                "correlation": correlation,
                "high_correlation": high_correlation,
                "threshold_exceeded": high_correlation
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market correlation: {str(e)}")
            return {
                "has_market_data": False,
                "error": str(e)
            }
    
    def _analyze_beta(self, price_df: pd.DataFrame,
                     market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח בטא"""
        try:
            if market_data is None:
                return {
                    "has_market_data": False,
                    "beta": 1.0,
                    "high_beta": False
                }
            
            stock_returns = price_df['close'].pct_change()
            market_returns = market_data['close'].pct_change()
            
            # התאמת נתונים
            common_dates = stock_returns.index.intersection(market_returns.index)
            if len(common_dates) < 30:
                return {
                    "has_market_data": True,
                    "beta": 1.0,
                    "high_beta": False,
                    "insufficient_data": True
                }
            
            stock_series = stock_returns.loc[common_dates]
            market_series = market_returns.loc[common_dates]
            
            # חישוב בטא
            covariance = np.cov(stock_series, market_series)[0, 1]
            market_variance = np.var(market_series)
            beta = covariance / market_variance if market_variance > 0 else 1.0
            
            high_beta = abs(beta) > self.beta_threshold
            
            return {
                "has_market_data": True,
                "beta": beta,
                "high_beta": high_beta,
                "threshold_exceeded": high_beta
            }
            
        except Exception as e:
            logger.error(f"Error analyzing beta: {str(e)}")
            return {
                "has_market_data": False,
                "error": str(e)
            }
    
    def _analyze_event_sensitivity(self, price_df: pd.DataFrame,
                                 macro_events_data: List[Dict] = None) -> Dict[str, Any]:
        """ניתוח רגישות לאירועים"""
        try:
            if not macro_events_data:
                return {
                    "has_events_data": False,
                    "event_sensitivity": 0.0,
                    "high_sensitivity": False
                }
            
            # ניתוח תגובות לאירועים
            event_responses = []
            
            for event in macro_events_data:
                event_date = event.get('date')
                event_type = event.get('type')
                
                if event_date and event_type:
                    # חישוב תגובת מחיר לאירוע
                    response = self._calculate_event_response(
                        price_df, event_date, event_type
                    )
                    if response is not None:
                        event_responses.append(response)
            
            if not event_responses:
                return {
                    "has_events_data": True,
                    "event_sensitivity": 0.0,
                    "high_sensitivity": False
                }
            
            # חישוב רגישות ממוצעת
            avg_sensitivity = np.mean([abs(r) for r in event_responses])
            high_sensitivity = avg_sensitivity > self.event_sensitivity_threshold
            
            return {
                "has_events_data": True,
                "event_sensitivity": avg_sensitivity,
                "event_responses": event_responses,
                "high_sensitivity": high_sensitivity,
                "threshold_exceeded": high_sensitivity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing event sensitivity: {str(e)}")
            return {
                "has_events_data": False,
                "error": str(e)
            }
    
    def _analyze_sector_correlation(self, price_df: pd.DataFrame,
                                  sector_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח קורלציה סקטוריאלית"""
        try:
            if sector_data is None:
                return {
                    "has_sector_data": False,
                    "sector_correlation": 0.0,
                    "high_sector_correlation": False
                }
            
            stock_returns = price_df['close'].pct_change()
            sector_returns = sector_data['close'].pct_change()
            
            # התאמת נתונים
            common_dates = stock_returns.index.intersection(sector_returns.index)
            if len(common_dates) < 30:
                return {
                    "has_sector_data": True,
                    "sector_correlation": 0.0,
                    "high_sector_correlation": False,
                    "insufficient_data": True
                }
            
            stock_series = stock_returns.loc[common_dates]
            sector_series = sector_returns.loc[common_dates]
            
            # חישוב קורלציה
            correlation = stock_series.corr(sector_series)
            high_correlation = abs(correlation) > self.sector_correlation_threshold
            
            return {
                "has_sector_data": True,
                "sector_correlation": correlation,
                "high_sector_correlation": high_correlation,
                "threshold_exceeded": high_correlation
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector correlation: {str(e)}")
            return {
                "has_sector_data": False,
                "error": str(e)
            }
    
    def _analyze_macro_volatility(self, price_df: pd.DataFrame,
                                economic_indicators: Dict = None) -> Dict[str, Any]:
        """ניתוח תנודתיות מאקרו"""
        try:
            prices = price_df['close']
            
            # חישוב תנודתיות
            volatility = prices.pct_change().std() * np.sqrt(252)
            high_volatility = volatility > self.volatility_threshold
            
            # ניתוח תנודתיות ביחס לאינדיקטורים כלכליים
            economic_volatility_analysis = self._analyze_economic_volatility(
                prices, economic_indicators
            )
            
            return {
                "volatility": volatility,
                "high_volatility": high_volatility,
                "economic_volatility_analysis": economic_volatility_analysis,
                "threshold_exceeded": high_volatility
            }
            
        except Exception as e:
            logger.error(f"Error analyzing macro volatility: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _analyze_economic_sensitivity(self, price_df: pd.DataFrame,
                                    economic_indicators: Dict = None) -> Dict[str, Any]:
        """ניתוח רגישות כלכלית"""
        try:
            if not economic_indicators:
                return {
                    "has_economic_data": False,
                    "economic_sensitivity": 0.0,
                    "high_economic_sensitivity": False
                }
            
            # ניתוח רגישות לאינדיקטורים כלכליים
            sensitivity_scores = []
            
            for indicator, data in economic_indicators.items():
                sensitivity = self._calculate_economic_sensitivity(
                    price_df, data
                )
                if sensitivity is not None:
                    sensitivity_scores.append(sensitivity)
            
            if not sensitivity_scores:
                return {
                    "has_economic_data": True,
                    "economic_sensitivity": 0.0,
                    "high_economic_sensitivity": False
                }
            
            # חישוב רגישות ממוצעת
            avg_sensitivity = np.mean(sensitivity_scores)
            high_sensitivity = avg_sensitivity > self.event_sensitivity_threshold
            
            return {
                "has_economic_data": True,
                "economic_sensitivity": avg_sensitivity,
                "sensitivity_scores": sensitivity_scores,
                "high_economic_sensitivity": high_sensitivity,
                "threshold_exceeded": high_sensitivity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing economic sensitivity: {str(e)}")
            return {
                "has_economic_data": False,
                "error": str(e)
            }
    
    def _calculate_macro_sensitivity_score(self, market_correlation_analysis: Dict,
                                         beta_analysis: Dict,
                                         event_sensitivity_analysis: Dict,
                                         sector_correlation_analysis: Dict,
                                         macro_volatility_analysis: Dict,
                                         economic_sensitivity_analysis: Dict) -> float:
        """חישוב ציון כללי"""
        try:
            score = 0.0
            max_score = 100.0
            
            # ציון קורלציה עם שוק (20 נקודות)
            if market_correlation_analysis.get("high_correlation", False):
                correlation = abs(market_correlation_analysis.get("correlation", 0))
                score += min(20, (correlation / 0.8) * 20)
            
            # ציון בטא (20 נקודות)
            if beta_analysis.get("high_beta", False):
                beta = abs(beta_analysis.get("beta", 1.0))
                score += min(20, (beta / 2.0) * 20)
            
            # ציון רגישות לאירועים (25 נקודות)
            if event_sensitivity_analysis.get("high_sensitivity", False):
                sensitivity = event_sensitivity_analysis.get("event_sensitivity", 0)
                score += min(25, (sensitivity / 0.1) * 25)
            
            # ציון קורלציה סקטוריאלית (15 נקודות)
            if sector_correlation_analysis.get("high_sector_correlation", False):
                correlation = abs(sector_correlation_analysis.get("sector_correlation", 0))
                score += min(15, (correlation / 0.8) * 15)
            
            # ציון תנודתיות מאקרו (10 נקודות)
            if macro_volatility_analysis.get("high_volatility", False):
                volatility = macro_volatility_analysis.get("volatility", 0)
                score += min(10, (volatility / 0.5) * 10)
            
            # ציון רגישות כלכלית (10 נקודות)
            if economic_sensitivity_analysis.get("high_economic_sensitivity", False):
                sensitivity = economic_sensitivity_analysis.get("economic_sensitivity", 0)
                score += min(10, (sensitivity / 0.1) * 10)
            
            return min(score, max_score)
            
        except Exception as e:
            logger.error(f"Error calculating macro sensitivity score: {str(e)}")
            return 0.0
    
    def _determine_confidence_level(self, score: float) -> str:
        """קביעת רמת ביטחון"""
        if score >= 80:
            return "HIGH"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _generate_recommendation(self, score: float, confidence: str) -> str:
        """יצירת המלצה"""
        if score >= 80:
            return "STRONG_BUY - High macro sensitivity opportunity"
        elif score >= 60:
            return "BUY - Significant macro sensitivity detected"
        elif score >= 40:
            return "WATCH - Monitor macro sensitivity"
        else:
            return "HOLD - Low macro sensitivity"
    
    def _extract_key_signals(self, market_correlation_analysis: Dict,
                            beta_analysis: Dict,
                            event_sensitivity_analysis: Dict,
                            sector_correlation_analysis: Dict,
                            macro_volatility_analysis: Dict,
                            economic_sensitivity_analysis: Dict) -> List[str]:
        """חילוץ אותות מפתח"""
        signals = []
        
        if market_correlation_analysis.get("high_correlation", False):
            correlation = market_correlation_analysis.get("correlation", 0)
            signals.append(f"High market correlation: {correlation:.2f}")
        
        if beta_analysis.get("high_beta", False):
            beta = beta_analysis.get("beta", 1.0)
            signals.append(f"High beta: {beta:.2f}")
        
        if event_sensitivity_analysis.get("high_sensitivity", False):
            sensitivity = event_sensitivity_analysis.get("event_sensitivity", 0)
            signals.append(f"High event sensitivity: {sensitivity:.2f}")
        
        if sector_correlation_analysis.get("high_sector_correlation", False):
            correlation = sector_correlation_analysis.get("sector_correlation", 0)
            signals.append(f"High sector correlation: {correlation:.2f}")
        
        if macro_volatility_analysis.get("high_volatility", False):
            volatility = macro_volatility_analysis.get("volatility", 0)
            signals.append(f"High macro volatility: {volatility:.1%}")
        
        if economic_sensitivity_analysis.get("high_economic_sensitivity", False):
            sensitivity = economic_sensitivity_analysis.get("economic_sensitivity", 0)
            signals.append(f"High economic sensitivity: {sensitivity:.2f}")
        
        return signals
    
    def _calculate_event_response(self, price_df: pd.DataFrame,
                                event_date: str, event_type: str) -> Optional[float]:
        """חישוב תגובת מחיר לאירוע"""
        try:
            event_date = pd.to_datetime(event_date)
            
            # חישוב תגובה יומית
            if event_date in price_df.index:
                event_idx = price_df.index.get_loc(event_date)
                
                if event_idx > 0 and event_idx < len(price_df) - 1:
                    pre_event_price = price_df['close'].iloc[event_idx - 1]
                    post_event_price = price_df['close'].iloc[event_idx + 1]
                    
                    response = (post_event_price - pre_event_price) / pre_event_price
                    return response
            
            return None
            
        except Exception:
            return None
    
    def _analyze_economic_volatility(self, prices: pd.Series,
                                   economic_indicators: Dict = None) -> Dict[str, Any]:
        """ניתוח תנודתיות כלכלית"""
        try:
            if not economic_indicators:
                return {"has_data": False}
            
            # ניתוח תנודתיות ביחס לאינדיקטורים
            volatility_analysis = {}
            
            for indicator, data in economic_indicators.items():
                if isinstance(data, pd.Series):
                    # חישוב קורלציה עם אינדיקטור
                    common_dates = prices.index.intersection(data.index)
                    if len(common_dates) > 10:
                        price_series = prices.loc[common_dates]
                        indicator_series = data.loc[common_dates]
                        correlation = price_series.corr(indicator_series)
                        volatility_analysis[indicator] = correlation
            
            return {
                "has_data": True,
                "indicator_correlations": volatility_analysis
            }
            
        except Exception:
            return {"has_data": False}
    
    def _calculate_economic_sensitivity(self, price_df: pd.DataFrame,
                                      economic_data: pd.Series) -> Optional[float]:
        """חישוב רגישות כלכלית"""
        try:
            if not isinstance(economic_data, pd.Series):
                return None
            
            stock_returns = price_df['close'].pct_change()
            
            # התאמת נתונים
            common_dates = stock_returns.index.intersection(economic_data.index)
            if len(common_dates) < 20:
                return None
            
            stock_series = stock_returns.loc[common_dates]
            economic_series = economic_data.loc[common_dates]
            
            # חישוב רגישות
            sensitivity = stock_series.corr(economic_series)
            return abs(sensitivity) if not np.isnan(sensitivity) else None
            
        except Exception:
            return None
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """יצירת תוצאת שגיאה"""
        return {
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "version": self.version,
            "score": 0.0,
            "confidence": "ERROR",
            "recommendation": "ERROR",
            "key_signals": [f"Error: {error_message}"]
        }