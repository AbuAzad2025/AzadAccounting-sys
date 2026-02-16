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
    from models import OnlinePreOrder, Sale, SaleLine, SaleStatus, SystemSettings, TaxEntry
    from sqlalchemy import delete as sa_delete, func, insert as sa_insert, select, update
    from datetime import datetime, timezone

    dry_run = str(os.getenv("DRY_RUN", "") or "").strip().lower() in ("1", "true", "yes", "on")
    strip_vat = str(os.getenv("STRIP_VAT", "") or "").strip().lower() in ("1", "true", "yes", "on")
    force = str(os.getenv("FORCE", "") or "").strip().lower() in ("1", "true", "yes", "on")

    app = create_app()
    with app.app_context():
        vat_enabled = bool(SystemSettings.get_setting("vat_enabled", False))
        if strip_vat and vat_enabled and not force:
            print("STRIP_VAT requested but VAT is enabled. Set FORCE=1 to override. No changes applied.")
            return

        conn = db.session.connection()
        now = datetime.now(timezone.utc)

        touched = 0
        touched_sale_ids: list[int] = []
        confirmed = 0
        skipped_cancelled = 0
        stripped = 0
        stripped_online_preorders = 0
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
            status_to_store = getattr(row.status, "value", row.status)
            if status in ("CANCELLED", "REFUNDED"):
                skipped_cancelled += 1
                continue

            sale_date = row.sale_date or now
            currency = (row.currency or "ILS").upper()
            tax_rate = float(row.tax_rate or 0)

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
            effective_tax_rate = 0.0 if strip_vat else tax_rate
            tax_amount = (base_for_tax * _d(effective_tax_rate) / Decimal("100")).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            total_amount = (base_for_tax + tax_amount).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            balance_due = (total_amount - paid).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

            conn.execute(
                update(Sale)
                .where(Sale.id == sid)
                .values(
                    status=SaleStatus.CONFIRMED.value if not strip_vat else status_to_store,
                    tax_rate=effective_tax_rate,
                    total_amount=float(total_amount),
                    balance_due=float(balance_due),
                    updated_at=now,
                )
            )
            touched += 1
            touched_sale_ids.append(sid)
            if not strip_vat and status != "CONFIRMED":
                confirmed += 1
            if strip_vat and tax_rate > 0:
                stripped += 1

            if strip_vat:
                conn.execute(
                    sa_delete(TaxEntry).where(
                        TaxEntry.transaction_type == "SALE",
                        TaxEntry.transaction_id == sid,
                    )
                )
                conn.execute(update(SaleLine).where(SaleLine.sale_id == sid).values(tax_rate=0))
            else:
                if vat_enabled and tax_rate > 0 and total_amount > 0:
                    conn.execute(
                        sa_delete(TaxEntry).where(
                            TaxEntry.transaction_type == "SALE",
                            TaxEntry.transaction_id == sid,
                        )
                    )
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

        if strip_vat:
            op_ids = [
                int(x)
                for (x,) in conn.execute(
                    select(OnlinePreOrder.id).where(
                        (func.coalesce(OnlinePreOrder.tax_rate, 0) > 0)
                        | (func.coalesce(OnlinePreOrder.tax_amount, 0) > 0)
                    )
                ).all()
            ]
            if op_ids:
                conn.execute(
                    update(OnlinePreOrder)
                    .where(OnlinePreOrder.id.in_(op_ids))
                    .values(
                        tax_rate=0,
                        tax_amount=0,
                        total_amount=func.coalesce(
                            OnlinePreOrder.base_amount,
                            func.coalesce(OnlinePreOrder.total_amount, 0) - func.coalesce(OnlinePreOrder.tax_amount, 0),
                        ),
                        updated_at=now,
                    )
                )
                conn.execute(
                    sa_delete(TaxEntry).where(
                        TaxEntry.transaction_type == "ONLINE_PREORDER",
                        TaxEntry.transaction_id.in_(op_ids),
                    )
                )
                try:
                    from models import GLBatch, GLEntry, GL_ACCOUNTS
                    from sqlalchemy import delete as sa_delete2
                    ar_account = (GL_ACCOUNTS.get("AR", "1100_AR") or "1100_AR").upper()
                    sales_account = (GL_ACCOUNTS.get("SALES", "4000_SALES") or "4000_SALES").upper()
                    op_rows = conn.execute(
                        select(OnlinePreOrder.id, OnlinePreOrder.order_number, OnlinePreOrder.total_amount).where(OnlinePreOrder.id.in_(op_ids))
                    ).all()
                    for oid, order_number, total_amount in op_rows:
                        amt = float(total_amount or 0)
                        if amt <= 0:
                            continue
                        bids = conn.execute(
                            select(GLBatch.id).where(
                                GLBatch.source_id == int(oid),
                                GLBatch.status == "POSTED",
                                GLBatch.source_type.in_(["ONLINE_PREORDER", "ONLINE_ORDER"]),
                            )
                        ).scalars().all()
                        for bid in bids:
                            conn.execute(sa_delete2(GLEntry).where(GLEntry.batch_id == int(bid)))
                            conn.execute(
                                sa_insert(GLEntry).values(
                                    batch_id=int(bid),
                                    account=ar_account,
                                    debit=amt,
                                    credit=0.0,
                                    ref=f"Online Order {order_number or oid}",
                                )
                            )
                            conn.execute(
                                sa_insert(GLEntry).values(
                                    batch_id=int(bid),
                                    account=sales_account,
                                    debit=0.0,
                                    credit=amt,
                                    ref=f"Online Sales {order_number or oid}",
                                )
                            )
                except Exception:
                    pass
                stripped_online_preorders = len(op_ids)

        if dry_run:
            db.session.rollback()
            print("DRY_RUN rollback done.")
        else:
            db.session.commit()
            print("OK committed.")
            try:
                from extensions import db as _db
                from models import Sale as _Sale, _sale_gl_upsert_core
                from sqlalchemy.orm import Session, joinedload
                from sqlalchemy import select as sa_select2

                def _sync_sales_gl(ids: list[int]) -> None:
                    if not ids:
                        return
                    s = Session(_db.engine)
                    try:
                        for sid in ids:
                            sale = s.execute(
                                sa_select2(_Sale).options(joinedload(_Sale.customer)).where(_Sale.id == int(sid))
                            ).unique().scalar_one_or_none()
                            if not sale:
                                continue
                            _sale_gl_upsert_core(s.connection(), sale)
                        s.commit()
                    finally:
                        s.close()

                if touched_sale_ids:
                    chunk = 200
                    done = 0
                    total = len(touched_sale_ids)
                    for i in range(0, total, chunk):
                        _sync_sales_gl(touched_sale_ids[i : i + chunk])
                        done = min(i + chunk, total)
                        if done % 1000 == 0 or done == total:
                            print("gl_synced_sales", done, "of", total)
            except Exception:
                pass

        print("touched", touched)
        if strip_vat:
            print("stripped_sales_tax_rate_to_zero", stripped)
            print("stripped_online_preorders_tax_to_zero", stripped_online_preorders)
        else:
            print("confirmed_changed", confirmed)
        print("skipped_cancelled_or_refunded", skipped_cancelled)
        print("tax_entries_written", tax_entries_written)


if __name__ == "__main__":
    run()
