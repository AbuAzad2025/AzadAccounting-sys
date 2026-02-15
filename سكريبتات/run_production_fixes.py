#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
تشغيل إصلاحات الإنتاج بأمر واحد.

الاستخدام من جذر المشروع:
  python سكريبتات/run_production_fixes.py --dry-run
  python سكريبتات/run_production_fixes.py --apply

يمكن أيضاً استخدام:
  APPLY=1 لتفعيل التنفيذ الفعلي
  DRY_RUN=1 للمعاينة (يتجاهل apply)
"""
from __future__ import print_function

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _as_bool(v, default=False):
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _has_arg(args, name):
    return any(a.strip().lower() == name for a in args)


def main():
    args = sys.argv[1:]
    env_dry = _as_bool(os.environ.get("DRY_RUN"), False)
    env_apply = _as_bool(os.environ.get("APPLY"), False)
    arg_dry = _has_arg(args, "--dry-run")
    arg_apply = _has_arg(args, "--apply")

    if arg_apply:
        apply = True
        dry_run = False
    elif arg_dry:
        apply = False
        dry_run = True
    else:
        apply = env_apply and not env_dry
        dry_run = not apply

    print("=== تشغيل إصلاحات الإنتاج ===")
    print("الوضع:", "تنفيذ فعلي" if apply else "معاينة (DRY RUN)")

    from سكريبتات import (
        fix_account_types_standalone,
        ensure_gl_accounts_standalone,
        fill_legacy_data_standalone,
        confirm_sales_and_backfill_vat,
        backfill_service_vat_taxentries,
        fix_production_data,
        mark_expenses_fully_paid,
        run_entity_balance_auto_fix,
        fix_sales_sequence,
        purge_test_data,
    )

    print("1) تصحيح أنواع الحسابات")
    fix_account_types_standalone.run_fix_standalone(dry_run=dry_run)

    print("2) ضمان حسابات دفتر الأستاذ")
    ensure_gl_accounts_standalone.run_ensure(dry_run=dry_run)

    print("3) ملء البيانات القديمة الناقصة")
    fill_legacy_data_standalone.run_fill(dry_run=dry_run)

    os.environ["DRY_RUN"] = "1" if dry_run else "0"
    print("4) تأكيد المبيعات وملء ضريبة VAT")
    confirm_sales_and_backfill_vat.run()

    print("5) ملء ضريبة VAT للخدمات")
    backfill_service_vat_taxentries.run()

    print("6) إصلاح بيانات المدفوعات والسِبلِت")
    fix_production_data.fix_production_data(dry_run=dry_run)

    if apply:
        print("7) إكمال مدفوعات المصاريف")
        mark_expenses_fully_paid.run()

        print("8) تصحيح أرصدة العملاء/الموردين/الشركاء")
        run_entity_balance_auto_fix.run()

        print("9) مزامنة تسلسلات Postgres وتصحيح seller_id")
        fix_sales_sequence.main()
        
        print("10) حذف بيانات الاختبار (Purge)")
        os.environ["CONFIRM_DELETE"] = "1"
        os.environ["CONFIRM_PHRASE"] = "DELETE_TEST_DATA"
        purge_test_data.run()
    else:
        print("7) تخطي mark_expenses_fully_paid (يتطلب تنفيذ فعلي)")
        print("8) تخطي run_entity_balance_auto_fix (يتطلب تنفيذ فعلي)")
        print("9) تخطي fix_sales_sequence (يتطلب تنفيذ فعلي)")
        print("10) تخطي purge_test_data (يتطلب تنفيذ فعلي)")

    print("=== انتهى التنفيذ ===")


if __name__ == "__main__":
    main()
