import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import Expense, GLBatch, UtilityAccount, Supplier, ExpenseType
from sqlalchemy import or_


UTILITY_RULES = [
    {"utility_type": "ELECTRICITY", "provider": "شركة كهرباء محافظة القدس", "keywords": ["شركة كهرباء محافظة القدس", "فاتورة كهرباء", "كهرباء"]},
    {"utility_type": "WATER", "provider": "مصلحة المياه", "keywords": ["مصلحة المياه", "فاتورة مياه", "مياه"]},
]
SUPPLIER_RULES = [
    {"supplier_name": "شركة الاتصالات الفلسطينية للانترنت", "keywords": ["شركة الاتصالات الفلسطينية", "الاتصالات الفلسطينية", "فاتورة انترنت", "فاتورة إنترنت", "الانترنت", "إنترنت"]},
    {"supplier_name": "شركة جوال", "keywords": ["شركة جوال", "جوال", "فاتورة جوال", "فواتير الجوال"]},
]


def _norm(text):
    return (text or "").strip().lower()


def _detect_utility(exp):
    fields = [
        exp.description,
        exp.payee_name,
        exp.paid_to,
        exp.beneficiary_name,
        exp.notes,
    ]
    merged = " ".join([f for f in fields if f])
    if not merged:
        return None
    m = _norm(merged)
    for rule in UTILITY_RULES:
        for kw in rule["keywords"]:
            if _norm(kw) in m:
                return rule
    return None


def _detect_supplier(exp):
    fields = [
        exp.description,
        exp.payee_name,
        exp.paid_to,
        exp.beneficiary_name,
        exp.notes,
    ]
    merged = " ".join([f for f in fields if f])
    if not merged:
        return None
    m = _norm(merged)
    for rule in SUPPLIER_RULES:
        for kw in rule["keywords"]:
            if _norm(kw) in m:
                return rule
    return None


def _ensure_utility(rule, created, dry_run):
    existing = UtilityAccount.query.filter_by(utility_type=rule["utility_type"], provider=rule["provider"]).first()
    if existing:
        return existing
    if dry_run:
        return None
    ua = UtilityAccount(utility_type=rule["utility_type"], provider=rule["provider"], alias=rule["provider"])
    db.session.add(ua)
    db.session.flush()
    created.append({"id": ua.id, "utility_type": ua.utility_type, "provider": ua.provider})
    return ua


def _ensure_supplier(rule, created, dry_run):
    existing = Supplier.query.filter_by(name=rule["supplier_name"]).first()
    if existing:
        return existing
    if dry_run:
        return None
    s = Supplier(name=rule["supplier_name"])
    db.session.add(s)
    db.session.flush()
    created.append({"id": s.id, "name": s.name})
    return s


def _ensure_type_supplier(type_name, created, dry_run):
    name = f"حساب مصروف - {type_name}".strip()
    existing = Supplier.query.filter_by(name=name).first()
    if existing:
        return existing
    if dry_run:
        return None
    s = Supplier(name=name)
    db.session.add(s)
    db.session.flush()
    created.append({"id": s.id, "name": s.name})
    return s


def run(dry_run=True):
    app = create_app()
    results = {
        "dry_run": dry_run,
        "created_utilities": [],
        "created_suppliers": [],
        "updated_expenses": [],
        "skipped_expenses": 0,
    }
    with app.app_context():
        q = Expense.query.order_by(Expense.id.asc())
        expenses = q.all()
        for exp in expenses:
            if exp.customer_id or exp.supplier_id or exp.partner_id or exp.employee_id:
                results["skipped_expenses"] += 1
                continue
            payee_type = (exp.payee_type or "").strip().upper()
            if payee_type in {"SUPPLIER", "PARTNER", "CUSTOMER", "EMPLOYEE"} and exp.payee_entity_id:
                results["skipped_expenses"] += 1
                continue
            rule = _detect_utility(exp)
            if rule:
                ua = _ensure_utility(rule, results["created_utilities"], dry_run)
                if dry_run and not ua:
                    results["updated_expenses"].append({"expense_id": exp.id, "entity_type": "UTILITY", "name": rule["provider"], "status": "would_update"})
                    continue
                if not ua:
                    continue
                exp.utility_account_id = ua.id
                exp.payee_type = "UTILITY"
                exp.payee_entity_id = ua.id
                exp.payee_name = ua.alias or ua.provider
                b = GLBatch.query.filter_by(source_type="EXPENSE", source_id=exp.id).first()
                if b:
                    b.entity_type = "UTILITY"
                    b.entity_id = ua.id
                results["updated_expenses"].append({"expense_id": exp.id, "entity_type": "UTILITY", "name": ua.provider, "status": "updated"})
                continue
            s_rule = _detect_supplier(exp)
            if not s_rule:
                exp_type = db.session.get(ExpenseType, exp.type_id) if exp.type_id else None
                type_name = (exp_type.name if exp_type else "") or ""
                if not type_name:
                    results["skipped_expenses"] += 1
                    continue
                sup = _ensure_type_supplier(type_name, results["created_suppliers"], dry_run)
                if dry_run and not sup:
                    results["updated_expenses"].append({"expense_id": exp.id, "entity_type": "SUPPLIER", "name": f"حساب مصروف - {type_name}", "status": "would_update"})
                    continue
                if not sup:
                    continue
                exp.supplier_id = sup.id
                exp.payee_type = "SUPPLIER"
                exp.payee_entity_id = sup.id
                exp.payee_name = sup.name
                b = GLBatch.query.filter_by(source_type="EXPENSE", source_id=exp.id).first()
                if b:
                    b.entity_type = "SUPPLIER"
                    b.entity_id = sup.id
                results["updated_expenses"].append({"expense_id": exp.id, "entity_type": "SUPPLIER", "name": sup.name, "status": "updated"})
                continue
            sup = _ensure_supplier(s_rule, results["created_suppliers"], dry_run)
            if dry_run and not sup:
                results["updated_expenses"].append({"expense_id": exp.id, "entity_type": "SUPPLIER", "name": s_rule["supplier_name"], "status": "would_update"})
                continue
            if not sup:
                continue
            exp.supplier_id = sup.id
            exp.payee_type = "SUPPLIER"
            exp.payee_entity_id = sup.id
            exp.payee_name = sup.name
            b = GLBatch.query.filter_by(source_type="EXPENSE", source_id=exp.id).first()
            if b:
                b.entity_type = "SUPPLIER"
                b.entity_id = sup.id
            results["updated_expenses"].append({"expense_id": exp.id, "entity_type": "SUPPLIER", "name": sup.name, "status": "updated"})
        if not dry_run:
            db.session.commit()
    return results


def main():
    dry_run = True
    if "--apply" in sys.argv:
        dry_run = False
    if "--dry-run" in sys.argv:
        dry_run = True
    res = run(dry_run=dry_run)
    print(res)


if __name__ == "__main__":
    main()
