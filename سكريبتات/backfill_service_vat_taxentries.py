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


def _parse_ym(s: str | None) -> tuple[int, int] | None:
    raw = (str(s or "").strip() or "")
    if not raw:
        return None
    if "-" not in raw:
        return None
    y, m = raw.split("-", 1)
    try:
        yy = int(str(y).strip())
        mm = int(str(m).strip())
    except Exception:
        return None
    if mm < 1 or mm > 12:
        return None
    return yy, mm


def run() -> None:
    from app import create_app
    from extensions import db
    from models import ServicePart, ServiceRequest, ServiceTask, SystemSettings, TaxEntry, _recalc_service_request_totals
    from sqlalchemy import delete as sa_delete, insert as sa_insert, update as sa_update
    from sqlalchemy.orm import selectinload
    from datetime import datetime, timedelta, timezone

    dry_run = str(os.getenv("DRY_RUN", "") or "").strip().lower() in ("1", "true", "yes", "on")
    strip_vat = str(os.getenv("STRIP_VAT", "") or "").strip().lower() in ("1", "true", "yes", "on")
    force = str(os.getenv("FORCE", "") or "").strip().lower() in ("1", "true", "yes", "on")
    from_period = _parse_ym(os.getenv("FROM_PERIOD"))
    to_period = _parse_ym(os.getenv("TO_PERIOD"))

    app = create_app()
    with app.app_context():
        vat_enabled = bool(SystemSettings.get_setting("vat_enabled", False))
        if strip_vat and vat_enabled and not force:
            print("STRIP_VAT requested but VAT is enabled. Set FORCE=1 to override. No changes applied.")
            return
        if not strip_vat:
            try:
                vat_rate = float(SystemSettings.get_setting("default_vat_rate", 0.0) or 0.0)
            except Exception:
                vat_rate = 0.0
            if vat_enabled and vat_rate <= 0:
                vat_rate = 16.0
            if not vat_enabled or vat_rate <= 0:
                print("VAT is disabled or default rate is invalid. No changes applied.")
                return

        q = (
            ServiceRequest.query.options(selectinload(ServiceRequest.parts), selectinload(ServiceRequest.tasks))
            .order_by(ServiceRequest.id)
        )

        if from_period:
            fy, fm = from_period
            q = q.filter(ServiceRequest.received_at >= datetime(fy, fm, 1))
        if to_period:
            ty, tm = to_period
            if tm == 12:
                end_dt = datetime(ty + 1, 1, 1) - timedelta(microseconds=1)
            else:
                end_dt = datetime(ty, tm + 1, 1) - timedelta(microseconds=1)
            q = q.filter(ServiceRequest.received_at <= end_dt)

        conn = db.session.connection()
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        scanned = 0
        skipped = 0
        totals_recalc = 0
        stripped = 0
        tax_entries_written = 0

        for sr in q.yield_per(200):
            scanned += 1
            status_raw = getattr(sr.status, "value", sr.status)
            status_str = str(status_raw or "").strip()
            status_norm = status_str.upper()

            if getattr(sr, "cancelled_at", None):
                skipped += 1
                continue
            if status_norm != "COMPLETED" and status_str.lower() != "completed":
                skipped += 1
                continue

            _recalc_service_request_totals(sr)
            totals_recalc += 1

            service_date = getattr(sr, "received_at", None) or now
            currency = (getattr(sr, "currency", None) or "ILS").upper()

            base_amount = _d(getattr(sr, "total_amount", 0) or 0).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            if base_amount <= Decimal("0.00"):
                skipped += 1
                continue

            tax_rate = _d(getattr(sr, "tax_rate", 0) or 0)
            if strip_vat:
                has_line_tax = False
                for p in (getattr(sr, "parts", None) or []):
                    if _d(getattr(p, "tax_rate", 0) or 0) > Decimal("0"):
                        has_line_tax = True
                        break
                if not has_line_tax:
                    for t in (getattr(sr, "tasks", None) or []):
                        if _d(getattr(t, "tax_rate", 0) or 0) > Decimal("0"):
                            has_line_tax = True
                            break
                if tax_rate <= Decimal("0") and not has_line_tax:
                    skipped += 1
                    continue

                conn.execute(
                    sa_update(ServiceRequest)
                    .where(ServiceRequest.id == int(sr.id))
                    .values(tax_rate=0, updated_at=now)
                )
                conn.execute(sa_update(ServicePart).where(ServicePart.service_id == int(sr.id)).values(tax_rate=0))
                conn.execute(sa_update(ServiceTask).where(ServiceTask.service_id == int(sr.id)).values(tax_rate=0))

                conn.execute(
                    sa_delete(TaxEntry).where(
                        TaxEntry.transaction_type == "SERVICE",
                        TaxEntry.transaction_id == int(sr.id),
                    )
                )
                try:
                    from models import GLBatch, GLEntry
                    from sqlalchemy import delete as sa_delete2, select as sa_select
                    bad_batch_ids = conn.execute(
                        sa_select(GLBatch.id).where(
                            GLBatch.source_type == "SERVICE",
                            GLBatch.source_id == int(sr.id),
                            GLBatch.purpose == "SERVICE_COMPLETE",
                            GLBatch.status == "POSTED",
                        )
                    ).scalars().all()
                    for bid in bad_batch_ids:
                        conn.execute(sa_delete2(GLEntry).where(GLEntry.batch_id == int(bid)))
                        conn.execute(sa_delete2(GLBatch).where(GLBatch.id == int(bid)))
                except Exception:
                    pass
                stripped += 1
                continue
            else:
                if tax_rate <= Decimal("0"):
                    skipped += 1
                    continue

            tax_amount = (base_amount * tax_rate / Decimal("100")).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
            if tax_amount <= Decimal("0.00"):
                skipped += 1
                continue

            total_amount = (base_amount + tax_amount).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

            conn.execute(
                sa_delete(TaxEntry).where(
                    TaxEntry.transaction_type == "SERVICE",
                    TaxEntry.transaction_id == int(sr.id),
                )
            )
            conn.execute(
                sa_insert(TaxEntry).values(
                    entry_type="OUTPUT_VAT",
                    transaction_type="SERVICE",
                    transaction_id=int(sr.id),
                    transaction_reference=getattr(sr, "service_number", None),
                    tax_rate=float(tax_rate),
                    base_amount=float(base_amount),
                    tax_amount=float(tax_amount),
                    total_amount=float(total_amount),
                    currency=currency,
                    fiscal_year=int(getattr(service_date, "year", now.year)),
                    fiscal_month=int(getattr(service_date, "month", now.month)),
                    tax_period=f"{int(getattr(service_date, 'year', now.year))}-{int(getattr(service_date, 'month', now.month)):02d}",
                    customer_id=int(getattr(sr, "customer_id", 0) or 0) or None,
                    notes=f"صيانة: {getattr(sr, 'service_number', None) or sr.id}",
                    created_at=now,
                )
            )
            tax_entries_written += 1

            if scanned % 500 == 0:
                if dry_run:
                    db.session.rollback()
                    print("DRY_RUN checkpoint rollback at", scanned)
                else:
                    db.session.commit()
                    print("checkpoint committed at", scanned)

        if dry_run:
            db.session.rollback()
            print("DRY_RUN rollback done.")
        else:
            db.session.commit()
            print("OK committed.")

        print("scanned", scanned)
        print("skipped", skipped)
        print("totals_recalculated", totals_recalc)
        if strip_vat:
            print("stripped_services_tax_to_zero", stripped)
        print("tax_entries_written", tax_entries_written)


if __name__ == "__main__":
    run()
