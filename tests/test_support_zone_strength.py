import os
import pandas as pd
import matplotlib.pyplot as plt
from utils import data_fetcher
from core.support_zone_strength_detector import SupportResistanceZoneStrengthDetector

os.environ["TRANSFORMERS_VERIFIED_TOKEN"] = "true"
import transformers
import logging
import requests

transformers.logging.set_verbosity_error()

original_DataFetcher = data_fetcher.DataFetcher
class PatchedDataFetcher(original_DataFetcher):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except Exception as e:
            print("\u26a0\ufe0f לא ניתן לטעון מודלים מ-huggingface (המשך ללא ניתוח סנטימנט וסיכום)")
            from utils.credentials import APICredentials
            self.session = requests.Session()
            self.price_cache = {}
            self.fundamentals_cache = {}
            self.news_cache = {}
            self.finnhub_key = APICredentials.get_finnhub_key()
            self.fmp_key = APICredentials.get_fmp_key()
            self.twelve_key = APICredentials.get_twelve_key()
            self.sentiment_classifier = lambda text: [{"label": "neutral", "score": 0.0}]
            self.summarizer = lambda text, **kwargs: [{"summary_text": text[:60]}]

def main():
    symbol = input("הכנס סימבול של מניה (למשל QBTS): ").strip().upper()
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    fetcher = PatchedDataFetcher()
    print(f"[DEBUG] FMP_KEY: {fetcher.fmp_key}")
    print(f"[DEBUG] FINNHUB_KEY: {fetcher.finnhub_key}")
    print(f"[DEBUG] TWELVE_KEY: {fetcher.twelve_key}")
    price_data = fetcher.fetch_prices_batch([symbol])
    print(f"[DEBUG] תוצאה מ-fetch_prices_batch: {price_data}")
    price_df = price_data.get(symbol)

    if price_df is None:
        raise ValueError(f"שגיאה: לא נמצאו נתונים עבור {symbol}")

    price_df = price_df.reset_index()
    if 'timestamp' in price_df.columns:
        price_df = price_df.rename(columns={"timestamp": "date"})
    elif 'index' in price_df.columns:
        price_df = price_df.rename(columns={"index": "date"})

    for col in ['low', 'high', 'open']:
        if col not in price_df.columns:
            price_df[col] = price_df['close']

    if 'date' not in price_df.columns:
        raise ValueError("שגיאה: price_df חסר עמודת date לאחר reset_index()")
    if not pd.api.types.is_datetime64_any_dtype(price_df['date']):
        price_df['date'] = pd.to_datetime(price_df['date'], errors='coerce')

    start_input = input("הכנס תאריך התחלה (YYYY-MM-DD): ")
    end_input = input("הכנס תאריך סיום (YYYY-MM-DD): ")
    try:
        start_date = pd.to_datetime(start_input)
        end_date = pd.to_datetime(end_input)
        if start_date > end_date:
            raise ValueError("תאריך התחלה לא יכול להיות אחרי תאריך סיום.")
        price_df = price_df[(price_df['date'] >= start_date) & (price_df['date'] <= end_date)]
        print(f"[DEBUG] טווח תאריכים לאחר סינון: {start_date.date()} - {end_date.date()}")
        if price_df.empty:
            raise ValueError("לא נמצאו נתונים בטווח התאריכים שנבחר.")
    except Exception as e:
        raise ValueError(f"תאריכים לא תקינים או טווח ריק: {e}")

    filtered_df = price_df.copy().reset_index(drop=True)
    print("[DEBUG] טווח מחירים שנותחו:")
    print(filtered_df[['date', 'close']].head())
    print(filtered_df[['date', 'close']].tail())
    print(f"[DEBUG] מחיר סגירה מינימלי: {filtered_df['close'].min()} | מקסימלי: {filtered_df['close'].max()}")

    agent = SupportResistanceZoneStrengthDetector({
        "window": 80,
        "min_touches": 2,
        "sensitivity": 0.012,
        "profile_radius": 0.012,
        "min_score": 30,
        "plot": False
    })
    result = agent.analyze(symbol, filtered_df)

    supp_df = pd.DataFrame(result["support_zones"])
    res_df  = pd.DataFrame(result["resistance_zones"])

    for df in [supp_df, res_df]:
        for col in ['score', 'level']:
            if col not in df.columns:
                df[col] = pd.NA

    min_score = agent.min_score
    supp_strong = supp_df[supp_df['score'] >= min_score]
    supp_weak   = supp_df[supp_df['score'] < min_score]
    res_strong  = res_df[res_df['score'] >= min_score]
    res_weak    = res_df[res_df['score'] < min_score]

    excel_path = f"outputs/zones_results_{symbol}.xlsx"
    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        supp_df.to_excel(writer, sheet_name="Support Zones", index=False)
        res_df.to_excel(writer, sheet_name="Resistance Zones", index=False)

        try:
            date_range = f"{filtered_df['date'].min().date()} - {filtered_df['date'].max().date()}"
        except Exception:
            date_range = "תאריכים לא זמינים"

        summary_lines = [
            f"מספר אזורי תמיכה חזקים: {len(supp_strong)}",
            f"מספר אזורי תמיכה חלשים: {len(supp_weak)}",
            f"מספר אזורי התנגדות חזקים: {len(res_strong)}",
            f"מספר אזורי התנגדות חלשים: {len(res_weak)}",
            f"שמות מניה: {symbol}",
            f"תקופת ניתוח: {date_range}"
        ]
        summary_text = "\n".join(summary_lines)
        summary_df = pd.DataFrame({"Summary": [summary_text]})
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(filtered_df['date'], filtered_df['close'], label='Close', color='black')
        for lvl in supp_strong['level'].dropna():
            ax.axhline(lvl, color='green', linestyle='--', alpha=0.7, label='Support')
        for lvl in res_strong['level'].dropna():
            ax.axhline(lvl, color='red', linestyle='--', alpha=0.7, label='Resistance')
        ax.set_title(f"סיכום רמות תמיכה/התנגדות ל-{symbol}")
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())
        plt.tight_layout()
        plot_path = f"outputs/zones_summary_plot_{symbol}.png"
        plt.savefig(plot_path)
        plt.close(fig)

        worksheet = writer.sheets["Summary"]
        worksheet.insert_image('B4', plot_path)

    print(f"\nהקובץ {excel_path} נוצר בהצלחה! כולל תמיכה/התנגדות וסיכום.")

if __name__ == "__main__":
    main()
