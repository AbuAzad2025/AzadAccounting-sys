
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import text
from app import create_app
from extensions import db

def fix_sequences():
    print("🔧 Fixing Database Sequences...")
    app = create_app()
    with app.app_context():
        # Get all tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        for table in tables:
            try:
                # Construct sequence name (Postgres default: table_id_seq)
                seq_name = f"{table}_id_seq"
                
                # Check if sequence exists
                check_sql = text(f"SELECT 1 FROM information_schema.sequences WHERE sequence_name = :seq")
                result = db.session.execute(check_sql, {'seq': seq_name}).fetchone()
                
                if result:
                    print(f"  Processing {table}...")
                    # Get max id
                    max_id_sql = text(f"SELECT MAX(id) FROM \"{table}\"")
                    max_id = db.session.execute(max_id_sql).scalar() or 0
                    
                    # Set sequence to max_id + 1
                    next_val = max_id + 1
                    reset_sql = text(f"ALTER SEQUENCE \"{seq_name}\" RESTART WITH {next_val}")
                    db.session.execute(reset_sql)
                    print(f"  ✅ {table}: Sequence reset to {next_val}")
            except Exception as e:
                print(f"  ⚠️ Error processing {table}: {e}")
                
        db.session.commit()
        print("\n✨ All sequences fixed successfully!")

if __name__ == "__main__":
    fix_sequences()
