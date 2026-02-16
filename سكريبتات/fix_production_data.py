
import sys
from app import create_app
from extensions import db
from models import Payment, PaymentSplit, GLBatch, PaymentStatus, _payment_split_gl_batch_upsert
from sqlalchemy import func
from flask import has_app_context, current_app

def fix_production_data(app=None, dry_run: bool = False):
    def _run():
        print("=== Starting Data Repair for Production ===")
        
        # --- Phase 1: Create Missing Splits ---
        print("--- Phase 1: Checking for Payments without Splits ---")
        excluded_statuses = {
            PaymentStatus.CANCELLED.value,
            PaymentStatus.FAILED.value,
        }
        payments_no_splits = (
            db.session.query(Payment)
            .outerjoin(PaymentSplit)
            .filter(PaymentSplit.id == None)
            .filter(Payment.status.notin_(excluded_statuses))
            .all()
        )
        
        if not payments_no_splits:
            print("✅ All payments have splits. No action needed.")
        else:
            print(f"⚠️ Found {len(payments_no_splits)} payments without splits. Creating them now...")
            count = 0
            for payment in payments_no_splits:
                if dry_run:
                    count += 1
                    continue
                try:
                    split = PaymentSplit(
                        payment_id=payment.id,
                        amount=payment.total_amount,
                        currency=payment.currency,
                        method=payment.method,
                        details={"auto_created": True, "reason": "migration_fix_v1"}
                    )
                    db.session.add(split)
                    db.session.commit()
                    count += 1
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ Error creating split for Payment {payment.id}: {e}")
            
            if dry_run:
                db.session.rollback()
                print(f"✅ Dry-Run: Would create {count} missing splits.")
            else:
                print(f"✅ Successfully created {count} missing splits.")

        # --- Phase 2: Ensure GL Batches for All Splits ---
        print("--- Phase 2: Ensuring GL Batches for all Splits ---")
        
        # Strategy: For missing GLBatch, run the upsert in an isolated transaction per split
        
        splits = (
            db.session.query(PaymentSplit)
            .join(Payment, PaymentSplit.payment_id == Payment.id)
            .filter(Payment.status.notin_(excluded_statuses))
            .all()
        )
        fixed_gl_count = 0
        
        for split in splits:
            exists = db.session.query(GLBatch).filter(
                GLBatch.source_type == 'PAYMENT_SPLIT',
                GLBatch.source_id == split.id
            ).first()

            if not exists:
                print(f"⚠️ Split {split.id} (Payment {split.payment_id}) missing GL Batch. Triggering update...")
                if dry_run:
                    fixed_gl_count += 1
                    continue
                try:
                    with db.engine.begin() as conn:
                        _payment_split_gl_batch_upsert(None, conn, split)
                    fixed_gl_count += 1
                except Exception as e:
                    print(f"❌ Error updating split {split.id}: {e}")
        
        if fixed_gl_count > 0:
            try:
                if dry_run:
                    print(f"✅ Dry-Run: Would trigger GL creation for {fixed_gl_count} splits.")
                else:
                    print(f"✅ Triggered GL creation for {fixed_gl_count} splits.")
            except Exception as e:
                print(f"❌ Failed to commit updates: {e}")
        else:
            print("✅ All splits already have GL Batches.")

        print("=== Data Repair Completed Successfully ===")

    if has_app_context():
        return _run()

    app = app or create_app()
    with app.app_context():
        return _run()

if __name__ == "__main__":
    fix_production_data()
