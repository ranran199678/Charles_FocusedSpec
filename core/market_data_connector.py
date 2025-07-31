import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import logging
from typing import Dict, List, Optional

# ייבוא DataFetcher במקום yfinance
try:
    from utils.data_fetcher import DataFetcher
    DATA_FETCHER_AVAILABLE = True
except ImportError:
    DATA_FETCHER_AVAILABLE = False
    logging.warning("DataFetcher לא זמין, יוחזרו נתונים ריקים")

class MarketDataConnector:
    """
    מחבר נתוני שוק מתקדם
    מתחבר למקורות נתונים שונים לניתוח מקיף
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # יצירת DataFetcher
        self.data_fetcher = DataFetcher() if DATA_FETCHER_AVAILABLE else None
        
        # מקורות נתונים
        self.data_sources = {
            "data_fetcher": self._get_data_fetcher_data,
            "alpha_vantage": self._get_alpha_vantage_data,
            "market_data": self._get_market_data,
            "fmp": self._get_fmp_data,
            "twelve": self._get_twelve_data,
            "finnhub": self._get_finnhub_data
        }
        
        # ייבוא credentials
        try:
            from utils.credentials import APICredentials
            self.credentials = APICredentials()
        except ImportError:
            self.credentials = None
        
        # מדדים עיקריים
        self.major_indices = {
            "SPY": "S&P 500",
            "QQQ": "NASDAQ",
            "IWM": "Russell 2000",
            "DIA": "Dow Jones",
            "VIX": "Volatility Index"
        }
        
        # סקטורים
        self.sectors = {
            "XLK": "Technology",
            "XLF": "Financial",
            "XLE": "Energy",
            "XLV": "Healthcare",
            "XLI": "Industrial",
            "XLP": "Consumer Staples",
            "XLY": "Consumer Discretionary",
            "XLU": "Utilities",
            "XLB": "Materials"
        }

    def get_comprehensive_market_data(self, symbol: str, period: str = "100d") -> Dict:
        """
        קבלת נתוני שוק מקיפים
        """
        try:
            # נתוני המניה
            stock_data = self._get_stock_data(symbol, period)
            
            # נתוני השוק הכללי
            market_data = self._get_market_overview()
            
            # נתוני הסקטור
            sector_data = self._get_sector_data(symbol)
            
            # ניתוח יחסי
            relative_analysis = self._analyze_relative_performance(stock_data, market_data, sector_data)
            
            return {
                "stock_data": stock_data,
                "market_data": market_data,
                "sector_data": sector_data,
                "relative_analysis": relative_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתוני שוק מקיפים: {str(e)}")
            return self._get_dummy_market_data()

    def _get_stock_data(self, symbol: str, period: str) -> Dict:
        """קבלת נתוני מניה"""
        try:
            # קבלת נתונים מ-DataFetcher במקום yfinance
            if self.data_fetcher is None:
                return {"error": "DataFetcher לא זמין"}
            
            # המרת תקופה לפורמט של DataFetcher
            period_map = {
                "1d": "1d", "5d": "5d", "1mo": "30d", 
                "3mo": "90d", "6mo": "180d", "1y": "365d",
                "2y": "730d", "5y": "1825d", "10y": "3650d",
                "ytd": "ytd", "max": "max"
            }
            
            data_fetcher_period = period_map.get(period, "100d")
            hist = self.data_fetcher.get_price_history(symbol, data_fetcher_period)
            
            if hist is None or hist.empty:
                return {"error": "אין נתונים זמינים"}
            
            # מידע בסיסי על המניה (ללא yfinance)
            company_info = {
                "name": symbol,
                "sector": "Unknown",
                "industry": "Unknown",
                "market_cap": 0,
                "pe_ratio": 0,
                "beta": 1.0
            }
            
            return {
                "price_data": hist,
                "company_info": company_info,
                "technical_indicators": self._calculate_technical_indicators(hist)
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתוני מניה: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"}

    def _get_market_overview(self) -> Dict:
        """קבלת סקירת שוק כללית"""
        try:
            market_data = {}
            
            # נתוני מדדים עיקריים - שימוש ב-DataFetcher
            for symbol, name in self.major_indices.items():
                try:
                    if self.data_fetcher is None:
                        continue
                    
                    hist = self.data_fetcher.get_price_history(symbol, "20d")
                    
                    if hist is not None and not hist.empty:
                        current_price = hist['close'].iloc[-1]
                        prev_price = hist['close'].iloc[-5] if len(hist) > 5 else current_price
                        change_pct = (current_price / prev_price - 1) * 100
                        
                        market_data[symbol] = {
                            "name": name,
                            "current_price": current_price,
                            "change_5d": change_pct,
                            "volume": hist['volume'].iloc[-1] if 'volume' in hist.columns else 0
                        }
                except Exception as e:
                    self.logger.warning(f"שגיאה בקבלת נתוני {symbol}: {str(e)}")
            
            # ניתוח VIX (תנודתיות) - שימוש ב-DataFetcher
            try:
                if self.data_fetcher is not None:
                    vix_hist = self.data_fetcher.get_price_history("^VIX", "20d")
                    if vix_hist is not None and not vix_hist.empty:
                        current_vix = vix_hist['close'].iloc[-1]
                        avg_vix = vix_hist['close'].mean()
                    
                    market_data["VIX"] = {
                        "name": "Volatility Index",
                        "current_value": current_vix,
                        "average_value": avg_vix,
                        "volatility_level": "גבוה" if current_vix > 20 else "נורמלי" if current_vix > 15 else "נמוך"
                    }
            except Exception as e:
                self.logger.warning(f"שגיאה בקבלת נתוני VIX: {str(e)}")
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת סקירת שוק: {str(e)}")
            return {}

    def _get_sector_data(self, symbol: str) -> Dict:
        """קבלת נתוני סקטור"""
        try:
            # קבלת מידע בסיסי על הסקטור (ללא yfinance)
            sector = "Unknown"
            
            # מציאת ETF של הסקטור
            sector_etf = self._find_sector_etf(sector)
            
            if sector_etf and self.data_fetcher is not None:
                hist_etf = self.data_fetcher.get_price_history(sector_etf, "20d")
                
                if hist_etf is not None and not hist_etf.empty:
                    current_price = hist_etf['close'].iloc[-1]
                    prev_price = hist_etf['close'].iloc[-5] if len(hist_etf) > 5 else current_price
                    change_pct = (current_price / prev_price - 1) * 100
                    
                    return {
                        "sector": sector,
                        "sector_etf": sector_etf,
                        "current_price": current_price,
                        "change_5d": change_pct,
                        "performance": "טוב" if change_pct > 2 else "בינוני" if change_pct > -2 else "גרוע"
                    }
            
            return {"sector": sector, "error": "אין נתוני סקטור זמינים"}
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתוני סקטור: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"}

    def _find_sector_etf(self, sector: str) -> Optional[str]:
        """מציאת ETF של הסקטור"""
        sector_mapping = {
            "Technology": "XLK",
            "Financial Services": "XLF",
            "Energy": "XLE",
            "Healthcare": "XLV",
            "Industrials": "XLI",
            "Consumer Defensive": "XLP",
            "Consumer Cyclical": "XLY",
            "Utilities": "XLU",
            "Basic Materials": "XLB"
        }
        
        return sector_mapping.get(sector)

    def _calculate_technical_indicators(self, hist: pd.DataFrame) -> Dict:
        """חישוב אינדיקטורים טכניים"""
        try:
            # התאמה לעמודות של DataFetcher
            close_column = 'close' if 'close' in hist.columns else 'Close'
            volume_column = 'volume' if 'volume' in hist.columns else 'Volume'
            high_column = 'high' if 'high' in hist.columns else 'High'
            low_column = 'low' if 'low' in hist.columns else 'Low'
            
            close_prices = hist[close_column]
            volume = hist[volume_column] if volume_column in hist.columns else pd.Series([0] * len(hist))
            
            # RSI
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            ema_12 = close_prices.ewm(span=12).mean()
            ema_26 = close_prices.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            # Bollinger Bands
            sma_20 = close_prices.rolling(20).mean()
            std_20 = close_prices.rolling(20).std()
            upper_band = sma_20 + (std_20 * 2)
            lower_band = sma_20 - (std_20 * 2)
            
            # Stochastic
            low_14 = hist[low_column].rolling(14).min()
            high_14 = hist[high_column].rolling(14).max()
            k_percent = 100 * ((close_prices - low_14) / (high_14 - low_14))
            d_percent = k_percent.rolling(3).mean()
            
            return {
                "rsi": rsi.iloc[-1] if not rsi.empty else 50,
                "macd": macd.iloc[-1] if not macd.empty else 0,
                "macd_signal": signal.iloc[-1] if not signal.empty else 0,
                "bollinger_upper": upper_band.iloc[-1] if not upper_band.empty else close_prices.iloc[-1],
                "bollinger_lower": lower_band.iloc[-1] if not lower_band.empty else close_prices.iloc[-1],
                "stochastic_k": k_percent.iloc[-1] if not k_percent.empty else 50,
                "stochastic_d": d_percent.iloc[-1] if not d_percent.empty else 50
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בחישוב אינדיקטורים טכניים: {str(e)}")
            return {}

    def _analyze_relative_performance(self, stock_data: Dict, market_data: Dict, sector_data: Dict) -> Dict:
        """ניתוח ביצועים יחסיים"""
        try:
            if "error" in stock_data or stock_data.get("price_data") is None:
                return {"error": "אין נתוני מניה זמינים"}
            
            stock_prices = stock_data["price_data"]['Close']
            current_stock_price = stock_prices.iloc[-1]
            
            # ביצועים יחסיים לשוק
            market_performance = {}
            if "SPY" in market_data:
                spy_data = market_data["SPY"]
                spy_change = spy_data["change_5d"]
                
                # חישוב ביצועים יחסיים
                stock_change_5d = (current_stock_price / stock_prices.iloc[-5] - 1) * 100
                relative_to_market = stock_change_5d - spy_change
                
                market_performance = {
                    "market_change": spy_change,
                    "stock_change": stock_change_5d,
                    "relative_performance": relative_to_market,
                    "outperformance": relative_to_market > 0
                }
            
            # ביצועים יחסיים לסקטור
            sector_performance = {}
            if "change_5d" in sector_data:
                sector_change = sector_data["change_5d"]
                stock_change_5d = (current_stock_price / stock_prices.iloc[-5] - 1) * 100
                relative_to_sector = stock_change_5d - sector_change
                
                sector_performance = {
                    "sector_change": sector_change,
                    "stock_change": stock_change_5d,
                    "relative_performance": relative_to_sector,
                    "outperformance": relative_to_sector > 0
                }
            
            # ניתוח תנודתיות
            stock_volatility = stock_prices.pct_change().std() * np.sqrt(252)
            market_volatility = 0
            if "SPY" in market_data:
                # חישוב תנודתיות השוק (פשט)
                market_volatility = 15  # ממוצע היסטורי
            
            volatility_ratio = stock_volatility / market_volatility if market_volatility > 0 else 1
            
            return {
                "market_performance": market_performance,
                "sector_performance": sector_performance,
                "volatility_analysis": {
                    "stock_volatility": stock_volatility,
                    "market_volatility": market_volatility,
                    "volatility_ratio": volatility_ratio,
                    "risk_level": "גבוה" if volatility_ratio > 1.5 else "בינוני" if volatility_ratio > 1 else "נמוך"
                }
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בניתוח ביצועים יחסיים: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"}

    def _get_dummy_market_data(self) -> Dict:
        """נתוני שוק ריקים במקרה של שגיאה"""
        return {
            "stock_data": {"error": "אין נתונים זמינים"},
            "market_data": {},
            "sector_data": {"error": "אין נתונים זמינים"},
            "relative_analysis": {"error": "אין נתונים זמינים"},
            "timestamp": datetime.now().isoformat()
        }

    def get_market_sentiment(self) -> Dict:
        """קבלת סנטימנט השוק"""
        try:
            # ניתוח VIX
            vix_sentiment = "ניטרלי"
            if "VIX" in self._get_market_overview():
                vix_value = self._get_market_overview()["VIX"]["current_value"]
                if vix_value > 25:
                    vix_sentiment = "פחד"
                elif vix_value < 15:
                    vix_sentiment = "תאוות בצע"
                else:
                    vix_sentiment = "ניטרלי"
            
            # ניתוח מגמות מדדים
            market_trend = "ניטרלי"
            market_data = self._get_market_overview()
            bullish_count = 0
            bearish_count = 0
            
            for symbol, data in market_data.items():
                if symbol != "VIX" and "change_5d" in data:
                    if data["change_5d"] > 1:
                        bullish_count += 1
                    elif data["change_5d"] < -1:
                        bearish_count += 1
            
            if bullish_count > bearish_count + 2:
                market_trend = "בולשי"
            elif bearish_count > bullish_count + 2:
                market_trend = "ברישי"
            else:
                market_trend = "מעורב"
            
            return {
                "vix_sentiment": vix_sentiment,
                "market_trend": market_trend,
                "bullish_count": bullish_count,
                "bearish_count": bearish_count
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת סנטימנט השוק: {str(e)}")
            return {
                "vix_sentiment": "לא ידוע",
                "market_trend": "לא ידוע",
                "bullish_count": 0,
                "bearish_count": 0
            } 

    def _get_data_fetcher_data(self, symbol: str) -> Dict:
        """קבלת נתונים מ-DataFetcher"""
        try:
            if self.data_fetcher is None:
                return {"error": "DataFetcher לא זמין"}
            
            hist = self.data_fetcher.get_price_history(symbol, "100d")
            
            if hist is None or hist.empty:
                return {"error": "אין נתונים זמינים"}
            
            return {
                "price_data": hist,
                "source": "data_fetcher",
                "company_info": {
                    "name": symbol,
                    "sector": "Unknown",
                    "industry": "Unknown",
                    "market_cap": 0,
                    "pe_ratio": 0,
                    "beta": 1.0
                }
            }
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתונים מ-DataFetcher: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"}

    def _get_alpha_vantage_data(self, symbol: str) -> Dict:
        """קבלת נתונים מ-Alpha Vantage"""
        try:
            if not self.credentials:
                return {"error": "אין credentials זמינים"}
            
            api_key = self.credentials.get_alpha_vantage_key()
            if not api_key:
                return {"error": "אין Alpha Vantage API key"}
            
            # קבלת נתוני מחיר
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": api_key,
                "outputsize": "compact"
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if "Error Message" in data:
                return {"error": data["Error Message"]}
            
            if "Time Series (Daily)" not in data:
                return {"error": "אין נתונים זמינים"}
            
            # המרה ל-DataFrame
            time_series = data["Time Series (Daily)"]
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)
            
            return {
                "price_data": df,
                "source": "alpha_vantage",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתונים מ-Alpha Vantage: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"}

    def _get_market_data(self, symbol: str) -> Dict:
        """קבלת נתוני שוק כללי"""
        try:
            # קבלת נתוני מדדים עיקריים - שימוש ב-DataFetcher
            market_data = {}
            
            for index_symbol in self.major_indices.keys():
                try:
                    if self.data_fetcher is None:
                        continue
                    
                    hist = self.data_fetcher.get_price_history(index_symbol, "30d")
                    
                    if hist is not None and not hist.empty:
                        current_price = hist['close'].iloc[-1]
                        prev_price = hist['close'].iloc[-5] if len(hist) >= 5 else current_price
                        change_5d = ((current_price / prev_price) - 1) * 100
                        
                        market_data[index_symbol] = {
                            "current_value": current_price,
                            "change_5d": change_5d,
                            "name": self.major_indices[index_symbol]
                        }
                except Exception as e:
                    self.logger.warning(f"שגיאה בקבלת נתונים עבור {index_symbol}: {str(e)}")
                    continue
            
            return {
                "market_data": market_data,
                "source": "data_fetcher",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתוני שוק: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"} 

    def _get_fmp_data(self, symbol: str) -> Dict:
        """קבלת נתונים מ-FMP (Financial Modeling Prep)"""
        try:
            from utils.fmp_utils import fmp_client
            
            # קבלת נתוני מחיר
            price_df = fmp_client.fmp_get_price_df(symbol, verify_ssl=False)
            
            # קבלת חדשות
            news_data = fmp_client.fmp_get_stock_news(tickers=symbol, limit=10, verify_ssl=False)
            
            # קבלת נתונים פונדמנטליים
            fundamental_data = fmp_client.fmp_get_company_profile(symbol, verify_ssl=False)
            
            return {
                "price_data": price_df,
                "news_data": news_data,
                "fundamental_data": fundamental_data,
                "source": "fmp",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתונים מ-FMP: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"}

    def _get_twelve_data(self, symbol: str) -> Dict:
        """קבלת נתונים מ-TwelveData"""
        try:
            from utils.twelve_utils import td_get_price_df, td_get
            
            # קבלת נתוני מחיר
            price_df = td_get_price_df(symbol)
            
            # קבלת נתונים טכניים
            technical_data = td_get("technical_indicators", {
                "symbol": symbol,
                "indicator": "sma",
                "interval": "1day",
                "time_period": 20
            })
            
            # קבלת נתוני נפח
            volume_data = td_get("time_series", {
                "symbol": symbol,
                "interval": "1day",
                "outputsize": 30
            })
            
            return {
                "price_data": price_df,
                "technical_data": technical_data,
                "volume_data": volume_data,
                "source": "twelve_data",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתונים מ-TwelveData: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"}

    def _get_finnhub_data(self, symbol: str) -> Dict:
        """קבלת נתונים מ-Finnhub"""
        try:
            if not self.credentials:
                return {"error": "אין credentials זמינים"}
            
            api_key = self.credentials.get_finnhub_key()
            if not api_key:
                return {"error": "אין Finnhub API key"}
            
            # קבלת חדשות
            url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2024-01-01&to=2024-12-31&token={api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return {"error": f"שגיאת HTTP: {response.status_code}"}
            
            news_data = response.json()
            
            # קבלת נתוני חברה
            company_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}"
            company_response = requests.get(company_url, timeout=10)
            company_data = company_response.json() if company_response.status_code == 200 else {}
            
            return {
                "news_data": news_data,
                "company_data": company_data,
                "source": "finnhub",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתונים מ-Finnhub: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"}

    def get_enhanced_market_data(self, symbol: str) -> Dict:
        """קבלת נתוני שוק משופרים מכל המקורות"""
        try:
            enhanced_data = {}
            
            # נתונים מ-Yahoo Finance
            yf_data = self._get_yfinance_data(symbol)
            if "error" not in yf_data:
                enhanced_data["yfinance"] = yf_data
            
            # נתונים מ-FMP
            fmp_data = self._get_fmp_data(symbol)
            if "error" not in fmp_data:
                enhanced_data["fmp"] = fmp_data
            
            # נתונים מ-TwelveData
            twelve_data = self._get_twelve_data(symbol)
            if "error" not in twelve_data:
                enhanced_data["twelve_data"] = twelve_data
            
            # נתונים מ-Finnhub
            finnhub_data = self._get_finnhub_data(symbol)
            if "error" not in finnhub_data:
                enhanced_data["finnhub"] = finnhub_data
            
            # נתוני שוק כללי
            market_data = self._get_market_data(symbol)
            enhanced_data["market_data"] = market_data
            
            return {
                "enhanced_data": enhanced_data,
                "sources_count": len(enhanced_data),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"שגיאה בקבלת נתוני שוק משופרים: {str(e)}")
            return {"error": f"שגיאה: {str(e)}"} 