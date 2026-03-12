
import os
import sys
from sqlalchemy import create_engine, text, MetaData, inspect
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from alembic.operations import Operations

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db

def fix_indexes_and_constraints():
    app = create_app()
    with app.app_context():
        print(f"🔧 Starting STRICT Schema Synchronization on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        engine = db.engine
        metadata = db.metadata
        inspector = inspect(engine)
        
        stats = {'added': 0, 'renamed': 0, 'skipped': 0, 'errors': 0}

        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            diff = compare_metadata(context, metadata)
            
            if not diff:
                print("✅ Schema is perfectly IN SYNC. No actions needed.")
                return

            print(f"🔍 Found {len(diff)} discrepancies. Analyzing...\n")
            
            for change in diff:
                op_type = change[0]
                
                # --- FIX INDEXES ---
                if op_type == 'add_index':
                    index = change[1]
                    table_name = index.table.name
                    expected_name = index.name
                    col_names = [c.name for c in index.columns]
                    
                    # Check existing indexes
                    existing_indexes = inspector.get_indexes(table_name)
                    found_equivalent = False
                    existing_name = None
                    
                    for existing in existing_indexes:
                        if existing['column_names'] == col_names:
                            found_equivalent = True
                            existing_name = existing['name']
                            break
                    
                    if found_equivalent:
                        if existing_name != expected_name:
                            print(f"🔄 Renaming Index on '{table_name}': '{existing_name}' -> '{expected_name}'...", end=" ")
                            try:
                                sql = f'ALTER INDEX "{existing_name}" RENAME TO "{expected_name}";'
                                connection.execute(text(sql))
                                connection.commit()
                                print("✅ Done.")
                                stats['renamed'] += 1
                            except Exception as e:
                                print(f"❌ Failed: {e}")
                                stats['errors'] += 1
                                connection.rollback()
                        else:
                            print(f"⏩ Index '{expected_name}' exists and matches. (Skipped)")
                            stats['skipped'] += 1
                    else:
                        print(f"➕ Adding Index: {expected_name} on table {table_name}...", end=" ")
                        try:
                            col_str = ", ".join([f'"{c}"' for c in col_names])
                            unique_str = "UNIQUE" if index.unique else ""
                            sql = f'CREATE {unique_str} INDEX IF NOT EXISTS "{expected_name}" ON "{table_name}" ({col_str});'
                            connection.execute(text(sql))
                            connection.commit()
                            print("✅ Done.")
                            stats['added'] += 1
                        except Exception as e:
                            print(f"❌ Failed: {e}")
                            stats['errors'] += 1
                            connection.rollback()

                # --- FIX FOREIGN KEYS ---
                elif op_type == 'add_fk':
                    fk_constraint = change[1]
                    table_name = fk_constraint.table.name
                    expected_name = fk_constraint.name
                    
                    if not expected_name:
                         # Skip unnamed FKs or generate standard name
                         expected_name = f"fk_{table_name}_{fk_constraint.column_keys[0]}_{fk_constraint.elements[0].column.table.name}"

                    # Check existing FKs
                    existing_fks = inspector.get_foreign_keys(table_name)
                    local_cols = fk_constraint.column_keys
                    found_equivalent = False
                    existing_name = None
                    
                    for existing in existing_fks:
                        if existing['constrained_columns'] == local_cols:
                            found_equivalent = True
                            existing_name = existing['name']
                            break
                    
                    if found_equivalent:
                        if existing_name != expected_name:
                            print(f"🔄 Renaming FK on '{table_name}': '{existing_name}' -> '{expected_name}'...", end=" ")
                            try:
                                # Postgres requires renaming the constraint
                                sql = f'ALTER TABLE "{table_name}" RENAME CONSTRAINT "{existing_name}" TO "{expected_name}";'
                                connection.execute(text(sql))
                                connection.commit()
                                print("✅ Done.")
                                stats['renamed'] += 1
                            except Exception as e:
                                print(f"❌ Failed: {e}")
                                stats['errors'] += 1
                                connection.rollback()
                        else:
                            print(f"⏩ FK '{expected_name}' exists and matches. (Skipped)")
                            stats['skipped'] += 1
                    else:
                        print(f"🔗 Adding FK: {expected_name} on {table_name}...", end=" ")
                        try:
                            local_cols_str = ", ".join([f'"{c}"' for c in fk_constraint.column_keys])
                            remote_table = fk_constraint.elements[0].column.table.name
                            remote_cols_str = ", ".join([f'"{e.column.name}"' for e in fk_constraint.elements])
                            ondelete = f"ON DELETE {fk_constraint.ondelete}" if fk_constraint.ondelete else ""
                            onupdate = f"ON UPDATE {fk_constraint.onupdate}" if fk_constraint.onupdate else ""
                            
                            sql = f'''
                                ALTER TABLE "{table_name}" 
                                ADD CONSTRAINT "{expected_name}" 
                                FOREIGN KEY ({local_cols_str}) 
                                REFERENCES "{remote_table}" ({remote_cols_str})
                                {ondelete} {onupdate};
                            '''
                            connection.execute(text(sql))
                            connection.commit()
                            print("✅ Done.")
                            stats['added'] += 1
                        except Exception as e:
                            print(f"❌ Failed: {e}")
                            stats['errors'] += 1
                            connection.rollback()

            print("\n" + "="*50)
            print("📊 STRICT SYNCHRONIZATION REPORT")
            print(f"   - Added: {stats['added']}")
            print(f"   - Renamed (Corrected): {stats['renamed']}")
            print(f"   - Skipped (Perfect Match): {stats['skipped']}")
            print(f"   - Errors: {stats['errors']}")
            print("="*50)

if __name__ == "__main__":
    fix_indexes_and_constraints()
