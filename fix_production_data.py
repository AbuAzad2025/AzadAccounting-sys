
import sys
from app import create_app
from extensions import db
from models import Payment, PaymentSplit, GLBatch
from sqlalchemy import func

def fix_production_data():
    app = create_app()
    with app.app_context():
        print("=== Starting Data Repair for Production ===")
        
        # --- Phase 1: Create Missing Splits ---
        print("--- Phase 1: Checking for Payments without Splits ---")
        payments_no_splits = db.session.query(Payment).outerjoin(PaymentSplit).filter(PaymentSplit.id == None).all()
        
        if not payments_no_splits:
            print("✅ All payments have splits. No action needed.")
        else:
            print(f"⚠️ Found {len(payments_no_splits)} payments without splits. Creating them now...")
            count = 0
            for payment in payments_no_splits:
                try:
                    # Create a default split
                    split = PaymentSplit(
                        payment_id=payment.id,
                        amount=payment.total_amount,
                        currency=payment.currency,
                        method=payment.method,
                        details={"auto_created": True, "reason": "migration_fix_v1"},
                        converted_amount=payment.total_amount, # Assuming base currency for now
                        converted_currency=payment.currency
                    )
                    db.session.add(split)
                    count += 1
                except Exception as e:
                    print(f"❌ Error creating split for Payment {payment.id}: {e}")
            
            try:
                db.session.commit()
                print(f"✅ Successfully created {count} missing splits.")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to commit new splits: {e}")
                return

        # --- Phase 2: Ensure GL Batches for All Splits ---
        print("--- Phase 2: Ensuring GL Batches for all Splits ---")
        
        # Strategy: Find splits that don't have a corresponding GLBatch
        # We can trigger the event listener by "touching" the split (updating it)
        
        splits = db.session.query(PaymentSplit).all()
        fixed_gl_count = 0
        
        for split in splits:
            # Check if GL Batch exists
            exists = db.session.query(GLBatch).filter(
                GLBatch.source_type == 'PAYMENT_SPLIT',
                GLBatch.source_id == split.id
            ).first()
            
            if not exists:
                print(f"⚠️ Split {split.id} (Payment {split.payment_id}) missing GL Batch. Triggering update...")
                # Force update by modifying details
                d = dict(split.details or {})
                d['force_gl_update'] = True
                split.details = d
                
                db.session.add(split)
                fixed_gl_count += 1
        
        if fixed_gl_count > 0:
            try:
                db.session.commit()
                print(f"✅ Triggered GL creation for {fixed_gl_count} splits.")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to commit updates: {e}")
        else:
            print("✅ All splits already have GL Batches.")

        # --- Phase 3: Cleanup Old 'PAYMENT' Batches ---
        print("--- Phase 3: Cleaning up old 'PAYMENT' GL Batches ---")
        old_batches = db.session.query(GLBatch).filter(GLBatch.source_type == 'PAYMENT').all()
        
        if old_batches:
            print(f"⚠️ Found {len(old_batches)} old 'PAYMENT' batches. Deleting...")
            try:
                # Delete in bulk
                db.session.query(GLBatch).filter(GLBatch.source_type == 'PAYMENT').delete(synchronize_session=False)
                db.session.commit()
                print("✅ Deleted old 'PAYMENT' batches.")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to delete old batches: {e}")
        else:
            print("✅ No old 'PAYMENT' batches found.")

        print("=== Data Repair Completed Successfully ===")

if __name__ == "__main__":
    fix_production_data()
