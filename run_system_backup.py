
import sys
import os
from app import create_app
from extensions import perform_backup_db

def run_backup():
    app = create_app()
    print("Starting system backup...")
    try:
        success, msg, path = perform_backup_db(app)
        if success:
            print(f"System Backup SUCCESS: {path}")
        else:
            print(f"System Backup FAILED: {msg}")
    except Exception as e:
        print(f"System Backup ERROR: {e}")

if __name__ == "__main__":
    run_backup()
