import time
from abc import ABC, abstractmethod

class LiveExecutableAgent(ABC):
    def __init__(self, symbol, interval="1day", live_mode=False, frequency_sec=60):
        self.symbol = symbol
        self.interval = interval
        self.live_mode = live_mode
        self.frequency_sec = frequency_sec

    @abstractmethod
    def run_once(self):
        """הסוכן מממש את הפעולה הזאת – מה קורה בכל הרצה"""
        pass

    def run_live(self, cycles=None):
        """הפעלת הסוכן בלייב – בלולאה"""
        i = 0
        while True:
            print(f"\n⚡ הרצה {i+1} | סוכן: {self.__class__.__name__} | סימבול: {self.symbol} | אינטרוול: {self.interval}")
            try:
                result = self.run_once()
                print(result)
            except Exception as e:
                print(f"❌ שגיאה במהלך ההרצה: {e}")

            i += 1
            if cycles and i >= cycles:
                break

            time.sleep(self.frequency_sec)
