"""
File Utils - מערכת ניהול קבצים
===============================

מערכת ניהול קבצים מקיפה לכל הסוכנים.
כוללת קריאה/כתיבה של קבצים, ניהול תיקיות, גיבוי קבצים וארכוב נתונים.
"""

import os
import json
import csv
import pickle
import shutil
import zipfile
import gzip
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import logging

from utils.logger import get_system_logger

logger = get_system_logger("file_utils")

class FileManager:
    """
    מנהל קבצים מתקדם
    """
    
    def __init__(self, base_dir: str = "data"):
        """
        אתחול מנהל קבצים
        
        Args:
            base_dir: תיקייה בסיסית
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # תיקיות משנה
        self.subdirs = {
            'price_data': self.base_dir / 'price_data',
            'volume_data': self.base_dir / 'volume_data',
            'technical_data': self.base_dir / 'technical_data',
            'news_data': self.base_dir / 'news_data',
            'backup': self.base_dir / 'backup',
            'archive': self.base_dir / 'archive',
            'temp': self.base_dir / 'temp',
            'logs': self.base_dir / 'logs'
        }
        
        # יצירת תיקיות
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)
    
    def save_json(self, data: Dict[str, Any], filename: str, subdir: str = None) -> bool:
        """
        שמירת נתונים בפורמט JSON
        
        Args:
            data: נתונים לשמירה
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            
        Returns:
            True אם השמירה הצליחה, False אחרת
        """
        try:
            filepath = self._get_filepath(filename, subdir, '.json')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"JSON data saved successfully: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving JSON data: {str(e)}")
            return False
    
    def load_json(self, filename: str, subdir: str = None) -> Optional[Dict[str, Any]]:
        """
        טעינת נתונים מפורמט JSON
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            
        Returns:
            הנתונים או None אם נכשל
        """
        try:
            filepath = self._get_filepath(filename, subdir, '.json')
            
            if not filepath.exists():
                logger.warning(f"JSON file not found: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"JSON data loaded successfully: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading JSON data: {str(e)}")
            return None
    
    def save_csv(self, data: pd.DataFrame, filename: str, subdir: str = None) -> bool:
        """
        שמירת נתונים בפורמט CSV
        
        Args:
            data: DataFrame לשמירה
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            
        Returns:
            True אם השמירה הצליחה, False אחרת
        """
        try:
            filepath = self._get_filepath(filename, subdir, '.csv')
            
            data.to_csv(filepath, index=True, encoding='utf-8')
            
            logger.info(f"CSV data saved successfully: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving CSV data: {str(e)}")
            return False
    
    def load_csv(self, filename: str, subdir: str = None, **kwargs) -> Optional[pd.DataFrame]:
        """
        טעינת נתונים מפורמט CSV
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            **kwargs: פרמטרים נוספים ל-pd.read_csv
            
        Returns:
            DataFrame או None אם נכשל
        """
        try:
            filepath = self._get_filepath(filename, subdir, '.csv')
            
            if not filepath.exists():
                logger.warning(f"CSV file not found: {filepath}")
                return None
            
            data = pd.read_csv(filepath, **kwargs)
            
            logger.info(f"CSV data loaded successfully: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {str(e)}")
            return None
    
    def save_pickle(self, data: Any, filename: str, subdir: str = None) -> bool:
        """
        שמירת נתונים בפורמט Pickle
        
        Args:
            data: נתונים לשמירה
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            
        Returns:
            True אם השמירה הצליחה, False אחרת
        """
        try:
            filepath = self._get_filepath(filename, subdir, '.pkl')
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Pickle data saved successfully: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving pickle data: {str(e)}")
            return False
    
    def load_pickle(self, filename: str, subdir: str = None) -> Optional[Any]:
        """
        טעינת נתונים מפורמט Pickle
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            
        Returns:
            הנתונים או None אם נכשל
        """
        try:
            filepath = self._get_filepath(filename, subdir, '.pkl')
            
            if not filepath.exists():
                logger.warning(f"Pickle file not found: {filepath}")
                return None
            
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            logger.info(f"Pickle data loaded successfully: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading pickle data: {str(e)}")
            return None
    
    def save_excel(self, data: pd.DataFrame, filename: str, subdir: str = None, 
                  sheet_name: str = 'Sheet1') -> bool:
        """
        שמירת נתונים בפורמט Excel
        
        Args:
            data: DataFrame לשמירה
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            sheet_name: שם הגיליון
            
        Returns:
            True אם השמירה הצליחה, False אחרת
        """
        try:
            filepath = self._get_filepath(filename, subdir, '.xlsx')
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=True)
            
            logger.info(f"Excel data saved successfully: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving Excel data: {str(e)}")
            return False
    
    def load_excel(self, filename: str, subdir: str = None, sheet_name: str = None, 
                  **kwargs) -> Optional[pd.DataFrame]:
        """
        טעינת נתונים מפורמט Excel
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            sheet_name: שם הגיליון (אופציונלי)
            **kwargs: פרמטרים נוספים ל-pd.read_excel
            
        Returns:
            DataFrame או None אם נכשל
        """
        try:
            filepath = self._get_filepath(filename, subdir, '.xlsx')
            
            if not filepath.exists():
                logger.warning(f"Excel file not found: {filepath}")
                return None
            
            data = pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)
            
            logger.info(f"Excel data loaded successfully: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading Excel data: {str(e)}")
            return None
    
    def backup_file(self, filename: str, subdir: str = None, backup_suffix: str = None) -> bool:
        """
        גיבוי קובץ
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            backup_suffix: סיומת גיבוי (אופציונלי)
            
        Returns:
            True אם הגיבוי הצליח, False אחרת
        """
        try:
            source_path = self._get_filepath(filename, subdir)
            
            if not source_path.exists():
                logger.warning(f"Source file not found for backup: {source_path}")
                return False
            
            # יצירת שם קובץ גיבוי
            if backup_suffix is None:
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            backup_filename = f"{source_path.stem}_{backup_suffix}{source_path.suffix}"
            backup_path = self.subdirs['backup'] / backup_filename
            
            # העתקת הקובץ
            shutil.copy2(source_path, backup_path)
            
            logger.info(f"File backed up successfully: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error backing up file: {str(e)}")
            return False
    
    def archive_files(self, file_pattern: str, subdir: str = None, 
                     archive_name: str = None) -> bool:
        """
        ארכוב קבצים
        
        Args:
            file_pattern: תבנית קבצים לארכוב
            subdir: תיקייה משנה (אופציונלי)
            archive_name: שם הארכיון (אופציונלי)
            
        Returns:
            True אם הארכוב הצליח, False אחרת
        """
        try:
            # קביעת תיקיית מקור
            source_dir = self.subdirs.get(subdir, self.base_dir) if subdir else self.base_dir
            
            # קביעת שם ארכיון
            if archive_name is None:
                archive_name = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            archive_path = self.subdirs['archive'] / f"{archive_name}.zip"
            
            # יצירת ארכיון
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in source_dir.glob(file_pattern):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.name)
            
            logger.info(f"Files archived successfully: {archive_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error archiving files: {str(e)}")
            return False
    
    def compress_file(self, filename: str, subdir: str = None) -> bool:
        """
        דחיסת קובץ
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            
        Returns:
            True אם הדחיסה הצליחה, False אחרת
        """
        try:
            source_path = self._get_filepath(filename, subdir)
            
            if not source_path.exists():
                logger.warning(f"Source file not found for compression: {source_path}")
                return False
            
            compressed_path = source_path.with_suffix(source_path.suffix + '.gz')
            
            with open(source_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"File compressed successfully: {compressed_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error compressing file: {str(e)}")
            return False
    
    def decompress_file(self, filename: str, subdir: str = None) -> bool:
        """
        חילוץ קובץ דחוס
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            
        Returns:
            True אם החילוץ הצליח, False אחרת
        """
        try:
            source_path = self._get_filepath(filename, subdir)
            
            if not source_path.exists():
                logger.warning(f"Source file not found for decompression: {source_path}")
                return False
            
            if not source_path.suffix.endswith('.gz'):
                logger.warning(f"File is not compressed: {source_path}")
                return False
            
            decompressed_path = source_path.with_suffix(source_path.suffix[:-3])
            
            with gzip.open(source_path, 'rb') as f_in:
                with open(decompressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"File decompressed successfully: {decompressed_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error decompressing file: {str(e)}")
            return False
    
    def list_files(self, subdir: str = None, pattern: str = "*") -> List[Path]:
        """
        רשימת קבצים
        
        Args:
            subdir: תיקייה משנה (אופציונלי)
            pattern: תבנית קבצים
            
        Returns:
            רשימת קבצים
        """
        try:
            target_dir = self.subdirs.get(subdir, self.base_dir) if subdir else self.base_dir
            files = list(target_dir.glob(pattern))
            
            logger.info(f"Found {len(files)} files in {target_dir}")
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    def delete_file(self, filename: str, subdir: str = None) -> bool:
        """
        מחיקת קובץ
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            
        Returns:
            True אם המחיקה הצליחה, False אחרת
        """
        try:
            filepath = self._get_filepath(filename, subdir)
            
            if not filepath.exists():
                logger.warning(f"File not found for deletion: {filepath}")
                return False
            
            filepath.unlink()
            
            logger.info(f"File deleted successfully: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def move_file(self, filename: str, source_subdir: str = None, 
                 target_subdir: str = None, new_filename: str = None) -> bool:
        """
        העברת קובץ
        
        Args:
            filename: שם הקובץ
            source_subdir: תיקיית מקור (אופציונלי)
            target_subdir: תיקיית יעד (אופציונלי)
            new_filename: שם קובץ חדש (אופציונלי)
            
        Returns:
            True אם ההעברה הצליחה, False אחרת
        """
        try:
            source_path = self._get_filepath(filename, source_subdir)
            
            if not source_path.exists():
                logger.warning(f"Source file not found for move: {source_path}")
                return False
            
            # קביעת שם קובץ יעד
            if new_filename is None:
                new_filename = filename
            
            target_path = self._get_filepath(new_filename, target_subdir)
            
            # העברת הקובץ
            shutil.move(str(source_path), str(target_path))
            
            logger.info(f"File moved successfully: {source_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving file: {str(e)}")
            return False
    
    def copy_file(self, filename: str, source_subdir: str = None, 
                 target_subdir: str = None, new_filename: str = None) -> bool:
        """
        העתקת קובץ
        
        Args:
            filename: שם הקובץ
            source_subdir: תיקיית מקור (אופציונלי)
            target_subdir: תיקיית יעד (אופציונלי)
            new_filename: שם קובץ חדש (אופציונלי)
            
        Returns:
            True אם ההעתקה הצליחה, False אחרת
        """
        try:
            source_path = self._get_filepath(filename, source_subdir)
            
            if not source_path.exists():
                logger.warning(f"Source file not found for copy: {source_path}")
                return False
            
            # קביעת שם קובץ יעד
            if new_filename is None:
                new_filename = filename
            
            target_path = self._get_filepath(new_filename, target_subdir)
            
            # העתקת הקובץ
            shutil.copy2(str(source_path), str(target_path))
            
            logger.info(f"File copied successfully: {source_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error copying file: {str(e)}")
            return False
    
    def get_file_info(self, filename: str, subdir: str = None) -> Optional[Dict[str, Any]]:
        """
        קבלת מידע על קובץ
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            
        Returns:
            מילון עם מידע על הקובץ או None
        """
        try:
            filepath = self._get_filepath(filename, subdir)
            
            if not filepath.exists():
                logger.warning(f"File not found: {filepath}")
                return None
            
            stat = filepath.stat()
            
            info = {
                'name': filepath.name,
                'path': str(filepath),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': filepath.suffix,
                'is_file': filepath.is_file(),
                'is_dir': filepath.is_dir()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None
    
    def cleanup_temp_files(self, max_age_days: int = 7) -> int:
        """
        ניקוי קבצים זמניים ישנים
        
        Args:
            max_age_days: גיל מקסימלי בימים
            
        Returns:
            מספר הקבצים שנמחקו
        """
        try:
            temp_dir = self.subdirs['temp']
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            deleted_count = 0
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old temp files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
            return 0
    
    def _get_filepath(self, filename: str, subdir: str = None, extension: str = None) -> Path:
        """
        קבלת נתיב קובץ מלא
        
        Args:
            filename: שם הקובץ
            subdir: תיקייה משנה (אופציונלי)
            extension: סיומת (אופציונלי)
            
        Returns:
            נתיב קובץ מלא
        """
        if subdir:
            target_dir = self.subdirs.get(subdir, self.base_dir)
        else:
            target_dir = self.base_dir
        
        if extension and not filename.endswith(extension):
            filename += extension
        
        return target_dir / filename

# פונקציות עזר גלובליות
def save_data(data: Any, filename: str, format_type: str = 'json', 
              base_dir: str = "data", subdir: str = None) -> bool:
    """
    שמירת נתונים בפורמט מסוים
    
    Args:
        data: נתונים לשמירה
        filename: שם הקובץ
        format_type: סוג פורמט ('json', 'csv', 'pickle', 'excel')
        base_dir: תיקייה בסיסית
        subdir: תיקייה משנה
        
    Returns:
        True אם השמירה הצליחה, False אחרת
    """
    file_manager = FileManager(base_dir)
    
    if format_type == 'json':
        return file_manager.save_json(data, filename, subdir)
    elif format_type == 'csv':
        if isinstance(data, pd.DataFrame):
            return file_manager.save_csv(data, filename, subdir)
        else:
            logger.error("Data must be DataFrame for CSV format")
            return False
    elif format_type == 'pickle':
        return file_manager.save_pickle(data, filename, subdir)
    elif format_type == 'excel':
        if isinstance(data, pd.DataFrame):
            return file_manager.save_excel(data, filename, subdir)
        else:
            logger.error("Data must be DataFrame for Excel format")
            return False
    else:
        logger.error(f"Unsupported format type: {format_type}")
        return False

def load_data(filename: str, format_type: str = 'json', 
              base_dir: str = "data", subdir: str = None, **kwargs) -> Optional[Any]:
    """
    טעינת נתונים מפורמט מסוים
    
    Args:
        filename: שם הקובץ
        format_type: סוג פורמט ('json', 'csv', 'pickle', 'excel')
        base_dir: תיקייה בסיסית
        subdir: תיקייה משנה
        **kwargs: פרמטרים נוספים
        
    Returns:
        הנתונים או None אם נכשל
    """
    file_manager = FileManager(base_dir)
    
    if format_type == 'json':
        return file_manager.load_json(filename, subdir)
    elif format_type == 'csv':
        return file_manager.load_csv(filename, subdir, **kwargs)
    elif format_type == 'pickle':
        return file_manager.load_pickle(filename, subdir)
    elif format_type == 'excel':
        return file_manager.load_excel(filename, subdir, **kwargs)
    else:
        logger.error(f"Unsupported format type: {format_type}")
        return None

def backup_data(filename: str, base_dir: str = "data", subdir: str = None) -> bool:
    """
    גיבוי נתונים
    
    Args:
        filename: שם הקובץ
        base_dir: תיקייה בסיסית
        subdir: תיקייה משנה
        
    Returns:
        True אם הגיבוי הצליח, False אחרת
    """
    file_manager = FileManager(base_dir)
    return file_manager.backup_file(filename, subdir)

def archive_data(file_pattern: str, base_dir: str = "data", 
                subdir: str = None, archive_name: str = None) -> bool:
    """
    ארכוב נתונים
    
    Args:
        file_pattern: תבנית קבצים
        base_dir: תיקייה בסיסית
        subdir: תיקייה משנה
        archive_name: שם הארכיון
        
    Returns:
        True אם הארכוב הצליח, False אחרת
    """
    file_manager = FileManager(base_dir)
    return file_manager.archive_files(file_pattern, subdir, archive_name)

class DataFileHandler:
    """
    מנהל קבצי נתונים מותאם למערכת
    """
    
    def __init__(self, base_dir: str = "data"):
        """
        אתחול מנהל קבצי נתונים
        
        Args:
            base_dir: תיקייה בסיסית
        """
        self.file_manager = FileManager(base_dir)
        self.logger = get_system_logger("data_file_handler")
    
    def save_stock_data(self, symbol: str, data: pd.DataFrame, data_type: str = "price") -> bool:
        """
        שמירת נתוני מניה
        
        Args:
            symbol: סמל המניה
            data: נתונים לשמירה
            data_type: סוג הנתונים ('price', 'volume', 'technical')
            
        Returns:
            True אם השמירה הצליחה, False אחרת
        """
        try:
            filename = f"{symbol}_{data_type}.csv"
            subdir = f"{data_type}_data"
            
            success = self.file_manager.save_csv(data, filename, subdir)
            
            if success:
                self.logger.info(f"Stock data saved: {symbol} - {data_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving stock data: {str(e)}")
            return False
    
    def load_stock_data(self, symbol: str, data_type: str = "price") -> Optional[pd.DataFrame]:
        """
        טעינת נתוני מניה
        
        Args:
            symbol: סמל המניה
            data_type: סוג הנתונים ('price', 'volume', 'technical')
            
        Returns:
            DataFrame או None אם נכשל
        """
        try:
            filename = f"{symbol}_{data_type}.csv"
            subdir = f"{data_type}_data"
            
            data = self.file_manager.load_csv(filename, subdir)
            
            if data is not None:
                self.logger.info(f"Stock data loaded: {symbol} - {data_type}")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading stock data: {str(e)}")
            return None
    
    def save_analysis_result(self, symbol: str, result: Dict[str, Any]) -> bool:
        """
        שמירת תוצאת ניתוח
        
        Args:
            symbol: סמל המניה
            result: תוצאת הניתוח
            
        Returns:
            True אם השמירה הצליחה, False אחרת
        """
        try:
            filename = f"{symbol}_analysis.json"
            subdir = "analysis_results"
            
            success = self.file_manager.save_json(result, filename, subdir)
            
            if success:
                self.logger.info(f"Analysis result saved: {symbol}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving analysis result: {str(e)}")
            return False
    
    def load_analysis_result(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        טעינת תוצאת ניתוח
        
        Args:
            symbol: סמל המניה
            
        Returns:
            תוצאת הניתוח או None אם נכשל
        """
        try:
            filename = f"{symbol}_analysis.json"
            subdir = "analysis_results"
            
            result = self.file_manager.load_json(filename, subdir)
            
            if result is not None:
                self.logger.info(f"Analysis result loaded: {symbol}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error loading analysis result: {str(e)}")
            return None
    
    def save_agent_config(self, agent_name: str, config: Dict[str, Any]) -> bool:
        """
        שמירת תצורת סוכן
        
        Args:
            agent_name: שם הסוכן
            config: תצורת הסוכן
            
        Returns:
            True אם השמירה הצליחה, False אחרת
        """
        try:
            filename = f"{agent_name}_config.json"
            subdir = "agent_configs"
            
            success = self.file_manager.save_json(config, filename, subdir)
            
            if success:
                self.logger.info(f"Agent config saved: {agent_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving agent config: {str(e)}")
            return False
    
    def load_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        טעינת תצורת סוכן
        
        Args:
            agent_name: שם הסוכן
            
        Returns:
            תצורת הסוכן או None אם נכשל
        """
        try:
            filename = f"{agent_name}_config.json"
            subdir = "agent_configs"
            
            config = self.file_manager.load_json(filename, subdir)
            
            if config is not None:
                self.logger.info(f"Agent config loaded: {agent_name}")
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading agent config: {str(e)}")
            return None

# יצירת מופע ברירת מחדל
file_manager = FileManager()
data_file_handler = DataFileHandler()