
import os
import sys
from sqlalchemy import create_engine, text, MetaData
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
        print(f"🔧 Fixing Indexes & Constraints on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        engine = db.engine
        metadata = db.metadata
        
        # Configure migration context
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            diff = compare_metadata(context, metadata)
            
            # Initialize Operations with context
            op = Operations(context)
            
            if not diff:
                print("✅ No missing indexes or constraints found.")
                return

            print(f"🔍 Found {len(diff)} discrepancies. Applying fixes safely...")
            
            for change in diff:
                op_type = change[0]
                
                # --- FIX INDEXES ---
                if op_type == 'add_index':
                    index = change[1]
                    table_name = index.table.name
                    index_name = index.name
                    
                    print(f"➕ Adding Index: {index_name} on table {table_name}...", end=" ")
                    try:
                        # Construct CREATE INDEX manually to be safe
                        # Using alembic op.create_index is better but needs active transaction context
                        # We will use raw SQL for maximum control and error handling
                        
                        cols = [c.name for c in index.columns]
                        col_str = ", ".join([f'"{c}"' for c in cols])
                        unique_str = "UNIQUE" if index.unique else ""
                        
                        sql = f'CREATE {unique_str} INDEX IF NOT EXISTS "{index_name}" ON "{table_name}" ({col_str});'
                        connection.execute(text(sql))
                        connection.commit()
                        print("✅ Done.")
                    except Exception as e:
                        print(f"❌ Failed: {e}")
                        connection.rollback()

                # --- FIX FOREIGN KEYS ---
                elif op_type == 'add_fk':
                    fk_constraint = change[1]
                    table_name = fk_constraint.table.name
                    fk_name = fk_constraint.name
                    
                    # Generate a name if None (Postgres needs named constraints)
                    if not fk_name:
                        fk_name = f"fk_{table_name}_{fk_constraint.column_keys[0]}_{fk_constraint.elements[0].column.table.name}"
                    
                    print(f"🔗 Adding FK: {fk_name} on {table_name}...", end=" ")
                    try:
                        local_cols = [f'"{c}"' for c in fk_constraint.column_keys]
                        remote_table = fk_constraint.elements[0].column.table.name
                        remote_cols = [f'"{e.column.name}"' for e in fk_constraint.elements]
                        
                        ondelete = f"ON DELETE {fk_constraint.ondelete}" if fk_constraint.ondelete else ""
                        onupdate = f"ON UPDATE {fk_constraint.onupdate}" if fk_constraint.onupdate else ""
                        
                        sql = f'''
                            ALTER TABLE "{table_name}" 
                            ADD CONSTRAINT "{fk_name}" 
                            FOREIGN KEY ({", ".join(local_cols)}) 
                            REFERENCES "{remote_table}" ({", ".join(remote_cols)})
                            {ondelete} {onupdate};
                        '''
                        connection.execute(text(sql))
                        connection.commit()
                        print("✅ Done.")
                    except Exception as e:
                        # Common error: constraint already exists with different name
                        if "already exists" in str(e):
                            print("⚠️ Already exists (skipped).")
                        else:
                            print(f"❌ Failed: {e}")
                        connection.rollback()
                        
                # --- FIX UNIQUE CONSTRAINTS ---
                elif op_type == 'add_constraint':
                    constraint = change[1]
                    # Only handle UniqueConstraint here, CheckConstraint is harder
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
                        except Exception as e:
                            print(f"❌ Failed: {e}")
                            connection.rollback()

            print("\n🎉 Index & Constraint repairs completed.")

if __name__ == "__main__":
    fix_indexes_and_constraints()
