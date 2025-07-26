import os
import csv
from datetime import datetime

def log_forecast(symbol, expected_return, std_dev, confidence_interval, model_used, forecast_prices, run_date=None):
    """
    שומר תחזית תחזיות לקובץ CSV מתגלגל – עבור כל הרצה.

    :param symbol: סימול המניה (למשל: 'QBTS')
    :param expected_return: תחזית תשואה (float)
    :param std_dev: סטיית תקן של התחזית
    :param confidence_interval: טווח ביטחון [low, high]
    :param model_used: שם המודל (למשל 'boosting')
    :param forecast_prices: רשימת מחירים חזויים לימים הקרובים
    :param run_date: תאריך הריצה (אם לא מוגדר – יילקח אוטומטית עכשיו)
    """
    run_date = run_date or datetime.now().strftime("%Y-%m-%d")
    ci_low, ci_high = confidence_interval

    # הגדרת התיקייה והקובץ
    log_dir = os.path.join(os.path.dirname(__file__), "..", "outputs", "forecast_logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "forecast_log.csv")

    # יצירת כותרת (אם הקובץ לא קיים)
    file_exists = os.path.exists(log_file)
    num_days = len(forecast_prices)

    with open(log_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        if not file_exists:
            headers = [
                "timestamp", "symbol", "expected_return", "std_dev", "ci_low", "ci_high", "model"
            ] + [f"day_{i+1}_price" for i in range(num_days)]
            writer.writerow(headers)

        row = [
            run_date, symbol, round(expected_return, 6), round(std_dev, 6),
            round(ci_low, 6), round(ci_high, 6), model_used
        ] + [round(p, 4) for p in forecast_prices]

        writer.writerow(row)

    print(f"📝 התחזית נשמרה בהצלחה בקובץ: {log_file}")
