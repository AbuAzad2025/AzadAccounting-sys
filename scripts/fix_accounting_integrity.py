#!/usr/bin/env python3
"""
Accounting integrity repair script.

What it fixes:
1) Voids legacy PAYMENT "Fix" batches that overlap with PAYMENT_SPLIT postings
   for the same payment (duplicate posting path).
2) Voids orphan EXPENSE_REVERSAL batches where the original expense no longer
   exists and no posted EXPENSE batch exists for the same source_id.

Usage:
    venv\\Scripts\\python scripts/fix_accounting_integrity.py
    venv\\Scripts\\python scripts/fix_accounting_integrity.py --apply
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import sys

import psycopg2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import Config


@dataclass
class RepairPlan:
    payment_fix_batch_ids: list[int]
    orphan_expense_reversal_batch_ids: list[int]


def _fetch_value(cursor, query: str, params: tuple | None = None):
    cursor.execute(query, params or ())
    row = cursor.fetchone()
    return row[0] if row else None


def _equation_snapshot(cursor) -> dict:
    cursor.execute(
        """
        WITH p AS (
            SELECT
                e.account,
                a.type,
                SUM(e.debit) AS d,
                SUM(e.credit) AS c
            FROM gl_entries e
            JOIN gl_batches b ON b.id = e.batch_id
            JOIN accounts a ON a.code = e.account
            WHERE b.status = 'POSTED'
            GROUP BY e.account, a.type
        )
        SELECT
            COALESCE(SUM(CASE WHEN type='ASSET' THEN d - c ELSE 0 END), 0) AS assets,
            COALESCE(SUM(CASE WHEN type='LIABILITY' THEN c - d ELSE 0 END), 0) AS liabilities,
            COALESCE(SUM(CASE WHEN type='EQUITY' THEN c - d ELSE 0 END), 0) AS equity,
            COALESCE(SUM(CASE WHEN type='REVENUE' THEN c - d ELSE 0 END), 0) AS revenue,
            COALESCE(SUM(CASE WHEN type='EXPENSE' THEN d - c ELSE 0 END), 0) AS expense
        FROM p
        """
    )
    assets, liabilities, equity, revenue, expense = [Decimal(str(x or 0)) for x in cursor.fetchone()]
    retained = revenue - expense
    rhs = liabilities + equity + retained
    return {
        "assets": float(assets),
        "liabilities": float(liabilities),
        "equity": float(equity),
        "retained_earnings_calc": float(retained),
        "rhs": float(rhs),
        "diff": float(assets - rhs),
    }


def build_plan(cursor) -> RepairPlan:
    cursor.execute(
        """
        SELECT b.id
        FROM gl_batches b
        WHERE b.status = 'POSTED'
          AND b.source_type = 'PAYMENT'
          AND b.memo ILIKE '%Fix%'
          AND EXISTS (
              SELECT 1
              FROM payment_splits ps
              JOIN gl_batches sb ON sb.source_type = 'PAYMENT_SPLIT'
                                AND sb.source_id = ps.id
                                AND sb.status = 'POSTED'
              WHERE ps.payment_id = b.source_id
          )
        ORDER BY b.id
        """
    )
    payment_fix_batch_ids = [int(r[0]) for r in cursor.fetchall()]

    cursor.execute(
        """
        SELECT r.id
        FROM gl_batches r
        WHERE r.status = 'POSTED'
          AND r.source_type = 'EXPENSE_REVERSAL'
          AND NOT EXISTS (
              SELECT 1
              FROM expenses ex
              WHERE ex.id = r.source_id
          )
          AND NOT EXISTS (
              SELECT 1
              FROM gl_batches b2
              WHERE b2.source_type = 'EXPENSE'
                AND b2.source_id = r.source_id
                AND b2.status = 'POSTED'
          )
        ORDER BY r.id
        """
    )
    orphan_expense_reversal_batch_ids = [int(r[0]) for r in cursor.fetchall()]

    return RepairPlan(
        payment_fix_batch_ids=payment_fix_batch_ids,
        orphan_expense_reversal_batch_ids=orphan_expense_reversal_batch_ids,
    )


def _void_batches(cursor, batch_ids: list[int], reason_tag: str) -> int:
    if not batch_ids:
        return 0
    cursor.execute(
        """
        UPDATE gl_batches
        SET
            status = 'VOID',
            posted_at = NULL,
            memo = COALESCE(memo, '') || %s
        WHERE id = ANY(%s)
        """,
        (f" [{reason_tag}]", batch_ids),
    )
    return cursor.rowcount


def _normalize_legacy_fix_accounts(cursor) -> int:
    """
    Normalize legacy account codes used by old manual payment fix batches.
    """
    cursor.execute(
        """
        UPDATE gl_entries e
        SET account = CASE
            WHEN e.account = '1100_CASH' THEN '1000_CASH'
            WHEN e.account = '2100_AP' THEN '2000_AP'
            ELSE e.account
        END
        FROM gl_batches b
        WHERE b.id = e.batch_id
          AND b.status = 'POSTED'
          AND b.source_type = 'PAYMENT'
          AND b.memo ILIKE '%Fix%'
          AND e.account IN ('1100_CASH', '2100_AP')
        """
    )
    return cursor.rowcount


def _print_plan(cursor, plan: RepairPlan) -> None:
    print("=== Accounting Integrity Repair Plan ===")
    print(f"PAYMENT Fix batches to void: {len(plan.payment_fix_batch_ids)}")
    print(f"Orphan EXPENSE_REVERSAL batches to void: {len(plan.orphan_expense_reversal_batch_ids)}")

    for account in ("1100_CASH", "2100_AP"):
        value = _fetch_value(
            cursor,
            """
            SELECT COALESCE(SUM(e.debit - e.credit), 0)
            FROM gl_entries e
            JOIN gl_batches b ON b.id = e.batch_id
            WHERE b.status = 'POSTED'
              AND e.account = %s
            """,
            (account,),
        )
        print(f"Posted net ({account}) before: {float(Decimal(str(value or 0))):,.2f}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply changes. Default is dry-run.")
    args = parser.parse_args()

    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    try:
        with conn.cursor() as cursor:
            before = _equation_snapshot(cursor)
            plan = build_plan(cursor)
            _print_plan(cursor, plan)

            print("Equation before:", before)

            if not args.apply:
                print("Dry-run only. Re-run with --apply to execute.")
                conn.rollback()
                return 0

            changed_a = _void_batches(cursor, plan.payment_fix_batch_ids, "AUTO_VOID_DUP_PAYMENT_FIX")
            changed_b = _void_batches(cursor, plan.orphan_expense_reversal_batch_ids, "AUTO_VOID_ORPHAN_EXPENSE_REVERSAL")
            changed_c = _normalize_legacy_fix_accounts(cursor)
            conn.commit()
            print(
                "Applied: "
                f"voided PAYMENT fix batches={changed_a}, "
                f"orphan reversals={changed_b}, "
                f"normalized legacy fix entries={changed_c}"
            )

        with conn.cursor() as cursor:
            after = _equation_snapshot(cursor)
            print("Equation after :", after)
            for account in ("1100_CASH", "2100_AP"):
                value = _fetch_value(
                    cursor,
                    """
                    SELECT COALESCE(SUM(e.debit - e.credit), 0)
                    FROM gl_entries e
                    JOIN gl_batches b ON b.id = e.batch_id
                    WHERE b.status = 'POSTED'
                      AND e.account = %s
                    """,
                    (account,),
                )
                print(f"Posted net ({account}) after: {float(Decimal(str(value or 0))):,.2f}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
