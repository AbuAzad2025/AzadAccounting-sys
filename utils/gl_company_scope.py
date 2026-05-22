"""فلترة قيود GL حسب فروع الشركة."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_, select

from utils.company_scope import _sale_ids_in_branches, branch_ids_for_company


def resolve_branch_filter(company_id: Optional[int] = None) -> Optional[List[int]]:
    """None = كل الفروع، [] = لا شيء، list = فروع محددة."""
    if company_id:
        return branch_ids_for_company(company_id)
    return None


def gl_batch_branch_clause(branch_ids: List[int]):
    """شرط SQLAlchemy على GLBatch حسب الفرع."""
    from models import GLBatch, Expense, PurchaseOrder, Shipment, Warehouse, Invoice, Sale

    sale_ids = _sale_ids_in_branches(branch_ids)
    cust_ids = select(Sale.customer_id).filter(
        Sale.id.in_(sale_ids), Sale.customer_id.isnot(None)
    ).distinct()
    invoice_via_sale = select(Invoice.id).filter(
        or_(Invoice.sale_id.in_(sale_ids), Invoice.customer_id.in_(cust_ids))
    )
    expense_ids = select(Expense.id).where(Expense.branch_id.in_(branch_ids))
    po_ids = select(PurchaseOrder.id).where(PurchaseOrder.branch_id.in_(branch_ids))
    ship_ids = (
        select(Shipment.id)
        .join(Warehouse, Warehouse.id == Shipment.destination_id)
        .where(Warehouse.branch_id.in_(branch_ids))
    )
    return or_(
        and_(GLBatch.source_type == "SALE", GLBatch.source_id.in_(sale_ids)),
        and_(GLBatch.source_type == "INVOICE", GLBatch.source_id.in_(invoice_via_sale)),
        and_(
            GLBatch.source_type.in_(("EXPENSE", "EXPENSE_PAYMENT", "PAYROLL")),
            GLBatch.source_id.in_(expense_ids),
        ),
        and_(GLBatch.source_type == "PURCHASE_ORDER", GLBatch.source_id.in_(po_ids)),
        and_(GLBatch.source_type == "SHIPMENT", GLBatch.source_id.in_(ship_ids)),
    )


def gl_entries_base(branch_filter_ids: Optional[List[int]], start_dt: datetime, end_dt: datetime):
    """استعلام أساسي: GLEntry + GLBatch + Account مع فترة واختيار فروع."""
    from models import GLBatch, GLEntry, Account

    q = (
        GLEntry.query.join(GLBatch, GLBatch.id == GLEntry.batch_id)
        .join(Account, Account.code == GLEntry.account)
        .filter(
            GLBatch.status == "POSTED",
            GLBatch.posted_at >= start_dt,
            GLBatch.posted_at <= end_dt,
        )
    )
    if branch_filter_ids is not None:
        if not branch_filter_ids:
            return q.filter(GLEntry.id == -1)
        q = q.filter(gl_batch_branch_clause(branch_filter_ids))
    return q
