#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
تدقيق شامل + فهرسة أداء لقاعدة البيانات (Back/Front/DB) في ملف واحد.

هذا السكربت يجمع ما يلي في مجلد index/ (أو مسار يحدد بـ --output-dir):

1) تشغيل فهرسة بنية المشروع (Routes/Models/Permissions/Templates/...) عبر generate_index.run
2) فهرسة حقيقية لهيكل قاعدة البيانات والفهارس الموجودة:
   - INDEX_DB_SCHEMA.json / INDEX_DB_SCHEMA.md
     * كل الجداول والأعمدة وأنواعها والمفاتيح الأساسية والأجنبية
   - INDEX_DB_INDEXES.json / INDEX_DB_INDEXES.md
     * كل الفهارس الحالية (الاسم، الجدول، الأعمدة، نوع الفهرس، هل هو unique)
3) اختيارياً: تشغيل ensure_performance_indexes(app) لتطبيق فهارس الأداء الجاهزة
   - مع تسجيل تقرير قبل/بعد للفـهارس:
     * INDEX_DB_INDEXES_BEFORE.json
     * INDEX_DB_INDEXES_AFTER.json

طريقة الاستخدام (من جذر المشروع مع تفعيل venv):

    python scripts/full_audit_and_indexing.py
    python scripts/full_audit_and_indexing.py --output-dir index --apply-indexes

ملاحظات:
- السكربت لا يسقط جداول ولا يغير هيكل الأعمدة؛ فقط يقرأ أو ينشئ فهارس.
- في الإنتاج يُفضّل تشغيله أولاً بدون --apply-indexes لمراجعة التقارير، ثم مرة ثانية مع الخيار عند التأكد.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
os.chdir(basedir)
if basedir not in sys.path:
    sys.path.insert(0, basedir)


def _dump_json(path: str, data: object) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _dump_md(path: str, lines: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _collect_db_schema_and_indexes(app, db, output_dir: str) -> tuple[dict, dict]:
    """
    فهرسة حقيقية لهيكل القاعدة والفهارس الحالية باستخدام SQLAlchemy Inspector فقط (بدون أي إسقاط).
    """
    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    all_tables = sorted(inspector.get_table_names())

    schema: dict[str, dict] = {}
    indexes: dict[str, list[dict]] = {}

    for table in all_tables:
        cols = inspector.get_columns(table)
        pk = inspector.get_pk_constraint(table) or {}
        fks = inspector.get_foreign_keys(table) or []
        idxs = inspector.get_indexes(table) or []

        schema[table] = {
            "columns": [
                {
                    "name": c.get("name"),
                    "type": str(c.get("type")),
                    "nullable": bool(c.get("nullable", True)),
                    "default": c.get("default"),
                }
                for c in cols
            ],
            "primary_key": pk.get("constrained_columns") or [],
            "foreign_keys": [
                {
                    "name": fk.get("name"),
                    "columns": fk.get("constrained_columns") or [],
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": fk.get("referred_columns") or [],
                }
                for fk in fks
            ],
        }

        table_indexes: list[dict] = []
        for idx in idxs:
            cols_for_index = idx.get("column_names") or []
            if not isinstance(cols_for_index, (list, tuple)):
                cols_for_index = [cols_for_index]
            table_indexes.append(
                {
                    "name": idx.get("name"),
                    "columns": list(cols_for_index),
                    "unique": bool(idx.get("unique", False)),
                }
            )
        indexes[table] = table_indexes

    # كتابة ملفات الفهرسة
    schema_path_json = os.path.join(output_dir, "INDEX_DB_SCHEMA.json")
    _dump_json(schema_path_json, schema)

    schema_md_lines = [
        "# فهرس هيكل قاعدة البيانات (DB Schema)",
        "",
        f"تم التوليد في: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
    ]
    for table in all_tables:
        info = schema[table]
        schema_md_lines.append(f"## {table}")
        schema_md_lines.append("")
        schema_md_lines.append("| العمود | النوع | nullable | default |")
        schema_md_lines.append("|--------|-------|----------|---------|")
        for col in info["columns"]:
            schema_md_lines.append(
                f"| {col['name']} | {col['type']} | {col['nullable']} | {col['default'] or '-'} |"
            )
        if info["primary_key"]:
            schema_md_lines.append("")
            schema_md_lines.append(f"- **المفتاح الأساسي (PK):** {', '.join(info['primary_key'])}")
        if info["foreign_keys"]:
            schema_md_lines.append("")
            schema_md_lines.append("- **المفاتيح الأجنبية (FK):**")
            for fk in info["foreign_keys"]:
                schema_md_lines.append(
                    f"  - {fk['name'] or '-'}: ({', '.join(fk['columns'])}) → "
                    f"{fk['referred_table']}({', '.join(fk['referred_columns'])})"
                )
        schema_md_lines.append("")

    schema_path_md = os.path.join(output_dir, "INDEX_DB_SCHEMA.md")
    _dump_md(schema_path_md, schema_md_lines)

    # فهرس الفهارس
    idx_json_path = os.path.join(output_dir, "INDEX_DB_INDEXES.json")
    _dump_json(idx_json_path, indexes)

    idx_md_lines = [
        "# فهرس فهارس قاعدة البيانات (Indexes)",
        "",
        f"تم التوليد في: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "| الجدول | اسم الفهرس | الأعمدة | Unique |",
        "|--------|------------|---------|--------|",
    ]
    for table in all_tables:
        for idx in indexes.get(table, []):
            cols_safe = [str(c) if c is not None else "<UNKNOWN>" for c in idx.get("columns", [])]
            idx_md_lines.append(
                f"| {table} | {idx.get('name')} | {', '.join(cols_safe) or '-'} | {bool(idx.get('unique', False))} |"
            )
    idx_md_path = os.path.join(output_dir, "INDEX_DB_INDEXES.md")
    _dump_md(idx_md_path, idx_md_lines)

    return schema, indexes


def _build_index_recommendations(schema: dict[str, dict], indexes: dict[str, list[dict]]) -> list[dict]:
    """
    توليد توصيات فهارس اعتماداً على:
    - كل FK يجب أن يملك فهرساً على أعمدته.
    - الأعمدة المتكررة الشائعة مثل: created_at, updated_at, is_active, status, customer_id, supplier_id...
    لا ينفذ شيئاً، فقط يقترح.
    """
    existing_by_table_col: dict[tuple[str, str], bool] = {}
    for table, idx_list in indexes.items():
        for idx in idx_list:
            for col in idx.get("columns", []) or []:
                if col:
                    existing_by_table_col[(table, str(col))] = True

    recommendations: list[dict] = []

    # 1) فهارس على أعمدة الـ FK
    for table, info in schema.items():
        for fk in info.get("foreign_keys", []):
            for col in fk.get("columns") or []:
                key = (table, str(col))
                if not existing_by_table_col.get(key):
                    idx_name = f"ix_{table}_{col}_fk"
                    sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({col})"
                    recommendations.append(
                        {
                            "table": table,
                            "column": col,
                            "reason": "FK column without index",
                            "sql": sql,
                        }
                    )

    # 2) فهارس على أعمدة شائعة
    common_cols = [
        "created_at",
        "updated_at",
        "is_active",
        "status",
        "customer_id",
        "supplier_id",
        "partner_id",
        "warehouse_id",
    ]
    for table, info in schema.items():
        column_names = {c["name"] for c in info.get("columns", []) if c.get("name")}
        for col in common_cols:
            if col in column_names and not existing_by_table_col.get((table, col)):
                idx_name = f"ix_{table}_{col}"
                sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({col})"
                recommendations.append(
                    {
                        "table": table,
                        "column": col,
                        "reason": "common filter column without index",
                        "sql": sql,
                    }
                )

    return recommendations


def main() -> None:
    parser = argparse.ArgumentParser(description="تدقيق شامل + تحسين فهارس قاعدة البيانات.")
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default=os.path.join(basedir, "index"),
        help="مجلد حفظ ملفات الفهرسة (افتراضي: index/ تحت جذر المشروع).",
    )
    parser.add_argument(
        "--apply-indexes",
        action="store_true",
        help="تطبيق فهارس الأداء الجاهزة (ensure_performance_indexes). بدون هذا الخيار يتم الفحص فقط.",
    )
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # 1) تشغيل فهرسة المشروع العامة (Routes/Models/Permissions/...)
    try:
        from scripts import generate_index

        generate_index.run(output_dir=output_dir)
    except Exception as e:
        print(f"[WARN] تعذر تشغيل generate_index.run: {e}")

    from app import create_app
    from extensions import db, ensure_performance_indexes

    app = create_app()

    with app.app_context():
        # 2) فهرسة هيكل القاعدة والفهارس الحالية (قبل أي تعديل)
        print("[INFO] جمع هيكل القاعدة والفهارس الحالية...")
        schema, indexes_before = _collect_db_schema_and_indexes(app, db, output_dir)
        before_path = os.path.join(output_dir, "INDEX_DB_INDEXES_BEFORE.json")
        _dump_json(before_path, indexes_before)

        # توصيات الفهارس (قبل التطبيق)
        print("[INFO] توليد توصيات فهارس إضافية (لا يتم تنفيذها تلقائياً)...")
        recommendations = _build_index_recommendations(schema, indexes_before)
        rec_path_json = os.path.join(output_dir, "INDEX_DB_INDEX_RECOMMENDATIONS.json")
        _dump_json(rec_path_json, recommendations)

        # 3) اختيارياً: تطبيق فهارس الأداء
        if args.apply_indexes:
            print("[INFO] تطبيق فهارس الأداء عبر ensure_performance_indexes...")
            ensure_performance_indexes(app)

            # بعد التطبيق نعيد قراءة الفهارس
            print("[INFO] إعادة جمع الفهارس بعد التطبيق...")
            _, indexes_after = _collect_db_schema_and_indexes(app, db, output_dir)
            after_path = os.path.join(output_dir, "INDEX_DB_INDEXES_AFTER.json")
            _dump_json(after_path, indexes_after)
        else:
            indexes_after = indexes_before

        # 4) ملخص سريع للفروقات بين الفهارس قبل/بعد (حسب الاسم)
        created_indexes = []
        dropped_indexes = []

        before_flat = {
            (table, idx["name"])
            for table, lst in indexes_before.items()
            for idx in lst
        }
        after_flat = {
            (table, idx["name"])
            for table, lst in indexes_after.items()
            for idx in lst
        }

        for key in sorted(after_flat - before_flat):
            created_indexes.append({"table": key[0], "name": key[1]})
        for key in sorted(before_flat - after_flat):
            dropped_indexes.append({"table": key[0], "name": key[1]})

        summary = {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "apply_indexes": bool(args.apply_indexes),
            "created_indexes": created_indexes,
            "dropped_indexes": dropped_indexes,
        }
        summary_path = os.path.join(output_dir, "INDEX_DB_INDEXES_DIFF.json")
        _dump_json(summary_path, summary)

        summary_md = [
            "# ملخص فهارس قاعدة البيانات (قبل/بعد)",
            "",
            f"- تم التوليد في: {summary['generated_at']}",
            f"- تم تطبيق فهارس الأداء؟ {'نعم' if args.apply_indexes else 'لا (فحص فقط)'}",
            "",
            "## فهارس تم إنشاؤها",
        ]
        if created_indexes:
            for item in created_indexes:
                summary_md.append(f"- `{item['table']}` → `{item['name']}`")
        else:
            summary_md.append("- لا يوجد فهارس جديدة.")

        summary_md.append("")
        summary_md.append("## فهارس تم حذفها (من منظور Inspector فقط)")
        if dropped_indexes:
            for item in dropped_indexes:
                summary_md.append(f"- `{item['table']}` → `{item['name']}`")
        else:
            summary_md.append("- لا يوجد فهارس محذوفة.")

        _dump_md(os.path.join(output_dir, "INDEX_DB_INDEXES_DIFF.md"), summary_md)

        print("[INFO] تم الانتهاء من التدقيق والفهرسة. راجع ملفات index/* قبل تثبيتها على الإنتاج.")


if __name__ == "__main__":
    main()

