"""
Logger System - מערכת לוגים מתקדמת
====================================

מערכת לוגים מתקדמת לכל הסוכנים.
כוללת רוטציה של קבצים, רמות לוג שונות, פורמט מובנה ואינטגרציה עם המערכת.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import traceback
from pathlib import Path

# הגדרות ברירת מחדל
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_LOG_BACKUP_COUNT = 5
DEFAULT_LOG_DIR = "log"

class StructuredFormatter(logging.Formatter):
    """
    פורמטר לוגים מובנה עם JSON
    """
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
    
    def format(self, record: logging.LogRecord) -> str:
        """
        פורמט לוג עם מבנה מובנה
        """
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # הוספת מידע נוסף אם קיים
        if hasattr(record, 'agent_name'):
            log_entry['agent'] = record.agent_name
        
        if hasattr(record, 'symbol'):
            log_entry['symbol'] = record.symbol
        
        if hasattr(record, 'score'):
            log_entry['score'] = record.score
        
        if hasattr(record, 'confidence'):
            log_entry['confidence'] = record.confidence
        
        # הוספת exception info אם קיים
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class AgentLogger:
    """
    לוגר מותאם לסוכנים
    """
    
    def __init__(self, agent_name: str, log_level: int = DEFAULT_LOG_LEVEL):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self.logger.setLevel(log_level)
        
        # הוספת handler אם לא קיים
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """הגדרת handlers ללוגר"""
        # יצירת תיקיית לוגים
        log_dir = Path(DEFAULT_LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # File handler עם רוטציה
        log_file = log_dir / f"{self.agent_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=DEFAULT_LOG_FILE_SIZE,
            backupCount=DEFAULT_LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # הגדרת פורמט
        formatter = StructuredFormatter()
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        
        # הוספת handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """לוג debug"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """לוג info"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """לוג warning"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """לוג error"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """לוג critical"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """פונקציה פנימית ללוג"""
        extra = {'agent_name': self.agent_name}
        extra.update(kwargs)
        
        self.logger.log(level, message, extra=extra)

class SystemLogger:
    """
    לוגר מערכת כללי
    """
    
    def __init__(self, name: str = "system", log_level: int = DEFAULT_LOG_LEVEL):
        self.name = name
        self.logger = logging.getLogger(f"system.{name}")
        self.logger.setLevel(log_level)
        
        # הוספת handler אם לא קיים
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """הגדרת handlers ללוגר"""
        # יצירת תיקיית לוגים
        log_dir = Path(DEFAULT_LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # File handler עם רוטציה
        log_file = log_dir / f"{self.name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=DEFAULT_LOG_FILE_SIZE,
            backupCount=DEFAULT_LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # הגדרת פורמט
        formatter = StructuredFormatter()
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        
        # הוספת handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """לוג debug"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """לוג info"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """לוג warning"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """לוג error"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """לוג critical"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """פונקציה פנימית ללוג"""
        extra = {'system_name': self.name}
        extra.update(kwargs)
        
        self.logger.log(level, message, extra=extra)

class PerformanceLogger:
    """
    לוגר ביצועים
    """
    
    def __init__(self, name: str = "performance"):
        self.name = name
        self.logger = logging.getLogger(f"performance.{name}")
        self.logger.setLevel(logging.INFO)
        
        # הוספת handler אם לא קיים
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """הגדרת handlers ללוגר"""
        # יצירת תיקיית לוגים
        log_dir = Path(DEFAULT_LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # File handler עם רוטציה
        log_file = log_dir / "performance.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=DEFAULT_LOG_FILE_SIZE,
            backupCount=DEFAULT_LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # הגדרת פורמט
        formatter = StructuredFormatter()
        file_handler.setFormatter(formatter)
        
        # הוספת handler
        self.logger.addHandler(file_handler)
    
    def log_execution_time(self, agent_name: str, symbol: str, execution_time: float, 
                          score: Optional[float] = None, confidence: Optional[str] = None):
        """לוג זמן ביצוע"""
        self.logger.info(
            f"Execution completed",
            extra={
                'agent_name': agent_name,
                'symbol': symbol,
                'execution_time': execution_time,
                'score': score,
                'confidence': confidence,
                'performance_metric': 'execution_time'
            }
        )
    
    def log_memory_usage(self, agent_name: str, memory_usage: float):
        """לוג שימוש זיכרון"""
        self.logger.info(
            f"Memory usage recorded",
            extra={
                'agent_name': agent_name,
                'memory_usage': memory_usage,
                'performance_metric': 'memory_usage'
            }
        )
    
    def log_error_performance(self, agent_name: str, symbol: str, error_type: str, 
                            error_message: str, execution_time: float):
        """לוג שגיאות ביצועים"""
        self.logger.error(
            f"Performance error occurred",
            extra={
                'agent_name': agent_name,
                'symbol': symbol,
                'error_type': error_type,
                'error_message': error_message,
                'execution_time': execution_time,
                'performance_metric': 'error'
            }
        )

class DataLogger:
    """
    לוגר נתונים
    """
    
    def __init__(self, name: str = "data"):
        self.name = name
        self.logger = logging.getLogger(f"data.{name}")
        self.logger.setLevel(logging.INFO)
        
        # הוספת handler אם לא קיים
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """הגדרת handlers ללוגר"""
        # יצירת תיקיית לוגים
        log_dir = Path(DEFAULT_LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # File handler עם רוטציה
        log_file = log_dir / "data.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=DEFAULT_LOG_FILE_SIZE,
            backupCount=DEFAULT_LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # הגדרת פורמט
        formatter = StructuredFormatter()
        file_handler.setFormatter(formatter)
        
        # הוספת handler
        self.logger.addHandler(file_handler)
    
    def log_data_validation(self, symbol: str, data_type: str, is_valid: bool, 
                           validation_errors: Optional[list] = None):
        """לוג אימות נתונים"""
        self.logger.info(
            f"Data validation completed",
            extra={
                'symbol': symbol,
                'data_type': data_type,
                'is_valid': is_valid,
                'validation_errors': validation_errors,
                'data_metric': 'validation'
            }
        )
    
    def log_data_loading(self, symbol: str, data_source: str, data_points: int, 
                        start_date: str, end_date: str):
        """לוג טעינת נתונים"""
        self.logger.info(
            f"Data loaded successfully",
            extra={
                'symbol': symbol,
                'data_source': data_source,
                'data_points': data_points,
                'start_date': start_date,
                'end_date': end_date,
                'data_metric': 'loading'
            }
        )
    
    def log_data_error(self, symbol: str, data_type: str, error_message: str):
        """לוג שגיאות נתונים"""
        self.logger.error(
            f"Data error occurred",
            extra={
                'symbol': symbol,
                'data_type': data_type,
                'error_message': error_message,
                'data_metric': 'error'
            }
        )

# פונקציות עזר גלובליות
def get_agent_logger(agent_name: str) -> AgentLogger:
    """
    קבלת לוגר לסוכן
    
    Args:
        agent_name: שם הסוכן
        
    Returns:
        AgentLogger: לוגר מותאם לסוכן
    """
    return AgentLogger(agent_name)

def get_system_logger(name: str = "system") -> SystemLogger:
    """
    קבלת לוגר מערכת
    
    Args:
        name: שם הלוגר
        
    Returns:
        SystemLogger: לוגר מערכת
    """
    return SystemLogger(name)

def get_performance_logger() -> PerformanceLogger:
    """
    קבלת לוגר ביצועים
    
    Returns:
        PerformanceLogger: לוגר ביצועים
    """
    return PerformanceLogger()

def get_data_logger() -> DataLogger:
    """
    קבלת לוגר נתונים
    
    Returns:
        DataLogger: לוגר נתונים
    """
    return DataLogger()

def setup_logging_config(log_level: int = DEFAULT_LOG_LEVEL, 
                        log_dir: str = DEFAULT_LOG_DIR,
                        log_file_size: int = DEFAULT_LOG_FILE_SIZE,
                        log_backup_count: int = DEFAULT_LOG_BACKUP_COUNT):
    """
    הגדרת תצורת לוגים גלובלית
    
    Args:
        log_level: רמת לוג
        log_dir: תיקיית לוגים
        log_file_size: גודל קובץ לוג מקסימלי
        log_backup_count: מספר קבצי גיבוי
    """
    global DEFAULT_LOG_LEVEL, DEFAULT_LOG_DIR, DEFAULT_LOG_FILE_SIZE, DEFAULT_LOG_BACKUP_COUNT
    
    DEFAULT_LOG_LEVEL = log_level
    DEFAULT_LOG_DIR = log_dir
    DEFAULT_LOG_FILE_SIZE = log_file_size
    DEFAULT_LOG_BACKUP_COUNT = log_backup_count
    
    # יצירת תיקיית לוגים
    Path(log_dir).mkdir(exist_ok=True)

def log_agent_result(agent_name: str, symbol: str, score: float, confidence: str, 
                    execution_time: float, recommendation: str, key_signals: list):
    """
    לוג תוצאת סוכן
    
    Args:
        agent_name: שם הסוכן
        symbol: סמל המניה
        score: ציון
        confidence: רמת ביטחון
        execution_time: זמן ביצוע
        recommendation: המלצה
        key_signals: אותות מפתח
    """
    logger = get_agent_logger(agent_name)
    perf_logger = get_performance_logger()
    
    # לוג תוצאה
    logger.info(
        f"Analysis completed successfully",
        symbol=symbol,
        score=score,
        confidence=confidence,
        recommendation=recommendation,
        key_signals=key_signals
    )
    
    # לוג ביצועים
    perf_logger.log_execution_time(agent_name, symbol, execution_time, score, confidence)

def log_agent_error(agent_name: str, symbol: str, error_message: str, 
                   execution_time: float = 0.0):
    """
    לוג שגיאת סוכן
    
    Args:
        agent_name: שם הסוכן
        symbol: סמל המניה
        error_message: הודעת שגיאה
        execution_time: זמן ביצוע
    """
    logger = get_agent_logger(agent_name)
    perf_logger = get_performance_logger()
    
    # לוג שגיאה
    logger.error(
        f"Analysis failed: {error_message}",
        symbol=symbol
    )
    
    # לוג ביצועים
    perf_logger.log_error_performance(agent_name, symbol, "analysis_error", 
                                     error_message, execution_time)

def log_data_operation(operation: str, symbol: str, data_type: str, 
                      success: bool, details: Optional[Dict] = None):
    """
    לוג פעולת נתונים
    
    Args:
        operation: סוג הפעולה
        symbol: סמל המניה
        data_type: סוג הנתונים
        success: האם הפעולה הצליחה
        details: פרטים נוספים
    """
    data_logger = get_data_logger()
    
    if success:
        data_logger.log_data_loading(symbol, data_type, details.get('data_points', 0),
                                   details.get('start_date', ''), details.get('end_date', ''))
    else:
        data_logger.log_data_error(symbol, data_type, details.get('error_message', 'Unknown error'))

# לוגרים מוגדרים מראש
logger = get_system_logger("default")

# פונקציות תאימות לאחור
def setup_logger(name: str = "default", log_level: int = DEFAULT_LOG_LEVEL) -> SystemLogger:
    """
    פונקציה תאימה לאחור להגדרת לוגר
    
    Args:
        name: שם הלוגר
        log_level: רמת לוג
        
    Returns:
        SystemLogger: לוגר מערכת
    """
    return get_system_logger(name)

def get_logger(name: str = "default") -> SystemLogger:
    """
    פונקציה תאימה לאחור לקבלת לוגר
    
    Args:
        name: שם הלוגר
        
    Returns:
        SystemLogger: לוגר מערכת
    """
    return get_system_logger(name)