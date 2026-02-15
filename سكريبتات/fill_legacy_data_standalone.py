#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ملء البيانات القديمة الناقصة (NULL أو فارغة) لتوافق الجداول والنظام الجديد.

يحدّث الحقول الإلزامية والاختيارية بقيم مناسبة حقيقية قدر الإمكان
لتجنّب أي خطأ مستقبلاً عند استدعاء السجلات القديمة.

الاستخدام من جذر المشروع:
  python سكريبتات/fill_legacy_data_standalone.py [--dry-run]

يدعم SQLite و PostgreSQL.
"""
from __future__ import print_function

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _load_dotenv_simple():
    try:
        from dotenv import load_dotenv
        for name in (".env", ".env.txt"):
            path = os.path.join(ROOT, name)
            if os.path.isfile(path):
                load_dotenv(path)
                break
    except Exception:
        pass


def _get_db_uri(prefer_sqlite=False):
    _load_dotenv_simple()
    if prefer_sqlite:
        instance = os.path.join(ROOT, "instance", "garage.db")
        if os.path.isfile(instance):
            return "sqlite:///" + instance
    uri = os.environ.get("DATABASE_URL")
    if uri:
        return uri
    host = os.environ.get("PGHOST") or os.environ.get("POSTGRES_HOST")
    database = os.environ.get("PGDATABASE") or os.environ.get("POSTGRES_DB")
    user = os.environ.get("PGUSER") or os.environ.get("POSTGRES_USER")
    if host and database and user:
        from urllib.parse import quote_plus
        pwd = os.environ.get("PGPASSWORD") or os.environ.get("POSTGRES_PASSWORD") or ""
        port = os.environ.get("PGPORT") or os.environ.get("POSTGRES_PORT") or "5432"
        try:
            port = int(port)
        except Exception:
            port = 5432
        auth = "{}:{}".format(quote_plus(user), quote_plus(pwd)) if pwd else quote_plus(user)
        return "postgresql://{}@{}:{}/{}".format(auth, host, port, database)
    instance = os.path.join(ROOT, "instance", "garage.db")
    if os.path.isfile(instance):
        return "sqlite:///" + instance
    return None


def _column_exists_sqlite(cur, table, column):
    cur.execute("PRAGMA table_info(?)", (table,))
    for row in cur.fetchall():
        if row[1] == column:
            return True
    return False


def _column_exists_pg(cur, table, column):
    cur.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
        (table, column),
    )
    return cur.fetchone() is not None


def _ensure_columns_sqlite(conn, dry_run):
    """Add missing columns (SQLite). Existing rows get NULL; fill step will set value."""
    cur = conn.cursor()
    # (table, column, type_and_default_sqlite)
    adds = [
        ("gl_batches", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("gl_entries", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("sales", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("sales", "tax_rate", "NUMERIC(5,2) DEFAULT 0 NOT NULL"),
        ("sales", "status", "VARCHAR(20) DEFAULT 'DRAFT' NOT NULL"),
        ("sales", "payment_status", "VARCHAR(20) DEFAULT 'PENDING' NOT NULL"),
        ("payments", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("payments", "payment_number", "VARCHAR(50) DEFAULT '' NOT NULL"),
        ("payments", "method", "VARCHAR(20) DEFAULT 'CASH' NOT NULL"),
        ("payments", "status", "VARCHAR(20) DEFAULT 'PENDING' NOT NULL"),
        ("payments", "direction", "VARCHAR(10) DEFAULT 'IN' NOT NULL"),
        ("payments", "entity_type", "VARCHAR(20) DEFAULT 'CUSTOMER' NOT NULL"),
        ("expenses", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("expenses", "payee_type", "VARCHAR(20) DEFAULT 'OTHER' NOT NULL"),
        ("expenses", "payment_method", "VARCHAR(20) DEFAULT 'cash' NOT NULL"),
        ("service_requests", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("service_requests", "status", "VARCHAR(20) DEFAULT 'PENDING' NOT NULL"),
    ]
    added = []
    for table, col, typ in adds:
        try:
            if not _column_exists_sqlite(cur, table, col):
                sql = 'ALTER TABLE "%s" ADD COLUMN "%s" %s' % (table.replace('"', '""'), col.replace('"', '""'), typ)
                if not dry_run:
                    cur.execute(sql)
                added.append("%s.%s" % (table, col))
        except Exception as e:
            if "duplicate column" in str(e).lower():
                pass
            else:
                print("  WARN: add column %s.%s: %s" % (table, col, e))
    conn.commit()
    cur.close()
    return added


def _ensure_columns_pg(conn, dry_run):
    """Add missing columns (PostgreSQL). IF NOT EXISTS so safe to run."""
    cur = conn.cursor()
    adds = [
        ("gl_batches", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("gl_entries", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("sales", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("sales", "tax_rate", "NUMERIC(5,2) DEFAULT 0 NOT NULL"),
        ("sales", "status", "VARCHAR(20) DEFAULT 'DRAFT' NOT NULL"),
        ("sales", "payment_status", "VARCHAR(20) DEFAULT 'PENDING' NOT NULL"),
        ("payments", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("payments", "payment_number", "VARCHAR(50) DEFAULT '' NOT NULL"),
        ("payments", "method", "VARCHAR(20) DEFAULT 'CASH' NOT NULL"),
        ("payments", "status", "VARCHAR(20) DEFAULT 'PENDING' NOT NULL"),
        ("payments", "direction", "VARCHAR(10) DEFAULT 'IN' NOT NULL"),
        ("payments", "entity_type", "VARCHAR(20) DEFAULT 'CUSTOMER' NOT NULL"),
        ("expenses", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("expenses", "payee_type", "VARCHAR(20) DEFAULT 'OTHER' NOT NULL"),
        ("expenses", "payment_method", "VARCHAR(20) DEFAULT 'cash' NOT NULL"),
        ("service_requests", "currency", "VARCHAR(10) DEFAULT 'ILS' NOT NULL"),
        ("service_requests", "status", "VARCHAR(20) DEFAULT 'PENDING' NOT NULL"),
    ]
    added = []
    for table, col, typ in adds:
        try:
            if not _column_exists_pg(cur, table, col):
                sql = 'ALTER TABLE "%s" ADD COLUMN IF NOT EXISTS "%s" %s' % (table, col, typ)
                if not dry_run:
                    cur.execute(sql)
                added.append("%s.%s" % (table, col))
        except Exception as e:
            print("  WARN: add column %s.%s: %s" % (table, col, e))
    conn.commit()
    cur.close()
    return added


def _run_updates_sqlite(conn, dry_run):
    cur = conn.cursor()
    updates = []
    # (sql, description)
    updates.append(("UPDATE accounts SET name = COALESCE(NULLIF(TRIM(name), ''), code) WHERE name IS NULL OR TRIM(name) = ''", "accounts.name"))
    updates.append(("UPDATE gl_batches SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "gl_batches.currency"))
    updates.append(("UPDATE gl_entries SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "gl_entries.currency"))
    updates.append(("UPDATE gl_entries SET debit = 0 WHERE debit IS NULL", "gl_entries.debit"))
    updates.append(("UPDATE gl_entries SET credit = 0 WHERE credit IS NULL", "gl_entries.credit"))
    updates.append(("UPDATE sales SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "sales.currency"))
    updates.append(("UPDATE sales SET tax_rate = 0 WHERE tax_rate IS NULL", "sales.tax_rate"))
    updates.append(("UPDATE sales SET discount_total = 0 WHERE discount_total IS NULL", "sales.discount_total"))
    updates.append(("UPDATE sales SET shipping_cost = 0 WHERE shipping_cost IS NULL", "sales.shipping_cost"))
    updates.append(("UPDATE sales SET total_amount = 0 WHERE total_amount IS NULL", "sales.total_amount"))
    updates.append(("UPDATE sales SET total_paid = 0 WHERE total_paid IS NULL", "sales.total_paid"))
    updates.append(("UPDATE sales SET balance_due = 0 WHERE balance_due IS NULL", "sales.balance_due"))
    updates.append(("UPDATE sales SET refunded_total = 0 WHERE refunded_total IS NULL", "sales.refunded_total"))
    updates.append(("UPDATE sales SET status = 'DRAFT' WHERE status IS NULL OR TRIM(status) = ''", "sales.status"))
    updates.append(("UPDATE sales SET payment_status = 'PENDING' WHERE payment_status IS NULL OR TRIM(payment_status) = ''", "sales.payment_status"))
    updates.append(("UPDATE sale_lines SET quantity = 0 WHERE quantity IS NULL", "sale_lines.quantity"))
    updates.append(("UPDATE sale_lines SET unit_price = 0 WHERE unit_price IS NULL", "sale_lines.unit_price"))
    updates.append(("UPDATE sale_lines SET discount_rate = 0 WHERE discount_rate IS NULL", "sale_lines.discount_rate"))
    updates.append(("UPDATE sale_lines SET tax_rate = 0 WHERE tax_rate IS NULL", "sale_lines.tax_rate"))
    updates.append(("UPDATE sale_returns SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "sale_returns.currency"))
    updates.append(("UPDATE sale_returns SET total_amount = 0 WHERE total_amount IS NULL", "sale_returns.total_amount"))
    updates.append(("UPDATE sale_returns SET status = 'DRAFT' WHERE status IS NULL OR TRIM(status) = ''", "sale_returns.status"))
    updates.append(("UPDATE sale_return_lines SET quantity = 1 WHERE quantity IS NULL", "sale_return_lines.quantity"))
    updates.append(("UPDATE sale_return_lines SET unit_price = 0 WHERE unit_price IS NULL", "sale_return_lines.unit_price"))
    updates.append(("UPDATE sale_return_lines SET condition = 'GOOD' WHERE condition IS NULL OR TRIM(condition) = ''", "sale_return_lines.condition"))
    updates.append(("UPDATE invoices SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "invoices.currency"))
    updates.append(("UPDATE invoices SET kind = 'INVOICE' WHERE kind IS NULL OR TRIM(kind) = ''", "invoices.kind"))
    updates.append(("UPDATE invoices SET source = 'MANUAL' WHERE source IS NULL OR TRIM(source) = ''", "invoices.source"))
    updates.append(("UPDATE invoices SET total_amount = 0 WHERE total_amount IS NULL", "invoices.total_amount"))
    updates.append(("UPDATE invoices SET tax_amount = 0 WHERE tax_amount IS NULL", "invoices.tax_amount"))
    updates.append(("UPDATE invoices SET discount_amount = 0 WHERE discount_amount IS NULL", "invoices.discount_amount"))
    updates.append(("UPDATE invoices SET refunded_total = 0 WHERE refunded_total IS NULL", "invoices.refunded_total"))
    updates.append(("UPDATE invoice_lines SET quantity = 0 WHERE quantity IS NULL", "invoice_lines.quantity"))
    updates.append(("UPDATE invoice_lines SET unit_price = 0 WHERE unit_price IS NULL", "invoice_lines.unit_price"))
    updates.append(("UPDATE invoice_lines SET tax_rate = 0 WHERE tax_rate IS NULL", "invoice_lines.tax_rate"))
    updates.append(("UPDATE invoice_lines SET discount = 0 WHERE discount IS NULL", "invoice_lines.discount"))
    updates.append(("UPDATE invoice_lines SET description = COALESCE(NULLIF(TRIM(description), ''), '—') WHERE description IS NULL OR TRIM(description) = ''", "invoice_lines.description"))
    updates.append(("UPDATE payments SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "payments.currency"))
    updates.append(("UPDATE payments SET total_amount = 0.01 WHERE total_amount IS NULL", "payments.total_amount"))
    updates.append(("UPDATE payments SET method = 'CASH' WHERE method IS NULL OR TRIM(method) = ''", "payments.method"))
    updates.append(("UPDATE payments SET status = 'PENDING' WHERE status IS NULL OR TRIM(status) = ''", "payments.status"))
    updates.append(("UPDATE payments SET direction = 'IN' WHERE direction IS NULL OR TRIM(direction) = ''", "payments.direction"))
    updates.append(("UPDATE payments SET entity_type = 'CUSTOMER' WHERE entity_type IS NULL OR TRIM(entity_type) = ''", "payments.entity_type"))
    updates.append(("UPDATE payments SET payment_number = 'LEGACY-' || id WHERE payment_number IS NULL OR TRIM(payment_number) = ''", "payments.payment_number"))
    updates.append(("UPDATE payment_splits SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "payment_splits.currency"))
    updates.append(("UPDATE payment_splits SET converted_currency = 'ILS' WHERE converted_currency IS NULL OR TRIM(converted_currency) = ''", "payment_splits.converted_currency"))
    updates.append(("UPDATE payment_splits SET amount = 0.01 WHERE amount IS NULL", "payment_splits.amount"))
    updates.append(("UPDATE payment_splits SET converted_amount = 0 WHERE converted_amount IS NULL", "payment_splits.converted_amount"))
    updates.append(("UPDATE expenses SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "expenses.currency"))
    updates.append(("UPDATE expenses SET payee_type = 'OTHER' WHERE payee_type IS NULL OR TRIM(payee_type) = ''", "expenses.payee_type"))
    updates.append(("UPDATE expenses SET payment_method = 'cash' WHERE payment_method IS NULL OR TRIM(payment_method) = ''", "expenses.payment_method"))
    updates.append(("UPDATE service_requests SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "service_requests.currency"))
    updates.append(("UPDATE service_requests SET total_amount = 0 WHERE total_amount IS NULL", "service_requests.total_amount"))
    updates.append(("UPDATE service_requests SET parts_total = 0 WHERE parts_total IS NULL", "service_requests.parts_total"))
    updates.append(("UPDATE service_requests SET labor_total = 0 WHERE labor_total IS NULL", "service_requests.labor_total"))
    updates.append(("UPDATE service_requests SET discount_total = 0 WHERE discount_total IS NULL", "service_requests.discount_total"))
    updates.append(("UPDATE service_requests SET total_cost = 0 WHERE total_cost IS NULL", "service_requests.total_cost"))
    updates.append(("UPDATE service_requests SET tax_rate = 0 WHERE tax_rate IS NULL", "service_requests.tax_rate"))
    updates.append(("UPDATE service_requests SET tax_amount = 0 WHERE tax_amount IS NULL", "service_requests.tax_amount"))
    updates.append(("UPDATE service_requests SET status = 'PENDING' WHERE status IS NULL OR TRIM(status) = ''", "service_requests.status"))
    updates.append(("UPDATE service_requests SET service_number = 'SVC-' || id WHERE service_number IS NULL OR TRIM(service_number) = ''", "service_requests.service_number"))
    updates.append(("UPDATE service_parts SET quantity = 0 WHERE quantity IS NULL", "service_parts.quantity"))
    updates.append(("UPDATE service_parts SET unit_price = 0 WHERE unit_price IS NULL", "service_parts.unit_price"))
    updates.append(("UPDATE service_parts SET discount = 0 WHERE discount IS NULL", "service_parts.discount"))
    updates.append(("UPDATE service_tasks SET quantity = 0 WHERE quantity IS NULL", "service_tasks.quantity"))
    updates.append(("UPDATE service_tasks SET unit_price = 0 WHERE unit_price IS NULL", "service_tasks.unit_price"))
    updates.append(("UPDATE service_tasks SET discount = 0 WHERE discount IS NULL", "service_tasks.discount"))
    updates.append(("UPDATE customers SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "customers.currency"))
    updates.append(("UPDATE customers SET name = 'عميل غير محدد' WHERE name IS NULL OR TRIM(name) = ''", "customers.name"))
    updates.append(("UPDATE customers SET phone = '—' WHERE phone IS NULL OR TRIM(phone) = ''", "customers.phone"))
    updates.append(("UPDATE customers SET opening_balance = 0 WHERE opening_balance IS NULL", "customers.opening_balance"))
    updates.append(("UPDATE customers SET current_balance = 0 WHERE current_balance IS NULL", "customers.current_balance"))
    updates.append(("UPDATE suppliers SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "suppliers.currency"))
    updates.append(("UPDATE suppliers SET name = 'مورد غير محدد' WHERE name IS NULL OR TRIM(name) = ''", "suppliers.name"))
    updates.append(("UPDATE suppliers SET opening_balance = 0 WHERE opening_balance IS NULL", "suppliers.opening_balance"))
    updates.append(("UPDATE suppliers SET current_balance = 0 WHERE current_balance IS NULL", "suppliers.current_balance"))
    updates.append(("UPDATE partners SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "partners.currency"))
    updates.append(("UPDATE partners SET name = 'شريك غير محدد' WHERE name IS NULL OR TRIM(name) = ''", "partners.name"))
    updates.append(("UPDATE partners SET opening_balance = 0 WHERE opening_balance IS NULL", "partners.opening_balance"))
    updates.append(("UPDATE partners SET current_balance = 0 WHERE current_balance IS NULL", "partners.current_balance"))
    updates.append(("UPDATE preorders SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "preorders.currency"))
    updates.append(("UPDATE preorders SET total_amount = 0 WHERE total_amount IS NULL", "preorders.total_amount"))
    updates.append(("UPDATE preorders SET prepaid_amount = 0 WHERE prepaid_amount IS NULL", "preorders.prepaid_amount"))
    updates.append(("UPDATE shipments SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "shipments.currency"))
    updates.append(("UPDATE exchange_transactions SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "exchange_transactions.currency"))
    updates.append(("UPDATE supplier_settlements SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "supplier_settlements.currency"))
    updates.append(("UPDATE partner_settlements SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "partner_settlements.currency"))
    updates.append(("UPDATE tax_entries SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "tax_entries.currency"))
    updates.append(("UPDATE tax_entries SET tax_rate = 0 WHERE tax_rate IS NULL", "tax_entries.tax_rate"))
    updates.append(("UPDATE tax_entries SET base_amount = 0 WHERE base_amount IS NULL", "tax_entries.base_amount"))
    updates.append(("UPDATE tax_entries SET tax_amount = 0 WHERE tax_amount IS NULL", "tax_entries.tax_amount"))
    updates.append(("UPDATE tax_entries SET total_amount = 0 WHERE total_amount IS NULL", "tax_entries.total_amount"))
    updates.append(("UPDATE recurring_invoice_templates SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "recurring_invoice_templates.currency"))
    updates.append(("UPDATE recurring_invoice_templates SET tax_rate = 0 WHERE tax_rate IS NULL", "recurring_invoice_templates.tax_rate"))

    done = []
    for sql, desc in updates:
        try:
            cur.execute(sql)
            if not dry_run:
                conn.commit()
            n = cur.rowcount
            if n and n > 0:
                done.append((desc, n))
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            if "no such column" in str(e).lower() or "does not exist" in str(e).lower():
                pass  # skip if table/column missing (e.g. old DB)
            else:
                print("  WARN: {} -> {}".format(desc, e))
    cur.close()
    return done


def _run_updates_pg(conn, dry_run):
    cur = conn.cursor()
    updates = []
    updates.append(("UPDATE accounts SET name = COALESCE(NULLIF(TRIM(name), ''), code) WHERE name IS NULL OR TRIM(name) = ''", "accounts.name"))
    updates.append(("UPDATE gl_batches SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "gl_batches.currency"))
    updates.append(("UPDATE gl_entries SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "gl_entries.currency"))
    updates.append(("UPDATE gl_entries SET debit = 0 WHERE debit IS NULL", "gl_entries.debit"))
    updates.append(("UPDATE gl_entries SET credit = 0 WHERE credit IS NULL", "gl_entries.credit"))
    updates.append(("UPDATE sales SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "sales.currency"))
    updates.append(("UPDATE sales SET tax_rate = 0 WHERE tax_rate IS NULL", "sales.tax_rate"))
    updates.append(("UPDATE sales SET discount_total = 0 WHERE discount_total IS NULL", "sales.discount_total"))
    updates.append(("UPDATE sales SET shipping_cost = 0 WHERE shipping_cost IS NULL", "sales.shipping_cost"))
    updates.append(("UPDATE sales SET total_amount = 0 WHERE total_amount IS NULL", "sales.total_amount"))
    updates.append(("UPDATE sales SET total_paid = 0 WHERE total_paid IS NULL", "sales.total_paid"))
    updates.append(("UPDATE sales SET balance_due = 0 WHERE balance_due IS NULL", "sales.balance_due"))
    updates.append(("UPDATE sales SET refunded_total = 0 WHERE refunded_total IS NULL", "sales.refunded_total"))
    updates.append(("UPDATE sales SET status = 'DRAFT' WHERE status IS NULL OR TRIM(status) = ''", "sales.status"))
    updates.append(("UPDATE sales SET payment_status = 'PENDING' WHERE payment_status IS NULL OR TRIM(payment_status) = ''", "sales.payment_status"))
    updates.append(("UPDATE sale_lines SET quantity = 0 WHERE quantity IS NULL", "sale_lines.quantity"))
    updates.append(("UPDATE sale_lines SET unit_price = 0 WHERE unit_price IS NULL", "sale_lines.unit_price"))
    updates.append(("UPDATE sale_lines SET discount_rate = 0 WHERE discount_rate IS NULL", "sale_lines.discount_rate"))
    updates.append(("UPDATE sale_lines SET tax_rate = 0 WHERE tax_rate IS NULL", "sale_lines.tax_rate"))
    updates.append(("UPDATE sale_returns SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "sale_returns.currency"))
    updates.append(("UPDATE sale_returns SET total_amount = 0 WHERE total_amount IS NULL", "sale_returns.total_amount"))
    updates.append(("UPDATE sale_returns SET status = 'DRAFT' WHERE status IS NULL OR TRIM(status) = ''", "sale_returns.status"))
    updates.append(("UPDATE sale_return_lines SET quantity = 1 WHERE quantity IS NULL", "sale_return_lines.quantity"))
    updates.append(("UPDATE sale_return_lines SET unit_price = 0 WHERE unit_price IS NULL", "sale_return_lines.unit_price"))
    updates.append(("UPDATE sale_return_lines SET condition = 'GOOD' WHERE condition IS NULL OR TRIM(condition) = ''", "sale_return_lines.condition"))
    updates.append(("UPDATE invoices SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "invoices.currency"))
    updates.append(("UPDATE invoices SET kind = 'INVOICE' WHERE kind IS NULL OR TRIM(kind) = ''", "invoices.kind"))
    updates.append(("UPDATE invoices SET source = 'MANUAL' WHERE source IS NULL OR TRIM(source) = ''", "invoices.source"))
    updates.append(("UPDATE invoices SET total_amount = 0 WHERE total_amount IS NULL", "invoices.total_amount"))
    updates.append(("UPDATE invoices SET tax_amount = 0 WHERE tax_amount IS NULL", "invoices.tax_amount"))
    updates.append(("UPDATE invoices SET discount_amount = 0 WHERE discount_amount IS NULL", "invoices.discount_amount"))
    updates.append(("UPDATE invoices SET refunded_total = 0 WHERE refunded_total IS NULL", "invoices.refunded_total"))
    updates.append(("UPDATE invoice_lines SET quantity = 0 WHERE quantity IS NULL", "invoice_lines.quantity"))
    updates.append(("UPDATE invoice_lines SET unit_price = 0 WHERE unit_price IS NULL", "invoice_lines.unit_price"))
    updates.append(("UPDATE invoice_lines SET tax_rate = 0 WHERE tax_rate IS NULL", "invoice_lines.tax_rate"))
    updates.append(("UPDATE invoice_lines SET discount = 0 WHERE discount IS NULL", "invoice_lines.discount"))
    updates.append(("UPDATE invoice_lines SET description = COALESCE(NULLIF(TRIM(description), ''), '—') WHERE description IS NULL OR TRIM(description) = ''", "invoice_lines.description"))
    updates.append(("UPDATE payments SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "payments.currency"))
    updates.append(("UPDATE payments SET total_amount = 0.01 WHERE total_amount IS NULL", "payments.total_amount"))
    updates.append(("UPDATE payments SET method = 'CASH' WHERE method IS NULL OR TRIM(method) = ''", "payments.method"))
    updates.append(("UPDATE payments SET status = 'PENDING' WHERE status IS NULL OR TRIM(status) = ''", "payments.status"))
    updates.append(("UPDATE payments SET direction = 'IN' WHERE direction IS NULL OR TRIM(direction) = ''", "payments.direction"))
    updates.append(("UPDATE payments SET entity_type = 'CUSTOMER' WHERE entity_type IS NULL OR TRIM(entity_type) = ''", "payments.entity_type"))
    updates.append(("UPDATE payments SET payment_number = 'LEGACY-' || id WHERE payment_number IS NULL OR TRIM(payment_number) = ''", "payments.payment_number"))
    updates.append(("UPDATE payment_splits SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "payment_splits.currency"))
    updates.append(("UPDATE payment_splits SET converted_currency = 'ILS' WHERE converted_currency IS NULL OR TRIM(converted_currency) = ''", "payment_splits.converted_currency"))
    updates.append(("UPDATE payment_splits SET amount = 0.01 WHERE amount IS NULL", "payment_splits.amount"))
    updates.append(("UPDATE payment_splits SET converted_amount = 0 WHERE converted_amount IS NULL", "payment_splits.converted_amount"))
    updates.append(("UPDATE expenses SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "expenses.currency"))
    updates.append(("UPDATE expenses SET payee_type = 'OTHER' WHERE payee_type IS NULL OR TRIM(payee_type) = ''", "expenses.payee_type"))
    updates.append(("UPDATE expenses SET payment_method = 'cash' WHERE payment_method IS NULL OR TRIM(payment_method) = ''", "expenses.payment_method"))
    updates.append(("UPDATE service_requests SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "service_requests.currency"))
    updates.append(("UPDATE service_requests SET total_amount = 0 WHERE total_amount IS NULL", "service_requests.total_amount"))
    updates.append(("UPDATE service_requests SET parts_total = 0 WHERE parts_total IS NULL", "service_requests.parts_total"))
    updates.append(("UPDATE service_requests SET labor_total = 0 WHERE labor_total IS NULL", "service_requests.labor_total"))
    updates.append(("UPDATE service_requests SET discount_total = 0 WHERE discount_total IS NULL", "service_requests.discount_total"))
    updates.append(("UPDATE service_requests SET total_cost = 0 WHERE total_cost IS NULL", "service_requests.total_cost"))
    updates.append(("UPDATE service_requests SET tax_rate = 0 WHERE tax_rate IS NULL", "service_requests.tax_rate"))
    updates.append(("UPDATE service_requests SET tax_amount = 0 WHERE tax_amount IS NULL", "service_requests.tax_amount"))
    updates.append(("UPDATE service_requests SET status = 'PENDING' WHERE status IS NULL OR TRIM(status) = ''", "service_requests.status"))
    updates.append(("UPDATE service_requests SET service_number = 'SVC-' || id WHERE service_number IS NULL OR TRIM(service_number) = ''", "service_requests.service_number"))
    updates.append(("UPDATE service_parts SET quantity = 0 WHERE quantity IS NULL", "service_parts.quantity"))
    updates.append(("UPDATE service_parts SET unit_price = 0 WHERE unit_price IS NULL", "service_parts.unit_price"))
    updates.append(("UPDATE service_parts SET discount = 0 WHERE discount IS NULL", "service_parts.discount"))
    updates.append(("UPDATE service_tasks SET quantity = 0 WHERE quantity IS NULL", "service_tasks.quantity"))
    updates.append(("UPDATE service_tasks SET unit_price = 0 WHERE unit_price IS NULL", "service_tasks.unit_price"))
    updates.append(("UPDATE service_tasks SET discount = 0 WHERE discount IS NULL", "service_tasks.discount"))
    updates.append(("UPDATE customers SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "customers.currency"))
    updates.append(("UPDATE customers SET name = 'عميل غير محدد' WHERE name IS NULL OR TRIM(name) = ''", "customers.name"))
    updates.append(("UPDATE customers SET phone = '—' WHERE phone IS NULL OR TRIM(phone) = ''", "customers.phone"))
    updates.append(("UPDATE customers SET opening_balance = 0 WHERE opening_balance IS NULL", "customers.opening_balance"))
    updates.append(("UPDATE customers SET current_balance = 0 WHERE current_balance IS NULL", "customers.current_balance"))
    updates.append(("UPDATE suppliers SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "suppliers.currency"))
    updates.append(("UPDATE suppliers SET name = 'مورد غير محدد' WHERE name IS NULL OR TRIM(name) = ''", "suppliers.name"))
    updates.append(("UPDATE suppliers SET opening_balance = 0 WHERE opening_balance IS NULL", "suppliers.opening_balance"))
    updates.append(("UPDATE suppliers SET current_balance = 0 WHERE current_balance IS NULL", "suppliers.current_balance"))
    updates.append(("UPDATE partners SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "partners.currency"))
    updates.append(("UPDATE partners SET name = 'شريك غير محدد' WHERE name IS NULL OR TRIM(name) = ''", "partners.name"))
    updates.append(("UPDATE partners SET opening_balance = 0 WHERE opening_balance IS NULL", "partners.opening_balance"))
    updates.append(("UPDATE partners SET current_balance = 0 WHERE current_balance IS NULL", "partners.current_balance"))
    updates.append(("UPDATE preorders SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "preorders.currency"))
    updates.append(("UPDATE preorders SET total_amount = 0 WHERE total_amount IS NULL", "preorders.total_amount"))
    updates.append(("UPDATE preorders SET prepaid_amount = 0 WHERE prepaid_amount IS NULL", "preorders.prepaid_amount"))
    updates.append(("UPDATE shipments SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "shipments.currency"))
    updates.append(("UPDATE exchange_transactions SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "exchange_transactions.currency"))
    updates.append(("UPDATE supplier_settlements SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "supplier_settlements.currency"))
    updates.append(("UPDATE partner_settlements SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "partner_settlements.currency"))
    updates.append(("UPDATE tax_entries SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "tax_entries.currency"))
    updates.append(("UPDATE tax_entries SET tax_rate = 0 WHERE tax_rate IS NULL", "tax_entries.tax_rate"))
    updates.append(("UPDATE tax_entries SET base_amount = 0 WHERE base_amount IS NULL", "tax_entries.base_amount"))
    updates.append(("UPDATE tax_entries SET tax_amount = 0 WHERE tax_amount IS NULL", "tax_entries.tax_amount"))
    updates.append(("UPDATE tax_entries SET total_amount = 0 WHERE total_amount IS NULL", "tax_entries.total_amount"))
    updates.append(("UPDATE recurring_invoice_templates SET currency = 'ILS' WHERE currency IS NULL OR TRIM(currency) = ''", "recurring_invoice_templates.currency"))
    updates.append(("UPDATE recurring_invoice_templates SET tax_rate = 0 WHERE tax_rate IS NULL", "recurring_invoice_templates.tax_rate"))

    done = []
    for sql, desc in updates:
        try:
            cur.execute(sql)
            if not dry_run:
                conn.commit()
            n = cur.rowcount
            if n and n > 0:
                done.append((desc, n))
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                pass
            elif "relation" in str(e).lower() and "does not exist" in str(e).lower():
                pass
            else:
                print("  WARN: {} -> {}".format(desc, e))
    cur.close()
    return done


def run_fill(dry_run=True):
    print("[1/4] Loading env...", flush=True)
    uri = _get_db_uri(prefer_sqlite=True)
    if not uri:
        uri = _get_db_uri(prefer_sqlite=False)
    if not uri:
        print("ERROR: DATABASE_URL not set and no instance/garage.db found")
        return {"updated": 0}

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    # عرض موجز لاتصال القاعدة (بدون كلمة السر كاملة)
    _show_uri = uri.split("@")[-1] if "@" in uri else (uri.replace("sqlite:///", "sqlite: ") if "sqlite" in uri else uri[:50] + "...")
    print("[2/4] DB: %s" % _show_uri, flush=True)

    if dry_run:
        print("DRY-RUN: will ensure columns exist and apply updates where column IS NULL or empty.", flush=True)

    done = []
    added = []
    if uri.startswith("sqlite:///"):
        import sqlite3
        db_path = uri.replace("sqlite:///", "").lstrip("/")
        conn = sqlite3.connect(db_path)
        try:
            added = _ensure_columns_sqlite(conn, dry_run)
            if added:
                print("Columns ensured (added if missing): %s" % (added,))
            done = _run_updates_sqlite(conn, dry_run)
        finally:
            conn.close()
    else:
        try:
            import psycopg2
            from urllib.parse import urlparse
            parsed = urlparse(uri)
            conn = psycopg2.connect(
                host=parsed.hostname or "localhost",
                port=parsed.port or 5432,
                dbname=(parsed.path or "").lstrip("/"),
                user=parsed.username,
                password=parsed.password,
                connect_timeout=5,
            )
            try:
                added = _ensure_columns_pg(conn, dry_run)
                if added:
                    print("Columns ensured (added if missing): %s" % (added,))
                done = _run_updates_pg(conn, dry_run)
            finally:
                conn.close()
        except ImportError:
            print("ERROR: For PostgreSQL install psycopg2: pip install psycopg2-binary")
            return {"updated": 0}
        except Exception as e:
            print("ERROR connecting:", e)
            return {"updated": 0}

    if done:
        print("Updates applied (rows affected):")
        for desc, n in done:
            print("  {}: {}".format(desc, n))
        total = sum(n for _, n in done)
        print("Total rows updated: {}".format(total))
    else:
        print("No rows needed updating (or dry-run with no changes).")
    print("[3/4] Done. Columns added: %s. Rows updated: %s." % (len(added) if added else 0, sum(n for _, n in done)), flush=True)
    return {"updated": sum(n for _, n in done), "items": done}


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    run_fill(dry_run=dry_run)
    print("[4/4] Exit.", flush=True)
