
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
        
        print(f"Existing tables: {len(existing_tables)}")
        
        # --- FIX 1: Ensure 'users' table has a Primary Key ---
        # The error "there is no unique constraint matching given keys for referenced table 'users'"
        # usually means 'users.id' is not a PK.
        try:
            print("🔍 Checking 'users' table constraints...")
            pk_check = inspector.get_pk_constraint('users')
            if not pk_check or not pk_check.get('constrained_columns'):
                print("⚠️ 'users' table missing PRIMARY KEY! Fixing...")
                # Try to add PK. This might fail if duplicates exist, but we assume user ids are unique from import.
                db.session.execute(text("ALTER TABLE users ADD PRIMARY KEY (id);"))
                db.session.commit()
                print("✅ Added PRIMARY KEY to 'users'.")
            else:
                print(f"✅ 'users' table has PK: {pk_check.get('constrained_columns')}")
        except Exception as e:
            print(f"⚠️ Warning checking users PK: {e}")
            db.session.rollback()

        # --- FIX 2: Create Missing Tables ---
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
            
        # --- FIX 3: Sale Returns Schema ---
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
