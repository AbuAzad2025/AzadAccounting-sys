import os
import sys
from pathlib import Path
from decimal import Decimal as D

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _parse_names(raw):
    parts = [p.strip() for p in (raw or "").split(",")]
    return [p for p in parts if p]


def _to_ils(amount, currency, at_date, convert_amount):
    value = D(str(amount or 0))
    code = (currency or "ILS").strip().upper()
    if code == "ILS":
        return value
    try:
        return D(str(convert_amount(value, code, "ILS", at_date)))
    except Exception:
        return value


def run(
    dry_run=True,
    suppliers_only=False,
    expense_type_names=None,
    force_cash=False,
    audit=False,
    only_negative=False,
    list_expense_types=False,
):
    from app import create_app
    from extensions import db
    from models import Expense, ExpenseType, Payment, PaymentStatus, PaymentDirection, PaymentEntityType, Supplier
    from routes.payments import _ensure_payment_number
    from datetime import datetime, timezone
    from sqlalchemy import or_, and_
    from utils.supplier_balance_updater import calculate_supplier_balance_components, convert_amount

    app = create_app()
    with app.app_context():
        if list_expense_types:
            types = db.session.query(ExpenseType).order_by(ExpenseType.id).all()
            for t in types:
                print(f"{t.id} | {t.name} | {t.code or ''}")
            return
        q = db.session.query(Expense).filter(Expense.amount > 0)
        type_ids = None
        if expense_type_names:
            types = db.session.query(ExpenseType).filter(ExpenseType.name.in_(expense_type_names)).all()
            if not types:
                name_filters = [ExpenseType.name.ilike(f"%{name}%") for name in expense_type_names]
                types = db.session.query(ExpenseType).filter(or_(*name_filters)).all()
            type_ids = [t.id for t in types]
            q = q.join(ExpenseType, Expense.type_id == ExpenseType.id).filter(ExpenseType.id.in_(type_ids))
        if suppliers_only:
            q = q.filter(
                or_(
                    Expense.supplier_id.isnot(None),
                    and_(Expense.payee_type == "SUPPLIER", Expense.payee_entity_id.isnot(None)),
                )
            )
        q = q.order_by(Expense.id)
        added = 0
        supplier_cache = {}
        supplier_stats = {}
        missing_type_names = None
        if expense_type_names and type_ids is not None:
            found_names = {t.name for t in types}
            missing_type_names = [n for n in expense_type_names if n not in found_names]
        for exp in q.yield_per(200):
            total_paid = float(exp.total_paid or 0)
            amount = float(exp.amount or 0)
            if amount <= 0:
                continue
            remaining = amount - total_paid
            supplier_id = exp.supplier_id or (exp.payee_entity_id if exp.payee_type == "SUPPLIER" else None)
            if supplier_id:
                stat = supplier_stats.get(supplier_id)
                if not stat:
                    stat = {
                        "expense_total": D("0.00"),
                        "paid_total": D("0.00"),
                        "remaining_total": D("0.00"),
                        "count": 0,
                    }
                    supplier_stats[supplier_id] = stat
                amount_ils = _to_ils(exp.amount, exp.currency, exp.date, convert_amount)
                paid_ils = _to_ils(exp.total_paid, exp.currency, exp.date, convert_amount)
                remaining_ils = amount_ils - paid_ils
                if remaining_ils < D("0.00"):
                    remaining_ils = D("0.00")
                stat["expense_total"] += amount_ils
                stat["paid_total"] += paid_ils
                stat["remaining_total"] += remaining_ils
                stat["count"] += 1
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
            supplier_balance = None
            if supplier_id and (only_negative or audit):
                supplier = supplier_cache.get(supplier_id)
                if not supplier:
                    supplier = db.session.get(Supplier, supplier_id)
                    supplier_cache[supplier_id] = supplier
                if supplier:
                    supplier_balance = float(supplier.current_balance or 0)
            if only_negative and (supplier_balance is None or supplier_balance >= 0):
                continue
            if dry_run:
                added += 1
                continue
            method_val = (exp.payment_method or "cash").strip().lower()
            if force_cash:
                method_val = "cash"
            payment = Payment(
                payment_date=pay_date,
                total_amount=D(str(remaining)),
                currency=base_currency,
                method=method_val,
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
        if audit:
            if missing_type_names:
                print("أنواع المصروف غير موجودة:", ", ".join(missing_type_names))
            if not supplier_stats:
                print("لا يوجد مصاريف مطابقة للأنواع المحددة.")
            for supplier_id, stat in supplier_stats.items():
                supplier = supplier_cache.get(supplier_id) or db.session.get(Supplier, supplier_id)
                if not supplier:
                    continue
                balance = float(supplier.current_balance or 0)
                components = calculate_supplier_balance_components(supplier_id, db.session) or {}
                exp_total = float(stat["expense_total"])
                paid_total = float(stat["paid_total"])
                remaining_total = float(stat["remaining_total"])
                print("----")
                print("المورد:", supplier.name, "#", supplier_id)
                print("الرصيد الحالي:", balance)
                print("إجمالي المصاريف (ILS):", exp_total)
                print("إجمالي المدفوع (ILS):", paid_total)
                print("المتبقي (ILS):", remaining_total)
                print("expenses_normal:", float(components.get("expenses_normal", 0) or 0))
                print("expenses_service_supply:", float(components.get("expenses_service_supply", 0) or 0))
                print("payments_out_balance:", float(components.get("payments_out_balance", 0) or 0))
                print("payments_in_balance:", float(components.get("payments_in_balance", 0) or 0))
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
    parser.add_argument("--expense-type-names", dest="expense_type_names", type=str, default=None)
    parser.add_argument("--force-cash", dest="force_cash", action="store_true")
    parser.add_argument("--audit", dest="audit", action="store_true")
    parser.add_argument("--only-negative", dest="only_negative", action="store_true")
    parser.add_argument("--list-expense-types", dest="list_expense_types", action="store_true")
    args = parser.parse_args()
    names = _parse_names(args.expense_type_names)
    run(
        dry_run=not args.apply,
        suppliers_only=args.suppliers_only,
        expense_type_names=names,
        force_cash=args.force_cash,
        audit=args.audit,
        only_negative=args.only_negative,
        list_expense_types=args.list_expense_types,
    )
