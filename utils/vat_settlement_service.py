"""تسوية ضريبة القيمة المضافة — إقرار فترة."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func

from extensions import db
from models import TaxEntry, GLBatch, GLEntry, Account


def vat_settlement_for_period(start_dt: datetime, end_dt: datetime) -> dict:
    """مجموع مخرجات/مدخلات VAT من TaxEntry والـ GL."""
    output_q = (
        db.session.query(func.coalesce(func.sum(TaxEntry.tax_amount), 0))
        .filter(
            TaxEntry.entry_type == "OUTPUT",
            TaxEntry.created_at >= start_dt,
            TaxEntry.created_at <= end_dt,
        )
        .scalar()
    )
    input_q = (
        db.session.query(func.coalesce(func.sum(TaxEntry.tax_amount), 0))
        .filter(
            TaxEntry.entry_type == "INPUT",
            TaxEntry.created_at >= start_dt,
            TaxEntry.created_at <= end_dt,
        )
        .scalar()
    )
    output_vat = float(output_q or 0)
    input_vat = float(input_q or 0)
    net_payable = output_vat - input_vat

    gl_output = (
        db.session.query(func.coalesce(func.sum(GLEntry.credit - GLEntry.debit), 0))
        .join(GLBatch)
        .join(Account, Account.code == GLEntry.account)
        .filter(
            GLBatch.status == "POSTED",
            GLBatch.posted_at >= start_dt,
            GLBatch.posted_at <= end_dt,
            GLEntry.account.like("2200%"),
        )
        .scalar()
    )
    gl_input = (
        db.session.query(func.coalesce(func.sum(GLEntry.debit - GLEntry.credit), 0))
        .join(GLBatch)
        .filter(
            GLBatch.status == "POSTED",
            GLBatch.posted_at >= start_dt,
            GLBatch.posted_at <= end_dt,
            GLEntry.account.like("1500%"),
        )
        .scalar()
    )

    return {
        "output_vat_taxentry": round(output_vat, 2),
        "input_vat_taxentry": round(input_vat, 2),
        "net_payable": round(net_payable, 2),
        "gl_vat_payable_net": round(float(gl_output or 0), 2),
        "gl_vat_input_net": round(float(gl_input or 0), 2),
        "reconciled": abs(net_payable - float(gl_output or 0)) < 1.0,
    }
