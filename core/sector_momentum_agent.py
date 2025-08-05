"""
Sector Momentum Agent - ניתוח מגמות סקטוריאליות
===============================================

סוכן המנתח מגמות סקטוריאליות ומזהה סקטורים עם מומנטום חיובי או שלילי.
מבוסס על ניתוח ביצועים יחסיים של סקטורים שונים.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("SectorMomentumAgent")

class SectorMomentumAgent:
    """
    סוכן לניתוח מגמות סקטוריאליות
    
    מנתח ביצועים של סקטורים שונים ומזהה:
    - סקטורים עם מומנטום חיובי
    - סקטורים עם מומנטום שלילי
    - רוטציות בין סקטורים
    - מגמות ארוכות טווח
    """
    
    def __init__(self):
        """אתחול הסוכן"""
        self.name = "SectorMomentumAgent"
        self.description = "ניתוח מגמות סקטוריאליות"
        self.version = "1.0.0"
        
        # הגדרת סקטורים עיקריים
        self.sectors = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT'],
            'financial': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO'],
            'consumer_discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW'],
            'consumer_staples': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'PM', 'MO'],
            'industrials': ['BA', 'CAT', 'MMM', 'GE', 'HON', 'UPS', 'FDX'],
            'materials': ['LIN', 'APD', 'FCX', 'NEM', 'DOW', 'DD', 'NUE'],
            'utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'XEL', 'SRE'],
            'real_estate': ['PLD', 'AMT', 'CCI', 'EQIX', 'DLR', 'PSA', 'O']
        }
        
        # פרמטרים לניתוח
        self.lookback_periods = {
            'short': 5,
            'medium': 20,
            'long': 60
        }
        
        self.momentum_threshold = 0.02  # 2% שינוי למומנטום משמעותי
        # relative_strength_threshold calculation moved to RelativeStrengthAgent
        self.relative_strength_threshold = 0.05  # 5% ביצועים יחסיים (placeholder)
        
        logger.info(f"אתחול {self.name} v{self.version}")
    
    def analyze(self, sector_data: Dict[str, pd.DataFrame], 
                market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח מגמות סקטוריאליות
        
        Args:
            sector_data: מילון עם נתוני סקטורים (סקטור -> DataFrame)
            market_data: נתוני השוק הכללי (אופציונלי)
            
        Returns:
            Dict[str, Any]: תוצאות הניתוח
        """
        try:
            logger.info("התחלת ניתוח מגמות סקטוריאליות")
            
            # אימות נתונים
            if not sector_data:
                return self._create_error_result("אין נתוני סקטורים")
            
            # ניתוח ביצועים יחסיים
            relative_performance = self._analyze_relative_performance(sector_data, market_data)
            
            # ניתוח מומנטום
            momentum_analysis = self._analyze_momentum(sector_data)
            
            # ניתוח תנודתיות
            volatility_analysis = self._analyze_volatility(sector_data)
            
            # ניתוח קורלציות
            correlation_analysis = self._analyze_correlations(sector_data)
            
            # זיהוי רוטציות
            rotation_analysis = self._analyze_sector_rotation(sector_data)
            
            # חישוב ציונים
            sector_scores = self._calculate_sector_scores(
                relative_performance, momentum_analysis, volatility_analysis
            )
            
            # דירוג סקטורים
            sector_rankings = self._rank_sectors(sector_scores)
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(sector_rankings, rotation_analysis)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'agent': self.name,
                'version': self.version,
                'sector_rankings': sector_rankings,
                'recommendations': recommendations,
                'analysis': {
                    'relative_performance': relative_performance,
                    'momentum_analysis': momentum_analysis,
                    'volatility_analysis': volatility_analysis,
                    'correlation_analysis': correlation_analysis,
                    'rotation_analysis': rotation_analysis
                },
                'sector_scores': sector_scores,
                'top_performers': self._get_top_performers(sector_rankings, 3),
                'bottom_performers': self._get_bottom_performers(sector_rankings, 3),
                'status': 'success'
            }
            
            logger.info("ניתוח מגמות סקטוריאליות הושלם")
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח מגמות סקטוריאליות: {str(e)}")
            return self._create_error_result(f"שגיאה בניתוח: {str(e)}")
    
    def _analyze_relative_performance(self, sector_data: Dict[str, pd.DataFrame], 
                                     market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח ביצועים יחסיים של סקטורים"""
        try:
            relative_performance = {}
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is None or sector_df.empty:
                    continue
                
                # חישוב תשואות
                sector_df = sector_df.copy()
                sector_df['returns'] = sector_df['Close'].pct_change()
                
                # תשואות לתקופות שונות
                returns_5d = sector_df['returns'].tail(5).sum()
                returns_20d = sector_df['returns'].tail(20).sum()
                returns_60d = sector_df['returns'].tail(60).sum()
                
                # השוואה לשוק אם קיים
                if market_data is not None and not market_data.empty:
                    market_df = market_data.copy()
                    market_df['returns'] = market_df['Close'].pct_change()
                    
                    market_5d = market_df['returns'].tail(5).sum()
                    market_20d = market_df['returns'].tail(20).sum()
                    market_60d = market_df['returns'].tail(60).sum()
                    
                    relative_5d = returns_5d - market_5d
                    relative_20d = returns_20d - market_20d
                    relative_60d = returns_60d - market_60d
                else:
                    relative_5d = returns_5d
                    relative_20d = returns_20d
                    relative_60d = returns_60d
                
                relative_performance[sector_name] = {
                    'returns_5d': returns_5d,
                    'returns_20d': returns_20d,
                    'returns_60d': returns_60d,
                    'relative_5d': relative_5d,
                    'relative_20d': relative_20d,
                    'relative_60d': relative_60d,
                    'avg_relative': (relative_5d + relative_20d + relative_60d) / 3
                }
            
            return relative_performance
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח ביצועים יחסיים: {str(e)}")
            return {}
    
    def _analyze_momentum(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח מומנטום סקטוריאלי"""
        try:
            momentum_analysis = {}
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is None or sector_df.empty:
                    continue
                
                sector_df = sector_df.copy()
                
                # חישוב אינדיקטורי מומנטום
                sector_df['sma_20'] = sector_df['Close'].rolling(window=20).mean()
                sector_df['sma_50'] = sector_df['Close'].rolling(window=50).mean()
                sector_df['rsi'] = self._calculate_rsi(sector_df['Close'], 14)
                
                # זיהוי מומנטום
                current_price = sector_df['Close'].iloc[-1]
                sma_20 = sector_df['sma_20'].iloc[-1]
                sma_50 = sector_df['sma_50'].iloc[-1]
                rsi = sector_df['rsi'].iloc[-1]
                
                # חישוב ציוני מומנטום
                price_momentum = (current_price - sma_20) / sma_20
                trend_momentum = (sma_20 - sma_50) / sma_50
                rsi_momentum = (rsi - 50) / 50  # נרמול RSI
                
                # ציון מומנטום כללי
                overall_momentum = (price_momentum + trend_momentum + rsi_momentum) / 3
                
                momentum_analysis[sector_name] = {
                    'price_momentum': price_momentum,
                    'trend_momentum': trend_momentum,
                    'rsi_momentum': rsi_momentum,
                    'overall_momentum': overall_momentum,
                    'current_rsi': rsi,
                    'above_sma_20': current_price > sma_20,
                    'above_sma_50': current_price > sma_50
                }
            
            return momentum_analysis
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח מומנטום: {str(e)}")
            return {}
    
    def _analyze_volatility(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח תנודתיות סקטוריאלית"""
        try:
            volatility_analysis = {}
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is None or sector_df.empty:
                    continue
                
                sector_df = sector_df.copy()
                sector_df['returns'] = sector_df['Close'].pct_change()
                
                # חישוב תנודתיות
                volatility_20d = sector_df['returns'].tail(20).std() * np.sqrt(252)  # שנתי
                volatility_60d = sector_df['returns'].tail(60).std() * np.sqrt(252)
                
                # השוואה לתנודתיות היסטורית
                historical_vol = sector_df['returns'].std() * np.sqrt(252)
                vol_ratio = volatility_20d / historical_vol if historical_vol > 0 else 1
                
                volatility_analysis[sector_name] = {
                    'volatility_20d': volatility_20d,
                    'volatility_60d': volatility_60d,
                    'historical_volatility': historical_vol,
                    'volatility_ratio': vol_ratio,
                    'is_high_volatility': vol_ratio > 1.2,
                    'is_low_volatility': vol_ratio < 0.8
                }
            
            return volatility_analysis
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח תנודתיות: {str(e)}")
            return {}
    
    def _analyze_correlations(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח קורלציות בין סקטורים"""
        try:
            # יצירת DataFrame עם תשואות כל הסקטורים
            returns_data = {}
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is not None and not sector_df.empty:
                    sector_df = sector_df.copy()
                    sector_df['returns'] = sector_df['Close'].pct_change()
                    returns_data[sector_name] = sector_df['returns']
            
            if len(returns_data) < 2:
                return {}
            
            # יצירת DataFrame קורלציות
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            
            # חישוב קורלציות ממוצעות
            avg_correlations = {}
            for sector in returns_data.keys():
                correlations = correlation_matrix[sector].drop(sector)
                avg_correlations[sector] = correlations.mean()
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'average_correlations': avg_correlations,
                'high_correlation_pairs': self._find_high_correlation_pairs(correlation_matrix)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח קורלציות: {str(e)}")
            return {}
    
    def _analyze_sector_rotation(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח רוטציות בין סקטורים"""
        try:
            rotation_analysis = {}
            
            # חישוב ביצועים יחסיים לתקופות שונות
            performance_5d = {}
            performance_20d = {}
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is not None and not sector_df.empty:
                    sector_df = sector_df.copy()
                    sector_df['returns'] = sector_df['Close'].pct_change()
                    
                    performance_5d[sector_name] = sector_df['returns'].tail(5).sum()
                    performance_20d[sector_name] = sector_df['returns'].tail(20).sum()
            
            # דירוג ביצועים
            ranked_5d = sorted(performance_5d.items(), key=lambda x: x[1], reverse=True)
            ranked_20d = sorted(performance_20d.items(), key=lambda x: x[1], reverse=True)
            
            # זיהוי שינויים בדירוג
            rotation_changes = {}
            for sector in performance_5d.keys():
                if sector in performance_20d:
                    rank_5d = next(i for i, (s, _) in enumerate(ranked_5d) if s == sector)
                    rank_20d = next(i for i, (s, _) in enumerate(ranked_20d) if s == sector)
                    rank_change = rank_20d - rank_5d
                    
                    rotation_changes[sector] = {
                        'rank_change': rank_change,
                        'rank_5d': rank_5d,
                        'rank_20d': rank_20d,
                        'is_improving': rank_change > 0,
                        'is_declining': rank_change < 0
                    }
            
            rotation_analysis = {
                'top_performers_5d': ranked_5d[:3],
                'top_performers_20d': ranked_20d[:3],
                'rotation_changes': rotation_changes,
                'improving_sectors': [s for s, data in rotation_changes.items() if data['is_improving']],
                'declining_sectors': [s for s, data in rotation_changes.items() if data['is_declining']]
            }
            
            return rotation_analysis
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח רוטציות: {str(e)}")
            return {}
    
    def _calculate_sector_scores(self, relative_performance: Dict, 
                                momentum_analysis: Dict, 
                                volatility_analysis: Dict) -> Dict[str, float]:
        """חישוב ציונים כללים לסקטורים"""
        try:
            sector_scores = {}
            
            for sector in relative_performance.keys():
                score = 0.0
                weight_count = 0
                
                # ציון מביצועים יחסיים (40%)
                if sector in relative_performance:
                    rel_perf = relative_performance[sector]
                    perf_score = rel_perf.get('avg_relative', 0) * 100
                    score += perf_score * 0.4
                    weight_count += 0.4
                
                # ציון ממומנטום (35%)
                if sector in momentum_analysis:
                    momentum = momentum_analysis[sector]
                    mom_score = momentum.get('overall_momentum', 0) * 100
                    score += mom_score * 0.35
                    weight_count += 0.35
                
                # ציון מתנודתיות (25%)
                if sector in volatility_analysis:
                    vol = volatility_analysis[sector]
                    vol_ratio = vol.get('volatility_ratio', 1)
                    # תנודתיות נמוכה = ציון גבוה
                    vol_score = max(0, 100 - (vol_ratio - 1) * 50)
                    score += vol_score * 0.25
                    weight_count += 0.25
                
                # נרמול לפי משקלים
                if weight_count > 0:
                    sector_scores[sector] = score / weight_count
                else:
                    sector_scores[sector] = 0.0
            
            return sector_scores
            
        except Exception as e:
            logger.error(f"שגיאה בחישוב ציוני סקטורים: {str(e)}")
            return {}
    
    def _rank_sectors(self, sector_scores: Dict[str, float]) -> List[Tuple[str, float]]:
        """דירוג סקטורים לפי ציונים"""
        try:
            ranked_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
            return ranked_sectors
        except Exception as e:
            logger.error(f"שגיאה בדירוג סקטורים: {str(e)}")
            return []
    
    def _generate_recommendations(self, sector_rankings: List[Tuple[str, float]], 
                                 rotation_analysis: Dict) -> List[str]:
        """יצירת המלצות"""
        try:
            recommendations = []
            
            if not sector_rankings:
                return ["אין מספיק נתונים להמלצות"]
            
            # המלצות על סקטורים מובילים
            top_sectors = sector_rankings[:3]
            recommendations.append(f"סקטורים מובילים: {', '.join([s[0] for s in top_sectors])}")
            
            # המלצות על סקטורים משתפרים
            improving = rotation_analysis.get('improving_sectors', [])
            if improving:
                recommendations.append(f"סקטורים משתפרים: {', '.join(improving)}")
            
            # המלצות על סקטורים יורדים
            declining = rotation_analysis.get('declining_sectors', [])
            if declining:
                recommendations.append(f"סקטורים יורדים: {', '.join(declining)}")
            
            # המלצות כלליות
            if len(sector_rankings) >= 2:
                top_score = sector_rankings[0][1]
                bottom_score = sector_rankings[-1][1]
                score_spread = top_score - bottom_score
                
                if score_spread > 20:
                    recommendations.append("פיזור גבוה בין סקטורים - הזדמנות לרוטציה")
                elif score_spread < 5:
                    recommendations.append("פיזור נמוך בין סקטורים - שוק מאוזן")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"שגיאה ביצירת המלצות: {str(e)}")
            return ["שגיאה ביצירת המלצות"]
    
    def _get_top_performers(self, sector_rankings: List[Tuple[str, float]], count: int) -> List[Dict]:
        """קבלת הסקטורים המובילים"""
        try:
            top_performers = []
            for i, (sector, score) in enumerate(sector_rankings[:count]):
                top_performers.append({
                    'rank': i + 1,
                    'sector': sector,
                    'score': score
                })
            return top_performers
        except Exception as e:
            logger.error(f"שגיאה בקבלת מובילים: {str(e)}")
            return []
    
    def _get_bottom_performers(self, sector_rankings: List[Tuple[str, float]], count: int) -> List[Dict]:
        """קבלת הסקטורים הגרועים"""
        try:
            bottom_performers = []
            for i, (sector, score) in enumerate(sector_rankings[-count:]):
                bottom_performers.append({
                    'rank': len(sector_rankings) - count + i + 1,
                    'sector': sector,
                    'score': score
                })
            return bottom_performers
        except Exception as e:
            logger.error(f"שגיאה בקבלת גרועים: {str(e)}")
            return []
    
    def _find_high_correlation_pairs(self, correlation_matrix: pd.DataFrame, 
                                    threshold: float = 0.8) -> List[Tuple[str, str, float]]:
        """מציאת זוגות סקטורים עם קורלציה גבוהה"""
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
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """חישוב RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """יצירת תוצאת שגיאה"""
        return {
            'timestamp': datetime.now().isoformat(),
            'agent': self.name,
            'version': self.version,
            'status': 'error',
            'error': error_message,
            'sector_rankings': [],
            'recommendations': ['שגיאה בניתוח']
        }

# דוגמאות שימוש
if __name__ == "__main__":
    # יצירת הסוכן
    agent = SectorMomentumAgent()
    
    # יצירת נתונים לדוגמה
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    sector_data = {}
    sectors = ['technology', 'healthcare', 'financial', 'energy']
    
    for sector in sectors:
        sector_data[sector] = pd.DataFrame({
            'Date': dates,
            'Open': np.random.uniform(100, 200, 100),
            'High': np.random.uniform(200, 250, 100),
            'Low': np.random.uniform(50, 100, 100),
            'Close': np.random.uniform(100, 200, 100),
            'Volume': np.random.uniform(1000000, 5000000, 100)
        })
    
    # ניתוח
    result = agent.analyze(sector_data)
    print(f"תוצאות ניתוח סקטוריאלי: {result}")