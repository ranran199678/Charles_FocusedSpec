# example_run.py

from core.meta_agent import MetaAgent

# ציוני דוגמה מכל הסוכנים (C1–C4)
agent_scores = {
    "technical": 78,
    "fundamental": 65,
    "news": 54,
    "sentiment": 72
}

# הפעלת MetaAgent
meta = MetaAgent("config/config.yaml")
result = meta.run(agent_scores)

print("\n--- תוצאה ---")
print(f"ציון משוקלל: {result['score']}")
print(f"המלצה: {result['recommendation']}")
