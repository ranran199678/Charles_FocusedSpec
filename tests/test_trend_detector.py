# test_trend_detector.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from core.trend_detector import TrendDetector

detector = TrendDetector(short_window=20, long_window=50)

# טסט 1: מגמה עולה עם ווליום גבוה
data_uptrend = {
    'close': [i + (i * 0.01) for i in range(1, 101)],
    'volume': [100000] * 95 + [150000] * 5
}
df_uptrend = pd.DataFrame(data_uptrend)
result1 = detector.run(df_uptrend)
print("--- מגמה עולה ---")
print(f"מגמה: {result1['trend']}, ציון: {result1['score']}, ווליום חזק: {result1['volume_boost']}")

# טסט 2: מגמה יורדת עם ווליום גבוה
data_downtrend = {
    'close': [100 - (i * 0.5) for i in range(100)],
    'volume': [80000] * 95 + [120000] * 5
}
df_downtrend = pd.DataFrame(data_downtrend)
result2 = detector.run(df_downtrend)
print("--- מגמה יורדת ---")
print(f"מגמה: {result2['trend']}, ציון: {result2['score']}, ווליום חזק: {result2['volume_boost']}")

# טסט 3: דאטה קצר מדי
short_data = {
    'close': [10, 11, 12],
    'volume': [100000, 105000, 110000]
}
df_short = pd.DataFrame(short_data)
result3 = detector.run(df_short)
print("--- נתונים חסרים ---")
print(f"מגמה: {result3['trend']}, ציון: {result3['score']}")
