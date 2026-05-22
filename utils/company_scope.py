"""نطاق الشركة/الفرع للمستخدم والتقارير — قاعدة واحدة بدون tenants."""
from __future__ import annotations

from typing import List, Optional, Set

from flask_login import current_user
from sqlalchemy import and_, exists, or_, select


def get_accessible_branch_ids() -> Optional[List[int]]:
    """None = كل الفروع (مدير)، وإلا قائمة معرفات."""
    try:
        import utils
        if utils.is_super() or utils.is_admin():
            return None
    except Exception:
        pass
    try:
        u = current_user
        if not u or not getattr(u, "is_authenticated", False):
            return []
        links = getattr(u, "user_branches", None) or []
        ids = [int(ub.branch_id) for ub in links if getattr(ub, "branch_id", None)]
        return ids or []
    except Exception:
        return []


def get_accessible_company_ids() -> Optional[List[int]]:
    from extensions import db
    from models import Branch

    branch_ids = get_accessible_branch_ids()
    if branch_ids is None:
        return None
    if not branch_ids:
        return []
    rows = (
        db.session.query(Branch.company_id)
        .filter(Branch.id.in_(branch_ids), Branch.company_id.isnot(None))
        .distinct()
        .all()
    )
    return list({int(r[0]) for r in rows if r[0]})


def branch_ids_for_company(company_id: Optional[int]) -> Optional[List[int]]:
    """فروع شركة معيّنة؛ None = بدون فلتر شركة (كل الفروع المتاحة للمستخدم)."""
    from models import Branch

    if not company_id:
        return get_accessible_branch_ids()
    q = Branch.query.filter_by(company_id=int(company_id), is_active=True)
    allowed = get_accessible_branch_ids()
    if allowed is not None:
        q = q.filter(Branch.id.in_(allowed))
    return [b.id for b in q.all()]


def filter_by_branches(query, branch_column):
    ids = get_accessible_branch_ids()
    if ids is None:
        return query
    if not ids:
        return query.filter(branch_column == -1)
    return query.filter(branch_column.in_(ids))


def _sale_ids_in_branches(branch_ids: List[int]):
    from extensions import db
    from models import Sale, SaleLine, Warehouse

    return (
        db.session.query(SaleLine.sale_id)
        .join(Warehouse, Warehouse.id == SaleLine.warehouse_id)
        .filter(Warehouse.branch_id.in_(branch_ids), SaleLine.sale_id.isnot(None))
        .distinct()
    )


def filter_sales_query(query):
    """قيود المبيعات حسب مستودعات الفروع المتاحة."""
    ids = get_accessible_branch_ids()
    if ids is None:
        return query
    if not ids:
        from models import Sale
        return query.filter(Sale.id == -1)
    from models import Sale
    sub = _sale_ids_in_branches(ids).subquery()
    return query.filter(Sale.id.in_(select(sub.c.sale_id)))


def filter_customers_query(query):
    """عملاء لهم نشاط (مبيعات) في فروع المستخدم."""
    ids = get_accessible_branch_ids()
    if ids is None:
        return query
    if not ids:
        from models import Customer
        return query.filter(Customer.id == -1)
    from extensions import db
    from models import Customer, Sale

    customer_ids_q = (
        db.session.query(Sale.customer_id)
        .filter(
            Sale.id.in_(_sale_ids_in_branches(ids)),
            Sale.customer_id.isnot(None),
        )
        .distinct()
    )
    return query.filter(Customer.id.in_(customer_ids_q))


def filter_payments_query(query):
    """دفعات مرتبطة بفروع المستخدم (مبيعة/شحنة/مصروف)."""
    ids = get_accessible_branch_ids()
    if ids is None:
        return query
    if not ids:
        from models import Payment
        return query.filter(Payment.id == -1)

    from models import Payment, Sale, Shipment, Warehouse, Expense

    sale_sub = _sale_ids_in_branches(ids).subquery()
    shipment_branch = (
        select(Shipment.id)
        .join(Warehouse, Warehouse.id == Shipment.destination_id)
        .where(Warehouse.branch_id.in_(ids))
    )
    clauses = [
        Payment.sale_id.in_(select(sale_sub.c.sale_id)),
        Payment.expense.has(Expense.branch_id.in_(ids)),
        Payment.shipment_id.in_(shipment_branch),
    ]
    # دفعات على عميل له مبيعات في الفرع
    customer_in_branch = (
        select(Sale.customer_id)
        .filter(Sale.id.in_(select(sale_sub.c.sale_id)), Sale.customer_id.isnot(None))
        .distinct()
    )
    clauses.append(
        and_(
            Payment.customer_id.isnot(None),
            Payment.customer_id.in_(customer_in_branch),
            Payment.sale_id.is_(None),
            Payment.invoice_id.is_(None),
        )
    )
    return query.filter(or_(*clauses))


def filter_shipments_query(query):
    """شحنات مخزن الوجهة ضمن فروع المستخدم."""
    ids = get_accessible_branch_ids()
    if ids is None:
        return query
    if not ids:
        from models import Shipment
        return query.filter(Shipment.id == -1)
    from models import Shipment, Warehouse

    wh_ids = (
        Warehouse.query.filter(Warehouse.branch_id.in_(ids))
        .with_entities(Warehouse.id)
    )
    return query.filter(Shipment.destination_id.in_(wh_ids))


def default_company():
    from models import Company

    return Company.query.filter_by(is_active=True).order_by(Company.id.asc()).first()
