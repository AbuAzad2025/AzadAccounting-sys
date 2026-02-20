import os
import sys
from pathlib import Path
from decimal import Decimal as D

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def run(dry_run=True, suppliers_only=False):
    from app import create_app
    from extensions import db
    from models import Expense, Payment, PaymentStatus, PaymentDirection, PaymentEntityType
    from routes.payments import _ensure_payment_number
    from datetime import datetime, timezone
    from sqlalchemy import or_, and_

    app = create_app()
    with app.app_context():
        q = db.session.query(Expense).filter(Expense.amount > 0)
        if suppliers_only:
            q = q.filter(
                or_(
                    Expense.supplier_id.isnot(None),
                    and_(Expense.payee_type == "SUPPLIER", Expense.payee_entity_id.isnot(None)),
                )
            )
        q = q.order_by(Expense.id)
        added = 0
        for exp in q.yield_per(200):
            total_paid = float(exp.total_paid or 0)
            amount = float(exp.amount or 0)
            if amount <= 0:
                continue
            remaining = amount - total_paid
            if remaining <= 0.005:
                continue
            pay_date = exp.date
            if hasattr(pay_date, "date"):
                pay_date = pay_date.date() if pay_date else datetime.now(timezone.utc).replace(tzinfo=None)
            elif not pay_date:
                pay_date = datetime.now(timezone.utc).replace(tzinfo=None)
            base_currency = (exp.currency or "ILS").strip().upper()
            expense_ref = f"مصروف #{exp.id}"
            if exp.description:
                expense_ref += f" - {exp.description}"
            elif exp.type and exp.type.name:
                expense_ref += f" - {exp.type.name}"
            supplier_id = exp.supplier_id or (exp.payee_entity_id if exp.payee_type == "SUPPLIER" else None)
            if dry_run:
                added += 1
                continue
            payment = Payment(
                payment_date=pay_date,
                total_amount=D(str(remaining)),
                currency=base_currency,
                method=(exp.payment_method or "cash").strip().lower(),
                status=PaymentStatus.COMPLETED.value,
                direction=PaymentDirection.OUT.value,
                entity_type=PaymentEntityType.EXPENSE.value,
                expense_id=exp.id,
                supplier_id=supplier_id,
                reference=expense_ref,
                notes=exp.description or None,
                receiver_name=exp.payee_name or exp.paid_to or exp.beneficiary_name,
                created_by=None,
            )
            _ensure_payment_number(payment)
            db.session.add(payment)
            added += 1
        if dry_run:
            print("DRY-RUN payments to add:", added)
        elif added > 0:
            db.session.commit()
            print("OK payments added:", added)
        else:
            print("OK no expenses needed payment.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", dest="dry_run", action="store_true")
    parser.add_argument("--apply", dest="apply", action="store_true")
    parser.add_argument("--suppliers-only", dest="suppliers_only", action="store_true")
    args = parser.parse_args()
    run(dry_run=not args.apply, suppliers_only=args.suppliers_only)
