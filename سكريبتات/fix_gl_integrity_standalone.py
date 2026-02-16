import os
import re
import sys
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from sqlalchemy import text


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


def _fetchall(sql: str, params: dict | None = None):
    return db.session.execute(text(sql), params or {}).mappings().all()


def _scalar(sql: str, params: dict | None = None):
    return db.session.execute(text(sql), params or {}).scalar()


def _audit_summary() -> dict:
    out: dict[str, Any] = {}

    out["dup_payment_number"] = _scalar(
        "SELECT COUNT(*) FROM (SELECT payment_number FROM payments GROUP BY payment_number HAVING COUNT(*)>1) x"
    )
    out["dup_receipt_number"] = _scalar(
        "SELECT COUNT(*) FROM (SELECT receipt_number FROM payments WHERE receipt_number IS NOT NULL AND receipt_number<>'' GROUP BY receipt_number HAVING COUNT(*)>1) x"
    )
    out["dup_payment_idempotency"] = _scalar(
        "SELECT COUNT(*) FROM (SELECT idempotency_key FROM payments WHERE idempotency_key IS NOT NULL AND idempotency_key<>'' GROUP BY idempotency_key HAVING COUNT(*)>1) x"
    )
    out["dup_sale_number"] = _scalar(
        "SELECT COUNT(*) FROM (SELECT sale_number FROM sales WHERE sale_number IS NOT NULL AND sale_number<>'' GROUP BY sale_number HAVING COUNT(*)>1) x"
    )
    out["dup_sale_idempotency"] = _scalar(
        "SELECT COUNT(*) FROM (SELECT idempotency_key FROM sales WHERE idempotency_key IS NOT NULL AND idempotency_key<>'' GROUP BY idempotency_key HAVING COUNT(*)>1) x"
    )

    out["dup_posted_gl_batches"] = _scalar(
        """
        SELECT COUNT(*)
        FROM (
            SELECT source_type, source_id, purpose
            FROM gl_batches
            WHERE status='POSTED'
            GROUP BY source_type, source_id, purpose
            HAVING COUNT(*)>1
        ) x
        """
    )

    out["unbalanced_or_empty_posted_batches"] = _scalar(
        """
        SELECT COUNT(*)
        FROM (
            SELECT b.id
            FROM gl_batches b
            LEFT JOIN gl_entries e ON e.batch_id = b.id
            WHERE b.status='POSTED'
            GROUP BY b.id
            HAVING ROUND(COALESCE(SUM(e.debit),0)::numeric, 2) <> ROUND(COALESCE(SUM(e.credit),0)::numeric, 2)
                OR COUNT(e.id)=0
        ) x
        """
    )

    out["orphan_entries_count"] = _scalar(
        """
        SELECT COUNT(*)
        FROM gl_entries e
        LEFT JOIN gl_batches b ON b.id=e.batch_id
        WHERE b.id IS NULL
        """
    )

    out["negative_entries_count"] = _scalar(
        "SELECT COUNT(*) FROM gl_entries WHERE COALESCE(debit,0)<0 OR COALESCE(credit,0)<0"
    )

    out["dup_entries_same_batch_count"] = _scalar(
        """
        SELECT COUNT(*)
        FROM (
            SELECT batch_id, account, COALESCE(debit,0) AS debit, COALESCE(credit,0) AS credit, COALESCE(currency,'') AS currency, COALESCE(ref,'') AS ref
            FROM gl_entries
            GROUP BY batch_id, account, COALESCE(debit,0), COALESCE(credit,0), COALESCE(currency,''), COALESCE(ref,'')
            HAVING COUNT(*)>1
        ) x
        """
    )

    out["payments_with_splits_and_payment_batch_count"] = _scalar(
        """
        SELECT COUNT(*)
        FROM payments p
        WHERE EXISTS (SELECT 1 FROM payment_splits s WHERE s.payment_id=p.id)
          AND EXISTS (SELECT 1 FROM gl_batches b WHERE b.source_type='PAYMENT' AND b.source_id=p.id AND b.status='POSTED')
        """
    )

    out["splits_missing_payment_batch_count"] = _scalar(
        """
        SELECT COUNT(*)
        FROM payment_splits s
        JOIN payments p ON p.id=s.payment_id
        WHERE p.status IN ('COMPLETED','PENDING')
          AND NOT EXISTS (
              SELECT 1 FROM gl_batches b
              WHERE b.source_type='PAYMENT_SPLIT' AND b.source_id=s.id AND b.purpose='PAYMENT' AND b.status='POSTED'
          )
        """
    )

    out["splits_missing_reversal_count"] = _scalar(
        """
        SELECT COUNT(*)
        FROM payment_splits s
        JOIN payments p ON p.id=s.payment_id
        WHERE p.status IN ('REFUNDED','CANCELLED')
          AND EXISTS (
              SELECT 1 FROM gl_batches b
              WHERE b.source_type='PAYMENT_SPLIT' AND b.source_id=s.id AND b.purpose='PAYMENT' AND b.status='POSTED'
          )
          AND NOT EXISTS (
              SELECT 1 FROM gl_batches b
              WHERE b.source_type='PAYMENT_SPLIT' AND b.source_id=s.id AND b.purpose='PAYMENT_REVERSAL' AND b.status='POSTED'
          )
        """
    )

    out["legacy_refunded_with_refund_of_count"] = _scalar(
        """
        SELECT COUNT(*)
        FROM payments p
        WHERE p.status='REFUNDED'
          AND EXISTS (SELECT 1 FROM payments r WHERE r.refund_of_id = p.id)
        """
    )

    return out


def _audit_samples() -> dict:
    out: dict[str, Any] = {}
    out["unbalanced_or_empty_posted_batches_sample"] = _fetchall(
        """
        SELECT b.id AS batch_id,
               b.source_type,
               b.source_id,
               b.purpose,
               ROUND(COALESCE(SUM(e.debit),0)::numeric, 2) AS debit,
               ROUND(COALESCE(SUM(e.credit),0)::numeric, 2) AS credit,
               COUNT(e.id) AS entry_count
        FROM gl_batches b
        LEFT JOIN gl_entries e ON e.batch_id = b.id
        WHERE b.status='POSTED'
        GROUP BY b.id, b.source_type, b.source_id, b.purpose
        HAVING ROUND(COALESCE(SUM(e.debit),0)::numeric, 2) <> ROUND(COALESCE(SUM(e.credit),0)::numeric, 2)
            OR COUNT(e.id)=0
        ORDER BY b.id DESC
        LIMIT 25
        """
    )
    out["orphan_entries_sample"] = _fetchall(
        """
        SELECT e.id, e.batch_id, e.account, e.debit, e.credit, e.currency, e.ref
        FROM gl_entries e
        LEFT JOIN gl_batches b ON b.id = e.batch_id
        WHERE b.id IS NULL
        ORDER BY e.batch_id, e.id
        LIMIT 25
        """
    )
    out["splits_missing_reversal_sample"] = _fetchall(
        """
        SELECT s.id AS split_id,
               p.id AS payment_id,
               p.payment_number,
               p.status AS payment_status,
               s.amount,
               s.currency,
               s.method
        FROM payment_splits s
        JOIN payments p ON p.id = s.payment_id
        WHERE p.status IN ('REFUNDED','CANCELLED')
          AND EXISTS (
              SELECT 1 FROM gl_batches b
              WHERE b.source_type='PAYMENT_SPLIT' AND b.source_id=s.id AND b.purpose='PAYMENT' AND b.status='POSTED'
          )
          AND NOT EXISTS (
              SELECT 1 FROM gl_batches b
              WHERE b.source_type='PAYMENT_SPLIT' AND b.source_id=s.id AND b.purpose='PAYMENT_REVERSAL' AND b.status='POSTED'
          )
        ORDER BY p.id, s.id
        LIMIT 25
        """
    )
    out["legacy_refunded_with_refund_of_sample"] = _fetchall(
        """
        SELECT p.id AS original_payment_id,
               p.payment_number AS original_payment_number,
               p.entity_type,
               p.customer_id,
               p.supplier_id,
               p.partner_id,
               p.direction AS original_direction,
               p.total_amount AS original_total_amount,
               r.id AS refund_payment_id,
               r.payment_number AS refund_payment_number,
               r.direction AS refund_direction,
               r.total_amount AS refund_total_amount,
               r.status AS refund_status
        FROM payments p
        JOIN payments r ON r.refund_of_id = p.id
        WHERE p.status='REFUNDED'
        ORDER BY p.id
        LIMIT 25
        """
    )
    return out


def _find_stray_entry_ids() -> tuple[list[int], list[int]]:
    rows = _fetchall(
        """
        SELECT e.id, e.ref
        FROM gl_entries e
        JOIN gl_batches b ON b.id = e.batch_id
        WHERE b.status='POSTED'
          AND b.source_type <> 'PAYMENT_SPLIT'
          AND (
              e.ref LIKE 'TEST\\_%' ESCAPE '\\'
              OR e.ref LIKE 'SPLIT-%-PMT-%'
              OR e.ref LIKE 'REV-SPLIT-%-PMT-%'
          )
        ORDER BY e.id
        """
    )
    entry_ids: list[int] = []
    split_ids: list[int] = []
    rx = re.compile(r"^(?:REV-)?SPLIT-(\d+)-PMT-", re.IGNORECASE)
    for r in rows:
        entry_ids.append(int(r["id"]))
        ref = str(r.get("ref") or "")
        m = rx.match(ref)
        if m:
            try:
                split_ids.append(int(m.group(1)))
            except Exception:
                pass
    split_ids = sorted({int(x) for x in split_ids if int(x) > 0})
    return entry_ids, split_ids


def _delete_orphan_entries() -> int:
    res = db.session.execute(
        text(
            """
            DELETE FROM gl_entries e
            WHERE NOT EXISTS (SELECT 1 FROM gl_batches b WHERE b.id = e.batch_id)
            """
        )
    )
    return int(res.rowcount or 0)


def _delete_entries_by_ids(entry_ids: list[int]) -> int:
    if not entry_ids:
        return 0
    res = db.session.execute(
        text("DELETE FROM gl_entries WHERE id = ANY(CAST(:ids AS int[]))"),
        {"ids": entry_ids},
    )
    return int(res.rowcount or 0)


def _backfill_split_reversals(split_ids: list[int]) -> int:
    if not split_ids:
        return 0
    from models import _payment_split_gl_batch_upsert_by_id

    fixed = 0
    with db.engine.begin() as conn:
        for sid in split_ids:
            _payment_split_gl_batch_upsert_by_id(conn, split_id=int(sid))
            fixed += 1
    return fixed


def _fix_legacy_refunded_with_refund_of() -> tuple[int, list[int], set[tuple[str, int]]]:
    rows = _fetchall(
        """
        SELECT p.id AS payment_id,
               p.customer_id,
               p.supplier_id,
               p.partner_id
        FROM payments p
        WHERE p.status='REFUNDED'
          AND EXISTS (SELECT 1 FROM payments r WHERE r.refund_of_id = p.id)
        ORDER BY p.id
        """
    )
    payment_ids = [int(r["payment_id"]) for r in rows]
    if not payment_ids:
        return 0, [], set()

    target_entities: set[tuple[str, int]] = set()
    for r in rows:
        cid = r.get("customer_id")
        sid = r.get("supplier_id")
        pid = r.get("partner_id")
        if cid:
            target_entities.add(("CUSTOMER", int(cid)))
        if sid:
            target_entities.add(("SUPPLIER", int(sid)))
        if pid:
            target_entities.add(("PARTNER", int(pid)))

    split_rows = _fetchall(
        """
        SELECT s.id AS split_id
        FROM payment_splits s
        WHERE s.payment_id = ANY(CAST(:pids AS int[]))
        ORDER BY s.id
        """,
        {"pids": payment_ids},
    )
    split_ids = [int(r["split_id"]) for r in split_rows]

    updated = db.session.execute(
        text("UPDATE payments SET status='COMPLETED' WHERE id = ANY(CAST(:pids AS int[]))"),
        {"pids": payment_ids},
    )
    return int(updated.rowcount or 0), split_ids, target_entities


def run_fix_standalone(*, dry_run: bool) -> dict:
    app = create_app()
    with app.app_context():
        before = _audit_summary()
        samples = _audit_samples()

        stray_entry_ids, stray_split_ids = _find_stray_entry_ids()

        result: dict[str, Any] = {
            "dry_run": bool(dry_run),
            "before": before,
            "samples": samples,
            "planned": {
                "delete_orphan_entries": int(before.get("orphan_entries_count") or 0),
                "delete_stray_entries": len(stray_entry_ids),
                "touch_split_ids_from_stray_refs": len(stray_split_ids),
                "backfill_missing_reversal_splits": int(before.get("splits_missing_reversal_count") or 0),
                "fix_legacy_refunded_with_refund_of": int(before.get("legacy_refunded_with_refund_of_count") or 0),
            },
            "applied": {},
            "after": None,
        }

        if dry_run:
            return result

        fixed_legacy_payments, legacy_split_ids, legacy_entities = _fix_legacy_refunded_with_refund_of()
        deleted_orphans = _delete_orphan_entries()
        deleted_strays = _delete_entries_by_ids(stray_entry_ids)
        db.session.commit()

        missing_reversal_ids = [
            int(r["split_id"])
            for r in _fetchall(
                """
                SELECT s.id AS split_id
                FROM payment_splits s
                JOIN payments p ON p.id = s.payment_id
                WHERE p.status IN ('REFUNDED','CANCELLED')
                  AND EXISTS (
                      SELECT 1 FROM gl_batches b
                      WHERE b.source_type='PAYMENT_SPLIT' AND b.source_id=s.id AND b.purpose='PAYMENT' AND b.status='POSTED'
                  )
                  AND NOT EXISTS (
                      SELECT 1 FROM gl_batches b
                      WHERE b.source_type='PAYMENT_SPLIT' AND b.source_id=s.id AND b.purpose='PAYMENT_REVERSAL' AND b.status='POSTED'
                  )
                ORDER BY s.id
                """
            )
        ]

        touched_split_ids = sorted({*stray_split_ids, *missing_reversal_ids, *legacy_split_ids})
        fixed_splits = _backfill_split_reversals(touched_split_ids)

        updated_entities = 0
        if legacy_entities:
            try:
                import utils

                for etype, eid in sorted(legacy_entities):
                    try:
                        utils.update_entity_balance(etype, int(eid))
                        updated_entities += 1
                    except Exception:
                        pass
                db.session.commit()
            except Exception:
                db.session.rollback()

        after = _audit_summary()
        result["applied"] = {
            "fixed_legacy_refunded_payments": fixed_legacy_payments,
            "deleted_orphan_entries": deleted_orphans,
            "deleted_stray_entries": deleted_strays,
            "touched_split_ids": len(touched_split_ids),
            "fixed_splits_called": fixed_splits,
            "updated_entity_balances": updated_entities,
        }
        result["after"] = after
        return result


def main():
    args = sys.argv[1:]
    env_dry = _as_bool(os.environ.get("DRY_RUN"), False)
    env_apply = _as_bool(os.environ.get("APPLY"), False)
    arg_dry = _has_arg(args, "--dry-run")
    arg_apply = _has_arg(args, "--apply")

    if arg_apply:
        dry_run = False
    elif arg_dry:
        dry_run = True
    else:
        dry_run = (not env_apply) or env_dry

    result = run_fix_standalone(dry_run=dry_run)

    print("=== fix_gl_integrity_standalone ===")
    print("الوضع:", "معاينة (DRY RUN)" if result["dry_run"] else "تنفيذ فعلي")

    print("قبل:")
    for k in sorted(result["before"].keys()):
        print(" -", k, "=", result["before"][k])

    print("عينات:")
    for k in [
        "unbalanced_or_empty_posted_batches_sample",
        "orphan_entries_sample",
        "splits_missing_reversal_sample",
        "legacy_refunded_with_refund_of_sample",
    ]:
        rows = result["samples"].get(k) or []
        print(" -", k, "=", len(rows))
        if rows:
            print("   مثال:", rows[:3])

    print("الخطة:")
    for k in sorted(result["planned"].keys()):
        print(" -", k, "=", result["planned"][k])

    if not result["dry_run"]:
        print("تم:")
        for k in sorted(result["applied"].keys()):
            print(" -", k, "=", result["applied"][k])
        print("بعد:")
        for k in sorted((result["after"] or {}).keys()):
            print(" -", k, "=", result["after"][k])


if __name__ == "__main__":
    main()
