#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""تقرير سريع: عدد الصفوف والقيم الناقصة في الجداول الرئيسية (PostgreSQL)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
try:
    from dotenv import load_dotenv
    load_dotenv(".env")
except Exception:
    pass

uri = os.environ.get("DATABASE_URL", "")
if not uri or "postgresql" not in uri and "postgres" not in uri:
    print("DATABASE_URL not set or not PostgreSQL. Exit.")
    sys.exit(0)
uri = uri.replace("postgres://", "postgresql://", 1)

import psycopg2
from urllib.parse import urlparse
parsed = urlparse(uri)
conn = psycopg2.connect(
    host=parsed.hostname or "localhost",
    port=parsed.port or 5432,
    dbname=(parsed.path or "").lstrip("/"),
    user=parsed.username,
    password=parsed.password,
)
cur = conn.cursor()

tables = ["accounts", "customers", "suppliers", "sales", "payments", "invoices", "expenses", "service_requests", "sale_returns"]
print("=== Row counts (main tables) ===")
for t in tables:
    try:
        cur.execute("SELECT COUNT(*) FROM " + t)
        n = cur.fetchone()[0]
        print("  %s: %s" % (t, n))
    except Exception as e:
        print("  %s: err - %s" % (t, str(e)[:60]))

checks = [
    ("customers", "name", "name IS NULL OR TRIM(name) = ''"),
    ("sales", "currency", "currency IS NULL OR TRIM(currency) = ''"),
    ("payments", "payment_number", "payment_number IS NULL OR TRIM(payment_number) = ''"),
]
print("\n=== Rows with NULL or empty (legacy gaps) ===")
for tbl, col, cond in checks:
    try:
        cur.execute("SELECT COUNT(*) FROM " + tbl + " WHERE " + cond)
        n = cur.fetchone()[0]
        print("  %s.%s: %s" % (tbl, col, n))
    except Exception as e:
        print("  %s.%s: %s" % (tbl, col, str(e)[:50]))

cur.close()
conn.close()
print("\nDone.")
