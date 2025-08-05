import certifi
import os
import ssl
import urllib3

def fix_certificates():
    """
    תיקון בעיות תעודות SSL
    """
    try:
        # הדפסת מיקום קובץ התעודות
        cert_path = certifi.where()
        print(f"Certificate path: {cert_path}")
        
        # הגדרת משתנה סביבה לתעודות
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        os.environ['SSL_CERT_FILE'] = cert_path
        
        # עדכון urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        print("✅ תעודות SSL תוקנו בהצלחה")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בתיקון תעודות SSL: {e}")
        return False

# הרצה אוטומטית בעת ייבוא המודול
if __name__ == "__main__":
    print(certifi.where())
    fix_certificates()
