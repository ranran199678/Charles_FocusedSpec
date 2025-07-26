# run_engine/runner.py

import os
import sys

# שלב 1: הוספת הנתיב של תיקיית הבסיס לפרויקט (charles_architect_env)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# שלב 2: ייבוא הפונקציות מיחידות אחרות
from gpt_interface.gpt_client import ask_gpt
from project_logging.memory_log import log_to_memory

def run_basic():
    # שלב 3: הגדרת ההודעה שנשלחת ל-GPT
    prompt = "תן לי רשימה של 3 צעדים לבניית מערכת חכמה לזיהוי מניות פורצות"
    log_to_memory("user", prompt)  # שמירת השאלה בלוג

    # שלב 4: שליחה ל-GPT דרך ה-API וקבלת תשובה
    response = ask_gpt(prompt)
    log_to_memory("assistant", response)  # שמירת התשובה בלוג

    # שלב 5: הצגת התשובה למשתמש
    print("\n📤 תשובת GPT:\n")
    print(response)

if __name__ == "__main__":
    run_basic()
