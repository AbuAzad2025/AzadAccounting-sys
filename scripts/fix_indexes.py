
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
        print(f"🔧 Starting Professional Schema Synchronization on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        engine = db.engine
        metadata = db.metadata
        inspector = inspect(engine)
        
        # Stats
        stats = {'indexes_added': 0, 'fks_added': 0, 'skipped': 0, 'errors': 0}

        # Configure migration context
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            diff = compare_metadata(context, metadata)
            
            if not diff:
                print("✅ Schema is perfectly IN SYNC. No actions needed.")
                return

            print(f"🔍 Found {len(diff)} discrepancies. Applying fixes safely...\n")
            
            for change in diff:
                op_type = change[0]
                
                # --- FIX INDEXES ---
                if op_type == 'add_index':
                    index = change[1]
                    table_name = index.table.name
                    index_name = index.name
                    
                    # Check if index exists (by columns) to avoid duplicate/redundant indexes
                    existing_indexes = inspector.get_indexes(table_name)
                    col_names = [c.name for c in index.columns]
                    already_exists = False
                    for existing in existing_indexes:
                        if existing['column_names'] == col_names:
                            already_exists = True
                            break
                    
                    if already_exists:
                        print(f"⏩ Skipping Index '{index_name}' on '{table_name}' (Equivalent index exists).")
                        stats['skipped'] += 1
                        continue

                    print(f"➕ Adding Index: {index_name} on table {table_name}...", end=" ")
                    try:
                        cols = [c.name for c in index.columns]
                        col_str = ", ".join([f'"{c}"' for c in cols])
                        unique_str = "UNIQUE" if index.unique else ""
                        
                        sql = f'CREATE {unique_str} INDEX IF NOT EXISTS "{index_name}" ON "{table_name}" ({col_str});'
                        connection.execute(text(sql))
                        connection.commit()
                        print("✅ Done.")
                        stats['indexes_added'] += 1
                    except Exception as e:
                        print(f"❌ Failed: {e}")
                        stats['errors'] += 1
                        connection.rollback()

                # --- FIX FOREIGN KEYS ---
                elif op_type == 'add_fk':
                    fk_constraint = change[1]
                    table_name = fk_constraint.table.name
                    fk_name = fk_constraint.name
                    
                    # Generate a name if None
                    if not fk_name:
                        fk_name = f"fk_{table_name}_{fk_constraint.column_keys[0]}_{fk_constraint.elements[0].column.table.name}"
                    
                    # Double check if constraint exists (postgres constraint names are unique per schema)
                    # or if a FK on these columns already exists
                    existing_fks = inspector.get_foreign_keys(table_name)
                    local_cols = fk_constraint.column_keys
                    already_exists = False
                    for existing in existing_fks:
                        # Compare columns
                        if existing['constrained_columns'] == local_cols:
                            already_exists = True
                            break
                    
                    if already_exists:
                        print(f"⏩ Skipping FK '{fk_name}' on '{table_name}' (Equivalent FK exists).")
                        stats['skipped'] += 1
                        continue

                    print(f"🔗 Adding FK: {fk_name} on {table_name}...", end=" ")
                    try:
                        local_cols_str = ", ".join([f'"{c}"' for c in fk_constraint.column_keys])
                        remote_table = fk_constraint.elements[0].column.table.name
                        remote_cols_str = ", ".join([f'"{e.column.name}"' for e in fk_constraint.elements])
                        
                        ondelete = f"ON DELETE {fk_constraint.ondelete}" if fk_constraint.ondelete else ""
                        onupdate = f"ON UPDATE {fk_constraint.onupdate}" if fk_constraint.onupdate else ""
                        
                        sql = f'''
                            ALTER TABLE "{table_name}" 
                            ADD CONSTRAINT "{fk_name}" 
                            FOREIGN KEY ({local_cols_str}) 
                            REFERENCES "{remote_table}" ({remote_cols_str})
                            {ondelete} {onupdate};
                        '''
                        connection.execute(text(sql))
                        connection.commit()
                        print("✅ Done.")
                        stats['fks_added'] += 1
                    except Exception as e:
                        if "already exists" in str(e):
                            print("⚠️ Already exists (skipped).")
                            stats['skipped'] += 1
                        elif "insert or update on table" in str(e) and "violates foreign key constraint" in str(e):
                             print(f"❌ Data Integrity Error: Cannot add FK because orphan data exists.")
                             stats['errors'] += 1
                        else:
                            print(f"❌ Failed: {e}")
                            stats['errors'] += 1
                        connection.rollback()
                        
                # --- FIX UNIQUE CONSTRAINTS ---
                elif op_type == 'add_constraint':
                    constraint = change[1]
                    if hasattr(constraint, 'columns'): 
                        table_name = constraint.table.name
                        con_name = constraint.name
                        if not con_name:
                            con_name = f"uq_{table_name}_{'_'.join([c.name for c in constraint.columns])}"
                            
                        print(f"🔒 Adding Unique Constraint: {con_name} on {table_name}...", end=" ")
                        try:
                            cols = [f'"{c.name}"' for c in constraint.columns]
                            sql = f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{con_name}" UNIQUE ({", ".join(cols)});'
                            connection.execute(text(sql))
                            connection.commit()
                            print("✅ Done.")
                            stats['indexes_added'] += 1 # counting as index roughly
                        except Exception as e:
                            print(f"❌ Failed: {e}")
                            stats['errors'] += 1
                            connection.rollback()

            print("\n" + "="*50)
            print("📊 SYNCHRONIZATION REPORT")
            print(f"   - Indexes Added: {stats['indexes_added']}")
            print(f"   - Foreign Keys Added: {stats['fks_added']}")
            print(f"   - Skipped (Already Exists): {stats['skipped']}")
            print(f"   - Errors: {stats['errors']}")
            print("="*50)
            
            if stats['errors'] == 0:
                print("🎉 Database Schema is now robust and synchronized.")
            else:
                print("⚠️ Some issues occurred. Check logs above.")

if __name__ == "__main__":
    fix_indexes_and_constraints()
