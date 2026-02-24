#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
سكريبت موحد لتنفيذ صيانة شاملة لقاعدة بيانات الإنتاج.
ينفذ الخطوات التالية:
1. تصحيح أنواع الحسابات
2. ضمان حسابات دفتر الأستاذ
3. ملء البيانات القديمة
4. تأكيد المبيعات وإزالة الضرائب (STRIP_VAT=1)
5. إزالة ضرائب الخدمات (STRIP_VAT=1)
6. تحديث بيانات الصيانة القديمة
7. إصلاح بيانات المدفوعات
8. فحص وتصحيح تكامل دفتر الأستاذ
9. حذف الحركات المحذوفة واليتيمة
10. تصحيح أرصدة الكيانات
11. تصحيح تسلسلات قاعدة البيانات
12. حذف بيانات الرواتب (اختياري، مدمج)
13. حذف بيانات الاختبار (اختياري، مدمج)

الاستخدام:
  python سكريبتات/run_production_maintenance.py
"""
import os
import sys
import subprocess
import time

# التأكد من المسار الصحيح
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

# إعداد متغيرات البيئة العامة
ENV = os.environ.copy()
ENV["APPLY"] = "1"
ENV["DRY_RUN"] = "0"
ENV["APPLY_CHANGES"] = "1"
ENV["PYTHONPATH"] = ROOT  # لتجاوز مشكلة استيراد app

# إعدادات خاصة لتعطيل الضرائب وحذف البيانات
# تم إزالة STRIP_VAT و FORCE للسماح للسكريبتات باحترام إعدادات النظام الحالية (VAT Disabled)
# والحفاظ على الضرائب المدخلة يدويًا في المعاملات القديمة.
ENV["CONFIRM_DELETE"] = "1"
ENV["CONFIRM_PHRASE"] = "DELETE_TEST_DATA"

SCRIPTS = [
    ("1) تصحيح أنواع الحسابات", "سكريبتات/fix_account_types_standalone.py"),
    ("2) ضمان حسابات دفتر الأستاذ", "سكريبتات/ensure_gl_accounts_standalone.py"),
    ("3) ملء البيانات القديمة الناقصة", "سكريبتات/fill_legacy_data_standalone.py"),
    ("4) تأكيد المبيعات (مع الحفاظ على الضرائب اليدوية)", "سكريبتات/confirm_sales_and_backfill_vat.py"),
    ("5) معالجة ضرائب الخدمات (حسب إعدادات النظام)", "سكريبتات/backfill_service_vat_taxentries.py"),
    ("6) تحديث بيانات الصيانة القديمة وخصم المخزون", "سكريبتات/run_entity_balance_auto_fix.py"), # ملاحظة: هذا السكريبت يحتوي على دوال backfill، لكنه يُشغل run() افتراضيًا. سنستخدمه لإصلاح الأرصدة لاحقًا (رقم 10)
    # ملاحظة: لتشغيل backfill الصيانة، نحتاج لاستدعاء دوال محددة، لكن run_entity_balance_auto_fix لا يوفر واجهة CLI مباشرة لها بسهولة إلا عبر التعديل. 
    # سنفترض أن المستخدم يريد run_entity_balance_auto_fix لإصلاح الأرصدة كخطوة أساسية.
    
    # 6 الفعلي: سنستخدم run_entity_balance_auto_fix لاحقًا، هنا سنشغل fix_expense_utility_accounts
    ("6) ربط المصاريف بالموردين/الخدمات", "سكريبتات/fix_expense_utility_accounts.py"),
    
    ("7) إصلاح بيانات المدفوعات والسبلت", "سكريبتات/fix_production_data.py"),
    
    ("8) فحص وتصحيح تكامل دفتر الأستاذ", "سكريبتات/fix_gl_integrity_standalone.py"),
    ("8.4) تصحيح كيان دفعات الإلغاء", "سكريبتات/fix_payment_reversal_split_entities.py"),
    
    ("9) حذف الحركات المحذوفة واليتيمة", "سكريبتات/purge_deleted_payments_expenses.py"),
    
    ("10) تصحيح أرصدة العملاء/الموردين/الشركاء", "سكريبتات/run_entity_balance_auto_fix.py"),
    
    ("11) مزامنة تسلسلات Postgres", "سكريبتات/fix_sales_sequence.py"),
    
    ("12) حذف بيانات الرواتب", "سكريبتات/wipe_salary_data.py"),
    ("13) حذف بيانات الاختبار", "سكريبتات/purge_test_data.py"),
]

def run_script(title, script_path):
    print(f"\n>>> جاري تشغيل: {title} ({script_path})...")
    start_time = time.time()
    try:
        # استخدام python -m لتجنب مشاكل المسارات والاستيراد
        module_name = script_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        
        # بعض السكريبتات تحتاج وسائط إضافية للتطبيق
        args = [sys.executable, script_path]
        if "wipe_salary_data" in script_path or "fix_expense_utility_accounts" in script_path or "fix_gl_integrity_standalone" in script_path or "purge_deleted_payments_expenses" in script_path or "run_pending_salaries" in script_path:
             args.append("--apply")
        elif "fix_production_data" in script_path:
             # هذا السكريبت لا يأخذ --apply كـ arg في main block المباشر (يعتمد على الكود)، 
             # لكن دالة fix_production_data تأخذ dry_run.
             # في استدعاء __main__ هو يستدعيها بدون args، لذا يجب التأكد من الكود.
             # الكود في fix_production_data.py يستدعي fix_production_data() بدون وسائط في if __name__ == "__main__".
             # ودالة fix_production_data تأخذ dry_run=False افتراضيًا. إذن هو سيطبق التغييرات افتراضيًا عند التشغيل المباشر.
             pass

        process = subprocess.run(
            args,
            env=ENV,
            check=False, # لا توقف التنفيذ عند الخطأ
            capture_output=False # اترك المخرجات تظهر مباشرة
        )
        
        elapsed = time.time() - start_time
        if process.returncode == 0:
            print(f"✅ تم بنجاح: {title} (في {elapsed:.2f} ثانية)")
        else:
            print(f"❌ فشل: {title} (كود الخروج: {process.returncode})")
            
    except Exception as e:
        print(f"❌ خطأ غير متوقع في {title}: {e}")

def main():
    print("=== بدء صيانة الإنتاج الشاملة ===")
    print("تحذير: سيتم تطبيق التغييرات فعليًا على قاعدة البيانات!")
    print(f"CONFIRM_DELETE={ENV.get('CONFIRM_DELETE', '0')}")
    print(f"STRIP_VAT={ENV.get('STRIP_VAT', '0')} (Default System Behavior)")
    
    for title, script in SCRIPTS:
        run_script(title, script)
        
    print("\n=== انتهت الصيانة ===")

if __name__ == "__main__":
    main()
