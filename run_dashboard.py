#!/usr/bin/env python3
"""
Run Dashboard - סקריפט להרצת הדשבורד
"""

import subprocess
import sys
import os

def install_requirements():
    """מתקין את הדרישות הנדרשות"""
    print("📦 מתקין דרישות...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "streamlit>=1.28.0",
            "plotly>=5.17.0"
        ])
        print("✅ הדרישות הותקנו בהצלחה!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ שגיאה בהתקנת הדרישות: {e}")
        return False

def run_dashboard():
    """מריץ את הדשבורד"""
    print("🚀 מפעיל דשבורד...")
    
    try:
        # הרצת הדשבורד
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard/streamlit_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 הדשבורד נסגר")
    except Exception as e:
        print(f"❌ שגיאה בהרצת הדשבורד: {e}")

def main():
    """פונקציה ראשית"""
    print("📈 Charles FocusedSpec - דשבורד ניתוח מניות")
    print("=" * 50)
    
    # בדיקת קיום קובץ הדשבורד
    dashboard_file = "dashboard/streamlit_dashboard.py"
    if not os.path.exists(dashboard_file):
        print(f"❌ קובץ הדשבורד לא נמצא: {dashboard_file}")
        return
    
    # התקנת דרישות
    if not install_requirements():
        return
    
    print("\n🌐 הדשבורד ייפתח בדפדפן...")
    print("📍 כתובת: http://localhost:8501")
    print("⏹️  לסגירה: Ctrl+C")
    print("-" * 50)
    
    # הרצת הדשבורד
    run_dashboard()

if __name__ == "__main__":
    main() 