from __future__ import annotations

import os
import sys
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP


TWOPLACES = Decimal("0.01")

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _d(x) -> Decimal:
    try:
        return Decimal(str(x or 0))
    except Exception:
        return Decimal("0")


def run() -> None:
    from app import create_app
    from extensions import db
    from models import Sale, SaleLine, SaleStatus, SystemSettings, TaxEntry
    from sqlalchemy import delete as sa_delete, func, insert as sa_insert, select, update
    from datetime import datetime, timezone

    dry_run = str(os.getenv("DRY_RUN", "") or "").strip().lower() in ("1", "true", "yes", "on")

    app = create_app()
    with app.app_context():
        vat_enabled = bool(SystemSettings.get_setting("vat_enabled", False))
        try:
            vat_rate = float(SystemSettings.get_setting("default_vat_rate", 0.0) or 0.0)
        except Exception:
            vat_rate = 0.0
        if vat_enabled and vat_rate <= 0:
            vat_rate = 16.0

        conn = db.session.connection()
        now = datetime.now(timezone.utc)

        touched = 0
        confirmed = 0
        skipped_cancelled = 0
        vat_applied = 0
        tax_entries_written = 0

        q = (
            db.session.query(
                Sale.id,
                Sale.sale_number,
                Sale.sale_date,
                Sale.customer_id,
                Sale.currency,
                Sale.tax_rate,
                Sale.discount_total,
                Sale.shipping_cost,
                Sale.total_paid,
                Sale.status,
            )
            .order_by(Sale.id)
        )

        for row in q.yield_per(200):
            sid = int(row.id)
            status = (getattr(row.status, "value", None) or row.status or "").upper()
            if status in ("CANCELLED", "REFUNDED"):
                skipped_cancelled += 1
                continue

            sale_date = row.sale_date or now
            currency = (row.currency or "ILS").upper()
            tax_rate = float(row.tax_rate or 0)
            if vat_enabled and tax_rate <= 0:
                tax_rate = float(vat_rate)
                vat_applied += 1

            subtotal_float = (
                conn.execute(
                    select(
                        func.coalesce(
                            func.sum(
                                (SaleLine.quantity * SaleLine.unit_price)
                                * (1 - (func.coalesce(SaleLine.discount_rate, 0) / 100.0))
                            ),
                            0.0,
                        )
                    ).where(SaleLine.sale_id == sid)
                ).scalar_one()
                or 0.0
            )
            subtotal = _d(subtotal_float)
            discount = _d(row.discount_total)
            shipping = _d(row.shipping_cost)
            paid = _d(row.total_paid)

            base_for_tax = subtotal - discount + shipping
            if base_for_tax < 0:
                base_for_tax = Decimal("0")
            tax_amount = (base_for_tax * _d(tax_rate) / Decimal("100")).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            total_amount = (base_for_tax + tax_amount).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            balance_due = (total_amount - paid).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

            conn.execute(
                update(Sale)
                .where(Sale.id == sid)
                .values(
                    status=SaleStatus.CONFIRMED.value,
                    tax_rate=tax_rate,
                    total_amount=float(total_amount),
                    balance_due=float(balance_due),
                    updated_at=now,
                )
            )
            touched += 1
            if status != "CONFIRMED":
                confirmed += 1

            conn.execute(
                sa_delete(TaxEntry).where(
                    TaxEntry.transaction_type == "SALE",
                    TaxEntry.transaction_id == sid,
                )
            )
            if vat_enabled and tax_rate > 0 and total_amount > 0:
                conn.execute(
                    sa_insert(TaxEntry).values(
                        entry_type="OUTPUT_VAT",
                        transaction_type="SALE",
                        transaction_id=sid,
                        transaction_reference=row.sale_number,
                        tax_rate=float(tax_rate),
                        base_amount=float(base_for_tax.quantize(TWOPLACES, rounding=ROUND_HALF_UP)),
                        tax_amount=float(tax_amount),
                        total_amount=float(total_amount),
                        currency=currency,
                        fiscal_year=int(getattr(sale_date, "year", now.year)),
                        fiscal_month=int(getattr(sale_date, "month", now.month)),
                        tax_period=f"{int(getattr(sale_date, 'year', now.year))}-{int(getattr(sale_date, 'month', now.month)):02d}",
                        customer_id=int(row.customer_id) if row.customer_id is not None else None,
                        notes=f"بيع: {row.sale_number or sid}",
                        created_at=now,
                    )
                )
                tax_entries_written += 1

            if touched % 500 == 0:
                if dry_run:
                    db.session.rollback()
                    print("DRY_RUN checkpoint rollback at", touched)
                else:
                    db.session.commit()
                    print("checkpoint committed at", touched)

        if dry_run:
            db.session.rollback()
            print("DRY_RUN rollback done.")
        else:
            db.session.commit()
            print("OK committed.")

        print("touched", touched)
        print("confirmed_changed", confirmed)
        print("skipped_cancelled_or_refunded", skipped_cancelled)
        print("vat_applied_to_zero_rate", vat_applied)
        print("tax_entries_written", tax_entries_written)


if __name__ == "__main__":
    run()
