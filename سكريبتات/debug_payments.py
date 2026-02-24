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
from models import Payment, PaymentSplit, Supplier

def run():
    app = create_app()
    with app.app_context():
        print("\n=== DEBUGGING PAYMENTS ===")
        
        # 1. Check all payments on that date
        date_str = "2026-02-23"
        print(f"\n1. Searching Payments on {date_str}...")
        try:
            payments = db.session.execute(
                text("SELECT id, payment_number, total_amount, entity_type, supplier_id, status FROM payments WHERE date(payment_date) = :d"),
                {"d": date_str}
            ).fetchall()
            
            if not payments:
                print("   -> No payments found on this date.")
            else:
                for p in payments:
                    print(f"   -> Found: ID={p.id}, Num='{p.payment_number}', Amount={p.total_amount}, SupplierID={p.supplier_id}, Status={p.status}")
        except Exception as e:
            print(f"   -> Error searching by date: {e}")

        # 2. Check by amount
        amounts = [10000, 18000, 8000]
        print(f"\n2. Searching Payments by Amounts {amounts}...")
        for amt in amounts:
            try:
                payments_amt = db.session.execute(
                    text("SELECT id, payment_number, total_amount, payment_date FROM payments WHERE total_amount = :a"),
                    {"a": amt}
                ).fetchall()
                if payments_amt:
                    for p in payments_amt:
                        print(f"   -> Found Amount {amt}: ID={p.id}, Num='{p.payment_number}', Date={p.payment_date}")
                else:
                    print(f"   -> No payments found with amount {amt}")
            except Exception as e:
                print(f"   -> Error searching by amount {amt}: {e}")

        # 3. Check Payment Splits directly
        print(f"\n3. Searching Payment Splits directly...")
        splits = db.session.execute(
            text("SELECT id, payment_id, amount FROM payment_splits WHERE amount IN (10000, 18000, 8000)")
        ).fetchall()
        if splits:
            for s in splits:
                parent = db.session.get(Payment, s.payment_id)
                p_num = parent.payment_number if parent else "ORPHAN"
                print(f"   -> Found Split: ID={s.id}, Amount={s.amount}, ParentPayment={p_num}")
        else:
             print("   -> No matching splits found.")
             
        # 4. Check Supplier Ismail Abu Khalaf
        print(f"\n4. Searching Supplier 'Ismail'...")
        suppliers = Supplier.query.filter(Supplier.name.ilike("%Ismail%") | Supplier.name.ilike("%اسماعيل%")).all()
        for s in suppliers:
            print(f"   -> Found Supplier: ID={s.id}, Name='{s.name}'")
            # List last 5 payments for this supplier
            last_payments = Payment.query.filter(
                Payment.entity_type == 'SUPPLIER', 
                Payment.supplier_id == s.id
            ).order_by(Payment.id.desc()).limit(5).all()
            print("      Last 5 payments:")
            for lp in last_payments:
                print(f"      - {lp.payment_number} | {lp.total_amount} | {lp.payment_date}")

        print("\n=== END DEBUG ===")

if __name__ == "__main__":
    run()
