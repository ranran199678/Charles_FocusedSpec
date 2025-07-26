# utils/credentials.py

import os
from dotenv import load_dotenv

# טען משתנים מתוך קובץ .env אם קיים
load_dotenv()

class APICredentials:
    """
    מחלקת גישה למפתחות API מרוכזים.
    """
    @staticmethod
    def get_finnhub_key() -> str:
        return os.getenv("FINNHUB_API_KEY", "")

    @staticmethod
    def get_fmp_key() -> str:
        return os.getenv("FMP_API_KEY", "")

    @staticmethod
    def get_twelve_key() -> str:
        return os.getenv("TWELVE_API_KEY", "")

    @staticmethod
    def get_openai_key() -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @staticmethod
    def get_marketaux_key() -> str:
        return os.getenv("MARKETAUX_API_KEY", "Dx8X1gzfxklRC5WETItJAncifB4bXp98EnSqzT6P")

    @staticmethod
    def get_newsdata_key() -> str:
        return os.getenv("NEWSDATA_API_KEY", "pub_a54510d1206a48d39dd48b3b3b624a2f")

    @staticmethod
    def get_alpha_vantage_key() -> str:
        return os.getenv("ALPHA_VANTAGE_API_KEY", "")

    @staticmethod
    def get_reuters_key() -> str:
        return os.getenv("REUTERS_API_KEY", "")

    @staticmethod
    def get_yahoo_finance_rss() -> str:
        return "https://feeds.finance.yahoo.com/rss/2.0/headline"
