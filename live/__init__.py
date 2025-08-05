"""
Charles_FocusedSpec - Live Module
מערכת חיזוי מניות פורצות - מודול ניטור חי

מודול זה מכיל את כל הכלים לניטור חי והרצת סוכנים בזמן אמת
"""

# Live Monitoring
from .multi_agent_runner import MultiAgentRunner
from .agent_runner import AgentRunner

# Version
__version__ = "1.0.0"
__author__ = "Charles_FocusedSpec Team"
__description__ = "ניטור חי והרצת סוכנים בזמן אמת"

# Main exports
__all__ = [
    'MultiAgentRunner',
    'AgentRunner',
] 