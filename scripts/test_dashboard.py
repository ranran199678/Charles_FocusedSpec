import sys
sys.path.append('.')

from dashboard.main_dashboard import MainDashboard

# בדיקת Dashboard
print("=== בדיקת Main Dashboard ===")

# יצירת מופע
dashboard = MainDashboard()

# בדיקת מניה בודדת
test_symbol = "AAPL"
print(f"\n=== ניתוח מפורט עבור {test_symbol} ===")

try:
    result = dashboard.analyze_stock(test_symbol)
    
    print(f"סמל: {result.get('symbol', 'Unknown')}")
    print(f"ציון כולל: {result.get('overall_score', 0)}/100")
    print(f"תאריך: {result.get('timestamp', 'Unknown')}")
    
    # פרטי הסוכנים
    print(f"\n=== ציוני סוכנים ===")
    agent_scores = result.get("detailed_report", {}).get("agent_scores", {})
    for agent, score in agent_scores.items():
        print(f"{agent:25}: {score}/100")
    
    # ניתוח סנטימנט
    print(f"\n=== ניתוח סנטימנט ===")
    sentiment_analysis = result.get("detailed_report", {}).get("sentiment_analysis", {})
    for source, sentiment in sentiment_analysis.items():
        print(f"{source:15}: {sentiment}")
    
    # תובנות מפתח
    print(f"\n=== תובנות מפתח ===")
    key_insights = result.get("detailed_report", {}).get("key_insights", [])
    for insight in key_insights:
        print(f"- {insight}")
    
    # הערכת סיכונים
    print(f"\n=== הערכת סיכונים ===")
    risk_assessment = result.get("detailed_report", {}).get("risk_assessment", {})
    print(f"ציון סיכון: {risk_assessment.get('risk_score', 0)}/100")
    print(f"רמת סיכון: {risk_assessment.get('risk_level', 'unknown')}")
    risk_factors = risk_assessment.get('risk_factors', [])
    for factor in risk_factors:
        print(f"- {factor}")
    
    # ניתוח הזדמנויות
    print(f"\n=== ניתוח הזדמנויות ===")
    opportunity_analysis = result.get("detailed_report", {}).get("opportunity_analysis", {})
    print(f"ציון הזדמנות: {opportunity_analysis.get('opportunity_score', 0)}/100")
    print(f"רמת הזדמנות: {opportunity_analysis.get('opportunity_level', 'unknown')}")
    opportunities = opportunity_analysis.get('opportunities', [])
    for opportunity in opportunities:
        print(f"- {opportunity}")
    
    # המלצות
    print(f"\n=== המלצות ===")
    recommendations = result.get("recommendations", [])
    for rec in recommendations:
        print(f"- {rec}")
    
    # התראות
    print(f"\n=== התראות ===")
    alerts = result.get("alerts", [])
    if alerts:
        for alert in alerts:
            severity = alert.get('severity', 'unknown')
            message = alert.get('message', 'Unknown alert')
            print(f"[{severity.upper()}] {message}")
    else:
        print("אין התראות")
    
except Exception as e:
    print(f"שגיאה בניתוח {test_symbol}: {e}")

# בדיקת ניתוח תיק השקעות
print(f"\n=== ניתוח תיק השקעות ===")
portfolio_symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]

try:
    portfolio_result = dashboard.get_portfolio_analysis(portfolio_symbols)
    
    summary = portfolio_result.get("portfolio_summary", {})
    print(f"סה\"כ מניות: {summary.get('total_stocks', 0)}")
    print(f"ציון ממוצע: {summary.get('average_score', 0)}/100")
    print(f"הביצוע הטוב ביותר: {summary.get('best_performer', 'Unknown')}")
    print(f"הביצוע הגרוע ביותר: {summary.get('worst_performer', 'Unknown')}")
    
    buy_recs = summary.get('buy_recommendations', [])
    if buy_recs:
        print(f"המלצות קנייה: {', '.join(buy_recs)}")
    
    sell_recs = summary.get('sell_recommendations', [])
    if sell_recs:
        print(f"המלצות מכירה: {', '.join(sell_recs)}")
    
    # פירוט כל מניה
    print(f"\n=== פירוט מניות ===")
    portfolio_results = portfolio_result.get("portfolio_results", {})
    for symbol, result in portfolio_results.items():
        if "error" not in result:
            score = result.get("overall_score", 0)
            recommendation = dashboard._get_recommendation_level(score)
            print(f"{symbol:6}: {score:3d}/100 - {recommendation}")
        else:
            print(f"{symbol:6}: שגיאה - {result.get('error', 'Unknown error')}")
    
except Exception as e:
    print(f"שגיאה בניתוח תיק: {e}")

# בדיקת ייצוא דוח
print(f"\n=== ייצוא דוח ===")
try:
    # ניתוח מניה לבדיקה
    test_result = dashboard.analyze_stock("TSLA")
    
    # ייצוא ל-JSON
    json_file = dashboard.export_report(test_result, "json")
    print(f"דוח JSON נוצר: {json_file}")
    
    # ייצוא ל-TXT
    txt_file = dashboard.export_report(test_result, "txt")
    print(f"דוח TXT נוצר: {txt_file}")
    
except Exception as e:
    print(f"שגיאה בייצוא דוח: {e}")

print(f"\n=== סיום בדיקת Dashboard ===") 