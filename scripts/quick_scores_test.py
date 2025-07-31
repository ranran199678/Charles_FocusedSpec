from core.alpha_score_engine import AlphaScoreEngine
import pandas as pd
import numpy as np

# יצירת נתונים
dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
prices = [100 + i * 0.5 + np.random.normal(0, 2) for i in range(len(dates))]
volumes = [1000000 + np.random.normal(0, 200000) for i in range(len(dates))]

df = pd.DataFrame({
    'Open': [p * 0.99 for p in prices],
    'High': [p * 1.02 for p in prices], 
    'Low': [p * 0.98 for p in prices],
    'Close': prices,
    'Volume': volumes
}, index=dates)

# הרצת מנוע
engine = AlphaScoreEngine()
result = engine.evaluate('TEST', df)

print('ציון סופי:', result.get('final_score'))
print('מספר סוכנים:', result.get('agents_count'))
print()

scores = result.get('agent_scores', {})
print('ציוני סוכנים:')
for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    print(f'{name}: {score}') 