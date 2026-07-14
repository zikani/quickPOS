import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "quickpos.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

os.makedirs(BACKUP_DIR, exist_ok=True)

class Settings:
    STORE_NAME = "QuickPOS Terminal"
    STORE_ADDRESS = "123 Commerce Way, Tech District"
    STORE_PHONE = "+1 (555) 123-4567"
    STORE_TAX_ID = "TX-987654321"
    
    CURRENCY = "$"
    TAX_RATE = 0.0825  # 8.25% Sales Tax by default
    LOW_STOCK_THRESHOLD = 10
    
    # Session config
    AUTO_LOCK_SECONDS = 900  # 15 minutes

settings = Settings()
