# سكريبتات تحسين قاعدة الإنتاج

هذا المجلد مخصّص لسكريبتات تُطبَّق على البيئة المحلية أولاً، ثم تُحفَظ لاستخدامها عند **تحديث قاعدة بيانات الإنتاج**.

**تنفيذ السكريبتات:** من جذر المشروع `garage_manager` (نفس الـ venv إن وُجد). **قبل التطبيق على الإنتاج خذ نسخة احتياطية من قاعدة البيانات.**

---

## ترتيب التنفيذ عند تحديث الإنتاج

1. **نسخة احتياطية** من قاعدة الإنتاج.
2. **تهجيرات قاعدة البيانات** (إن وُجدت):
   ```bash
   python -m flask db upgrade
   ```
   أو تنفيذ ملف SQL يدوياً إن كان لديك runbook (مثل `production_update_20260206.sql`).
3. **تصحيح أنواع الحسابات** — `fix_account_types_standalone.py`
4. **ضمان حسابات دفتر الأستاذ** — `ensure_gl_accounts_standalone.py`
5. **ملء البيانات القديمة الناقصة** — `fill_legacy_data_standalone.py`

---

## السكريبتات المتوفرة

### 1) تصحيح أنواع الحسابات — `fix_account_types_standalone.py`

يصحّح عمود `type` في جدول `accounts` حسب أول رقم في `code` ليتوافق مع النظام الجديد:

| أول رقم | النوع      |
|---------|------------|
| 1       | ASSET      |
| 2       | LIABILITY  |
| 3       | EQUITY     |
| 4       | REVENUE    |
| 5 أو 6  | EXPENSE    |

**تشغيل (من جذر المشروع):**

```bash
# معاينة فقط (لا يغيّر البيانات)
python سكريبتات/fix_account_types_standalone.py --dry-run

# تنفيذ التصحيح
python سكريبتات/fix_account_types_standalone.py
```

يدعم SQLite و PostgreSQL (يحتاج `psycopg2-binary` على الإنتاج).

---

### 2) ضمان حسابات دفتر الأستاذ — `ensure_gl_accounts_standalone.py`

يُدرج أي **حساب ناقص** في جدول `accounts` من القائمة المرجعية للنظام الجديد، ومنها:

- ضريبة الدخل: `6200_INCOME_TAX_EXPENSE`, `2200_INCOME_TAX_PAYABLE`
- ضريبة القيمة المضافة: `2100_VAT_PAYABLE`
- المبيعات والإيرادات والخصوم والأصول والمصروفات الشائعة

بهذا تتوافق البيانات القديمة مع القيود والتقارير الجديدة (قائمة الدخل، استحقاق ضريبة الدخل، الميزانية العمومية).

**تشغيل:**

```bash
# معاينة الحسابات التي ستُدرج فقط
python سكريبتات/ensure_gl_accounts_standalone.py --dry-run

# إدراج الحسابات الناقصة
python سكريبتات/ensure_gl_accounts_standalone.py
```

لا يحذف ولا يعدّل حسابات موجودة؛ يضيف فقط الحسابات المفقودة.

---

### 3) ملء البيانات القديمة الناقصة — `fill_legacy_data_standalone.py`

**مهم:** حتى لو كان **عمود ناقص** في قاعدة قديمة، السكريبت يضيف العمود (إن وُجد الجدول) ثم يملأ القيم. بهذا تبقى كل البيانات متوافقة مع النظام ولا يحدث خلل بسبب بيانات قديمة.

يُنفّذ مرحلتين:
1. **ضمان الأعمدة (SQLite/PostgreSQL):** إن لم يكن العمود موجوداً يُضاف بقيمة افتراضية (مثل `currency`, `status`, `payment_status`, `method`, `payment_number`, …).
2. **ملء البيانات:** تحديث السجلات التي تحتوي على حقول **NULL** أو **فارغة** بقيم مناسبة:

- **عملة:** تعيين `currency = 'ILS'` حيث القيمة ناقصة (مبيعات، فواتير، دفعات، مصروفات، صيانة، عملاء، موردين، شركاء، إلخ).
- **حسابات رقمية:** تعيين 0 (أو 0.01 للدفعات/البنود التي تتطلب قيمة موجبة) للحقول مثل `total_amount`, `tax_rate`, `quantity`, `unit_price`, وأرصدة العملاء/الموردين/الشركاء.
- **حالة واتجاه:** تعيين قيم افتراضية لـ `status`, `payment_status`, `method`, `direction`, `entity_type` في المبيعات والدفعات وطلبات الصيانة وبنود المرتجع (`condition = 'GOOD'`).
- **نصوص إلزامية:** تعيين أسماء/هواتف/وصف مناسبة (مثل «عميل غير محدد», «—») للعملاء/الموردين/الشركاء وبنود الفواتير.
- **دفعات:** تعيين `payment_number = 'LEGACY-' || id` للسجلات التي تفتقد رقم السند.

**تشغيل:**

```bash
# معاينة (بدون حفظ)
python سكريبتات/fill_legacy_data_standalone.py --dry-run

# تنفيذ التحديثات (إضافة أعمدة ناقصة + ملء)
python سكريبتات/fill_legacy_data_standalone.py
```

يُنفّذ بعد تصحيح أنواع الحسابات وضمان حسابات GL. التهجيرة `d4e5f6a7b8c9_legacy_columns_and_data_backfill` تملأ البيانات فقط (تفترض أن الأعمدة من التهجيرات السابقة). لضمان وجود الأعمدة ثم الملء على قواعد قديمة جداً استخدم هذا السكريبت.

---

### 4) تصحيح أنواع الحسابات (مع تحميل التطبيق) — `fix_account_types.py`

نسخة تعتمد على Flask و SQLAlchemy. إن ظهر خطأ استيراد (مثلاً `ModuleNotFoundError`) استخدم النسخة المستقلة أعلاه.

```bash
python سكريبتات/fix_account_types.py --dry-run
python سكريبتات/fix_account_types.py
```

أو من `flask shell`:

```python
from سكريبتات.fix_account_types import run_fix
run_fix(dry_run=True)
run_fix(dry_run=False)
```

---

## تنفيذ سريع على الإنتاج (بعد النسخة الاحتياطية)

```bash
cd /path/to/garage_manager

# 1) التهجيرات
python -m flask db upgrade

# 2) تصحيح أنواع الحسابات (معاينة ثم تنفيذ)
python سكريبتات/fix_account_types_standalone.py --dry-run
python سكريبتات/fix_account_types_standalone.py

# 3) ضمان حسابات GL (معاينة ثم تنفيذ)
python سكريبتات/ensure_gl_accounts_standalone.py --dry-run
python سكريبتات/ensure_gl_accounts_standalone.py

# 4) ملء البيانات القديمة الناقصة (معاينة ثم تنفيذ)
python سكريبتات/fill_legacy_data_standalone.py --dry-run
python سكريبتات/fill_legacy_data_standalone.py
```

ثم أعد تشغيل خدمة التطبيق.

---

## ملاحظات

- السكريبتات المستقلة (`*_standalone.py`) تعتمد على `config` واتصال قاعدة البيانات من متغيرات البيئة (`DATABASE_URL` أو `PGHOST`/`PGDATABASE`/`PGUSER`/`PGPASSWORD`) أو على وجود `instance/garage.db` في SQLite.
- على الإنتاج تأكد أن متغيرات البيئة تشير إلى قاعدة الإنتاج قبل التشغيل.
- للمزيد عن التهجيرات وملفات SQL الخاصة بالإنتاج راجع `PRODUCTION_MIGRATION_RUNBOOK_20260206.md` و `UPDATE_PRODUCTION.md` في جذر المشروع.
