import pandas as pd
import pytest
from core.adx_score_agent import ADXScoreAgent

def make_sample_df():
    # נתונים סינתטיים עם מגמה ברורה
    data = {
        "high": [100, 102, 105, 107, 110, 112, 115, 117, 120, 122, 125, 127, 130, 132, 135],
        "low": [95, 97, 100, 102, 105, 107, 110, 112, 115, 117, 120, 122, 125, 127, 130],
        "close": [98, 101, 104, 106, 109, 111, 114, 116, 119, 121, 124, 126, 129, 131, 134]
    }
    return pd.DataFrame(data)

def test_adx_score_agent_basic():
    df = make_sample_df()
    agent = ADXScoreAgent()
    result = agent.analyze("AAPL", df)
    assert isinstance(result, dict)
    assert result["symbol"] == "AAPL"
    assert result["agent_name"] == "ADXScoreAgent"
    assert "score" in result
    assert "explanation" in result
    assert "details" in result
    # בדוק שהציון הגיוני
    assert 0 <= result["score"] <= 100
    # בדוק שההסבר כולל ADX
    assert "ADX" in result["explanation"]

def test_adx_score_agent_missing_columns():
    df = pd.DataFrame({"close": [1,2,3]})
    agent = ADXScoreAgent()
    result = agent.analyze("MSFT", df)
    assert result["score"] == 1
    assert "חסרים" in result["explanation"]

def test_adx_score_agent_multi_timeframe():
    df_daily = make_sample_df()
    df_weekly = make_sample_df().iloc[-7:].reset_index(drop=True)
    agent = ADXScoreAgent()
    result = agent.analyze("TSLA", df_daily, price_df_weekly=df_weekly)
    assert "all_timeframes" in result
    assert "daily" in result["all_timeframes"]
    assert "weekly" in result["all_timeframes"]
    assert result["all_timeframes"]["weekly"]["details"]["timeframe"] == "weekly" 

def test_adx_score_agent_real_data_utils():
    try:
        from utils.data_fetcher import DataFetcher
    except ImportError:
        pytest.skip("DataFetcher לא קיים במערכת")
    fetcher = DataFetcher()
    # ננסה למשוך נתונים עדכניים (3 חודשים אחרונים)
    df = fetcher.fetch_prices_batch(["QBTS"], interval="1day")["QBTS"]
    assert df is not None and not df.empty, "לא התקבלו נתונים אמיתיים מ-DataFetcher"
    # סינון ל-90 הימים האחרונים (אם יש)
    if len(df) > 90:
        df = df.tail(90)
    # התאמה לשמות עמודות (אם צריך)
    if set(["high", "low", "close"]).issubset(df.columns):
        df = df
    elif set(["High", "Low", "Close"]).issubset(df.columns):
        df = df.rename(columns={"High": "high", "Low": "low", "Close": "close"})
    else:
        pytest.fail("העמודות הדרושות לא קיימות ב-DataFrame")
    print("\n--- טווח תאריכים של הנתונים שנשלפו ל-QBTS ---")
    print(f"מתאריך: {df.index.min()} עד {df.index.max()} (סה\"כ {len(df)} ימים)")
    print(df.tail(10))
    agent = ADXScoreAgent()
    result = agent.analyze("QBTS", df)
    print("\n--- פלט ADX אמיתי QBTS ---")
    print(result)
    assert isinstance(result, dict)
    assert result["symbol"] == "QBTS"
    assert "score" in result
    assert result["score"] > 1
    assert "explanation" in result 

def test_adx_score_agent_real_data_yfinance():
    try:
        import yfinance as yf
    except ImportError:
        pytest.skip("yfinance לא מותקן")
    df = yf.download("QBTS", period="3mo", interval="1d")
    assert df is not None and not df.empty, "לא התקבלו נתונים מ-yfinance"
    # התאמה לשמות עמודות
    if set(["High", "Low", "Close"]).issubset(df.columns):
        df = df.rename(columns={"High": "high", "Low": "low", "Close": "close"})
    print("\n--- טווח תאריכים של הנתונים שנשלפו ל-QBTS (yfinance) ---")
    print(f'מתאריך: {df.index.min()} עד {df.index.max()} (סה"כ {len(df)} ימים)')
    print(df.tail(10)[["high", "low", "close"]])
    agent = ADXScoreAgent()
    result = agent.analyze("QBTS", df)
    print("\n--- פלט ADX אמיתי QBTS (yfinance) ---")
    print(result)
    assert isinstance(result, dict)
    assert result["symbol"] == "QBTS"
    assert "score" in result
    assert result["score"] > 1
    assert "explanation" in result 