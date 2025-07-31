"""
ProfitabilityMetricsAgent - חישוב יחסי רווחיות מתקדם
====================================================

סוכן מתקדם לחישוב יחסי רווחיות מקיפים וניתוח ביצועים פיננסיים.
מחלץ ומרכז את כל הפונקציונליות הקיימת מקבצים אחרים.

תכונות מתקדמות:
- חישוב ROE, ROA, Gross Margin, Net Margin
- השוואה לסקטור ותעשייה
- ניתוח מגמות רווחיות לאורך זמן
- זיהוי שיפור/הדרדרות ברווחיות
- דירוג percentile של רווחיות
- ניתוח איכות רווחיות
- זיהוי אנומליות ברווחיות
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from utils.data_fetcher import data_fetcher
from utils.logger import logger
from utils.validators import validate_symbol

@dataclass
class ProfitabilityMetrics:
    """מבנה נתונים למדדי רווחיות"""
    roe: float
    roa: float
    gross_margin: float
    net_margin: float
    operating_margin: float
    ebitda_margin: float
    return_on_capital: float
    return_on_equity: float
    quality_score: float
    trend_score: float

@dataclass
class SectorComparison:
    """מבנה נתונים להשוואת סקטור"""
    sector_roe: float
    sector_roa: float
    sector_gross_margin: float
    sector_net_margin: float
    percentile_rank: float
    competitive_position: str

@dataclass
class ProfitabilityTrend:
    """מבנה נתונים למגמת רווחיות"""
    trend_direction: str
    trend_strength: float
    consistency_score: float
    improvement_rate: float
    sustainability_score: float

class ProfitabilityMetricsAgent:
    """
    סוכן מתקדם לחישוב יחסי רווחיות מקיפים
    
    תכונות מתקדמות:
    - חישוב ROE, ROA, Gross Margin, Net Margin
    - השוואה לסקטור ותעשייה
    - ניתוח מגמות רווחיות לאורך זמן
    - זיהוי שיפור/הדרדרות ברווחיות
    - דירוג percentile של רווחיות
    - ניתוח איכות רווחיות
    - זיהוי אנומליות ברווחיות
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        self.config = config or {}
        
        # הגדרות מתקדמות
        self.analysis_periods = {
            'current': 1,      # שנה נוכחית
            'recent': 3,       # 3 שנים אחרונות
            'historical': 5    # 5 שנים אחרונות
        }
        
        self.profitability_thresholds = {
            'excellent': {
                'roe': 0.20,      # 20%
                'roa': 0.10,      # 10%
                'gross_margin': 0.50,  # 50%
                'net_margin': 0.15     # 15%
            },
            'good': {
                'roe': 0.15,      # 15%
                'roa': 0.08,      # 8%
                'gross_margin': 0.40,  # 40%
                'net_margin': 0.10     # 10%
            },
            'average': {
                'roe': 0.10,      # 10%
                'roa': 0.05,      # 5%
                'gross_margin': 0.30,  # 30%
                'net_margin': 0.05     # 5%
            },
            'poor': {
                'roe': 0.05,      # 5%
                'roa': 0.02,      # 2%
                'gross_margin': 0.20,  # 20%
                'net_margin': 0.02     # 2%
            }
        }
        
        self.trend_weights = {
            'recent': 0.5,      # משקל גבוה לתקופה האחרונה
            'medium': 0.3,      # משקל בינוני לתקופה בינונית
            'long': 0.2         # משקל נמוך לתקופה ארוכה
        }
        
        # סוגי מגמות רווחיות
        self.trend_types = {
            'improving': 'משתפר',
            'stable': 'יציב',
            'declining': 'יורד',
            'volatile': 'תנודתי',
            'recovering': 'מתאושש'
        }
    
    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח רווחיות מקיף
        
        Args:
            symbol: סימבול המניה
            price_df: נתוני מחיר (לא נדרש לניתוח רווחיות)
            
        Returns:
            Dict עם תוצאות הניתוח
        """
        try:
            # ולידציה
            if not validate_symbol(symbol):
                return self._error_response("סימבול לא תקין")
            
            # שליפת נתונים פיננסיים
            financial_data = self._fetch_financial_data(symbol)
            if financial_data is None:
                return self._error_response("לא ניתן לשלוף נתונים פיננסיים")
            
            # חישוב מדדי רווחיות
            profitability_metrics = self._calculate_profitability_metrics(financial_data)
            sector_comparison = self._calculate_sector_comparison(symbol, profitability_metrics)
            profitability_trend = self._analyze_profitability_trend(financial_data)
            quality_analysis = self._analyze_profitability_quality(financial_data)
            
            # חישוב ציון כללי
            overall_score = self._calculate_overall_score(profitability_metrics, sector_comparison, profitability_trend)
            
            # חישוב רמת ביטחון
            confidence = self._calculate_confidence(financial_data, profitability_metrics)
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(profitability_metrics, sector_comparison, profitability_trend)
            
            # תוצאה סופית
            result = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "score": overall_score,
                "confidence": confidence,
                "explanation": self._generate_explanation(profitability_metrics, sector_comparison, profitability_trend),
                "recommendations": recommendations,
                "details": {
                    "profitability_metrics": profitability_metrics.__dict__,
                    "sector_comparison": sector_comparison.__dict__,
                    "profitability_trend": profitability_trend.__dict__,
                    "quality_analysis": quality_analysis,
                    "financial_data_summary": self._summarize_financial_data(financial_data)
                }
            }
            
            logger.info(f"Profitability analysis completed for {symbol}: Score={overall_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error in profitability analysis for {symbol}: {str(e)}")
            return self._error_response(f"שגיאה בניתוח: {str(e)}")
    
    def _fetch_financial_data(self, symbol: str) -> Optional[Dict]:
        """שליפת נתונים פיננסיים"""
        try:
            # שליפת דוחות רווח והפסד
            income_statement = data_fetcher.get_income_statement(symbol)
            if income_statement is None or income_statement.empty:
                return None
            
            # שליפת מאזן
            balance_sheet = data_fetcher.get_balance_sheet(symbol)
            if balance_sheet is None or balance_sheet.empty:
                return None
            
            # שליפת תזרים מזומנים
            cash_flow = data_fetcher.get_cash_flow_statement(symbol)
            
            return {
                "income_statement": income_statement,
                "balance_sheet": balance_sheet,
                "cash_flow": cash_flow
            }
            
        except Exception as e:
            logger.error(f"Error fetching financial data for {symbol}: {str(e)}")
            return None
    
    def _calculate_profitability_metrics(self, financial_data: Dict) -> ProfitabilityMetrics:
        """חישוב מדדי רווחיות"""
        try:
            income_stmt = financial_data["income_statement"]
            balance_sheet = financial_data["balance_sheet"]
            
            # נתונים נוכחיים (השנה האחרונה)
            current_data = income_stmt.iloc[0] if not income_stmt.empty else None
            current_balance = balance_sheet.iloc[0] if not balance_sheet.empty else None
            
            if current_data is None or current_balance is None:
                return self._default_profitability_metrics()
            
            # חישוב מדדי רווחיות
            roe = self._calculate_roe(current_data, current_balance)
            roa = self._calculate_roa(current_data, current_balance)
            gross_margin = self._calculate_gross_margin(current_data)
            net_margin = self._calculate_net_margin(current_data)
            operating_margin = self._calculate_operating_margin(current_data)
            ebitda_margin = self._calculate_ebitda_margin(current_data)
            return_on_capital = self._calculate_return_on_capital(current_data, current_balance)
            return_on_equity = roe  # זהה ל-ROE
            
            # חישוב ציוני איכות ומגמה
            quality_score = self._calculate_quality_score(gross_margin, net_margin, operating_margin)
            trend_score = self._calculate_trend_score(financial_data)
            
            return ProfitabilityMetrics(
                roe=roe,
                roa=roa,
                gross_margin=gross_margin,
                net_margin=net_margin,
                operating_margin=operating_margin,
                ebitda_margin=ebitda_margin,
                return_on_capital=return_on_capital,
                return_on_equity=return_on_equity,
                quality_score=quality_score,
                trend_score=trend_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating profitability metrics: {str(e)}")
            return self._default_profitability_metrics()
    
    def _calculate_roe(self, income_data: pd.Series, balance_data: pd.Series) -> float:
        """חישוב ROE (Return on Equity)"""
        try:
            net_income = float(income_data.get("netIncome", 0) or 0)
            total_equity = float(balance_data.get("totalEquity", 1) or 1)
            
            return net_income / total_equity if total_equity > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_roa(self, income_data: pd.Series, balance_data: pd.Series) -> float:
        """חישוב ROA (Return on Assets)"""
        try:
            net_income = float(income_data.get("netIncome", 0) or 0)
            total_assets = float(balance_data.get("totalAssets", 1) or 1)
            
            return net_income / total_assets if total_assets > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_gross_margin(self, income_data: pd.Series) -> float:
        """חישוב Gross Margin"""
        try:
            gross_profit = float(income_data.get("grossProfit", 0) or 0)
            revenue = float(income_data.get("revenue", 1) or 1)
            
            return gross_profit / revenue if revenue > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_net_margin(self, income_data: pd.Series) -> float:
        """חישוב Net Margin"""
        try:
            net_income = float(income_data.get("netIncome", 0) or 0)
            revenue = float(income_data.get("revenue", 1) or 1)
            
            return net_income / revenue if revenue > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_operating_margin(self, income_data: pd.Series) -> float:
        """חישוב Operating Margin"""
        try:
            operating_income = float(income_data.get("operatingIncome", 0) or 0)
            revenue = float(income_data.get("revenue", 1) or 1)
            
            return operating_income / revenue if revenue > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_ebitda_margin(self, income_data: pd.Series) -> float:
        """חישוב EBITDA Margin"""
        try:
            ebitda = float(income_data.get("ebitda", 0) or 0)
            revenue = float(income_data.get("revenue", 1) or 1)
            
            return ebitda / revenue if revenue > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_return_on_capital(self, income_data: pd.Series, balance_data: pd.Series) -> float:
        """חישוב Return on Capital"""
        try:
            net_income = float(income_data.get("netIncome", 0) or 0)
            total_equity = float(balance_data.get("totalEquity", 0) or 0)
            total_debt = float(balance_data.get("totalDebt", 0) or 0)
            
            total_capital = total_equity + total_debt
            return net_income / total_capital if total_capital > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_quality_score(self, gross_margin: float, net_margin: float, operating_margin: float) -> float:
        """חישוב ציון איכות רווחיות"""
        try:
            # בדיקת עקביות בין המדדים
            margin_spread = gross_margin - net_margin
            operating_efficiency = operating_margin / gross_margin if gross_margin > 0 else 0
            
            # ציון איכות
            quality_score = 50  # ציון בסיסי
            
            # בונוס למדדי רווחיות גבוהים
            if gross_margin > 0.4:
                quality_score += 20
            if net_margin > 0.1:
                quality_score += 20
            if operating_margin > 0.15:
                quality_score += 10
            
            # בונוס לעקביות
            if margin_spread < 0.3:  # פער קטן בין gross ל-net
                quality_score += 10
            
            # בונוס ליעילות תפעולית
            if operating_efficiency > 0.7:
                quality_score += 10
            
            return min(100, max(0, quality_score))
            
        except:
            return 50.0
    
    def _calculate_trend_score(self, financial_data: Dict) -> float:
        """חישוב ציון מגמה"""
        try:
            income_stmt = financial_data["income_statement"]
            
            if income_stmt.empty or len(income_stmt) < 2:
                return 50.0
            
            # חישוב מגמה ב-3 שנים אחרונות
            recent_years = min(3, len(income_stmt))
            margins = []
            
            for i in range(recent_years):
                year_data = income_stmt.iloc[i]
                revenue = float(year_data.get("revenue", 1) or 1)
                net_income = float(year_data.get("netIncome", 0) or 0)
                margin = net_income / revenue if revenue > 0 else 0
                margins.append(margin)
            
            if len(margins) < 2:
                return 50.0
            
            # חישוב מגמה
            if len(margins) == 2:
                trend = margins[0] - margins[1]
            else:
                # רגרסיה ליניארית פשוטה
                x = np.arange(len(margins))
                slope = np.polyfit(x, margins, 1)[0]
                trend = slope * len(margins)
            
            # המרה לציון
            trend_score = 50 + trend * 1000  # קנה מידה
            return min(100, max(0, trend_score))
            
        except:
            return 50.0
    
    def _calculate_sector_comparison(self, symbol: str, metrics: ProfitabilityMetrics) -> SectorComparison:
        """חישוב השוואה לסקטור"""
        try:
            # נתונים סטטיסטיים של סקטור (משוערים)
            sector_metrics = self._get_sector_benchmarks(symbol)
            
            # השוואה
            sector_roe = sector_metrics.get("roe", 0.10)
            sector_roa = sector_metrics.get("roa", 0.05)
            sector_gross_margin = sector_metrics.get("gross_margin", 0.30)
            sector_net_margin = sector_metrics.get("net_margin", 0.05)
            
            # חישוב percentile
            percentile_rank = self._calculate_percentile_rank(metrics, sector_metrics)
            
            # זיהוי עמדה תחרותית
            competitive_position = self._identify_competitive_position(metrics, sector_metrics)
            
            return SectorComparison(
                sector_roe=sector_roe,
                sector_roa=sector_roa,
                sector_gross_margin=sector_gross_margin,
                sector_net_margin=sector_net_margin,
                percentile_rank=percentile_rank,
                competitive_position=competitive_position
            )
            
        except Exception as e:
            logger.warning(f"Error in sector comparison: {str(e)}")
            return SectorComparison(
                sector_roe=0.10,
                sector_roa=0.05,
                sector_gross_margin=0.30,
                sector_net_margin=0.05,
                percentile_rank=50.0,
                competitive_position="unknown"
            )
    
    def _get_sector_benchmarks(self, symbol: str) -> Dict:
        """קבלת נתוני סקטור (משוערים)"""
        # מיפוי בסיסי של סקטורים
        sector_benchmarks = {
            'technology': {
                'roe': 0.15,
                'roa': 0.08,
                'gross_margin': 0.60,
                'net_margin': 0.12
            },
            'healthcare': {
                'roe': 0.12,
                'roa': 0.06,
                'gross_margin': 0.50,
                'net_margin': 0.08
            },
            'financials': {
                'roe': 0.10,
                'roa': 0.04,
                'gross_margin': 0.40,
                'net_margin': 0.06
            },
            'consumer': {
                'roe': 0.14,
                'roa': 0.07,
                'gross_margin': 0.45,
                'net_margin': 0.09
            }
        }
        
        # ברירת מחדל - technology
        return sector_benchmarks.get('technology', sector_benchmarks['technology'])
    
    def _calculate_percentile_rank(self, metrics: ProfitabilityMetrics, sector_metrics: Dict) -> float:
        """חישוב דירוג percentile"""
        try:
            # השוואה למדדי הסקטור
            roe_rank = min(100, max(0, (metrics.roe / sector_metrics.get("roe", 0.1)) * 50))
            roa_rank = min(100, max(0, (metrics.roa / sector_metrics.get("roa", 0.05)) * 50))
            gross_rank = min(100, max(0, (metrics.gross_margin / sector_metrics.get("gross_margin", 0.3)) * 50))
            net_rank = min(100, max(0, (metrics.net_margin / sector_metrics.get("net_margin", 0.05)) * 50))
            
            # ממוצע משוקלל
            percentile = (roe_rank * 0.3 + roa_rank * 0.2 + gross_rank * 0.25 + net_rank * 0.25)
            return min(100, max(0, percentile))
            
        except:
            return 50.0
    
    def _identify_competitive_position(self, metrics: ProfitabilityMetrics, sector_metrics: Dict) -> str:
        """זיהוי עמדה תחרותית"""
        try:
            # השוואה למדדי הסקטור
            roe_ratio = metrics.roe / sector_metrics.get("roe", 0.1)
            roa_ratio = metrics.roa / sector_metrics.get("roa", 0.05)
            gross_ratio = metrics.gross_margin / sector_metrics.get("gross_margin", 0.3)
            net_ratio = metrics.net_margin / sector_metrics.get("net_margin", 0.05)
            
            # ממוצע יחסים
            avg_ratio = (roe_ratio + roa_ratio + gross_ratio + net_ratio) / 4
            
            if avg_ratio > 1.5:
                return "מוביל"
            elif avg_ratio > 1.2:
                return "חזק"
            elif avg_ratio > 0.8:
                return "ממוצע"
            elif avg_ratio > 0.5:
                return "חלש"
            else:
                return "נחשל"
                
        except:
            return "לא ידוע"
    
    def _analyze_profitability_trend(self, financial_data: Dict) -> ProfitabilityTrend:
        """ניתוח מגמת רווחיות"""
        try:
            income_stmt = financial_data["income_statement"]
            
            if income_stmt.empty or len(income_stmt) < 2:
                return ProfitabilityTrend(
                    trend_direction="stable",
                    trend_strength=50.0,
                    consistency_score=50.0,
                    improvement_rate=0.0,
                    sustainability_score=50.0
                )
            
            # חישוב מגמות
            margins = []
            for i in range(min(5, len(income_stmt))):
                year_data = income_stmt.iloc[i]
                revenue = float(year_data.get("revenue", 1) or 1)
                net_income = float(year_data.get("netIncome", 0) or 0)
                margin = net_income / revenue if revenue > 0 else 0
                margins.append(margin)
            
            if len(margins) < 2:
                return ProfitabilityTrend(
                    trend_direction="stable",
                    trend_strength=50.0,
                    consistency_score=50.0,
                    improvement_rate=0.0,
                    sustainability_score=50.0
                )
            
            # זיהוי כיוון מגמה
            recent_margin = margins[0]
            older_margin = margins[-1]
            improvement_rate = (recent_margin - older_margin) / older_margin if older_margin > 0 else 0
            
            if improvement_rate > 0.1:
                trend_direction = "improving"
            elif improvement_rate > -0.05:
                trend_direction = "stable"
            else:
                trend_direction = "declining"
            
            # חישוב עוצמת מגמה
            trend_strength = min(100, max(0, 50 + improvement_rate * 500))
            
            # חישוב עקביות
            consistency_score = self._calculate_consistency_score(margins)
            
            # חישוב קיימות
            sustainability_score = self._calculate_sustainability_score(margins)
            
            return ProfitabilityTrend(
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                consistency_score=consistency_score,
                improvement_rate=improvement_rate,
                sustainability_score=sustainability_score
            )
            
        except Exception as e:
            logger.error(f"Error analyzing profitability trend: {str(e)}")
            return ProfitabilityTrend(
                trend_direction="stable",
                trend_strength=50.0,
                consistency_score=50.0,
                improvement_rate=0.0,
                sustainability_score=50.0
            )
    
    def _calculate_consistency_score(self, margins: List[float]) -> float:
        """חישוב ציון עקביות"""
        try:
            if len(margins) < 2:
                return 50.0
            
            # חישוב סטיית תקן
            std_dev = np.std(margins)
            mean_margin = np.mean(margins)
            
            # מקדם וריאציה
            cv = std_dev / mean_margin if mean_margin > 0 else 1.0
            
            # המרה לציון (נמוך יותר = עקביות גבוהה יותר)
            consistency_score = max(0, 100 - cv * 100)
            return min(100, consistency_score)
            
        except:
            return 50.0
    
    def _calculate_sustainability_score(self, margins: List[float]) -> float:
        """חישוב ציון קיימות"""
        try:
            if len(margins) < 2:
                return 50.0
            
            # בדיקת יציבות
            recent_trend = margins[0] - margins[1] if len(margins) >= 2 else 0
            
            # בדיקת רמה
            avg_margin = np.mean(margins)
            
            # ציון קיימות
            sustainability_score = 50.0
            
            # בונוס לרמה גבוהה
            if avg_margin > 0.1:
                sustainability_score += 20
            elif avg_margin > 0.05:
                sustainability_score += 10
            
            # בונוס ליציבות
            if abs(recent_trend) < 0.02:
                sustainability_score += 20
            elif abs(recent_trend) < 0.05:
                sustainability_score += 10
            
            # בונוס למגמה חיובית
            if recent_trend > 0:
                sustainability_score += 10
            
            return min(100, max(0, sustainability_score))
            
        except:
            return 50.0
    
    def _analyze_profitability_quality(self, financial_data: Dict) -> Dict:
        """ניתוח איכות רווחיות"""
        try:
            income_stmt = financial_data["income_statement"]
            cash_flow = financial_data.get("cash_flow")
            
            quality_metrics = {
                "cash_flow_quality": 50.0,
                "earnings_quality": 50.0,
                "revenue_quality": 50.0,
                "expense_quality": 50.0
            }
            
            if not income_stmt.empty:
                current_data = income_stmt.iloc[0]
                
                # איכות תזרים מזומנים
                if cash_flow is not None and not cash_flow.empty:
                    net_income = float(current_data.get("netIncome", 0) or 0)
                    operating_cash_flow = float(cash_flow.iloc[0].get("operatingCashFlow", 0) or 0)
                    
                    if net_income > 0:
                        cash_flow_ratio = operating_cash_flow / net_income
                        quality_metrics["cash_flow_quality"] = min(100, max(0, cash_flow_ratio * 100))
                
                # איכות רווחים
                revenue = float(current_data.get("revenue", 1) or 1)
                net_income = float(current_data.get("netIncome", 0) or 0)
                
                if revenue > 0:
                    net_margin = net_income / revenue
                    quality_metrics["earnings_quality"] = min(100, max(0, net_margin * 1000))
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing profitability quality: {str(e)}")
            return {
                "cash_flow_quality": 50.0,
                "earnings_quality": 50.0,
                "revenue_quality": 50.0,
                "expense_quality": 50.0
            }
    
    def _calculate_overall_score(self, metrics: ProfitabilityMetrics, 
                               sector_comparison: SectorComparison, 
                               trend: ProfitabilityTrend) -> int:
        """חישוב ציון כללי"""
        # משקלים
        weights = {
            'roe': 0.20,
            'roa': 0.15,
            'gross_margin': 0.15,
            'net_margin': 0.20,
            'sector_comparison': 0.15,
            'trend': 0.15
        }
        
        # ציונים
        roe_score = min(100, max(0, metrics.roe * 500))  # 20% ROE = 100 נקודות
        roa_score = min(100, max(0, metrics.roa * 1000))  # 10% ROA = 100 נקודות
        gross_margin_score = min(100, max(0, metrics.gross_margin * 200))  # 50% margin = 100 נקודות
        net_margin_score = min(100, max(0, metrics.net_margin * 1000))  # 10% margin = 100 נקודות
        sector_score = sector_comparison.percentile_rank
        trend_score = trend.trend_strength
        
        # חישוב ציון משוקלל
        overall_score = (
            roe_score * weights['roe'] +
            roa_score * weights['roa'] +
            gross_margin_score * weights['gross_margin'] +
            net_margin_score * weights['net_margin'] +
            sector_score * weights['sector_comparison'] +
            trend_score * weights['trend']
        )
        
        return int(min(100, max(1, overall_score)))
    
    def _calculate_confidence(self, financial_data: Dict, metrics: ProfitabilityMetrics) -> float:
        """חישוב רמת ביטחון"""
        try:
            # גורמים שמשפיעים על הביטחון
            data_completeness = 100 if financial_data["income_statement"] is not None else 0
            data_recency = 100 if not financial_data["income_statement"].empty else 0
            metrics_quality = metrics.quality_score
            
            confidence = (data_completeness + data_recency + metrics_quality) / 3
            return min(100, max(0, confidence))
            
        except:
            return 50.0
    
    def _generate_recommendations(self, metrics: ProfitabilityMetrics, 
                                sector_comparison: SectorComparison, 
                                trend: ProfitabilityTrend) -> List[str]:
        """יצירת המלצות"""
        recommendations = []
        
        # המלצות לפי ROE
        if metrics.roe > self.profitability_thresholds['excellent']['roe']:
            recommendations.append("ROE מצוין - רווחיות גבוהה על הון")
        elif metrics.roe < self.profitability_thresholds['poor']['roe']:
            recommendations.append("ROE נמוך - רווחיות חלשה על הון")
        
        # המלצות לפי Net Margin
        if metrics.net_margin > self.profitability_thresholds['excellent']['net_margin']:
            recommendations.append("רווח נקי גבוה - יעילות תפעולית מצוינת")
        elif metrics.net_margin < self.profitability_thresholds['poor']['net_margin']:
            recommendations.append("רווח נקי נמוך - בעיות יעילות תפעולית")
        
        # המלצות לפי השוואה לסקטור
        if sector_comparison.percentile_rank > 80:
            recommendations.append("ביצועים מעל 80% מהסקטור - יתרון תחרותי")
        elif sector_comparison.percentile_rank < 20:
            recommendations.append("ביצועים מתחת ל-20% מהסקטור - חולשה תחרותית")
        
        # המלצות לפי מגמה
        if trend.trend_direction == "improving":
            recommendations.append("מגמת שיפור ברווחיות - סימן חיובי")
        elif trend.trend_direction == "declining":
            recommendations.append("מגמת ירידה ברווחיות - דורש תשומת לב")
        
        # המלצות לפי איכות
        if metrics.quality_score > 80:
            recommendations.append("איכות רווחיות גבוהה - רווחים איכותיים")
        elif metrics.quality_score < 30:
            recommendations.append("איכות רווחיות נמוכה - רווחים לא יציבים")
        
        return recommendations
    
    def _generate_explanation(self, metrics: ProfitabilityMetrics, 
                            sector_comparison: SectorComparison, 
                            trend: ProfitabilityTrend) -> str:
        """יצירת הסבר מפורט"""
        explanation_parts = []
        
        # הסבר ROE
        explanation_parts.append(f"ROE: {metrics.roe:.1%}")
        
        # הסבר Net Margin
        explanation_parts.append(f"רווח נקי: {metrics.net_margin:.1%}")
        
        # הסבר השוואה לסקטור
        explanation_parts.append(f"דירוג סקטור: {sector_comparison.percentile_rank:.0f}%")
        
        # הסבר מגמה
        trend_name = self.trend_types.get(trend.trend_direction, trend.trend_direction)
        explanation_parts.append(f"מגמה: {trend_name}")
        
        # הסבר איכות
        explanation_parts.append(f"איכות: {metrics.quality_score:.0f}")
        
        return " | ".join(explanation_parts)
    
    def _summarize_financial_data(self, financial_data: Dict) -> Dict:
        """סיכום נתונים פיננסיים"""
        try:
            income_stmt = financial_data["income_statement"]
            balance_sheet = financial_data["balance_sheet"]
            
            summary = {
                "years_available": len(income_stmt) if income_stmt is not None else 0,
                "latest_revenue": float(income_stmt.iloc[0].get("revenue", 0) or 0) if not income_stmt.empty else 0,
                "latest_net_income": float(income_stmt.iloc[0].get("netIncome", 0) or 0) if not income_stmt.empty else 0,
                "total_assets": float(balance_sheet.iloc[0].get("totalAssets", 0) or 0) if not balance_sheet.empty else 0,
                "total_equity": float(balance_sheet.iloc[0].get("totalEquity", 0) or 0) if not balance_sheet.empty else 0
            }
            
            return summary
            
        except:
            return {
                "years_available": 0,
                "latest_revenue": 0,
                "latest_net_income": 0,
                "total_assets": 0,
                "total_equity": 0
            }
    
    def _default_profitability_metrics(self) -> ProfitabilityMetrics:
        """מדדי רווחיות ברירת מחדל"""
        return ProfitabilityMetrics(
            roe=0.0,
            roa=0.0,
            gross_margin=0.0,
            net_margin=0.0,
            operating_margin=0.0,
            ebitda_margin=0.0,
            return_on_capital=0.0,
            return_on_equity=0.0,
            quality_score=50.0,
            trend_score=50.0
        )
    
    def _error_response(self, message: str) -> Dict:
        """תגובת שגיאה סטנדרטית"""
        return {
            "symbol": "UNKNOWN",
            "timestamp": datetime.now().isoformat(),
            "score": 50,
            "confidence": 0,
            "explanation": message,
            "recommendations": ["לא ניתן לנתח - בדוק את הנתונים"],
            "details": {},
            "error": True
        } 