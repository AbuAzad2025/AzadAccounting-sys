
import os
import sys
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.schema import CreateIndex, CreateConstraint
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
                            # Use SQLAlchemy to generate correct DDL for functional/partial indexes
                            # This handles func.lower(), postgresql_where, etc. correctly
                            connection.execute(CreateIndex(index))
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
                    # Fix for indexes that are "extra" but also "missing" with different properties (e.g. Unique vs Non-Unique)
                    # We should drop them to allow 'add_index' to recreate them correctly
                    index = change[1]
                    table_name = index.table.name
                    index_name = index.name
                    
                    # Check if this index is also in the 'add_index' list (implies recreation needed)
                    is_recreation = False
                    for other_change in diff:
                        if other_change[0] == 'add_index' and other_change[1].name == index_name and other_change[1].table.name == table_name:
                            is_recreation = True
                            break
                    
                    if is_recreation:
                        print(f"♻️  Recreating Index (Drop Old): {index_name} on {table_name}...", end=" ")
                        try:
                            sql = f'DROP INDEX IF EXISTS "{index_name}";'
                            connection.execute(text(sql))
                            connection.commit()
                            print("✅ Done.")
                            stats['added'] += 1 # Count as action taken
                        except Exception as e:
                            print(f"❌ Failed: {e}")
                            connection.rollback()
                    else:
                        # NEW: Force drop specific "stubborn" indexes that appear as Extra but also Missing in check report
                        stubborn_indexes = [
                            'ix_payments_payment_number', 'ix_payments_receipt_number', 
                            'uq_products_name_global_ci', 'uq_products_name_wh_ci', 
                            'uq_products_serial_ci', 'uq_products_sku_ci',
                            'ix_invoices_invoice_number'
                        ]
                        if index_name in stubborn_indexes:
                            print(f"🔨 Force Dropping Stubborn Index: {index_name} on {table_name}...", end=" ")
                            try:
                                sql = f'DROP INDEX IF EXISTS "{index_name}";'
                                connection.execute(text(sql))
                                connection.commit()
                                print("✅ Done.")
                                stats['added'] += 1
                            except Exception as e:
                                print(f"❌ Failed: {e}")
                                connection.rollback()
                
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
                        # Special handling for Enum(native_enum=False) which is effectively VARCHAR
                        is_new_enum_varchar = False
                        if hasattr(new_type, 'native_enum') and new_type.native_enum is False:
                             is_new_enum_varchar = True
                        
                        if 'VARCHAR' in existing_str and (
                            'VARCHAR' in new_str or 'STRING' in new_str or is_new_enum_varchar
                        ):
                            import re
                            match_old = re.search(r'\(.*?(\d+).*?\)', existing_str)
                            len_old = int(match_old.group(1)) if match_old else 0
                            
                            # If it's Enum(native_enum=False), we need to find max length of values
                            len_new = 0
                            if is_new_enum_varchar:
                                if hasattr(new_type, 'enums'):
                                     len_new = max(len(e) for e in new_type.enums) if new_type.enums else 0
                                elif hasattr(new_type, 'length'):
                                     len_new = new_type.length
                            else:
                                match_new = re.search(r'\(.*?(\d+).*?\)', new_str)
                                len_new = int(match_new.group(1)) if match_new else 0
                            
                            # If new length is greater, OR if it's just converting to Enum-Varchar wrapper
                            # we can just run the ALTER because VARCHAR(N) -> VARCHAR(M) where M>=N is safe
                            if len_new >= len_old:
                                is_string_expansion = True
                        
                        # 2. Check Enum Fix (VARCHAR -> Native Enum)
                        if 'ENUM' in new_str and 'VARCHAR' in existing_str and not is_new_enum_varchar:
                             is_enum_fix = True
                             
                    except Exception as e:
                        print(f"DEBUG: Type check error: {e}")
                        pass
                        
                    if is_string_expansion:
                        # Construct the new type string correctly
                        new_type_sql = new_type
                        if is_new_enum_varchar:
                             # Force it to be VARCHAR(N) for the ALTER statement
                             # Otherwise SQLAlchemy might try to output ENUM syntax
                             # We need to find the length
                             length = 255
                             if hasattr(new_type, 'length') and new_type.length:
                                 length = new_type.length
                             elif hasattr(new_type, 'enums'):
                                 length = max(len(e) for e in new_type.enums)
                             new_type_sql = f"VARCHAR({length})"

                        print(f"📏 Expanding Column: {table_name}.{col_name} ({existing_type} -> {new_type_sql})...", end=" ")
                        try:
                            sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{col_name}" TYPE {new_type_sql};'
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
                            
                            if hasattr(new_type, 'name'):
                                enum_name = new_type.name
                                # First ensure enum type exists
                                # Extract values from Enum type if available to create it
                                if hasattr(new_type, 'enums'):
                                    enums_str = ", ".join([f"'{e}'" for e in new_type.enums])
                                    create_type_sql = f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}') THEN CREATE TYPE {enum_name} AS ENUM ({enums_str}); END IF; END $$;"
                                    connection.execute(text(create_type_sql))
                                
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
