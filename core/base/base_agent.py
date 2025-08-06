# core/base/base_agent.py

import logging
import traceback
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd

# ייבוא מנהל הנתונים החכם
try:
    from utils.smart_data_manager import SmartDataManager
    from utils.data_fetcher import DataFetcher
    from utils.fmp_utils import fmp_client
except ImportError as e:
    logging.warning(f"לא ניתן לייבא מנהלי נתונים: {e}")

class BaseAgent(ABC):
    """
    מחלקת בסיס חכמה לכל הסוכנים במערכת Charles_FocusedSpec
    כוללת מבנה אחיד, ניהול קונפיגורציה, טיפול בשגיאות, תיעוד וביצועים
    וגישה אחידה לנתונים דרך SmartDataManager
    """

    def __init__(self, config=None):
        """
        אתחול הסוכן עם קונפיגורציה ואופציה ל־debug
        :param config: dict עם הגדרות כמו debug, מזהה וכו'
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        self.debug = self.config.get("debug", False)
        self.logger = logging.getLogger(self.name)
        
        # אתחול מנהלי נתונים
        self._init_data_managers()
        
        # הגדרות ברירת מחדל לנתונים
        self.default_days = self.config.get("default_days", 90)
        self.default_interval = self.config.get("default_interval", "1day")
        self.include_live = self.config.get("include_live", True)

    def _init_data_managers(self):
        """אתחול מנהלי הנתונים - עם טיפול בשגיאות"""
        try:
            self.data_manager = SmartDataManager()
            self.data_fetcher = DataFetcher()
            self.fmp_client = fmp_client
            self.logger.info(f"{self.name}: מנהלי נתונים אותחלו בהצלחה")
        except Exception as e:
            self.logger.warning(f"{self.name}: שגיאה באתחול מנהלי נתונים: {e}")
            self.data_manager = None
            self.data_fetcher = None
            self.fmp_client = None

    def get_stock_data(self, symbol: str, days: int = None, 
                      include_live: bool = None) -> Optional[pd.DataFrame]:
        """
        קבלת נתוני מניה דרך מנהל הנתונים החכם
        :param symbol: סימול המניה
        :param days: מספר ימים לשליפה
        :param include_live: האם לכלול נתונים חיים
        :return: DataFrame עם נתוני המניה או None
        """
        if not self.data_manager:
            self.logger.error(f"{self.name}: מנהל נתונים לא זמין")
            return None
            
        try:
            days = days or self.default_days
            include_live = include_live if include_live is not None else self.include_live
            
            data = self.data_manager.get_stock_data(symbol, days, include_live)
            if data is not None and not data.empty:
                self.logger.info(f"{self.name}: נתונים נטענו עבור {symbol} ({len(data)} רשומות)")
                return data
            else:
                self.logger.warning(f"{self.name}: לא נמצאו נתונים עבור {symbol}")
                return None
        except Exception as e:
            self.logger.error(f"{self.name}: שגיאה בקבלת נתונים עבור {symbol}: {e}")
            return None

    def get_technical_indicators(self, symbol: str, indicator: str = 'all', 
                               days: int = None) -> Optional[pd.DataFrame]:
        """
        קבלת אינדיקטורים טכניים
        :param symbol: סימול המניה
        :param indicator: שם האינדיקטור או 'all' לכל האינדיקטורים
        :param days: מספר ימים
        :return: DataFrame עם אינדיקטורים טכניים
        """
        if not self.data_manager:
            return None
            
        try:
            days = days or self.default_days
            return self.data_manager.get_technical_indicators(symbol, indicator, days)
        except Exception as e:
            self.logger.error(f"{self.name}: שגיאה בקבלת אינדיקטורים טכניים: {e}")
            return None

    def get_news_sentiment(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        קבלת נתוני חדשות ורגשות
        :param symbol: סימול המניה
        :param days: מספר ימים
        :return: DataFrame עם נתוני חדשות
        """
        if not self.data_manager:
            return None
            
        try:
            return self.data_manager.get_news_sentiment(symbol, days)
        except Exception as e:
            self.logger.error(f"{self.name}: שגיאה בקבלת נתוני חדשות: {e}")
            return None

    def get_fundamentals(self, symbol: str, statement_type: str = 'income') -> Optional[pd.DataFrame]:
        """
        קבלת נתונים פונדמנטליים
        :param symbol: סימול המניה
        :param statement_type: סוג הדוח (income, balance, cash)
        :return: DataFrame עם נתונים פונדמנטליים
        """
        if not self.data_manager:
            return None
            
        try:
            return self.data_manager.get_fundamentals(symbol, statement_type)
        except Exception as e:
            self.logger.error(f"{self.name}: שגיאה בקבלת נתונים פונדמנטליים: {e}")
            return None

    def get_comprehensive_data(self, symbol: str, days: int = None,
                             include_technical: bool = True,
                             include_news: bool = True,
                             include_fundamentals: bool = False) -> Dict[str, pd.DataFrame]:
        """
        קבלת נתונים מקיפים - מחיר, טכני, חדשות ופונדמנטלי
        :param symbol: סימול המניה
        :param days: מספר ימים
        :param include_technical: האם לכלול אינדיקטורים טכניים
        :param include_news: האם לכלול חדשות
        :param include_fundamentals: האם לכלול נתונים פונדמנטליים
        :return: dict עם כל סוגי הנתונים
        """
        if not self.data_manager:
            return {}
            
        try:
            days = days or self.default_days
            return self.data_manager.get_comprehensive_data(
                symbol, days, include_technical, include_news, include_fundamentals
            )
        except Exception as e:
            self.logger.error(f"{self.name}: שגיאה בקבלת נתונים מקיפים: {e}")
            return {}

    def log(self, msg):
        """רישום הודעה ללוג ו־debug בעת הצורך"""
        if self.debug:
            print(f"[{self.name}] {msg}")
        self.logger.info(msg)

    def handle_error(self, ex):
        """טיפול בשגיאה, כולל תיעוד מלא בעת debug"""
        msg = f"[{self.name}] ERROR: {type(ex).__name__} | {str(ex)}"
        self.logger.error(msg)
        if self.debug:
            traceback.print_exc()

    def _get_dummy_result(self, explanation: str = "Agent לא מומש"):
        """
        מחזיר תוצאה דמוית עבור סוכנים שלא מומשו או שנכשלו
        :param explanation: הסבר למה התוצאה היא דמוית
        :return: dict עם תוצאה דמוית
        """
        return {
            "score": 1,
            "explanation": explanation,
            "details": {},
            "timestamp": None
        }

    def validate_input(self, *args, **kwargs):
        """ניתן לממש בעתיד עבור כל סוכן – לבדוק תקינות קלט"""
        return True

    def pre_process(self, *args, **kwargs):
        """שלב הכנה לפני ניתוח – ניקוי קלט, לוגים וכו'"""
        return args, kwargs

    def post_process(self, result):
        """עיבוד תוצאה – ניקוי, עיגול, תיעוד נוסף"""
        return result

    def cache_result(self, symbol, result):
        """
        אופציונלי: שמירת תוצאות ל־DB/קובץ/זיכרון
        :param symbol: סימול המניה שנותחה
        :param result: dict של תוצאות הניתוח
        """
        pass

    def run(self, *args, **kwargs):
        """
        הרצת הסוכן – ניהול מלא של תהליך הניתוח
        :return: dict עם score, explanation ו־details
        """
        try:
            if not self.validate_input(*args, **kwargs):
                raise ValueError("Invalid input for agent")

            args, kwargs = self.pre_process(*args, **kwargs)
            raw_result = self.analyze(*args, **kwargs)
            processed = self.post_process(raw_result)
            if "symbol" in kwargs:
                self.cache_result(kwargs["symbol"], processed)
            return processed

        except Exception as ex:
            self.handle_error(ex)
            return self.fallback()

    @abstractmethod
    def analyze(self, *args, **kwargs):
        """
        פונקציית הניתוח שעל כל סוכן לממש בפועל
        :return: dict עם score, explanation ו־details
        """
        pass

    def fallback(self):
        """
        ברירת מחדל – מה יוחזר במקרה של כשל/מימוש חסר
        :return: dict
        """
        return {
            "score": 1,
            "explanation": f"{self.name} failed or not implemented",
            "details": {}
        }
