import requests
import pandas as pd
from datetime import datetime, timedelta

symbol = "AAPL"

# משוך את כל נתוני 1min של 2 ימים אחורה (למקרה שהיום הוא לא יום מסחר)
end_dt = datetime.now()
start_dt = end_dt - timedelta(days=2)
start_ts = int(start_dt.timestamp())
end_ts = int(end_dt.timestamp())

url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1m"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

response = requests.get(url, headers=headers, timeout=10)
data = response.json()

try:
    timestamps = data['chart']['result'][0]['timestamp']
    indicators = data['chart']['result'][0]['indicators']['quote'][0]
    df = pd.DataFrame(indicators)
    df['timestamp'] = pd.to_datetime(timestamps, unit='s')
    df.set_index('timestamp', inplace=True)
    # מצא את יום המסחר האחרון
    last_day = df.index.date[-1]
    df_last_day = df[df.index.date == last_day]
    # קח את 59 הדקות האחרונות של אותו יום
    df_last_59 = df_last_day.tail(59)
    print(df_last_59)
except Exception as e:
    print("שגיאה בשליפת נתונים:", e)