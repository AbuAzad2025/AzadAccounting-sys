#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
سكريبت تصحيح أنواع الحسابات (Account.type) في جدول accounts.

يُحدّث النوع حسب أول رقم في كود الحساب:
  1 → ASSET
  2 → LIABILITY
  3 → EQUITY
  4 → REVENUE
  5 أو 6 → EXPENSE
  غير ذلك → ASSET (افتراضي)

الاستخدام من جذر المشروع:
  python سكريبتات/fix_account_types.py [--dry-run]
  أو:
  flask shell
  >>> from سكريبتات.fix_account_types import run_fix
  >>> run_fix(dry_run=False)

إذا ظهر خطأ في الاستيراد (مثلاً ModuleNotFoundError)، استخدم النسخة المستقلة:
  python سكريبتات/fix_account_types_standalone.py [--dry-run]
"""
from __future__ import print_function

import os
import sys

# تشغيل من جذر المشروع
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def type_from_code(code):
    """استنتاج النوع المحاسبي من أول حرف في الكود."""
    if not code or not code.strip():
        return "ASSET"
    c = (code.strip().upper())[0]
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


def run_fix(dry_run=True):
    from app import app
    from models import db, Account

    with app.app_context():
        accounts = Account.query.all()
        to_update = []
        for acc in accounts:
            expected = type_from_code(acc.code)
            current = getattr(acc.type, "value", acc.type) if hasattr(acc.type, "value") else acc.type
            if (current or "").upper() != (expected or "").upper():
                to_update.append((acc, current, expected))

        if not to_update:
            print("لا توجد حسابات تحتاج تصحيح.")
            return {"updated": 0, "corrected": []}

        if dry_run:
            print("وضع جاف (dry-run) — الحسابات التي ستُصحّح:")
            for acc, current, expected in to_update:
                print("  {} | {} → {} ({})".format(acc.code, current, expected, acc.name or ""))
            print("عدد الحسابات: {}".format(len(to_update)))
            return {"updated": 0, "dry_run": True, "would_update": len(to_update), "corrected": [(a.code, c, e) for a, c, e in to_update]}

        corrected = []
        for acc, _current, expected in to_update:
            acc.type = expected
            corrected.append((acc.code, expected))
        db.session.commit()
        print("تم تصحيح {} حساباً.".format(len(corrected)))
        for code, typ in corrected:
            print("  {} → {}".format(code, typ))
        return {"updated": len(corrected), "corrected": corrected}


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    run_fix(dry_run=dry_run)
