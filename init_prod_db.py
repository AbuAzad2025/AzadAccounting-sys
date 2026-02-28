import os
import sys
import getpass
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Try to load from .env first, but allow manual override
load_dotenv(".env")

def get_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input.strip() or default
    else:
        return input(f"{prompt}: ").strip()

def init_prod_db():
    print("\n🚀 === Production Database Initialization Script === 🚀")
    print("WARNING: This script will WIPE and RECREATE the target database.")
    print("Use with extreme caution on production systems.\n")

    # 1. Gather Credentials
    print("--- Database Credentials ---")
    
    # Defaults from env or standard PythonAnywhere patterns
    default_host = os.environ.get("PGHOST", "Azad-4977.postgres.pythonanywhere-services.com")
    default_port = os.environ.get("PGPORT", "14977")
    default_user = os.environ.get("PGUSER", "super") # Based on user screenshot
    default_db = os.environ.get("PGDATABASE", "garage_db") # Placeholder
    
    host = get_input("Host", default_host)
    port = get_input("Port", default_port)
    user = get_input("Username", default_user)
    db_name = get_input("Target Database Name", default_db)
    
    # Check if password is in env to avoid typing it every time
    env_password = os.environ.get("PGPASSWORD")
    if env_password:
        use_env_pass = input("Found password in env. Use it? (yes/no) [yes]: ").strip().lower() or "yes"
        if use_env_pass == "yes":
            password = env_password
        else:
            password = getpass.getpass("Password: ")
    else:
        password = getpass.getpass("Password: ")

    if not password:
        print("❌ Error: Password is required.")
        return

    # 2. Confirm Action
    print(f"\n⚠️  TARGET: {user}@{host}:{port}/{db_name}")
    confirm = input("Are you SURE you want to DESTROY and RECREATE this database? (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    try:
        # 3. Connect to Maintenance DB (postgres)
        print("\n1️⃣ Connecting to maintenance database 'postgres'...")
        # For maintenance connection, we use raw parameters, so special chars in password are fine
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # 4. Terminate Connections
        print(f"2️⃣ Terminating connections to '{db_name}'...")
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid();
        """)

        # 5. Drop Database
        print(f"3️⃣ Dropping database '{db_name}' (if exists)...")
        cur.execute(f"DROP DATABASE IF EXISTS \"{db_name}\";")

        # 6. Create Database
        print(f"4️⃣ Creating fresh database '{db_name}'...")
        cur.execute(f"CREATE DATABASE \"{db_name}\" WITH ENCODING 'UTF8';")

        cur.close()
        conn.close()
        print("✅ Database reset successfully.")

        # 7. Initialize Schema (using App Context)
        print("\n5️⃣ Initializing Schema & Seed Data...")
        
        # CRITICAL FIX: URL Encode the password for the connection string
        # This handles special characters like '@' in the password correctly
        encoded_password = quote_plus(password)
        
        # Construct the safe URL
        safe_db_url = f"postgresql://{user}:{encoded_password}@{host}:{port}/{db_name}"
        
        # Force set the environment variable for this process
        os.environ["DATABASE_URL"] = safe_db_url
        os.environ["FLASK_APP"] = "app.py"
        
        print(f"🔌 Connecting to app with safe URL (password hidden)...")
        
        # Import app here to use the updated env
        from app import create_app
        from extensions import db
        from flask_migrate import upgrade
        
        app = create_app()
        with app.app_context():
            print("📦 Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully!")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_prod_db()
