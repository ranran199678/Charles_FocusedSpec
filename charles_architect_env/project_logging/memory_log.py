import os
from datetime import datetime

LOG_FILE_PATH = "logs/charles_architect_memory.log"

def log_to_memory(role, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{role.upper()}]: {content}\n")

def read_memory():
    if not os.path.exists(LOG_FILE_PATH):
        return []
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        return f.readlines()
