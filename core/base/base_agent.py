# core/base/base_agent.py

import logging
import traceback
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    מחלקת בסיס חכמה לכל הסוכנים במערכת Charles_FocusedSpec
    כוללת מבנה אחיד, ניהול קונפיגורציה, טיפול בשגיאות, תיעוד וביצועים
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
