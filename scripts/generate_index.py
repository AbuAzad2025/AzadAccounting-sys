#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
فهرسة شاملة للمشروع — قابلة للتشغيل محلياً أو على سيرفر الإنتاج.

يولّد في مجلد index/ (أو مسار يُحدد بـ --output-dir):
  INDEX_META.json      — وقت التوليد، أعداد المكونات، بيئة التشغيل
  INDEX_ROUTES.json    — كل مسارات التطبيق
  INDEX_ROUTES.md
  INDEX_MODELS.json    — النماذج (جدول ↔ كلاس)
  INDEX_MODELS.md
  INDEX_PERMISSIONS.json — الصلاحيات والأدوار
  INDEX_PERMISSIONS.md
  INDEX_BLUEPRINTS.json  — الـ Blueprints ومساراتها وصلاحيات ACL
  INDEX_BLUEPRINTS.md
  INDEX_FORMS.json    — نماذج Flask-WTF
  INDEX_FORMS.md
  INDEX_SERVICES.md   — قائمة خدمات services/
  INDEX_TEMPLATES.json — قائمة ملفات القوالب (مجلدات وعدد الملفات)
  INDEX_SUMMARY.md    — ملخص الفهرسة وتواريخ التحديث

استخدام (من جذر المشروع مع تفعيل venv):
  python scripts/generate_index.py
  python scripts/generate_index.py --output-dir /var/www/app/index
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


def _collect_models(db):
    """جمع كل النماذج التي لها __tablename__ (من db.Model)."""
    collected = []
    seen = set()
    stack = [db.Model]
    while stack:
        cls = stack.pop()
        for sub in cls.__subclasses__():
            if sub in seen:
                continue
            seen.add(sub)
            collected.append(sub)
            stack.append(sub)
    return [c for c in collected if hasattr(c, "__tablename__")]


def _collect_forms():
    """جمع كل كلاسات النماذج (FlaskForm) من forms."""
    try:
        import forms as forms_module
        from flask_wtf import FlaskForm
        out = []
        for name in dir(forms_module):
            obj = getattr(forms_module, name)
            if (
                isinstance(obj, type)
                and issubclass(obj, FlaskForm)
                and obj is not FlaskForm
            ):
                out.append(name)
        return sorted(out)
    except Exception:
        return []


def _list_templates(root: str) -> dict:
    """قائمة مجلدات القوالب وعدد الملفات في كل منها."""
    templates_dir = os.path.join(root, "templates")
    if not os.path.isdir(templates_dir):
        return {}
    out = {}
    for name in sorted(os.listdir(templates_dir)):
        path = os.path.join(templates_dir, name)
        if os.path.isdir(path):
            count = sum(1 for _, __, files in os.walk(path) for f in files if f.endswith((".html", ".htm", ".jinja2")))
            out[name] = count
        elif name.endswith((".html", ".htm", ".jinja2")):
            out["(root)"] = out.get("(root)", 0) + 1
    return out


def _list_services(root: str) -> list[str]:
    """قائمة ملفات الخدمات (services/*.py)."""
    services_dir = os.path.join(root, "services")
    if not os.path.isdir(services_dir):
        return []
    return [
        f for f in sorted(os.listdir(services_dir))
        if f.endswith(".py") and not f.startswith("_")
    ]


def run(output_dir: str | None = None) -> None:
    output_dir = output_dir or os.path.join(basedir, "index")
    os.makedirs(output_dir, exist_ok=True)

    from app import create_app
    from extensions import db

    app = create_app()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with app.app_context():
        # —— Routes ——
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith("static"):
                continue
            methods = sorted(m for m in (rule.methods or set()) if m not in {"HEAD", "OPTIONS"})
            routes.append({"rule": rule.rule, "endpoint": rule.endpoint, "methods": methods})
        routes.sort(key=lambda x: (x["rule"], x["endpoint"]))

        # —— Models ——
        model_classes = _collect_models(db)
        models = [{"table": getattr(c, "__tablename__"), "class": c.__name__} for c in model_classes]
        models.sort(key=lambda x: (x["table"] or "", x["class"]))

        # —— Permissions & Roles ——
        from permissions_config.enums import SystemPermissions, SystemRoles
        permissions = [{"name": p.name, "value": p.value} for p in SystemPermissions]
        roles = [{"name": r.name, "value": r.value} for r in SystemRoles]

        # —— Blueprints ——
        from permissions_config.blueprint_guards import get_blueprint_guard_config
        guard_map = {name: opts for name, opts in get_blueprint_guard_config()}
        blueprints = []
        for bp_name, bp_obj in sorted(app.blueprints.items()):
            url_prefix = getattr(bp_obj, "url_prefix", None) or ""
            acl = guard_map.get(bp_name, {})
            blueprints.append({
                "name": bp_name,
                "url_prefix": url_prefix,
                "read_perm": acl.get("read_perm"),
                "write_perm": acl.get("write_perm"),
            })

        # —— Forms ——
        forms = _collect_forms()

        # —— Services (من الملفات) ——
        services = _list_services(basedir)

        # —— Templates (إحصائيات) ——
        templates_by_dir = _list_templates(basedir)
        template_total = sum(templates_by_dir.values())

    # —— Meta ——
    meta = {
        "generated_at": generated_at,
        "python_version": sys.version.split()[0],
        "flask_env": os.environ.get("FLASK_ENV", os.environ.get("APP_ENV", "")),
        "counts": {
            "routes": len(routes),
            "models": len(models),
            "permissions": len(permissions),
            "roles": len(roles),
            "blueprints": len(blueprints),
            "forms": len(forms),
            "services": len(services),
            "templates": template_total,
        },
    }

    def write_json(name: str, data: object) -> None:
        path = os.path.join(output_dir, f"INDEX_{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def write_md(name: str, lines: list[str]) -> None:
        path = os.path.join(output_dir, f"INDEX_{name}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # حفظ الملفات
    write_json("META", meta)

    write_json("ROUTES", routes)
    md_routes = ["# فهرس المسارات (Routes)\n", "| المسار | Endpoint | الطرق |", "|--------|----------|-------|"]
    for r in routes:
        md_routes.append(f"| {r['rule']} | {r['endpoint']} | {', '.join(r['methods']) or '-'} |")
    write_md("ROUTES", md_routes)

    write_json("MODELS", models)
    md_models = ["# فهرس النماذج (Models)\n", "| الجدول | الكلاس |", "|--------|--------|"]
    for m in models:
        md_models.append(f"| {m['table']} | {m['class']} |")
    write_md("MODELS", md_models)

    perms_data = {"permissions": permissions, "roles": roles}
    write_json("PERMISSIONS", perms_data)
    md_perms = ["# فهرس الصلاحيات والأدوار\n", "## SystemPermissions", "| الاسم | القيمة |", "|-------|--------|"]
    for p in permissions:
        md_perms.append(f"| {p['name']} | {p['value']} |")
    md_perms.append("\n## SystemRoles\n| الاسم | القيمة |\n|-------|--------|")
    for r in roles:
        md_perms.append(f"| {r['name']} | {r['value']} |")
    write_md("PERMISSIONS", md_perms)

    write_json("BLUEPRINTS", blueprints)
    md_bp = ["# فهرس Blueprints\n", "| الاسم | url_prefix | read_perm | write_perm |", "|------|------------|-----------|------------|"]
    for b in blueprints:
        md_bp.append(f"| {b['name']} | {b['url_prefix']} | {b['read_perm'] or '-'} | {b['write_perm'] or '-'} |")
    write_md("BLUEPRINTS", md_bp)

    write_json("FORMS", forms)
    md_forms = ["# فهرس النماذج (Forms)\n"] + [f"- {f}" for f in forms]
    write_md("FORMS", md_forms)

    write_json("TEMPLATES", {"by_directory": templates_by_dir, "total": template_total})
    md_tpl = ["# إحصائيات القوالب (Templates)\n", "| المجلد | عدد الملفات |", "|--------|-------------|"]
    for d, c in sorted(templates_by_dir.items(), key=lambda x: -x[1]):
        md_tpl.append(f"| {d} | {c} |")
    md_tpl.append(f"\n**المجموع:** {template_total}")
    write_md("TEMPLATES", md_tpl)

    # INDEX_SERVICES (بدون JSON؛ قائمة بسيطة)
    md_svc = ["# فهرس الخدمات (services/)\n"] + [f"- {s}" for s in services]
    write_md("SERVICES", md_svc)

    # INDEX_SUMMARY.md — ملخص واحد
    summary = [
        "# ملخص الفهرسة",
        "",
        f"**تاريخ التوليد:** {generated_at}",
        "",
        "## الأعداد",
        f"- مسارات (Routes): {meta['counts']['routes']}",
        f"- نماذج (Models): {meta['counts']['models']}",
        f"- صلاحيات: {meta['counts']['permissions']}",
        f"- أدوار: {meta['counts']['roles']}",
        f"- Blueprints: {meta['counts']['blueprints']}",
        f"- نماذج ويب (Forms): {meta['counts']['forms']}",
        f"- خدمات (services/): {meta['counts']['services']}",
        f"- قوالب (templates): {meta['counts']['templates']}",
        "",
        "## الملفات المُولَّدة",
        "- INDEX_META.json",
        "- INDEX_ROUTES.json / INDEX_ROUTES.md",
        "- INDEX_MODELS.json / INDEX_MODELS.md",
        "- INDEX_PERMISSIONS.json / INDEX_PERMISSIONS.md",
        "- INDEX_BLUEPRINTS.json / INDEX_BLUEPRINTS.md",
        "- INDEX_FORMS.json / INDEX_FORMS.md",
        "- INDEX_TEMPLATES.json / INDEX_TEMPLATES.md",
        "- INDEX_SERVICES.md",
        "- INDEX_SUMMARY.md (هذا الملف)",
        "",
        "لتحديث الفهرسة على سيرفر الإنتاج:",
        "  python scripts/generate_index.py",
        "  أو: python scripts/generate_index.py --output-dir /path/to/index",
    ]
    write_md("SUMMARY", summary)

    print(f"تمت الفهرسة بنجاح → {output_dir}")
    print(f"  مسارات: {len(routes)} | نماذج: {len(models)} | صلاحيات: {len(permissions)} | Blueprints: {len(blueprints)} | نماذج ويب: {len(forms)}")
    print(f"  الخلاصة: INDEX_SUMMARY.md")


def main():
    parser = argparse.ArgumentParser(description="فهرسة شاملة للمشروع (محلي أو إنتاج)")
    parser.add_argument("--output-dir", "-o", default=None, help="مجلد حفظ الملفات (افتراضي: index/)")
    args = parser.parse_args()
    run(output_dir=args.output_dir)


if __name__ == "__main__":
    main()
