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
                income_tax = Decimal(str(emp.income_tax_amount or 0))
                net_before = base_salary - deductions - social_ins - income_tax

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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start", dest="start", help="YYYY-MM")
    parser.add_argument("--end", dest="end", help="YYYY-MM")
    parser.add_argument("--employee-id", dest="employee_id")
    parser.add_argument("--payment-method", dest="payment_method", default="bank")
    parser.add_argument("--payment-date", dest="payment_date", help="YYYY-MM-DD")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true")
    args = parser.parse_args()

    start_ym = _parse_ym(args.start) if args.start else None
    end_ym = _parse_ym(args.end) if args.end else None
    run(
        dry_run=args.dry_run,
        start_ym=start_ym,
        end_ym=end_ym,
        employee_id=args.employee_id,
        payment_method=args.payment_method,
        payment_date=args.payment_date,
    )
