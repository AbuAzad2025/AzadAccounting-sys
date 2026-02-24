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
from utils.supplier_balance_updater import update_supplier_balance_components as update_supplier_balance

def run():
    app = create_app()
    with app.app_context():
        # Payments to be deleted (using exact IDs found in debug)
        # ID 305 -> PMT20260223-0005 (Split 229)
        # ID 307 -> PMT20260223-0007 (Split 231)
        target_payment_ids = [305, 307]
        
        print(f"--- STARTING DELETION FOR PAYMENT IDs: {target_payment_ids} ---")
        
        deleted_count = 0
        supplier_ids_to_update = set()

        for pid in target_payment_ids:
            # Find payment by ID
            payment = db.session.get(Payment, pid)
            
            if not payment:
                print(f"❌ Payment ID {pid} NOT FOUND. Skipping.")
                continue

            print(f"✅ Found Payment: {payment.payment_number} (ID: {payment.id}, Amount: {payment.total_amount}, Date: {payment.payment_date})")
            
            # Track supplier for balance update
            if payment.entity_type == "SUPPLIER" and payment.supplier_id:
                supplier_ids_to_update.add(payment.supplier_id)

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
            print(f"🗑️  Deleted Payment {payment.payment_number} (ID: {pid})")

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
