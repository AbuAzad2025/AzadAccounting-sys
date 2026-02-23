import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime, date
from calendar import monthrange

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _parse_ym(value):
    if not value:
        return None
    parts = str(value).strip().split("-")
    if len(parts) != 2:
        raise ValueError("Invalid YYYY-MM")
    year = int(parts[0])
    month = int(parts[1])
    if month < 1 or month > 12:
        raise ValueError("Invalid month")
    return year, month


def _iter_months(start, end):
    y, m = start
    ey, em = end
    while (y < ey) or (y == ey and m <= em):
        yield y, m
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1


def _normalize_method(raw):
    from models import PaymentMethod
    key = str(raw or "").strip().replace(" ", "_").replace("-", "_").upper()
    key = {
        "BANK_TRANSFER": "BANK",
        "CHECK": "CHEQUE",
        "CREDIT_CARD": "CARD",
        "OTHER": "CASH",
    }.get(key, key)
    for m in PaymentMethod:
        if m.name == key or str(m.value).upper() == key:
            return m.value
    return PaymentMethod.BANK.value


def run(dry_run=True, start_ym=None, end_ym=None, employee_id=None, payment_method=None, payment_date=None):
    from app import create_app
    from extensions import db
    from models import (
        Employee,
        Expense,
        ExpenseType,
        Payment,
        PaymentStatus,
        PaymentDirection,
        PaymentEntityType,
        EmployeeAdvanceInstallment,
    )
    from routes.payments import _ensure_payment_number
    from routes.expenses import run_expense_gl_sync_after_commit, run_payment_gl_sync_after_commit
    from sqlalchemy import extract as sql_extract, or_, and_

    app = create_app()
    with app.app_context():
        salary_type = ExpenseType.query.filter_by(code="SALARY").first()
        if not salary_type:
            print("ERROR: SALARY type not found")
            return {"created": 0, "skipped": 0, "errors": 1}

        today = date.today()
        start = start_ym or (today.year, today.month)
        end = end_ym or start
        if (start[0], start[1]) > (end[0], end[1]):
            start, end = end, start

        method_value = _normalize_method(payment_method or "bank")

        employees_q = Employee.query.order_by(Employee.name)
        if employee_id:
            employees_q = employees_q.filter(Employee.id == int(employee_id))
        employees = employees_q.all()

        created = 0
        skipped = 0
        errors = 0
        created_expense_ids = []

        for emp in employees:
            for year, month in _iter_months(start, end):
                period_start = date(year, month, 1)
                last_day = monthrange(year, month)[1]
                period_end = date(year, month, last_day)
                existing = Expense.query.filter(
                    Expense.employee_id == emp.id,
                    Expense.type_id == salary_type.id,
                    or_(
                        Expense.period_start == period_start,
                        and_(
                            sql_extract("month", Expense.date) == month,
                            sql_extract("year", Expense.date) == year,
                        ),
                    ),
                ).first()
                if existing:
                    skipped += 1
                    continue

                prior_unpaid = Expense.query.filter(
                    Expense.employee_id == emp.id,
                    Expense.type_id == salary_type.id,
                    Expense.is_paid.is_(False),
                    or_(
                        Expense.period_start < period_start,
                        and_(
                            Expense.period_start.is_(None),
                            Expense.date < datetime.combine(period_start, datetime.min.time()),
                        ),
                    ),
                ).first()
                if prior_unpaid:
                    skipped += 1
                    continue

                base_salary = Decimal(str(emp.salary or 0))
                deductions = Decimal(str(emp.total_deductions or 0))
                social_ins = Decimal(str(emp.social_insurance_employee_amount or 0))
                net_before = base_salary - deductions - social_ins

                installments = EmployeeAdvanceInstallment.query.filter(
                    EmployeeAdvanceInstallment.employee_id == emp.id,
                    EmployeeAdvanceInstallment.paid == False,
                    EmployeeAdvanceInstallment.due_date >= period_start,
                    EmployeeAdvanceInstallment.due_date <= period_end,
                ).all()
                advances_total = sum(Decimal(str(inst.amount or 0)) for inst in installments)
                net_salary = net_before - advances_total

                if net_salary <= 0:
                    skipped += 1
                    continue
                if not emp.branch_id:
                    skipped += 1
                    continue

                pay_date = None
                if payment_date:
                    try:
                        pay_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
                    except Exception:
                        pay_date = None
                if not pay_date:
                    pay_date = period_end
                if pay_date > date.today():
                    skipped += 1
                    continue

                description = f"راتب شهر {month}/{year} - {emp.name}"
                notes = "تم توليد الراتب تلقائياً بواسطة سكريبت الرواتب المعلقة"

                if dry_run:
                    created += 1
                    continue

                try:
                    exp = Expense(
                        date=pay_date,
                        amount=net_salary,
                        currency=emp.currency,
                        type_id=salary_type.id,
                        employee_id=emp.id,
                        branch_id=emp.branch_id,
                        site_id=emp.site_id,
                        period_start=period_start,
                        period_end=period_end,
                        payment_method=method_value,
                        description=description,
                        notes=notes,
                        paid_to=emp.name,
                        beneficiary_name=emp.name,
                        payee_type="EMPLOYEE",
                        payee_entity_id=emp.id,
                        payee_name=emp.name,
                        disbursed_by="SCRIPT",
                    )
                    db.session.add(exp)
                    db.session.flush()

                    payment = Payment(
                        payment_date=pay_date,
                        total_amount=net_salary,
                        currency=emp.currency,
                        method=method_value,
                        status=PaymentStatus.COMPLETED.value,
                        direction=PaymentDirection.OUT.value,
                        entity_type=PaymentEntityType.EXPENSE.value,
                        expense_id=exp.id,
                        reference=f"دفع راتب {month}/{year} - {emp.name}",
                        notes=notes,
                        receiver_name=emp.name,
                        created_by=None,
                    )
                    _ensure_payment_number(payment)
                    db.session.add(payment)

                    for inst in installments:
                        inst.paid = True
                        inst.paid_date = pay_date
                        inst.paid_in_salary_expense_id = exp.id

                    created += 1
                    created_expense_ids.append(exp.id)
                except Exception:
                    db.session.rollback()
                    errors += 1

        if dry_run:
            print("DRY-RUN created:", created, "skipped:", skipped, "errors:", errors)
            return {"created": created, "skipped": skipped, "errors": errors}

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            errors += 1
            print("ERROR commit failed")
            return {"created": created, "skipped": skipped, "errors": errors}

        for exp_id in created_expense_ids:
            try:
                run_expense_gl_sync_after_commit(exp_id)
            except Exception:
                pass

        try:
            payment_ids = [
                r[0]
                for r in db.session.query(Payment.id)
                .filter(Payment.expense_id.in_(created_expense_ids))
                .filter(Payment.status == PaymentStatus.COMPLETED.value)
                .filter(Payment.direction == PaymentDirection.OUT.value)
                .all()
            ]
            for pid in payment_ids:
                try:
                    run_payment_gl_sync_after_commit(pid)
                except Exception:
                    pass
        except Exception:
            pass

        print("created:", created, "skipped:", skipped, "errors:", errors)
        return {"created": created, "skipped": skipped, "errors": errors}


def cleanup_future_salary_payments(dry_run=True, cutoff_date=None):
    from app import create_app
    from extensions import db
    from models import (
        Expense,
        ExpenseType,
        Payment,
        PaymentSplit,
        PaymentStatus,
        EmployeeAdvanceInstallment,
        GLBatch,
        GLEntry,
    )
    from sqlalchemy import delete as sa_delete, or_

    app = create_app()
    with app.app_context():
        salary_type = ExpenseType.query.filter_by(code="SALARY").first()
        if not salary_type:
            print("ERROR: SALARY type not found")
            return {"payments": 0, "expenses": 0, "installments": 0}

        cutoff = cutoff_date or date.today()
        salary_expense_ids = [
            r[0]
            for r in db.session.query(Expense.id)
            .filter(Expense.type_id == salary_type.id)
            .filter(Expense.date.isnot(None))
            .filter(Expense.date > cutoff)
            .all()
        ]

        payment_rows = (
            db.session.query(Payment.id, Payment.expense_id)
            .join(Expense, Payment.expense_id == Expense.id)
            .filter(Expense.type_id == salary_type.id)
            .filter(
                or_(
                    Payment.payment_date > cutoff,
                    Expense.date > cutoff,
                )
            )
            .filter(Payment.status.in_([PaymentStatus.COMPLETED.value, PaymentStatus.PENDING.value]))
            .all()
        )
        payment_ids = [r[0] for r in payment_rows]
        payment_expense_ids = [r[1] for r in payment_rows if r[1]]
        target_expense_ids = sorted(set(salary_expense_ids) | set(payment_expense_ids))

        inst_q = db.session.query(EmployeeAdvanceInstallment.id).filter(
            EmployeeAdvanceInstallment.paid_in_salary_expense_id.in_(target_expense_ids)
        )
        installment_ids = [r[0] for r in inst_q.all()]

        result = {
            "payments": len(payment_ids),
            "expenses": len(target_expense_ids),
            "installments": len(installment_ids),
        }

        if dry_run:
            print("DRY-RUN cleanup:", result)
            return result

        if installment_ids:
            db.session.query(EmployeeAdvanceInstallment).filter(
                EmployeeAdvanceInstallment.id.in_(installment_ids)
            ).update(
                {
                    EmployeeAdvanceInstallment.paid: False,
                    EmployeeAdvanceInstallment.paid_date: None,
                    EmployeeAdvanceInstallment.paid_in_salary_expense_id: None,
                },
                synchronize_session=False,
            )

        split_ids = [
            r[0]
            for r in db.session.query(PaymentSplit.id)
            .filter(PaymentSplit.payment_id.in_(payment_ids))
            .all()
        ]

        if split_ids:
            batch_ids = [
                r[0]
                for r in db.session.query(GLBatch.id)
                .filter(GLBatch.source_type == "PAYMENT_SPLIT")
                .filter(GLBatch.source_id.in_(split_ids))
                .all()
            ]
            if batch_ids:
                db.session.execute(sa_delete(GLEntry).where(GLEntry.batch_id.in_(batch_ids)))
                db.session.execute(sa_delete(GLBatch).where(GLBatch.id.in_(batch_ids)))
            db.session.execute(sa_delete(PaymentSplit).where(PaymentSplit.id.in_(split_ids)))

        if payment_ids:
            batch_ids = [
                r[0]
                for r in db.session.query(GLBatch.id)
                .filter(GLBatch.source_type == "PAYMENT")
                .filter(GLBatch.source_id.in_(payment_ids))
                .all()
            ]
            if batch_ids:
                db.session.execute(sa_delete(GLEntry).where(GLEntry.batch_id.in_(batch_ids)))
                db.session.execute(sa_delete(GLBatch).where(GLBatch.id.in_(batch_ids)))
            db.session.execute(sa_delete(Payment).where(Payment.id.in_(payment_ids)))

        db.session.commit()
        print("CLEANUP DONE:", result)
        return result


def fix_legacy_salary_tax(dry_run=True, start_ym=None, end_ym=None, employee_id=None, update_payments=False):
    from app import create_app
    from extensions import db
    from models import (
        Employee,
        Expense,
        ExpenseType,
        Payment,
        PaymentStatus,
        PaymentDirection,
        EmployeeAdvanceInstallment,
    )
    from routes.expenses import run_expense_gl_sync_after_commit, run_payment_gl_sync_after_commit
    from sqlalchemy import or_

    app = create_app()
    with app.app_context():
        salary_type = ExpenseType.query.filter_by(code="SALARY").first()
        if not salary_type:
            print("ERROR: SALARY type not found")
            return {"updated": 0, "skipped": 0, "ambiguous": 0, "errors": 1, "payments_updated": 0}

        today = date.today()
        start = start_ym or (2000, 1)
        end = end_ym or (today.year, today.month)
        if (start[0], start[1]) > (end[0], end[1]):
            start, end = end, start

        start_date = date(start[0], start[1], 1)
        end_last = monthrange(end[0], end[1])[1]
        end_date = date(end[0], end[1], end_last)

        q = Expense.query.filter(Expense.type_id == salary_type.id)
        q = q.filter(
            or_(
                Expense.date.between(start_date, end_date),
                Expense.period_start.between(start_date, end_date),
            )
        )
        if employee_id:
            q = q.filter(Expense.employee_id == int(employee_id))

        updated = 0
        skipped = 0
        ambiguous = 0
        errors = 0
        payments_updated = 0
        updated_expense_ids = []
        updated_payment_ids = []

        for exp in q.order_by(Expense.id).yield_per(200):
            try:
                if not exp.employee_id:
                    skipped += 1
                    continue
                emp = db.session.get(Employee, exp.employee_id)
                if not emp:
                    skipped += 1
                    continue

                base_salary = Decimal(str(emp.salary or 0))
                deductions = Decimal(str(emp.total_deductions or 0))
                social_ins = Decimal(str(emp.social_insurance_employee_amount or 0))
                income_tax = Decimal(str(emp.income_tax_amount or 0))

                advances_total = Decimal("0")
                inst_rows = EmployeeAdvanceInstallment.query.filter(
                    EmployeeAdvanceInstallment.paid_in_salary_expense_id == exp.id
                ).all()
                if inst_rows:
                    advances_total = sum(Decimal(str(inst.amount or 0)) for inst in inst_rows)

                old_expected = base_salary - deductions - social_ins - income_tax - advances_total
                new_expected = base_salary - deductions - social_ins - advances_total
                current_amount = Decimal(str(exp.amount or 0))

                if new_expected <= 0:
                    skipped += 1
                    continue

                if abs(current_amount - new_expected) <= Decimal("0.01"):
                    skipped += 1
                    continue

                if abs(current_amount - old_expected) > Decimal("0.01"):
                    ambiguous += 1
                    continue

                if dry_run:
                    updated += 1
                    continue

                exp.amount = float(new_expected)
                updated += 1
                updated_expense_ids.append(exp.id)

                if update_payments:
                    pay_q = Payment.query.filter(
                        Payment.expense_id == exp.id,
                        Payment.status == PaymentStatus.COMPLETED.value,
                        Payment.direction == PaymentDirection.OUT.value,
                    )
                    pay_rows = pay_q.order_by(Payment.id).all()
                    if len(pay_rows) == 1:
                        p = pay_rows[0]
                        pay_amount = Decimal(str(p.total_amount or 0))
                        if abs(pay_amount - current_amount) <= Decimal("0.01"):
                            p.total_amount = float(new_expected)
                            updated_payment_ids.append(p.id)
                            payments_updated += 1
            except Exception:
                errors += 1
                db.session.rollback()

        if dry_run:
            print(
                "DRY-RUN updated:",
                updated,
                "skipped:",
                skipped,
                "ambiguous:",
                ambiguous,
                "errors:",
                errors,
                "payments_updated:",
                payments_updated,
            )
            return {
                "updated": updated,
                "skipped": skipped,
                "ambiguous": ambiguous,
                "errors": errors,
                "payments_updated": payments_updated,
            }

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            errors += 1
            print("ERROR commit failed")
            return {
                "updated": updated,
                "skipped": skipped,
                "ambiguous": ambiguous,
                "errors": errors,
                "payments_updated": payments_updated,
            }

        for exp_id in updated_expense_ids:
            try:
                run_expense_gl_sync_after_commit(exp_id)
            except Exception:
                pass

        for pid in updated_payment_ids:
            try:
                run_payment_gl_sync_after_commit(pid)
            except Exception:
                pass

        print(
            "updated:",
            updated,
            "skipped:",
            skipped,
            "ambiguous:",
            ambiguous,
            "errors:",
            errors,
            "payments_updated:",
            payments_updated,
        )
        return {
            "updated": updated,
            "skipped": skipped,
            "ambiguous": ambiguous,
            "errors": errors,
            "payments_updated": payments_updated,
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start", dest="start", help="YYYY-MM")
    parser.add_argument("--end", dest="end", help="YYYY-MM")
    parser.add_argument("--employee-id", dest="employee_id")
    parser.add_argument("--payment-method", dest="payment_method", default="bank")
    parser.add_argument("--payment-date", dest="payment_date", help="YYYY-MM-DD")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true")
    parser.add_argument("--apply", dest="apply", action="store_true")
    parser.add_argument("--cleanup-future-payments", dest="cleanup_future_payments", action="store_true")
    parser.add_argument("--fix-legacy-salary-tax", dest="fix_legacy_salary_tax", action="store_true")
    parser.add_argument("--update-payments", dest="update_payments", action="store_true")
    parser.add_argument("--cutoff-date", dest="cutoff_date", help="YYYY-MM-DD")
    args = parser.parse_args()

    start_ym = _parse_ym(args.start) if args.start else None
    end_ym = _parse_ym(args.end) if args.end else None
    if args.cleanup_future_payments:
        cut_date = None
        if args.cutoff_date:
            try:
                cut_date = datetime.strptime(args.cutoff_date, "%Y-%m-%d").date()
            except Exception:
                cut_date = None
        cleanup_future_salary_payments(dry_run=not args.apply, cutoff_date=cut_date)
    elif args.fix_legacy_salary_tax:
        dry_run = True
        if args.apply and not args.dry_run:
            dry_run = False
        fix_legacy_salary_tax(
            dry_run=dry_run,
            start_ym=start_ym,
            end_ym=end_ym,
            employee_id=args.employee_id,
            update_payments=args.update_payments,
        )
    else:
        run(
            dry_run=args.dry_run,
            start_ym=start_ym,
            end_ym=end_ym,
            employee_id=args.employee_id,
            payment_method=args.payment_method,
            payment_date=args.payment_date,
        )
