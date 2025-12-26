import os
import sys
from sqlalchemy import text

# Add the project directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.append(project_home)

from app import create_app
from extensions import db

def reset_database():
    app = create_app()
    with app.app_context():
        print("="*60)
        print("🚨 DATABASE RESET TOOL | أداة إعادة ضبط قاعدة البيانات")
        print("="*60)
        print("WARNING: This will DELETE ALL DATA and TABLES in the database.")
        print("تحذير: هذا سيقوم بحذف جميع البيانات والجداول في قاعدة البيانات.")
        print("="*60)
        
        # Auto-confirm if argument provided (for automation if needed, but safer to ask)
        # But since user is in console, let's just do it or ask simply.
        # Given the context, the user WANTS to fix the error.
        
        print("Connecting to database...")
        try:
            # We will use raw SQL to drop the schema and recreate it to be 100% sure
            # This is the most effective way to clear everything in PostgreSQL
            with db.engine.connect() as conn:
                print("🗑️  Dropping all tables (Schema Reset)...")
                conn.execute(text("DROP SCHEMA public CASCADE;"))
                conn.execute(text("CREATE SCHEMA public;"))
                conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
                conn.commit()
                print("✅ Schema reset successfully.")
                
        except Exception as e:
            print(f"❌ Error during schema reset: {e}")
            print("Attempting fallback (db.drop_all)...")
            try:
                db.drop_all()
                with db.engine.connect() as conn:
                    conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
                    conn.commit()
                print("✅ Fallback reset successful.")
            except Exception as e2:
                print(f"❌ Fallback failed: {e2}")
                return

        print("\n✨ Database is now clean.")
        print("You can now run: flask db upgrade")
        print("="*60)

if __name__ == "__main__":
    reset_database()
