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
        # תומך גם במפתח בשם 'Marketaux'
        return (
            os.getenv("MARKETAUX_API_KEY")
            or os.getenv("Marketaux")
            or ""
        )

    @staticmethod
    def get_newsdata_key() -> str:
        # תומך גם במפתח בשם 'NEWS_API'
        return (
            os.getenv("NEWSDATA_API_KEY")
            or os.getenv("NEWS_API")
            or ""
        )

    @staticmethod
    def get_alpha_vantage_key() -> str:
        return os.getenv("ALPHA_VANTAGE_API_KEY", "")

    @staticmethod
    def get_polygon_key() -> str:
        # תומך גם במפתח בשם 'POLYGON_IO' או 'Polygon.io'
        return (
            os.getenv("POLYGON_API_KEY")
            or os.getenv("POLYGON_IO_API_KEY")
            or os.getenv("POLYGON_IO")
            or os.getenv("Polygon.io")
            or ""
        )

    @staticmethod
    def get_twitter_key() -> str:
        # תומך גם ב-TWITTER_BEARER_TOKEN ובשם 'Twitter_API'
        return (
            os.getenv("TWITTER_API_KEY")
            or os.getenv("TWITTER_BEARER_TOKEN")
            or os.getenv("Twitter_API")
            or ""
        )

    @staticmethod
    def get_reddit_credentials() -> dict:
        # תומך גם באיחוד בשם 'Reddit_API' אם נשמר כמחרוזת
        return {
            "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
            "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
            "username": os.getenv("REDDIT_USERNAME", ""),
            "password": os.getenv("REDDIT_PASSWORD", ""),
            "user_agent": os.getenv("REDDIT_USER_AGENT", "CharlesFocusedSpec/1.0"),
            "token": os.getenv("Reddit_API", "")
        }

    @staticmethod
    def get_reuters_key() -> str:
        return os.getenv("REUTERS_API_KEY", "")

    @staticmethod
    def get_yahoo_finance_rss() -> str:
        return "https://feeds.finance.yahoo.com/rss/2.0/headline"

class CredentialsManager:
    """
    מנהל מפתחות API מתקדם
    """
    
    def __init__(self):
        """אתחול מנהל המפתחות"""
        self.credentials = APICredentials()
        self._validate_keys()
    
    def _validate_keys(self):
        """בדיקת תקינות המפתחות"""
        self.valid_keys = {}
        
        # בדיקת מפתחות נדרשים
        required_keys = {
            'fmp': self.credentials.get_fmp_key(),
            'finnhub': self.credentials.get_finnhub_key(),
            'alpha_vantage': self.credentials.get_alpha_vantage_key(),
            'openai': self.credentials.get_openai_key()
        }
        
        for key_name, key_value in required_keys.items():
            if key_value and key_value.strip():
                self.valid_keys[key_name] = True
            else:
                self.valid_keys[key_name] = False
    
    def get_valid_keys(self) -> dict:
        """קבלת רשימת מפתחות תקינים"""
        return self.valid_keys.copy()
    
    def is_key_valid(self, key_name: str) -> bool:
        """בדיקה אם מפתח תקין"""
        return self.valid_keys.get(key_name, False)
    
    def get_missing_keys(self) -> list:
        """קבלת רשימת מפתחות חסרים"""
        missing = []
        for key_name, is_valid in self.valid_keys.items():
            if not is_valid:
                missing.append(key_name)
        return missing

def check_api_keys() -> dict:
    """
    בדיקת מפתחות API זמינים
    
    Returns:
        מילון עם סטטוס המפתחות
    """
    manager = CredentialsManager()
    return manager.get_valid_keys()
