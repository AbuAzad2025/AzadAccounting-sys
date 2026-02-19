import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import GLBatch, GLEntry, Expense, Payment, PaymentSplit
from sqlalchemy import delete as sa_delete


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
    res = run(dry_run=dry_run)
    print(res)


if __name__ == "__main__":
    main()
