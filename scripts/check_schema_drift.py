
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
                
                # --- INTELLIGENT ANALYSIS ---
                # Instead of hiding differences, we analyze them and explain WHY they are happening
                # This gives transparency without the noise
                
                explanation = ""
                severity = "🔴 CRITICAL"
                
                # Analyze Type Mismatch
                if op_type == 'modify_type':
                    # op = ('modify_type', schema, table_name, col_name, existing_meta, existing_type, new_type)
                    existing_type = str(op[5]).upper()
                    new_type = str(op[6]).upper()
                    
                    if ('ENUM' in existing_type or 'VARCHAR' in existing_type) and \
                       ('ENUM' in new_type or 'VARCHAR' in new_type):
                        severity = "🟡 INFO"
                        explanation = " -> (Enum/VARCHAR representation difference. Usually safe if lengths match.)"
                    else:
                        explanation = f" -> ({existing_type} vs {new_type})"

                # Analyze Default Clause
                elif op_type == 'modify_default':
                    severity = "🟡 INFO"
                    explanation = " -> (Default value representation difference. SQL string vs Python object.)"

                # Analyze Extra Index
                elif op_type == 'remove_index':
                    idx_name = op[1].name
                    if idx_name and (idx_name.startswith('gin_') or idx_name.startswith('idx_')):
                        severity = "🟢 OPTIMIZATION"
                        explanation = " -> (Performance index added manually. Keep it.)"
                    else:
                        severity = "🟡 WARNING"
                        explanation = " -> (Index exists in DB but not in Models. May be old or duplicate.)"

                # Analyze Missing Index
                elif op_type == 'add_index':
                    idx_name = op[1].name
                    severity = "🔴 CRITICAL"
                    explanation = " -> (Index defined in Code but missing in DB. Performance risk!)"

                # --- PRINT REPORT ---
                if op_type == 'add_table':
                    print(f"❌ Missing Table in DB: {op[1].name}")
                elif op_type == 'remove_table':
                    print(f"ℹ️  Extra Table in DB: {op[1].name} {explanation}")
                elif op_type == 'add_column':
                    table_name = op[2]
                    col_name = op[3].name
                    print(f"❌ Missing Column: {table_name}.{col_name}")
                elif op_type == 'remove_column':
                    table_name = op[2]
                    col_name = op[3].name
                    print(f"ℹ️  Extra Column: {table_name}.{col_name}")
                elif op_type == 'modify_type':
                    table_name = op[2]
                    col_name = op[3]
                    print(f"{severity} Type Mismatch: {table_name}.{col_name}{explanation}")
                elif op_type == 'modify_default':
                    table_name = op[2]
                    col_name = op[3]
                    print(f"{severity} Default Change: {table_name}.{col_name}{explanation}")
                elif op_type == 'add_index':
                    print(f"{severity} Missing Index: {op[1].name} on {op[1].table.name}{explanation}")
                elif op_type == 'remove_index':
                    print(f"{severity} Extra Index: {op[1].name} on {op[1].table.name}{explanation}")
                elif op_type == 'add_fk':
                    print(f"❌ Missing Foreign Key: {op[1].name} on {op[1].table.name}")
                elif op_type == 'remove_fk':
                    print(f"ℹ️  Extra Foreign Key: {op[1].name} on {op[1].table.name}")
                else:
                    print(f"⚠️  Other Change: {op}")
            
            print("=" * 60)
            print("\n💡 Recommendation: Review 'CRITICAL' items immediately. 'INFO' items are usually safe to ignore.")

if __name__ == "__main__":
    check_schema_drift()
