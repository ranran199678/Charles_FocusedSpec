# 📊 מדריך העלאת נתונים - Charles FocusedSpec

## 🎯 מטרה
מאגר נתונים מרכזי להפחתת שימוש ב-API ולאחסון מידע היסטורי.

## 📁 מבנה תיקיות ופורמט קבצים

### 1. **נתוני מחירים גולמיים**
- **תיקייה:** `data/raw_price_data/`
- **פורמט:** CSV
- **עמודות מקוריות:** `"Date","Price","Open","High","Low","Vol.","Change %"`
- **עמודות נדרשות (אחרי עיבוד):** `date,symbol,open,high,low,close,volume,adjusted_close`
- **דוגמה מקורית:**
```csv
"Date","Price","Open","High","Low","Vol.","Change %"
"07/25/2025","213.88","214.70","215.24","213.40","40.27M","0.06%"
"07/24/2025","213.76","213.90","215.69","213.53","46.02M","-0.18%"
```
- **המערכת תמיר אוטומטית לפורמט הנדרש**

### 2. **חדשות פיננסיות**
- **תיקייה:** `data/news_sentiment/financial_news/`
- **פורמט:** CSV או JSON
- **עמודות נדרשות:** `date,symbol,headline,sentiment,source,url,category`
- **דוגמה:**
```csv
date,symbol,headline,sentiment,source,url,category
2020-01-01,AAPL,Apple Reports Strong Q4 Earnings,0.8,Reuters,https://...,earnings
```

### 3. **סנטימנט רשת**
- **תיקייה:** `data/news_sentiment/social_media/`
- **פורמט:** CSV או JSON
- **עמודות נדרשות:** `date,symbol,platform,sentiment,volume,engagement`
- **דוגמה:**
```csv
date,symbol,platform,sentiment,volume,engagement
2020-01-01,AAPL,Twitter,0.6,1500,25000
```

### 4. **דירוגי אנליסטים**
- **תיקייה:** `data/news_sentiment/analyst_ratings/`
- **פורמט:** CSV
- **עמודות נדרשות:** `date,symbol,analyst_firm,rating,price_target,action`
- **דוגמה:**
```csv
date,symbol,analyst_firm,rating,price_target,action
2020-01-01,AAPL,Morgan Stanley,Buy,180.00,Upgrade
```

### 5. **מדדי שוק**
- **תיקייה:** `data/market_data/indices/`
- **פורמט:** CSV
- **עמודות נדרשות:** `date,index_symbol,open,high,low,close,volume`
- **דוגמה:**
```csv
date,index_symbol,open,high,low,close,volume
2020-01-01,SPY,3200.00,3220.00,3190.00,3210.00,1000000
```

### 6. **נתוני סקטורים**
- **תיקייה:** `data/market_data/sectors/`
- **פורמט:** CSV
- **עמודות נדרשות:** `date,sector,performance,volume,change_pct`
- **דוגמה:**
```csv
date,sector,performance,volume,change_pct
2020-01-01,Technology,1.5,5000000,2.3
```

### 7. **נתוני מאקרו**
- **תיקייה:** `data/market_data/economic_indicators/`
- **פורמט:** CSV
- **עמודות נדרשות:** `date,indicator,value,unit,source`
- **דוגמה:**
```csv
date,indicator,value,unit,source
2020-01-01,Interest_Rate,2.5,percent,Fed
```

## 🔄 זרימת עבודה

### שלב 1: העלאת נתונים גולמיים
1. העלה קבצי CSV/JSON לתיקיות המתאימות
2. הרץ את `enhanced_data_processor.py` לעיבוד נתוני מחירים
3. הרץ את `news_data_processor.py` לעיבוד חדשות (אם יש)
4. הרץ את `market_data_processor.py` לעיבוד נתוני שוק (אם יש)

### שלב 2: שימוש במערכת
```python
from data_manager import DataManager

dm = DataManager()
# שליפת נתונים מהמאגר
df_prices = dm.get_price_data('AAPL', '2020-01-01', '2024-12-31')
df_news = dm.get_news('AAPL', '2020-01-01', '2024-12-31')

# בדיקת חוסרים
missing_dates = dm.find_missing_dates('AAPL', '2020-01-01', '2024-12-31')

# עדכון המאגר בנתונים חדשים
dm.update_price_data('AAPL', df_new_data)
```

## 📋 רשימת סימבולים מומלצת
קובץ `data/metadata/symbols_list.csv` מכיל רשימת מניות נפוצות.
ניתן להרחיב עם:
- S&P 500 (500 מניות)
- NASDAQ 100 (100 מניות)
- Russell 2000 (2000 מניות)

## ⚠️ הערות חשובות
1. **תאריכים:** השתמש בפורמט YYYY-MM-DD
2. **ערכים:** השתמש בנקודות עשרוניות (לא פסיקים)
3. **קידוד:** UTF-8
4. **גיבוי:** שמור גיבוי של כל הקבצים המקוריים

## 🛠️ כלי עיבוד
- `enhanced_data_processor.py` - עיבוד נתוני מחירים ואינדיקטורים
- `data_manager.py` - ממשק מרכזי לשליפה ועדכון
- `news_data_processor.py` - עיבוד חדשות וסנטימנט (בקרוב)
- `market_data_processor.py` - עיבוד נתוני שוק ומאקרו (בקרוב) 