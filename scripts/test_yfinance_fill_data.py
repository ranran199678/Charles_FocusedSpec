#!/usr/bin/env python3
"""
סקריפט ניסיון למילוי נתונים מ-yfinance עבור 3 מניות בלבד
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import time
import json

class YFinanceTestFiller:
    """מחלקה למילוי נתונים מ-yfinance - גרסת ניסיון"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self._ensure_directories()
        
    def _ensure_directories(self):
        """יצירת תיקיות נדרשות"""
        directories = [
            f"{self.base_dir}/historical_prices/daily",
            f"{self.base_dir}/technical_indicators/rsi/daily",
            f"{self.base_dir}/technical_indicators/macd/daily",
            f"{self.base_dir}/technical_indicators/bollinger/daily",
            f"{self.base_dir}/technical_indicators/sma/daily",
            f"{self.base_dir}/fundamentals/company_info",
            f"{self.base_dir}/news_sentiment/financial_news",
            f"{self.base_dir}/market_data/indices",
            f"{self.base_dir}/metadata"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ תיקייה נוצרה: {directory}")
    
    def test_fill_data(self, symbols: list = None, years: int = 2):
        """ניסיון מילוי נתונים עבור 3 מניות"""
        
        if symbols is None:
            symbols = ['AAPL', 'MSFT', 'TSLA']  # 3 מניות לניסיון
        
        print(f"🎯 מתחיל ניסיון מילוי נתונים עבור {len(symbols)} מניות...")
        print(f"📊 מניות: {', '.join(symbols)}")
        print(f"📅 תקופה: {years} שנים")
        print("=" * 60)
        
        start_time = time.time()
        results = {}
        
        for i, symbol in enumerate(symbols, 1):
            print(f"\n📈 [{i}/{len(symbols)}] עובד על {symbol}...")
            
            symbol_results = {
                'prices': False,
                'technical': False,
                'fundamentals': False,
                'news': False,
                'rows_count': 0
            }
            
            try:
                # 1. נתוני מחירים
                print(f"  🔄 מוריד נתוני מחירים...")
                price_success, rows = self._download_price_data(symbol, years)
                symbol_results['prices'] = price_success
                symbol_results['rows_count'] = rows
                
                if price_success:
                    # 2. אינדיקטורים טכניים
                    print(f"  📊 מחשב אינדיקטורים טכניים...")
                    tech_success = self._calculate_technical_indicators(symbol, years)
                    symbol_results['technical'] = tech_success
                    
                    # 3. נתונים פיננסיים
                    print(f"  💰 מוריד נתונים פיננסיים...")
                    fund_success = self._download_fundamental_data(symbol)
                    symbol_results['fundamentals'] = fund_success
                    
                    # 4. חדשות
                    print(f"  📰 מוריד חדשות...")
                    news_success = self._download_news_data(symbol)
                    symbol_results['news'] = news_success
                
                results[symbol] = symbol_results
                
                # סיכום ביניים
                success_count = sum([symbol_results['prices'], symbol_results['technical'], 
                                   symbol_results['fundamentals'], symbol_results['news']])
                print(f"  ✅ {symbol}: {success_count}/4 סוגי נתונים הצליחו ({rows} שורות)")
                
            except Exception as e:
                print(f"  ❌ {symbol}: שגיאה - {e}")
                results[symbol] = symbol_results
        
        # מילוי נתוני מדדים
        print(f"\n📊 מוריד נתוני מדדים...")
        market_success = self._download_market_data()
        
        # יצירת מטא-דאטה
        print(f"\n📋 יוצר מטא-דאטה...")
        self._create_metadata(symbols, results)
        
        end_time = time.time()
        
        # סיכום סופי
        self._print_summary(results, end_time - start_time, market_success)
        
        return results
    
    def _download_price_data(self, symbol: str, years: int):
        """הורדת נתוני מחירים"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f"{years}y")
            
            if not hist.empty:
                # המרה לפורמט הנדרש
                df = hist.reset_index()
                df['date'] = df['Date'].dt.strftime('%Y-%m-%d')
                df['symbol'] = symbol
                
                columns_mapping = {
                    'Open': 'open',
                    'High': 'high', 
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume',
                    'Adj Close': 'adjusted_close'
                }
                
                df = df.rename(columns=columns_mapping)
                df = df[['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'adjusted_close']]
                
                # שמירה
                file_path = f"{self.base_dir}/historical_prices/daily/{symbol}.csv"
                df.to_csv(file_path, index=False)
                
                print(f"    ✅ מחירים: {len(df)} שורות נשמרו")
                return True, len(df)
            else:
                print(f"    ❌ מחירים: אין נתונים")
                return False, 0
                
        except Exception as e:
            print(f"    ❌ מחירים: שגיאה - {e}")
            return False, 0
    
    def _calculate_technical_indicators(self, symbol: str, years: int):
        """חישוב אינדיקטורים טכניים"""
        try:
            # קריאת נתוני מחירים
            file_path = f"{self.base_dir}/historical_prices/daily/{symbol}.csv"
            if not os.path.exists(file_path):
                print(f"    ❌ אינדיקטורים: קובץ מחירים לא נמצא")
                return False
            
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            
            close = df['close']
            high = df['high']
            low = df['low']
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            # Bollinger Bands
            sma_20 = close.rolling(20).mean()
            std_20 = close.rolling(20).std()
            upper_band = sma_20 + (std_20 * 2)
            lower_band = sma_20 - (std_20 * 2)
            
            # SMA & EMA
            sma_20 = close.rolling(20).mean()
            ema_20 = close.ewm(span=20).mean()
            
            # שמירת אינדיקטורים
            indicators = {
                'rsi': rsi,
                'macd': macd,
                'bollinger': upper_band,  # רק העליון לדוגמה
                'sma': sma_20,
                'ema': ema_20
            }
            
            saved_count = 0
            for indicator_name, indicator_data in indicators.items():
                indicator_df = pd.DataFrame({
                    'date': df.index.strftime('%Y-%m-%d'),
                    'symbol': symbol,
                    'value': indicator_data.values,
                    'period': 14 if indicator_name == 'rsi' else 20
                })
                
                # הסרת שורות עם NaN
                indicator_df = indicator_df.dropna()
                
                if not indicator_df.empty:
                    file_path = f"{self.base_dir}/technical_indicators/{indicator_name}/daily/{symbol}_{indicator_name}.csv"
                    indicator_df.to_csv(file_path, index=False)
                    saved_count += 1
            
            print(f"    ✅ אינדיקטורים: {saved_count} אינדיקטורים נשמרו")
            return True
            
        except Exception as e:
            print(f"    ❌ אינדיקטורים: שגיאה - {e}")
            return False
    
    def _download_fundamental_data(self, symbol: str):
        """הורדת נתונים פיננסיים"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            financial_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'symbol': symbol,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'price_to_book': info.get('priceToBook', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'employees': info.get('fullTimeEmployees', 0),
                'long_name': info.get('longName', symbol)
            }
            
            df = pd.DataFrame([financial_data])
            file_path = f"{self.base_dir}/fundamentals/company_info/{symbol}_info.csv"
            df.to_csv(file_path, index=False)
            
            print(f"    ✅ פיננסיים: נתונים נשמרו")
            return True
            
        except Exception as e:
            print(f"    ❌ פיננסיים: שגיאה - {e}")
            return False
    
    def _download_news_data(self, symbol: str):
        """הורדת חדשות"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if news:
                news_data = []
                for article in news:
                    news_data.append({
                        'date': datetime.fromtimestamp(article.get('providerPublishTime', 0)).strftime('%Y-%m-%d'),
                        'symbol': symbol,
                        'headline': article.get('title', ''),
                        'summary': article.get('summary', ''),
                        'source': article.get('publisher', ''),
                        'url': article.get('link', ''),
                        'category': 'general'
                    })
                
                df = pd.DataFrame(news_data)
                file_path = f"{self.base_dir}/news_sentiment/financial_news/{symbol}_news.csv"
                df.to_csv(file_path, index=False)
                
                print(f"    ✅ חדשות: {len(news_data)} חדשות נשמרו")
                return True
            else:
                print(f"    ⚠️ חדשות: אין חדשות זמינות")
                return False
                
        except Exception as e:
            print(f"    ❌ חדשות: שגיאה - {e}")
            return False
    
    def _download_market_data(self):
        """הורדת נתוני מדדים"""
        indices = ['^GSPC', '^IXIC', '^DJI']  # S&P 500, NASDAQ, Dow Jones
        
        success_count = 0
        for index in indices:
            try:
                ticker = yf.Ticker(index)
                hist = ticker.history(period="2y")
                
                if not hist.empty:
                    df = hist.reset_index()
                    df['date'] = df['Date'].dt.strftime('%Y-%m-%d')
                    df['index_symbol'] = index.replace('^', '')
                    
                    columns_mapping = {
                        'Open': 'open',
                        'High': 'high', 
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    }
                    
                    df = df.rename(columns=columns_mapping)
                    df = df[['date', 'index_symbol', 'open', 'high', 'low', 'close', 'volume']]
                    
                    file_path = f"{self.base_dir}/market_data/indices/{index.replace('^', '')}.csv"
                    df.to_csv(file_path, index=False)
                    
                    print(f"    ✅ מדד {index}: {len(df)} שורות")
                    success_count += 1
                    
            except Exception as e:
                print(f"    ❌ מדד {index}: שגיאה - {e}")
        
        return success_count > 0
    
    def _create_metadata(self, symbols: list, results: dict):
        """יצירת מטא-דאטה"""
        metadata = {
            'created_date': datetime.now().isoformat(),
            'test_run': True,
            'total_symbols': len(symbols),
            'symbols': symbols,
            'results': results,
            'data_types': ['prices', 'technical_indicators', 'fundamentals', 'news', 'market_data'],
            'period_years': 2
        }
        
        file_path = f"{self.base_dir}/metadata/test_data_status.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"    ✅ מטא-דאטה: נשמר לקובץ {file_path}")
    
    def _print_summary(self, results: dict, duration: float, market_success: bool):
        """הדפסת סיכום"""
        print("\n" + "=" * 60)
        print("📊 סיכום הניסיון")
        print("=" * 60)
        
        total_symbols = len(results)
        successful_symbols = sum(1 for r in results.values() if r['prices'])
        total_rows = sum(r['rows_count'] for r in results.values())
        
        print(f"⏱️ זמן כולל: {duration:.2f} שניות")
        print(f"📈 מניות: {successful_symbols}/{total_symbols} הצליחו")
        print(f"📊 שורות נתונים: {total_rows:,}")
        print(f"📰 מדדים: {'✅' if market_success else '❌'}")
        
        print(f"\n📋 פירוט לפי מניה:")
        for symbol, result in results.items():
            success_count = sum([result['prices'], result['technical'], 
                               result['fundamentals'], result['news']])
            status = "✅" if result['prices'] else "❌"
            print(f"  {status} {symbol}: {success_count}/4 סוגים ({result['rows_count']} שורות)")
        
        print(f"\n🎯 השלב הבא: אם הניסיון הצליח, נריץ על כל המניות!")

def main():
    """הפונקציה הראשית"""
    print("🚀 מתחיל ניסיון מילוי נתונים מ-yfinance")
    print("=" * 60)
    
    # יצירת מופע
    filler = YFinanceTestFiller()
    
    # רשימת 3 מניות לניסיון
    test_symbols = ['AAPL', 'MSFT', 'TSLA']
    
    # הרצת הניסיון
    results = filler.test_fill_data(test_symbols, years=2)
    
    print(f"\n🎉 הניסיון הושלם!")
    print(f"📁 בדוק את התיקיות ב-data/ כדי לראות את הנתונים")

if __name__ == "__main__":
    main() 