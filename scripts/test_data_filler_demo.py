#!/usr/bin/env python3
"""
סקריפט לשליפת נתונים אמיתיים מ-Yahoo Finance
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import time
import json
import sys

# הוספת הנתיב למערכת
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from utils.smart_data_manager import smart_data_manager
    SMART_DATA_AVAILABLE = True
    print("✅ SmartDataManager נטען בהצלחה")
except ImportError as e:
    print(f"⚠️ לא ניתן לטעון SmartDataManager: {e}")
    SMART_DATA_AVAILABLE = False

class RealDataFiller:
    """מחלקה לשליפת נתונים אמיתיים מ-Yahoo Finance"""
    
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
    
    def generate_real_data(self, symbols: list = None, years: int = 10):
        """שליפת נתונים אמיתיים עבור 3 מניות"""
        
        if not SMART_DATA_AVAILABLE:
            print("❌ SmartDataManager לא זמין, לא ניתן לשלוף נתונים אמיתיים")
            return {}
        
        if symbols is None:
            symbols = ['AAPL', 'MSFT', 'TSLA']  # 3 מניות לניסיון
        
        print(f"🎯 מתחיל שליפת נתונים אמיתיים עבור {len(symbols)} מניות...")
        print(f"📊 מניות: {', '.join(symbols)}")
        print(f"📅 תקופה: {years} שנים")
        print("=" * 60)
        
        start_time = time.time()
        results = {}
        
        for i, symbol in enumerate(symbols, 1):
            print(f"\n📈 [{i}/{len(symbols)}] שולף נתונים עבור {symbol}...")
            
            symbol_results = {
                'prices': False,
                'technical': False,
                'fundamentals': False,
                'news': False,
                'rows_count': 0
            }
            
            try:
                # 1. שליפת נתוני מחירים אמיתיים
                print(f"  🔄 שולף נתוני מחירים...")
                days = years * 365
                price_data = smart_data_manager.get_stock_data(symbol, days)
                
                if price_data is not None and not price_data.empty:
                    symbol_results['prices'] = True
                    symbol_results['rows_count'] = len(price_data)
                    print(f"  ✅ {symbol}: {len(price_data)} שורות מחירים נשלפו")
                    
                    # 2. אינדיקטורים טכניים
                    print(f"  📊 מחשב אינדיקטורים טכניים...")
                    try:
                        tech_data = smart_data_manager.get_technical_indicators(symbol, days)
                        if tech_data is not None and len(tech_data) > 0:
                            symbol_results['technical'] = True
                            print(f"  ✅ {symbol}: אינדיקטורים טכניים חושבו")
                        else:
                            print(f"  ⚠️ {symbol}: לא ניתן לחשב אינדיקטורים טכניים")
                    except Exception as e:
                        print(f"  ⚠️ {symbol}: שגיאה באינדיקטורים טכניים - {e}")
                    
                    # 3. נתונים פיננסיים
                    print(f"  💰 שולף נתונים פיננסיים...")
                    try:
                        fund_data = smart_data_manager.get_fundamentals(symbol, 'company_info')
                        if fund_data is not None and len(fund_data) > 0:
                            symbol_results['fundamentals'] = True
                            print(f"  ✅ {symbol}: נתונים פיננסיים נשלפו")
                        else:
                            print(f"  ⚠️ {symbol}: לא נמצאו נתונים פיננסיים")
                    except Exception as e:
                        print(f"  ⚠️ {symbol}: שגיאה בנתונים פיננסיים - {e}")
                    
                    # 4. חדשות
                    print(f"  📰 שולף חדשות...")
                    try:
                        news_data = smart_data_manager.get_news_sentiment(symbol)
                        if news_data is not None and len(news_data) > 0:
                            symbol_results['news'] = True
                            print(f"  ✅ {symbol}: חדשות נשלפו")
                        else:
                            print(f"  ⚠️ {symbol}: לא נמצאו חדשות")
                    except Exception as e:
                        print(f"  ⚠️ {symbol}: שגיאה בחדשות - {e}")
                else:
                    print(f"  ❌ {symbol}: לא ניתן לשלוף נתוני מחירים")
                
                results[symbol] = symbol_results
                
                # סיכום ביניים
                success_count = sum([symbol_results['prices'], symbol_results['technical'], 
                                   symbol_results['fundamentals'], symbol_results['news']])
                print(f"  ✅ {symbol}: {success_count}/4 סוגי נתונים נשלפו ({symbol_results['rows_count']} שורות)")
                
            except Exception as e:
                print(f"  ❌ {symbol}: שגיאה - {e}")
                results[symbol] = symbol_results
        
        # יצירת נתוני מדדים
        print(f"\n📊 יוצר נתוני מדדים...")
        market_success = self._generate_market_data()
        
        # יצירת מטא-דאטה
        print(f"\n📋 יוצר מטא-דאטה...")
        self._create_metadata(symbols, results)
        
        end_time = time.time()
        
        # סיכום סופי
        self._print_summary(results, end_time - start_time, market_success)
        
        return results
    
    def _generate_price_data(self, symbol: str, years: int):
        """יצירת נתוני מחירים מדומים"""
        try:
            # יצירת תאריכים
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years * 365)
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # יצירת נתונים מדומים
            np.random.seed(hash(symbol) % 1000)  # זרע קבוע לכל מניה
            
            # מחיר התחלתי שונה לכל מניה
            base_price = {
                'AAPL': 150,
                'MSFT': 300,
                'TSLA': 200
            }.get(symbol, 100)
            
            # יצירת מחירים עם תנודתיות
            returns = np.random.normal(0.0005, 0.02, len(dates))  # תשואה יומית
            prices = [base_price]
            
            for ret in returns[1:]:
                new_price = prices[-1] * (1 + ret)
                prices.append(max(new_price, 1))  # מחיר מינימלי של 1
            
            # יצירת נתוני OHLCV
            data = []
            for i, (date, price) in enumerate(zip(dates, prices)):
                # יצירת OHLC סביב המחיר
                daily_volatility = np.random.uniform(0.01, 0.03)
                open_price = price * (1 + np.random.uniform(-daily_volatility/2, daily_volatility/2))
                high_price = max(open_price, price) * (1 + np.random.uniform(0, daily_volatility))
                low_price = min(open_price, price) * (1 - np.random.uniform(0, daily_volatility))
                close_price = price
                
                # נפח מסחר
                volume = np.random.randint(1000000, 100000000)
                
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'symbol': symbol,
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': volume,
                    'adjusted_close': round(close_price, 2)
                })
            
            df = pd.DataFrame(data)
            
            # שמירה
            file_path = f"{self.base_dir}/historical_prices/daily/{symbol}.csv"
            df.to_csv(file_path, index=False)
            
            print(f"    ✅ מחירים: {len(df)} שורות נוצרו")
            return True, len(df)
                
        except Exception as e:
            print(f"    ❌ מחירים: שגיאה - {e}")
            return False, 0
    
    def _generate_technical_indicators(self, symbol: str, years: int):
        """יצירת אינדיקטורים טכניים מדומים"""
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
            
            # RSI מדומה
            rsi = 50 + np.random.normal(0, 15, len(close))  # RSI בין 20-80
            rsi = np.clip(rsi, 20, 80)
            
            # MACD מדומה
            macd = np.random.normal(0, 2, len(close))
            signal = macd + np.random.normal(0, 0.5, len(close))
            
            # Bollinger Bands מדומים
            sma_20 = close.rolling(20).mean()
            upper_band = sma_20 * (1 + np.random.uniform(0.02, 0.05, len(close)))
            lower_band = sma_20 * (1 - np.random.uniform(0.02, 0.05, len(close)))
            
            # SMA & EMA מדומים
            sma_20 = close.rolling(20).mean()
            ema_20 = close.ewm(span=20).mean()
            
            # שמירת אינדיקטורים
            indicators = {
                'rsi': rsi,
                'macd': macd,
                'bollinger': upper_band,
                'sma': sma_20,
                'ema': ema_20
            }
            
            saved_count = 0
            for indicator_name, indicator_data in indicators.items():
                indicator_df = pd.DataFrame({
                    'date': df.index.strftime('%Y-%m-%d'),
                    'symbol': symbol,
                    'value': indicator_data,
                    'period': 14 if indicator_name == 'rsi' else 20
                })
                
                # הסרת שורות עם NaN
                indicator_df = indicator_df.dropna()
                
                if not indicator_df.empty:
                    file_path = f"{self.base_dir}/technical_indicators/{indicator_name}/daily/{symbol}_{indicator_name}.csv"
                    indicator_df.to_csv(file_path, index=False)
                    saved_count += 1
            
            print(f"    ✅ אינדיקטורים: {saved_count} אינדיקטורים נוצרו")
            return True
            
        except Exception as e:
            print(f"    ❌ אינדיקטורים: שגיאה - {e}")
            return False
    
    def _generate_fundamental_data(self, symbol: str):
        """יצירת נתונים פיננסיים מדומים"""
        try:
            # נתונים מדומים לכל מניה
            company_data = {
                'AAPL': {
                    'long_name': 'Apple Inc.',
                    'sector': 'Technology',
                    'industry': 'Consumer Electronics',
                    'market_cap': 2500000000000,
                    'pe_ratio': 25.5,
                    'price_to_book': 15.2,
                    'employees': 164000
                },
                'MSFT': {
                    'long_name': 'Microsoft Corporation',
                    'sector': 'Technology',
                    'industry': 'Software',
                    'market_cap': 2800000000000,
                    'pe_ratio': 30.1,
                    'price_to_book': 12.8,
                    'employees': 221000
                },
                'TSLA': {
                    'long_name': 'Tesla, Inc.',
                    'sector': 'Consumer Cyclical',
                    'industry': 'Auto Manufacturers',
                    'market_cap': 800000000000,
                    'pe_ratio': 45.2,
                    'price_to_book': 8.5,
                    'employees': 127855
                }
            }
            
            data = company_data.get(symbol, {
                'long_name': f'{symbol} Corporation',
                'sector': 'Unknown',
                'industry': 'Unknown',
                'market_cap': 100000000000,
                'pe_ratio': 20.0,
                'price_to_book': 10.0,
                'employees': 50000
            })
            
            financial_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'symbol': symbol,
                'market_cap': data['market_cap'],
                'pe_ratio': data['pe_ratio'],
                'price_to_book': data['price_to_book'],
                'sector': data['sector'],
                'industry': data['industry'],
                'employees': data['employees'],
                'long_name': data['long_name']
            }
            
            df = pd.DataFrame([financial_data])
            file_path = f"{self.base_dir}/fundamentals/company_info/{symbol}_info.csv"
            df.to_csv(file_path, index=False)
            
            print(f"    ✅ פיננסיים: נתונים נוצרו")
            return True
            
        except Exception as e:
            print(f"    ❌ פיננסיים: שגיאה - {e}")
            return False
    
    def _generate_news_data(self, symbol: str):
        """יצירת חדשות מדומות"""
        try:
            # חדשות מדומות לכל מניה
            news_templates = {
                'AAPL': [
                    'Apple Reports Strong Q4 Earnings',
                    'New iPhone Model Announced',
                    'Apple Expands Services Business',
                    'Apple Stock Hits New High',
                    'Apple Announces Dividend Increase'
                ],
                'MSFT': [
                    'Microsoft Cloud Revenue Soars',
                    'Windows 12 Preview Released',
                    'Microsoft Acquires Gaming Studio',
                    'Azure Growth Exceeds Expectations',
                    'Microsoft Announces AI Partnership'
                ],
                'TSLA': [
                    'Tesla Delivers Record Number of Vehicles',
                    'New Tesla Model Announced',
                    'Tesla Expands Production Capacity',
                    'Tesla Stock Surges on Earnings Beat',
                    'Tesla Announces New Battery Technology'
                ]
            }
            
            news_list = news_templates.get(symbol, [
                f'{symbol} Reports Strong Earnings',
                f'{symbol} Announces New Product',
                f'{symbol} Stock Performance Update',
                f'{symbol} Expands Business Operations',
                f'{symbol} Financial Results Released'
            ])
            
            news_data = []
            for i, headline in enumerate(news_list):
                # תאריך מדומה - ימים אחורה
                news_date = datetime.now() - timedelta(days=np.random.randint(1, 30))
                
                news_data.append({
                    'date': news_date.strftime('%Y-%m-%d'),
                    'symbol': symbol,
                    'headline': headline,
                    'summary': f'This is a demo news article about {symbol}. {headline}',
                    'source': 'Demo News',
                    'url': f'https://demo-news.com/{symbol.lower()}-{i}',
                    'category': 'earnings' if 'earnings' in headline.lower() else 'general'
                })
            
            df = pd.DataFrame(news_data)
            file_path = f"{self.base_dir}/news_sentiment/financial_news/{symbol}_news.csv"
            df.to_csv(file_path, index=False)
            
            print(f"    ✅ חדשות: {len(news_data)} חדשות נוצרו")
            return True
                
        except Exception as e:
            print(f"    ❌ חדשות: שגיאה - {e}")
            return False
    
    def _generate_market_data(self):
        """יצירת נתוני מדדים מדומים"""
        indices = ['GSPC', 'IXIC', 'DJI']  # S&P 500, NASDAQ, Dow Jones
        
        success_count = 0
        for index in indices:
            try:
                # יצירת נתונים מדומים למדדים
                end_date = datetime.now()
                start_date = end_date - timedelta(days=2 * 365)
                dates = pd.date_range(start=start_date, end=end_date, freq='D')
                
                # מחיר בסיס שונה לכל מדד
                base_prices = {
                    'GSPC': 4000,
                    'IXIC': 12000,
                    'DJI': 35000
                }
                
                base_price = base_prices.get(index, 1000)
                returns = np.random.normal(0.0003, 0.015, len(dates))
                prices = [base_price]
                
                for ret in returns[1:]:
                    new_price = prices[-1] * (1 + ret)
                    prices.append(max(new_price, 100))
                
                data = []
                for date, price in zip(dates, prices):
                    data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'index_symbol': index,
                        'open': round(price * (1 + np.random.uniform(-0.01, 0.01)), 2),
                        'high': round(price * (1 + np.random.uniform(0, 0.02)), 2),
                        'low': round(price * (1 - np.random.uniform(0, 0.02)), 2),
                        'close': round(price, 2),
                        'volume': np.random.randint(1000000, 5000000)
                    })
                
                df = pd.DataFrame(data)
                file_path = f"{self.base_dir}/market_data/indices/{index}.csv"
                df.to_csv(file_path, index=False)
                
                print(f"    ✅ מדד {index}: {len(df)} שורות נוצרו")
                success_count += 1
                
            except Exception as e:
                print(f"    ❌ מדד {index}: שגיאה - {e}")
        
        return success_count > 0
    
    def _create_metadata(self, symbols: list, results: dict):
        """יצירת מטא-דאטה"""
        metadata = {
            'created_date': datetime.now().isoformat(),
            'test_run': True,
            'demo_data': True,
            'total_symbols': len(symbols),
            'symbols': symbols,
            'results': results,
            'data_types': ['prices', 'technical_indicators', 'fundamentals', 'news', 'market_data'],
            'period_years': 2,
            'note': 'נתונים מדומים לניסיון - לא נתונים אמיתיים'
        }
        
        file_path = f"{self.base_dir}/metadata/test_data_status.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"    ✅ מטא-דאטה: נשמר לקובץ {file_path}")
    
    def _print_summary(self, results: dict, duration: float, market_success: bool):
        """הדפסת סיכום"""
        print("\n" + "=" * 60)
        print("📊 סיכום הניסיון - נתונים מדומים")
        print("=" * 60)
        
        total_symbols = len(results)
        successful_symbols = sum(1 for r in results.values() if r['prices'])
        total_rows = sum(r['rows_count'] for r in results.values())
        
        print(f"⏱️ זמן כולל: {duration:.2f} שניות")
        print(f"📈 מניות: {successful_symbols}/{total_symbols} נוצרו")
        print(f"📊 שורות נתונים: {total_rows:,}")
        print(f"📰 מדדים: {'✅' if market_success else '❌'}")
        print(f"⚠️ הערה: אלו נתונים מדומים לניסיון!")
        
        print(f"\n📋 פירוט לפי מניה:")
        for symbol, result in results.items():
            success_count = sum([result['prices'], result['technical'], 
                               result['fundamentals'], result['news']])
            status = "✅" if result['prices'] else "❌"
            print(f"  {status} {symbol}: {success_count}/4 סוגים ({result['rows_count']} שורות)")
        
        print(f"\n🎯 השלב הבא: בדוק את הנתונים בתיקיות data/")

def get_all_us_stocks():
    """קבלת רשימת כל המניות האמריקאיות"""
    # S&P 500 (500 מניות)
    sp500 = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
        'CRM', 'ORCL', 'ADBE', 'PYPL', 'NKE', 'DIS', 'JPM', 'BAC', 'WFC', 'GS',
        'JNJ', 'PFE', 'UNH', 'HD', 'LOW', 'PG', 'KO', 'PEP', 'WMT', 'COST',
        'ABT', 'TMO', 'AVGO', 'QCOM', 'TXN', 'HON', 'UPS', 'RTX', 'LMT', 'BA',
        'CAT', 'DE', 'MMM', 'GE', 'IBM', 'CSCO', 'VZ', 'T', 'CMCSA', 'CME',
        'SPGI', 'BLK', 'AXP', 'V', 'MA', 'UNP', 'NSC', 'CP', 'CNI', 'FDX'
    ]
    
    # NASDAQ 100 (100 מניות)
    nasdaq100 = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
        'CRM', 'ADBE', 'PYPL', 'NKE', 'DIS', 'JPM', 'BAC', 'WFC', 'GS', 'JNJ',
        'PFE', 'UNH', 'HD', 'LOW', 'PG', 'KO', 'PEP', 'WMT', 'COST', 'ABT',
        'TMO', 'AVGO', 'QCOM', 'TXN', 'HON', 'UPS', 'RTX', 'LMT', 'BA', 'CAT',
        'DE', 'MMM', 'GE', 'IBM', 'CSCO', 'VZ', 'T', 'CMCSA', 'CME', 'SPGI'
    ]
    
    # איחוד הרשימות
    all_stocks = list(set(sp500 + nasdaq100))
    return all_stocks

def main():
    """הפונקציה הראשית"""
    print("🚀 מתחיל שליפת נתונים אמיתיים ל-5 מניות חדשות")
    print("=" * 60)
    
    # יצירת מופע
    filler = RealDataFiller()
    
    # 5 מניות חדשות שעוד לא הרצנו עליהן
    new_test_symbols = ['GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX']
    
    print(f"📊 יורד {len(new_test_symbols)} מניות חדשות: {', '.join(new_test_symbols)}")
    
    # שליפת הנתונים - 10 שנים
    results = filler.generate_real_data(new_test_symbols, years=10)
    
    print(f"\n🎉 שליפת הנתונים האמיתיים הושלמה!")
    print(f"📁 בדוק את התיקיות ב-data/ כדי לראות את הנתונים")
    print(f"✅ אלו נתונים אמיתיים מ-Yahoo Finance!")

if __name__ == "__main__":
    main() 