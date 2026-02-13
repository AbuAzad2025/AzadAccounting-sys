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
        try:
            existing = {c.name.strip().lower(): c for c in ProductCategory.query.all()}
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
        _out("OK added: " + str(added) + " total: " + str(len(existing)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
