
import os
import sys
from flask import Flask
from sqlalchemy import inspect, text

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app import create_app
from extensions import db
from models import *  # Import all models to ensure they are registered

def check_postgres_compatibility():
    app = create_app()
    with app.app_context():
        print("Checking PostgreSQL compatibility and missing indexes...")
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        missing_indexes = []
        
        for table_name in tables:
            fks = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            pks = inspector.get_pk_constraint(table_name)
            
            # Helper to check if a column list is covered by an index
            def is_indexed(columns):
                # Check primary key
                if pks and pks['constrained_columns'] == columns:
                    return True
                
                # Check explicit indexes
                for idx in indexes:
                    # Index covers the columns if it starts with them
                    # (simplification: exact match or prefix match logic could be added)
                    idx_cols = idx['column_names']
                    if len(idx_cols) >= len(columns) and idx_cols[:len(columns)] == columns:
                        return True
                return False

            for fk in fks:
                constrained_columns = fk['constrained_columns']
                if not is_indexed(constrained_columns):
                    missing_indexes.append(f"Table '{table_name}' missing index on FK columns: {constrained_columns} -> {fk['referred_table']}")

        if missing_indexes:
            print(f"Found {len(missing_indexes)} missing indexes on foreign keys:")
            for msg in missing_indexes:
                print(f" - {msg}")
            print("\nRecommendation: Create indexes for these foreign keys to improve JOIN performance.")
        else:
            print("✅ All foreign keys appear to be indexed.")

        # Check for reserved words or other issues
        print("\nChecking for potential reserved word conflicts...")
        reserved_words = {'user', 'order', 'limit', 'offset', 'group', 'table', 'create', 'select', 'insert', 'update', 'delete', 'where', 'from', 'desc', 'asc'}
        
        potential_conflicts = []
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            for col in columns:
                if col['name'].lower() in reserved_words:
                    potential_conflicts.append(f"Table '{table_name}' has column '{col['name']}' which is a reserved word.")
                    
        if potential_conflicts:
            print(f"Found {len(potential_conflicts)} potential reserved word conflicts:")
            for msg in potential_conflicts:
                print(f" - {msg}")
        else:
            print("✅ No obvious reserved word conflicts found.")

if __name__ == "__main__":
    check_postgres_compatibility()
