import os
import re
import sys
from decimal import Decimal as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import Check, Expense, GLBatch, GLEntry, Payment, PaymentSplit
from routes.payments import _sync_payment_method_with_splits
from sqlalchemy import delete as sa_delete, or_


def _as_bool(v):
    return str(v or "").strip().lower() in ("1", "true", "yes", "y", "on")


def _collect_orphan_batches(source_type, model):
    q = (
        db.session.query(GLBatch.id, GLBatch.source_id, GLBatch.source_type, GLBatch.purpose, GLBatch.memo)
        .filter(GLBatch.source_type == source_type)
        .filter(~db.session.query(model.id).filter(model.id == GLBatch.source_id).exists())
        .order_by(GLBatch.id.asc())
    )
    return [dict(r._mapping) for r in q.all()]


def _collect_orphan_splits():
    q = (
        db.session.query(PaymentSplit.id, PaymentSplit.payment_id, PaymentSplit.amount, PaymentSplit.currency)
        .filter(~db.session.query(Payment.id).filter(Payment.id == PaymentSplit.payment_id).exists())
        .order_by(PaymentSplit.id.asc())
    )
    return [dict(r._mapping) for r in q.all()]


def _chunked(items, size=500):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _parse_split_refs(raw_refs: str):
    items = re.split(r"[,\s]+", str(raw_refs or "").strip())
    out = []
    for it in items:
        if not it:
            continue
        m = re.search(r"SPLIT-(\d+)-PMT-(\d+)", it.upper())
        if not m:
            continue
        out.append(
            {
                "ref": f"SPLIT-{int(m.group(1))}-PMT-{int(m.group(2))}",
                "split_id": int(m.group(1)),
                "payment_id": int(m.group(2)),
            }
        )
    return out


def _collect_split_batches(split_ids):
    if not split_ids:
        return []
    q = (
        db.session.query(GLBatch.id, GLBatch.source_id, GLBatch.purpose)
        .filter(GLBatch.source_type == "PAYMENT_SPLIT")
        .filter(GLBatch.source_id.in_(split_ids))
        .order_by(GLBatch.id.asc())
    )
    return [dict(r._mapping) for r in q.all()]


def _collect_split_checks(split_ids):
    if not split_ids:
        return []
    checks = (
        db.session.query(Check)
        .filter(
            or_(
                Check.reference_number.in_([f"PMT-SPLIT-{sid}" for sid in split_ids]),
                *[Check.reference_number.like(f"PMT-SPLIT-{sid}-%") for sid in split_ids],
            )
        )
        .all()
    )
    return checks


def _delete_split_gl_batches(split_ids):
    if not split_ids:
        return {"deleted_batches": 0, "deleted_entries": 0}
    batch_ids = [b["id"] for b in _collect_split_batches(split_ids)]
    deleted_entries = 0
    deleted_batches = 0
    for chunk in _chunked(batch_ids):
        if chunk:
            res_e = db.session.execute(sa_delete(GLEntry).where(GLEntry.batch_id.in_(chunk)))
            res_b = db.session.execute(sa_delete(GLBatch).where(GLBatch.id.in_(chunk)))
            deleted_entries += int(res_e.rowcount or 0)
            deleted_batches += int(res_b.rowcount or 0)
    return {"deleted_batches": deleted_batches, "deleted_entries": deleted_entries}


def _delete_payment_gl_batches(payment_ids):
    if not payment_ids:
        return {"deleted_batches": 0, "deleted_entries": 0}
    batch_ids = [
        r[0]
        for r in db.session.query(GLBatch.id)
        .filter(GLBatch.source_type.in_(["PAYMENT", "PAYMENT_REVERSAL"]))
        .filter(GLBatch.source_id.in_(payment_ids))
        .all()
    ]
    deleted_entries = 0
    deleted_batches = 0
    for chunk in _chunked(batch_ids):
        if chunk:
            res_e = db.session.execute(sa_delete(GLEntry).where(GLEntry.batch_id.in_(chunk)))
            res_b = db.session.execute(sa_delete(GLBatch).where(GLBatch.id.in_(chunk)))
            deleted_entries += int(res_e.rowcount or 0)
            deleted_batches += int(res_b.rowcount or 0)
    return {"deleted_batches": deleted_batches, "deleted_entries": deleted_entries}


def cleanup_specific_splits(*, raw_refs: str, dry_run: bool = True):
    app = create_app()
    with app.app_context():
        items = _parse_split_refs(raw_refs)
        split_ids = [i["split_id"] for i in items]
        result = {
            "dry_run": dry_run,
            "requested": items,
            "found_splits": [],
            "missing_splits": [],
            "gl_batches": [],
            "checks": [],
            "deleted": {"splits": 0, "payments": 0, "gl_batches": 0, "gl_entries": 0, "checks": 0},
        }

        if not items:
            return result

        splits = (
            db.session.query(PaymentSplit)
            .filter(PaymentSplit.id.in_(split_ids))
            .all()
        )
        split_map = {int(s.id): s for s in splits}
        for item in items:
            if item["split_id"] not in split_map:
                result["missing_splits"].append(item)
            else:
                result["found_splits"].append(item)

        result["gl_batches"] = _collect_split_batches(split_ids)
        checks = _collect_split_checks(split_ids)
        result["checks"] = [{"id": int(c.id), "reference_number": c.reference_number} for c in checks]

        if dry_run:
            return result

        delete_summary = _delete_split_gl_batches(split_ids)
        result["deleted"]["gl_batches"] += int(delete_summary["deleted_batches"] or 0)
        result["deleted"]["gl_entries"] += int(delete_summary["deleted_entries"] or 0)

        for chk in checks:
            try:
                chk._skip_gl_reversal = True
            except Exception:
                pass
            db.session.delete(chk)
        result["deleted"]["checks"] = len(checks)

        payments_to_delete = set()
        payments_to_update = set()

        for item in result["found_splits"]:
            split = split_map.get(item["split_id"])
            if not split:
                continue
            payment = split.payment
            db.session.delete(split)
            result["deleted"]["splits"] += 1

            if payment:
                payments_to_update.add(payment.id)

        for pid in payments_to_update:
            payment = db.session.get(Payment, int(pid))
            if not payment:
                continue
            if payment.splits and len(payment.splits) > 0:
                total = sum(float(s.amount or 0) for s in payment.splits)
                payment.total_amount = D(str(total))
                _sync_payment_method_with_splits(payment)
            else:
                payments_to_delete.add(payment.id)

        for pid in payments_to_delete:
            payment = db.session.get(Payment, int(pid))
            if payment:
                db.session.delete(payment)
                result["deleted"]["payments"] += 1

        delete_pay_gl = _delete_payment_gl_batches(list(payments_to_delete))
        result["deleted"]["gl_batches"] += int(delete_pay_gl["deleted_batches"] or 0)
        result["deleted"]["gl_entries"] += int(delete_pay_gl["deleted_entries"] or 0)

        db.session.commit()
        return result


def run(*, dry_run=True):
    app = create_app()
    with app.app_context():
        batches = []
        batches += _collect_orphan_batches("EXPENSE", Expense)
        batches += _collect_orphan_batches("PAYMENT", Payment)
        batches += _collect_orphan_batches("PAYMENT_REVERSAL", Payment)
        batches += _collect_orphan_batches("PAYMENT_SPLIT", PaymentSplit)
        orphan_splits = _collect_orphan_splits()

        result = {
            "dry_run": dry_run,
            "orphan_batches": len(batches),
            "orphan_splits": len(orphan_splits),
            "sample_batches": batches[:50],
            "sample_splits": orphan_splits[:50],
            "deleted_batches": 0,
            "deleted_entries": 0,
            "deleted_splits": 0,
        }

        if dry_run:
            return result

        batch_ids = [b["id"] for b in batches]
        deleted_entries = 0
        deleted_batches = 0
        for chunk in _chunked(batch_ids):
            if chunk:
                res_e = db.session.execute(sa_delete(GLEntry).where(GLEntry.batch_id.in_(chunk)))
                res_b = db.session.execute(sa_delete(GLBatch).where(GLBatch.id.in_(chunk)))
                deleted_entries += int(res_e.rowcount or 0)
                deleted_batches += int(res_b.rowcount or 0)

        deleted_splits = 0
        split_ids = [s["id"] for s in orphan_splits]
        for chunk in _chunked(split_ids):
            if chunk:
                res_s = db.session.execute(sa_delete(PaymentSplit).where(PaymentSplit.id.in_(chunk)))
                deleted_splits += int(res_s.rowcount or 0)

        db.session.commit()

        result["deleted_entries"] = deleted_entries
        result["deleted_batches"] = deleted_batches
        result["deleted_splits"] = deleted_splits
        return result


def main():
    args = sys.argv[1:]
    dry_run = True
    if "--apply" in args or _as_bool(os.getenv("APPLY_CHANGES")):
        dry_run = False
    if "--dry-run" in args:
        dry_run = True
    split_refs = None
    for i, a in enumerate(args):
        if a == "--split-refs" and i + 1 < len(args):
            split_refs = args[i + 1]
    if split_refs:
        res = cleanup_specific_splits(raw_refs=split_refs, dry_run=dry_run)
    else:
        res = run(dry_run=dry_run)
    print(res)


if __name__ == "__main__":
    main()
