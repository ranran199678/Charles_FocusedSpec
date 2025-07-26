# meta_agent.py

import yaml
import os
from typing import Dict

class MetaAgent:
    """
    סוכן קונסולידציה שמחשב ציון כולל על בסיס תתי סוכנים,
    לפי משקלים מתוך קובץ config.yaml, עם המלצה השקעתית.
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.weights = self.load_weights()

    def load_weights(self) -> Dict[str, float]:
        """טעינת משקלים מתוך קובץ YAML"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"קובץ קונפיגורציה לא נמצא: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if "weights" not in config:
            raise KeyError("חסר מקטע 'weights' בקובץ הקונפיגורציה")
        return config["weights"]

    def consolidate_scores(self, agent_scores: Dict[str, float]) -> float:
        """שקלול ציונים לפי משקלים מתוך הקובץ"""
        weighted_sum = 0.0
        total_weight = 0.0

        for key, weight in self.weights.items():
            score = agent_scores.get(key)
            if score is not None:
                if not (0 <= score <= 100):
                    raise ValueError(f"ציון לא תקין עבור {key}: {score}")
                print(f"[+] {key}: {score} x משקל {weight}")
                weighted_sum += score * weight
                total_weight += weight
            else:
                print(f"[!] אין ציון עבור {key}, מדולג")

        if total_weight == 0:
            raise ValueError("סכום המשקלים הוא אפס – לא ניתן לחשב")

        return weighted_sum / total_weight

    def investment_decision(self, total_score: float) -> str:
        """החזרת המלצת השקעה לפי טווחי ציון"""
        if total_score >= 70:
            return "קנייה"
        elif total_score >= 41:
            return "ניטרלי"
        return "הימנעות"

    def run(self, agent_scores: Dict[str, float]) -> Dict[str, object]:
        """הרצת הסוכן: החזרת ציון כולל + המלצה"""
        print("\n--- הפעלת MetaAgent ---")
        total_score = self.consolidate_scores(agent_scores)
        recommendation = self.investment_decision(total_score)
        print(f"[=] ציון כולל: {round(total_score, 2)} | המלצה: {recommendation}")
        return {
            "score": round(total_score, 2),
            "recommendation": recommendation
        }
