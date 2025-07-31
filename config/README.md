# Config - הגדרות מערכת

## 🎯 מטרת התיקייה

תיקיית `config/` מכילה את כל קבצי ההגדרות של המערכת - הגדרות API keys, פרמטרים טכניים, הגדרות אינדיקטורים, והגדרות מערכת כלליות. קבצים אלה מגדירים את התנהגות המערכת והפרמטרים של כל הסוכנים.

## 📊 סטטוס הגדרות

- **קבצי הגדרות:** 2 קבצים
- **API Keys:** 3/7 זמינים
- **הגדרות טכניות:** ✅ זמינות
- **הגדרות מערכת:** ✅ זמינות

## 📋 טבלת קבצים ותפקידים

| קובץ | תפקיד | תלות עיקרית | סטטוס |
|------|-------|--------------|--------|
| `config.yaml` | הגדרות ראשיות | yaml | ✅ פעיל |
| `gap_config.yaml` | הגדרות גאפים | yaml | ✅ פעיל |

## 🚀 דוגמאות שימוש

### קריאת הגדרות ראשיות
```python
import yaml
from config.config import load_config

# טעינת הגדרות
config = load_config()

# קריאת API keys
api_keys = config['api_keys']
print(f"Available APIs: {list(api_keys.keys())}")

# קריאת הגדרות טכניות
technical_config = config['technical']
print(f"RSI Period: {technical_config['rsi_period']}")
print(f"MACD Fast: {technical_config['macd_fast']}")
```

### קריאת הגדרות גאפים
```python
import yaml
from config.gap_config import load_gap_config

# טעינת הגדרות גאפים
gap_config = load_gap_config()

# קריאת פרמטרים
min_gap_size = gap_config['min_gap_size']
max_gap_size = gap_config['max_gap_size']
print(f"Gap range: {min_gap_size}% - {max_gap_size}%")
```

### עדכון הגדרות
```python
import yaml

def update_api_key(api_name, new_key):
    """עדכון API key"""
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    config['api_keys'][api_name] = new_key
    
    with open('config/config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Updated {api_name} API key")

# דוגמה לשימוש
update_api_key('alpha_vantage', 'YOUR_NEW_KEY')
```

### הגדרת פרמטרים טכניים
```python
import yaml

def update_technical_params():
    """עדכון פרמטרים טכניים"""
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # עדכון פרמטרים
    config['technical']['rsi_period'] = 14
    config['technical']['macd_fast'] = 12
    config['technical']['macd_slow'] = 26
    config['technical']['bollinger_period'] = 20
    
    with open('config/config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("Updated technical parameters")
```

## 🔧 פקודות הפעלה

### בדיקת הגדרות
```bash
# בדיקת הגדרות ראשיות
python -c "import yaml; config = yaml.safe_load(open('config/config.yaml')); print('API Keys:', list(config['api_keys'].keys()))"

# בדיקת הגדרות גאפים
python -c "import yaml; gap_config = yaml.safe_load(open('config/gap_config.yaml')); print('Gap config:', gap_config)"
```

### עדכון הגדרות
```bash
# עדכון API key
python -c "import yaml; config = yaml.safe_load(open('config/config.yaml')); config['api_keys']['alpha_vantage'] = 'NEW_KEY'; yaml.dump(config, open('config/config.yaml', 'w'))"

# עדכון פרמטרים טכניים
python -c "import yaml; config = yaml.safe_load(open('config/config.yaml')); config['technical']['rsi_period'] = 21; yaml.dump(config, open('config/config.yaml', 'w'))"
```

### בדיקת תקינות
```bash
# בדיקת תקינות הגדרות
python -c "from config.config import validate_config; validate_config()"
```

## 📊 מבנה הגדרות

### config.yaml - הגדרות ראשיות
```yaml
# API Keys
api_keys:
  finnhub: "YOUR_FINNHUB_API_KEY"
  fmp: "YOUR_FMP_API_KEY"
  twelve_data: "YOUR_TWELVE_API_KEY"
  alpha_vantage: "YOUR_ALPHA_VANTAGE_API_KEY"
  marketaux: "YOUR_MARKETAUX_API_KEY"
  newsdata: "YOUR_NEWSDATA_API_KEY"
  reuters: "YOUR_REUTERS_API_KEY"

# הגדרות טכניות
technical:
  rsi_period: 14
  macd_fast: 12
  macd_slow: 26
  macd_signal: 9
  bollinger_period: 20
  bollinger_std: 2
  atr_period: 14
  sma_periods: [20, 50, 200]
  ema_periods: [20, 50, 200]

# הגדרות מערכת
system:
  data_dir: "data/"
  output_dir: "outputs/"
  log_level: "INFO"
  max_workers: 4
  cache_timeout: 3600
```

### gap_config.yaml - הגדרות גאפים
```yaml
# פרמטרים בסיסיים
min_gap_size: 2.0
max_gap_size: 20.0
min_volume_surge: 1.5
max_volume_surge: 10.0

# פרמטרים מתקדמים
gap_types:
  common_gap: 2.0
  breakaway_gap: 5.0
  runaway_gap: 8.0
  exhaustion_gap: 15.0

# פרמטרי נפח
volume_analysis:
  min_volume: 1000000
  volume_sma_period: 20
  volume_surge_threshold: 2.0

# פרמטרי מחיר
price_analysis:
  min_price: 5.0
  max_price: 1000.0
  price_change_threshold: 0.5
```

## 🔑 ניהול API Keys

### API Keys זמינים
```yaml
# ✅ זמינים
finnhub: "YOUR_FINNHUB_API_KEY"
fmp: "YOUR_FMP_API_KEY"
twelve_data: "YOUR_TWELVE_API_KEY"

# ❌ חסרים
alpha_vantage: "YOUR_ALPHA_VANTAGE_API_KEY"
marketaux: "YOUR_MARKETAUX_API_KEY"
newsdata: "YOUR_NEWSDATA_API_KEY"
reuters: "YOUR_REUTERS_API_KEY"
```

### הוספת API Key חדש
```python
def add_api_key(api_name, api_key):
    """הוספת API key חדש"""
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    config['api_keys'][api_name] = api_key
    
    with open('config/config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Added {api_name} API key")

# דוגמה
add_api_key('alpha_vantage', 'YOUR_NEW_KEY')
```

## ⚠️ בעיות ידועות

### בעיות הגדרות
1. **API Keys חסרים** - 4 מתוך 7
   - **פתרון:** הוספת API keys
   - **סטטוס:** ⚠️ ידוע

2. **הגדרות לא מעודכנות** - פרמטרים ישנים
   - **פתרון:** עדכון הגדרות
   - **סטטוס:** ⚠️ ידוע

3. **תקינות הגדרות** - בדיקת תקינות
   - **פתרון:** Validation functions
   - **סטטוס:** ⚠️ ידוע

### פתרונות מוצעים
- הוספת validation functions
- עדכון API keys חסרים
- שיפור תיעוד הגדרות
- הוספת default values

## 🔄 תלויות

### תלויות פנימיות
- `utils/` - שימוש בהגדרות
- `core/` - פרמטרים לסוכנים
- `data/` - הגדרות נתונים

### תלויות חיצוניות
- `yaml` - קריאת קבצי YAML
- `os` - ניהול קבצים
- `json` - פורמט חלופי

## 📈 ביצועים

### זמני טעינה
- **טעינת הגדרות:** <0.1 שניות
- **עדכון הגדרות:** <0.1 שניות
- **validation:** <0.1 שניות

### אופטימיזציה
- Caching הגדרות
- Lazy loading
- Validation מקדים
- Error handling

## 🔧 תחזוקה

### גיבוי הגדרות
```python
import shutil
from datetime import datetime

def backup_config():
    """גיבוי הגדרות"""
    backup_dir = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copytree('config/', backup_dir)
    print(f"Config backed up to: {backup_dir}")
```

### שחזור הגדרות
```python
import shutil

def restore_config(backup_dir):
    """שחזור הגדרות"""
    shutil.rmtree('config/')
    shutil.copytree(backup_dir, 'config/')
    print(f"Config restored from: {backup_dir}")
```

### ניקוי הגדרות
```python
import yaml

def cleanup_config():
    """ניקוי הגדרות"""
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # הסרת API keys ריקים
    config['api_keys'] = {k: v for k, v in config['api_keys'].items() if v and v != 'YOUR_KEY'}
    
    with open('config/config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("Cleaned up config")
```

## 📋 רשימת בדיקה

### בדיקות יומיות
- [ ] בדיקת זמינות API keys
- [ ] בדיקת תקינות הגדרות
- [ ] בדיקת פרמטרים טכניים
- [ ] גיבוי הגדרות

### בדיקות שבועיות
- [ ] עדכון API keys
- [ ] עדכון פרמטרים
- [ ] ניקוי הגדרות
- [ ] בדיקת ביצועים

### בדיקות לפני release
- [ ] בדיקת תקינות מלאה
- [ ] עדכון תיעוד
- [ ] גיבוי הגדרות
- [ ] בדיקת compatibility

---

**הערה:** הגדרות הן קריטיות לפעולת המערכת. יש לוודא תקינות ועדכניות לפני כל הרצה.