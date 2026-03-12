
import os
import sys
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db

def fix_sale_returns_schema():
    app = create_app()
    with app.app_context():
        print(f"Fixing schema on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Check if column exists
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sale_returns' AND column_name='return_date';
        """)
        
        result = db.session.execute(check_sql).fetchone()
        
        if result:
            print("✅ Column 'return_date' already exists in 'sale_returns'.")
        else:
            print("⚠️ Column 'return_date' missing. Adding it now...")
            try:
                # Add the column with a default value of created_at (since return_date usually equals creation date)
                alter_sql = text("ALTER TABLE sale_returns ADD COLUMN return_date TIMESTAMP;")
                db.session.execute(alter_sql)
                
                # Backfill data: set return_date = created_at for existing rows
                update_sql = text("UPDATE sale_returns SET return_date = created_at WHERE return_date IS NULL;")
                db.session.execute(update_sql)
                
                # Add index for performance
                index_sql = text("CREATE INDEX IF NOT EXISTS ix_sale_returns_return_date ON sale_returns (return_date);")
                db.session.execute(index_sql)
                
                db.session.commit()
                print("✅ Successfully added 'return_date' column.")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    fix_sale_returns_schema()
