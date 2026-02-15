#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ensure required GL accounts exist for the new system (6200/2200, VAT, etc.).
Same as سكريبتات/ensure_gl_accounts_standalone.py — run from project root:

  python سكريبتات/ensure_gl_accounts_standalone.py [--dry-run]
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


ACCOUNT_NAME_MAP = {
    "1000_CASH": "الصندوق",
    "1010_BANK": "البنك",
    "1020_CARD_CLEARING": "البطاقات",
    "1100_AR": "ذمم العملاء",
    "1150_CHQ_REC": "شيكات تحت التحصيل",
    "1205_INV_EXCHANGE": "مخزون توريد تبادل",
    "1300_INVENTORY": "المخزون",
    "1300_INV_RSV": "احتياطي مخزون",
    "1599_ACC_DEP": "مخصص إهلاك متراكم",
    "2000_AP": "ذمم الموردين والخصوم",
    "2100_VAT_PAYABLE": "ضريبة القيمة المضافة",
    "2200_INCOME_TAX_PAYABLE": "ضريبة الدخل المستحقة",
    "2200_PARTNER_CLEARING": "تسوية الشركاء",
    "2150_CHQ_PAY": "شيكات تحت الدفع",
    "2150_PAYROLL_CLR": "قيد الرواتب",
    "2300_ADV_PAY": "إيرادات مقدمة",
    "3000_EQUITY": "حقوق الملكية",
    "3100_OWNER_CURRENT": "حساب المالك الجاري",
    "3200_CURRENT_EARNINGS": "أرباح محتجزة جارية",
    "4000_SALES": "المبيعات",
    "4050_SALES_DISCOUNT": "خصم المبيعات",
    "4100_SERVICE_REVENUE": "إيراد الخدمات",
    "4200_SHIPPING_INCOME": "إيراد الشحن",
    "5000_EXPENSES": "مصروفات",
    "5100_COGS": "تكلفة البضاعة المباعة",
    "5100_PURCHASES": "المشتريات",
    "5100_SUPPLIER_EXPENSES": "مصروفات موردين",
    "5100_SUPPLIER_EXPENS": "مصروفات موردين",
    "5105_COGS_EXCHANGE": "تكلفة توريد تبادل",
    "6100_SALARIES": "الرواتب",
    "6200_INCOME_TAX_EXPENSE": "ضريبة الدخل (مصروف)",
    "6500_FUEL": "وقود",
    "6600_OFFICE": "مستلزمات مكتب",
    "6800_DEPRECIATION": "إهلاك",
    "6960_HOME_EXPENSE": "مصروفات منزلية",
}

TYPE_BY_PREFIX = (
    ("1", "ASSET"),
    ("2", "LIABILITY"),
    ("3", "EQUITY"),
    ("4", "REVENUE"),
    ("5", "EXPENSE"),
    ("6", "EXPENSE"),
)


def _account_type_from_code(code):
    code = (code or "").strip()
    if not code:
        return "ASSET"
    for prefix, at in TYPE_BY_PREFIX:
        if code.startswith(prefix):
            return at
    return "ASSET"


def run_ensure(dry_run=True):
    print("[1/4] Loading env...", flush=True)
    uri = _get_db_uri(prefer_sqlite=True)
    if not uri:
        uri = _get_db_uri(prefer_sqlite=False)
    if not uri:
        print("ERROR: DATABASE_URL not set and no instance/garage.db found")
        return {"inserted": 0}

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    to_insert = []
    if uri.startswith("sqlite:///"):
        import sqlite3
        db_path = uri.replace("sqlite:///", "").lstrip("/")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute("SELECT code FROM accounts")
            existing = {str(row["code"] or "").strip().upper() for row in cur.fetchall()}
            for code, name in ACCOUNT_NAME_MAP.items():
                code_upper = (code or "").strip().upper()
                if code_upper not in existing:
                    to_insert.append((code, name, _account_type_from_code(code)))
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
            cur = conn.cursor()
            cur.execute("SELECT code FROM accounts")
            existing = {str(row[0] or "").strip().upper() for row in cur.fetchall()}
            for code, name in ACCOUNT_NAME_MAP.items():
                code_upper = (code or "").strip().upper()
                if code_upper not in existing:
                    to_insert.append((code, name, _account_type_from_code(code)))
            cur.close()
            conn.close()
        except ImportError:
            print("ERROR: For PostgreSQL install psycopg2: pip install psycopg2-binary")
            return {"inserted": 0}
        except Exception as e:
            print("ERROR connecting to PostgreSQL:", e)
            return {"inserted": 0}

    if not to_insert:
        print("No missing accounts. All required GL accounts exist.")
        return {"inserted": 0}

    if dry_run:
        print("DRY-RUN - accounts that would be inserted:")
        for code, name, typ in to_insert:
            name_safe = (name or "")[:40].encode("ascii", "replace").decode() if name else ""
            print("  {} | {} | {}".format(code, typ, name_safe))
        print("Count: {}".format(len(to_insert)))
        return {"would_insert": len(to_insert)}

    print("[2/4] Inserting {} account(s)...".format(len(to_insert)), flush=True)
    if uri.startswith("sqlite:///"):
        import sqlite3
        db_path = uri.replace("sqlite:///", "").lstrip("/")
        conn = sqlite3.connect(db_path)
        try:
            for code, name, typ in to_insert:
                conn.execute(
                    "INSERT INTO accounts (code, name, type, is_active, created_at, updated_at) VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                    (code, name, typ),
                )
            conn.commit()
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
            cur = conn.cursor()
            for code, name, typ in to_insert:
                cur.execute(
                    "INSERT INTO accounts (code, name, type, is_active, created_at, updated_at) VALUES (%s, %s, %s, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                    (code, name, typ),
                )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print("ERROR inserting:", e)
            return {"inserted": 0}

    print("Inserted {} account(s).".format(len(to_insert)))
    for code, name, typ in to_insert:
        print("  + {} ({})".format(code, typ))
    print("[3/4] Done.", flush=True)
    return {"inserted": len(to_insert)}


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    run_ensure(dry_run=dry_run)
    print("[4/4] Exit.", flush=True)
