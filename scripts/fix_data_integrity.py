import os
import sys
from sqlalchemy import create_engine, text, inspect

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db

def fix_orphaned_data():
    app = create_app()
    with app.app_context():
        print(f"🧹 Starting DATA INTEGRITY CLEANUP on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        engine = db.engine
        inspector = inspect(engine)
        
        # Explicit fixes for known issues from logs
        # 1. payments.expense_id -> expenses.id
        # 2. payments.refund_of_id -> payments.id
        
        known_issues = [
            {
                'table': 'payments',
                'col': 'expense_id',
                'ref_table': 'expenses',
                'ref_col': 'id',
                'nullable': True 
            },
            {
                'table': 'payments',
                'col': 'refund_of_id',
                'ref_table': 'payments',
                'ref_col': 'id',
                'nullable': True
            },
            {
                'table': 'exchange_rates',
                'col': 'base_code',
                'ref_table': 'currencies',
                'ref_col': 'code',
                'nullable': False # Assuming not nullable, might need delete
            },
             {
                'table': 'exchange_rates',
                'col': 'quote_code',
                'ref_table': 'currencies',
                'ref_col': 'code',
                'nullable': False
            }
        ]

        with engine.connect() as connection:
            # 1. Fix known specific issues first
            print("\n🔧 Fixing Known Orphaned Data Issues...")
            for issue in known_issues:
                table = issue['table']
                col = issue['col']
                ref_table = issue['ref_table']
                ref_col = issue['ref_col']
                
                # Check for orphans
                sql_check = text(f'''
                    SELECT COUNT(*) FROM "{table}" 
                    WHERE "{col}" IS NOT NULL 
                    AND "{col}" NOT IN (SELECT "{ref_col}" FROM "{ref_table}")
                ''')
                
                try:
                    result = connection.execute(sql_check).scalar()
                    if result > 0:
                        print(f"   🚩 Found {result} orphans in {table}.{col} referencing {ref_table}.{ref_col}")
                        
                        if issue.get('nullable', True):
                            print(f"      ↳ Nullifying orphans...")
                            sql_fix = text(f'''
                                UPDATE "{table}" 
                                SET "{col}" = NULL 
                                WHERE "{col}" IS NOT NULL 
                                AND "{col}" NOT IN (SELECT "{ref_col}" FROM "{ref_table}")
                            ''')
                        else:
                            print(f"      ↳ DELETING orphans (Not nullable)...")
                            sql_fix = text(f'''
                                DELETE FROM "{table}" 
                                WHERE "{col}" IS NOT NULL 
                                AND "{col}" NOT IN (SELECT "{ref_col}" FROM "{ref_table}")
                            ''')
                            
                        connection.execute(sql_fix)
                        connection.commit()
                        print("      ✅ Fixed.")
                    else:
                        print(f"   ✅ No orphans in {table}.{col}")
                except Exception as e:
                    print(f"   ⚠️ Could not check/fix {table}.{col}: {e}")
                    connection.rollback()

            # 2. General check for all FKs defined in models
            # This is harder to automate perfectly without iterating all models, 
            # but we can try to infer from what we know or just rely on the user running fix_indexes again.
            
            print("\n✅ Data Integrity Check Complete.")

if __name__ == "__main__":
    fix_orphaned_data()
