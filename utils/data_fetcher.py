import requests
import pandas as pd
from datetime import datetime
from utils.credentials import APICredentials
from utils.fmp_utils import fmp_client
import time
import urllib3
import logging

# ביטול אזהרות SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ניסיון לטעון huggingface עם pipeline
try:
    from transformers import pipeline
    sentiment_classifier = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        use_auth_token=None,
        trust_remote_code=True,
        local_files_only=False,
        ignore_mismatched_sizes=True
    )
except Exception as e:
    sentiment_classifier = None
    logging.warning(f"⚠️ לא ניתן לטעון מודל sentiment - משתמש בפתרון חלופי: {e}")

try:
    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",
        use_auth_token=None,
        trust_remote_code=True,
        local_files_only=False,
        ignore_mismatched_sizes=True
    )
except Exception as e:
    summarizer = None
    logging.warning(f"⚠️ לא ניתן לטעון מודל summarizer - משתמש בפתרון חלופי: {e}")

# פונקציה חלופית לניתוח סנטימנט
def simple_sentiment_analysis(text):
    """ניתוח סנטימנט פשוט ללא מודל ML"""
    if not text:
        return 0.5
    
    positive_words = ['up', 'rise', 'gain', 'positive', 'growth', 'profit', 'earnings', 'beat', 'strong', 'buy']
    negative_words = ['down', 'fall', 'loss', 'negative', 'decline', 'miss', 'weak', 'sell', 'drop', 'crash']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count == 0 and negative_count == 0:
        return 0.5
    
    return positive_count / (positive_count + negative_count)


class DataFetcher:
    def __init__(self):
        self.finnhub_key = APICredentials.get_finnhub_key()
        self.fmp_key = APICredentials.get_fmp_key()
        self.twelve_key = APICredentials.get_twelve_key()

        self.session = requests.Session()
        self.price_cache = {}
        self.fundamentals_cache = {}
        self.news_cache = {}

    def _safe_request(self, url, retries=3, delay=2):
        for attempt in range(retries):
            try:
                response = self.session.get(url, verify=False)
                if response.status_code == 429:
                    time.sleep(delay)
                    continue
                response.raise_for_status()
                return response.json()
            except Exception:
                time.sleep(delay)
        return {}

    def fetch_prices_batch(self, symbols: list, interval: str = "1day") -> dict:
        result = {}
        for symbol in symbols:
            if symbol in self.price_cache and interval == "1day":
                result[symbol] = self.price_cache[symbol]
                continue

            # 1. Yahoo Finance
            df = self._fallback_yahoo_prices(symbol, interval)

            # 2. Finnhub
            if df is None:
                df = self._fallback_finnhub_prices(symbol, interval)

            # 3. FMP
            if df is None:
                df = self._fetch_fmp_prices(symbol, interval=interval)

            # 4. TwelveData
            if df is None:
                df = self._fallback_twelve_prices(symbol, interval)

            result[symbol] = df
            if df is not None and interval == "1day":
                self.price_cache[symbol] = df

        return result

    def _fetch_fmp_prices(self, symbol, interval="1day"):
        """
        שליפת נתוני מחירים מ-FMP באמצעות המערכת החכמה, תומך באינטרוולים: 1d, 1wk, 1mo, 1h, 5m, 15m
        """
        try:
            from utils.smart_data_manager import smart_data_manager
            interval_map = {
                "1day": ("1d", 90),
                "1d": ("1d", 90),
                "1wk": ("1wk", 104),
                "1mo": ("1mo", 60),
                "1h": ("1h", 7),
                "5min": ("5m", 5),
                "5m": ("5m", 5),
                "15min": ("15m", 5),
                "15m": ("15m", 5)
            }
            fmp_interval, days = interval_map.get(interval, ("1d", 90))
            df = smart_data_manager.get_stock_data(symbol, days=days, include_live=True)
            if df is not None and not df.empty:
                # הוספת עמודת תאריך אם חסרה
                if 'timestamp' not in df.columns and 'date' not in df.columns:
                    # יצירת עמודת תאריך מהאינדקס או מהיום הנוכחי
                    if df.index.name == 'timestamp':
                        df = df.reset_index()
                    elif df.index.name == 'date':
                        df = df.reset_index().rename(columns={'date': 'timestamp'})
                    else:
                        # יצירת עמודת תאריך מהיום הנוכחי אחורה
                        from datetime import datetime, timedelta
                        dates = [datetime.now() - timedelta(days=i) for i in range(len(df))]
                        df['timestamp'] = dates
                
                # וידוא שיש עמודת timestamp
                if 'timestamp' in df.columns:
                    df = df.set_index('timestamp')
                elif 'date' in df.columns:
                    df = df.set_index('date')
                
                required_columns = ['open', 'close', 'volume', 'high', 'low']
                available_columns = [col for col in required_columns if col in df.columns]
                if available_columns:
                    return df[available_columns].astype(float)
            return None
        except Exception as e:
            logging.warning(f"שגיאה בשליפת נתונים מ-FMP עבור {symbol} (interval={interval}): {e}")
            return None


    def _fallback_twelve_prices(self, symbol, interval="1day"):
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=100&apikey={self.twelve_key}"
        data = self._safe_request(url)
        values = data.get("values", [])
        df = pd.DataFrame(values)
        if not df.empty and {'close', 'volume', 'high', 'low', 'datetime', 'open'}.issubset(df.columns):
            df['timestamp'] = pd.to_datetime(df['datetime'])
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'close', 'volume', 'high', 'low']].astype(float)
            return df
        # אם TwelveData לא מחזיר נתונים, ננסה Yahoo Finance
        return self._fallback_yahoo_prices(symbol, interval)

    def _fallback_yahoo_prices(self, symbol, interval="1day"):
        """
        שליפת נתוני מחירים מ-Yahoo Finance (ללא API key), תומך באינטרוולים: 1d, 1wk, 1mo, 1h, 5m, 15m
        """
        try:
            from datetime import datetime, timedelta
            end_date = datetime.now()
            # ברירת מחדל: 100 ימים אחורה
            days = 100
            interval_map = {
                "1day": "1d",
                "1d": "1d",
                "1wk": "1wk",
                "1mo": "1mo",
                "1h": "1h",
                "5min": "5m",
                "5m": "5m",
                "15min": "15m",
                "15m": "15m"
            }
            yf_interval = interval_map.get(interval, "1d")
            # קביעת טווח זמן מתאים לפי אינטרוול
            if yf_interval in ["1d", "1wk", "1mo"]:
                start_date = end_date - timedelta(days=days)
            elif yf_interval in ["1h", "5m", "15m"]:
                start_date = end_date - timedelta(days=7)  # נתוני תוך-יומי מוגבלים ל-7 ימים אחורה
            else:
                start_date = end_date - timedelta(days=days)
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval={yf_interval}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            data = response.json()
            result = data.get('chart', {}).get('result', [{}])[0]
            if not result or 'indicators' not in result or 'quote' not in result['indicators']:
                return None
            closes = result['indicators']['quote'][0].get('close', [])
            opens = result['indicators']['quote'][0].get('open', [])
            highs = result['indicators']['quote'][0].get('high', [])
            lows = result['indicators']['quote'][0].get('low', [])
            volumes = result['indicators']['quote'][0].get('volume', [])
            dates = result.get('timestamp', [])
            if not closes or not dates:
                return None
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(dates, unit='s'),
                'open': opens,
                'close': closes,
                'high': highs,
                'low': lows,
                'volume': volumes
            })
            df.set_index('timestamp', inplace=True)
            return df[['open', 'close', 'volume', 'high', 'low']]
        except Exception as e:
            logging.warning(f"שגיאה בשליפת נתונים מ-Yahoo Finance עבור {symbol}: {e}")
        return None

    def _fallback_finnhub_prices(self, symbol, interval="1day"):
        resolution_map = {
            "1min": "1",
            "5min": "5",
            "15min": "15",
            "30min": "30",
            "1day": "D"
        }
        resolution = resolution_map.get(interval, "D")
        end_time = int(time.time())
        start_time = end_time - 60 * 60 * 24 * 100

        url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution={resolution}&from={start_time}&to={end_time}&token={self.finnhub_key}"
        data = self._safe_request(url)
        if data.get("s") != "ok":
            return None

        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data['t'], unit='s'),
            'open': data['o'],
            'close': data['c'],
            'high': data['h'],
            'low': data['l'],
            'volume': data['v']
        })
        df.set_index('timestamp', inplace=True)
        return df[['open', 'close', 'volume', 'high', 'low']]

    def summarize_text(self, text, max_length=60, min_length=20):
        if summarizer is None:
            # פתרון חלופי - חיתוך טקסט פשוט
            if len(text) <= max_length:
                return text
            # חיתוך חכם - מנסה לחתוך במשפט שלם
            words = text.split()
            summary = ""
            for word in words:
                if len(summary + " " + word) <= max_length:
                    summary += " " + word if summary else word
                else:
                    break
            return summary.strip() if summary else text[:max_length]
        try:
            summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            return f"שגיאה בסיכום: {e}"

    def fetch_fundamentals_batch(self, symbols: list) -> dict:
        result = {}
        for symbol in symbols:
            if symbol in self.fundamentals_cache:
                result[symbol] = self.fundamentals_cache[symbol]
                continue
            
            # שימוש במודול fmp_utils המעודכן
            try:
                company_data = fmp_client.fmp_get_company_profile(symbol, verify_ssl=False)
                output = company_data if company_data else {}
            except Exception as e:
                logging.warning(f"שגיאה בשליפת נתוני חברה עבור {symbol}: {e}")
                output = {}
            
            self.fundamentals_cache[symbol] = output
            result[symbol] = output
        return result

    def fetch_news_batch(self, symbols: list, limit: int = 3) -> dict:
        result = {}
        marketaux_key = "Dx8X1gzfxklRC5WETItJAncifB4bXp98EnSqzT6P"
        newsdata_key = "pub_a54510d1206a48d39dd48b3b3b624a2f"

        for symbol in symbols:
            if symbol in self.news_cache:
                result[symbol] = self.news_cache[symbol]
                continue

            url1 = f"https://api.marketaux.com/v1/news/all?symbols={symbol}&language=en&limit={limit}&api_token={marketaux_key}"
            data = self._safe_request(url1)
            if not data.get("data"):
                url2 = f"https://newsdata.io/api/1/news?apikey={newsdata_key}&q={symbol}&language=en&category=business"
                data = self._safe_request(url2)
                articles = data.get("results", [])
                headlines = []
                for item in articles[:limit]:
                    title = item.get("title", "")
                    summary = self.summarize_text(item.get("description", ""))
                    sentiment = sentiment_classifier(title)[0] if sentiment_classifier and title else {}
                    headlines.append({
                        "title": title,
                        "summary": summary,
                        "sentiment": sentiment
                    })
            else:
                articles = data.get("data", [])
                headlines = []
                for item in articles[:limit]:
                    title = item.get("title", "")
                    summary = self.summarize_text(item.get("description", ""))
                    sentiment = sentiment_classifier(title)[0] if sentiment_classifier and title else {}
                    headlines.append({
                        "title": title,
                        "summary": summary,
                        "sentiment": sentiment
                    })

            if not headlines:
                headlines.append({
                    "title": "No news available",
                    "summary": "",
                    "sentiment": {"label": "neutral", "score": 0.0}
                })

            self.news_cache[symbol] = headlines
            result[symbol] = headlines
        return result

    def fetch_alpha_vantage_news(self, symbol: str, limit: int = 5) -> list:
        """
        שליפת חדשות מ-Alpha Vantage News API
        """
        try:
            alpha_key = APICredentials.get_alpha_vantage_key()
            if not alpha_key:
                return []
                
            url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={alpha_key}&limit={limit}"
            data = self._safe_request(url)
            
            articles = []
            if data.get("feed"):
                for item in data["feed"][:limit]:
                    title = item.get("title", "")
                    summary = item.get("summary", "")
                    sentiment = item.get("overall_sentiment_label", "neutral")
                    source = item.get("source", "Alpha Vantage")
                    
                    articles.append({
                        "title": title,
                        "summary": summary,
                        "sentiment": sentiment,
                        "source": source,
                        "published_at": item.get("time_published", "")
                    })
                    
            return articles
        except Exception as e:
            logging.warning(f"שגיאה בשליפת חדשות מ-Alpha Vantage: {e}")
            return []

    def fetch_finnhub_news(self, symbol: str, limit: int = 5) -> list:
        """
        שליפת חדשות מ-Finnhub News API
        """
        try:
            finnhub_key = self.finnhub_key
            if not finnhub_key:
                return []
                
            url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from=2024-01-01&to=2024-12-31&token={finnhub_key}"
            data = self._safe_request(url)
            
            articles = []
            if isinstance(data, list):
                for item in data[:limit]:
                    title = item.get("headline", "")
                    summary = item.get("summary", "")
                    source = item.get("source", "Finnhub")
                    
                    articles.append({
                        "title": title,
                        "summary": summary,
                        "sentiment": "neutral",  # Finnhub לא מספק סנטימנט
                        "source": source,
                        "published_at": item.get("datetime", "")
                    })
                    
            return articles
        except Exception as e:
            logging.warning(f"שגיאה בשליפת חדשות מ-Finnhub: {e}")
            return []

    def fetch_yahoo_finance_rss(self, symbol: str, limit: int = 5) -> list:
        """
        שליפת חדשות מ-Yahoo Finance RSS
        """
        try:
            import feedparser
            
            # Yahoo Finance RSS URL
            rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
            
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:limit]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                published = entry.get("published", "")
                
                articles.append({
                    "title": title,
                    "summary": summary,
                    "sentiment": "neutral",  # RSS לא מספק סנטימנט
                    "source": "Yahoo Finance",
                    "published_at": published
                })
                
            return articles
        except Exception as e:
            logging.warning(f"שגיאה בשליפת חדשות מ-Yahoo Finance RSS: {e}")
            return []

    def _calculate_news_relevance(self, title: str, summary: str, symbol: str) -> float:
        """
        חישוב ציון רלוונטיות לחדשות
        """
        text = f"{title} {summary}".lower()
        symbol_lower = symbol.lower()
        
        # בדיקה ישירה של שם המניה
        if symbol_lower in text:
            return 0.8
        
        # בדיקת שמות חברות ידועות
        company_names = {
            'INTC': ['intel', 'intel corporation'],
            'AAPL': ['apple', 'apple inc'],
            'TSLA': ['tesla', 'tesla inc'],
            'NVDA': ['nvidia', 'nvidia corporation'],
            'MSFT': ['microsoft', 'microsoft corporation'],
            'GOOGL': ['google', 'alphabet', 'alphabet inc'],
            'AMZN': ['amazon', 'amazon.com'],
            'META': ['meta', 'facebook', 'meta platforms']
        }
        
        if symbol in company_names:
            for name in company_names[symbol]:
                if name in text:
                    return 0.7
        
        # בדיקה של מילות מפתח פיננסיות + שם המניה
        financial_keywords = ['earnings', 'revenue', 'profit', 'stock', 'shares', 'trading', 'quarterly', 'financial']
        has_financial = any(keyword in text for keyword in financial_keywords)
        
        if has_financial and symbol_lower in text:
            return 0.6
        
        return 0.0

    def _filter_news_by_date(self, articles: list, days_back: int = 7) -> list:
        """
        סינון חדשות לפי תאריך - רק חדשות אחרונות
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        filtered_articles = []
        
        for article in articles:
            try:
                # ניסיון לפרסר תאריכים שונים
                published_str = article.get('published_at', '')
                if not published_str:
                    continue
                    
                # פורמטים שונים של תאריכים
                date_formats = [
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                    '%m/%d/%Y'
                ]
                
                published_date = None
                for fmt in date_formats:
                    try:
                        published_date = datetime.strptime(published_str[:19], fmt)
                        break
                    except ValueError:
                        continue
                
                if published_date and published_date >= cutoff_date:
                    filtered_articles.append(article)
                    
            except Exception:
                # אם לא מצליח לפרסר תאריך, נכלול את הכתבה
                filtered_articles.append(article)
        
        return filtered_articles

    def _filter_news_by_source(self, articles: list, trusted_sources: list = None) -> list:
        """
        סינון חדשות לפי מקורות אמינים
        """
        if trusted_sources is None:
            trusted_sources = [
                'reuters', 'bloomberg', 'cnbc', 'marketwatch', 'yahoo finance',
                'seeking alpha', 'barrons', 'wall street journal', 'financial times',
                'forbes', 'fortune', 'business insider', 'techcrunch'
            ]
        
        filtered_articles = []
        
        for article in articles:
            source = article.get('source', '').lower()
            
            # בדיקה אם המקור אמין
            is_trusted = any(trusted in source for trusted in trusted_sources)
            
            # אם המקור אמין או שיש מילות מפתח חשובות
            if is_trusted:
                article['source_credibility'] = 1.0
                filtered_articles.append(article)
            else:
                # בדיקה אם יש מילות מפתח חשובות
                title = article.get('title', '').lower()
                summary = article.get('summary', '').lower()
                text = f"{title} {summary}"
                
                important_keywords = ['earnings', 'revenue', 'profit', 'quarterly', 'financial', 'results']
                has_important = any(keyword in text for keyword in important_keywords)
                
                if has_important:
                    article['source_credibility'] = 0.7
                    filtered_articles.append(article)
                else:
                    article['source_credibility'] = 0.3
                    filtered_articles.append(article)
        
        return filtered_articles

    def _calculate_news_quality_score(self, article: dict, symbol: str) -> float:
        """
        חישוב ציון איכות כולל לחדשות
        """
        relevance_score = article.get('relevance_score', 0)
        source_credibility = article.get('source_credibility', 0.5)
        
        # משקל לפי סוג חדשות
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        text = f"{title} {summary}"
        
        # חדשות חשובות יותר
        important_keywords = ['earnings', 'revenue', 'profit', 'quarterly', 'financial', 'results', 'guidance']
        important_weight = 1.2 if any(keyword in text for keyword in important_keywords) else 1.0
        
        # חדשות שליליות חשובות יותר
        negative_keywords = ['layoffs', 'restructuring', 'decline', 'miss', 'disappointing', 'dismal']
        negative_weight = 1.3 if any(keyword in text for keyword in negative_keywords) else 1.0
        
        # חישוב ציון סופי
        quality_score = relevance_score * source_credibility * important_weight * negative_weight
        
        return min(quality_score, 1.0)  # מקסימום 1.0

    def fetch_enhanced_news_batch(self, symbols: list, limit: int = 3) -> dict:
        """
        שליפת חדשות מכל המקורות הזמינים עם סינון מתקדם
        """
        result = {}
        
        for symbol in symbols:
            if symbol in self.news_cache:
                result[symbol] = self.news_cache[symbol]
                continue
                
            all_articles = []
            
            # 1. MarketAux (מקור ראשי)
            marketaux_key = APICredentials.get_marketaux_key()
            url1 = f"https://api.marketaux.com/v1/news/all?symbols={symbol}&language=en&limit={limit}&api_token={marketaux_key}"
            data1 = self._safe_request(url1)
            if data1.get("data"):
                for item in data1["data"][:limit]:
                    all_articles.append({
                        "title": item.get("title", ""),
                        "summary": item.get("description", ""),
                        "sentiment": item.get("sentiment", "neutral"),
                        "source": item.get("source", "MarketAux"),
                        "published_at": item.get("published_at", ""),
                        "relevance_score": self._calculate_news_relevance(item.get("title", ""), item.get("description", ""), symbol)
                    })
            
            # 2. Alpha Vantage (אם זמין)
            alpha_articles = self.fetch_alpha_vantage_news(symbol, limit)
            for item in alpha_articles:
                item["relevance_score"] = self._calculate_news_relevance(item["title"], item["summary"], symbol)
                all_articles.append(item)
            
            # 3. Finnhub (אם זמין)
            finnhub_articles = self.fetch_finnhub_news(symbol, limit)
            for item in finnhub_articles:
                item["relevance_score"] = self._calculate_news_relevance(item["title"], item["summary"], symbol)
                all_articles.append(item)
            
            # 4. Yahoo Finance RSS (אם זמין)
            yahoo_articles = self.fetch_yahoo_finance_rss(symbol, limit)
            for item in yahoo_articles:
                item["relevance_score"] = self._calculate_news_relevance(item["title"], item["summary"], symbol)
                all_articles.append(item)
            
            # 5. NewsData (גיבוי)
            if len(all_articles) < limit:
                newsdata_key = APICredentials.get_newsdata_key()
                url2 = f"https://newsdata.io/api/1/news?apikey={newsdata_key}&q={symbol}&language=en&category=business"
                data2 = self._safe_request(url2)
                if data2.get("results"):
                    for item in data2["results"][:limit]:
                        all_articles.append({
                            "title": item.get("title", ""),
                            "summary": item.get("description", ""),
                            "sentiment": "neutral",
                            "source": item.get("source_id", "NewsData"),
                            "published_at": item.get("pubDate", ""),
                            "relevance_score": self._calculate_news_relevance(item.get("title", ""), item.get("description", ""), symbol)
                        })
            
            # סינון מתקדם
            # 1. סינון לפי תאריך (רק חדשות אחרונות)
            all_articles = self._filter_news_by_date(all_articles, days_back=7)
            
            # 2. סינון לפי מקורות אמינים
            all_articles = self._filter_news_by_source(all_articles)
            
            # 3. חישוב ציון איכות
            for article in all_articles:
                article['quality_score'] = self._calculate_news_quality_score(article, symbol)
            
            # 4. סינון ומיון לפי איכות
            filtered_articles = [article for article in all_articles if article["relevance_score"] > 0.3 and article['quality_score'] > 0.4]
            filtered_articles.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            
            # המרה לפורמט סטנדרטי
            headlines = []
            for article in filtered_articles[:limit]:
                sentiment = sentiment_classifier(article["title"])[0] if sentiment_classifier and article["title"] else {"label": article["sentiment"], "score": 0.5}
                headlines.append({
                    "title": article["title"],
                    "summary": self.summarize_text(article["summary"]),
                    "sentiment": sentiment,
                    "source": article["source"],
                    "relevance_score": article.get("relevance_score", 0),
                    "quality_score": article.get("quality_score", 0)
                })
            
            if not headlines:
                headlines.append({
                    "title": "No relevant news available",
                    "summary": "",
                    "sentiment": {"label": "neutral", "score": 0.0}
                })
            
            self.news_cache[symbol] = headlines
            result[symbol] = headlines
            
        return result

    def fetch(self, symbols: list, datatype: str, interval: str = "1day") -> dict:
        if datatype == 'price':
            return self.fetch_prices_batch(symbols, interval=interval)
        elif datatype == 'fundamentals':
            return self.fetch_fundamentals_batch(symbols)
        elif datatype == 'news':
            return self.fetch_news_batch(symbols)
        else:
            raise ValueError(f"סוג מידע לא נתמך: {datatype}")

    def fetch_live_prices(self, symbol: str, interval: str = "1min") -> pd.DataFrame:
        """
        מחזיר נתוני מחיר בזמן אמת לפי סימבול ואינטרוול (1min, 5min, וכו').
        ברירת המחדל: 1min, משתמש ב-Finnhub או TwelveData לפי זמינות.
        """
        try:
            df = self._fallback_twelve_prices(symbol, interval)
            if df is not None and not df.empty:
                return df
        except Exception as e:
            print(f"⚠️ שגיאה ב־TwelveData ל־{symbol}: {e}")

        try:
            df = self._fallback_finnhub_prices(symbol, interval)
            if df is not None and not df.empty:
                return df
        except Exception as e:
            print(f"⚠️ שגיאה ב־Finnhub ל־{symbol}: {e}")

        return pd.DataFrame()  # במידה ולא נמצאו נתונים

    def get_price_history(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        מחזיר היסטוריית מחירים לפי סימבול ותקופה.
        
        Args:
            symbol: סימבול המניה
            period: תקופה (1y, 6m, 3m, 1m, או מספר ימים כמו "100d")
            
        Returns:
            DataFrame עם נתוני מחירים
        """
        # מיפוי תקופות לימים
        period_days = {
            "1y": 365,
            "6m": 180,
            "3m": 90,
            "1m": 30
        }
        
        # בדיקה אם period הוא מספר ימים (למשל "100d")
        if isinstance(period, str) and period.endswith('d'):
            try:
                days = int(period[:-1])
            except ValueError:
                days = 365
        else:
            days = period_days.get(period, 365)
        
        # נסה לקבל נתונים מ-FMP עם הגבלת ימים
        df = self._fetch_fmp_prices_with_limit(symbol, days)
        if df is not None and not df.empty:
            return df
        
        # נסה TwelveData
        df = self._fallback_twelve_prices(symbol, "1day")
        if df is not None and not df.empty:
            if len(df) > days:
                df = df.tail(days)
            return df
        
        # נסה Finnhub
        df = self._fallback_finnhub_prices(symbol, "1day")
        if df is not None and not df.empty:
            if len(df) > days:
                df = df.tail(days)
            return df
        
        # אם לא הצלחנו לקבל נתונים, החזר DataFrame ריק
        return pd.DataFrame(columns=['open', 'close', 'volume', 'high', 'low'])

    def _fetch_fmp_prices_with_limit(self, symbol: str, days: int = 365):
        """
        מביא נתוני מחירים מ-FMP עם הגבלת ימים באמצעות המערכת החכמה
        """
        try:
            # שימוש במערכת החכמה החדשה
            from utils.smart_data_manager import smart_data_manager
            
            df = smart_data_manager.get_stock_data(symbol, days=days, include_live=True)
            
            if df is not None and not df.empty:
                # המרת האינדקס ל-timestamp
                df.index.name = 'timestamp'
                df = df.reset_index()
                df = df.set_index('timestamp')
                
                # בחירת העמודות הנדרשות
                required_columns = ['open', 'close', 'volume', 'high', 'low']
                available_columns = [col for col in required_columns if col in df.columns]
                
                if available_columns:
                    return df[available_columns].astype(float)
            
            return None
            
        except Exception as e:
            logging.warning(f"שגיאה בשליפת נתונים מ-FMP עבור {symbol}: {e}")
            return None

    def get_pe_ratio(self, symbol: str) -> tuple:
        """
        מחזיר את ה-PE ratio של המניה ואת ה-PE הממוצע של הסקטור
        """
        try:
            fundamentals = self.fetch_fundamentals_batch([symbol])
            if symbol in fundamentals and fundamentals[symbol]:
                pe = fundamentals[symbol].get('pe', 0)
                sector_pe = fundamentals[symbol].get('sectorPE', 0)
                return pe, sector_pe
        except Exception as e:
            print(f"שגיאה בקבלת PE ratio ל-{symbol}: {e}")
        return 0, 0

    def get_sentiment_score(self, symbol: str) -> float:
        """
        מחזיר ציון סנטימנט עבור המניה
        """
        try:
            news = self.fetch_news_batch([symbol], limit=5)
            if symbol in news and news[symbol]:
                sentiment_scores = []
                for article in news[symbol]:
                    if 'sentiment' in article and 'score' in article['sentiment']:
                        sentiment_scores.append(article['sentiment']['score'])
                if sentiment_scores:
                    return sum(sentiment_scores) / len(sentiment_scores)
        except Exception as e:
            print(f"שגיאה בקבלת סנטימנט ל-{symbol}: {e}")
        return 0.0

    def get_growth_rate(self, symbol: str) -> float:
        """
        מחזיר את קצב הצמיחה של המניה
        """
        try:
            fundamentals = self.fetch_fundamentals_batch([symbol])
            if symbol in fundamentals and fundamentals[symbol]:
                # נסה לקבל נתוני צמיחה מפונדמנטלים
                growth = fundamentals[symbol].get('revenueGrowth', 0)
                return growth
        except Exception as e:
            print(f"שגיאה בקבלת קצב צמיחה ל-{symbol}: {e}")
        return 0.0

    def get_last_earnings_surprise(self, symbol: str) -> tuple:
        """
        מחזיר את הפתעת הרווחים האחרונה
        """
        try:
            # נסה לקבל נתוני earnings surprise
            # כרגע נחזיר ערכים דומים
            return 0.05, 0.02  # surprise, surprise_pct
        except Exception as e:
            print(f"שגיאה בקבלת earnings surprise ל-{symbol}: {e}")
        return 0.0, 0.0

    def get_geo_risk_score(self, symbol: str) -> float:
        """
        מחזיר ציון סיכון גיאופוליטי
        """
        try:
            # כרגע נחזיר ציון קבוע
            return 0.3  # סיכון נמוך-בינוני
        except Exception as e:
            print(f"שגיאה בקבלת סיכון גיאופוליטי ל-{symbol}: {e}")
        return 0.5

# יצירת instance גלובלי לשימוש בטסטים
data_fetcher = DataFetcher()
