import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# הוספת הנתיב לספריות
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.alpha_score_engine import AlphaScoreEngine
from core.nlp_analyzer import NLPAnalyzer
from core.event_scanner import EventScanner
from core.macro_trend_scanner import MacroTrendScanner
from core.social_media_hype_scanner import SocialMediaHypeScanner
from utils.data_fetcher import DataFetcher

class MainDashboard:
    """
    Main Dashboard - תצוגה גרפית ומרכזית של המערכת
    
    כולל:
    - דוחות מפורטים
    - התראות בזמן אמת
    - ניהול תסריטי אוטומציה
    - שילוב ML
    - backtesting
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.data_fetcher = DataFetcher()
        
        # אתחול כל הסוכנים
        self.alpha_engine = AlphaScoreEngine()
        self.nlp_analyzer = NLPAnalyzer()
        self.event_scanner = EventScanner()
        self.macro_scanner = MacroTrendScanner()
        self.hype_scanner = SocialMediaHypeScanner()
        
        # ניהול התראות
        self.alerts = []
        self.alert_thresholds = {
            "score_change": 10,  # שינוי של 10 נקודות
            "sentiment_change": "significant",  # שינוי משמעותי בסנטימנט
            "hype_spike": 20,  # עלייה של 20 נקודות ב-hype
            "macro_event": True  # אירוע מאקרו משמעותי
        }
        
        # היסטוריית ניתוחים
        self.analysis_history = {}
        
        # ניהול תסריטים
        self.scenarios = {
            "bull_market": {
                "conditions": ["macro_score > 70", "sentiment > 60"],
                "actions": ["buy_quality_stocks", "hold_positions"]
            },
            "bear_market": {
                "conditions": ["macro_score < 30", "sentiment < 40"],
                "actions": ["sell_weak_positions", "buy_defensive"]
            },
            "hype_mania": {
                "conditions": ["hype_score > 80", "sentiment > 70"],
                "actions": ["caution", "take_profits"]
            }
        }
        
        self.log("Main Dashboard initialized")

    def log(self, msg):
        """רישום הודעה ללוג"""
        print(f"[Dashboard] {msg}")

    def analyze_stock(self, symbol: str) -> Dict:
        """
        ניתוח מלא של מניה עם כל הסוכנים
        
        Args:
            symbol: סמל המניה
            
        Returns:
            Dict עם כל הניתוחים והמלצות
        """
        try:
            self.log(f"Starting comprehensive analysis for {symbol}")
            
            # 1. איסוף נתוני מחירים
            price_df = self.data_fetcher.get_price_history(symbol, period="1y")
            
            # 2. ניתוח עם כל הסוכנים
            results = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "alpha_engine": self.alpha_engine.evaluate(symbol, price_df),
                "nlp_analyzer": self.nlp_analyzer.analyze(symbol),
                "event_scanner": self.event_scanner.analyze(symbol),
                "macro_scanner": self.macro_scanner.analyze(symbol),
                "hype_scanner": self.hype_scanner.analyze(symbol)
            }
            
            # 3. חישוב ציון כולל
            overall_score = self._calculate_overall_score(results)
            results["overall_score"] = overall_score
            
            # 4. יצירת המלצות
            recommendations = self._generate_recommendations(results)
            results["recommendations"] = recommendations
            
            # 5. בדיקת התראות
            alerts = self._check_alerts(symbol, results)
            results["alerts"] = alerts
            
            # 6. שמירה בהיסטוריה
            self.analysis_history[symbol] = results
            
            # 7. יצירת דוח מפורט
            detailed_report = self._generate_detailed_report(results)
            results["detailed_report"] = detailed_report
            
            self.log(f"Analysis completed for {symbol}: Overall Score {overall_score}")
            return results
            
        except Exception as e:
            self.log(f"Error analyzing {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "overall_score": 50
            }

    def _calculate_overall_score(self, results: Dict) -> int:
        """חישוב ציון כולל מכל הסוכנים"""
        scores = []
        weights = []
        
        # Alpha Score Engine (משקל גבוה)
        alpha_score = results.get("alpha_engine", {}).get("score", 50)
        scores.append(alpha_score)
        weights.append(0.35)
        
        # NLP Analyzer
        nlp_score = results.get("nlp_analyzer", {}).get("score", 50)
        scores.append(nlp_score)
        weights.append(0.25)
        
        # Event Scanner
        event_score = results.get("event_scanner", {}).get("score", 50)
        scores.append(event_score)
        weights.append(0.15)
        
        # Macro Scanner
        macro_score = results.get("macro_scanner", {}).get("score", 50)
        scores.append(macro_score)
        weights.append(0.15)
        
        # Hype Scanner
        hype_score = results.get("hype_scanner", {}).get("score", 50)
        scores.append(hype_score)
        weights.append(0.10)
        
        # חישוב ממוצע משוקלל
        weighted_score = sum(score * weight for score, weight in zip(scores, weights))
        return int(weighted_score)

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """יצירת המלצות על בסיס כל הניתוחים"""
        recommendations = []
        overall_score = results.get("overall_score", 50)
        
        # המלצות לפי ציון כולל
        if overall_score >= 80:
            recommendations.append("🟢 קנייה חזקה - ציון גבוה מאוד")
        elif overall_score >= 60:
            recommendations.append("🟡 קנייה - ציון חיובי")
        elif overall_score >= 40:
            recommendations.append("🟠 החזקה - ציון בינוני")
        elif overall_score >= 20:
            recommendations.append("🔴 מכירה - ציון נמוך")
        else:
            recommendations.append("🔴 מכירה חזקה - ציון נמוך מאוד")
        
        # המלצות לפי סוכנים ספציפיים
        alpha_engine = results.get("alpha_engine", {})
        if alpha_engine.get("score", 50) < 30:
            recommendations.append("⚠️ סוכנים טכניים לא ממליצים")
        
        nlp_analyzer = results.get("nlp_analyzer", {})
        if nlp_analyzer.get("sentiment") == "negative":
            recommendations.append("📰 סנטימנט חדשות שלילי")
        
        event_scanner = results.get("event_scanner", {})
        if event_scanner.get("score", 50) > 70:
            recommendations.append("📅 אירועים משמעותיים זוהו")
        
        macro_scanner = results.get("macro_scanner", {})
        if macro_scanner.get("sentiment") == "very_bearish":
            recommendations.append("🌍 סביבה מאקרו שלילית")
        
        hype_scanner = results.get("hype_scanner", {})
        if hype_scanner.get("score", 50) > 80:
            recommendations.append("🚀 Hype גבוה - זהירות")
        
        return recommendations

    def _check_alerts(self, symbol: str, results: Dict) -> List[Dict]:
        """בדיקת התראות"""
        alerts = []
        
        # בדיקת שינוי משמעותי בציון
        if symbol in self.analysis_history:
            previous_score = self.analysis_history[symbol].get("overall_score", 50)
            current_score = results.get("overall_score", 50)
            change = abs(current_score - previous_score)
            
            if change >= self.alert_thresholds["score_change"]:
                alerts.append({
                    "type": "score_change",
                    "message": f"שינוי משמעותי בציון: {previous_score} → {current_score}",
                    "severity": "high" if change > 20 else "medium"
                })
        
        # בדיקת שינוי בסנטימנט
        nlp_sentiment = results.get("nlp_analyzer", {}).get("sentiment", "neutral")
        if nlp_sentiment in ["very_negative", "very_bullish"]:
            alerts.append({
                "type": "sentiment_change",
                "message": f"סנטימנט קיצוני: {nlp_sentiment}",
                "severity": "high"
            })
        
        # בדיקת hype spike
        hype_score = results.get("hype_scanner", {}).get("score", 50)
        if hype_score > 80:
            alerts.append({
                "type": "hype_spike",
                "message": f"Hype גבוה מאוד: {hype_score}/100",
                "severity": "medium"
            })
        
        # בדיקת אירועים מאקרו
        macro_sentiment = results.get("macro_scanner", {}).get("sentiment", "neutral")
        if macro_sentiment in ["very_bearish", "very_bullish"]:
            alerts.append({
                "type": "macro_event",
                "message": f"אירוע מאקרו משמעותי: {macro_sentiment}",
                "severity": "high"
            })
        
        return alerts

    def _generate_detailed_report(self, results: Dict) -> Dict:
        """יצירת דוח מפורט"""
        symbol = results.get("symbol", "UNKNOWN")
        
        report = {
            "summary": {
                "symbol": symbol,
                "overall_score": results.get("overall_score", 0),
                "timestamp": results.get("timestamp", ""),
                "recommendation": self._get_recommendation_level(results.get("overall_score", 50))
            },
            "agent_scores": {
                "Alpha Score Engine": results.get("alpha_engine", {}).get("score", 0),
                "NLP Analyzer": results.get("nlp_analyzer", {}).get("score", 0),
                "Event Scanner": results.get("event_scanner", {}).get("score", 0),
                "Macro Scanner": results.get("macro_scanner", {}).get("score", 0),
                "Hype Scanner": results.get("hype_scanner", {}).get("score", 0)
            },
            "sentiment_analysis": {
                "nlp_sentiment": results.get("nlp_analyzer", {}).get("sentiment", "neutral"),
                "macro_sentiment": results.get("macro_scanner", {}).get("sentiment", "neutral"),
                "hype_sentiment": results.get("hype_scanner", {}).get("sentiment", "neutral")
            },
            "key_insights": self._extract_key_insights(results),
            "risk_assessment": self._assess_risk(results),
            "opportunity_analysis": self._analyze_opportunities(results)
        }
        
        return report

    def _get_recommendation_level(self, score: int) -> str:
        """קביעת רמת המלצה"""
        if score >= 80:
            return "Strong Buy"
        elif score >= 60:
            return "Buy"
        elif score >= 40:
            return "Hold"
        elif score >= 20:
            return "Sell"
        else:
            return "Strong Sell"

    def _extract_key_insights(self, results: Dict) -> List[str]:
        """חילוץ תובנות מפתח"""
        insights = []
        
        # תובנות מ-NLP
        nlp_details = results.get("nlp_analyzer", {}).get("details", {})
        if "event_analysis" in nlp_details:
            events = nlp_details["event_analysis"].get("events", {})
            for event_type, event_list in events.items():
                if event_list:
                    insights.append(f"זוהו {len(event_list)} אירועי {event_type}")
        
        # תובנות מ-Event Scanner
        event_events = results.get("event_scanner", {}).get("events", {})
        for category, event_list in event_events.items():
            if event_list:
                insights.append(f"אירועי {category}: {len(event_list)} אירועים")
        
        # תובנות מ-Macro Scanner
        macro_details = results.get("macro_scanner", {}).get("details", {})
        if "trend_analysis" in macro_details:
            trends = macro_details["trend_analysis"]
            strong_trends = [k for k, v in trends.items() if v.get("trend_strength") == "strong"]
            if strong_trends:
                insights.append(f"מגמות חזקות: {', '.join(strong_trends)}")
        
        # תובנות מ-Hype Scanner
        hype_details = results.get("hype_scanner", {}).get("details", {})
        if "hype_analysis" in hype_details:
            hype_level = hype_details["hype_analysis"].get("hype_level", "none")
            if hype_level != "none":
                insights.append(f"רמת Hype: {hype_level}")
        
        return insights

    def _assess_risk(self, results: Dict) -> Dict:
        """הערכת סיכונים"""
        risk_factors = []
        risk_score = 0
        
        # סיכון לפי ציון נמוך
        overall_score = results.get("overall_score", 50)
        if overall_score < 30:
            risk_factors.append("ציון כולל נמוך מאוד")
            risk_score += 30
        elif overall_score < 50:
            risk_factors.append("ציון כולל נמוך")
            risk_score += 20
        
        # סיכון לפי סנטימנט שלילי
        nlp_sentiment = results.get("nlp_analyzer", {}).get("sentiment", "neutral")
        if nlp_sentiment in ["negative", "very_negative"]:
            risk_factors.append("סנטימנט חדשות שלילי")
            risk_score += 15
        
        # סיכון לפי מאקרו שלילי
        macro_sentiment = results.get("macro_scanner", {}).get("sentiment", "neutral")
        if macro_sentiment in ["bearish", "very_bearish"]:
            risk_factors.append("סביבה מאקרו שלילית")
            risk_score += 20
        
        # סיכון לפי hype קיצוני
        hype_score = results.get("hype_scanner", {}).get("score", 50)
        if hype_score > 90:
            risk_factors.append("Hype קיצוני - סיכון ל-FOMO")
            risk_score += 25
        
        return {
            "risk_score": min(100, risk_score),
            "risk_level": "high" if risk_score > 50 else "medium" if risk_score > 25 else "low",
            "risk_factors": risk_factors
        }

    def _analyze_opportunities(self, results: Dict) -> Dict:
        """ניתוח הזדמנויות"""
        opportunities = []
        opportunity_score = 0
        
        # הזדמנות לפי ציון גבוה
        overall_score = results.get("overall_score", 50)
        if overall_score > 70:
            opportunities.append("ציון כולל גבוה")
            opportunity_score += 25
        
        # הזדמנות לפי סנטימנט חיובי
        nlp_sentiment = results.get("nlp_analyzer", {}).get("sentiment", "neutral")
        if nlp_sentiment in ["positive", "very_positive"]:
            opportunities.append("סנטימנט חדשות חיובי")
            opportunity_score += 20
        
        # הזדמנות לפי מאקרו חיובי
        macro_sentiment = results.get("macro_scanner", {}).get("sentiment", "neutral")
        if macro_sentiment in ["bullish", "very_bullish"]:
            opportunities.append("סביבה מאקרו חיובית")
            opportunity_score += 20
        
        # הזדמנות לפי hype מתון
        hype_score = results.get("hype_scanner", {}).get("score", 50)
        if 50 < hype_score < 80:
            opportunities.append("Hype מתון - הזדמנות טובה")
            opportunity_score += 15
        
        return {
            "opportunity_score": min(100, opportunity_score),
            "opportunity_level": "high" if opportunity_score > 50 else "medium" if opportunity_score > 25 else "low",
            "opportunities": opportunities
        }

    def get_portfolio_analysis(self, symbols: List[str]) -> Dict:
        """
        ניתוח תיק השקעות
        
        Args:
            symbols: רשימת סמלי מניות
            
        Returns:
            Dict עם ניתוח התיק
        """
        portfolio_results = {}
        
        for symbol in symbols:
            try:
                result = self.analyze_stock(symbol)
                portfolio_results[symbol] = result
            except Exception as e:
                self.log(f"Error analyzing {symbol}: {e}")
                portfolio_results[symbol] = {"error": str(e)}
        
        # חישוב סטטיסטיקות תיק
        scores = [r.get("overall_score", 50) for r in portfolio_results.values() if "error" not in r]
        
        portfolio_summary = {
            "total_stocks": len(symbols),
            "average_score": int(np.mean(scores)) if scores else 50,
            "best_performer": max(portfolio_results.items(), key=lambda x: x[1].get("overall_score", 0))[0] if portfolio_results else None,
            "worst_performer": min(portfolio_results.items(), key=lambda x: x[1].get("overall_score", 100))[0] if portfolio_results else None,
            "buy_recommendations": [s for s, r in portfolio_results.items() if r.get("overall_score", 0) >= 60],
            "sell_recommendations": [s for s, r in portfolio_results.items() if r.get("overall_score", 0) < 40]
        }
        
        return {
            "portfolio_results": portfolio_results,
            "portfolio_summary": portfolio_summary
        }

    def export_report(self, results: Dict, format: str = "json") -> str:
        """
        ייצוא דוח
        
        Args:
            results: תוצאות הניתוח
            format: פורמט ייצוא (json, csv, txt)
            
        Returns:
            נתיב לקובץ המיוצא
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        symbol = results.get("symbol", "UNKNOWN")
        
        if format == "json":
            filename = f"report_{symbol}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        elif format == "txt":
            filename = f"report_{symbol}_{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self._format_text_report(results))
        
        self.log(f"Report exported to {filename}")
        return filename

    def _format_text_report(self, results: Dict) -> str:
        """עיצוב דוח טקסט"""
        symbol = results.get("symbol", "UNKNOWN")
        overall_score = results.get("overall_score", 0)
        
        report = f"""
=== דוח ניתוח מניית {symbol} ===
תאריך: {results.get("timestamp", "Unknown")}

ציון כולל: {overall_score}/100
המלצה: {self._get_recommendation_level(overall_score)}

=== ציוני סוכנים ===
"""
        
        agent_scores = results.get("detailed_report", {}).get("agent_scores", {})
        for agent, score in agent_scores.items():
            report += f"{agent}: {score}/100\n"
        
        report += f"\n=== המלצות ===\n"
        recommendations = results.get("recommendations", [])
        for rec in recommendations:
            report += f"- {rec}\n"
        
        report += f"\n=== התראות ===\n"
        alerts = results.get("alerts", [])
        for alert in alerts:
            report += f"- {alert['message']} ({alert['severity']})\n"
        
        return report 

def run_dashboard(symbols: List[str] = None, config: Dict = None) -> Dict:
    """
    הרצת הדשבורד הראשי
    
    Args:
        symbols: רשימת סמלי מניות לניתוח
        config: הגדרות נוספות
        
    Returns:
        Dict עם תוצאות הניתוח
    """
    try:
        dashboard = MainDashboard(config)
        
        if symbols is None:
            symbols = ['AAPL', 'MSFT', 'GOOGL']  # ברירת מחדל
        
        results = {}
        for symbol in symbols:
            results[symbol] = dashboard.analyze_stock(symbol)
        
        # ניתוח תיק השקעות אם יש יותר ממניה אחת
        if len(symbols) > 1:
            portfolio_analysis = dashboard.get_portfolio_analysis(symbols)
            results['portfolio'] = portfolio_analysis
        
        return results
        
    except Exception as e:
        print(f"Error running dashboard: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # הרצה לדוגמה
    results = run_dashboard(['AAPL', 'MSFT'])
    print(json.dumps(results, indent=2, default=str)) 