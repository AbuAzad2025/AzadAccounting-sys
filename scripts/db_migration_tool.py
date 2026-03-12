
import os
import sys
import json
import gzip
import datetime
from decimal import Decimal
import traceback

print("Script started...", file=sys.stderr)

try:
    from sqlalchemy import create_engine, MetaData, inspect, text
    from sqlalchemy.orm import sessionmaker

    # Add project root to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from app import create_app
    from extensions import db
    print("Imports successful...", file=sys.stderr)
except Exception as e:
    print(f"Import Error: {e}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

# Custom JSON Encoder for special types
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, bytes):
            return obj.hex()  # Store bytes as hex string
        return super().default(obj)

def get_sorted_tables(metadata):
    """Sort tables based on foreign key dependencies."""
    # metadata.sorted_tables returns tables in dependency order (parent first)
    return metadata.sorted_tables

def dump_database(output_file="production_data.json.gz"):
    print("Creating app context...", file=sys.stderr)
    try:
        app = create_app()
    except Exception as e:
        print(f"Error creating app: {e}", file=sys.stderr)
        traceback.print_exc()
        return

    with app.app_context():
        print(f"Exporting data from: {app.config['SQLALCHEMY_DATABASE_URI']}", file=sys.stderr)
        try:
            metadata = MetaData()
            metadata.reflect(bind=db.engine)
            
            data = {}
            # Iterate over sorted tables
            sorted_tables = get_sorted_tables(metadata)
            
            total_rows = 0
            for table in sorted_tables:
                print(f"  - Dumping table: {table.name}...", file=sys.stderr)
                # Select all rows
                result = db.session.execute(table.select())
                rows = []
                keys = result.keys()
                for row in result:
                    # Convert row to dict
                    row_dict = {}
                    for idx, col in enumerate(keys):
                        val = row[idx]
                        # Handle specific types if needed, but JSON encoder handles most
                        row_dict[col] = val
                    rows.append(row_dict)
                
                data[table.name] = rows
                total_rows += len(rows)
                
            print(f"Total rows exported: {total_rows}", file=sys.stderr)
            
            print(f"Writing to {output_file}...", file=sys.stderr)
            with gzip.open(output_file, 'wt', encoding='utf-8') as f:
                json.dump(data, f, cls=CustomEncoder, indent=2)
                
            print("Export completed successfully.", file=sys.stderr)
        except Exception as e:
             print(f"Dump Error: {e}", file=sys.stderr)
             traceback.print_exc()

def restore_database(input_file="production_data.json.gz"):
    print("Creating app context for restore...", file=sys.stderr)
    try:
        app = create_app()
    except Exception as e:
        print(f"Error creating app: {e}", file=sys.stderr)
        traceback.print_exc()
        return

    with app.app_context():
        print(f"Importing data to: {app.config['SQLALCHEMY_DATABASE_URI']}", file=sys.stderr)
        
        if not os.path.exists(input_file):
            print(f"Error: File {input_file} not found.", file=sys.stderr)
            return

        print(f"Reading {input_file}...", file=sys.stderr)
        try:
            with gzip.open(input_file, 'rt', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading dump file: {e}", file=sys.stderr)
            return
            
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        
        is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
        
        # Disable FK checks
        if is_postgres:
            print("Disabling Foreign Key checks (Postgres)...", file=sys.stderr)
            db.session.execute(text("SET session_replication_role = 'replica';"))
        else:
            print("Disabling Foreign Key checks (SQLite)...", file=sys.stderr)
            db.session.execute(text("PRAGMA foreign_keys = OFF;"))

        try:
            # 1. Truncate/Delete all tables in REVERSE dependency order (child first)
            sorted_tables = get_sorted_tables(metadata)
            reversed_tables = list(reversed(sorted_tables))
            
            print("Cleaning existing data...", file=sys.stderr)
            for table in reversed_tables:
                if table.name in data:
                    # Only delete if we are going to import data for it
                    db.session.execute(table.delete())
            
            # 2. Insert data in dependency order (parent first)
            for table in sorted_tables:
                if table.name not in data:
                    continue
                
                rows = data[table.name]
                if not rows:
                    continue
                    
                print(f"  - Importing {len(rows)} rows into {table.name}...", file=sys.stderr)
                
                prepared_rows = []
                for row in rows:
                    new_row = {}
                    for col_name, val in row.items():
                        if val is None:
                            new_row[col_name] = None
                            continue
                            
                        # Check column type
                        col = table.columns.get(col_name)
                        if col is None: 
                            continue # Column might have been removed
                            
                        col_type = str(col.type).lower()
                        
                        # Type conversion logic
                        if 'date' in col_type or 'time' in col_type:
                            if isinstance(val, str):
                                try:
                                    if 'T' in val:
                                        new_row[col_name] = datetime.datetime.fromisoformat(val)
                                    else:
                                        # Handle simple date
                                        new_row[col_name] = datetime.datetime.strptime(val, "%Y-%m-%d").date()
                                except:
                                    new_row[col_name] = val
                            else:
                                new_row[col_name] = val
                        elif 'numeric' in col_type or 'decimal' in col_type:
                            new_row[col_name] = Decimal(val)
                        elif 'bytea' in col_type or 'binary' in col_type:
                            if isinstance(val, str):
                                new_row[col_name] = bytes.fromhex(val)
                            else:
                                new_row[col_name] = val
                        else:
                            new_row[col_name] = val
                    prepared_rows.append(new_row)
                
                # Bulk insert in chunks
                if prepared_rows:
                    chunk_size = 500
                    for i in range(0, len(prepared_rows), chunk_size):
                        chunk = prepared_rows[i:i+chunk_size]
                        db.session.execute(table.insert(), chunk)
                        
            # 3. Reset Sequences (Postgres specific)
            if is_postgres:
                print("Resetting sequences...", file=sys.stderr)
                # Reset all sequences for tables with 'id' column
                for table in sorted_tables:
                    if 'id' in table.columns:
                        seq_name = f"{table.name}_id_seq"
                        try:
                            # Check if sequence exists
                            check_sql = text(f"SELECT 1 FROM pg_class WHERE relname = '{seq_name}'")
                            if db.session.execute(check_sql).scalar():
                                sql = text(f"SELECT setval('{seq_name}', (SELECT MAX(id) FROM {table.name}));")
                                db.session.execute(sql)
                        except Exception:
                            pass

            db.session.commit()
            print("Import completed successfully.", file=sys.stderr)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during import: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
        finally:
            if is_postgres:
                db.session.execute(text("SET session_replication_role = 'origin';"))
            else:
                db.session.execute(text("PRAGMA foreign_keys = ON;"))
            db.session.commit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db_migration_tool.py [dump|restore]", file=sys.stderr)
        sys.exit(1)
        
    action = sys.argv[1]
    print(f"Action: {action}", file=sys.stderr)
    
    if action == "dump":
        dump_database()
    elif action == "restore":
        restore_database()
    else:
        print("Invalid action. Use 'dump' or 'restore'.", file=sys.stderr)
