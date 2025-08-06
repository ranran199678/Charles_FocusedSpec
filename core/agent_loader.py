"""
Agent Loader - טוען דינמי לסוכנים
==================================

מערכת טעינה דינמית לסוכנים עם ניהול קונפיגורציה,
ולידציה וניהול תלויות.
"""

import yaml
import importlib
import logging
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
from dataclasses import dataclass
from core.base.base_agent import BaseAgent

logger = logging.getLogger(__name__)

@dataclass
class AgentInfo:
    """מידע על סוכן"""
    name: str
    class_name: str
    module_path: str
    enabled: bool
    weight: float
    priority: str
    config: Dict[str, Any]
    category: str

class AgentLoader:
    """
    טוען דינמי לסוכנים
    
    תכונות:
    - טעינה דינמית של סוכנים מקובץ קונפיגורציה
    - ולידציה של סוכנים
    - ניהול תלויות
    - ניהול ביצועים
    """
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        """אתחול הטוען"""
        self.config_path = config_path
        self.config = self._load_config()
        self.agents: Dict[str, AgentInfo] = {}
        self.loaded_agents: Dict[str, BaseAgent] = {}
        self._parse_agents()
        
    def _load_config(self) -> Dict[str, Any]:
        """טעינת קובץ קונפיגורציה"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"קובץ קונפיגורציה נטען בהצלחה: {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"שגיאה בטעינת קובץ קונפיגורציה: {e}")
            raise
    
    def _parse_agents(self):
        """ניתוח הסוכנים מקובץ הקונפיגורציה"""
        active_agents = self.config.get('active_agents', {})
        
        for category, agents in active_agents.items():
            for agent_name, agent_config in agents.items():
                if agent_config.get('enabled', False):
                    agent_info = AgentInfo(
                        name=agent_name,
                        class_name=self._get_class_name(agent_name),
                        module_path=f"core.{agent_name}",
                        enabled=agent_config.get('enabled', False),
                        weight=agent_config.get('weight', 0.1),
                        priority=agent_config.get('priority', 'medium'),
                        config=agent_config.get('config', {}),
                        category=category
                    )
                    self.agents[agent_name] = agent_info
        
        logger.info(f"נטענו {len(self.agents)} סוכנים פעילים")
    
    def _get_class_name(self, agent_name: str) -> str:
        """המרת שם קובץ לשם מחלקה"""
        # המרה מ-snake_case ל-PascalCase
        words = agent_name.split('_')
        class_name = ''.join(word.capitalize() for word in words)
        
        # תיקונים מיוחדים
        special_cases = {
            'atr_score_agent': 'ATRScoreAgent',
            'macd_momentum_detector': 'MACDMomentumDetector',
            'ml_breakout_model': 'MLBreakoutModel',
            'vcp_super_pattern_agent': 'VCPSuperPatternAgent',
            'vwap_agent': 'VWAPAgent',
            'rsi_sniffer': 'RSISniffer'
        }
        
        return special_cases.get(agent_name, class_name)
    
    def load_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """טעינת סוכן בודד"""
        if agent_name not in self.agents:
            logger.warning(f"סוכן לא נמצא: {agent_name}")
            return None
        
        if agent_name in self.loaded_agents:
            return self.loaded_agents[agent_name]
        
        agent_info = self.agents[agent_name]
        
        try:
            # טעינת המודול
            module = importlib.import_module(agent_info.module_path)
            
            # קבלת המחלקה
            agent_class = getattr(module, agent_info.class_name)
            
            # יצירת מופע עם קונפיגורציה
            agent_instance = agent_class(agent_info.config)
            
            # ולידציה
            if not self._validate_agent(agent_instance):
                logger.error(f"ולידציה נכשלה עבור סוכן: {agent_name}")
                return None
            
            self.loaded_agents[agent_name] = agent_instance
            logger.info(f"סוכן נטען בהצלחה: {agent_name}")
            
            return agent_instance
            
        except Exception as e:
            logger.error(f"שגיאה בטעינת סוכן {agent_name}: {e}")
            return None
    
    def load_agents_by_category(self, category: str) -> Dict[str, BaseAgent]:
        """טעינת כל הסוכנים מקטגוריה מסוימת"""
        category_agents = {}
        
        for agent_name, agent_info in self.agents.items():
            if agent_info.category == category and agent_info.enabled:
                agent = self.load_agent(agent_name)
                if agent:
                    category_agents[agent_name] = agent
        
        logger.info(f"נטענו {len(category_agents)} סוכנים מקטגוריה: {category}")
        return category_agents
    
    def load_agents_by_priority(self, priority: str) -> Dict[str, BaseAgent]:
        """טעינת סוכנים לפי עדיפות"""
        priority_agents = {}
        
        for agent_name, agent_info in self.agents.items():
            if agent_info.priority == priority and agent_info.enabled:
                agent = self.load_agent(agent_name)
                if agent:
                    priority_agents[agent_name] = agent
        
        logger.info(f"נטענו {len(priority_agents)} סוכנים בעדיפות: {priority}")
        return priority_agents
    
    def load_all_agents(self) -> Dict[str, BaseAgent]:
        """טעינת כל הסוכנים הפעילים"""
        all_agents = {}
        
        for agent_name in self.agents.keys():
            if self.agents[agent_name].enabled:
                agent = self.load_agent(agent_name)
                if agent:
                    all_agents[agent_name] = agent
        
        logger.info(f"נטענו {len(all_agents)} סוכנים בסך הכל")
        return all_agents
    
    def _validate_agent(self, agent: BaseAgent) -> bool:
        """ולידציה של סוכן"""
        try:
            # בדיקה שיש מתודת analyze
            if not hasattr(agent, 'analyze'):
                logger.error("סוכן חסר מתודת analyze")
                return False
            
            # בדיקה שהמתודה היא callable
            if not callable(getattr(agent, 'analyze')):
                logger.error("מתודת analyze אינה callable")
                return False
            
            # בדיקה שהסוכן יורש מ-BaseAgent (אופציונלי)
            if not isinstance(agent, BaseAgent):
                logger.warning("סוכן אינו יורש מ-BaseAgent")
            
            return True
            
        except Exception as e:
            logger.error(f"שגיאה בולידציה: {e}")
            return False
    
    def get_agent_info(self, agent_name: str) -> Optional[AgentInfo]:
        """קבלת מידע על סוכן"""
        return self.agents.get(agent_name)
    
    def get_agents_by_category(self, category: str) -> List[AgentInfo]:
        """קבלת רשימת סוכנים לפי קטגוריה"""
        return [agent for agent in self.agents.values() if agent.category == category]
    
    def get_agents_by_priority(self, priority: str) -> List[AgentInfo]:
        """קבלת רשימת סוכנים לפי עדיפות"""
        return [agent for agent in self.agents.values() if agent.priority == priority]
    
    def get_agent_weights(self) -> Dict[str, float]:
        """קבלת משקלים של כל הסוכנים"""
        return {name: agent.weight for name, agent in self.agents.items()}
    
    def run_agent(self, agent_name: str, symbol: str, **kwargs) -> Optional[Dict]:
        """הרצת סוכן בודד"""
        agent = self.load_agent(agent_name)
        if not agent:
            return None
        
        try:
            result = agent.analyze(symbol, **kwargs)
            logger.info(f"סוכן {agent_name} הור בהצלחה עבור {symbol}")
            return result
        except Exception as e:
            logger.error(f"שגיאה בהרצת סוכן {agent_name}: {e}")
            return None
    
    def run_agents_by_category(self, category: str, symbol: str, **kwargs) -> Dict[str, Dict]:
        """הרצת כל הסוכנים מקטגוריה מסוימת"""
        agents = self.load_agents_by_category(category)
        results = {}
        
        for agent_name, agent in agents.items():
            try:
                result = agent.analyze(symbol, **kwargs)
                results[agent_name] = result
            except Exception as e:
                logger.error(f"שגיאה בהרצת סוכן {agent_name}: {e}")
                results[agent_name] = {"error": str(e)}
        
        return results
    
    def run_agents_by_priority(self, priority: str, symbol: str, **kwargs) -> Dict[str, Dict]:
        """הרצת סוכנים לפי עדיפות"""
        agents = self.load_agents_by_priority(priority)
        results = {}
        
        for agent_name, agent in agents.items():
            try:
                result = agent.analyze(symbol, **kwargs)
                results[agent_name] = result
            except Exception as e:
                logger.error(f"שגיאה בהרצת סוכן {agent_name}: {e}")
                results[agent_name] = {"error": str(e)}
        
        return results
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """קבלת סטטיסטיקות על הסוכנים"""
        stats = {
            "total_agents": len(self.agents),
            "loaded_agents": len(self.loaded_agents),
            "categories": {},
            "priorities": {},
            "enabled_agents": 0,
            "disabled_agents": 0
        }
        
        # סטטיסטיקות לפי קטגוריות
        for agent in self.agents.values():
            if agent.enabled:
                stats["enabled_agents"] += 1
            else:
                stats["disabled_agents"] += 1
            
            # קטגוריות
            if agent.category not in stats["categories"]:
                stats["categories"][agent.category] = 0
            stats["categories"][agent.category] += 1
            
            # עדיפויות
            if agent.priority not in stats["priorities"]:
                stats["priorities"][agent.priority] = 0
            stats["priorities"][agent.priority] += 1
        
        return stats
    
    def reload_config(self):
        """טעינה מחדש של הקונפיגורציה"""
        self.config = self._load_config()
        self.agents.clear()
        self.loaded_agents.clear()
        self._parse_agents()
        logger.info("קונפיגורציה נטענה מחדש")
    
    def cleanup(self):
        """ניקוי משאבים"""
        self.loaded_agents.clear()
        logger.info("משאבי הטוען נוקו")

# פונקציה עזר ליצירת טוען
def create_agent_loader(config_path: str = "config/agent_config.yaml") -> AgentLoader:
    """יצירת טוען סוכנים"""
    return AgentLoader(config_path)

# דוגמה לשימוש
if __name__ == "__main__":
    # יצירת טוען
    loader = create_agent_loader()
    
    # הדפסת סטטיסטיקות
    stats = loader.get_agent_statistics()
    print("סטטיסטיקות סוכנים:")
    print(f"סה\"כ סוכנים: {stats['total_agents']}")
    print(f"סוכנים פעילים: {stats['enabled_agents']}")
    print(f"סוכנים נטענים: {stats['loaded_agents']}")
    
    print("\nסוכנים לפי קטגוריות:")
    for category, count in stats['categories'].items():
        print(f"  {category}: {count}")
    
    print("\nסוכנים לפי עדיפויות:")
    for priority, count in stats['priorities'].items():
        print(f"  {priority}: {count}") 