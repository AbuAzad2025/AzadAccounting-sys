import os
import sys
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from app import app, db
    from models import GLBatch, GLEntry
except ImportError as e:
    print(f"Error importing app modules: {e}")
    sys.exit(1)

def check_ledger_integrity():
    print("===================================================")
    print("   Garage Manager - Ledger Integrity Check")
    print("===================================================")
    
    with app.app_context():
        conn = db.session.connection()
        
        # 1. Check for Batches with NO Entries (Empty Batches)
        print("\n1. Checking for Empty Batches (No Entries)...")
        empty_batches = conn.execute(text("""
            SELECT b.id, b.code, b.source_type, b.source_id 
            FROM gl_batches b
            LEFT JOIN gl_entries e ON b.id = e.batch_id
            WHERE e.id IS NULL
        """)).fetchall()
        
        if empty_batches:
            print(f"   [WARNING] Found {len(empty_batches)} empty batches:")
            for b in empty_batches:
                print(f"     - Batch #{b.id} ({b.code}) for {b.source_type} #{b.source_id}")
        else:
            print("   [OK] No empty batches found.")

        # 2. Check for Unbalanced Batches
        print("\n2. Checking for Unbalanced Batches (Debit != Credit)...")
        unbalanced = conn.execute(text("""
            SELECT b.id, b.code, b.source_type, b.source_id, 
                   SUM(e.debit) as total_debit, 
                   SUM(e.credit) as total_credit
            FROM gl_batches b
            JOIN gl_entries e ON b.id = e.batch_id
            GROUP BY b.id, b.code, b.source_type, b.source_id
            HAVING ABS(SUM(e.debit) - SUM(e.credit)) > 0.05
        """)).fetchall()
        
        if unbalanced:
            print(f"   [WARNING] Found {len(unbalanced)} unbalanced batches:")
            for b in unbalanced:
                diff = float(b.total_debit or 0) - float(b.total_credit or 0)
                print(f"     - Batch #{b.id} ({b.code}): Diff {diff:.2f}")
        else:
            print("   [OK] All batches are balanced.")
            
        # 3. Check for Entries with Zero Amount (Ghost Entries)
        print("\n3. Checking for Zero-Amount Entries...")
        zero_entries = conn.execute(text("""
            SELECT count(*) as count
            FROM gl_entries 
            WHERE debit = 0 AND credit = 0
        """)).scalar()
        
        if zero_entries > 0:
             print(f"   [INFO] Found {zero_entries} entries with zero value (usually harmless, but worth noting).")
        else:
             print("   [OK] No zero-value entries found.")

        print("\n===================================================")
        if not empty_batches and not unbalanced:
            print("   ✅ LEDGER INTEGRITY CONFIRMED")
        else:
            print("   ⚠️  ISSUES FOUND - PLEASE RUN FIX SCRIPT")
        print("===================================================")

if __name__ == "__main__":
    check_ledger_integrity()
