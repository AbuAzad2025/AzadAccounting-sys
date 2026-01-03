
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
            if 'postgresql' in db.engine.url.drivername:
                connection.execute(text("SET session_replication_role = 'replica';"))
            elif 'sqlite' in db.engine.url.drivername:
                connection.execute(text("PRAGMA foreign_keys = OFF;"))
            # Add MySQL handling if needed
            
            # 2. Iterate through tables and insert data
            for table_name, records in data.items():
                if not records:
                    continue
                    
                log(f"Importing {len(records)} records into {table_name}...")
                
                # Option: Truncate table before import?
                # User said "restore", usually implies replacing state.
                # To be safe against duplicates, we should probably clear the table first.
                try:
                    # Use a nested transaction for truncate to avoid aborting the main transaction on error
                    with connection.begin_nested():
                        connection.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
                except Exception:
                    # Fallback for SQLite or if CASCADE not supported
                    # Also use nested transaction for delete
                    try:
                        with connection.begin_nested():
                             connection.execute(text(f"DELETE FROM {table_name}"))
                    except Exception as e:
                        log(f"  Warning: Could not clear table {table_name}: {e}")
                
                # Bulk insert is tricky with raw SQL and varying columns, 
                # but since it's a restore, we assume schema matches keys.
                # We'll use SQLAlchemy's insert.
                
                # Get table object
                from sqlalchemy import MetaData, Table
                metadata = MetaData()
                try:
                    table = Table(table_name, metadata, autoload_with=connection)
                except Exception as e:
                    log(f"  Warning: Could not load table {table_name}: {e}")
                    continue

                # Insert in chunks
                chunk_size = 1000
                for i in range(0, len(records), chunk_size):
                    chunk = records[i:i + chunk_size]
                    try:
                        # Ensure chunk is a list of dictionaries
                        if not isinstance(chunk, list):
                            log(f"Error: Chunk is not a list for {table_name}")
                            continue
                            
                        # If table has 'method' column (enum), we might need to handle it?
                        # SQLAlchemy usually handles string -> Enum mapping if the value matches.
                        
                        connection.execute(table.insert(), chunk)
                        log(f"  Inserted {len(chunk)} rows into {table_name}")
                        trans.commit()
                        trans = connection.begin()
                    except Exception as e:
                        log(f"Error inserting chunk into {table_name}: {e}")
                        # If a chunk fails, we might want to stop or continue?
                        # For now, let's re-raise to rollback everything
                        raise e
                    
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
