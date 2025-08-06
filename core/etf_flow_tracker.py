"""
ETF Flow Tracker - מעקב אחר זרימות ETF
=======================================

סוכן המעקב אחר זרימות כספים ב-ETFs ומזהה מגמות השקעה.
מבוסס על ניתוח נפח, שווי נכסים וזרימות כספים.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from core.base.base_agent import BaseAgent
from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("ETFFlowTracker")

class ETFFlowTracker(BaseAgent):
    """
    סוכן למעקב אחר זרימות ETF
    
    מנתח זרימות כספים ב-ETFs ומזהה:
    - ETFs עם זרימות חיוביות/שליליות
    - מגמות השקעה בסקטורים
    - שינויים בהעדפות משקיעים
    - הזדמנויות השקעה
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן"""
        super().__init__(config)
        self.name = "ETFFlowTracker"
        self.description = "מעקב אחר זרימות ETF"
        self.version = "1.0.0"
        
        # הגדרת ETFs עיקריים לפי קטגוריות
        self.etf_categories = {
            'broad_market': {
                'SPY': 'S&P 500 ETF',
                'VTI': 'Vanguard Total Stock Market',
                'QQQ': 'NASDAQ-100 ETF',
                'IWM': 'Russell 2000 ETF'
            },
            'sector_etfs': {
                'XLK': 'Technology Select Sector',
                'XLF': 'Financial Select Sector',
                'XLE': 'Energy Select Sector',
                'XLV': 'Healthcare Select Sector',
                'XLI': 'Industrial Select Sector',
                'XLP': 'Consumer Staples Select Sector',
                'XLY': 'Consumer Discretionary Select Sector',
                'XLU': 'Utilities Select Sector',
                'XLB': 'Materials Select Sector',
                'XLRE': 'Real Estate Select Sector'
            },
            'international': {
                'EFA': 'MSCI EAFE ETF',
                'EEM': 'MSCI Emerging Markets ETF',
                'VEA': 'Vanguard FTSE Developed Markets',
                'VWO': 'Vanguard FTSE Emerging Markets'
            },
            'bonds': {
                'TLT': '20+ Year Treasury Bond ETF',
                'AGG': 'Core U.S. Aggregate Bond ETF',
                'LQD': 'Investment Grade Corporate Bond ETF',
                'HYG': 'High Yield Corporate Bond ETF'
            },
            'commodities': {
                'GLD': 'SPDR Gold Shares',
                'SLV': 'iShares Silver Trust',
                'USO': 'United States Oil Fund',
                'DBA': 'Invesco DB Agriculture Fund'
            }
        }
        
        # פרמטרים לניתוח
        self.lookback_periods = {
            'short': 5,
            'medium': 20,
            'long': 60
        }
        
        self.flow_threshold = 0.05  # 5% שינוי בנפח לזרימה משמעותית
        self.aum_threshold = 0.02  # 2% שינוי בשווי נכסים
        
        logger.info(f"אתחול {self.name} v{self.version}")
    
    def analyze(self, symbol: str, price_df: pd.DataFrame = None, **kwargs) -> Dict[str, Any]:
        """
        ניתוח זרימות ETF
        
        Args:
            symbol: סימול המניה
            price_df: DataFrame עם נתוני מחיר
            **kwargs: פרמטרים נוספים
            
        Returns:
            Dict[str, Any]: תוצאות הניתוח
        """
        try:
            self.log("התחלת ניתוח זרימות ETF")
            
            # קבלת נתונים דרך מנהל הנתונים החכם אם לא הועברו
            if price_df is None:
                price_df = self.get_stock_data(symbol, days=180)
                if price_df is None or price_df.empty:
                    return self.fallback()
            
            # יצירת מילון נתוני ETF (לצורך תאימות)
            etf_data = {symbol: price_df}
            aum_data = kwargs.get('aum_data')
            
            # אימות נתונים
            if not etf_data:
                return self.fallback()
            
            # ניתוח זרימות נפח
            volume_flow_analysis = self._analyze_volume_flows(etf_data)
            
            # ניתוח שווי נכסים
            aum_analysis = self._analyze_aum_changes(etf_data, aum_data)
            
            # ניתוח ביצועים יחסיים
            performance_analysis = self._analyze_relative_performance(etf_data)
            
            # ניתוח קורלציות
            correlation_analysis = self._analyze_etf_correlations(etf_data)
            
            # ניתוח מגמות קטגוריות
            category_analysis = self._analyze_category_trends(etf_data)
            
            # חישוב ציונים
            etf_scores = self._calculate_etf_scores(
                volume_flow_analysis, aum_analysis, performance_analysis
            )
            
            # דירוג ETFs
            etf_rankings = self._rank_etfs(etf_scores)
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(etf_rankings, category_analysis)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'agent': self.name,
                'version': self.version,
                'etf_rankings': etf_rankings,
                'recommendations': recommendations,
                'analysis': {
                    'volume_flow_analysis': volume_flow_analysis,
                    'aum_analysis': aum_analysis,
                    'performance_analysis': performance_analysis,
                    'correlation_analysis': correlation_analysis,
                    'category_analysis': category_analysis
                },
                'etf_scores': etf_scores,
                'top_inflows': self._get_top_inflows(etf_rankings, 5),
                'top_outflows': self._get_top_outflows(etf_rankings, 5),
                'category_summary': self._get_category_summary(category_analysis),
                'status': 'success'
            }
            
            self.log("ניתוח זרימות ETF הושלם")
            return result
            
        except Exception as e:
            self.handle_error(e)
            return self.fallback()
    
    def _analyze_volume_flows(self, etf_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח זרימות נפח"""
        try:
            volume_analysis = {}
            
            for etf_symbol, etf_df in etf_data.items():
                if etf_df is None or etf_df.empty:
                    continue
                
                etf_df = etf_df.copy()
                
                # חישוב ממוצעי נפח
                etf_df['volume_sma_20'] = etf_df['Volume'].rolling(window=20).mean()
                etf_df['volume_sma_60'] = etf_df['Volume'].rolling(window=60).mean()
                
                # חישוב יחסי נפח
                etf_df['volume_ratio_20'] = etf_df['Volume'] / etf_df['volume_sma_20']
                etf_df['volume_ratio_60'] = etf_df['Volume'] / etf_df['volume_sma_60']
                
                # זיהוי זרימות משמעותיות
                high_volume_20 = etf_df['volume_ratio_20'] > self.flow_threshold
                high_volume_60 = etf_df['volume_ratio_60'] > self.flow_threshold
                
                # ניתוח נפח במחיר עולה/יורד
                etf_df['price_change'] = etf_df['Close'].pct_change()
                volume_on_up = (etf_df['price_change'] > 0) & high_volume_20
                volume_on_down = (etf_df['price_change'] < 0) & high_volume_20
                
                # חישוב ציונים
                avg_volume_ratio = etf_df['volume_ratio_20'].tail(20).mean()
                volume_trend = etf_df['volume_ratio_20'].tail(5).mean() - etf_df['volume_ratio_20'].tail(20).mean()
                up_volume_score = volume_on_up.sum() / len(etf_df) * 100
                down_volume_score = volume_on_down.sum() / len(etf_df) * 100
                
                volume_analysis[etf_symbol] = {
                    'avg_volume_ratio': avg_volume_ratio,
                    'volume_trend': volume_trend,
                    'up_volume_score': up_volume_score,
                    'down_volume_score': down_volume_score,
                    'high_volume_days': high_volume_20.sum(),
                    'recent_volume_surge': avg_volume_ratio > 1.5,
                    'volume_increasing': volume_trend > 0.1
                }
            
            return volume_analysis
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח זרימות נפח: {str(e)}")
            return {}
    
    def _analyze_aum_changes(self, etf_data: Dict[str, pd.DataFrame], 
                            aum_data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """ניתוח שינויים בשווי נכסים"""
        try:
            aum_analysis = {}
            
            for etf_symbol, etf_df in etf_data.items():
                if etf_df is None or etf_df.empty:
                    continue
                
                etf_df = etf_df.copy()
                
                # חישוב שווי נכסים משוער (מחיר * נפח)
                etf_df['estimated_aum'] = etf_df['Close'] * etf_df['Volume']
                
                # חישוב שינויים בשווי נכסים
                etf_df['aum_change'] = etf_df['estimated_aum'].pct_change()
                etf_df['aum_sma_20'] = etf_df['estimated_aum'].rolling(window=20).mean()
                
                # זיהוי שינויים משמעותיים
                significant_aum_change = abs(etf_df['aum_change']) > self.aum_threshold
                
                # חישוב ציונים
                recent_aum_change = etf_df['aum_change'].tail(5).sum()
                aum_trend = etf_df['estimated_aum'].tail(5).mean() / etf_df['estimated_aum'].tail(20).mean() - 1
                aum_volatility = etf_df['aum_change'].tail(20).std()
                
                aum_analysis[etf_symbol] = {
                    'recent_aum_change': recent_aum_change,
                    'aum_trend': aum_trend,
                    'aum_volatility': aum_volatility,
                    'significant_changes': significant_aum_change.sum(),
                    'aum_increasing': aum_trend > 0.05,
                    'aum_decreasing': aum_trend < -0.05,
                    'current_aum': etf_df['estimated_aum'].iloc[-1]
                }
            
            return aum_analysis
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח שווי נכסים: {str(e)}")
            return {}
    
    def _analyze_relative_performance(self, etf_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח ביצועים יחסיים"""
        try:
            performance_analysis = {}
            
            for etf_symbol, etf_df in etf_data.items():
                if etf_df is None or etf_df.empty:
                    continue
                
                etf_df = etf_df.copy()
                etf_df['returns'] = etf_df['Close'].pct_change()
                
                # חישוב תשואות לתקופות שונות
                returns_5d = etf_df['returns'].tail(5).sum()
                returns_20d = etf_df['returns'].tail(20).sum()
                returns_60d = etf_df['returns'].tail(60).sum()
                
                # חישוב תנודתיות
                volatility_20d = etf_df['returns'].tail(20).std() * np.sqrt(252)
                volatility_60d = etf_df['returns'].tail(60).std() * np.sqrt(252)
                
                # חישוב Sharpe ratio (פישוט)
                risk_free_rate = 0.02  # 2% שנתי
                sharpe_ratio = (returns_20d * 252/20 - risk_free_rate) / volatility_20d if volatility_20d > 0 else 0
                
                # זיהוי מגמות
                price_trend = etf_df['Close'].tail(20).iloc[-1] / etf_df['Close'].tail(20).iloc[0] - 1
                
                performance_analysis[etf_symbol] = {
                    'returns_5d': returns_5d,
                    'returns_20d': returns_20d,
                    'returns_60d': returns_60d,
                    'volatility_20d': volatility_20d,
                    'volatility_60d': volatility_60d,
                    'sharpe_ratio': sharpe_ratio,
                    'price_trend': price_trend,
                    'outperforming': returns_20d > 0.05,  # 5% ב-20 ימים
                    'underperforming': returns_20d < -0.05
                }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח ביצועים יחסיים: {str(e)}")
            return {}
    
    def _analyze_etf_correlations(self, etf_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח קורלציות בין ETFs"""
        try:
            # יצירת DataFrame עם תשואות כל ה-ETFs
            returns_data = {}
            
            for etf_symbol, etf_df in etf_data.items():
                if etf_df is not None and not etf_df.empty:
                    etf_df = etf_df.copy()
                    etf_df['returns'] = etf_df['Close'].pct_change()
                    returns_data[etf_symbol] = etf_df['returns']
            
            if len(returns_data) < 2:
                return {}
            
            # יצירת DataFrame קורלציות
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            
            # חישוב קורלציות ממוצעות
            avg_correlations = {}
            for etf in returns_data.keys():
                correlations = correlation_matrix[etf].drop(etf)
                avg_correlations[etf] = correlations.mean()
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'average_correlations': avg_correlations,
                'high_correlation_pairs': self._find_high_correlation_pairs(correlation_matrix)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח קורלציות: {str(e)}")
            return {}
    
    def _analyze_category_trends(self, etf_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח מגמות קטגוריות"""
        try:
            category_analysis = {}
            
            for category, etfs in self.etf_categories.items():
                category_returns = []
                category_volumes = []
                
                for etf_symbol in etfs.keys():
                    if etf_symbol in etf_data and etf_data[etf_symbol] is not None:
                        etf_df = etf_data[etf_symbol].copy()
                        etf_df['returns'] = etf_df['Close'].pct_change()
                        
                        # תשואות אחרונות
                        recent_return = etf_df['returns'].tail(20).sum()
                        category_returns.append(recent_return)
                        
                        # נפח ממוצע
                        avg_volume = etf_df['Volume'].tail(20).mean()
                        category_volumes.append(avg_volume)
                
                if category_returns:
                    category_analysis[category] = {
                        'avg_return': np.mean(category_returns),
                        'return_std': np.std(category_returns),
                        'total_volume': np.sum(category_volumes),
                        'etf_count': len(category_returns),
                        'best_performer': max(category_returns) if category_returns else 0,
                        'worst_performer': min(category_returns) if category_returns else 0,
                        'positive_returns': sum(1 for r in category_returns if r > 0),
                        'negative_returns': sum(1 for r in category_returns if r < 0)
                    }
            
            return category_analysis
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח מגמות קטגוריות: {str(e)}")
            return {}
    
    def _calculate_etf_scores(self, volume_analysis: Dict, aum_analysis: Dict, 
                             performance_analysis: Dict) -> Dict[str, float]:
        """חישוב ציונים כללים ל-ETFs"""
        try:
            etf_scores = {}
            
            for etf_symbol in set(volume_analysis.keys()) | set(aum_analysis.keys()) | set(performance_analysis.keys()):
                score = 0.0
                weight_count = 0
                
                # ציון מזרימות נפח (30%)
                if etf_symbol in volume_analysis:
                    vol_analysis = volume_analysis[etf_symbol]
                    vol_score = min(vol_analysis.get('avg_volume_ratio', 1) * 50, 100)
                    if vol_analysis.get('volume_increasing', False):
                        vol_score += 20
                    score += vol_score * 0.3
                    weight_count += 0.3
                
                # ציון משווי נכסים (25%)
                if etf_symbol in aum_analysis:
                    aum_analysis_data = aum_analysis[etf_symbol]
                    aum_trend = aum_analysis_data.get('aum_trend', 0)
                    aum_score = max(0, min(100, (aum_trend + 0.1) * 500))  # נרמול
                    score += aum_score * 0.25
                    weight_count += 0.25
                
                # ציון מביצועים (45%)
                if etf_symbol in performance_analysis:
                    perf_analysis = performance_analysis[etf_symbol]
                    returns_20d = perf_analysis.get('returns_20d', 0)
                    sharpe = perf_analysis.get('sharpe_ratio', 0)
                    
                    # ציון תשואות
                    returns_score = max(0, min(100, (returns_20d + 0.2) * 250))
                    
                    # ציון Sharpe
                    sharpe_score = max(0, min(100, (sharpe + 1) * 50))
                    
                    perf_score = (returns_score + sharpe_score) / 2
                    score += perf_score * 0.45
                    weight_count += 0.45
                
                # נרמול לפי משקלים
                if weight_count > 0:
                    etf_scores[etf_symbol] = score / weight_count
                else:
                    etf_scores[etf_symbol] = 0.0
            
            return etf_scores
            
        except Exception as e:
            logger.error(f"שגיאה בחישוב ציוני ETFs: {str(e)}")
            return {}
    
    def _rank_etfs(self, etf_scores: Dict[str, float]) -> List[Tuple[str, float]]:
        """דירוג ETFs לפי ציונים"""
        try:
            ranked_etfs = sorted(etf_scores.items(), key=lambda x: x[1], reverse=True)
            return ranked_etfs
        except Exception as e:
            logger.error(f"שגיאה בדירוג ETFs: {str(e)}")
            return []
    
    def _generate_recommendations(self, etf_rankings: List[Tuple[str, float]], 
                                 category_analysis: Dict) -> List[str]:
        """יצירת המלצות"""
        try:
            recommendations = []
            
            if not etf_rankings:
                return ["אין מספיק נתונים להמלצות"]
            
            # המלצות על ETFs מובילים
            top_etfs = etf_rankings[:5]
            recommendations.append(f"ETFs מובילים: {', '.join([e[0] for e in top_etfs])}")
            
            # המלצות על קטגוריות
            if category_analysis:
                best_category = max(category_analysis.items(), 
                                  key=lambda x: x[1].get('avg_return', 0))
                worst_category = min(category_analysis.items(), 
                                   key=lambda x: x[1].get('avg_return', 0))
                
                recommendations.append(f"קטגוריה מובילה: {best_category[0]} (תשואה: {best_category[1]['avg_return']:.2%})")
                recommendations.append(f"קטגוריה יורדת: {worst_category[0]} (תשואה: {worst_category[1]['avg_return']:.2%})")
            
            # המלצות כלליות
            if len(etf_rankings) >= 2:
                top_score = etf_rankings[0][1]
                bottom_score = etf_rankings[-1][1]
                score_spread = top_score - bottom_score
                
                if score_spread > 30:
                    recommendations.append("פיזור גבוה בין ETFs - הזדמנות לרוטציה")
                elif score_spread < 10:
                    recommendations.append("פיזור נמוך בין ETFs - שוק מאוזן")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"שגיאה ביצירת המלצות: {str(e)}")
            return ["שגיאה ביצירת המלצות"]
    
    def _get_top_inflows(self, etf_rankings: List[Tuple[str, float]], count: int) -> List[Dict]:
        """קבלת ETFs עם זרימות חיוביות"""
        try:
            top_inflows = []
            for i, (etf, score) in enumerate(etf_rankings[:count]):
                top_inflows.append({
                    'rank': i + 1,
                    'etf': etf,
                    'score': score,
                    'category': self._get_etf_category(etf)
                })
            return top_inflows
        except Exception as e:
            logger.error(f"שגיאה בקבלת זרימות חיוביות: {str(e)}")
            return []
    
    def _get_top_outflows(self, etf_rankings: List[Tuple[str, float]], count: int) -> List[Dict]:
        """קבלת ETFs עם זרימות שליליות"""
        try:
            top_outflows = []
            for i, (etf, score) in enumerate(etf_rankings[-count:]):
                top_outflows.append({
                    'rank': len(etf_rankings) - count + i + 1,
                    'etf': etf,
                    'score': score,
                    'category': self._get_etf_category(etf)
                })
            return top_outflows
        except Exception as e:
            logger.error(f"שגיאה בקבלת זרימות שליליות: {str(e)}")
            return []
    
    def _get_category_summary(self, category_analysis: Dict) -> Dict[str, Any]:
        """סיכום קטגוריות"""
        try:
            summary = {}
            
            for category, data in category_analysis.items():
                summary[category] = {
                    'avg_return': data.get('avg_return', 0),
                    'etf_count': data.get('etf_count', 0),
                    'positive_count': data.get('positive_returns', 0),
                    'negative_count': data.get('negative_returns', 0),
                    'success_rate': data.get('positive_returns', 0) / data.get('etf_count', 1) * 100
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"שגיאה בסיכום קטגוריות: {str(e)}")
            return {}
    
    def _get_etf_category(self, etf_symbol: str) -> str:
        """קבלת קטגוריית ETF"""
        for category, etfs in self.etf_categories.items():
            if etf_symbol in etfs:
                return category
        return 'unknown'
    
    def _find_high_correlation_pairs(self, correlation_matrix: pd.DataFrame, 
                                    threshold: float = 0.8) -> List[Tuple[str, str, float]]:
        """מציאת זוגות ETFs עם קורלציה גבוהה"""
        try:
            high_corr_pairs = []
            
            for i in range(len(correlation_matrix.columns)):
                for j in range(i + 1, len(correlation_matrix.columns)):
                    col1 = correlation_matrix.columns[i]
                    col2 = correlation_matrix.columns[j]
                    corr_value = correlation_matrix.iloc[i, j]
                    
                    if abs(corr_value) >= threshold:
                        high_corr_pairs.append((col1, col2, corr_value))
            
            return sorted(high_corr_pairs, key=lambda x: abs(x[2]), reverse=True)
            
        except Exception as e:
            logger.error(f"שגיאה במציאת קורלציות גבוהות: {str(e)}")
            return []
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """יצירת תוצאת שגיאה"""
        return {
            'timestamp': datetime.now().isoformat(),
            'agent': self.name,
            'version': self.version,
            'status': 'error',
            'error': error_message,
            'etf_rankings': [],
            'recommendations': ['שגיאה בניתוח']
        }

# דוגמאות שימוש
if __name__ == "__main__":
    # יצירת הסוכן
    agent = ETFFlowTracker()
    
    # יצירת נתונים לדוגמה
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    etf_data = {}
    etfs = ['SPY', 'QQQ', 'XLK', 'XLF', 'XLE']
    
    for etf in etfs:
        etf_data[etf] = pd.DataFrame({
            'Date': dates,
            'Open': np.random.uniform(100, 200, 100),
            'High': np.random.uniform(200, 250, 100),
            'Low': np.random.uniform(50, 100, 100),
            'Close': np.random.uniform(100, 200, 100),
            'Volume': np.random.uniform(1000000, 5000000, 100)
        })
    
    # ניתוח
    result = agent.analyze(etf_data)
    print(f"תוצאות ניתוח ETF: {result}")