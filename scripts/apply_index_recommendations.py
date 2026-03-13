#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
تشغيل توصيات الفهارس المخزنة في index/INDEX_DB_INDEX_RECOMMENDATIONS.json.

⚠️ تحذير مهم:
    هذا السكربت ينفّذ أوامر CREATE INDEX مباشرة على قاعدة البيانات الحالية.
    يُفضَّل جداً:
        1) تشغيله أولاً على النسخة المحلية أو نسخة اختبارية من القاعدة.
        2) مراقبة الحجم والأداء قبل تشغيله على الإنتاج.

طريقة الاستخدام (من جذر المشروع مع تفعيل venv):

    python scripts/apply_index_recommendations.py
    python scripts/apply_index_recommendations.py --dry-run   # يعرض الأوامر فقط
"""
from __future__ import annotations

import argparse
import json
import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
os.chdir(basedir)
if basedir not in sys.path:
    sys.path.insert(0, basedir)


def main() -> None:
    parser = argparse.ArgumentParser(description="تطبيق توصيات الفهارس من INDEX_DB_INDEX_RECOMMENDATIONS.json")
    parser.add_argument(
        "--file",
        dest="file",
        default=os.path.join(basedir, "index", "INDEX_DB_INDEX_RECOMMENDATIONS.json"),
        help="مسار ملف التوصيات (افتراضي: index/INDEX_DB_INDEX_RECOMMENDATIONS.json).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="عدم تنفيذ الأوامر، فقط عرضها.",
    )
    args = parser.parse_args()

    rec_path = os.path.abspath(args.file)
    if not os.path.exists(rec_path):
        print(f"[ERROR] لم يتم العثور على ملف التوصيات: {rec_path}")
        sys.exit(1)

    with open(rec_path, "r", encoding="utf-8") as f:
        try:
            recommendations = json.load(f)
        except Exception as e:
            print(f"[ERROR] تعذر قراءة JSON من {rec_path}: {e}")
            sys.exit(1)

    if not isinstance(recommendations, list):
        print("[ERROR] ملف التوصيات لا يحتوي على قائمة (list). تأكد من أنه مُولّد من full_audit_and_indexing.py.")
        sys.exit(1)

    from app import create_app
    from extensions import db
    from sqlalchemy import text

    app = create_app()

    executed = 0
    failed = 0

    with app.app_context():
        # نستخدم معاملة عادية؛ DDL في PostgreSQL يعمل داخل المعاملة بشكل طبيعي
        with db.engine.begin() as conn:
            for rec in recommendations:
                sql = rec.get("sql")
                table = rec.get("table")
                column = rec.get("column")
                reason = rec.get("reason")

                if not sql:
                    continue

                print(f"\n=== توصية فهرس ===")
                print(f"الجدول : {table}")
                print(f"العمود : {column}")
                print(f"السبب  : {reason}")
                print(f"SQL    : {sql}")

                if args.dry_run:
                    continue

                try:
                    conn.execute(text(sql))
                    executed += 1
                except Exception as e:
                    failed += 1
                    print(f"[WARN] فشل تنفيذ الفهرس على {table}.{column}: {e}")

    if args.dry_run:
        print("\n[INFO] وضع DRY-RUN: لم يتم تنفيذ أي فهرس، فقط عرض الأوامر.")
    else:
        print(f"\n[INFO] تم تنفيذ {executed} فهرس/فهارس بنجاح. فشل {failed} (إن وجد).")


if __name__ == "__main__":
    main()

