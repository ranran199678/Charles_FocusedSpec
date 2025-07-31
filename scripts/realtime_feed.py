import websocket
import json
import pandas as pd
import time
import threading

from utils import data_fetcher
from core.alpha_score_engine import AlphaScoreEngine

# מפתחות API (Finnhub)
FINNHUB_KEY = "d1in1ahr01qhbuvr1dggd1in1ahr01qhbuvr1dh0"

# רשימת סימולים
SYMBOLS = ["QBTS"]

# פרמטר: כל כמה שניות לבצע הערכה מחודשת (מניעת יותר מדי קריאות API)
EVAL_INTERVAL_SEC = 120

# זיכרון מתי כל סימול נבדק לאחרונה
last_evaluated = {}

# טוען קונפיגורציה
with open("config/settings.json", "r") as f:
    config = json.load(f)

engine = AlphaScoreEngine(config)

def evaluate_symbol(symbol):
    try:
        price_df = data_fetcher.get_price_data(symbol, interval="1day", outputsize=100)
        result = engine.evaluate(symbol, price_df)
        print(f"[{symbol}] AlphaScore: {result['score']} | {result['recommendation']}")
        # כאן אפשר להוסיף: שליחת התראה/מייל/וואטסאפ וכו׳ אם התוצאה היא קניה חזקה!
        if result['recommendation'].startswith("HIGH"):
            print(f"🚨🚨 SIGNAL: {symbol} = STRONG BUY 🚨🚨")
        return result
    except Exception as e:
        print(f"Error evaluating {symbol}: {e}")

def on_message(ws, message):
    data = json.loads(message)
    if data.get("type") == "trade":
        for trade in data["data"]:
            symbol = trade['s']
            print(f"Live trade: {symbol} | Price: {trade['p']} | Volume: {trade['v']}")
            # נבדוק אם עבר מספיק זמן מאז ההערכה האחרונה
            now = time.time()
            if symbol not in last_evaluated or now - last_evaluated[symbol] > EVAL_INTERVAL_SEC:
                threading.Thread(target=evaluate_symbol, args=(symbol,)).start()
                last_evaluated[symbol] = now

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    # נרשם לקבלת עדכונים
    for sym in SYMBOLS:
        ws.send(json.dumps({"type": "subscribe", "symbol": sym}))
    print(f"Subscribed to real-time data for: {SYMBOLS}")

if __name__ == "__main__":
    socket_url = f"wss://ws.finnhub.io?token={FINNHUB_KEY}"
    ws_app = websocket.WebSocketApp(socket_url,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
    print("Connecting to Finnhub WebSocket...")
    ws_app.run_forever()
