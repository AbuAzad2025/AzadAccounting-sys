from __future__ import annotations

import os
import sys
from pathlib import Path

# Setup paths to ensure we can import from the main application
ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import Payment, PaymentSplit, GLBatch, GLEntry
from utils.supplier_balance_updater import update_supplier_balance

def run():
    app = create_app()
    with app.app_context():
        # Payments to be deleted based on user request
        # 2026-02-23 دفعة للمورد SPLIT-229-PMT-305
        # 2026-02-23 دفعة للمورد SPLIT-231-PMT-307
        target_payment_numbers = ["SPLIT-229-PMT-305", "SPLIT-231-PMT-307"]
        
        print(f"--- STARTING DELETION FOR: {target_payment_numbers} ---")
        
        deleted_count = 0
        supplier_ids_to_update = set()

        for p_num in target_payment_numbers:
            # Try to find payment by exact number or partial match if needed
            payment = Payment.query.filter(Payment.payment_number == p_num).first()
            
            # If not found exact, try flexible search (though these look exact)
            if not payment:
                 # Extract PMT-XXX part if needed, but let's try strict first
                 pass

            if not payment:
                print(f"❌ Payment {p_num} NOT FOUND. Skipping.")
                continue

            print(f"✅ Found Payment: {payment.payment_number} (ID: {payment.id}, Amount: {payment.amount})")
            
            # Track supplier for balance update
            if payment.payee_type == "SUPPLIER" and payment.payee_entity_id:
                supplier_ids_to_update.add(payment.payee_entity_id)

            # 1. Delete associated GL Batches & Entries for the Payment itself
            gl_batches = GLBatch.query.filter(
                GLBatch.source_type == "PAYMENT", 
                GLBatch.source_id == payment.id
            ).all()
            
            for batch in gl_batches:
                GLEntry.query.filter(GLEntry.batch_id == batch.id).delete()
                db.session.delete(batch)
            
            # 2. Delete Payment Splits and their GL Batches
            splits = PaymentSplit.query.filter(PaymentSplit.payment_id == payment.id).all()
            for split in splits:
                split_batches = GLBatch.query.filter(
                    GLBatch.source_type == "PAYMENT_SPLIT", 
                    GLBatch.source_id == split.id
                ).all()
                for batch in split_batches:
                    GLEntry.query.filter(GLEntry.batch_id == batch.id).delete()
                    db.session.delete(batch)
                
                db.session.delete(split)

            # 3. Delete the Payment record
            db.session.delete(payment)
            deleted_count += 1
            print(f"🗑️  Deleted Payment {payment.payment_number}")

        # Commit changes
        if deleted_count > 0:
            db.session.commit()
            print(f"--- DELETED {deleted_count} PAYMENTS SUCCESSFULLY ---")
            
            # Update Supplier Balances
            print("--- UPDATING SUPPLIER BALANCES ---")
            for supp_id in supplier_ids_to_update:
                print(f"🔄 Updating balance for Supplier ID: {supp_id}...")
                update_supplier_balance(supp_id)
            
            # Commit balance updates
            db.session.commit()
            print("--- DONE ---")
        else:
            print("--- NO PAYMENTS WERE DELETED ---")

if __name__ == "__main__":
    run()
