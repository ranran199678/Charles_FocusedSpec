import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.base.base_agent import BaseAgent
from core.profitability_metrics import ProfitabilityMetricsAgent

class FinancialStabilityAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__(config)
        self.leverage_weight = self.config.get("leverage_weight", 0.25)
        self.liquidity_weight = self.config.get("liquidity_weight", 0.25)
        self.cash_flow_weight = self.config.get("cash_flow_weight", 0.25)
        self.risk_weight = self.config.get("risk_weight", 0.25)
        self.profitability_agent = ProfitabilityMetricsAgent()

    def analyze(self, symbol, price_df=None):
        try:
            # שליפת נתוני מאזן דרך מנהל הנתונים החכם
            balance = self.get_fundamentals(symbol, "balance")
            income = self.get_fundamentals(symbol, "income")
            cash_flow = self.get_fundamentals(symbol, "cash_flow")
            
            if balance is None or balance.empty:
                return {
                    "score": 50,
                    "explanation": "אין נתוני מאזן זמינים",
                    "details": {}
                }

            # ניתוח מפורט של יציבות פיננסית
            leverage_analysis = self._analyze_leverage_ratios(balance)
            liquidity_analysis = self._analyze_liquidity_ratios(balance)
            cash_flow_analysis = self._analyze_cash_flow_stability(cash_flow, income)
            risk_analysis = self._analyze_financial_risk(balance, income)
            
            # ניתוח רווחיות
            profitability_result = self.profitability_agent.analyze(symbol, price_df)
            profitability_score = profitability_result.get("score", 50)
            
            # חישוב ציון סופי משוקלל
            final_score = self._calculate_weighted_score(
                leverage_analysis, liquidity_analysis, cash_flow_analysis, 
                risk_analysis, profitability_score
            )
            
            explanation = self._build_comprehensive_explanation(
                leverage_analysis, liquidity_analysis, cash_flow_analysis,
                risk_analysis, profitability_score, final_score
            )

            return {
                "score": max(1, min(100, final_score)),
                "explanation": explanation,
                "details": {
                    "leverage_analysis": leverage_analysis,
                    "liquidity_analysis": liquidity_analysis,
                    "cash_flow_analysis": cash_flow_analysis,
                    "risk_analysis": risk_analysis,
                    "profitability_analysis": profitability_result
                }
            }
        except Exception as e:
            self.handle_error(e)
            return self.fallback()

    def _analyze_leverage_ratios(self, balance):
        """ניתוח יחסי מינוף"""
        try:
            # חישוב יחס חוב להון
            total_debt = float(balance.iloc[0].get("totalDebt", 0) or 0)
            total_equity = float(balance.iloc[0].get("totalEquity", 1) or 1)
            debt_to_equity = total_debt / total_equity if total_equity > 0 else 1
            
            # חישוב יחס חוב כולל
            total_assets = float(balance.iloc[0].get("totalAssets", 1) or 1)
            debt_to_assets = total_debt / total_assets if total_assets > 0 else 1
            
            # חישוב יחס כיסוי ריבית (אם זמין)
            interest_expense = float(balance.iloc[0].get("interestExpense", 1) or 1)
            ebit = float(balance.iloc[0].get("ebit", 0) or 0)
            interest_coverage = ebit / interest_expense if interest_expense > 0 else 10
            
            # ניקוד מינוף
            if debt_to_equity < 0.3:
                leverage_score = 90
                leverage_level = "מצוין"
            elif debt_to_equity < 0.5:
                leverage_score = 75
                leverage_level = "טוב"
            elif debt_to_equity < 1.0:
                leverage_score = 60
                leverage_level = "בינוני"
            elif debt_to_equity < 2.0:
                leverage_score = 40
                leverage_level = "גבוה"
            else:
                leverage_score = 20
                leverage_level = "מסוכן"
            
            return {
                "score": leverage_score,
                "debt_to_equity": debt_to_equity,
                "debt_to_assets": debt_to_assets,
                "interest_coverage": interest_coverage,
                "level": leverage_level,
                "total_debt": total_debt,
                "total_equity": total_equity
            }
        except Exception:
            return {"score": 50, "level": "לא ידוע"}

    def _analyze_liquidity_ratios(self, balance):
        """ניתוח יחסי נזילות"""
        try:
            # חישוב יחס שוטף
            current_assets = float(balance.iloc[0].get("totalCurrentAssets", 0) or 0)
            current_liabilities = float(balance.iloc[0].get("totalCurrentLiabilities", 1) or 1)
            current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 1
            
            # חישוב יחס מהיר
            inventory = float(balance.iloc[0].get("inventory", 0) or 0)
            quick_assets = current_assets - inventory
            quick_ratio = quick_assets / current_liabilities if current_liabilities > 0 else 1
            
            # חישוב נזילות מזומן
            cash = float(balance.iloc[0].get("cashAndCashEquivalents", 0) or 0)
            cash_ratio = cash / current_liabilities if current_liabilities > 0 else 0
            
            # ניקוד נזילות
            if current_ratio > 2.0 and quick_ratio > 1.5:
                liquidity_score = 90
                liquidity_level = "מצוין"
            elif current_ratio > 1.5 and quick_ratio > 1.0:
                liquidity_score = 75
                liquidity_level = "טוב"
            elif current_ratio > 1.2 and quick_ratio > 0.8:
                liquidity_score = 60
                liquidity_level = "בינוני"
            elif current_ratio > 1.0:
                liquidity_score = 40
                liquidity_level = "נמוך"
            else:
                liquidity_score = 20
                liquidity_level = "מסוכן"
            
            return {
                "score": liquidity_score,
                "current_ratio": current_ratio,
                "quick_ratio": quick_ratio,
                "cash_ratio": cash_ratio,
                "level": liquidity_level,
                "current_assets": current_assets,
                "current_liabilities": current_liabilities
            }
        except Exception:
            return {"score": 50, "level": "לא ידוע"}

    def _analyze_cash_flow_stability(self, cash_flow, income):
        """ניתוח יציבות תזרים מזומנים"""
        try:
            if cash_flow is None or cash_flow.empty:
                return {"score": 50, "level": "לא ידוע"}
            
            # חישוב תזרים מזומנים תפעולי
            operating_cash_flow = float(cash_flow.iloc[0].get("operatingCashFlow", 0) or 0)
            
            # חישוב תזרים מזומנים חופשי
            capex = float(cash_flow.iloc[0].get("capitalExpenditure", 0) or 0)
            free_cash_flow = operating_cash_flow + capex  # capex הוא שלילי בדרך כלל
            
            # חישוב יחס כיסוי תזרים
            total_debt = float(cash_flow.iloc[0].get("totalDebt", 1) or 1)
            cash_flow_coverage = operating_cash_flow / total_debt if total_debt > 0 else 10
            
            # ניקוד תזרים מזומנים
            if operating_cash_flow > 0 and free_cash_flow > 0:
                if cash_flow_coverage > 0.3:
                    cash_flow_score = 90
                    cash_flow_level = "מצוין"
                elif cash_flow_coverage > 0.2:
                    cash_flow_score = 75
                    cash_flow_level = "טוב"
                elif cash_flow_coverage > 0.1:
                    cash_flow_score = 60
                    cash_flow_level = "בינוני"
                else:
                    cash_flow_score = 40
                    cash_flow_level = "נמוך"
            elif operating_cash_flow > 0:
                cash_flow_score = 50
                cash_flow_level = "חיובי אך לא חופשי"
            else:
                cash_flow_score = 20
                cash_flow_level = "שלילי"
            
            return {
                "score": cash_flow_score,
                "operating_cash_flow": operating_cash_flow,
                "free_cash_flow": free_cash_flow,
                "cash_flow_coverage": cash_flow_coverage,
                "level": cash_flow_level
            }
        except Exception:
            return {"score": 50, "level": "לא ידוע"}

    def _analyze_financial_risk(self, balance, income):
        """ניתוח סיכונים פיננסיים"""
        try:
            # חישוב יחס כיסוי ריבית
            ebit = float(income.iloc[0].get("ebit", 0) or 0) if income is not None and not income.empty else 0
            interest_expense = float(income.iloc[0].get("interestExpense", 1) or 1) if income is not None and not income.empty else 1
            interest_coverage = ebit / interest_expense if interest_expense > 0 else 10
            
            # חישוב יחס כיסוי דיבידנד
            net_income = float(income.iloc[0].get("netIncome", 0) or 0) if income is not None and not income.empty else 0
            dividends = float(income.iloc[0].get("dividendPaid", 0) or 0) if income is not None and not income.empty else 0
            dividend_coverage = net_income / abs(dividends) if dividends < 0 else 10
            
            # ניקוד סיכון
            if interest_coverage > 5 and dividend_coverage > 3:
                risk_score = 90
                risk_level = "נמוך מאוד"
            elif interest_coverage > 3 and dividend_coverage > 2:
                risk_score = 75
                risk_level = "נמוך"
            elif interest_coverage > 2 and dividend_coverage > 1.5:
                risk_score = 60
                risk_level = "בינוני"
            elif interest_coverage > 1.5:
                risk_score = 40
                risk_level = "גבוה"
            else:
                risk_score = 20
                risk_level = "מסוכן"
            
            return {
                "score": risk_score,
                "interest_coverage": interest_coverage,
                "dividend_coverage": dividend_coverage,
                "level": risk_level,
                "ebit": ebit,
                "net_income": net_income
            }
        except Exception:
            return {"score": 50, "level": "לא ידוע"}

    def _calculate_weighted_score(self, leverage, liquidity, cash_flow, risk, profitability):
        """חישוב ציון סופי משוקלל"""
        leverage_score = leverage.get("score", 50)
        liquidity_score = liquidity.get("score", 50)
        cash_flow_score = cash_flow.get("score", 50)
        risk_score = risk.get("score", 50)
        
        weighted_score = (
            leverage_score * self.leverage_weight +
            liquidity_score * self.liquidity_weight +
            cash_flow_score * self.cash_flow_weight +
            risk_score * self.risk_weight
        )
        
        # התאמה לפי רווחיות
        final_score = (weighted_score * 0.7) + (profitability * 0.3)
        
        return max(1, min(100, int(final_score)))

    def _build_comprehensive_explanation(self, leverage, liquidity, cash_flow, risk, profitability, final_score):
        """בניית הסבר מקיף"""
        explanation = f"🏦 FinancialStabilityAgent – ניתוח יציבות פיננסית:\n"
        
        # ניתוח מינוף
        leverage_level = leverage.get("level", "לא ידוע")
        debt_to_equity = leverage.get("debt_to_equity", 0)
        explanation += f"📊 מינוף: {leverage_level} (יחס חוב/הון: {debt_to_equity:.2f})\n"
        
        # ניתוח נזילות
        liquidity_level = liquidity.get("level", "לא ידוע")
        current_ratio = liquidity.get("current_ratio", 0)
        explanation += f"💧 נזילות: {liquidity_level} (יחס שוטף: {current_ratio:.2f})\n"
        
        # ניתוח תזרים מזומנים
        cash_flow_level = cash_flow.get("level", "לא ידוע")
        operating_cf = cash_flow.get("operating_cash_flow", 0)
        explanation += f"💰 תזרים מזומנים: {cash_flow_level} (תזרים תפעולי: {operating_cf:,.0f})\n"
        
        # ניתוח סיכון
        risk_level = risk.get("level", "לא ידוע")
        interest_coverage = risk.get("interest_coverage", 0)
        explanation += f"⚠️ סיכון: {risk_level} (כיסוי ריבית: {interest_coverage:.2f})\n"
        
        # רווחיות
        explanation += f"📈 רווחיות: {profitability} נקודות\n"
        
        # ציון סופי
        if final_score >= 80:
            stability_level = "🚀 יציבות פיננסית מצוינת"
        elif final_score >= 65:
            stability_level = "✅ יציבות פיננסית טובה"
        elif final_score >= 45:
            stability_level = "⚠️ יציבות פיננסית בינונית"
        else:
            stability_level = "❌ יציבות פיננסית חלשה"
        
        explanation += f"🎯 ציון סופי: {final_score} - {stability_level}"
        
        return explanation
