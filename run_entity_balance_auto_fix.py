import json
import sys
from datetime import datetime, timezone
from typing import Any

from app import create_app
from extensions import db, perform_backup_db
from models import (
    Customer,
    GLBatch,
    GLEntry,
    GL_ACCOUNTS,
    Partner,
    Supplier,
)
from services.ledger_service import SmartEntityExtractor
from sqlalchemy import func, or_


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
    partner_gl_sq = (
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

        fixed = _fix_gl_entities(as_of_date=as_of_date, override=override, max_batches=max_batches)
        print(json.dumps({"phase": "fix_gl_entities", **fixed}, ensure_ascii=False))

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


if __name__ == "__main__":
    run()
