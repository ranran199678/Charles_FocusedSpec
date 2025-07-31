import time
import sys
import threading
import os
import json
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_fetcher import DataFetcher
from core.trend_shift_detector import TrendShiftDetector
from core.bollinger_squeeze import BollingerSqueeze
from core.breakout_retest_recognizer import BreakoutRetestRecognizer

# רשימת הסוכנים הפעילים
agent_classes = {
    "TrendShiftDetector": TrendShiftDetector,
    "BollingerSqueezeAgent": BollingerSqueeze,
    "BreakoutRetestRecognizer": BreakoutRetestRecognizer,
}

# פונקציה לשמירת הפלט לקובץ JSON
def save_live_output(symbol, agent_name, result):
    output_dir = Path("live/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{agent_name}_{symbol}_live.json"
    filepath = output_dir / filename

    try:
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "agent": agent_name,
            "result": result
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, default=str)
    except Exception as e:
        print(f"❌ שגיאה בשמירת קובץ JSON עבור {agent_name}: {e}")

# פונקציית הרצת סוכן בלייב
def run_agent_live(agent_name, agent_class, symbol, interval, delay):
    fetcher = DataFetcher()

    try:
        if agent_name == "TrendShiftDetector":
            agent = agent_class(symbol, interval=interval, live_mode=True, frequency_sec=delay)
        else:
            agent = agent_class(symbol)
    except Exception as e:
        print(f"❌ שגיאה באתחול {agent_name}: {e}")
        return

    while True:
        try:
            batch = fetcher.fetch_prices_batch([symbol], interval)
            if not batch:
                print(f"⚠️ [FETCH ERROR] לא הוחזרו נתונים כלל מהפונקציה fetch_prices_batch עבור {symbol}")
                time.sleep(delay)
                continue

            price_data = batch.get(symbol)
            if price_data is None:
                print(f"⚠️ [None] הנתונים עבור {symbol} לא נמצאו ב־batch או ריקים")
                time.sleep(delay)
                continue

            if price_data.empty:
                print(f"❌ [{symbol}] לא נמצאו נתונים (DataFrame ריק)")
            else:
                print(f"📊 DEBUG: נתונים גולמיים עבור {symbol} ({interval}):\n{price_data.head()}\n")
                print(f"\n⚡ הרצה | סוכן: {agent_name} | סימבול: {symbol} | אינטרוול: {interval}")
                if hasattr(agent, "run_live"):
                    if agent_name == "TrendShiftDetector":
                        result = agent.run_live(symbol, price_data)
                    else:
                        result = agent.run_live(price_data)
                elif hasattr(agent, "run"):
                    result = agent.run()
                elif hasattr(agent, "analyze"):
                    result = agent.analyze(symbol, price_data)
                else:
                    print(f"⚠️ לסוכן {agent_name} אין פונקציה מתאימה (run/run_live/analyze)")
                    continue

                print(result)
                save_live_output(symbol, agent_name, result)

        except Exception as e:
            print(f"❌ [{symbol}] שגיאה בסוכן {agent_name}: {e}")

        time.sleep(delay)

# פונקציה ראשית
def main():
    print("🎯 מצב לייב – הרצת סוכנים לפי בחירה")
    symbols = input("📥 הזן סימבולים (מופרדים בפסיקים, לדו' QBTS,NVDA): ").split(",")
    interval = input("⏱️ הזן אינטרוול (1min, 5min, 1day): ").strip()
    delay = input("⏲️ כל כמה שניות לבצע הרצה? (ברירת מחדל: 60): ").strip()
    delay = int(delay) if delay else 60

    print(f"\n🚀 מריץ את הסוכנים: {', '.join(symbols)} | אינטרוול: {interval} | כל {delay} שניות")
    print("🛑 לחץ Enter כדי לעצור את כל הסוכנים...")

    threads = []
    for symbol in symbols:
        symbol = symbol.strip().upper()
        for name, cls in agent_classes.items():
            thread = threading.Thread(target=run_agent_live, args=(name, cls, symbol, interval, delay))
            thread.daemon = True
            thread.start()
            threads.append(thread)

    input()
    print("✅ כל הסוכנים נעצרו. להתראות!")

if __name__ == "__main__":
    main()
