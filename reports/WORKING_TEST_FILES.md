# קבצי בדיקה עובדים - Charles FocusedSpec

## 🎯 **קבצי בדיקה מומלצים לשימוש**

### 1. `test_working_data_only.py` - **הכי מומלץ**
- **מטרה**: בדיקה עם מקורות נתונים עובדים בלבד
- **תוצאות**: ציונים אמיתיים (33-36) עם 29 סוכנים
- **שימוש**: `python test_working_data_only.py`
- **מניות**: INTC, AAPL, MSFT, GOOGL, TSLA
- **סטטוס**: ✅ עובד בהצלחה

### 2. `test_alternative_data_sources.py` - **בדיקת מקורות**
- **מטרה**: בדיקת מקורות נתונים חלופיים
- **תוצאות**: זיהוי מקורות עובדים
- **שימוש**: `python test_alternative_data_sources.py`
- **סטטוס**: ✅ עובד בהצלחה

### 3. `test_simple_real_data.py` - **בדיקה פשוטה**
- **מטרה**: בדיקה פשוטה עם נתונים אמיתיים
- **תוצאות**: ציונים אמיתיים
- **שימוש**: `python test_simple_real_data.py`
- **סטטוס**: ✅ עובד בהצלחה

## 🔧 **קבצי בדיקה לפתרון בעיות**

### 4. `check_api_keys.py` - **בדיקת מפתחות API**
- **מטרה**: בדיקת מפתחות API
- **תוצאות**: זיהוי מפתחות עובדים
- **שימוש**: `python check_api_keys.py`
- **סטטוס**: ✅ עובד בהצלחה

### 5. `test_network_connectivity.py` - **בדיקת רשת**
- **מטרה**: בדיקת חיבור רשת
- **תוצאות**: זיהוי בעיות רשת
- **שימוש**: `python test_network_connectivity.py`
- **סטטוס**: ✅ עובד בהצלחה

### 6. `test_yfinance_direct.py` - **בדיקת yfinance**
- **מטרה**: בדיקה ישירה של yfinance
- **תוצאות**: זיהוי בעיות yfinance
- **שימוש**: `python test_yfinance_direct.py`
- **סטטוס**: ❌ לא עובד (HTTP 429)

## 📊 **קבצי בדיקה כללים**

### 7. `quick_scores_test.py` - **בדיקה מהירה**
- **מטרה**: בדיקה מהירה של המערכת
- **תוצאות**: ציון כללי של המערכת
- **שימוש**: `python quick_scores_test.py`
- **סטטוס**: ✅ עובד בהצלחה

### 8. `test_qbts_complete_system.py` - **בדיקה מלאה**
- **מטרה**: בדיקה מלאה של המערכת
- **תוצאות**: ניתוח מפורט
- **שימוש**: `python test_qbts_complete_system.py`
- **סטטוס**: ⚠️ חלקי (בעיות yfinance)

## 🎯 **המלצות לשימוש**

### **לבדיקה מהירה:**
```bash
python test_working_data_only.py
```

### **לבדיקת מקורות נתונים:**
```bash
python test_alternative_data_sources.py
```

### **לבדיקת מפתחות API:**
```bash
python check_api_keys.py
```

### **לבדיקה כללית:**
```bash
python quick_scores_test.py
```

## 📈 **תוצאות צפויות**

### **עם `test_working_data_only.py`:**
- ✅ ציונים אמיתיים (33-36)
- ✅ 29 סוכנים פעילים
- ✅ נתונים מלאים (100 ימים)
- ✅ 5 מניות נבדקות בהצלחה

### **עם `test_alternative_data_sources.py`:**
- ✅ זיהוי מקורות עובדים
- ✅ השוואה בין מקורות
- ✅ סטטיסטיקות מפורטות

## 🛠️ **פתרון בעיות**

### **אם יש שגיאות yfinance:**
- השתמש ב-`test_working_data_only.py`
- עקוף yfinance עם DataFetcher

### **אם יש שגיאות API:**
- בדוק עם `check_api_keys.py`
- עדכן מפתחות API

### **אם יש בעיות רשת:**
- בדוק עם `test_network_connectivity.py`
- בדוק חיבור לאינטרנט

## 📝 **הערות חשובות**

1. **yfinance לא עובד** - השתמש ב-DataFetcher
2. **FMP Analyst Estimates לא עובד** - HTTP 403
3. **המערכת עובדת** - ציונים אמיתיים מתקבלים
4. **29 סוכנים פעילים** - המערכת פועלת היטב
5. **נתונים אמיתיים** - 5 מניות נבדקו בהצלחה 