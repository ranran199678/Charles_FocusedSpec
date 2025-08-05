"""
Sector Rotation Analyzer - ניתוח רוטציות סקטוריאליות
=======================================================

סוכן המזהה רוטציות בין סקטורים שונים בשוק.
מבוסס על ניתוח ביצועים יחסיים, מומנטום וקורלציות.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from utils.logger import get_agent_logger
from utils.validators import validate_symbol, validate_stock_data

logger = get_agent_logger("SectorRotationAnalyzer")

class SectorRotationAnalyzer:
    """
    סוכן לניתוח רוטציות סקטוריאליות
    """
    
    def __init__(self):
        """אתחול סוכן ניתוח רוטציות סקטוריאליות"""
        self.logger = logger
        self.validator = validate_symbol
        self.data_validator = validate_stock_data
        
        # פרמטרים לניתוח רוטציות
        self.rotation_threshold = 0.05  # 5% שינוי מינימלי
        self.momentum_period = 20  # תקופה לחישוב מומנטום
        self.correlation_threshold = 0.7  # סף קורלציה גבוהה
        self.volatility_period = 30  # תקופה לחישוב תנודתיות
        
        # הגדרת סקטורים
        self.sector_categories = {
            'technology': ['XLK', 'VGT', 'SMH', 'SOXX'],
            'healthcare': ['XLV', 'VHT', 'IHI', 'IBB'],
            'financial': ['XLF', 'VFH', 'KBE', 'KRE'],
            'energy': ['XLE', 'VDE', 'XOP', 'OIH'],
            'consumer_discretionary': ['XLY', 'VCR', 'XRT', 'FDIS'],
            'consumer_staples': ['XLP', 'VDC', 'XLP', 'FSTA'],
            'industrials': ['XLI', 'VIS', 'XAR', 'FIDU'],
            'materials': ['XLB', 'VAW', 'XME', 'FMAT'],
            'utilities': ['XLU', 'VPU', 'XLU', 'FUTY'],
            'real_estate': ['XLRE', 'VNQ', 'IYR', 'FREL']
        }
        
    def analyze(self, sector_data: Dict[str, pd.DataFrame],
                market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        ניתוח רוטציות סקטוריאליות
        
        Args:
            sector_data: מילון עם נתוני סקטורים
            market_data: נתוני השוק הכללי (אופציונלי)
            
        Returns:
            Dict[str, Any]: תוצאות הניתוח
        """
        try:
            self.logger.info("מתחיל ניתוח רוטציות סקטוריאליות")
            
            # אימות נתונים
            if not sector_data:
                return self._create_error_result("אין נתוני סקטורים לניתוח")
            
            # ניתוח רוטציות
            rotation_analysis = self._analyze_sector_rotations(sector_data, market_data)
            momentum_analysis = self._analyze_sector_momentum(sector_data)
            correlation_analysis = self._analyze_sector_correlations(sector_data)
            volatility_analysis = self._analyze_sector_volatility(sector_data)
            performance_analysis = self._analyze_relative_performance(sector_data, market_data)
            
            # חישוב ציון כללי
            overall_score = self._calculate_rotation_score(
                rotation_analysis, momentum_analysis, correlation_analysis,
                volatility_analysis, performance_analysis
            )
            
            # קביעת רמת ביטחון
            confidence_level = self._determine_confidence_level(overall_score)
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(
                rotation_analysis, momentum_analysis, performance_analysis
            )
            
            # חילוץ אותות מפתח
            key_signals = self._extract_key_signals(
                rotation_analysis, momentum_analysis, correlation_analysis,
                volatility_analysis, performance_analysis
            )
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'overall_score': overall_score,
                'confidence_level': confidence_level,
                'recommendations': recommendations,
                'key_signals': key_signals,
                'rotation_analysis': rotation_analysis,
                'momentum_analysis': momentum_analysis,
                'correlation_analysis': correlation_analysis,
                'volatility_analysis': volatility_analysis,
                'performance_analysis': performance_analysis,
                'status': 'success'
            }
            
            self.logger.info(f"ניתוח רוטציות סקטוריאליות הושלם - ציון: {overall_score:.2f}")
            return result
            
        except Exception as e:
            error_msg = f"שגיאה בניתוח רוטציות סקטוריאליות: {str(e)}"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg)
    
    def _analyze_sector_rotations(self, sector_data: Dict[str, pd.DataFrame],
                                 market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח רוטציות בין סקטורים"""
        try:
            rotations = {}
            sector_performances = {}
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is None or len(sector_df) < self.momentum_period:
                    continue
                
                # חישוב ביצועים יחסיים
                sector_returns = sector_df['Close'].pct_change().dropna()
                sector_performances[sector_name] = sector_returns.mean()
                
                # חישוב מומנטום
                recent_performance = sector_returns.tail(self.momentum_period).mean()
                historical_performance = sector_returns.mean()
                
                # זיהוי רוטציה
                rotation_strength = recent_performance - historical_performance
                is_rotating = abs(rotation_strength) > self.rotation_threshold
                
                rotations[sector_name] = {
                    'recent_performance': recent_performance,
                    'historical_performance': historical_performance,
                    'rotation_strength': rotation_strength,
                    'is_rotating': is_rotating,
                    'rotation_direction': 'in' if rotation_strength > 0 else 'out'
                }
            
            # זיהוי סקטורים מובילים ונחשלים
            sorted_sectors = sorted(sector_performances.items(), key=lambda x: x[1], reverse=True)
            leading_sectors = sorted_sectors[:3]
            lagging_sectors = sorted_sectors[-3:]
            
            return {
                'rotations': rotations,
                'leading_sectors': leading_sectors,
                'lagging_sectors': lagging_sectors,
                'rotation_count': sum(1 for r in rotations.values() if r['is_rotating']),
                'score': min(100, len([r for r in rotations.values() if r['is_rotating']]) * 20)
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח רוטציות: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_sector_momentum(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח מומנטום סקטוריאלי"""
        try:
            momentum_data = {}
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is None or len(sector_df) < self.momentum_period:
                    continue
                
                # חישוב RSI
                rsi = self._calculate_rsi(sector_df['Close'])
                current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
                
                # חישוב MACD
                macd_line, signal_line = self._calculate_macd(sector_df['Close'])
                current_macd = macd_line.iloc[-1] if len(macd_line) > 0 else 0
                current_signal = signal_line.iloc[-1] if len(signal_line) > 0 else 0
                
                # חישוב מומנטום
                returns = sector_df['Close'].pct_change().dropna()
                momentum = returns.tail(self.momentum_period).mean()
                
                momentum_data[sector_name] = {
                    'rsi': current_rsi,
                    'macd': current_macd,
                    'macd_signal': current_signal,
                    'momentum': momentum,
                    'momentum_score': min(100, max(0, (momentum + 0.1) * 500))
                }
            
            # חישוב ציון כללי
            avg_momentum_score = np.mean([m['momentum_score'] for m in momentum_data.values()])
            
            return {
                'sector_momentum': momentum_data,
                'average_momentum_score': avg_momentum_score,
                'high_momentum_sectors': [s for s, m in momentum_data.items() if m['momentum_score'] > 70],
                'low_momentum_sectors': [s for s, m in momentum_data.items() if m['momentum_score'] < 30],
                'score': avg_momentum_score
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח מומנטום: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_sector_correlations(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח קורלציות בין סקטורים"""
        try:
            # יצירת DataFrame עם ביצועים של כל הסקטורים
            sector_returns = {}
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is not None and len(sector_df) > 0:
                    returns = sector_df['Close'].pct_change().dropna()
                    sector_returns[sector_name] = returns
            
            if len(sector_returns) < 2:
                return {'score': 0, 'error': 'אין מספיק נתונים לניתוח קורלציות'}
            
            # יצירת correlation matrix
            returns_df = pd.DataFrame(sector_returns)
            correlation_matrix = returns_df.corr()
            
            # זיהוי קורלציות גבוהות
            high_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > self.correlation_threshold:
                        high_correlations.append({
                            'sector1': correlation_matrix.columns[i],
                            'sector2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
            
            # חישוב ציון קורלציה
            avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            correlation_score = min(100, max(0, (1 - abs(avg_correlation)) * 100))
            
            return {
                'correlation_matrix': correlation_matrix,
                'high_correlations': high_correlations,
                'average_correlation': avg_correlation,
                'correlation_score': correlation_score,
                'score': correlation_score
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח קורלציות: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_sector_volatility(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """ניתוח תנודתיות סקטוריאלית"""
        try:
            volatility_data = {}
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is None or len(sector_df) < self.volatility_period:
                    continue
                
                # חישוב תנודתיות
                returns = sector_df['Close'].pct_change().dropna()
                volatility = returns.tail(self.volatility_period).std()
                
                # חישוב תנודתיות יחסית
                avg_volatility = returns.std()
                relative_volatility = volatility / avg_volatility if avg_volatility > 0 else 1
                
                volatility_data[sector_name] = {
                    'volatility': volatility,
                    'relative_volatility': relative_volatility,
                    'volatility_score': min(100, max(0, (1 - relative_volatility) * 100))
                }
            
            # חישוב ציון כללי
            avg_volatility_score = np.mean([v['volatility_score'] for v in volatility_data.values()])
            
            return {
                'sector_volatility': volatility_data,
                'average_volatility_score': avg_volatility_score,
                'high_volatility_sectors': [s for s, v in volatility_data.items() if v['relative_volatility'] > 1.2],
                'low_volatility_sectors': [s for s, v in volatility_data.items() if v['relative_volatility'] < 0.8],
                'score': avg_volatility_score
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח תנודתיות: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _analyze_relative_performance(self, sector_data: Dict[str, pd.DataFrame],
                                    market_data: pd.DataFrame = None) -> Dict[str, Any]:
        """ניתוח ביצועים יחסיים"""
        try:
            relative_performances = {}
            
            # חישוב ביצועי השוק הכללי
            market_performance = 0
            if market_data is not None and len(market_data) > 0:
                market_returns = market_data['Close'].pct_change().dropna()
                market_performance = market_returns.tail(self.momentum_period).mean()
            
            for sector_name, sector_df in sector_data.items():
                if sector_df is None or len(sector_df) < self.momentum_period:
                    continue
                
                # חישוב ביצועים יחסיים
                sector_returns = sector_df['Close'].pct_change().dropna()
                sector_performance = sector_returns.tail(self.momentum_period).mean()
                
                relative_performance = sector_performance - market_performance
                
                relative_performances[sector_name] = {
                    'sector_performance': sector_performance,
                    'market_performance': market_performance,
                    'relative_performance': relative_performance,
                    'outperformance': relative_performance > 0,
                    'performance_score': min(100, max(0, (relative_performance + 0.1) * 500))
                }
            
            # חישוב ציון כללי
            avg_performance_score = np.mean([p['performance_score'] for p in relative_performances.values()])
            
            return {
                'relative_performances': relative_performances,
                'average_performance_score': avg_performance_score,
                'outperforming_sectors': [s for s, p in relative_performances.items() if p['outperformance']],
                'underperforming_sectors': [s for s, p in relative_performances.items() if not p['outperformance']],
                'score': avg_performance_score
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח ביצועים יחסיים: {str(e)}")
            return {'score': 0, 'error': str(e)}
    
    def _calculate_rotation_score(self, rotation_analysis: Dict, momentum_analysis: Dict,
                                 correlation_analysis: Dict, volatility_analysis: Dict,
                                 performance_analysis: Dict) -> float:
        """חישוב ציון רוטציה כללי"""
        try:
            weights = {
                'rotation': 0.25,
                'momentum': 0.20,
                'correlation': 0.15,
                'volatility': 0.15,
                'performance': 0.25
            }
            
            scores = {
                'rotation': rotation_analysis.get('score', 0),
                'momentum': momentum_analysis.get('score', 0),
                'correlation': correlation_analysis.get('score', 0),
                'volatility': volatility_analysis.get('score', 0),
                'performance': performance_analysis.get('score', 0)
            }
            
            weighted_score = sum(scores[key] * weights[key] for key in weights)
            
            # בונוסים נוספים
            bonuses = 0
            
            # בונוס לרוטציות חזקות
            rotation_count = rotation_analysis.get('rotation_count', 0)
            if rotation_count >= 3:
                bonuses += 10
            
            # בונוס לסקטורים מובילים
            leading_sectors = rotation_analysis.get('leading_sectors', [])
            if len(leading_sectors) >= 2:
                bonuses += 5
            
            final_score = min(100, weighted_score + bonuses)
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"שגיאה בחישוב ציון: {str(e)}")
            return 0
    
    def _determine_confidence_level(self, score: float) -> str:
        """קביעת רמת ביטחון"""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _generate_recommendations(self, rotation_analysis: Dict, momentum_analysis: Dict,
                                 performance_analysis: Dict) -> List[str]:
        """יצירת המלצות"""
        recommendations = []
        
        # המלצות על סמך רוטציות
        rotation_count = rotation_analysis.get('rotation_count', 0)
        if rotation_count >= 3:
            recommendations.append("רוטציה חזקה בשוק - הזדמנות למיקום מחדש")
        
        leading_sectors = rotation_analysis.get('leading_sectors', [])
        if leading_sectors:
            sector_names = [s[0] for s in leading_sectors[:2]]
            recommendations.append(f"סקטורים מובילים: {', '.join(sector_names)}")
        
        # המלצות על סמך מומנטום
        high_momentum = momentum_analysis.get('high_momentum_sectors', [])
        if high_momentum:
            recommendations.append(f"סקטורים עם מומנטום גבוה: {', '.join(high_momentum[:3])}")
        
        # המלצות על סמך ביצועים
        outperforming = performance_analysis.get('outperforming_sectors', [])
        if outperforming:
            recommendations.append(f"סקטורים עם ביצועים מעל השוק: {', '.join(outperforming[:3])}")
        
        return recommendations
    
    def _extract_key_signals(self, rotation_analysis: Dict, momentum_analysis: Dict,
                            correlation_analysis: Dict, volatility_analysis: Dict,
                            performance_analysis: Dict) -> List[str]:
        """חילוץ אותות מפתח"""
        signals = []
        
        # אותות רוטציה
        rotation_count = rotation_analysis.get('rotation_count', 0)
        if rotation_count >= 2:
            signals.append(f"זיהוי {rotation_count} רוטציות סקטוריאליות")
        
        # אותות מומנטום
        high_momentum_count = len(momentum_analysis.get('high_momentum_sectors', []))
        if high_momentum_count >= 2:
            signals.append(f"{high_momentum_count} סקטורים עם מומנטום גבוה")
        
        # אותות קורלציה
        high_correlations = correlation_analysis.get('high_correlations', [])
        if len(high_correlations) >= 3:
            signals.append(f"קורלציות גבוהות בין {len(high_correlations)} זוגות סקטורים")
        
        # אותות תנודתיות
        low_volatility_count = len(volatility_analysis.get('low_volatility_sectors', []))
        if low_volatility_count >= 2:
            signals.append(f"{low_volatility_count} סקטורים עם תנודתיות נמוכה")
        
        # אותות ביצועים
        outperforming_count = len(performance_analysis.get('outperforming_sectors', []))
        if outperforming_count >= 3:
            signals.append(f"{outperforming_count} סקטורים עם ביצועים מעל השוק")
        
        return signals
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """יצירת תוצאת שגיאה"""
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0,
            'confidence_level': 'Very Low',
            'recommendations': ['לא ניתן לנתח - שגיאה בנתונים'],
            'key_signals': [],
            'error': error_message,
            'status': 'error'
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """חישוב RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """חישוב MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        return macd_line, signal_line

# פונקציות עזר
def analyze_sector_rotations(sector_data: Dict[str, pd.DataFrame],
                           market_data: pd.DataFrame = None) -> Dict[str, Any]:
    """
    ניתוח רוטציות סקטוריאליות
    
    Args:
        sector_data: מילון עם נתוני סקטורים
        market_data: נתוני השוק הכללי (אופציונלי)
        
    Returns:
        Dict[str, Any]: תוצאות הניתוח
    """
    analyzer = SectorRotationAnalyzer()
    return analyzer.analyze(sector_data, market_data)

def get_rotation_recommendations(analysis_result: Dict[str, Any]) -> List[str]:
    """
    קבלת המלצות רוטציה
    
    Args:
        analysis_result: תוצאת הניתוח
        
    Returns:
        List[str]: רשימת המלצות
    """
    return analysis_result.get('recommendations', [])

def get_leading_sectors(analysis_result: Dict[str, Any]) -> List[str]:
    """
    קבלת הסקטורים המובילים
    
    Args:
        analysis_result: תוצאת הניתוח
        
    Returns:
        List[str]: רשימת הסקטורים המובילים
    """
    rotation_analysis = analysis_result.get('rotation_analysis', {})
    leading_sectors = rotation_analysis.get('leading_sectors', [])
    return [sector[0] for sector in leading_sectors]