import os
import sys
import datetime
import glob
import subprocess
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DB_URI = os.getenv("DATABASE_URL", "")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "backups")
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)
MAX_BACKUPS = 30 # Keep last 30 backups
PG_DUMP_PATH = os.getenv("PG_DUMP_PATH")

def find_pg_dump():
    if PG_DUMP_PATH and os.path.exists(PG_DUMP_PATH):
        return PG_DUMP_PATH
    
    # Common locations on Windows
    common_paths = [
        r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\13\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\17\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\16\bin\pg_dump.exe",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
            
    # Check if in PATH
    try:
        subprocess.run(["pg_dump", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return "pg_dump"
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
        
    return None

def find_psql():
    pg_dump = find_pg_dump()
    if pg_dump and pg_dump != "pg_dump":
        try:
            guess = os.path.join(os.path.dirname(pg_dump), "psql.exe")
            if os.path.exists(guess):
                return guess
        except Exception:
            pass

    common_paths = [
        r"C:\Program Files\PostgreSQL\18\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\17\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\13\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\17\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\16\bin\psql.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path

    try:
        subprocess.run(["psql", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return "psql"
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

def parse_db_uri(uri):
    # postgresql://user:pass@host:port/dbname
    if "://" not in uri:
        return None
    
    prefix, rest = uri.split("://", 1)
    if "@" in rest:
        auth, loc = rest.split("@", 1)
        if ":" in auth:
            user, password = auth.split(":", 1)
        else:
            user, password = auth, ""
    else:
        user, password = "", ""
        loc = rest
        
    if "/" in loc:
        host_port, dbname = loc.split("/", 1)
    else:
        host_port, dbname = loc, ""
        
    if ":" in host_port:
        host, port = host_port.split(":", 1)
    else:
        host, port = host_port, "5432"
        
    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "dbname": dbname
    }

def create_backup():
    if not DB_URI:
        print("Error: DATABASE_URL is missing.")
        return False
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    pg_dump = find_pg_dump()
    if not pg_dump:
        print("Error: pg_dump not found. Please install PostgreSQL or set PG_DUMP_PATH in .env")
        return False
        
    db_info = parse_db_uri(DB_URI)
    if not db_info:
        print("Error: Invalid DATABASE_URL")
        return False
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    print(f"Creating backup: {filepath}")
    
    # Set PGPASSWORD env var
    env = os.environ.copy()
    env["PGPASSWORD"] = db_info["password"]
    
    cmd = [
        pg_dump,
        "-h", db_info["host"],
        "-p", db_info["port"],
        "-U", db_info["user"],
        "-F", "p", # Plain text format (easier to read/edit if needed, use 'c' for custom/compressed)
        "-f", filepath,
        db_info["dbname"]
    ]
    
    try:
        subprocess.run(cmd, env=env, check=True)
        print("Backup created successfully.")
        rotate_backups()
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating backup: {e}")
        return False

def rotate_backups():
    files = glob.glob(os.path.join(BACKUP_DIR, "backup_*.sql"))
    files.sort(key=os.path.getmtime, reverse=True)
    
    if len(files) > MAX_BACKUPS:
        print(f"Rotating backups (keeping last {MAX_BACKUPS})...")
        for f in files[MAX_BACKUPS:]:
            try:
                os.remove(f)
                print(f"Deleted old backup: {os.path.basename(f)}")
            except OSError as e:
                print(f"Error deleting {f}: {e}")

def list_backups():
    files = glob.glob(os.path.join(BACKUP_DIR, "backup_*.sql"))
    files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"{'#':<3} | {'Filename':<30} | {'Size (MB)':<10} | {'Created'}")
    print("-" * 65)
    for i, f in enumerate(files):
        size_mb = os.path.getsize(f) / (1024 * 1024)
        created = datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i+1:<3} | {os.path.basename(f):<30} | {size_mb:<10.2f} | {created}")
    return files

def restore_backup():
    if not DB_URI:
        print("Error: DATABASE_URL is missing.")
        return
    psql = find_psql()
    if not psql:
        print("Error: psql not found. Please install PostgreSQL client tools or set PG_DUMP_PATH.")
        return
         
    files = list_backups()
    if not files:
        print("No backups found.")
        return
        
    try:
        choice = input("\nEnter backup number to restore (or 'q' to quit): ")
        if choice.lower() == 'q':
            return
            
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            target_file = files[idx]
            print(f"Restoring from {os.path.basename(target_file)}...")
            
            db_info = parse_db_uri(DB_URI)
            env = os.environ.copy()
            env["PGPASSWORD"] = db_info["password"]
            
            # For plain text backup, we use psql
            cmd = [
                psql,
                "-h", db_info["host"],
                "-p", db_info["port"],
                "-U", db_info["user"],
                "-d", db_info["dbname"],
                "-v", "ON_ERROR_STOP=1",
                "-f", target_file
            ]
            
            # If pg_restore/psql path is not correct, we might need to search for it too
            # Assuming it's in the same bin folder
            
            subprocess.run(cmd, env=env, check=True)
            print("Restore completed successfully.")
            
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")
    except subprocess.CalledProcessError as e:
        print(f"Error restoring backup: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "backup":
            create_backup()
        elif sys.argv[1] == "restore":
            restore_backup()
        elif sys.argv[1] == "list":
            list_backups()
        else:
            print("Usage: python manage_backup.py [backup|restore|list]")
    else:
        print("Usage: python manage_backup.py [backup|restore|list]")
