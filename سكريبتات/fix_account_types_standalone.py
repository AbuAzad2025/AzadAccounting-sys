#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
نسخة مستقلة لتصحيح أنواع الحسابات — تعتمد على config واتصال قاعدة البيانات فقط.
الاستخدام من جذر المشروع: python سكريبتات/fix_account_types_standalone.py [--dry-run]
"""
from __future__ import print_function

import os
import sys

print("[1/5] Starting...", flush=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

# Load .env without importing full config (avoids slow/hanging imports)
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

print("[2/5] Loading env...", flush=True)


def type_from_code(code):
    if not code or not str(code).strip():
        return "ASSET"
    c = (str(code).strip().upper())[0]
    if c == "1":
        return "ASSET"
    if c == "2":
        return "LIABILITY"
    if c == "3":
        return "EQUITY"
    if c == "4":
        return "REVENUE"
    if c in ("5", "6"):
        return "EXPENSE"
    return "ASSET"


def run_fix_standalone(dry_run=True):
    print("[4/5] Connecting to DB...", flush=True)
    uri = _get_db_uri(prefer_sqlite=True)
    if not uri:
        uri = _get_db_uri(prefer_sqlite=False)
    if not uri:
        print("ERROR: DATABASE_URL not set and no instance/garage.db found")
        return
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    to_update = []
    if uri.startswith("sqlite:///"):
        import sqlite3
        db_path = uri.replace("sqlite:///", "").lstrip("/")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute("SELECT id, code, name, type FROM accounts")
            for row in cur.fetchall():
                rid, code, name = row["id"], row["code"], row["name"]
                current = (row["type"] or "").strip()
                expected = type_from_code(code)
                if (current or "").upper() != (expected or "").upper():
                    to_update.append((rid, code, name, current, expected))
        finally:
            conn.close()
    else:
        # PostgreSQL via psycopg2
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
            cur.execute("SELECT id, code, name, type FROM accounts")
            for row in cur.fetchall():
                rid, code, name, current = row[0], row[1], row[2], (row[3] or "").strip()
                expected = type_from_code(code)
                if (current or "").upper() != (expected or "").upper():
                    to_update.append((rid, code, name, current, expected))
            cur.close()
            conn.close()
        except ImportError:
            print("ERROR: For PostgreSQL install psycopg2: pip install psycopg2-binary")
            return
        except Exception as e:
            print("ERROR connecting to PostgreSQL:", e)
            return

    if not to_update:
        print("No accounts need correction.")
        return {"updated": 0}

    if dry_run:
        print("DRY-RUN - accounts to fix:")
        for _rid, code, name, current, expected in to_update:
            # Avoid printing Arabic name on Windows console (cp1252)
            name_safe = (name or "")[:30].encode("ascii", "replace").decode() if name else ""
            print("  {} | {} -> {}  [{}]".format(code, current, expected, name_safe))
        print("Count: {}".format(len(to_update)))
        return {"would_update": len(to_update)}

    if uri.startswith("sqlite:///"):
        import sqlite3
        db_path = uri.replace("sqlite:///", "").lstrip("/")
        conn = sqlite3.connect(db_path)
        try:
            for rid, _code, _name, _current, expected in to_update:
                conn.execute("UPDATE accounts SET type = ? WHERE id = ?", (expected, rid))
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
            for rid, _code, _name, _current, expected in to_update:
                cur.execute("UPDATE accounts SET type = %s WHERE id = %s", (expected, rid))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print("ERROR updating:", e)
            return

    print("Fixed {} account(s).".format(len(to_update)))
    for _rid, code, _name, _current, expected in to_update:
        print("  {} -> {}".format(code, expected))
    return {"updated": len(to_update)}


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    run_fix_standalone(dry_run=dry_run)
    print("[5/5] Done.", flush=True)
