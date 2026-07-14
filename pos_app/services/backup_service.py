import shutil
import os
from datetime import datetime
from pos_app.config.settings import DB_PATH, BACKUP_DIR

class BackupService:
    def create_backup(self) -> str | None:
        """Create a timestamped backup copy of the current SQLite database."""
        if not os.path.exists(DB_PATH):
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"quickpos_backup_{timestamp}.db"
        dest_path = os.path.join(BACKUP_DIR, backup_filename)
        
        try:
            shutil.copy2(DB_PATH, dest_path)
            return dest_path
        except IOError:
            return None

    def restore_backup(self, backup_filename: str) -> bool:
        """Overwrite the current database with a selected backup database."""
        source_path = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(source_path):
            return False
            
        try:
            shutil.copy2(source_path, DB_PATH)
            return True
        except IOError:
            return False

    def list_backups(self) -> list[str]:
        if not os.path.exists(BACKUP_DIR):
            return []
        return sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
