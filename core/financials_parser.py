"""
FinancialsParserAgent - פירוק דוחות כספיים מתקדם
================================================

סוכן מתקדם לפירוק דוחות כספיים והכנת נתונים לפונדמנטליים.
מרכז את כל הפונקציונליות הקיימת מקבצים אחרים.

תכונות מתקדמות:
- פירוק דוחות רווח והפסד
- פירוק מאזנים
- פירוק תזרימי מזומנים
- נרמול נתונים לפי מניה
- בניית טבלת בסיס אחידה
- טיפול בנתונים חסרים
- ולידציה של נתונים
- ניתוח מגמות פיננסיות
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from utils.data_fetcher import data_fetcher
from utils.logger import logger
from utils.validators import validate_symbol

@dataclass
class FinancialStatement:
    """מבנה נתונים לדוח כספי"""
    statement_type: str  # 'income', 'balance', 'cash_flow'
    data: pd.DataFrame
    period: str
    currency: str
    last_updated: datetime
    data_quality_score: float

@dataclass
class ParsedFinancials:
    """מבנה נתונים לדוחות כספיים מפורקים"""
    income_statement: FinancialStatement
    balance_sheet: FinancialStatement
    cash_flow_statement: Optional[FinancialStatement]
    consolidated_data: pd.DataFrame
    metrics_summary: Dict
    data_quality: Dict

@dataclass
class FinancialMetrics:
    """מבנה נתונים למדדים פיננסיים"""
    revenue: float
    net_income: float
    total_assets: float
    total_equity: float
    total_debt: float
    operating_cash_flow: float
    free_cash_flow: float
    growth_rate: float
    debt_to_equity: float
    current_ratio: float

class FinancialsParserAgent:
    """
    סוכן מתקדם לפירוק דוחות כספיים
    
    תכונות מתקדמות:
    - פירוק דוחות רווח והפסד
    - פירוק מאזנים
    - פירוק תזרימי מזומנים
    - נרמול נתונים לפי מניה
    - בניית טבלת בסיס אחידה
    - טיפול בנתונים חסרים
    - ולידציה של נתונים
    - ניתוח מגמות פיננסיות
    """
    
    def __init__(self, config=None):
        """אתחול הסוכן עם הגדרות מתקדמות"""
        self.config = config or {}
        
        # הגדרות מתקדמות
        self.required_periods = {
            'min_years': 2,      # מינימום שנים נדרשות
            'preferred_years': 5, # מספר שנים מועדף
            'max_years': 10      # מקסימום שנים לניתוח
        }
        
        self.data_quality_thresholds = {
            'excellent': 0.9,    # 90% נתונים זמינים
            'good': 0.7,         # 70% נתונים זמינים
            'acceptable': 0.5,   # 50% נתונים זמינים
            'poor': 0.3          # 30% נתונים זמינים
        }
        
        # מיפוי עמודות סטנדרטי
        self.column_mapping = {
            'income_statement': {
                'revenue': ['revenue', 'totalRevenue', 'sales'],
                'cost_of_revenue': ['costOfRevenue', 'costOfGoodsSold', 'cogs'],
                'gross_profit': ['grossProfit'],
                'operating_expenses': ['operatingExpenses', 'sellingGeneralAndAdministrative'],
                'operating_income': ['operatingIncome', 'operatingProfit'],
                'net_income': ['netIncome', 'netProfit', 'netEarnings'],
                'ebitda': ['ebitda', 'EBITDA'],
                'ebit': ['ebit', 'EBIT']
            },
            'balance_sheet': {
                'total_assets': ['totalAssets'],
                'total_liabilities': ['totalLiabilities'],
                'total_equity': ['totalEquity', 'totalStockholdersEquity'],
                'total_debt': ['totalDebt', 'longTermDebt'],
                'current_assets': ['totalCurrentAssets'],
                'current_liabilities': ['totalCurrentLiabilities'],
                'cash': ['cash', 'cashAndCashEquivalents'],
                'inventory': ['inventory'],
                'accounts_receivable': ['accountsReceivable', 'netReceivables']
            },
            'cash_flow': {
                'operating_cash_flow': ['operatingCashFlow', 'netCashProvidedByOperatingActivities'],
                'investing_cash_flow': ['investingCashFlow', 'netCashUsedForInvestingActivities'],
                'financing_cash_flow': ['financingCashFlow', 'netCashUsedProvidedByFinancingActivities'],
                'free_cash_flow': ['freeCashFlow'],
                'capital_expenditure': ['capitalExpenditure', 'capitalExpenditures']
            }
        }
        
        # מדדים פיננסיים חשובים
        self.key_metrics = [
            'revenue', 'net_income', 'total_assets', 'total_equity',
            'operating_cash_flow', 'free_cash_flow', 'debt_to_equity',
            'current_ratio', 'gross_margin', 'net_margin'
        ]
    
    def analyze(self, symbol: str, price_df: pd.DataFrame = None) -> Dict:
        """
        ניתוח דוחות כספיים מקיף
        
        Args:
            symbol: סימבול המניה
            price_df: נתוני מחיר (לא נדרש לניתוח דוחות)
            
        Returns:
            Dict עם תוצאות הניתוח
        """
        try:
            # ולידציה
            if not validate_symbol(symbol):
                return self._error_response("סימבול לא תקין")
            
            # שליפת דוחות כספיים
            financial_data = self._fetch_financial_statements(symbol)
            if financial_data is None:
                return self._error_response("לא ניתן לשלוף דוחות כספיים")
            
            # פירוק דוחות
            parsed_financials = self._parse_financial_statements(financial_data)
            
            # ניתוח איכות נתונים
            data_quality_analysis = self._analyze_data_quality(parsed_financials)
            
            # חישוב מדדים פיננסיים
            financial_metrics = self._calculate_financial_metrics(parsed_financials)
            
            # ניתוח מגמות
            trend_analysis = self._analyze_financial_trends(parsed_financials)
            
            # חישוב ציון כללי
            overall_score = self._calculate_overall_score(parsed_financials, data_quality_analysis, financial_metrics)
            
            # חישוב רמת ביטחון
            confidence = self._calculate_confidence(parsed_financials, data_quality_analysis)
            
            # יצירת המלצות
            recommendations = self._generate_recommendations(parsed_financials, data_quality_analysis, financial_metrics)
            
            # תוצאה סופית
            result = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "score": overall_score,
                "confidence": confidence,
                "explanation": self._generate_explanation(parsed_financials, financial_metrics, data_quality_analysis),
                "recommendations": recommendations,
                "details": {
                    "parsed_financials": {
                        "income_statement": parsed_financials.income_statement.__dict__,
                        "balance_sheet": parsed_financials.balance_sheet.__dict__,
                        "cash_flow_statement": parsed_financials.cash_flow_statement.__dict__ if parsed_financials.cash_flow_statement else None,
                        "consolidated_data": parsed_financials.consolidated_data.to_dict() if not parsed_financials.consolidated_data.empty else {},
                        "metrics_summary": parsed_financials.metrics_summary
                    },
                    "financial_metrics": financial_metrics.__dict__,
                    "data_quality_analysis": data_quality_analysis,
                    "trend_analysis": trend_analysis
                }
            }
            
            logger.info(f"Financials parsing completed for {symbol}: Score={overall_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error in financials parsing for {symbol}: {str(e)}")
            return self._error_response(f"שגיאה בניתוח: {str(e)}")
    
    def _fetch_financial_statements(self, symbol: str) -> Optional[Dict]:
        """שליפת דוחות כספיים"""
        try:
            # שליפת דוח רווח והפסד
            income_statement = data_fetcher.get_income_statement(symbol)
            if income_statement is None or income_statement.empty:
                logger.warning(f"No income statement data for {symbol}")
                return None
            
            # שליפת מאזן
            balance_sheet = data_fetcher.get_balance_sheet(symbol)
            if balance_sheet is None or balance_sheet.empty:
                logger.warning(f"No balance sheet data for {symbol}")
                return None
            
            # שליפת תזרים מזומנים
            cash_flow_statement = data_fetcher.get_cash_flow_statement(symbol)
            
            return {
                "income_statement": income_statement,
                "balance_sheet": balance_sheet,
                "cash_flow_statement": cash_flow_statement
            }
            
        except Exception as e:
            logger.error(f"Error fetching financial statements for {symbol}: {str(e)}")
            return None
    
    def _parse_financial_statements(self, financial_data: Dict) -> ParsedFinancials:
        """פירוק דוחות כספיים"""
        try:
            # פירוק דוח רווח והפסד
            income_statement = self._parse_income_statement(financial_data["income_statement"])
            
            # פירוק מאזן
            balance_sheet = self._parse_balance_sheet(financial_data["balance_sheet"])
            
            # פירוק תזרים מזומנים
            cash_flow_statement = None
            if financial_data["cash_flow_statement"] is not None:
                cash_flow_statement = self._parse_cash_flow_statement(financial_data["cash_flow_statement"])
            
            # בניית נתונים מאוחדים
            consolidated_data = self._build_consolidated_data(income_statement, balance_sheet, cash_flow_statement)
            
            # חישוב מדדים סיכומיים
            metrics_summary = self._calculate_metrics_summary(consolidated_data)
            
            # ניתוח איכות נתונים
            data_quality = self._assess_data_quality(income_statement, balance_sheet, cash_flow_statement)
            
            return ParsedFinancials(
                income_statement=income_statement,
                balance_sheet=balance_sheet,
                cash_flow_statement=cash_flow_statement,
                consolidated_data=consolidated_data,
                metrics_summary=metrics_summary,
                data_quality=data_quality
            )
            
        except Exception as e:
            logger.error(f"Error parsing financial statements: {str(e)}")
            raise
    
    def _parse_income_statement(self, income_data: pd.DataFrame) -> FinancialStatement:
        """פירוק דוח רווח והפסד"""
        try:
            # נרמול עמודות
            normalized_data = self._normalize_columns(income_data, 'income_statement')
            
            # טיפול בנתונים חסרים
            cleaned_data = self._handle_missing_data(normalized_data)
            
            # חישוב איכות נתונים
            data_quality_score = self._calculate_data_completeness(cleaned_data)
            
            return FinancialStatement(
                statement_type='income',
                data=cleaned_data,
                period='annual',
                currency='USD',
                last_updated=datetime.now(),
                data_quality_score=data_quality_score
            )
            
        except Exception as e:
            logger.error(f"Error parsing income statement: {str(e)}")
            raise
    
    def _parse_balance_sheet(self, balance_data: pd.DataFrame) -> FinancialStatement:
        """פירוק מאזן"""
        try:
            # נרמול עמודות
            normalized_data = self._normalize_columns(balance_data, 'balance_sheet')
            
            # טיפול בנתונים חסרים
            cleaned_data = self._handle_missing_data(normalized_data)
            
            # חישוב איכות נתונים
            data_quality_score = self._calculate_data_completeness(cleaned_data)
            
            return FinancialStatement(
                statement_type='balance',
                data=cleaned_data,
                period='annual',
                currency='USD',
                last_updated=datetime.now(),
                data_quality_score=data_quality_score
            )
            
        except Exception as e:
            logger.error(f"Error parsing balance sheet: {str(e)}")
            raise
    
    def _parse_cash_flow_statement(self, cash_flow_data: pd.DataFrame) -> FinancialStatement:
        """פירוק תזרים מזומנים"""
        try:
            # נרמול עמודות
            normalized_data = self._normalize_columns(cash_flow_data, 'cash_flow')
            
            # טיפול בנתונים חסרים
            cleaned_data = self._handle_missing_data(normalized_data)
            
            # חישוב איכות נתונים
            data_quality_score = self._calculate_data_completeness(cleaned_data)
            
            return FinancialStatement(
                statement_type='cash_flow',
                data=cleaned_data,
                period='annual',
                currency='USD',
                last_updated=datetime.now(),
                data_quality_score=data_quality_score
            )
            
        except Exception as e:
            logger.error(f"Error parsing cash flow statement: {str(e)}")
            raise
    
    def _normalize_columns(self, data: pd.DataFrame, statement_type: str) -> pd.DataFrame:
        """נרמול עמודות לפי מיפוי סטנדרטי"""
        try:
            normalized_data = data.copy()
            
            # מיפוי עמודות לפי סוג הדוח
            column_map = self.column_mapping.get(statement_type, {})
            
            for standard_name, possible_names in column_map.items():
                # חיפוש עמודה מתאימה
                found_column = None
                for col_name in possible_names:
                    if col_name in normalized_data.columns:
                        found_column = col_name
                        break
                
                # שינוי שם עמודה לסטנדרטי
                if found_column:
                    normalized_data[standard_name] = normalized_data[found_column]
                    if found_column != standard_name:
                        normalized_data = normalized_data.drop(columns=[found_column])
            
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error normalizing columns: {str(e)}")
            return data
    
    def _handle_missing_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """טיפול בנתונים חסרים"""
        try:
            cleaned_data = data.copy()
            
            # מילוי נתונים חסרים בשיטות שונות
            for column in cleaned_data.columns:
                if cleaned_data[column].dtype in ['float64', 'int64']:
                    # מילוי לפי ממוצע או אקסטרפולציה
                    if cleaned_data[column].isnull().sum() > 0:
                        # מילוי לפי ממוצע של העמודה
                        mean_value = cleaned_data[column].mean()
                        if pd.notna(mean_value):
                            cleaned_data[column] = cleaned_data[column].fillna(mean_value)
                        else:
                            # אם אין ממוצע, מילוי ב-0
                            cleaned_data[column] = cleaned_data[column].fillna(0)
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error handling missing data: {str(e)}")
            return data
    
    def _calculate_data_completeness(self, data: pd.DataFrame) -> float:
        """חישוב שלמות נתונים"""
        try:
            if data.empty:
                return 0.0
            
            # חישוב אחוז נתונים לא חסרים
            total_cells = data.size
            non_null_cells = data.notna().sum().sum()
            
            completeness = non_null_cells / total_cells if total_cells > 0 else 0.0
            return min(1.0, max(0.0, completeness))
            
        except Exception as e:
            logger.error(f"Error calculating data completeness: {str(e)}")
            return 0.0
    
    def _build_consolidated_data(self, income_stmt: FinancialStatement, 
                               balance_sheet: FinancialStatement, 
                               cash_flow_stmt: Optional[FinancialStatement]) -> pd.DataFrame:
        """בניית נתונים מאוחדים"""
        try:
            consolidated_data = pd.DataFrame()
            
            # הוספת נתוני דוח רווח והפסד
            if income_stmt and not income_stmt.data.empty:
                for col in income_stmt.data.columns:
                    consolidated_data[f'income_{col}'] = income_stmt.data[col]
            
            # הוספת נתוני מאזן
            if balance_sheet and not balance_sheet.data.empty:
                for col in balance_sheet.data.columns:
                    consolidated_data[f'balance_{col}'] = balance_sheet.data[col]
            
            # הוספת נתוני תזרים מזומנים
            if cash_flow_stmt and not cash_flow_stmt.data.empty:
                for col in cash_flow_stmt.data.columns:
                    consolidated_data[f'cash_flow_{col}'] = cash_flow_stmt.data[col]
            
            return consolidated_data
            
        except Exception as e:
            logger.error(f"Error building consolidated data: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_metrics_summary(self, consolidated_data: pd.DataFrame) -> Dict:
        """חישוב מדדים סיכומיים"""
        try:
            summary = {}
            
            if consolidated_data.empty:
                return summary
            
            # חישוב מדדים בסיסיים
            for col in consolidated_data.columns:
                if consolidated_data[col].dtype in ['float64', 'int64']:
                    summary[f'{col}_mean'] = consolidated_data[col].mean()
                    summary[f'{col}_std'] = consolidated_data[col].std()
                    summary[f'{col}_min'] = consolidated_data[col].min()
                    summary[f'{col}_max'] = consolidated_data[col].max()
                    summary[f'{col}_latest'] = consolidated_data[col].iloc[0] if len(consolidated_data) > 0 else None
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating metrics summary: {str(e)}")
            return {}
    
    def _assess_data_quality(self, income_stmt: FinancialStatement, 
                           balance_sheet: FinancialStatement, 
                           cash_flow_stmt: Optional[FinancialStatement]) -> Dict:
        """הערכת איכות נתונים"""
        try:
            quality_assessment = {
                'overall_quality': 0.0,
                'income_statement_quality': income_stmt.data_quality_score if income_stmt else 0.0,
                'balance_sheet_quality': balance_sheet.data_quality_score if balance_sheet else 0.0,
                'cash_flow_quality': cash_flow_stmt.data_quality_score if cash_flow_stmt else 0.0,
                'data_completeness': 0.0,
                'data_consistency': 0.0,
                'data_recency': 0.0
            }
            
            # חישוב איכות כללית
            quality_scores = []
            if income_stmt:
                quality_scores.append(income_stmt.data_quality_score)
            if balance_sheet:
                quality_scores.append(balance_sheet.data_quality_score)
            if cash_flow_stmt:
                quality_scores.append(cash_flow_stmt.data_quality_score)
            
            if quality_scores:
                quality_assessment['overall_quality'] = np.mean(quality_scores)
                quality_assessment['data_completeness'] = np.mean(quality_scores)
            
            # הערכת עקביות נתונים
            quality_assessment['data_consistency'] = self._assess_data_consistency(income_stmt, balance_sheet, cash_flow_stmt)
            
            # הערכת עדכניות נתונים
            quality_assessment['data_recency'] = self._assess_data_recency(income_stmt, balance_sheet, cash_flow_stmt)
            
            return quality_assessment
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {str(e)}")
            return {
                'overall_quality': 0.0,
                'income_statement_quality': 0.0,
                'balance_sheet_quality': 0.0,
                'cash_flow_quality': 0.0,
                'data_completeness': 0.0,
                'data_consistency': 0.0,
                'data_recency': 0.0
            }
    
    def _assess_data_consistency(self, income_stmt: FinancialStatement, 
                               balance_sheet: FinancialStatement, 
                               cash_flow_stmt: Optional[FinancialStatement]) -> float:
        """הערכת עקביות נתונים"""
        try:
            consistency_score = 1.0
            
            # בדיקת עקביות בין דוחות
            if income_stmt and balance_sheet:
                # בדיקה בסיסית - רווח נקי חיובי אם יש הון עצמי
                if 'net_income' in income_stmt.data.columns and 'total_equity' in balance_sheet.data.columns:
                    net_income = income_stmt.data['net_income'].iloc[0] if len(income_stmt.data) > 0 else 0
                    total_equity = balance_sheet.data['total_equity'].iloc[0] if len(balance_sheet.data) > 0 else 0
                    
                    if net_income > 0 and total_equity <= 0:
                        consistency_score *= 0.8  # עקביות נמוכה
            
            return consistency_score
            
        except Exception as e:
            logger.error(f"Error assessing data consistency: {str(e)}")
            return 0.5
    
    def _assess_data_recency(self, income_stmt: FinancialStatement, 
                           balance_sheet: FinancialStatement, 
                           cash_flow_stmt: Optional[FinancialStatement]) -> float:
        """הערכת עדכניות נתונים"""
        try:
            # בדיקת עדכניות לפי תאריך עדכון אחרון
            current_time = datetime.now()
            
            recency_scores = []
            
            for statement in [income_stmt, balance_sheet, cash_flow_stmt]:
                if statement:
                    time_diff = current_time - statement.last_updated
                    days_diff = time_diff.days
                    
                    if days_diff <= 30:
                        recency_score = 1.0
                    elif days_diff <= 90:
                        recency_score = 0.8
                    elif days_diff <= 180:
                        recency_score = 0.6
                    elif days_diff <= 365:
                        recency_score = 0.4
                    else:
                        recency_score = 0.2
                    
                    recency_scores.append(recency_score)
            
            return np.mean(recency_scores) if recency_scores else 0.5
            
        except Exception as e:
            logger.error(f"Error assessing data recency: {str(e)}")
            return 0.5
    
    def _calculate_financial_metrics(self, parsed_financials: ParsedFinancials) -> FinancialMetrics:
        """חישוב מדדים פיננסיים"""
        try:
            income_data = parsed_financials.income_statement.data
            balance_data = parsed_financials.balance_sheet.data
            
            # חישוב מדדים בסיסיים
            revenue = float(income_data.get('revenue', [0]).iloc[0]) if not income_data.empty and 'revenue' in income_data.columns else 0
            net_income = float(income_data.get('net_income', [0]).iloc[0]) if not income_data.empty and 'net_income' in income_data.columns else 0
            total_assets = float(balance_data.get('total_assets', [0]).iloc[0]) if not balance_data.empty and 'total_assets' in balance_data.columns else 0
            total_equity = float(balance_data.get('total_equity', [0]).iloc[0]) if not balance_data.empty and 'total_equity' in balance_data.columns else 0
            total_debt = float(balance_data.get('total_debt', [0]).iloc[0]) if not balance_data.empty and 'total_debt' in balance_data.columns else 0
            
            # חישוב מדדים נגזרים
            operating_cash_flow = 0
            free_cash_flow = 0
            if parsed_financials.cash_flow_statement and not parsed_financials.cash_flow_statement.data.empty:
                cash_flow_data = parsed_financials.cash_flow_statement.data
                operating_cash_flow = float(cash_flow_data.get('operating_cash_flow', [0]).iloc[0]) if 'operating_cash_flow' in cash_flow_data.columns else 0
                free_cash_flow = float(cash_flow_data.get('free_cash_flow', [0]).iloc[0]) if 'free_cash_flow' in cash_flow_data.columns else 0
            
            # חישוב יחסים
            debt_to_equity = total_debt / total_equity if total_equity > 0 else 0
            current_ratio = 0
            if not balance_data.empty and 'current_assets' in balance_data.columns and 'current_liabilities' in balance_data.columns:
                current_assets = float(balance_data.get('current_assets', [0]).iloc[0])
                current_liabilities = float(balance_data.get('current_liabilities', [1]).iloc[0])
                current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
            
            # חישוב קצב צמיחה
            growth_rate = 0
            if len(income_data) >= 2 and 'revenue' in income_data.columns:
                current_revenue = float(income_data['revenue'].iloc[0])
                previous_revenue = float(income_data['revenue'].iloc[1])
                growth_rate = (current_revenue - previous_revenue) / previous_revenue if previous_revenue > 0 else 0
            
            return FinancialMetrics(
                revenue=revenue,
                net_income=net_income,
                total_assets=total_assets,
                total_equity=total_equity,
                total_debt=total_debt,
                operating_cash_flow=operating_cash_flow,
                free_cash_flow=free_cash_flow,
                growth_rate=growth_rate,
                debt_to_equity=debt_to_equity,
                current_ratio=current_ratio
            )
            
        except Exception as e:
            logger.error(f"Error calculating financial metrics: {str(e)}")
            return FinancialMetrics(
                revenue=0, net_income=0, total_assets=0, total_equity=0,
                total_debt=0, operating_cash_flow=0, free_cash_flow=0,
                growth_rate=0, debt_to_equity=0, current_ratio=0
            )
    
    def _analyze_financial_trends(self, parsed_financials: ParsedFinancials) -> Dict:
        """ניתוח מגמות פיננסיות"""
        try:
            trends = {}
            
            # ניתוח מגמות בדוח רווח והפסד
            if not parsed_financials.income_statement.data.empty:
                income_trends = self._analyze_statement_trends(parsed_financials.income_statement.data)
                trends['income_statement_trends'] = income_trends
            
            # ניתוח מגמות במאזן
            if not parsed_financials.balance_sheet.data.empty:
                balance_trends = self._analyze_statement_trends(parsed_financials.balance_sheet.data)
                trends['balance_sheet_trends'] = balance_trends
            
            # ניתוח מגמות בתזרים מזומנים
            if parsed_financials.cash_flow_statement and not parsed_financials.cash_flow_statement.data.empty:
                cash_flow_trends = self._analyze_statement_trends(parsed_financials.cash_flow_statement.data)
                trends['cash_flow_trends'] = cash_flow_trends
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing financial trends: {str(e)}")
            return {}
    
    def _analyze_statement_trends(self, data: pd.DataFrame) -> Dict:
        """ניתוח מגמות בדוח ספציפי"""
        try:
            trends = {}
            
            for column in data.columns:
                if data[column].dtype in ['float64', 'int64'] and len(data) >= 2:
                    values = data[column].dropna()
                    if len(values) >= 2:
                        # חישוב מגמה
                        x = np.arange(len(values))
                        slope = np.polyfit(x, values, 1)[0]
                        
                        # זיהוי כיוון מגמה
                        if slope > 0:
                            trend_direction = "עולה"
                        elif slope < 0:
                            trend_direction = "יורד"
                        else:
                            trend_direction = "יציב"
                        
                        trends[column] = {
                            'trend_direction': trend_direction,
                            'slope': slope,
                            'change_percent': ((values.iloc[-1] - values.iloc[0]) / values.iloc[0] * 100) if values.iloc[0] != 0 else 0
                        }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing statement trends: {str(e)}")
            return {}
    
    def _analyze_data_quality(self, parsed_financials: ParsedFinancials) -> Dict:
        """ניתוח איכות נתונים"""
        try:
            quality_analysis = {
                'overall_score': parsed_financials.data_quality['overall_quality'],
                'completeness_score': parsed_financials.data_quality['data_completeness'],
                'consistency_score': parsed_financials.data_quality['data_consistency'],
                'recency_score': parsed_financials.data_quality['data_recency'],
                'quality_level': self._get_quality_level(parsed_financials.data_quality['overall_quality']),
                'issues': self._identify_data_issues(parsed_financials)
            }
            
            return quality_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing data quality: {str(e)}")
            return {
                'overall_score': 0.0,
                'completeness_score': 0.0,
                'consistency_score': 0.0,
                'recency_score': 0.0,
                'quality_level': 'poor',
                'issues': ['שגיאה בניתוח איכות נתונים']
            }
    
    def _get_quality_level(self, quality_score: float) -> str:
        """קבלת רמת איכות"""
        if quality_score >= self.data_quality_thresholds['excellent']:
            return 'excellent'
        elif quality_score >= self.data_quality_thresholds['good']:
            return 'good'
        elif quality_score >= self.data_quality_thresholds['acceptable']:
            return 'acceptable'
        else:
            return 'poor'
    
    def _identify_data_issues(self, parsed_financials: ParsedFinancials) -> List[str]:
        """זיהוי בעיות נתונים"""
        issues = []
        
        try:
            # בדיקת שלמות נתונים
            if parsed_financials.data_quality['data_completeness'] < 0.5:
                issues.append("נתונים חסרים רבים")
            
            # בדיקת עקביות
            if parsed_financials.data_quality['data_consistency'] < 0.7:
                issues.append("חוסר עקביות בין דוחות")
            
            # בדיקת עדכניות
            if parsed_financials.data_quality['data_recency'] < 0.5:
                issues.append("נתונים לא עדכניים")
            
            # בדיקת דוח תזרים מזומנים
            if parsed_financials.cash_flow_statement is None:
                issues.append("חסר דוח תזרים מזומנים")
            
            return issues
            
        except Exception as e:
            logger.error(f"Error identifying data issues: {str(e)}")
            return ["שגיאה בזיהוי בעיות נתונים"]
    
    def _calculate_overall_score(self, parsed_financials: ParsedFinancials, 
                               data_quality_analysis: Dict, 
                               financial_metrics: FinancialMetrics) -> int:
        """חישוב ציון כללי"""
        try:
            # משקלים
            weights = {
                'data_quality': 0.4,
                'financial_health': 0.3,
                'data_completeness': 0.3
            }
            
            # ציון איכות נתונים
            data_quality_score = data_quality_analysis.get('overall_score', 0) * 100
            
            # ציון בריאות פיננסית
            financial_health_score = self._calculate_financial_health_score(financial_metrics)
            
            # ציון שלמות נתונים
            data_completeness_score = data_quality_analysis.get('completeness_score', 0) * 100
            
            # חישוב ציון משוקלל
            overall_score = (
                data_quality_score * weights['data_quality'] +
                financial_health_score * weights['financial_health'] +
                data_completeness_score * weights['data_completeness']
            )
            
            return int(min(100, max(1, overall_score)))
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {str(e)}")
            return 50
    
    def _calculate_financial_health_score(self, metrics: FinancialMetrics) -> float:
        """חישוב ציון בריאות פיננסית"""
        try:
            score = 50.0  # ציון בסיסי
            
            # בונוס לרווחיות
            if metrics.net_income > 0:
                score += 20
            
            # בונוס לתזרים מזומנים חיובי
            if metrics.operating_cash_flow > 0:
                score += 15
            
            # בונוס ליחס חוב נמוך
            if metrics.debt_to_equity < 0.5:
                score += 10
            elif metrics.debt_to_equity < 1.0:
                score += 5
            
            # בונוס ליחס שוטף גבוה
            if metrics.current_ratio > 1.5:
                score += 5
            
            # בונוס לצמיחה
            if metrics.growth_rate > 0.1:
                score += 10
            elif metrics.growth_rate > 0:
                score += 5
            
            return min(100, max(0, score))
            
        except Exception as e:
            logger.error(f"Error calculating financial health score: {str(e)}")
            return 50.0
    
    def _calculate_confidence(self, parsed_financials: ParsedFinancials, 
                            data_quality_analysis: Dict) -> float:
        """חישוב רמת ביטחון"""
        try:
            # גורמים שמשפיעים על הביטחון
            data_quality = data_quality_analysis.get('overall_score', 0) * 100
            data_completeness = data_quality_analysis.get('completeness_score', 0) * 100
            data_recency = data_quality_analysis.get('recency_score', 0) * 100
            
            confidence = (data_quality + data_completeness + data_recency) / 3
            return min(100, max(0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 50.0
    
    def _generate_recommendations(self, parsed_financials: ParsedFinancials, 
                                data_quality_analysis: Dict, 
                                financial_metrics: FinancialMetrics) -> List[str]:
        """יצירת המלצות"""
        recommendations = []
        
        try:
            # המלצות לפי איכות נתונים
            quality_level = data_quality_analysis.get('quality_level', 'poor')
            if quality_level == 'poor':
                recommendations.append("איכות נתונים נמוכה - שקול מקורות נתונים נוספים")
            elif quality_level == 'acceptable':
                recommendations.append("איכות נתונים סבירה - יש מקום לשיפור")
            
            # המלצות לפי בריאות פיננסית
            if financial_metrics.net_income < 0:
                recommendations.append("רווח שלילי - דורש תשומת לב מיוחדת")
            
            if financial_metrics.debt_to_equity > 1.0:
                recommendations.append("יחס חוב גבוה - סיכון פיננסי מוגבר")
            
            if financial_metrics.current_ratio < 1.0:
                recommendations.append("יחס שוטף נמוך - בעיות נזילות")
            
            if financial_metrics.operating_cash_flow < 0:
                recommendations.append("תזרים מזומנים שלילי - בעיות תפעוליות")
            
            # המלצות לפי מגמות
            if financial_metrics.growth_rate > 0.2:
                recommendations.append("צמיחה גבוהה - הזדמנות טובה")
            elif financial_metrics.growth_rate < -0.1:
                recommendations.append("צמיחה שלילית - דורש מעקב")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["שגיאה ביצירת המלצות"]
    
    def _generate_explanation(self, parsed_financials: ParsedFinancials, 
                            financial_metrics: FinancialMetrics, 
                            data_quality_analysis: Dict) -> str:
        """יצירת הסבר מפורט"""
        try:
            explanation_parts = []
            
            # הסבר איכות נתונים
            quality_level = data_quality_analysis.get('quality_level', 'unknown')
            explanation_parts.append(f"איכות נתונים: {quality_level}")
            
            # הסבר מדדים פיננסיים
            if financial_metrics.revenue > 0:
                explanation_parts.append(f"הכנסות: ${financial_metrics.revenue:,.0f}")
            
            if financial_metrics.net_income != 0:
                explanation_parts.append(f"רווח נקי: ${financial_metrics.net_income:,.0f}")
            
            if financial_metrics.debt_to_equity > 0:
                explanation_parts.append(f"יחס חוב: {financial_metrics.debt_to_equity:.2f}")
            
            if financial_metrics.growth_rate != 0:
                explanation_parts.append(f"צמיחה: {financial_metrics.growth_rate:.1%}")
            
            return " | ".join(explanation_parts)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return "שגיאה ביצירת הסבר"
    
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