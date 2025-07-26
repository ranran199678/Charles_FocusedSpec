# main.py

import os
from gpt_interface.gpt_client import ask_gpt
from project_logging.memory_log import log_to_memory, read_memory

def send_custom_prompt():
    user_input = input("\n🔹 מה ברצונך לשאול את Charles_Architect? \n> ")
    log_to_memory("user", user_input)
    response = ask_gpt(user_input)
    log_to_memory("assistant", response)
    print("\n📤 תשובת GPT:\n")
    print(response)

def show_memory():
    print("\n🧠 זיכרון השיחות:")
    memory = read_memory()
    if not memory:
        print("(הזיכרון ריק)")
    else:
        for line in memory:
            print(line.strip())

def clear_memory():
    confirm = input("⚠️ אתה בטוח שברצונך למחוק את הזיכרון? (y/n): ")
    if confirm.lower() == 'y':
        with open("logs/charles_architect_memory.log", "w", encoding="utf-8") as f:
            f.write("")
        print("✅ הזיכרון נמחק בהצלחה.")
    else:
        print("❎ פעולה בוטלה.")

def main_menu():
    while True:
        print("\n📋 תפריט ראשי – Charles_Architect")
        print("1. שלח שאלה ל־GPT")
        print("2. הצג את זיכרון השיחות")
        print("3. נקה את הזיכרון")
        print("0. יציאה")

        choice = input("\nבחר אפשרות: ")

        if choice == '1':
            send_custom_prompt()
        elif choice == '2':
            show_memory()
        elif choice == '3':
            clear_memory()
        elif choice == '0':
            print("להתראות! 👋")
            break
        else:
            print("❌ בחירה לא תקפה. נסה שוב.")

if __name__ == "__main__":
    main_menu()
