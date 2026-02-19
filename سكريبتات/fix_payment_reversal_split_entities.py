import json
import os
import sys
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db, perform_backup_db
from models import GLBatch, PaymentSplit
from sqlalchemy import or_


def _as_bool(v: Any, default: bool = False) -> bool:
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _has_arg(args: list[str], name: str) -> bool:
    return any((a or "").strip().lower() == name for a in args)


def _find_payment_batch(payment_id: int | None):
    if not payment_id:
        return None
    return (
        GLBatch.query.filter(
            GLBatch.status == "POSTED",
            GLBatch.source_type == "PAYMENT",
            GLBatch.source_id == payment_id,
        )
        .order_by(GLBatch.id.desc())
        .first()
    )


def _fix_missing_entities(*, apply_changes: bool, include_details: bool) -> dict:
    updated = 0
    skipped = 0
    details: list[dict[str, Any]] = []

    revs = GLBatch.query.filter(
        GLBatch.status == "POSTED",
        GLBatch.source_type == "PAYMENT_REVERSAL",
        or_(GLBatch.entity_type.is_(None), GLBatch.entity_id.is_(None)),
    ).all()
    for b in revs:
        pay_batch = _find_payment_batch(b.source_id)
        if pay_batch and pay_batch.entity_type and pay_batch.entity_id:
            if apply_changes:
                b.entity_type = pay_batch.entity_type
                b.entity_id = pay_batch.entity_id
            updated += 1
            if include_details:
                details.append(
                    {
                        "batch_id": b.id,
                        "source_type": b.source_type,
                        "source_id": b.source_id,
                        "entity_type": pay_batch.entity_type,
                        "entity_id": int(pay_batch.entity_id),
                    }
                )
        else:
            skipped += 1
            if include_details:
                details.append(
                    {
                        "batch_id": b.id,
                        "source_type": b.source_type,
                        "source_id": b.source_id,
                        "entity_type": None,
                        "entity_id": None,
                    }
                )

    splits = GLBatch.query.filter(
        GLBatch.status == "POSTED",
        GLBatch.source_type == "PAYMENT_SPLIT",
        or_(GLBatch.entity_type.is_(None), GLBatch.entity_id.is_(None)),
    ).all()
    for b in splits:
        split = db.session.get(PaymentSplit, int(b.source_id)) if b.source_id else None
        payment_id = getattr(split, "payment_id", None) if split else None
        pay_batch = _find_payment_batch(payment_id)
        if pay_batch and pay_batch.entity_type and pay_batch.entity_id:
            if apply_changes:
                b.entity_type = pay_batch.entity_type
                b.entity_id = pay_batch.entity_id
            updated += 1
            if include_details:
                details.append(
                    {
                        "batch_id": b.id,
                        "source_type": b.source_type,
                        "source_id": b.source_id,
                        "entity_type": pay_batch.entity_type,
                        "entity_id": int(pay_batch.entity_id),
                    }
                )
        else:
            skipped += 1
            if include_details:
                details.append(
                    {
                        "batch_id": b.id,
                        "source_type": b.source_type,
                        "source_id": b.source_id,
                        "entity_type": None,
                        "entity_id": None,
                    }
                )

    if apply_changes and updated:
        db.session.commit()

    result = {
        "reversal_batches": len(revs),
        "split_batches": len(splits),
        "updated": updated,
        "skipped": skipped,
        "applied": bool(apply_changes),
    }
    if include_details:
        result["details"] = details
    return result


def run():
    args = sys.argv[1:]
    apply_changes = _has_arg(args, "--apply") or _as_bool(os.getenv("APPLY_CHANGES"))
    with_backup = _has_arg(args, "--backup") or _as_bool(os.getenv("BACKUP_DB"))
    include_details = _has_arg(args, "--details") or _as_bool(os.getenv("DETAILS"))

    app = create_app()
    with app.app_context():
        if with_backup:
            perform_backup_db()
        result = _fix_missing_entities(apply_changes=apply_changes, include_details=include_details)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    run()
