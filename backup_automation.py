import os
import glob
from datetime import datetime
import pathlib
from extensions import perform_backup_db

class AutomatedBackupManager:
    def __init__(self, app):
        self.app = app
        self.backup_dir = app.config.get("BACKUP_DB_DIR", os.path.join(app.instance_path, 'backups', 'db'))

    def get_backup_status(self):
        """
        Get the status of the latest backup.
        Returns a dictionary with 'latest_backup' info.
        """
        if not os.path.exists(self.backup_dir):
            return {'latest_backup': None}
        
        backups = []
        # Support various backup formats
        patterns = ['*.db', '*.dump', '*.sql', '*.sqlite']
        for pattern in patterns:
            backups.extend(glob.glob(os.path.join(self.backup_dir, pattern)))
            
        if not backups:
             return {'latest_backup': None}
             
        try:
            latest = max(backups, key=os.path.getmtime)
            mtime = datetime.fromtimestamp(os.path.getmtime(latest))
            size = os.path.getsize(latest)
            
            return {
                'latest_backup': {
                    'date': mtime,
                    'name': os.path.basename(latest),
                    'size': size,
                    'path': latest
                }
            }
        except Exception as e:
            self.app.logger.error(f"Error getting backup status: {e}")
            return {'latest_backup': None}

    def create_backup(self):
        """
        Trigger a manual backup using the unified backup function.
        Returns a pathlib.Path object of the created backup file, or None on failure.
        """
        success, msg, path = perform_backup_db(self.app)
        if success and path:
            return pathlib.Path(path)
        return None

def schedule_automated_backups(app, scheduler):
    """
    Register daily automated backup job with the global scheduler.
    The job id is 'automated_daily_backup' to integrate with control panel toggles.
    """
    try:
        scheduler.add_job(
            lambda: perform_backup_db(app),
            "cron",
            hour=3,
            minute=0,
            id="automated_daily_backup",
            name="النسخ الاحتياطي اليومي التلقائي",
            replace_existing=True,
        )
    except Exception as e:
        try:
            app.logger.warning(f"schedule_automated_backups failed: {e}")
        except Exception:
            pass
