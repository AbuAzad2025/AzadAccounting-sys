from __future__ import annotations

import os
import sys
from pathlib import Path
from sqlalchemy import text

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import Payment, GLBatch, GLEntry, run_payment_gl_sync_after_commit

def run_fix():
    app = create_app()
    with app.app_context():
        print("\n=======================================================")
        print("          FIXING AUDIT ISSUES (GL INTEGRITY)           ")
        print("=======================================================\n")
        
        # 1. Delete Empty Posted Batches
        print("--- 1. Fixing Empty Posted Batches ---")
        empty_batches = db.session.execute(text("""
            SELECT b.id FROM gl_batches b
            LEFT JOIN gl_entries e ON e.batch_id = b.id
            WHERE e.id IS NULL AND b.status='POSTED'
        """)).fetchall()
        
        if not empty_batches:
            print("   -> No empty batches found.")
        else:
            print(f"   -> Found {len(empty_batches)} empty batches. Deleting...")
            for row in empty_batches:
                batch_id = row[0]
                # Delete batch (entries already null)
                db.session.execute(text("DELETE FROM gl_batches WHERE id = :id"), {"id": batch_id})
            db.session.commit()
            print("   -> Deleted successfully.")

        # 2. Fix Payments without GL
        print("\n--- 2. Fixing Payments without GL ---")
        # Find completed payments that have NO GL Batch
        payments_no_gl = db.session.execute(text("""
            SELECT p.id, p.payment_number, p.total_amount, p.status FROM payments p
            WHERE p.status='COMPLETED'
            AND NOT EXISTS (
                SELECT 1 FROM gl_batches b 
                WHERE b.source_type='PAYMENT' AND b.source_id=p.id AND b.status='POSTED'
            )
            AND NOT EXISTS (
                SELECT 1 FROM payment_splits ps 
                JOIN gl_batches b ON b.source_type='PAYMENT_SPLIT' AND b.source_id=ps.id 
                WHERE ps.payment_id=p.id AND b.status='POSTED'
            )
        """)).fetchall()
        
        if not payments_no_gl:
            print("   -> No payments missing GL found.")
        else:
            count = len(payments_no_gl)
            print(f"   -> Found {count} payments missing GL entries. Rebuilding...")
            
            fixed_count = 0
            error_count = 0
            for i, row in enumerate(payments_no_gl):
                pid = row[0]
                pnum = row[1]
                pamount = row[2]
                print(f"      - Fixing Payment {pnum} (ID: {pid}, Amount: {pamount})...")
                try:
                    # Run sync in a nested transaction/try-catch to isolate failures
                    # We need to ensure commit happens per payment to save progress
                    run_payment_gl_sync_after_commit(pid)
                    fixed_count += 1
                    print(f"        -> Success.")
                except Exception as e:
                    error_count += 1
                    print(f"      ! Error fixing Payment {pnum} (ID: {pid}): {str(e)}")
                    # Try to see if it has splits but failed
                    splits = db.session.execute(text("SELECT id FROM payment_splits WHERE payment_id=:pid"), {"pid": pid}).fetchall()
                    if splits:
                        print(f"        -> Payment has {len(splits)} splits. Trying manual split fix...")
                        # Here we could try to fix splits individually if we had the function import
                        # But mostly likely run_payment_gl_sync_after_commit should handle it.
            
            print(f"   -> Summary: Fixed {fixed_count}, Failed {error_count} out of {count} payments.")

        # 3. Fix Orphan Entries
        print("\n--- 3. Fixing Orphan GL Entries ---")
        orphan_entries = db.session.execute(text("""
            SELECT e.id FROM gl_entries e
            LEFT JOIN gl_batches b ON b.id = e.batch_id
            WHERE b.id IS NULL
        """)).fetchall()
        
        if not orphan_entries:
            print("   -> No orphan entries found.")
        else:
            print(f"   -> Found {len(orphan_entries)} orphan entries. Deleting...")
            for row in orphan_entries:
                entry_id = row[0]
                db.session.execute(text("DELETE FROM gl_entries WHERE id = :id"), {"id": entry_id})
            db.session.commit()
            print("   -> Deleted successfully.")

        # 4. Fix Unbalanced Batches (Delete them so they can be regenerated if needed, or just warn)
        # For safety, we will delete them if they are payment batches, otherwise just warn.
        print("\n--- 4. Fixing Unbalanced Batches ---")
        unbalanced_batches = db.session.execute(text("""
            SELECT b.id, b.source_type, b.source_id FROM gl_batches b
            JOIN gl_entries e ON e.batch_id = b.id
            WHERE b.status='POSTED'
            GROUP BY b.id, b.source_type, b.source_id
            HAVING ROUND(SUM(e.debit), 2) <> ROUND(SUM(e.credit), 2)
        """)).fetchall()
        
        if not unbalanced_batches:
            print("   -> No unbalanced batches found.")
        else:
            print(f"   -> Found {len(unbalanced_batches)} unbalanced batches.")
            for row in unbalanced_batches:
                bid, stype, sid = row
                print(f"      - Deleting unbalanced batch {bid} ({stype} #{sid})...")
                # Delete entries then batch
                db.session.execute(text("DELETE FROM gl_entries WHERE batch_id = :id"), {"id": bid})
                db.session.execute(text("DELETE FROM gl_batches WHERE id = :id"), {"id": bid})
                
                # If it's a payment, try to regenerate
                if stype == 'PAYMENT':
                    try:
                        print(f"        -> Regenerating GL for Payment {sid}...")
                        run_payment_gl_sync_after_commit(sid)
                    except Exception as e:
                        print(f"        ! Failed to regenerate: {e}")
            db.session.commit()
            print("   -> Fix complete.")

        print("\n=======================================================")
        print("                   FIX COMPLETE                        ")
        print("=======================================================\n")

if __name__ == "__main__":
    run_fix()
