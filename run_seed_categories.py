#!/usr/bin/env python
import os
import sys

_ = os.chdir(os.path.dirname(os.path.abspath(__file__)))

def _out(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))

from app import create_app
from extensions import db
from models import ProductCategory
from sqlalchemy import text

CATEGORIES = [
    "محركات", "قطع غيار", "GEARBOX", "HYD PUMP", "HYD PARTS", "كوبلنات", "فلاتر", "بخاخات",
    "محركات ديزل", "جلود اهتزاز", "زيوت وشحمة", "الكترونيات", "كسكيتات", "مراوح تبريد",
    "برابيش هواء وماء ماتور", "رديترات", "قطع محركات جديدة", "متفرقات", "قطع محركات مستعملة",
    "معدات", "خدمات", "مولدات وماكنات", "شحن وجمرك",
]

def main():
    try:
        app = create_app()
    except Exception as e:
        _out("ERROR create_app: " + str(e))
        return 1
    with app.app_context():
        # Show DB target to avoid seeding the wrong database (common in production).
        try:
            url = db.engine.url.render_as_string(hide_password=True)
        except Exception:
            url = "<unknown>"
        _out("DB: " + str(url))
        if str(url).startswith("sqlite:///") and os.environ.get("ALLOW_SQLITE_SEED", "").strip() != "1":
            _out("ERROR: Detected SQLite DB. Refusing to seed unless ALLOW_SQLITE_SEED=1 is set.")
            _out("Tip: ensure DATABASE_URL/SQLALCHEMY_DATABASE_URI is set for production.")
            return 2
        try:
            db.session.execute(text("SELECT 1"))
        except Exception as e:
            _out("ERROR DB connectivity: " + str(e))
            return 1
        try:
            existing = {(c.name or "").strip().lower(): c for c in ProductCategory.query.all()}
        except Exception as e:
            _out("ERROR query ProductCategory: " + str(e))
            return 1
        _out("Existing categories count: " + str(len(existing)))
        added = 0
        for name in CATEGORIES:
            name = (name or "").strip()
            if not name or name.lower() in existing:
                continue
            c = ProductCategory(name=name)
            db.session.add(c)
            existing[name.lower()] = c
            added += 1
            _out("  + " + name)
        try:
            db.session.commit()
        except Exception as e:
            _out("ERROR commit: " + str(e))
            db.session.rollback()
            return 1
        try:
            total_now = ProductCategory.query.count()
        except Exception:
            total_now = len(existing)
        _out("OK added: " + str(added) + " total: " + str(total_now))
    return 0

if __name__ == "__main__":
    sys.exit(main())
