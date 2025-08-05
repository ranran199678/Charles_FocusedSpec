import os
import csv
from datetime import datetime

def log_forecast(symbol, expected_return, std_dev, confidence_interval, model_used, forecast_prices, run_date=None):
    """
    שומר תחזית תחזיות לקובץ CSV מתגלגל – עבור כל הרצה.

    :param symbol: סימול המניה (למשל: 'QBTS')
    :param expected_return: תחזית תשואה (float)
    :param std_dev: סטיית תקן של התחזית
    :param confidence_interval: טווח ביטחון [low, high]
    :param model_used: שם המודל (למשל 'boosting')
    :param forecast_prices: רשימת מחירים חזויים לימים הקרובים
    :param run_date: תאריך הריצה (אם לא מוגדר – יילקח אוטומטית עכשיו)
    """
    run_date = run_date or datetime.now().strftime("%Y-%m-%d")
    ci_low, ci_high = confidence_interval

    # הגדרת התיקייה והקובץ
    log_dir = os.path.join(os.path.dirname(__file__), "..", "outputs", "forecast_logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "forecast_log.csv")

    # יצירת כותרת (אם הקובץ לא קיים)
    file_exists = os.path.exists(log_file)
    num_days = len(forecast_prices)

    with open(log_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        if not file_exists:
            headers = [
                "timestamp", "symbol", "expected_return", "std_dev", "ci_low", "ci_high", "model"
            ] + [f"day_{i+1}_price" for i in range(num_days)]
            writer.writerow(headers)

        row = [
            run_date, symbol, round(expected_return, 6), round(std_dev, 6),
            round(ci_low, 6), round(ci_high, 6), model_used
        ] + [round(p, 4) for p in forecast_prices]

        writer.writerow(row)

    print(f"📝 התחזית נשמרה בהצלחה בקובץ: {log_file}")

class ForecastLogger:
    """
    מחלקת לוג תחזיות מתקדמת
    """
    
    def __init__(self, log_dir: str = None):
        """
        אתחול לוגר תחזיות
        
        Args:
            log_dir: תיקיית לוגים (אופציונלי)
        """
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(__file__), "..", "outputs", "forecast_logs")
        
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "forecast_log.csv")
    
    def log_forecast(self, symbol: str, expected_return: float, std_dev: float, 
                    confidence_interval: list, model_used: str, forecast_prices: list, 
                    run_date: str = None) -> bool:
        """
        שמירת תחזית לקובץ CSV
        
        Args:
            symbol: סמל המניה
            expected_return: תחזית תשואה
            std_dev: סטיית תקן
            confidence_interval: טווח ביטחון [low, high]
            model_used: שם המודל
            forecast_prices: רשימת מחירים חזויים
            run_date: תאריך הריצה
            
        Returns:
            True אם השמירה הצליחה, False אחרת
        """
        try:
            run_date = run_date or datetime.now().strftime("%Y-%m-%d")
            ci_low, ci_high = confidence_interval
            
            # יצירת כותרת (אם הקובץ לא קיים)
            file_exists = os.path.exists(self.log_file)
            num_days = len(forecast_prices)
            
            with open(self.log_file, mode='a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                if not file_exists:
                    headers = [
                        "timestamp", "symbol", "expected_return", "std_dev", "ci_low", "ci_high", "model"
                    ] + [f"day_{i+1}_price" for i in range(num_days)]
                    writer.writerow(headers)
                
                row = [
                    run_date, symbol, round(expected_return, 6), round(std_dev, 6),
                    round(ci_low, 6), round(ci_high, 6), model_used
                ] + [round(p, 4) for p in forecast_prices]
                
                writer.writerow(row)
            
            print(f"📝 התחזית נשמרה בהצלחה בקובץ: {self.log_file}")
            return True
            
        except Exception as e:
            print(f"❌ שגיאה בשמירת תחזית: {e}")
            return False
    
    def get_forecast_history(self, symbol: str = None, limit: int = 100) -> list:
        """
        קבלת היסטוריית תחזיות
        
        Args:
            symbol: סמל המניה (אופציונלי)
            limit: מספר רשומות מקסימלי
            
        Returns:
            רשימת תחזיות
        """
        try:
            if not os.path.exists(self.log_file):
                return []
            
            forecasts = []
            with open(self.log_file, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if symbol is None or row['symbol'] == symbol:
                        forecasts.append(row)
                        if len(forecasts) >= limit:
                            break
            
            return forecasts
            
        except Exception as e:
            print(f"❌ שגיאה בקריאת היסטוריית תחזיות: {e}")
            return []
    
    def get_latest_forecast(self, symbol: str) -> dict:
        """
        קבלת התחזית האחרונה למניה
        
        Args:
            symbol: סמל המניה
            
        Returns:
            מילון עם התחזית האחרונה או מילון ריק
        """
        forecasts = self.get_forecast_history(symbol, limit=1)
        return forecasts[0] if forecasts else {}
    
    def get_forecast_stats(self, symbol: str = None) -> dict:
        """
        קבלת סטטיסטיקות תחזיות
        
        Args:
            symbol: סמל המניה (אופציונלי)
            
        Returns:
            מילון עם סטטיסטיקות
        """
        forecasts = self.get_forecast_history(symbol)
        
        if not forecasts:
            return {}
        
        stats = {
            'total_forecasts': len(forecasts),
            'symbols': list(set(f['symbol'] for f in forecasts)),
            'models': list(set(f['model'] for f in forecasts)),
            'date_range': {
                'earliest': min(f['timestamp'] for f in forecasts),
                'latest': max(f['timestamp'] for f in forecasts)
            }
        }
        
        return stats
