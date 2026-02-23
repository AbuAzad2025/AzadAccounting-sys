import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _normalize_name(value: str) -> str:
    return " ".join((value or "").strip().split()).lower()


def _delete_gl_batches_for_split(session, split_id, GLEntry, GLBatch, sa_delete):
    batch_ids = [
        r[0]
        for r in session.query(GLBatch.id)
        .filter(GLBatch.source_type == "PAYMENT_SPLIT", GLBatch.source_id == split_id)
        .all()
    ]
    if batch_ids:
        session.execute(sa_delete(GLEntry).where(GLEntry.batch_id.in_(batch_ids)))
        session.execute(sa_delete(GLBatch).where(GLBatch.id.in_(batch_ids)))


def _delete_gl_batches_for_payment(session, payment_id, GLEntry, GLBatch, sa_delete):
    batch_ids = [
        r[0]
        for r in session.query(GLBatch.id)
        .filter(GLBatch.source_type == "PAYMENT", GLBatch.source_id == payment_id)
        .all()
    ]
    if batch_ids:
        session.execute(sa_delete(GLEntry).where(GLEntry.batch_id.in_(batch_ids)))
        session.execute(sa_delete(GLBatch).where(GLBatch.id.in_(batch_ids)))


def main():
    import argparse
    from app import create_app
    from extensions import db
    from sqlalchemy import delete as sa_delete
    from models import (
        Supplier,
        Payment,
        PaymentSplit,
        PaymentMethod,
        PaymentStatus,
        PaymentDirection,
        PaymentEntityType,
        GLBatch,
        GLEntry,
        run_payment_gl_sync_after_commit,
    )
    from routes.payments import _ensure_payment_number, _sync_payment_method_with_splits
    from utils import update_entity_balance

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", dest="apply", action="store_true")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true")
    args = parser.parse_args()
    apply_changes = bool(args.apply and not args.dry_run)

    app = create_app()
    with app.app_context():
        supplier_q = Supplier.query.all()
        matches = [
            s for s in supplier_q if _normalize_name(s.name) == _normalize_name("اسماعيل ابو خلف")
        ]
        if not matches:
            matches = [
                s for s in supplier_q if "اسماعيل ابو خلف" in _normalize_name(s.name)
            ]
        if not matches:
            print("المورد غير موجود")
            return
        if len(matches) > 1:
            print("يوجد أكثر من مورد مطابق:")
            for s in matches:
                print(f"- {s.id} | {s.name}")
            return
        supplier = matches[0]

        target_split_id = 193
        target_payment_id = 262
        split = db.session.get(PaymentSplit, target_split_id)
        if not split:
            print("Split غير موجود:", target_split_id)
        elif split.payment_id != target_payment_id:
            print("Split لا يطابق الدفعة المطلوبة:", split.payment_id)
        else:
            payment = db.session.get(Payment, target_payment_id)
            if not payment:
                print("الدفعة غير موجودة:", target_payment_id)
            else:
                print("سيتم حذف الدفعة:", f"SPLIT-{target_split_id}-PMT-{target_payment_id}")
                if apply_changes:
                    _delete_gl_batches_for_split(db.session, target_split_id, GLEntry, GLBatch, sa_delete)
                    db.session.delete(split)
                    db.session.flush()
                    remaining = list(payment.splits or [])
                    if remaining:
                        total = sum(float(s.amount or 0) for s in remaining)
                        payment.total_amount = total
                        _sync_payment_method_with_splits(payment)
                        db.session.add(payment)
                    else:
                        _delete_gl_batches_for_payment(db.session, payment.id, GLEntry, GLBatch, sa_delete)
                        db.session.delete(payment)
                    db.session.commit()

        new_payments = [
            {
                "date": "2026-01-11",
                "amount": 10000.0,
                "notes": "سداد نقداً للمورد",
            },
            {
                "date": "2026-01-31",
                "amount": 14000.0,
                "notes": "سداد نقداً للمورد",
            },
            {
                "date": "2026-01-31",
                "amount": 14200.0,
                "notes": "سداد نقداً للمورد - دفعة 10000 لاسماعيل وخصم 4200",
            },
        ]

        created_ids = []
        for item in new_payments:
            pay_date = datetime.strptime(item["date"], "%Y-%m-%d")
            if apply_changes:
                payment = Payment(
                    supplier_id=supplier.id,
                    entity_type=PaymentEntityType.SUPPLIER.value,
                    direction=PaymentDirection.OUT.value,
                    status=PaymentStatus.COMPLETED.value,
                    payment_date=pay_date,
                    total_amount=item["amount"],
                    currency="ILS",
                    method=PaymentMethod.CASH.value,
                    notes=item["notes"],
                    receiver_name=supplier.name,
                )
                _ensure_payment_number(payment)
                db.session.add(payment)
                db.session.flush()
                split = PaymentSplit(
                    payment_id=payment.id,
                    amount=payment.total_amount,
                    currency=payment.currency,
                    method=payment.method,
                    details={},
                )
                db.session.add(split)
                db.session.commit()
                created_ids.append((payment.id, split.id))
            else:
                print("سيتم إنشاء دفعة:", item["date"], item["amount"], item["notes"])

        if apply_changes:
            for pid, _ in created_ids:
                run_payment_gl_sync_after_commit(pid)
            update_entity_balance("SUPPLIER", supplier.id)
            print("تم التنفيذ بنجاح")
            for pid, sid in created_ids:
                print(f"تم إنشاء SPLIT-{sid}-PMT-{pid}")


if __name__ == "__main__":
    main()
