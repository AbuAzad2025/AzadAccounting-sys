
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
        
        # --- FIX 1: Ensure Critical Tables have Primary Keys ---
        # List of tables that are referenced by Foreign Keys and MUST have a PK
        critical_tables = ['users', 'products', 'warehouses', 'customers', 'suppliers']
        
        for table_name in critical_tables:
            if table_name not in existing_tables:
                continue
                
            try:
                print(f"🔍 Checking '{table_name}' table constraints...")
                pk_check = inspector.get_pk_constraint(table_name)
                
                # If no PK or empty constrained columns
                if not pk_check or not pk_check.get('constrained_columns'):
                    print(f"⚠️ '{table_name}' table missing PRIMARY KEY! Fixing...")
                    try:
                        # Try to add PK on 'id' column
                        db.session.execute(text(f"ALTER TABLE {table_name} ADD PRIMARY KEY (id);"))
                        db.session.commit()
                        print(f"✅ Added PRIMARY KEY to '{table_name}'.")
                    except Exception as pk_err:
                        print(f"❌ Failed to add PK to '{table_name}': {pk_err}")
                        db.session.rollback()
                else:
                    print(f"✅ '{table_name}' table has PK: {pk_check.get('constrained_columns')}")
            except Exception as e:
                print(f"⚠️ Warning checking {table_name} PK: {e}")
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
