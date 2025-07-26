from utils import data_fetcher
from core.gap_detector_ultimate import GapDetectorUltimate  # או השם של הקובץ/קלאס שלך

symbol = "TSLA"  # תוכל לבדוק גם AAPL, MSFT, וכו'
price_df = data_fetcher.get_price_history(symbol, period="6mo", interval="1d")

if price_df is None or price_df.empty:
    print("שגיאה: לא התקבלו נתוני מחיר")
else:
    agent = GapDetectorUltimate()  # ודא שאתה משתמש בשם הקלאס/קובץ הנכון
    score = agent.analyze(symbol, price_df)
    print(f"Gap Ultimate Score for {symbol}: {score}")
