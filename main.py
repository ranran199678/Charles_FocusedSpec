#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Charles_FocusedSpec - מערכת חיזוי מניות פורצות
Main Entry Point

זהו הקובץ הראשי להפעלת מערכת Charles_FocusedSpec
מספק ממשק שורת פקודה לניהול המערכת
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# הוספת תיקיית הפרויקט ל-Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logger import setup_logger
from utils.smart_data_manager import SmartDataManager
from core.alpha_score_engine import AlphaScoreEngine
from dashboard.main_dashboard import run_dashboard
from live.multi_agent_runner import MultiAgentRunner


class CharlesFocusedSpec:
    """
    המחלקה הראשית לניהול מערכת Charles_FocusedSpec
    """
    
    def __init__(self):
        """אתחול המערכת"""
        self.logger = setup_logger(__name__)
        self.data_manager = None
        self.alpha_engine = None
        self.agent_runner = None
        
    def initialize_system(self):
        """אתחול כל רכיבי המערכת"""
        try:
            self.logger.info("מתחיל אתחול מערכת Charles_FocusedSpec...")
            
            # אתחול מנהל הנתונים
            self.data_manager = SmartDataManager()
            self.logger.info("✓ מנהל נתונים אותחל בהצלחה")
            
            # אתחול מנוע האלפא
            self.alpha_engine = AlphaScoreEngine()
            self.logger.info("✓ מנוע אלפא אותחל בהצלחה")
            
            # אתחול הרצת סוכנים
            self.agent_runner = MultiAgentRunner()
            self.logger.info("✓ הרצת סוכנים אותחלה בהצלחה")
            
            self.logger.info("✓ כל רכיבי המערכת אותחלו בהצלחה")
            return True
            
        except Exception as e:
            self.logger.error(f"שגיאה באתחול המערכת: {e}")
            return False
    
    def run_analysis(self, symbols: List[str], analysis_type: str = "full"):
        """
        הרצת ניתוח על מניות
        
        Args:
            symbols: רשימת סימבולים לניתוח
            analysis_type: סוג הניתוח (full, technical, sentiment, news)
        """
        try:
            self.logger.info(f"מתחיל ניתוח {analysis_type} עבור: {symbols}")
            
            if not self.alpha_engine:
                self.initialize_system()
            
            results = {}
            for symbol in symbols:
                self.logger.info(f"מנתח {symbol}...")
                result = self.alpha_engine.analyze_stock(symbol, analysis_type)
                results[symbol] = result
                
            self.logger.info(f"✓ הניתוח הושלם עבור {len(symbols)} מניות")
            return results
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח: {e}")
            return None
    
    def run_dashboard(self, port: int = 8501):
        """הפעלת הדשבורד"""
        try:
            self.logger.info(f"מפעיל דשבורד על פורט {port}...")
            run_dashboard(port=port)
        except Exception as e:
            self.logger.error(f"שגיאה בהפעלת הדשבורד: {e}")
    
    def run_live_monitoring(self, symbols: List[str]):
        """הפעלת ניטור חי"""
        try:
            self.logger.info(f"מתחיל ניטור חי עבור: {symbols}")
            
            if not self.agent_runner:
                self.initialize_system()
            
            self.agent_runner.run_live_monitoring(symbols)
            
        except Exception as e:
            self.logger.error(f"שגיאה בניטור חי: {e}")
    
    def update_data(self, symbols: Optional[List[str]] = None):
        """עדכון נתונים"""
        try:
            self.logger.info("מתחיל עדכון נתונים...")
            
            if not self.data_manager:
                self.initialize_system()
            
            if symbols:
                self.data_manager.update_stock_data(symbols)
            else:
                self.data_manager.update_all_data()
                
            self.logger.info("✓ עדכון הנתונים הושלם")
            
        except Exception as e:
            self.logger.error(f"שגיאה בעדכון נתונים: {e}")
    
    def run_tests(self):
        """הרצת בדיקות מערכת"""
        try:
            self.logger.info("מתחיל הרצת בדיקות מערכת...")
            
            # בדיקת חיבוריות
            if not self.data_manager:
                self.initialize_system()
            
            # בדיקת API keys
            from utils.credentials import check_api_keys
            check_api_keys()
            
            # בדיקת נתונים
            test_symbols = ["AAPL", "MSFT", "GOOGL"]
            self.update_data(test_symbols)
            
            # בדיקת ניתוח
            results = self.run_analysis(test_symbols, "technical")
            
            self.logger.info("✓ כל הבדיקות עברו בהצלחה")
            return True
            
        except Exception as e:
            self.logger.error(f"שגיאה בבדיקות: {e}")
            return False


def main():
    """הפונקציה הראשית"""
    parser = argparse.ArgumentParser(
        description="Charles_FocusedSpec - מערכת חיזוי מניות פורצות",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
דוגמאות שימוש:
  python main.py dashboard                    # הפעלת דשבורד
  python main.py analyze AAPL MSFT GOOGL     # ניתוח מניות
  python main.py live AAPL MSFT              # ניטור חי
  python main.py update                      # עדכון נתונים
  python main.py test                        # הרצת בדיקות
        """
    )
    
    parser.add_argument(
        'command',
        choices=['dashboard', 'analyze', 'live', 'update', 'test'],
        help='הפקודה להרצה'
    )
    
    parser.add_argument(
        'symbols',
        nargs='*',
        help='סימבולי מניות (נדרש עבור analyze ו-live)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8501,
        help='פורט לדשבורד (ברירת מחדל: 8501)'
    )
    
    parser.add_argument(
        '--analysis-type',
        choices=['full', 'technical', 'sentiment', 'news'],
        default='full',
        help='סוג הניתוח (ברירת מחדל: full)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='רמת לוג (ברירת מחדל: INFO)'
    )
    
    args = parser.parse_args()
    
    # הגדרת רמת לוג
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # יצירת מופע המערכת
    system = CharlesFocusedSpec()
    
    try:
        if args.command == 'dashboard':
            system.run_dashboard(args.port)
            
        elif args.command == 'analyze':
            if not args.symbols:
                print("שגיאה: נדרשים סימבולי מניות עבור ניתוח")
                sys.exit(1)
            results = system.run_analysis(args.symbols, args.analysis_type)
            if results:
                print("תוצאות הניתוח:")
                for symbol, result in results.items():
                    print(f"\n{symbol}:")
                    print(f"  ציון אלפא: {result.get('alpha_score', 'N/A')}")
                    print(f"  רמת ביטחון: {result.get('confidence', 'N/A')}")
                    print(f"  אות: {result.get('signal', 'N/A')}")
            
        elif args.command == 'live':
            if not args.symbols:
                print("שגיאה: נדרשים סימבולי מניות עבור ניטור חי")
                sys.exit(1)
            system.run_live_monitoring(args.symbols)
            
        elif args.command == 'update':
            system.update_data(args.symbols if args.symbols else None)
            
        elif args.command == 'test':
            success = system.run_tests()
            if not success:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\nהמערכת הופסקה על ידי המשתמש")
        sys.exit(0)
    except Exception as e:
        print(f"שגיאה: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 