from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from extensions import db
from models import (
    Customer,
    Invoice,
    Payment,
    PaymentDirection,
    PaymentMethod,
    PaymentSplit,
    PaymentStatus,
    PreOrder,
    Sale,
    ServiceRequest,
    run_payment_gl_sync_after_commit,
)
from utils import q0


def _dec(v) -> Decimal:
    try:
        return q0(Decimal(str(v or 0)))
    except Exception:
        return Decimal("0")


def _now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _has_check_like(payment: Payment) -> bool:
    try:
        if getattr(payment, "check_number", None) or getattr(payment, "check_bank", None):
            return True
    except Exception:
        pass
    try:
        rc = getattr(payment, "related_check", None)
        if rc is not None:
            return True
    except Exception:
        pass
    try:
        for sp in (getattr(payment, "splits", None) or []):
            m = getattr(sp, "method", None)
            m = getattr(m, "value", m)
            m = str(m or "").upper()
            if "CHECK" in m or "CHEQUE" in m:
                return True
    except Exception:
        pass
    return False


def _ensure_default_split(payment: Payment) -> None:
    if getattr(payment, "splits", None):
        return
    sp = PaymentSplit(
        payment_id=getattr(payment, "id", None),
        method=getattr(payment.method, "value", payment.method) or PaymentMethod.CASH.value,
        amount=q0(_dec(payment.total_amount)),
        details={"auto_created": True},
        currency=(getattr(payment, "currency", None) or "ILS").upper(),
        converted_amount=q0(_dec(payment.total_amount)),
        converted_currency=(getattr(payment, "currency", None) or "ILS").upper(),
    )
    db.session.add(sp)


def _split_payment_amount(payment: Payment, keep_amount: Decimal) -> Payment | None:
    total = q0(_dec(payment.total_amount))
    keep = q0(_dec(keep_amount))
    if keep <= 0 or keep >= total:
        return None
    if _has_check_like(payment):
        return None

    remainder_amount = q0(total - keep)
    remainder = Payment(
        entity_type="CUSTOMER",
        customer_id=payment.customer_id,
        direction=payment.direction,
        status=payment.status,
        payment_date=payment.payment_date,
        total_amount=remainder_amount,
        currency=payment.currency,
        method=payment.method,
        reference=payment.reference,
        receipt_number=None,
        notes=payment.notes,
        deliverer_name=getattr(payment, "deliverer_name", None),
        receiver_name=getattr(payment, "receiver_name", None),
        created_by=getattr(payment, "created_by", None),
    )
    db.session.add(remainder)
    db.session.flush()

    splits = list(getattr(payment, "splits", None) or [])
    if not splits:
        _ensure_default_split(payment)
        db.session.flush()
        splits = list(getattr(payment, "splits", None) or [])

    ratio = keep / total if total > 0 else Decimal("0")
    for sp in splits:
        sp_amt = q0(_dec(getattr(sp, "amount", 0)))
        sp_conv = q0(_dec(getattr(sp, "converted_amount", sp_amt)))
        keep_sp_amt = q0(sp_amt * ratio)
        keep_sp_conv = q0(sp_conv * ratio)
        rem_sp_amt = q0(sp_amt - keep_sp_amt)
        rem_sp_conv = q0(sp_conv - keep_sp_conv)

        sp.amount = keep_sp_amt
        sp.converted_amount = keep_sp_conv
        db.session.add(sp)

        if rem_sp_amt > 0:
            rsp = PaymentSplit(
                payment_id=remainder.id,
                method=getattr(sp.method, "value", sp.method),
                amount=rem_sp_amt,
                details=(sp.details or {}),
                currency=sp.currency,
                converted_amount=rem_sp_conv,
                converted_currency=getattr(sp, "converted_currency", None) or sp.currency,
                fx_rate_used=getattr(sp, "fx_rate_used", None),
                fx_rate_source=getattr(sp, "fx_rate_source", None),
                fx_rate_timestamp=getattr(sp, "fx_rate_timestamp", None),
                fx_base_currency=getattr(sp, "fx_base_currency", None),
                fx_quote_currency=getattr(sp, "fx_quote_currency", None),
            )
            db.session.add(rsp)

    payment.total_amount = keep
    db.session.add(payment)
    return remainder


def _open_customer_obligations(customer_id: int):
    obligations = []

    try:
        rows = (
            ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.is_archived == False,
                ServiceRequest.cancelled_at.is_(None),
                ServiceRequest.balance_due > 0.01,
            )
            .order_by(ServiceRequest.received_at.asc(), ServiceRequest.id.asc())
            .all()
        )
        for r in rows:
            dtv = getattr(r, "received_at", None) or getattr(r, "created_at", None)
            obligations.append(("SERVICE", dtv, r.id, q0(_dec(getattr(r, "balance_due", 0)))))
    except Exception:
        pass

    try:
        rows = (
            PreOrder.query.filter(
                PreOrder.customer_id == customer_id,
                PreOrder.cancelled_at.is_(None),
                PreOrder.balance_due > 0.01,
            )
            .order_by(PreOrder.preorder_date.asc(), PreOrder.id.asc())
            .all()
        )
        for r in rows:
            dtv = getattr(r, "preorder_date", None) or getattr(r, "created_at", None)
            obligations.append(("PREORDER", dtv, r.id, q0(_dec(getattr(r, "balance_due", 0)))))
    except Exception:
        pass

    try:
        rows = (
            Sale.query.filter(
                Sale.customer_id == customer_id,
                Sale.balance_due > 0.01,
                Sale.is_archived == False,
                Sale.cancelled_at.is_(None),
            )
            .order_by(Sale.sale_date.asc(), Sale.id.asc())
            .all()
        )
        for r in rows:
            dtv = getattr(r, "sale_date", None)
            obligations.append(("SALE", dtv, r.id, q0(_dec(getattr(r, "balance_due", 0)))))
    except Exception:
        pass

    try:
        rows = (
            Invoice.query.filter(
                Invoice.customer_id == customer_id,
                Invoice.cancelled_at.is_(None),
                (Invoice.total_amount - Invoice.total_paid) > 0.01,
                Invoice.sale_id.is_(None),
                Invoice.service_id.is_(None),
                Invoice.preorder_id.is_(None),
            )
            .order_by(Invoice.invoice_date.asc(), Invoice.id.asc())
            .all()
        )
        for r in rows:
            dtv = getattr(r, "invoice_date", None)
            due = q0(_dec(getattr(r, "total_amount", 0)) - _dec(getattr(r, "total_paid", 0)))
            obligations.append(("INVOICE", dtv, r.id, due))
    except Exception:
        pass

    obligations = [o for o in obligations if o[3] > 0]
    obligations.sort(key=lambda x: (x[1] or datetime.min.replace(tzinfo=None), x[0], x[2]))
    return obligations


def apply_customer_credit_to_obligations(customer_id: int, *, created_by: int | None = None) -> list[int]:
    if not customer_id:
        return []

    touched_payment_ids: list[int] = []

    customer = db.session.get(Customer, int(customer_id))
    if not customer:
        return []

    obligations = _open_customer_obligations(int(customer_id))
    if not obligations:
        return []

    credit_payments = (
        Payment.query.filter(
            Payment.customer_id == int(customer_id),
            Payment.direction == PaymentDirection.IN.value,
            Payment.status == PaymentStatus.COMPLETED.value,
            Payment.sale_id.is_(None),
            Payment.invoice_id.is_(None),
            Payment.service_id.is_(None),
            Payment.preorder_id.is_(None),
            Payment.expense_id.is_(None),
            Payment.shipment_id.is_(None),
            Payment.supplier_id.is_(None),
            Payment.partner_id.is_(None),
            Payment.loan_settlement_id.is_(None),
            Payment.is_archived == False,
        )
        .order_by(Payment.payment_date.asc(), Payment.id.asc())
        .all()
    )

    def _assign_payment(p: Payment, kind: str, oid: int):
        if kind == "SALE":
            p.sale_id = oid
            p.entity_type = "SALE"
        elif kind == "SERVICE":
            p.service_id = oid
            p.entity_type = "SERVICE"
        elif kind == "PREORDER":
            p.preorder_id = oid
            p.entity_type = "PREORDER"
        else:
            p.invoice_id = oid
            p.entity_type = "INVOICE"
        p.customer_id = None
        db.session.add(p)

    for kind, _dtv, oid, due in obligations:
        remaining_due = q0(_dec(due))
        while remaining_due > 0 and credit_payments:
            p = credit_payments[0]
            amt = q0(_dec(p.total_amount))
            if amt <= 0:
                credit_payments.pop(0)
                continue
            if amt <= remaining_due + Decimal("0.0001"):
                _assign_payment(p, kind, int(oid))
                touched_payment_ids.append(int(p.id))
                credit_payments.pop(0)
                remaining_due = q0(remaining_due - amt)
                continue

            remainder = _split_payment_amount(p, remaining_due)
            _assign_payment(p, kind, int(oid))
            touched_payment_ids.append(int(p.id))
            if remainder is not None:
                credit_payments[0] = remainder
            else:
                credit_payments.pop(0)
            remaining_due = Decimal("0")

    opening_credit = q0(_dec(getattr(customer, "opening_balance", 0)))
    if opening_credit > 0 and (getattr(customer, "currency", "ILS") or "ILS").upper() == "ILS":
        for kind, _dtv, oid, due in obligations:
            if opening_credit <= 0:
                break
            need = q0(_dec(due))
            if need <= 0:
                continue
            apply_amt = need if need <= opening_credit else q0(opening_credit)
            if apply_amt <= 0:
                continue

            p = Payment(
                direction=PaymentDirection.IN.value,
                status=PaymentStatus.COMPLETED.value,
                payment_date=_now_naive(),
                total_amount=apply_amt,
                currency="ILS",
                method=PaymentMethod.BANK.value,
                reference="تسديد من رصيد سابق",
                notes="[CREDIT_APPLIED=true]",
                created_by=created_by,
            )
            p._skip_gl_entry = True
            if kind == "SALE":
                p.entity_type = "SALE"
                p.sale_id = int(oid)
            elif kind == "SERVICE":
                p.entity_type = "SERVICE"
                p.service_id = int(oid)
            elif kind == "PREORDER":
                p.entity_type = "PREORDER"
                p.preorder_id = int(oid)
            else:
                p.entity_type = "INVOICE"
                p.invoice_id = int(oid)
            db.session.add(p)
            db.session.flush()
            sp = PaymentSplit(
                payment_id=p.id,
                method=p.method,
                amount=apply_amt,
                details={"credit_applied": True},
                currency="ILS",
                converted_amount=apply_amt,
                converted_currency="ILS",
            )
            db.session.add(sp)
            touched_payment_ids.append(int(p.id))
            opening_credit = q0(opening_credit - apply_amt)

        customer.opening_balance = opening_credit
        db.session.add(customer)

    db.session.commit()
    for pid in touched_payment_ids:
        try:
            run_payment_gl_sync_after_commit(int(pid))
        except Exception:
            pass
    return touched_payment_ids
