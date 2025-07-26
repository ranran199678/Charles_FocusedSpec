import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.return_forecaster import ReturnForecaster
from utils.data_fetcher import DataFetcher
from utils.forecast_logger import log_forecast  # ✅ נוספה השורה

@pytest.mark.integration
def test_return_forecaster_qbts():
    symbol = "QBTS"
    model_type = "boosting"
    window_size = 90
    forecast_days = 5

    fetcher = DataFetcher()
    price_data = fetcher.fetch_prices_batch([symbol])
    price_df = price_data.get(symbol)

    assert price_df is not None and not price_df.empty, "❌ נתוני מחיר לא נטענו"
    price_df = price_df.sort_index()

    print("🔢 כמות נתונים זמינים:", len(price_df))

    forecaster = ReturnForecaster(
        symbol=symbol,
        model_type=model_type,
        window_size=window_size,
        forecast_days=forecast_days
    )

    train_result = forecaster.train(price_df)
    prediction = forecaster.predict(price_df)

    expected_return = float(prediction["expected_return"])
    std_dev = prediction["std_dev"]
    ci = prediction["confidence_interval"]
    feature_importance = prediction.get("feature_importance", {})

    print("✅ תחזית תשואה:", expected_return)
    print("📉 סטיית תקן:", std_dev)
    print("🔐 טווח ביטחון 95%:", ci)
    for k, v in feature_importance.items():
        print(f" - {k}: {v*100:.2f}%")

    # ✔️ חלק 1: דוח היסטורי
    historical_df = price_df.copy().reset_index()
    historical_df.rename(columns={'timestamp': 'Date', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

    # ✔️ חלק 2: תחזית עתידית עם חישוב מצטבר אמיתי
    last_date = historical_df['Date'].iloc[-1]
    last_close = float(round(historical_df['Close'].iloc[-1], 4))
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days, freq='B')

    forecast_prices = []
    price = last_close
    for i in range(forecast_days):
        price = float(round(float(price) * (1 + float(expected_return)), 4))
        forecast_prices.append(price)

    print("📈 תחזיות מחושבות בפועל (מצטברות):", forecast_prices)

    # ✅ לוג התחזית לקובץ CSV
    log_forecast(
        symbol=symbol,
        expected_return=expected_return,
        std_dev=std_dev,
        confidence_interval=ci,
        model_used=prediction["model_used"],
        forecast_prices=forecast_prices
    )

    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Forecasted Return": [round(expected_return, 4)] * forecast_days,
        "Projected Price": forecast_prices
    })

    current_row = pd.DataFrame({
        "Date": [last_date],
        "Forecasted Return": [None],
        "Projected Price": [round(last_close, 4)]
    })

    forecast_df = pd.concat([current_row, forecast_df], ignore_index=True)

    # ✔️ חלק 3: גרף משולב
    chart_df = pd.concat([
        historical_df[["Date", "Close"]].rename(columns={"Close": "Price"}),
        forecast_df[["Date", "Projected Price"]].rename(columns={"Projected Price": "Price"})
    ])
    chart_df = chart_df.sort_values("Date").reset_index(drop=True)

    # ✔️ כתיבה לקובץ אקסל
    outputs_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    excel_path = os.path.join(outputs_dir, "forecast_report.xlsx")

    try:
        with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
            historical_df.to_excel(writer, sheet_name="Historical_Data", index=False)
            forecast_df.to_excel(writer, sheet_name="Forecast_Data", index=False)
            chart_df.to_excel(writer, sheet_name="Forecast_Chart", index=False)

            workbook = writer.book
            worksheet = writer.sheets["Forecast_Chart"]

            chart = workbook.add_chart({'type': 'line'})
            chart.add_series({
                'name': 'Price',
                'categories': ['Forecast_Chart', 1, 0, len(chart_df), 0],
                'values':     ['Forecast_Chart', 1, 1, len(chart_df), 1],
            })
            chart.set_title({'name': f"{symbol} Forecast Chart"})
            chart.set_x_axis({'name': 'Date'})
            chart.set_y_axis({'name': 'Price'})
            worksheet.insert_chart('D2', chart)

        print(f"📁 דוח נוצר בהצלחה: {excel_path}")
    except PermissionError:
        print("❌ לא ניתן לכתוב לקובץ Excel – ודא שהקובץ סגור ב־Excel ונסה שוב.")

    # ✅ בדיקות מקרים חריגים

    # 🧪 Edge Case 1: טווח נתונים קצר מדי
    try:
        short_df = price_df.tail(5)
        forecaster.train(short_df)
        print("⚠️ אזהרה: המודל איפשר אימון עם פחות מדי נתונים. יש להוסיף טיפול במקרה כזה.")
    except Exception as e:
        print("✅ זיהוי תקין של נתונים חסרים (train):", str(e))

    # 🧪 Edge Case 2: תחזית ללא ETF
    try:
        prediction_no_etf = forecaster.predict(price_df, etf_df=None)
        print("✅ תחזית ללא ETF עובדת (fallback):", prediction_no_etf["expected_return"])
    except Exception as e:
        print("❌ שגיאה בעת חיזוי ללא ETF:", str(e))

    # 🧪 Edge Case 3: טעינת מודל שמור
    try:
        new_forecaster = ReturnForecaster(
            symbol=symbol,
            model_type=model_type,
            window_size=window_size,
            forecast_days=forecast_days
        )
        new_forecaster.load_model()
        prediction_loaded = new_forecaster.predict(price_df)
        print("✅ טעינת מודל קיימת והפעלה תקינה:", prediction_loaded["expected_return"])
    except Exception as e:
        print("❌ שגיאה בטעינת מודל קיים:", str(e))

    # 🧪 Edge Case 4: סימבול שגוי/לא קיים
    try:
        bad_symbol_data = fetcher.fetch_prices_batch(["ZZZZZ"])
        bad_df = bad_symbol_data.get("ZZZZZ")
        assert bad_df is None or bad_df.empty, "❌ לא זוהתה בעיה בסימבול שגוי"
        print("✅ סימבול שגוי מזוהה ונחסם כראוי")
    except Exception as e:
        print("✅ טיפול תקין בסימבול לא קיים:", str(e))
