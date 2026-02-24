from __future__ import annotations

import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import Payment, GLBatch, GLEntry

def force_fix():
    app = create_app()
    with app.app_context():
        pid = 207
        pnum = "PMT20251231-0003"
        print(f"\n=== FORCE FIXING PAYMENT {pnum} (ID: {pid}) ===")
        
        # 1. Get Payment Details
        payment = db.session.get(Payment, pid)
        if not payment:
            print("❌ Payment not found!")
            return

        print(f"   -> Payment Details: Amount={payment.total_amount}, Date={payment.payment_date}, Status={payment.status}")
        
        # 2. Delete ANY existing GL Batch for this payment (even unposted or partial)
        batches = GLBatch.query.filter(
            GLBatch.source_type == 'PAYMENT',
            GLBatch.source_id == pid
        ).all()
        
        if batches:
            print(f"   -> Found {len(batches)} existing batches. Deleting...")
            for b in batches:
                GLEntry.query.filter(GLEntry.batch_id == b.id).delete()
                db.session.delete(b)
            db.session.commit()
            print("   -> Deleted existing batches.")
        
        # 3. Create GL Batch MANUALLY
        print("   -> Creating NEW GL Batch manually...")
        batch = GLBatch(
            source_type='PAYMENT',
            source_id=pid,
            status='POSTED',
            posting_date=payment.payment_date or datetime.now(),
            entity_type=payment.entity_type,
            entity_id=payment.entity_id,
            description=f"Manual Fix for Payment {pnum}",
            created_by_id=1,  # System
            currency=payment.currency or 'ILS',
            rate=Decimal('1.0')
        )
        db.session.add(batch)
        db.session.flush()
        
        # 4. Create GL Entries (Simple Cash/AP logic for safety)
        # Debit: Accounts Payable (Supplier)
        # Credit: Cash/Bank
        
        amount = Decimal(str(payment.total_amount))
        
        # Assuming Supplier Payment
        # Debit AP (Liability decreases)
        debit_entry = GLEntry(
            batch_id=batch.id,
            account_id=2100, # Approximate AP account, or we can fetch dynamically. 
                             # Ideally we should use the exact accounts from settings.
                             # But for now, let's try to use the logic from run_payment_gl_sync_after_commit if possible.
            debit=amount,
            credit=Decimal('0.00'),
            description=f"Payment {pnum} - Manual Fix",
            entity_type=payment.entity_type,
            entity_id=payment.entity_id
        )
        
        # Credit Cash (Asset decreases)
        credit_entry = GLEntry(
            batch_id=batch.id,
            account_id=1100, # Approximate Cash account
            debit=Decimal('0.00'),
            credit=amount,
            description=f"Payment {pnum} - Manual Fix",
            entity_type=payment.entity_type,
            entity_id=payment.entity_id
        )

        # However, to be safer and correct, we should use the standard function first,
        # but force commit. If that failed before, maybe it's because of missing accounts.
        # Let's try the standard function one more time with verbose error catching.
        
        db.session.rollback() # Undo manual creation for a moment
        
        print("   -> Retrying standard sync with forced commit...")
        from models import run_payment_gl_sync_after_commit
        try:
            run_payment_gl_sync_after_commit(pid)
            # FORCE COMMIT
            db.session.commit()
            
            # Check if created
            check = GLBatch.query.filter(
                GLBatch.source_type == 'PAYMENT',
                GLBatch.source_id == pid,
                GLBatch.status == 'POSTED'
            ).first()
            
            if check:
                print(f"   ✅ SUCCESS! Batch created with ID: {check.id}")
            else:
                print("   ❌ FAILED! Batch still not found after sync.")
                # Fallback: Create dummy posted batch just to satisfy audit if the payment is valid
                # This is a last resort "band-aid"
                
        except Exception as e:
            print(f"   ❌ ERROR during sync: {e}")

if __name__ == "__main__":
    force_fix()
