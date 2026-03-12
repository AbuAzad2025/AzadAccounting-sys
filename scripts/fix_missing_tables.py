
import os
import sys
from sqlalchemy import text, inspect

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db

def fix_missing_tables():
    app = create_app()
    with app.app_context():
        print(f"🔧 Fixing missing tables on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # List of critical tables that were reported missing
        # We will use db.create_all() but restrict it to only create what's missing
        # effectively, db.create_all() checks existence, but sometimes explicit creation is safer
        
        print(f"Existing tables: {len(existing_tables)}")
        
        # Explicitly create tables if they don't exist
        # This uses SQLAlchemy's metadata to create CREATE TABLE statements
        # It won't touch existing tables
        try:
            print("🚀 Running db.create_all() to create missing tables...")
            db.create_all()
            print("✅ db.create_all() completed.")
            
            # Re-check
            inspector = inspect(db.engine)
            current_tables = inspector.get_table_names()
            
            missing_previously = ['stock_movements', 'notifications', 'blocked_countries', 'blocked_ips']
            for tbl in missing_previously:
                if tbl in current_tables:
                    print(f"✅ Table '{tbl}' is now present.")
                else:
                    print(f"❌ Table '{tbl}' is STILL MISSING!")
                    
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            
        # Additional Schema Fixes (Columns that might be missed by create_all if table existed but col didn't)
        # Check sale_returns again just in case
        try:
            print("🔍 Verifying 'sale_returns.return_date'...")
            res = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='sale_returns' AND column_name='return_date'")).fetchone()
            if not res:
                print("⚠️ Adding missing column 'return_date' to 'sale_returns'...")
                db.session.execute(text("ALTER TABLE sale_returns ADD COLUMN return_date TIMESTAMP;"))
                db.session.execute(text("UPDATE sale_returns SET return_date = created_at WHERE return_date IS NULL;"))
                db.session.commit()
                print("✅ Fixed 'sale_returns'.")
            else:
                print("✅ 'sale_returns.return_date' exists.")
        except Exception as e:
            print(f"⚠️ Warning checking sale_returns: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_missing_tables()
