
import json
import os
import sys
from sqlalchemy import text
from app import create_app
from extensions import db

def import_from_json(filename, app=None):
    """
    Import data from a JSON backup file into the database.
    WARNING: This will replace existing data in the database.
    Returns: (success: bool, messages: list)
    """
    messages = []
    
    def log(msg):
        print(msg)
        messages.append(msg)

    if app is None:
        try:
            from flask import current_app
            if current_app:
                app = current_app
            else:
                app = create_app()
        except Exception:
            app = create_app()
            
    with app.app_context():
        # Handle absolute paths vs filenames
        if os.path.isabs(filename):
            filepath = filename
        elif os.path.exists(filename):
            filepath = filename
        else:
            filepath = os.path.join(os.getcwd(), 'exports', filename)
            
        if not os.path.exists(filepath):
            log(f"Error: File not found: {filepath}")
            return False, messages

        log(f"Loading data from {filepath}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            log(f"Error loading JSON file: {e}")
            return False, messages

        connection = db.engine.connect()
        trans = connection.begin()
        
        try:
            log(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            log("Preparing database for import...")
            
            # 1. Disable Foreign Key Constraints
            # This allows us to insert data in any order without FK violations
            if 'postgresql' in connection.dialect.name:
                try:
                    connection.execute(text("SET session_replication_role = 'replica';"))
                except Exception as e:
                    log(f"Warning: Could not set replication role: {e}")
            elif 'sqlite' in connection.dialect.name:
                connection.execute(text("PRAGMA foreign_keys = OFF;"))
            
            # Phase 1: Clear all tables
            log("Clearing tables...")
            tables_to_import = list(data.keys())
            
            for table_name in tables_to_import:
                try:
                    # Use a nested transaction for truncate
                    with connection.begin_nested():
                        connection.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
                except Exception:
                    # Fallback for SQLite or if CASCADE not supported
                    try:
                        with connection.begin_nested():
                             connection.execute(text(f"DELETE FROM {table_name}"))
                    except Exception as e:
                        log(f"  Warning: Could not clear table {table_name}: {e}")

            # Phase 2: Insert data
            for table_name, records in data.items():
                if not records:
                    continue
                
                log(f"Importing {len(records)} records into {table_name}...")
                
                # Get columns from first record
                columns = ", ".join(records[0].keys())
                placeholders = ", ".join([f":{key}" for key in records[0].keys()])
                
                # Prepare records for insertion
                prepared_records = []
                import json
                
                for record in records:
                    new_record = record.copy()
                    for key, value in new_record.items():
                        # Handle list/dict types that need to be JSON serialized for JSON columns
                        if isinstance(value, (dict, list)):
                            new_record[key] = json.dumps(value)
                    prepared_records.append(new_record)

                try:
                    # Use raw SQL for speed and simplicity
                    stmt = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
                    connection.execute(stmt, prepared_records)
                    log(f"  Inserted {len(records)} rows into {table_name}")
                except Exception as e:
                    log(f"Error importing {table_name}: {e}")
                    raise e

            # Re-enable FK checks (at the end)
            if 'postgresql' in connection.dialect.name:
                 try:
                    connection.execute(text("SET session_replication_role = 'origin';"))
                 except Exception:
                    pass
                    
            # 3. Reset Sequences (Postgres specific, crucial for ID auto-increment)
            if 'postgresql' in db.engine.url.drivername:
                log("Resetting sequences...")
                # Find all sequences and reset them to max(id)
                # This is a complex SQL but necessary for a functional restore
                # We can try to guess sequence names usually table_id_seq
                for table_name in data.keys():
                    try:
                        # Use nested transaction for each sequence reset attempt
                        # so one failure doesn't abort the whole process
                        with connection.begin_nested():
                            # Check if table has 'id' column
                            result = connection.execute(text(f"SELECT MAX(id) FROM {table_name}"))
                            max_id = result.scalar()
                            if max_id is not None:
                                seq_name = f"{table_name}_id_seq"
                                # Try reset
                                try:
                                    connection.execute(text(f"SELECT setval('{seq_name}', {max_id}, true)"))
                                except Exception:
                                    # Try public schema prefix
                                    try:
                                        connection.execute(text(f"SELECT setval('public.{seq_name}', {max_id}, true)"))
                                    except Exception:
                                        pass # Sequence might have different name or not exist
                    except Exception:
                        pass

            # 4. Re-enable Constraints
            if 'postgresql' in db.engine.url.drivername:
                connection.execute(text("SET session_replication_role = 'origin';"))
            elif 'sqlite' in db.engine.url.drivername:
                connection.execute(text("PRAGMA foreign_keys = ON;"))

            trans.commit()
            log("Import completed successfully.")
            return True, messages
            
        except Exception as e:
            trans.rollback()
            log(f"CRITICAL ERROR during import: {e}")
            # Try to re-enable constraints even on failure
            try:
                if 'postgresql' in db.engine.url.drivername:
                    connection.execute(text("SET session_replication_role = 'origin';"))
            except:
                pass
            return False, messages
        finally:
            connection.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_data_json.py <filename>")
        print("Available exports:")
        exports_dir = os.path.join(os.getcwd(), 'exports')
        if os.path.exists(exports_dir):
            files = [f for f in os.listdir(exports_dir) if f.endswith('.json')]
            for f in files:
                print(f" - {f}")
    else:
        import_from_json(sys.argv[1])
