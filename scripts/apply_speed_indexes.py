#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
تطبيق فهارس الأداء على قاعدة البيانات لتسريع الاستعلامات.

- PostgreSQL: فهارس عادية + فهارس pg_trgm (بحث غامض) + فهارس جزئية.
- SQLite: فهارس عادية على الأعمدة الأكثر استعلاماً.

يعتمد على extensions.ensure_performance_indexes(app).
تشغيل (من جذر المشروع مع تفعيل venv):
  python scripts/apply_speed_indexes.py

على سيرفر الإنتاج (بعد النشر أو بعد استعادة نسخة):
  cd /path/to/garage_manager && source venv/bin/activate && python scripts/apply_speed_indexes.py

ملاحظة: التطبيق يطبّق الفهارس تلقائياً عند التشغيل إذا كان AUTO_CREATE_PERFORMANCE_INDEXES=True
في الإعدادات. هذا السكريبت مفيد عند التشغيل يدوياً بعد استعادة نسخة أو عند تعطيل التطبيق التلقائي.
"""
from __future__ import annotations

import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
os.chdir(basedir)
if basedir not in sys.path:
    sys.path.insert(0, basedir)


def main():
    from app import create_app
    from extensions import ensure_performance_indexes

    app = create_app()
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if "postgresql" in uri:
        db_type = "PostgreSQL"
    elif "sqlite" in uri:
        db_type = "SQLite"
    else:
        db_type = "قاعدة أخرى"
    print(f"نوع القاعدة: {db_type}")
    print("جاري تطبيق فهارس الأداء...")
    ensure_performance_indexes(app)
    print("تم. الفهارس تُسرّع استعلامات البحث والفلترة والترتيب.")


if __name__ == "__main__":
    main()
