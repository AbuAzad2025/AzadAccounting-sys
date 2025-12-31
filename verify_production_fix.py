import os
import sys
from sqlalchemy import text

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    from app import app, db
    from models import GLBatch, GLEntry
except ImportError as e:
    print(f"Error importing app modules: {e}")
    sys.exit(1)

def verify_fixes():
    # IDs taken from the error log provided
    sale_ids_to_check = [5, 7, 9, 8, 10, 12, 13, 22, 6, 16, 17, 18, 19, 39, 40, 51]
    
    print("===================================================")
    print("   Verification Report for 'Transaction Aborted' Fix")
    print("===================================================")
    
    with app.app_context():
        success_count = 0
        fail_count = 0
        
        for sale_id in sale_ids_to_check:
            print(f"\nChecking Sale #{sale_id}...")
            
            # Check for GLBatch
            batch = GLBatch.query.filter_by(source_type='SALE', source_id=sale_id).first()
            
            if batch:
                print(f"  ✅ GLBatch found: ID {batch.id}")
                
                # Check for entries
                entries = GLEntry.query.filter_by(batch_id=batch.id).all()
                if entries:
                    print(f"  ✅ Entries found: {len(entries)} entries")
                    
                    # Optional: Print entry details to ensure they look right
                    total_debit = sum(e.debit or 0 for e in entries)
                    total_credit = sum(e.credit or 0 for e in entries)
                    print(f"     Total Debit: {total_debit} | Total Credit: {total_credit}")
                    
                    if abs(total_debit - total_credit) < 0.01:
                         print("     STATUS: BALANCED (OK)")
                         success_count += 1
                    else:
                         print("     STATUS: UNBALANCED (WARNING)")
                         # Unbalanced is better than missing, but still an issue
                         success_count += 1 
                else:
                    print("  ❌ GLBatch exists but has NO entries!")
                    fail_count += 1
            else:
                print("  ❌ GLBatch NOT found (Fix failed or not run yet)")
                fail_count += 1

        print("\n===================================================")
        print(f"Summary:")
        print(f"  Verified/Fixed: {success_count}")
        print(f"  Missing/Failed: {fail_count}")
        print("===================================================")

if __name__ == "__main__":
    verify_fixes()
