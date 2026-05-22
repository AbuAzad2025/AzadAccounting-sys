"""فواتير الموردين وترحيل GL."""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from extensions import db
from models import (
    GL_ACCOUNTS,
    SupplierInvoice,
    SupplierInvoiceLine,
    PurchaseOrder,
    _gl_upsert_batch_and_entries,
    _ensure_account_exists,
)


def _next_si_number() -> str:
    n = SupplierInvoice.query.count() + 1
    return f"SINV-{datetime.now().year}-{n:05d}"


def create_from_purchase_order(po: PurchaseOrder, *, vat_rate: float = 16.0) -> SupplierInvoice:
    if po.status not in ("PARTIAL", "RECEIVED"):
        raise ValueError("أمر الشراء يجب أن يكون مستلماً جزئياً أو كلياً")
    existing = SupplierInvoice.query.filter_by(
        purchase_order_id=po.id, status="POSTED"
    ).first()
    if existing:
        return existing
    subtotal = Decimal("0")
    lines_data = []
    for ln in po.lines:
        qty = Decimal(str(ln.received_qty or 0))
        if qty <= 0:
            continue
        price = Decimal(str(ln.unit_price or 0))
        line_total = qty * price
        subtotal += line_total
        lines_data.append((ln, qty, price, line_total))
    if not lines_data:
        raise ValueError("لا كميات مستلمة لفوترة")
    vat = (subtotal * Decimal(str(vat_rate)) / Decimal("100")).quantize(Decimal("0.01"))
    inv = SupplierInvoice(
        number=_next_si_number(),
        supplier_id=po.supplier_id,
        purchase_order_id=po.id,
        branch_id=po.branch_id,
        invoice_date=date.today(),
        status="DRAFT",
        currency=po.currency or "ILS",
        subtotal=subtotal,
        vat_amount=vat,
        total_amount=subtotal + vat,
        notes=f"من أمر شراء {po.number}",
    )
    db.session.add(inv)
    db.session.flush()
    for ln, qty, price, _ in lines_data:
        db.session.add(
            SupplierInvoiceLine(
                supplier_invoice_id=inv.id,
                product_id=ln.product_id,
                description=ln.product.name if ln.product else None,
                quantity=qty,
                unit_price=price,
            )
        )
    return inv


def post_supplier_invoice_gl(invoice_id: int) -> int:
    inv = db.session.get(SupplierInvoice, invoice_id)
    if not inv:
        raise ValueError("فاتورة غير موجودة")
    if inv.status == "POSTED":
        return 0
    total = float(inv.total_amount or 0)
    sub = float(inv.subtotal or 0)
    vat = float(inv.vat_amount or 0)
    if total <= 0:
        raise ValueError("مبلغ الفاتورة صفر")
    ap = GL_ACCOUNTS.get("AP", "2000_AP")
    inv_accrual = GL_ACCOUNTS.get("PURCHASES", "5000_PURCHASES")
    vat_in = GL_ACCOUNTS.get("VAT_INPUT", "1500_VAT_INPUT")
    conn = db.session.connection()
    _ensure_account_exists(conn, ap)
    _ensure_account_exists(conn, inv_accrual)
    if vat > 0:
        _ensure_account_exists(conn, vat_in)
    entries = [(ap, 0.0, total)]
    entries.append((inv_accrual, sub, 0.0))
    if vat > 0:
        entries.append((vat_in, vat, 0.0))
    batch_id = _gl_upsert_batch_and_entries(
        conn,
        source_type="SUPPLIER_INVOICE",
        source_id=inv.id,
        purpose="SUPPLIER_INVOICE",
        currency=inv.currency or "ILS",
        memo=f"فاتورة مورد {inv.number}",
        entries=entries,
        ref=inv.number,
        entity_type="SUPPLIER",
        entity_id=inv.supplier_id,
        branch_id=inv.branch_id,
    )
    inv.status = "POSTED"
    db.session.commit()
    return int(batch_id)
