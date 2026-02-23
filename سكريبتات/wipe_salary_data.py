import os
import sys
import json
from pathlib import Path
from datetime import datetime

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _chunked(items, size=500):
    if not items:
        return []
    return [items[i : i + size] for i in range(0, len(items), size)]


def _ids(rows):
    return [r[0] for r in rows]


def _delete_in_chunks(db, model, ids):
    from sqlalchemy import delete as sa_delete
    deleted = 0
    for chunk in _chunked(ids):
        if not chunk:
            continue
        res = db.session.execute(sa_delete(model).where(model.id.in_(chunk)))
        deleted += int(res.rowcount or 0)
    return deleted


def wipe_salary_data(apply_changes=False, until_year=None):
    from app import create_app
    from extensions import db
    from models import (
        Expense,
        ExpenseType,
        Payment,
        PaymentSplit,
        EmployeeAdvanceInstallment,
        GLBatch,
        GLEntry,
        Check,
    )

    app = create_app()
    with app.app_context():
        from sqlalchemy import or_
        salary_types = ExpenseType.query.filter(
            or_(
                ExpenseType.code.ilike("%SALARY%"),
                ExpenseType.name.ilike("%راتب%"),
                ExpenseType.name.ilike("%رواتب%"),
            )
        ).all()
        salary_type_ids = [t.id for t in salary_types]
        if not salary_type_ids:
            print("ERROR: salary types not found")
            return {"error": "salary_type_missing"}

        salary_expense_query = db.session.query(Expense.id).filter(Expense.type_id.in_(salary_type_ids))
        if until_year:
            start_dt = datetime(int(until_year), 1, 1)
            end_dt = datetime(int(until_year), 12, 31, 23, 59, 59, 999999)
            salary_expense_query = salary_expense_query.filter(
                or_(
                    Expense.date.between(start_dt, end_dt),
                    Expense.period_start.between(start_dt, end_dt),
                    Expense.period_end.between(start_dt, end_dt),
                )
            )
        salary_expense_ids = _ids(salary_expense_query.all())

        payment_ids = []
        if salary_expense_ids:
            payment_ids = _ids(
                db.session.query(Payment.id)
                .filter(Payment.expense_id.in_(salary_expense_ids))
                .all()
            )

        split_ids = []
        check_ids = []
        if payment_ids:
            split_ids = _ids(
                db.session.query(PaymentSplit.id)
                .filter(PaymentSplit.payment_id.in_(payment_ids))
                .all()
            )
            check_ids = _ids(
                db.session.query(Check.id)
                .filter(Check.payment_id.in_(payment_ids))
                .all()
            )

        installment_ids = []
        if salary_expense_ids:
            installment_ids = _ids(
                db.session.query(EmployeeAdvanceInstallment.id)
                .filter(EmployeeAdvanceInstallment.paid_in_salary_expense_id.in_(salary_expense_ids))
                .all()
            )

        batch_ids = []
        if split_ids:
            batch_ids.extend(
                _ids(
                    db.session.query(GLBatch.id)
                    .filter(GLBatch.source_type == "PAYMENT_SPLIT")
                    .filter(GLBatch.source_id.in_(split_ids))
                    .all()
                )
            )
        if payment_ids:
            batch_ids.extend(
                _ids(
                    db.session.query(GLBatch.id)
                    .filter(GLBatch.source_type.in_(["PAYMENT", "PAYMENT_REVERSAL"]))
                    .filter(GLBatch.source_id.in_(payment_ids))
                    .all()
                )
            )
        if salary_expense_ids:
            batch_ids.extend(
                _ids(
                    db.session.query(GLBatch.id)
                    .filter(GLBatch.source_type == "EXPENSE")
                    .filter(GLBatch.source_id.in_(salary_expense_ids))
                    .all()
                )
            )

        result = {
            "salary_expenses": len(salary_expense_ids),
            "payments": len(payment_ids),
            "payment_splits": len(split_ids),
            "checks": len(check_ids),
            "gl_batches": len(batch_ids),
            "installments": len(installment_ids),
            "apply": bool(apply_changes),
            "year": int(until_year) if until_year else None,
        }
        print(json.dumps(result, ensure_ascii=False))

        if not apply_changes:
            return result

        if salary_expense_ids:
            db.session.query(EmployeeAdvanceInstallment).filter(
                EmployeeAdvanceInstallment.paid_in_salary_expense_id.in_(salary_expense_ids)
            ).update(
                {
                    EmployeeAdvanceInstallment.paid: False,
                    EmployeeAdvanceInstallment.paid_date: None,
                    EmployeeAdvanceInstallment.paid_in_salary_expense_id: None,
                },
                synchronize_session=False,
            )

        deleted_checks = _delete_in_chunks(db, Check, check_ids)
        deleted_entries = _delete_in_chunks(db, GLEntry, batch_ids)
        deleted_batches = _delete_in_chunks(db, GLBatch, batch_ids)
        deleted_splits = _delete_in_chunks(db, PaymentSplit, split_ids)
        deleted_payments = _delete_in_chunks(db, Payment, payment_ids)
        deleted_expenses = _delete_in_chunks(db, Expense, salary_expense_ids)

        db.session.commit()

        out = {
            "deleted_checks": deleted_checks,
            "deleted_gl_entries": deleted_entries,
            "deleted_gl_batches": deleted_batches,
            "deleted_payment_splits": deleted_splits,
            "deleted_payments": deleted_payments,
            "deleted_expenses": deleted_expenses,
        }
        print(json.dumps(out, ensure_ascii=False))
        return out


def run():
    args = sys.argv[1:]
    apply_changes = "--apply" in args or os.getenv("APPLY_CHANGES") == "1"
    until_year = None
    for arg in args:
        if arg.startswith("--year="):
            until_year = arg.split("=", 1)[1].strip() or None
        if arg.startswith("--until-year="):
            until_year = arg.split("=", 1)[1].strip() or None
    return wipe_salary_data(apply_changes=apply_changes, until_year=until_year)


if __name__ == "__main__":
    run()
