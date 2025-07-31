#!/usr/bin/env python3
"""
Calculate All Indicators - חישוב אינדיקטורים טכניים לכל המניות
מחשב אינדיקטורים טכניים עבור כל המניות הזמינות
"""

import os
import sys
import pandas as pd
import numpy as np
import gzip
import json
from datetime import datetime
from pathlib import Path
import time
import logging
from typing import Dict, List, Optional

# הוספת הנתיב לפרויקט
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# הגדרת לוגר
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TechnicalIndicatorsCalculator:
    """מחלקה לחישוב אינדיקטורים טכניים"""
    
    def __init__(self):
        # הגדרת תיקיות
        self.data_dir = Path("data")
        self.daily_dir = self.data_dir / "historical_prices" / "daily"
        self.indicators_dir = self.data_dir / "technical_indicators"
        
        # יצירת תיקיות אינדיקטורים
        self.indicators = {
            'rsi': {'periods': [14, 21]},
            'macd': {'periods': [12, 26, 9]},
            'bollinger': {'periods': [20]},
            'sma': {'periods': [20, 50, 200]},
            'ema': {'periods': [20, 50, 200]},
            'atr': {'periods': [14]},
            'stochastic': {'periods': [14]},
            'williams_r': {'periods': [14]},
            'cci': {'periods': [20]},
            'adx': {'periods': [14]}
        }
        
        self._create_indicator_directories()
    
    def _create_indicator_directories(self):
        """יוצר תיקיות לכל האינדיקטורים"""
        for indicator in self.indicators.keys():
            for timeframe in ['daily', 'weekly', 'monthly']:
                indicator_dir = self.indicators_dir / indicator / timeframe
                indicator_dir.mkdir(parents=True, exist_ok=True)
    
    def get_available_symbols(self) -> List[str]:
        """מחזיר רשימת מניות זמינות"""
        daily_files = list(self.daily_dir.glob("*.csv.gz"))
        symbols = []
        for f in daily_files:
            # הסרת הסיומת הכפולה
            symbol = f.stem
            if symbol.endswith('.csv'):
                symbol = symbol[:-4]  # הסרת .csv
            symbols.append(symbol)
        return symbols
    
    def load_price_data(self, symbol: str, timeframe: str = "daily") -> Optional[pd.DataFrame]:
        """טוען נתוני מחירים למניה"""
        try:
            if timeframe == "daily":
                file_path = self.daily_dir / f"{symbol}.csv.gz"
            elif timeframe == "weekly":
                file_path = self.data_dir / "historical_prices" / "weekly" / f"{symbol}.csv.gz"
            elif timeframe == "monthly":
                file_path = self.data_dir / "historical_prices" / "monthly" / f"{symbol}.csv.gz"
            else:
                raise ValueError(f"תדירות לא נתמכת: {timeframe}")
            
            if not file_path.exists():
                logger.warning(f"קובץ לא קיים: {file_path}")
                return None
            
            df = pd.read_csv(file_path, compression='gzip')
            
            # טיפול בעמודת תאריך
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            elif 'Date' in df.columns:
                df['date'] = pd.to_datetime(df['Date'])
                df = df.drop('Date', axis=1)
                df = df.set_index('date')
            
            # הסרת עמודת symbol אם קיימת
            if 'symbol' in df.columns:
                df = df.drop('symbol', axis=1)
            
            # סידור לפי תאריך
            df = df.sort_index()
            
            return df
            
        except Exception as e:
            logger.error(f"שגיאה בטעינת נתונים עבור {symbol}: {e}")
            return None
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """מחשב RSI"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"שגיאה בחישוב RSI: {e}")
            return pd.Series(index=df.index)
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """מחשב MACD"""
        try:
            ema_fast = df['close'].ewm(span=fast).mean()
            ema_slow = df['close'].ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
        except Exception as e:
            logger.error(f"שגיאה בחישוב MACD: {e}")
            return {'macd': pd.Series(), 'signal': pd.Series(), 'histogram': pd.Series()}
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """מחשב Bollinger Bands"""
        try:
            sma = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return {
                'upper': upper_band,
                'middle': sma,
                'lower': lower_band
            }
        except Exception as e:
            logger.error(f"שגיאה בחישוב Bollinger Bands: {e}")
            return {'upper': pd.Series(), 'middle': pd.Series(), 'lower': pd.Series()}
    
    def calculate_sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """מחשב Simple Moving Average"""
        try:
            return df['close'].rolling(window=period).mean()
        except Exception as e:
            logger.error(f"שגיאה בחישוב SMA: {e}")
            return pd.Series(index=df.index)
    
    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """מחשב Exponential Moving Average"""
        try:
            return df['close'].ewm(span=period).mean()
        except Exception as e:
            logger.error(f"שגיאה בחישוב EMA: {e}")
            return pd.Series(index=df.index)
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """מחשב Average True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(window=period).mean()
            
            return atr
        except Exception as e:
            logger.error(f"שגיאה בחישוב ATR: {e}")
            return pd.Series(index=df.index)
    
    def calculate_stochastic(self, df: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
        """מחשב Stochastic Oscillator"""
        try:
            lowest_low = df['low'].rolling(window=period).min()
            highest_high = df['high'].rolling(window=period).max()
            
            k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=3).mean()
            
            return {
                'k': k_percent,
                'd': d_percent
            }
        except Exception as e:
            logger.error(f"שגיאה בחישוב Stochastic: {e}")
            return {'k': pd.Series(), 'd': pd.Series()}
    
    def calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """מחשב Williams %R"""
        try:
            highest_high = df['high'].rolling(window=period).max()
            lowest_low = df['low'].rolling(window=period).min()
            
            williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
            return williams_r
        except Exception as e:
            logger.error(f"שגיאה בחישוב Williams %R: {e}")
            return pd.Series(index=df.index)
    
    def calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """מחשב Commodity Channel Index"""
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            sma_tp = typical_price.rolling(window=period).mean()
            mad = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
            
            cci = (typical_price - sma_tp) / (0.015 * mad)
            return cci
        except Exception as e:
            logger.error(f"שגיאה בחישוב CCI: {e}")
            return pd.Series(index=df.index)
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
        """מחשב Average Directional Index"""
        try:
            # True Range
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            tr = np.maximum(high_low, np.maximum(high_close, low_close))
            
            # Directional Movement
            up_move = df['high'] - df['high'].shift()
            down_move = df['low'].shift() - df['low']
            
            plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
            minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
            
            # Smoothed values
            tr_smooth = tr.rolling(window=period).mean()
            plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / tr_smooth)
            minus_di = 100 * (pd.Series(minus_dm).rolling(window=period).mean() / tr_smooth)
            
            # ADX
            dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = pd.Series(dx).rolling(window=period).mean()
            
            return {
                'adx': adx,
                'plus_di': plus_di,
                'minus_di': minus_di
            }
        except Exception as e:
            logger.error(f"שגיאה בחישוב ADX: {e}")
            return {'adx': pd.Series(), 'plus_di': pd.Series(), 'minus_di': pd.Series()}
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """מחשב את כל האינדיקטורים"""
        indicators = {}
        
        # RSI
        for period in self.indicators['rsi']['periods']:
            indicators[f'rsi_{period}'] = self.calculate_rsi(df, period)
        
        # MACD
        macd_result = self.calculate_macd(df)
        indicators['macd'] = macd_result['macd']
        indicators['macd_signal'] = macd_result['signal']
        indicators['macd_histogram'] = macd_result['histogram']
        
        # Bollinger Bands
        bb_result = self.calculate_bollinger_bands(df)
        indicators['bb_upper'] = bb_result['upper']
        indicators['bb_middle'] = bb_result['middle']
        indicators['bb_lower'] = bb_result['lower']
        
        # SMA
        for period in self.indicators['sma']['periods']:
            indicators[f'sma_{period}'] = self.calculate_sma(df, period)
        
        # EMA
        for period in self.indicators['ema']['periods']:
            indicators[f'ema_{period}'] = self.calculate_ema(df, period)
        
        # ATR
        for period in self.indicators['atr']['periods']:
            indicators[f'atr_{period}'] = self.calculate_atr(df, period)
        
        # Stochastic
        stoch_result = self.calculate_stochastic(df)
        indicators['stoch_k'] = stoch_result['k']
        indicators['stoch_d'] = stoch_result['d']
        
        # Williams %R
        for period in self.indicators['williams_r']['periods']:
            indicators[f'williams_r_{period}'] = self.calculate_williams_r(df, period)
        
        # CCI
        for period in self.indicators['cci']['periods']:
            indicators[f'cci_{period}'] = self.calculate_cci(df, period)
        
        # ADX
        adx_result = self.calculate_adx(df)
        indicators['adx'] = adx_result['adx']
        indicators['plus_di'] = adx_result['plus_di']
        indicators['minus_di'] = adx_result['minus_di']
        
        # המרה ל-DataFrame
        result_df = pd.DataFrame(indicators, index=df.index)
        result_df = result_df.dropna()
        
        return result_df
    
    def save_indicators(self, indicators_df: pd.DataFrame, symbol: str, indicator_name: str, timeframe: str):
        """שומר אינדיקטורים לקובץ"""
        try:
            if indicators_df.empty:
                return False
            
            # יצירת DataFrame עם תאריך
            result_df = indicators_df.reset_index()
            result_df['symbol'] = symbol
            
            # שמירה דחוסה
            file_path = self.indicators_dir / indicator_name / timeframe / f"{symbol}.csv.gz"
            result_df.to_csv(file_path, compression='gzip', index=False)
            
            logger.info(f"✅ נשמר {symbol} - {indicator_name} ({timeframe}): {len(result_df)} שורות")
            return True
            
        except Exception as e:
            logger.error(f"שגיאה בשמירת {symbol} - {indicator_name}: {e}")
            return False
    
    def process_symbol(self, symbol: str, timeframes: List[str] = None):
        """מעבד מניה אחת"""
        if timeframes is None:
            timeframes = ['daily']
        
        results = {}
        
        for timeframe in timeframes:
            logger.info(f"מעבד {symbol} ({timeframe})...")
            
            # טעינת נתוני מחירים
            price_df = self.load_price_data(symbol, timeframe)
            
            if price_df is None or price_df.empty:
                logger.warning(f"אין נתונים עבור {symbol} ({timeframe})")
                continue
            
            # חישוב אינדיקטורים
            indicators_df = self.calculate_all_indicators(price_df)
            
            if not indicators_df.empty:
                # שמירת אינדיקטורים לפי קטגוריות
                for indicator_name in self.indicators.keys():
                    if indicator_name == 'rsi':
                        indicator_data = indicators_df[[col for col in indicators_df.columns if col.startswith('rsi_')]]
                    elif indicator_name == 'macd':
                        indicator_data = indicators_df[['macd', 'macd_signal', 'macd_histogram']]
                    elif indicator_name == 'bollinger':
                        indicator_data = indicators_df[['bb_upper', 'bb_middle', 'bb_lower']]
                    elif indicator_name == 'sma':
                        indicator_data = indicators_df[[col for col in indicators_df.columns if col.startswith('sma_')]]
                    elif indicator_name == 'ema':
                        indicator_data = indicators_df[[col for col in indicators_df.columns if col.startswith('ema_')]]
                    elif indicator_name == 'atr':
                        indicator_data = indicators_df[[col for col in indicators_df.columns if col.startswith('atr_')]]
                    elif indicator_name == 'stochastic':
                        indicator_data = indicators_df[['stoch_k', 'stoch_d']]
                    elif indicator_name == 'williams_r':
                        indicator_data = indicators_df[[col for col in indicators_df.columns if col.startswith('williams_r_')]]
                    elif indicator_name == 'cci':
                        indicator_data = indicators_df[[col for col in indicators_df.columns if col.startswith('cci_')]]
                    elif indicator_name == 'adx':
                        indicator_data = indicators_df[['adx', 'plus_di', 'minus_di']]
                    else:
                        continue
                    
                    if not indicator_data.empty:
                        self.save_indicators(indicator_data, symbol, indicator_name, timeframe)
                
                results[timeframe] = len(indicators_df)
                logger.info(f"✅ הושלם {symbol} ({timeframe}): {len(indicators_df)} שורות")
            else:
                logger.warning(f"אין אינדיקטורים עבור {symbol} ({timeframe})")
        
        return results
    
    def process_all_symbols(self, symbols: List[str] = None, timeframes: List[str] = None):
        """מעבד את כל המניות"""
        if symbols is None:
            symbols = self.get_available_symbols()
        
        if timeframes is None:
            timeframes = ['daily']
        
        logger.info(f"מתחיל עיבוד {len(symbols)} מניות...")
        
        results = {
            'success': [],
            'failed': [],
            'stats': {
                'total_symbols': len(symbols),
                'total_indicators': len(self.indicators),
                'total_timeframes': len(timeframes)
            }
        }
        
        for i, symbol in enumerate(symbols, 1):
            logger.info(f"מעבד {symbol} ({i}/{len(symbols)})...")
            
            try:
                symbol_results = self.process_symbol(symbol, timeframes)
                
                if symbol_results:
                    results['success'].append(symbol)
                    logger.info(f"✅ הושלם {symbol}")
                else:
                    results['failed'].append(symbol)
                    logger.warning(f"❌ נכשל {symbol}")
                
                # השהייה בין מניות
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"שגיאה בעיבוד {symbol}: {e}")
                results['failed'].append(symbol)
        
        return results
    
    def print_summary(self, results: dict):
        """מדפיס סיכום התוצאות"""
        print("\n" + "="*60)
        print("📊 סיכום חישוב אינדיקטורים טכניים")
        print("="*60)
        print(f"📈 מניות שהושלמו: {len(results['success'])}")
        print(f"❌ מניות שנכשלו: {len(results['failed'])}")
        print(f"📊 אינדיקטורים: {results['stats']['total_indicators']}")
        print(f"📅 תדירויות: {results['stats']['total_timeframes']}")
        
        if results['success']:
            print(f"\n✅ מניות שהושלמו: {', '.join(results['success'][:10])}{'...' if len(results['success']) > 10 else ''}")
        
        if results['failed']:
            print(f"\n❌ מניות שנכשלו: {', '.join(results['failed'])}")

def main():
    """פונקציה ראשית"""
    print("🚀 מתחיל חישוב אינדיקטורים טכניים...")
    
    calculator = TechnicalIndicatorsCalculator()
    
    # קבלת רשימת מניות זמינות
    available_symbols = calculator.get_available_symbols()
    print(f"📋 מניות זמינות: {len(available_symbols)}")
    
    if not available_symbols:
        print("❌ אין מניות זמינות!")
        return
    
    # עיבוד כל המניות
    results = calculator.process_all_symbols(available_symbols, ['daily'])
    
    # הדפסת סיכום
    calculator.print_summary(results)
    
    print("\n🎉 חישוב אינדיקטורים טכניים הושלם!")

if __name__ == "__main__":
    main() 