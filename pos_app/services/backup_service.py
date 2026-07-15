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


import threading
import time

class BackupScheduler(threading.Thread):
    """Background service daemon thread that executes automated database snapshots hourly."""
    def __init__(self, backup_service, interval_seconds: int = 3600):
        super().__init__()
        self.backup_service = backup_service
        self.interval = interval_seconds
        self.daemon = True # safe exit on application shutdown
        self.running = True
        
    def run(self):
        print(f"[*] Scheduled database backup daemon thread started. Active interval: {self.interval} seconds.")
        # Brief sleep to avoid contention during app startup sequence
        time.sleep(10)
        
        while self.running:
            print("[*] Automated Backup Scheduler: Initiating hot SQLite snapshot...")
            dest_path = self.backup_service.create_backup()
            if dest_path:
                print(f"[+] Automated Backup Succeeded! Snapshot file: {os.path.basename(dest_path)}")
            else:
                print("[!] Automated Backup Failed: File access error or DB lock contention.")
                
            # Sleep in 1-second ticks so we can respond immediately to shutdown stop() signals
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)
                
    def stop(self):
        self.running = False

