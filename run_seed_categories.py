#!/usr/bin/env python
# تشغيل زرع فئات المنتجات محلياً (بدون الاعتماد على flask cli)
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
    app = create_app()
    with app.app_context():
        existing = {c.name.strip().lower(): c for c in ProductCategory.query.all()}
        added = 0
        for name in CATEGORIES:
            name = (name or "").strip()
            if not name or name.lower() in existing:
                continue
            c = ProductCategory(name=name)
            db.session.add(c)
            existing[name.lower()] = c
            added += 1
            print(f"  + {name}")
        db.session.commit()
        print(f"✅ تمت إضافة {added} فئة. (الإجمالي: {len(existing)})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
