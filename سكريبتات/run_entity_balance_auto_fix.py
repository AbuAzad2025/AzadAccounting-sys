import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db, perform_backup_db
from models import (
    Customer,
    Expense,
    GLBatch,
    GLEntry,
    GL_ACCOUNTS,
    Invoice,
    Partner,
    Payment,
    PaymentSplit,
    Sale,
    ServiceRequest,
    Supplier,
    _fx_rate_local_via_connection,
    _gl_upsert_batch_and_entries,
    _payment_split_gl_batch_upsert_by_id,
    run_expense_gl_sync_after_commit,
    run_invoice_gl_sync_after_commit,
    run_payment_gl_sync_after_commit,
    run_sale_gl_sync_after_commit,
    run_service_gl_sync_after_commit,
)
from services.ledger_service import SmartEntityExtractor
from sqlalchemy import func, or_, text


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


def _as_int(v: Any, default: int) -> int:
    try:
        return int(v)
    except Exception:
        return default


def _as_float(v: Any, default: float) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _as_date(v: Any) -> datetime.date:
    if not v:
        return datetime.now(timezone.utc).date()
    return datetime.fromisoformat(str(v).replace("Z", "+00:00")).date()


def _as_optional_date(v: Any) -> Optional[datetime.date]:
    if not v:
        return None
    return datetime.fromisoformat(str(v).replace("Z", "+00:00")).date()


def _parse_str_set(raw: Any) -> set[str]:
    if not raw:
        return set()
    if isinstance(raw, (list, tuple, set)):
        items = raw
    else:
        items = str(raw).split(",")
    out = set()
    for item in items:
        val = str(item).strip().lower()
        if val:
            out.add(val)
    return out


def _apply_date_range(q, column, from_date: Optional[datetime.date], to_date: Optional[datetime.date]):
    if from_date:
        q = q.filter(column >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        q = q.filter(column <= datetime.combine(to_date, datetime.max.time()))
    return q


def _legacy_fx_candidate_ids(*, from_date, to_date, limit: int, types: set[str], force: bool) -> dict:
    out = {"sales": [], "invoices": [], "services": [], "payments": [], "payment_splits": []}
    limit = int(limit or 0)
    if "sales" in types:
        q = db.session.query(Sale.id).filter(
            func.upper(func.coalesce(Sale.currency, "ILS")) != "ILS",
            Sale.status == "CONFIRMED",
        )
        if not force:
            q = q.filter(or_(Sale.fx_rate_used.is_(None), Sale.fx_rate_used <= 0))
        q = _apply_date_range(q, Sale.sale_date, from_date, to_date)
        if limit:
            q = q.order_by(Sale.id.asc()).limit(limit)
        out["sales"] = [int(r[0]) for r in q.all()]
    if "invoices" in types:
        q = db.session.query(Invoice.id).filter(
            func.upper(func.coalesce(Invoice.currency, "ILS")) != "ILS",
            Invoice.cancelled_at.is_(None),
        )
        if not force:
            q = q.filter(or_(Invoice.fx_rate_used.is_(None), Invoice.fx_rate_used <= 0))
        q = _apply_date_range(q, Invoice.invoice_date, from_date, to_date)
        if limit:
            q = q.order_by(Invoice.id.asc()).limit(limit)
        out["invoices"] = [int(r[0]) for r in q.all()]
    if "services" in types:
        q = db.session.query(ServiceRequest.id).filter(
            func.upper(func.coalesce(ServiceRequest.currency, "ILS")) != "ILS",
            ServiceRequest.cancelled_at.is_(None),
            func.coalesce(ServiceRequest.total_amount, 0) > 0,
        )
        if not force:
            q = q.filter(or_(ServiceRequest.fx_rate_used.is_(None), ServiceRequest.fx_rate_used <= 0))
        q = _apply_date_range(q, ServiceRequest.received_at, from_date, to_date)
        if limit:
            q = q.order_by(ServiceRequest.id.asc()).limit(limit)
        out["services"] = [int(r[0]) for r in q.all()]
    if "payments" in types:
        q = db.session.query(Payment.id).filter(
            func.upper(func.coalesce(Payment.currency, "ILS")) != "ILS",
            Payment.status.in_(["COMPLETED", "PENDING"]),
        )
        if not force:
            q = q.filter(or_(Payment.fx_rate_used.is_(None), Payment.fx_rate_used <= 0))
        q = _apply_date_range(q, Payment.payment_date, from_date, to_date)
        if limit:
            q = q.order_by(Payment.id.asc()).limit(limit)
        out["payments"] = [int(r[0]) for r in q.all()]
    if "payment_splits" in types:
        q = (
            db.session.query(PaymentSplit.id)
            .join(Payment, PaymentSplit.payment_id == Payment.id)
            .filter(
                func.upper(func.coalesce(PaymentSplit.currency, "ILS")) != "ILS",
                Payment.status.in_(["COMPLETED", "PENDING", "REFUNDED", "CANCELLED"]),
            )
        )
        if not force:
            q = q.filter(or_(PaymentSplit.fx_rate_used.is_(None), PaymentSplit.fx_rate_used <= 0))
        q = _apply_date_range(q, Payment.payment_date, from_date, to_date)
        if limit:
            q = q.order_by(PaymentSplit.id.asc()).limit(limit)
        out["payment_splits"] = [int(r[0]) for r in q.all()]
    return out


def _apply_legacy_fx(*, plan: dict, force: bool, dry_run: bool) -> dict:
    now_ts = datetime.now(timezone.utc)
    conn = db.session.connection()
    backfilled = {"sales": 0, "invoices": 0, "services": 0, "payments": 0, "payment_splits": 0}
    missing_rate = {"sales": 0, "invoices": 0, "services": 0, "payments": 0, "payment_splits": 0}

    def _update_row(table: str, row_id: int, rate, base):
        db.session.execute(
            text(
                f"""
                UPDATE {table}
                   SET fx_rate_used = :rate,
                       fx_rate_source = :src,
                       fx_rate_timestamp = :ts,
                       fx_base_currency = :base,
                       fx_quote_currency = :quote
                 WHERE id = :id
                """
            ),
            {
                "rate": rate,
                "src": "manual",
                "ts": now_ts,
                "base": base,
                "quote": "ILS",
                "id": int(row_id),
            },
        )

    if plan.get("sales"):
        rows = (
            db.session.query(Sale.id, Sale.currency, Sale.sale_date, Sale.fx_rate_used)
            .filter(Sale.id.in_(plan["sales"]))
            .all()
        )
        for rid, currency, sale_date, fx_rate_used in rows:
            if (fx_rate_used or 0) > 0 and not force:
                continue
            cur = (str(currency or "ILS")).upper()
            if cur == "ILS":
                continue
            rate = _fx_rate_local_via_connection(conn, cur, "ILS", sale_date or now_ts)
            if not rate or rate <= 0:
                missing_rate["sales"] += 1
                continue
            backfilled["sales"] += 1
            if not dry_run:
                _update_row("sales", int(rid), rate, cur)
    if plan.get("invoices"):
        rows = (
            db.session.query(Invoice.id, Invoice.currency, Invoice.invoice_date, Invoice.fx_rate_used)
            .filter(Invoice.id.in_(plan["invoices"]))
            .all()
        )
        for rid, currency, invoice_date, fx_rate_used in rows:
            if (fx_rate_used or 0) > 0 and not force:
                continue
            cur = (str(currency or "ILS")).upper()
            if cur == "ILS":
                continue
            rate = _fx_rate_local_via_connection(conn, cur, "ILS", invoice_date or now_ts)
            if not rate or rate <= 0:
                missing_rate["invoices"] += 1
                continue
            backfilled["invoices"] += 1
            if not dry_run:
                _update_row("invoices", int(rid), rate, cur)
    if plan.get("services"):
        rows = (
            db.session.query(ServiceRequest.id, ServiceRequest.currency, ServiceRequest.received_at, ServiceRequest.fx_rate_used)
            .filter(ServiceRequest.id.in_(plan["services"]))
            .all()
        )
        for rid, currency, received_at, fx_rate_used in rows:
            if (fx_rate_used or 0) > 0 and not force:
                continue
            cur = (str(currency or "ILS")).upper()
            if cur == "ILS":
                continue
            rate = _fx_rate_local_via_connection(conn, cur, "ILS", received_at or now_ts)
            if not rate or rate <= 0:
                missing_rate["services"] += 1
                continue
            backfilled["services"] += 1
            if not dry_run:
                _update_row("service_requests", int(rid), rate, cur)
    if plan.get("payments"):
        rows = (
            db.session.query(Payment.id, Payment.currency, Payment.payment_date, Payment.fx_rate_used)
            .filter(Payment.id.in_(plan["payments"]))
            .all()
        )
        for rid, currency, payment_date, fx_rate_used in rows:
            if (fx_rate_used or 0) > 0 and not force:
                continue
            cur = (str(currency or "ILS")).upper()
            if cur == "ILS":
                continue
            rate = _fx_rate_local_via_connection(conn, cur, "ILS", payment_date or now_ts)
            if not rate or rate <= 0:
                missing_rate["payments"] += 1
                continue
            backfilled["payments"] += 1
            if not dry_run:
                _update_row("payments", int(rid), rate, cur)
    if plan.get("payment_splits"):
        rows = (
            db.session.query(PaymentSplit.id, PaymentSplit.currency, PaymentSplit.fx_rate_used, Payment.payment_date)
            .join(Payment, PaymentSplit.payment_id == Payment.id)
            .filter(PaymentSplit.id.in_(plan["payment_splits"]))
            .all()
        )
        for rid, currency, fx_rate_used, payment_date in rows:
            if (fx_rate_used or 0) > 0 and not force:
                continue
            cur = (str(currency or "ILS")).upper()
            if cur == "ILS":
                continue
            rate = _fx_rate_local_via_connection(conn, cur, "ILS", payment_date or now_ts)
            if not rate or rate <= 0:
                missing_rate["payment_splits"] += 1
                continue
            backfilled["payment_splits"] += 1
            if not dry_run:
                _update_row("payment_splits", int(rid), rate, cur)

    if not dry_run:
        db.session.commit()

    return {"dry_run": bool(dry_run), "backfilled": backfilled, "missing_rate": missing_rate}


def _scalar(sql: str, params: Optional[dict] = None):
    return db.session.execute(text(sql), params or {}).scalar()


def _opening_balance_expected_net(opening_balance: float) -> float:
    if opening_balance > 0:
        return -abs(opening_balance)
    return abs(opening_balance)


def _delete_opening_balance_batches(*, source_type: str, source_id: int):
    dialect_name = getattr(getattr(db.session.get_bind(), "dialect", None), "name", "")
    batch_table = "public.gl_batches" if dialect_name == "postgresql" else "gl_batches"
    entry_table = "public.gl_entries" if dialect_name == "postgresql" else "gl_entries"
    db.session.execute(
        text(
            f"""
            DELETE FROM {entry_table}
            WHERE batch_id IN (
                SELECT id FROM {batch_table}
                WHERE source_type = :st AND source_id = :sid AND purpose = 'OPENING_BALANCE'
            )
            """
        ),
        {"st": source_type, "sid": int(source_id)},
    )
    db.session.execute(
        text(
            f"""
            DELETE FROM {batch_table}
            WHERE source_type = :st AND source_id = :sid AND purpose = 'OPENING_BALANCE'
            """
        ),
        {"st": source_type, "sid": int(source_id)},
    )


def _refresh_opening_balance_batches(*, target_ids: dict) -> dict:
    ar_account = (GL_ACCOUNTS.get("AR") or "1100_AR").upper()
    ap_account = (GL_ACCOUNTS.get("AP") or "2000_AP").upper()
    updated = 0
    cleared = 0
    skipped = 0

    def _process(entity, entity_type: str, account_code: str):
        nonlocal updated, cleared, skipped
        if not entity:
            skipped += 1
            return
        opening_balance = float(getattr(entity, "opening_balance", 0) or 0)
        if opening_balance == 0:
            existing = _scalar(
                """
                SELECT COUNT(1) FROM gl_batches
                 WHERE source_type = :st AND source_id = :sid AND purpose = 'OPENING_BALANCE'
                """,
                {"st": entity_type, "sid": int(entity.id)},
            )
            if int(existing or 0) > 0:
                _delete_opening_balance_batches(source_type=entity_type, source_id=int(entity.id))
                cleared += 1
            else:
                skipped += 1
            return

        expected_net = _opening_balance_expected_net(opening_balance)
        existing = (
            db.session.execute(
                text(
                    """
                    SELECT b.id AS id, COALESCE(SUM(e.debit - e.credit), 0) AS net
                    FROM gl_batches b
                    JOIN gl_entries e ON e.batch_id = b.id
                    WHERE b.source_type = :st AND b.source_id = :sid AND b.purpose = 'OPENING_BALANCE'
                      AND b.status = 'POSTED' AND e.account = :acc
                    GROUP BY b.id
                    ORDER BY b.id DESC
                    LIMIT 1
                    """
                ),
                {"st": entity_type, "sid": int(entity.id), "acc": account_code},
            )
            .mappings()
            .first()
        )
        if existing and abs(float(existing["net"] or 0) - float(expected_net)) <= 0.01:
            skipped += 1
            return

        _delete_opening_balance_batches(source_type=entity_type, source_id=int(entity.id))

        if opening_balance > 0:
            entries = [
                ("3000_EQUITY", abs(opening_balance), 0),
                (account_code, 0, abs(opening_balance)),
            ]
        else:
            entries = [
                (account_code, abs(opening_balance), 0),
                ("3000_EQUITY", 0, abs(opening_balance)),
            ]

        _gl_upsert_batch_and_entries(
            db.session.connection(),
            source_type=entity_type,
            source_id=int(entity.id),
            purpose="OPENING_BALANCE",
            currency="ILS",
            memo=f"رصيد افتتاحي - {getattr(entity, 'name', '')}",
            entries=entries,
            ref=f"OB-{entity_type}-{int(entity.id)}",
            entity_type=entity_type,
            entity_id=int(entity.id),
        )
        updated += 1

    for customer_id in target_ids.get("customers", []):
        _process(db.session.get(Customer, int(customer_id)), "CUSTOMER", ar_account)
    for supplier_id in target_ids.get("suppliers", []):
        _process(db.session.get(Supplier, int(supplier_id)), "SUPPLIER", ap_account)
    for partner_id in target_ids.get("partners", []):
        _process(db.session.get(Partner, int(partner_id)), "PARTNER", ap_account)

    if updated or cleared:
        db.session.commit()
    return {"updated": updated, "cleared": cleared, "skipped": skipped}


def _purge_orphan_invoice_gl() -> dict:
    dialect_name = getattr(getattr(db.session.get_bind(), "dialect", None), "name", "")
    batch_table = "public.gl_batches" if dialect_name == "postgresql" else "gl_batches"
    entry_table = "public.gl_entries" if dialect_name == "postgresql" else "gl_entries"
    orphan_ids = db.session.execute(
        text(
            f"""
            SELECT b.id
            FROM {batch_table} b
            LEFT JOIN invoices i ON i.id = b.source_id
            WHERE b.source_type = 'INVOICE' AND i.id IS NULL
            """
        )
    ).scalars().all()
    if not orphan_ids:
        return {"deleted_batches": 0, "deleted_entries": 0}
    db.session.execute(
        text(f"DELETE FROM {entry_table} WHERE batch_id IN :ids"),
        {"ids": tuple(int(x) for x in orphan_ids)},
    )
    db.session.execute(
        text(f"DELETE FROM {batch_table} WHERE id IN :ids"),
        {"ids": tuple(int(x) for x in orphan_ids)},
    )
    db.session.commit()
    return {"deleted_batches": len(orphan_ids), "deleted_entries": len(orphan_ids)}


def _parse_id_list(raw: Any) -> list[int]:
    if not raw:
        return []
    if isinstance(raw, (list, tuple)):
        items = raw
    else:
        items = str(raw).split(",")
    out = []
    for item in items:
        try:
            out.append(int(str(item).strip()))
        except Exception:
            continue
    return [i for i in out if i > 0]


def _fix_gl_entities(*, as_of_date, override: bool, max_batches: int) -> dict:
    as_of_dt = datetime.combine(as_of_date, datetime.max.time())

    q = GLBatch.query.filter(
        GLBatch.status == "POSTED",
        GLBatch.posted_at <= as_of_dt,
    )
    supported_source_types = {"PAYMENT", "PAYMENT_SPLIT", "SALE", "INVOICE", "EXPENSE", "SERVICE", "PREORDER", "SHIPMENT"}
    if override:
        q = q.filter(
            GLBatch.source_type.isnot(None),
            GLBatch.source_id.isnot(None),
            func.upper(GLBatch.source_type).in_(supported_source_types),
        )
    else:
        q = q.filter(or_(GLBatch.entity_type.is_(None), GLBatch.entity_id.is_(None)))

    batches = q.order_by(GLBatch.id.desc()).limit(max_batches).all()

    updated = 0
    skipped = 0

    for b in batches:
        old_type = b.entity_type
        old_id = b.entity_id

        if override:
            name, type_ar, entity_id, entity_type = SmartEntityExtractor.extract_from_source(b)
        else:
            name, type_ar, entity_id, entity_type = SmartEntityExtractor.extract_from_batch(b)
        if not entity_type or not entity_id:
            skipped += 1
            continue

        entity_type = str(entity_type).upper()
        if entity_type not in {"CUSTOMER", "SUPPLIER", "PARTNER", "EMPLOYEE"}:
            skipped += 1
            continue

        if (old_type or "").upper() == entity_type and int(old_id or 0) == int(entity_id or 0):
            skipped += 1
            continue

        b.entity_type = entity_type
        b.entity_id = int(entity_id)
        updated += 1

    if updated:
        db.session.commit()

    return {
        "found_batches": len(batches),
        "updated_batches": updated,
        "skipped_batches": skipped,
    }


def _find_mismatch_entity_ids(*, as_of_date, tolerance: float, include_archived: bool, max_customers: int, max_suppliers: int, max_partners: int) -> dict:
    as_of_dt = datetime.combine(as_of_date, datetime.max.time())

    ar_account = (GL_ACCOUNTS.get("AR") or "1100_AR").upper()
    ap_account = (GL_ACCOUNTS.get("AP") or "2000_AP").upper()

    customer_gl_sq = (
        db.session.query(
            GLBatch.entity_id.label("entity_id"),
            func.coalesce(func.sum(GLEntry.debit - GLEntry.credit), 0).label("gl_balance"),
        )
        .join(GLEntry, GLEntry.batch_id == GLBatch.id)
        .filter(
            GLBatch.status == "POSTED",
            GLBatch.posted_at <= as_of_dt,
            GLBatch.entity_type == "CUSTOMER",
            GLEntry.account == ar_account,
        )
        .group_by(GLBatch.entity_id)
        .subquery()
    )
    supplier_gl_sq = (
        db.session.query(
            GLBatch.entity_id.label("entity_id"),
            func.coalesce(func.sum(GLEntry.credit - GLEntry.debit), 0).label("gl_balance"),
        )
        .join(GLEntry, GLEntry.batch_id == GLBatch.id)
        .filter(
            GLBatch.status == "POSTED",
            GLBatch.posted_at <= as_of_dt,
            GLBatch.entity_type == "SUPPLIER",
            GLEntry.account == ap_account,
        )
        .group_by(GLBatch.entity_id)
        .subquery()
    )
    partner_ap_sq = (
        db.session.query(
            GLBatch.entity_id.label("entity_id"),
            func.coalesce(func.sum(GLEntry.credit - GLEntry.debit), 0).label("gl_balance"),
        )
        .join(GLEntry, GLEntry.batch_id == GLBatch.id)
        .filter(
            GLBatch.status == "POSTED",
            GLBatch.posted_at <= as_of_dt,
            GLBatch.entity_type == "PARTNER",
            GLEntry.account == ap_account,
        )
        .group_by(GLBatch.entity_id)
        .subquery()
    )
    partner_ar_sq = (
        db.session.query(
            Partner.id.label("entity_id"),
            func.coalesce(func.sum(GLEntry.debit - GLEntry.credit), 0).label("gl_balance"),
        )
        .join(GLBatch, GLBatch.entity_id == Partner.customer_id)
        .join(GLEntry, GLEntry.batch_id == GLBatch.id)
        .filter(
            GLBatch.status == "POSTED",
            GLBatch.posted_at <= as_of_dt,
            GLBatch.entity_type == "CUSTOMER",
            GLEntry.account == ar_account,
            Partner.customer_id.isnot(None),
        )
        .group_by(Partner.id)
        .subquery()
    )
    partner_gl_sq = (
        db.session.query(
            Partner.id.label("entity_id"),
            (
                func.coalesce(partner_ap_sq.c.gl_balance, 0)
                - func.coalesce(partner_ar_sq.c.gl_balance, 0)
            ).label("gl_balance"),
        )
        .outerjoin(partner_ap_sq, partner_ap_sq.c.entity_id == Partner.id)
        .outerjoin(partner_ar_sq, partner_ar_sq.c.entity_id == Partner.id)
        .subquery()
    )

    cust_stored = func.coalesce(Customer.current_balance, 0)
    cust_gl = func.coalesce(customer_gl_sq.c.gl_balance, 0)
    cust_diff = cust_gl - (-cust_stored)
    customers_q = db.session.query(Customer.id).outerjoin(customer_gl_sq, customer_gl_sq.c.entity_id == Customer.id)
    if hasattr(Customer, "is_archived") and not include_archived:
        customers_q = customers_q.filter(Customer.is_archived.is_(False))
    customers_ids = [
        int(r.id)
        for r in customers_q.filter(func.abs(cust_diff) > tolerance).order_by(func.abs(cust_diff).desc()).limit(max_customers).all()
    ]

    supp_stored = func.coalesce(Supplier.current_balance, 0)
    supp_gl = func.coalesce(supplier_gl_sq.c.gl_balance, 0)
    supp_diff = supp_gl - supp_stored
    suppliers_q = db.session.query(Supplier.id).outerjoin(supplier_gl_sq, supplier_gl_sq.c.entity_id == Supplier.id)
    if hasattr(Supplier, "is_archived") and not include_archived:
        suppliers_q = suppliers_q.filter(Supplier.is_archived.is_(False))
    suppliers_ids = [
        int(r.id)
        for r in suppliers_q.filter(func.abs(supp_diff) > tolerance).order_by(func.abs(supp_diff).desc()).limit(max_suppliers).all()
    ]

    part_stored = func.coalesce(Partner.current_balance, 0)
    part_gl = func.coalesce(partner_gl_sq.c.gl_balance, 0)
    part_diff = part_gl - part_stored
    partners_q = db.session.query(Partner.id).outerjoin(partner_gl_sq, partner_gl_sq.c.entity_id == Partner.id)
    if hasattr(Partner, "is_archived") and not include_archived:
        partners_q = partners_q.filter(Partner.is_archived.is_(False))
    partners_ids = [
        int(r.id)
        for r in partners_q.filter(func.abs(part_diff) > tolerance).order_by(func.abs(part_diff).desc()).limit(max_partners).all()
    ]

    return {
        "as_of_date": as_of_date.isoformat(),
        "tolerance": tolerance,
        "accounts": {"ar": ar_account, "ap": ap_account},
        "target_ids": {"customers": customers_ids, "suppliers": suppliers_ids, "partners": partners_ids},
    }


def _recalculate_entities(*, target_ids: dict) -> dict:
    from utils.customer_balance_updater import update_customer_balance_components
    from utils.supplier_balance_updater import update_supplier_balance_components
    from models import update_partner_balance

    recalculated = {"customers": 0, "suppliers": 0, "partners": 0}

    for cid in target_ids.get("customers", []):
        try:
            update_customer_balance_components(int(cid), db.session)
            recalculated["customers"] += 1
        except Exception:
            pass

    for sid in target_ids.get("suppliers", []):
        try:
            update_supplier_balance_components(int(sid), db.session)
            recalculated["suppliers"] += 1
        except Exception:
            pass

    for pid in target_ids.get("partners", []):
        try:
            update_partner_balance(int(pid), db.session)
            recalculated["partners"] += 1
        except Exception:
            pass

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    return recalculated


def _gl_balance_for_entity(*, entity_type: str, entity_id: int, as_of_date: datetime.date) -> float:
    as_of_dt = datetime.combine(as_of_date, datetime.max.time())
    ar_account = (GL_ACCOUNTS.get("AR") or "1100_AR").upper()
    ap_account = (GL_ACCOUNTS.get("AP") or "2000_AP").upper()
    q = (
        db.session.query(func.coalesce(func.sum(GLEntry.debit - GLEntry.credit), 0))
        .join(GLBatch, GLEntry.batch_id == GLBatch.id)
        .filter(
            GLBatch.status == "POSTED",
            GLBatch.posted_at <= as_of_dt,
            GLBatch.entity_type == entity_type,
            GLBatch.entity_id == int(entity_id),
        )
    )
    if entity_type == "CUSTOMER":
        q = q.filter(GLEntry.account == ar_account)
        return float(q.scalar() or 0)
    if entity_type == "PARTNER":
        ap_q = q.filter(GLEntry.account == ap_account)
        ap_q = ap_q.with_entities(func.coalesce(func.sum(GLEntry.credit - GLEntry.debit), 0))
        ap_balance = float(ap_q.scalar() or 0)
        partner = db.session.get(Partner, int(entity_id))
        customer_id = getattr(partner, "customer_id", None)
        ar_balance = 0.0
        if customer_id:
            ar_balance = (
                db.session.query(func.coalesce(func.sum(GLEntry.debit - GLEntry.credit), 0))
                .join(GLBatch, GLEntry.batch_id == GLBatch.id)
                .filter(
                    GLBatch.status == "POSTED",
                    GLBatch.posted_at <= as_of_dt,
                    GLBatch.entity_type == "CUSTOMER",
                    GLBatch.entity_id == int(customer_id),
                    GLEntry.account == ar_account,
                )
                .scalar()
                or 0
            )
        return float(ap_balance - float(ar_balance))
    q = q.filter(GLEntry.account == ap_account)
    q = q.with_entities(func.coalesce(func.sum(GLEntry.credit - GLEntry.debit), 0))
    return float(q.scalar() or 0)


def _missing_gl_for_customer(customer_id: int) -> dict:
    missing_sales = (
        db.session.query(func.count(Sale.id))
        .filter(
            Sale.customer_id == customer_id,
            Sale.status == "CONFIRMED",
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "SALE",
                GLBatch.source_id == Sale.id,
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    missing_invoices = (
        db.session.query(func.count(Invoice.id))
        .filter(
            Invoice.customer_id == customer_id,
            Invoice.cancelled_at.is_(None),
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "INVOICE",
                GLBatch.source_id == Invoice.id,
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    missing_services = (
        db.session.query(func.count(ServiceRequest.id))
        .filter(
            ServiceRequest.customer_id == customer_id,
            ServiceRequest.cancelled_at.is_(None),
            func.coalesce(ServiceRequest.total_amount, 0) > 0,
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "SERVICE",
                GLBatch.source_id == ServiceRequest.id,
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    missing_expenses = (
        db.session.query(func.count(Expense.id))
        .filter(
            Expense.customer_id == customer_id,
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "EXPENSE",
                GLBatch.source_id == Expense.id,
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    missing_split_gl = (
        db.session.query(func.count(PaymentSplit.id))
        .join(Payment, PaymentSplit.payment_id == Payment.id)
        .filter(
            Payment.customer_id == customer_id,
            Payment.status == "COMPLETED",
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "PAYMENT_SPLIT",
                GLBatch.source_id == PaymentSplit.id,
                GLBatch.purpose == "PAYMENT",
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    missing_payment_gl = (
        db.session.query(func.count(Payment.id))
        .filter(
            Payment.customer_id == customer_id,
            Payment.status == "COMPLETED",
            ~db.session.query(PaymentSplit.id).filter(PaymentSplit.payment_id == Payment.id).exists(),
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "PAYMENT",
                GLBatch.source_id == Payment.id,
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    return {
        "sales": int(missing_sales),
        "invoices": int(missing_invoices),
        "services": int(missing_services),
        "expenses": int(missing_expenses),
        "payment_splits": int(missing_split_gl),
        "payments": int(missing_payment_gl),
    }


def _missing_gl_for_supplier(supplier_id: int) -> dict:
    missing_expenses = (
        db.session.query(func.count(Expense.id))
        .filter(
            Expense.supplier_id == supplier_id,
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "EXPENSE",
                GLBatch.source_id == Expense.id,
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    missing_split_gl = (
        db.session.query(func.count(PaymentSplit.id))
        .join(Payment, PaymentSplit.payment_id == Payment.id)
        .filter(
            Payment.supplier_id == supplier_id,
            Payment.status == "COMPLETED",
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "PAYMENT_SPLIT",
                GLBatch.source_id == PaymentSplit.id,
                GLBatch.purpose == "PAYMENT",
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    missing_payment_gl = (
        db.session.query(func.count(Payment.id))
        .filter(
            Payment.supplier_id == supplier_id,
            Payment.status == "COMPLETED",
            ~db.session.query(PaymentSplit.id).filter(PaymentSplit.payment_id == Payment.id).exists(),
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "PAYMENT",
                GLBatch.source_id == Payment.id,
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    return {
        "expenses": int(missing_expenses),
        "payment_splits": int(missing_split_gl),
        "payments": int(missing_payment_gl),
    }


def _missing_gl_for_partner(partner_id: int) -> dict:
    missing_expenses = (
        db.session.query(func.count(Expense.id))
        .filter(
            Expense.partner_id == partner_id,
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "EXPENSE",
                GLBatch.source_id == Expense.id,
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    missing_split_gl = (
        db.session.query(func.count(PaymentSplit.id))
        .join(Payment, PaymentSplit.payment_id == Payment.id)
        .filter(
            Payment.partner_id == partner_id,
            Payment.status == "COMPLETED",
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "PAYMENT_SPLIT",
                GLBatch.source_id == PaymentSplit.id,
                GLBatch.purpose == "PAYMENT",
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    missing_payment_gl = (
        db.session.query(func.count(Payment.id))
        .filter(
            Payment.partner_id == partner_id,
            Payment.status == "COMPLETED",
            ~db.session.query(PaymentSplit.id).filter(PaymentSplit.payment_id == Payment.id).exists(),
            ~db.session.query(GLBatch.id)
            .filter(
                GLBatch.source_type == "PAYMENT",
                GLBatch.source_id == Payment.id,
                GLBatch.status == "POSTED",
            )
            .exists(),
        )
        .scalar()
        or 0
    )
    return {
        "expenses": int(missing_expenses),
        "payment_splits": int(missing_split_gl),
        "payments": int(missing_payment_gl),
    }


def _audit_integrity_summary(*, as_of_date: datetime.date) -> dict:
    as_of_dt = datetime.combine(as_of_date, datetime.max.time())
    ar_account = (GL_ACCOUNTS.get("AR") or "1100_AR").upper()
    ap_account = (GL_ACCOUNTS.get("AP") or "2000_AP").upper()
    return {
        "unbalanced_or_empty_posted_batches": int(
            _scalar(
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
            or 0
        ),
        "orphan_entries_count": int(
            _scalar(
                """
                SELECT COUNT(*)
                FROM gl_entries e
                LEFT JOIN gl_batches b ON b.id=e.batch_id
                WHERE b.id IS NULL
                """
            )
            or 0
        ),
        "splits_missing_payment_batch_count": int(
            _scalar(
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
            or 0
        ),
        "splits_missing_reversal_count": int(
            _scalar(
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
            or 0
        ),
        "posted_batches_missing_entity": int(
            _scalar(
                """
                SELECT COUNT(*)
                FROM gl_batches
                WHERE status='POSTED' AND posted_at <= :as_of_dt
                  AND (entity_type IS NULL OR entity_id IS NULL)
                """,
                {"as_of_dt": as_of_dt},
            )
            or 0
        ),
        "ar_unassigned_balance": float(
            _scalar(
                """
                SELECT COALESCE(SUM(e.debit - e.credit),0)
                FROM gl_entries e
                JOIN gl_batches b ON b.id = e.batch_id
                WHERE b.status='POSTED' AND b.posted_at <= :as_of_dt
                  AND e.account = :ar
                  AND (b.entity_type IS NULL OR b.entity_id IS NULL OR b.entity_type <> 'CUSTOMER')
                """,
                {"as_of_dt": as_of_dt, "ar": ar_account},
            )
            or 0
        ),
        "ap_unassigned_balance": float(
            _scalar(
                """
                SELECT COALESCE(SUM(e.credit - e.debit),0)
                FROM gl_entries e
                JOIN gl_batches b ON b.id = e.batch_id
                WHERE b.status='POSTED' AND b.posted_at <= :as_of_dt
                  AND e.account = :ap
                  AND (b.entity_type IS NULL OR b.entity_id IS NULL OR b.entity_type NOT IN ('SUPPLIER','PARTNER'))
                """,
                {"as_of_dt": as_of_dt, "ap": ap_account},
            )
            or 0
        ),
    }


def _build_entity_detail(*, entity_type: str, entity_id: int, as_of_date: datetime.date, include_components: bool) -> dict:
    etype = str(entity_type).upper()
    stored_balance = 0.0
    computed_balance = None
    computed_matches = None
    computed_diff = None
    components = None
    name = None
    if etype == "CUSTOMER":
        entity = db.session.get(Customer, int(entity_id))
        name = entity.name if entity else None
        stored_balance = float(getattr(entity, "current_balance", 0) or 0) if entity else 0.0
        from utils.balance_calculator import build_customer_balance_view
        view = build_customer_balance_view(int(entity_id), db.session)
        if view.get("success"):
            computed_balance = float(view.get("balance", {}).get("amount", 0))
            computed_matches = bool(view.get("balance", {}).get("matches_stored"))
            computed_diff = float(view.get("balance", {}).get("difference", 0))
            if include_components:
                components = view.get("components")
        missing_gl = _missing_gl_for_customer(int(entity_id))
    elif etype == "SUPPLIER":
        entity = db.session.get(Supplier, int(entity_id))
        name = entity.name if entity else None
        stored_balance = float(getattr(entity, "current_balance", 0) or 0) if entity else 0.0
        from utils.supplier_balance_updater import build_supplier_balance_view
        view = build_supplier_balance_view(int(entity_id), db.session)
        if view.get("success"):
            computed_balance = float(view.get("balance", {}).get("amount", 0))
            computed_matches = bool(view.get("balance", {}).get("matches_stored"))
            computed_diff = float(view.get("balance", {}).get("difference", 0))
            if include_components:
                components = view.get("components")
        missing_gl = _missing_gl_for_supplier(int(entity_id))
    else:
        entity = db.session.get(Partner, int(entity_id))
        name = entity.name if entity else None
        stored_balance = float(getattr(entity, "current_balance", 0) or 0) if entity else 0.0
        from utils.partner_balance_updater import build_partner_balance_view
        view = build_partner_balance_view(int(entity_id), db.session)
        if view.get("success"):
            computed_balance = float(view.get("balance", {}).get("amount", 0))
            computed_matches = bool(view.get("balance", {}).get("matches_stored"))
            computed_diff = float(view.get("balance", {}).get("difference", 0))
            if include_components:
                components = view.get("components")
        missing_gl = _missing_gl_for_partner(int(entity_id))

    gl_balance = _gl_balance_for_entity(entity_type=etype, entity_id=int(entity_id), as_of_date=as_of_date)
    expected_gl_from_stored = -stored_balance if etype == "CUSTOMER" else stored_balance
    expected_gl_from_computed = -computed_balance if etype == "CUSTOMER" and computed_balance is not None else computed_balance

    detail = {
        "entity_type": etype,
        "entity_id": int(entity_id),
        "name": name,
        "stored_balance": stored_balance,
        "computed_balance": computed_balance,
        "computed_matches_stored": computed_matches,
        "computed_difference": computed_diff,
        "gl_balance": float(gl_balance),
        "expected_gl_from_stored": float(expected_gl_from_stored),
        "expected_gl_from_computed": float(expected_gl_from_computed) if expected_gl_from_computed is not None else None,
        "gl_vs_stored_diff": float(gl_balance - expected_gl_from_stored),
        "gl_vs_computed_diff": float(gl_balance - expected_gl_from_computed) if expected_gl_from_computed is not None else None,
        "missing_gl_sources": missing_gl,
    }
    if include_components:
        detail["components"] = components
    return detail


def _audit_entity_details(*, target_ids: dict, as_of_date: datetime.date, include_components: bool, max_details: int) -> dict:
    out = {"customers": [], "suppliers": [], "partners": []}
    for cid in (target_ids.get("customers") or [])[:max_details]:
        out["customers"].append(_build_entity_detail(entity_type="CUSTOMER", entity_id=int(cid), as_of_date=as_of_date, include_components=include_components))
    for sid in (target_ids.get("suppliers") or [])[:max_details]:
        out["suppliers"].append(_build_entity_detail(entity_type="SUPPLIER", entity_id=int(sid), as_of_date=as_of_date, include_components=include_components))
    for pid in (target_ids.get("partners") or [])[:max_details]:
        out["partners"].append(_build_entity_detail(entity_type="PARTNER", entity_id=int(pid), as_of_date=as_of_date, include_components=include_components))
    return out


def run():
    args = sys.argv[1:]
    opts = {}
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            opts[k.strip()] = v.strip()
        else:
            opts[a.strip()] = True

    as_of_date = _as_date(opts.get("as_of_date"))
    override = _as_bool(opts.get("override"), False)
    include_archived = _as_bool(opts.get("include_archived"), False)
    max_batches = _as_int(opts.get("max_batches"), 5000)
    tolerance = _as_float(opts.get("tolerance"), 0.01)
    max_customers = _as_int(opts.get("max_customers"), 500)
    max_suppliers = _as_int(opts.get("max_suppliers"), 500)
    max_partners = _as_int(opts.get("max_partners"), 500)
    skip_backup = _as_bool(opts.get("skip_backup"), False)
    audit_only = _as_bool(opts.get("audit_only"), False)
    detailed = _as_bool(opts.get("detailed"), False)
    include_components = _as_bool(opts.get("include_components"), False)
    max_details = _as_int(opts.get("max_details"), 50)
    integrity_audit = _as_bool(opts.get("integrity_audit"), True)
    refresh_opening_balances = _as_bool(opts.get("refresh_opening_balances"), False)
    purge_orphan_invoices = _as_bool(opts.get("purge_orphan_invoices"), False)
    legacy_fx = _as_bool(opts.get("legacy_fx"), False)
    legacy_fx_dry_run = _as_bool(opts.get("legacy_fx_dry_run"), False)
    legacy_fx_force = _as_bool(opts.get("legacy_fx_force"), False)
    legacy_fx_limit = _as_int(opts.get("legacy_fx_limit"), 500)
    legacy_fx_from = _as_optional_date(opts.get("legacy_fx_from"))
    legacy_fx_to = _as_optional_date(opts.get("legacy_fx_to"))
    legacy_fx_types = _parse_str_set(opts.get("legacy_fx_types"))
    if not legacy_fx_types:
        legacy_fx_types = {"sales", "invoices", "services", "payments", "payment_splits"}
    rebuild_sales = _parse_id_list(opts.get("rebuild_sales"))
    rebuild_payment_splits = _parse_id_list(opts.get("rebuild_payment_splits"))
    rebuild_expenses = _parse_id_list(opts.get("rebuild_expenses"))

    app = create_app()
    with app.app_context():
        if not skip_backup and app.config.get("ENABLE_AUTOMATED_BACKUPS", True):
            ok, msg, path = perform_backup_db(app)
            print(f"backup: {ok} | {msg} | {path}")

        before = _find_mismatch_entity_ids(
            as_of_date=as_of_date,
            tolerance=tolerance,
            include_archived=include_archived,
            max_customers=max_customers,
            max_suppliers=max_suppliers,
            max_partners=max_partners,
        )
        print(json.dumps({"phase": "before", **before}, ensure_ascii=False))

        if integrity_audit:
            integrity_summary = _audit_integrity_summary(as_of_date=as_of_date)
            print(json.dumps({"phase": "integrity_summary", **integrity_summary}, ensure_ascii=False))

        if audit_only:
            if detailed:
                details = _audit_entity_details(
                    target_ids=before.get("target_ids", {}),
                    as_of_date=as_of_date,
                    include_components=include_components,
                    max_details=max_details,
                )
                print(json.dumps({"phase": "details", "entities": details}, ensure_ascii=False))
            return

        fixed = _fix_gl_entities(as_of_date=as_of_date, override=override, max_batches=max_batches)
        print(json.dumps({"phase": "fix_gl_entities", **fixed}, ensure_ascii=False))

        if purge_orphan_invoices:
            purged = _purge_orphan_invoice_gl()
            print(json.dumps({"phase": "purge_orphan_invoices", **purged}, ensure_ascii=False))

        if legacy_fx:
            plan = _legacy_fx_candidate_ids(
                from_date=legacy_fx_from,
                to_date=legacy_fx_to,
                limit=legacy_fx_limit,
                types=legacy_fx_types,
                force=legacy_fx_force,
            )
            plan_counts = {k: len(v) for k, v in plan.items()}
            print(
                json.dumps(
                    {
                        "phase": "legacy_fx_plan",
                        "dry_run": bool(legacy_fx_dry_run),
                        "force": bool(legacy_fx_force),
                        "from": legacy_fx_from.isoformat() if legacy_fx_from else None,
                        "to": legacy_fx_to.isoformat() if legacy_fx_to else None,
                        "limit": legacy_fx_limit,
                        "types": sorted(legacy_fx_types),
                        "counts": plan_counts,
                    },
                    ensure_ascii=False,
                )
            )
            if not legacy_fx_dry_run:
                fx_result = _apply_legacy_fx(plan=plan, force=legacy_fx_force, dry_run=False)
                print(json.dumps({"phase": "legacy_fx_apply", **fx_result}, ensure_ascii=False))
                rebuilt = {"sales": 0, "invoices": 0, "services": 0, "payments": 0, "payment_splits": 0}
                for sid in plan.get("sales") or []:
                    run_sale_gl_sync_after_commit(int(sid))
                    rebuilt["sales"] += 1
                for iid in plan.get("invoices") or []:
                    run_invoice_gl_sync_after_commit(int(iid))
                    rebuilt["invoices"] += 1
                for sid in plan.get("services") or []:
                    run_service_gl_sync_after_commit(int(sid))
                    rebuilt["services"] += 1
                for pid in plan.get("payments") or []:
                    run_payment_gl_sync_after_commit(int(pid))
                    rebuilt["payments"] += 1
                for sid in plan.get("payment_splits") or []:
                    with db.engine.connect() as conn:
                        with conn.begin():
                            _payment_split_gl_batch_upsert_by_id(conn, split_id=int(sid))
                    rebuilt["payment_splits"] += 1
                print(json.dumps({"phase": "legacy_fx_rebuild_gl", "rebuilt": rebuilt}, ensure_ascii=False))
            else:
                print(json.dumps({"phase": "legacy_fx_apply", "dry_run": True}, ensure_ascii=False))

        if rebuild_sales:
            for sid in rebuild_sales:
                run_sale_gl_sync_after_commit(int(sid))
            print(json.dumps({"phase": "rebuild_sales", "count": len(rebuild_sales)}, ensure_ascii=False))

        if rebuild_expenses:
            updated = 0
            for eid in rebuild_expenses:
                if run_expense_gl_sync_after_commit(int(eid)):
                    updated += 1
            print(json.dumps({"phase": "rebuild_expenses", "count": updated}, ensure_ascii=False))

        if rebuild_payment_splits:
            rebuilt = 0
            for sid in rebuild_payment_splits:
                with db.engine.connect() as conn:
                    with conn.begin():
                        _payment_split_gl_batch_upsert_by_id(conn, split_id=int(sid))
                rebuilt += 1
            print(json.dumps({"phase": "rebuild_payment_splits", "count": rebuilt}, ensure_ascii=False))

        if refresh_opening_balances:
            refreshed = _refresh_opening_balance_batches(target_ids=before.get("target_ids", {}))
            print(json.dumps({"phase": "refresh_opening_balances", **refreshed}, ensure_ascii=False))

        targets = _find_mismatch_entity_ids(
            as_of_date=as_of_date,
            tolerance=tolerance,
            include_archived=include_archived,
            max_customers=max_customers,
            max_suppliers=max_suppliers,
            max_partners=max_partners,
        )
        recalculated = _recalculate_entities(target_ids=targets.get("target_ids", {}))
        print(json.dumps({"phase": "recalculate", "recalculated": recalculated}, ensure_ascii=False))

        after = _find_mismatch_entity_ids(
            as_of_date=as_of_date,
            tolerance=tolerance,
            include_archived=include_archived,
            max_customers=max_customers,
            max_suppliers=max_suppliers,
            max_partners=max_partners,
        )
        print(json.dumps({"phase": "after", **after}, ensure_ascii=False))

        if detailed:
            details = _audit_entity_details(
                target_ids=after.get("target_ids", {}),
                as_of_date=as_of_date,
                include_components=include_components,
                max_details=max_details,
            )
            print(json.dumps({"phase": "details_after", "entities": details}, ensure_ascii=False))


if __name__ == "__main__":
    run()
