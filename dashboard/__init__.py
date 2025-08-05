"""
Charles_FocusedSpec - Dashboard Module
מערכת חיזוי מניות פורצות - מודול דשבורד

מודול זה מכיל את כל הדשבורדים והממשקים הגרפיים של המערכת
"""

# Dashboard Applications
from .main_dashboard import run_dashboard, MainDashboard
from .streamlit_dashboard import StreamlitDashboard

# Version
__version__ = "1.0.0"
__author__ = "Charles_FocusedSpec Team"
__description__ = "דשבורדים וממשקים גרפיים למערכת חיזוי מניות"

# Main exports
__all__ = [
    'run_dashboard',
    'MainDashboard',
    'StreamlitDashboard',
] 