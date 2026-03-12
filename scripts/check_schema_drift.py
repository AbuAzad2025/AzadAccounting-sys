
import os
import sys
from sqlalchemy import create_engine, inspect, MetaData
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db

def check_schema_drift():
    app = create_app()
    with app.app_context():
        print(f"🔍 Checking schema drift on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Get database connection
        engine = db.engine
        
        # Get metadata from Models (what code expects)
        metadata = db.metadata
        
        # Get migration context
        opts = {
            'compare_type': True,  # Check column types
            'compare_server_default': True,  # Check defaults
        }
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection, opts=opts)
            diff = compare_metadata(context, metadata)
            
        if not diff:
            print("✅ Schema is perfectly IN SYNC. No missing columns or tables.")
        else:
            print("\n⚠️  SCHEMA DRIFT DETECTED! Found the following differences:")
            print("=" * 60)
            
            for op in diff:
                op_type = op[0]
                
                if op_type == 'add_table':
                    print(f"❌ Missing Table in DB: {op[1].name}")
                elif op_type == 'remove_table':
                    print(f"ℹ️  Extra Table in DB (not in code): {op[1].name}")
                elif op_type == 'add_column':
                    # op = ('add_column', 'schema', 'table_name', Column('name', ...))
                    table_name = op[2]
                    col_name = op[3].name
                    print(f"❌ Missing Column in DB: Table '{table_name}' -> Column '{col_name}'")
                elif op_type == 'remove_column':
                    table_name = op[2]
                    col_name = op[3].name
                    print(f"ℹ️  Extra Column in DB: Table '{table_name}' -> Column '{col_name}'")
                elif op_type == 'modify_type':
                    table_name = op[2]
                    col_name = op[3]
                    print(f"⚠️  Type Mismatch: Table '{table_name}' -> Column '{col_name}'")
                else:
                    print(f"⚠️  Other Change: {op}")
            
            print("=" * 60)
            print("\n💡 Recommendation: If you see 'Missing Column', you need to add it manually or run a migration.")

if __name__ == "__main__":
    check_schema_drift()
