"""
رصيد العميل قبل تاريخ — نفس صيغة الرصيد المخزّن (حقوق − التزامات + افتتاحي).
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, or_, and_

from extensions import db
from utils.accounting_formulas import (
    customer_balance_from_components,
    customer_obligations_total,
    customer_rights_total,
)
from utils.balance_calculator import calculate_customer_balance_components, convert_amount


def _opening_ils(customer) -> Decimal:
    opening = Decimal(str(customer.opening_balance or 0))
    if customer.currency and str(customer.currency).upper() != "ILS":
        try:
            opening = convert_amount(opening, customer.currency, "ILS", customer.created_at)
        except Exception:
            pass
    return opening


def customer_components_since(customer_id: int, since_date: datetime, session=None) -> dict:
    """مكونات الحركات من since_date حتى الآن (لطرحها من الرصيد الحالي)."""
    from models import (
        Sale,
        SaleReturn,
        Invoice,
        ServiceRequest,
        ServicePart,
        ServiceTask,
        PreOrder,
        OnlinePreOrder,
        Payment,
        PaymentSplit,
        Check,
        Expense,
        ExpenseType,
    )
    from sqlalchemy import case

    if not session:
        session = db.session

    result = {k: Decimal("0.00") for k in (
        "sales_balance", "returns_balance", "invoices_balance", "services_balance",
        "preorders_balance", "online_orders_balance", "payments_in_balance",
        "payments_out_balance", "returned_checks_in_balance", "returned_checks_out_balance",
        "expenses_balance", "service_expenses_balance",
    )}

    def _sum_ils(model, date_col, amount_col, extra=None):
        filters = [getattr(model, "customer_id") == customer_id, getattr(date_col) >= since_date]
        if extra:
            filters.extend(extra)
        val = session.query(func.coalesce(func.sum(getattr(model, amount_col)), 0)).filter(
            *filters, getattr(model, "currency") == "ILS"
        ).scalar() or 0
        return Decimal(str(val))

    result["sales_balance"] = _sum_ils(Sale, Sale.sale_date, Sale.total_amount, [Sale.status == "CONFIRMED"])

    inv_filters = [
        Invoice.cancelled_at.is_(None),
        Invoice.sale_id.is_(None),
        Invoice.service_id.is_(None),
        Invoice.preorder_id.is_(None),
    ]
    result["invoices_balance"] = _sum_ils(Invoice, Invoice.invoice_date, Invoice.total_amount, inv_filters)

    result["returns_balance"] = _sum_ils(SaleReturn, SaleReturn.created_at, SaleReturn.total_amount, [SaleReturn.status == "CONFIRMED"])

    # services (same parts/tasks logic as balance_calculator — simplified: completed_at >= since)
    part_gross = func.coalesce(ServicePart.quantity, 0) * func.coalesce(ServicePart.unit_price, 0)
    part_disc = func.coalesce(ServicePart.discount, 0)
    part_taxable = case((part_gross - part_disc < 0, 0), else_=(part_gross - part_disc))
    part_tax = part_taxable * (func.coalesce(ServicePart.tax_rate, 0) / 100.0)
    part_total_expr = part_taxable + part_tax
    task_gross = func.coalesce(ServiceTask.quantity, 1) * func.coalesce(ServiceTask.unit_price, 0)
    task_disc = func.coalesce(ServiceTask.discount, 0)
    task_taxable = case((task_gross - task_disc < 0, 0), else_=(task_gross - task_disc))
    task_tax = task_taxable * (func.coalesce(ServiceTask.tax_rate, 0) / 100.0)
    task_total_expr = task_taxable + task_tax

    svc_filters = [
        ServiceRequest.customer_id == customer_id,
        ServiceRequest.completed_at.isnot(None),
        ServiceRequest.completed_at >= since_date,
    ]
    parts_sum = session.query(func.coalesce(func.sum(part_total_expr), 0)).join(
        ServiceRequest, ServiceRequest.id == ServicePart.service_id
    ).filter(*svc_filters, ServiceRequest.currency == "ILS").scalar() or 0
    tasks_sum = session.query(func.coalesce(func.sum(task_total_expr), 0)).join(
        ServiceRequest, ServiceRequest.id == ServiceTask.service_id
    ).filter(*svc_filters, ServiceRequest.currency == "ILS").scalar() or 0
    result["services_balance"] = Decimal(str(parts_sum)) + Decimal(str(tasks_sum))

    open_po = session.query(PreOrder).filter(
        PreOrder.customer_id == customer_id,
        PreOrder.cancelled_at.is_(None),
        PreOrder.status.in_(["PENDING", "CONFIRMED"]),
        PreOrder.preorder_date >= since_date,
    ).all()
    for po in open_po:
        try:
            bd = Decimal(str(po.balance_due or 0))
            if po.currency and po.currency != "ILS":
                bd = convert_amount(bd, po.currency, "ILS", po.preorder_date)
            result["preorders_balance"] += bd
        except Exception:
            pass

    result["online_orders_balance"] = _sum_ils(
        OnlinePreOrder, OnlinePreOrder.created_at, OnlinePreOrder.total_amount,
        [OnlinePreOrder.payment_status != "CANCELLED"],
    )

    payment_customer = or_(
        Payment.customer_id == customer_id,
        Sale.customer_id == customer_id,
        Invoice.customer_id == customer_id,
        ServiceRequest.customer_id == customer_id,
        PreOrder.customer_id == customer_id,
    )
    pay_base = [
        payment_customer,
        Payment.payment_date >= since_date,
        Payment.status == "COMPLETED",
        Payment.expense_id.is_(None),
    ]
    result["payments_in_balance"] = Decimal(str(
        session.query(func.coalesce(func.sum(Payment.total_amount), 0))
        .outerjoin(Sale, Payment.sale_id == Sale.id)
        .outerjoin(Invoice, Payment.invoice_id == Invoice.id)
        .outerjoin(ServiceRequest, Payment.service_id == ServiceRequest.id)
        .outerjoin(PreOrder, Payment.preorder_id == PreOrder.id)
        .filter(*pay_base, Payment.direction == "IN")
        .scalar() or 0
    ))
    result["payments_out_balance"] = Decimal(str(
        session.query(func.coalesce(func.sum(Payment.total_amount), 0))
        .outerjoin(Sale, Payment.sale_id == Sale.id)
        .outerjoin(Invoice, Payment.invoice_id == Invoice.id)
        .outerjoin(ServiceRequest, Payment.service_id == ServiceRequest.id)
        .outerjoin(PreOrder, Payment.preorder_id == PreOrder.id)
        .filter(*pay_base, Payment.direction == "OUT")
        .scalar() or 0
    ))

    return result


def calculate_balance_before_date(customer_id, before_date, session=None) -> Decimal:
    """رصيد تراكمي قبل تاريخ — مطابق لصيغة الرصيد المخزّن."""
    from models import Customer

    if not session:
        session = db.session
    customer = session.get(Customer, customer_id)
    if not customer:
        return Decimal("0.00")

    opening = _opening_ils(customer)
    comp_all = calculate_customer_balance_components(customer_id, session)
    if not comp_all:
        return opening

    balance_now = customer_balance_from_components(opening, comp_all)
    since = customer_components_since(customer_id, before_date, session)
    delta = customer_rights_total(since) - customer_obligations_total(since)
    return balance_now - delta
