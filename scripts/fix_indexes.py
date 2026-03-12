
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

def ensure_primary_key(connection, table_name, pk_column='id'):
    """Ensures a table has a primary key on the specified column."""
    try:
        # Special handling for tables where PK is not 'id'
        if table_name == 'currencies':
            pk_column = 'code'
            
        inspector = inspect(connection)
        pk_constraint = inspector.get_pk_constraint(table_name)
        
        if not pk_constraint or not pk_constraint.get('constrained_columns'):
            print(f"   ⚠️  Target table '{table_name}' has no PK. Fixing...", end=" ")
            # Check if index exists on id to avoid duplication or conflict
            # In postgres, adding PK automatically creates unique index
            connection.execute(text(f'ALTER TABLE "{table_name}" ADD PRIMARY KEY ("{pk_column}");'))
            connection.commit()
            print("✅ PK Added.")
            return True
    except Exception as e:
        print(f"   ❌ Failed to add PK to '{table_name}': {e}")
        connection.rollback()
        return False
    return True

def fix_indexes_and_constraints():
    app = create_app()
    with app.app_context():
        print(f"🔧 Starting SELF-HEALING Schema Synchronization on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        engine = db.engine
        metadata = db.metadata
        inspector = inspect(engine)
        
        stats = {'added': 0, 'renamed': 0, 'skipped': 0, 'errors': 0, 'pks_fixed': 0}

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
                                # Check if target index exists (conflict) and drop it
                                sql_check = f"SELECT 1 FROM pg_indexes WHERE indexname = '{expected_name}';"
                                conflict = connection.execute(text(sql_check)).scalar()
                                if conflict:
                                    print(f" (Target '{expected_name}' exists, dropping old '{existing_name}' instead)...", end=" ")
                                    sql = f'DROP INDEX "{existing_name}";'
                                else:
                                    sql = f'ALTER INDEX "{existing_name}" RENAME TO "{expected_name}";'
                                
                                connection.execute(text(sql))
                                connection.commit()
                                print("✅ Done.")
                                stats['renamed'] += 1
                            except Exception as e:
                                if "already exists" in str(e) or "DuplicateTable" in str(e):
                                    print(f" (Conflict detected, dropping old '{existing_name}')...", end=" ")
                                    try:
                                        connection.rollback()
                                        sql = f'DROP INDEX "{existing_name}";'
                                        connection.execute(text(sql))
                                        connection.commit()
                                        print("✅ Done (Dropped old).")
                                        stats['renamed'] += 1
                                    except Exception as e2:
                                        print(f"❌ Failed to drop old: {e2}")
                                        stats['errors'] += 1
                                        connection.rollback()
                                else:
                                    print(f"❌ Failed: {e}")
                                    stats['errors'] += 1
                                    connection.rollback()
                        else:
                            # print(f"⏩ Index '{expected_name}' exists. (Skipped)")
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
                    fk_name = fk_constraint.name
                    
                    if not fk_name:
                         fk_name = f"fk_{table_name}_{fk_constraint.column_keys[0]}_{fk_constraint.elements[0].column.table.name}"

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
                        if existing_name != fk_name:
                            print(f"🔄 Renaming FK on '{table_name}': '{existing_name}' -> '{fk_name}'...", end=" ")
                            try:
                                # Check if target FK exists (conflict)
                                # This is harder to check with simple SQL across all tables, but we can try-catch
                                sql = f'ALTER TABLE "{table_name}" RENAME CONSTRAINT "{existing_name}" TO "{fk_name}";'
                                connection.execute(text(sql))
                                connection.commit()
                                print("✅ Done.")
                                stats['renamed'] += 1
                            except Exception as e:
                                if "already exists" in str(e):
                                    print(f" (Target '{fk_name}' exists, dropping old '{existing_name}' instead)...", end=" ")
                                    connection.rollback()
                                    try:
                                        sql = f'ALTER TABLE "{table_name}" DROP CONSTRAINT "{existing_name}";'
                                        connection.execute(text(sql))
                                        connection.commit()
                                        print("✅ Done (Dropped old).")
                                        stats['renamed'] += 1
                                    except Exception as e2:
                                        print(f"❌ Failed to drop old: {e2}")
                                        stats['errors'] += 1
                                        connection.rollback()
                                else:
                                    print(f"❌ Failed: {e}")
                                    stats['errors'] += 1
                                    connection.rollback()
                        else:
                            stats['skipped'] += 1
                    else:
                        print(f"🔗 Adding FK: {fk_name} on {table_name}...", end=" ")
                        try:
                            local_cols_str = ", ".join([f'"{c}"' for c in fk_constraint.column_keys])
                            remote_table = fk_constraint.elements[0].column.table.name
                            remote_cols_str = ", ".join([f'"{e.column.name}"' for e in fk_constraint.elements])
                            ondelete = f"ON DELETE {fk_constraint.ondelete}" if fk_constraint.ondelete else ""
                            onupdate = f"ON UPDATE {fk_constraint.onupdate}" if fk_constraint.onupdate else ""
                            
                            # --- CRITICAL FIX: Ensure referenced table has PK ---
                            ensure_primary_key(connection, remote_table)
                            
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
                            stats['added'] += 1
                        except Exception as e:
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
                            stats['added'] += 1
                        except Exception as e:
                            print(f"❌ Failed: {e}")
                            stats['errors'] += 1
                            connection.rollback()
                
                # --- FIX REMOVE INDEX ---
                elif op_type == 'remove_index':
                    # Sometimes indexes are named differently or need recreation
                    # We can try to drop them if they are truly extra
                    index = change[1]
                    table_name = index.table.name
                    index_name = index.name
                    # print(f"➖ Removing Extra Index: {index_name} on {table_name}...", end=" ")
                    # try:
                    #     sql = f'DROP INDEX IF EXISTS "{index_name}";'
                    #     connection.execute(text(sql))
                    #     connection.commit()
                    #     print("✅ Done.")
                    #     stats['added'] += 1
                    # except Exception as e:
                    #     print(f"❌ Failed: {e}")
                    #     connection.rollback()
                    pass
                
                # --- FIX TYPE MISMATCH (Safe Expansion Only & Enum Fixes) ---
                elif op_type == 'modify_type':
                    # ('modify_type', schema, table_name, col_name, existing_meta, existing_type, new_type)
                    table_name = change[2]
                    col_name = change[3]
                    existing_type = change[5]
                    new_type = change[6]
                    
                    is_string_expansion = False
                    is_enum_fix = False
                    
                    try:
                        from sqlalchemy import String, VARCHAR, Enum
                        existing_str = str(existing_type).upper()
                        new_str = str(new_type).upper()
                        
                        # 1. Check String Expansion
                        if 'VARCHAR' in existing_str and ('VARCHAR' in new_str or 'STRING' in new_str):
                            import re
                            match_old = re.search(r'\(.*?(\d+).*?\)', existing_str)
                            len_old = int(match_old.group(1)) if match_old else 0
                            
                            match_new = re.search(r'\(.*?(\d+).*?\)', new_str)
                            len_new = int(match_new.group(1)) if match_new else 0
                            
                            if len_new > len_old:
                                is_string_expansion = True
                        
                        # 2. Check Enum Fix (VARCHAR -> Enum or Enum change)
                        # Often Postgres needs explicit cast for this
                        if 'ENUM' in new_str and 'VARCHAR' in existing_str:
                             is_enum_fix = True
                             
                    except Exception as e:
                        pass
                        
                    if is_string_expansion:
                        print(f"📏 Expanding Column: {table_name}.{col_name} ({existing_type} -> {new_type})...", end=" ")
                        try:
                            sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{col_name}" TYPE {new_type};'
                            connection.execute(text(sql))
                            connection.commit()
                            print("✅ Done.")
                            stats['added'] += 1
                        except Exception as e:
                            print(f"❌ Failed: {e}")
                            stats['errors'] += 1
                            connection.rollback()
                            
                    elif is_enum_fix:
                        print(f"🔄 Converting Column to ENUM: {table_name}.{col_name}...", end=" ")
                        try:
                            # We need to extract enum name and values from new_type if possible, 
                            # or just try a generic cast if the type object has a name
                            # This is tricky without raw SQL, but we can try:
                            # ALTER TABLE t ALTER COLUMN c TYPE enum_name USING c::enum_name
                            
                            if hasattr(new_type, 'name'):
                                enum_name = new_type.name
                                # First ensure enum type exists
                                # connection.execute(text(f"CREATE TYPE {enum_name} AS ENUM ...")) # Hard to get values here easily
                                
                                # Fallback: Attempt simple cast, usually fails if type doesn't exist
                                sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{col_name}" TYPE {enum_name} USING "{col_name}"::{enum_name};'
                                connection.execute(text(sql))
                                connection.commit()
                                print("✅ Done.")
                                stats['added'] += 1
                        except Exception as e:
                            print(f"❌ Failed (Enum): {e}")
                            connection.rollback()



            print("\n" + "="*50)
            print("📊 SELF-HEALING REPORT")
            print(f"   - Added (Indexes/FKs): {stats['added']}")
            print(f"   - Renamed: {stats['renamed']}")
            print(f"   - Skipped: {stats['skipped']}")
            print(f"   - Errors: {stats['errors']}")
            print("="*50)

if __name__ == "__main__":
    fix_indexes_and_constraints()
