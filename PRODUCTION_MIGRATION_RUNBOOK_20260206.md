# Runbook هجرة الإنتاج - 2026-02-06

## الملخص

- نسخة الإنتاج (حسب `instance/backup_20260206_120540.dump`) على:
  - PostgreSQL: 12.2
  - Alembic version: `79cf2ae42e8e`
- آخر تهجيرة موجودة في الكود حالياً:
  - Alembic head: `c3a0f1b8d2e4`
- المطلوب على الإنتاج:
  - تطبيق تهجرتين بالترتيب:
    - `b1a3f0c6d8a9` (إضافة فهارس مركبة للتسويات)
    - `c3a0f1b8d2e4` (توسيع قيود `payee_type` في جدول المصروفات)

## ما الذي سيتغير

### 1) فهارس جديدة (Indexes)

- `exchange_transactions`
  - `ix_exchange_supplier_dir_created_at` على (`supplier_id`, `direction`, `created_at`)
  - `ix_exchange_partner_dir_created_at` على (`partner_id`, `direction`, `created_at`)
- `payments`
  - `ix_pay_supplier_dir_status_date` على (`supplier_id`, `direction`, `status`, `payment_date`)
  - `ix_pay_partner_dir_status_date` على (`partner_id`, `direction`, `status`, `payment_date`)
  - `ix_pay_customer_dir_status_date` على (`customer_id`, `direction`, `status`, `payment_date`)
- `expenses`
  - `ix_expense_payee_type_entity_date` على (`payee_type`, `payee_entity_id`, `date`)

### 2) تحديث قيد (Check Constraint) على `expenses.payee_type`

- اسم القيد: `ck_expense_payee_type_allowed`
- قبل: `('EMPLOYEE','SUPPLIER','PARTNER','UTILITY','OTHER')`
- بعد: `('EMPLOYEE','SUPPLIER','CUSTOMER','PARTNER','WAREHOUSE','SHIPMENT','UTILITY','OTHER')`

## قبل التنفيذ (Pre-flight)

### 1) أخذ نسخة احتياطية جديدة

نفّذ Backup جديد من الإنتاج قبل أي تغيير.

### 2) التحقق من نسخة Alembic الحالية

على قاعدة الإنتاج:

```sql
SELECT version_num FROM public.alembic_version;
```

المتوقع قبل التنفيذ: `79cf2ae42e8e`

### 3) التحقق من وجود الجداول المستهدفة

```sql
SELECT to_regclass('public.exchange_transactions') AS exchange_transactions,
       to_regclass('public.payments')              AS payments,
       to_regclass('public.expenses')              AS expenses;
```

### 4) نافذة صيانة

- تنفيذ الفهارس بدون `CONCURRENTLY` قد يقفل جداول كبيرة أثناء بناء الفهرس.
- إذا كانت الجداول كبيرة، نفّذ الخيار اليدوي مع `CONCURRENTLY` (الخيار B) أو نفّذ التهجيرات خلال نافذة صيانة.

## الخيار A (المفضل): تشغيل التهجيرات عبر Flask-Migrate

1) تحديث الكود على سيرفر الإنتاج إلى آخر نسخة.
2) تفعيل البيئة الافتراضية.
3) تنفيذ:

```bash
python -m flask db upgrade
```

## الخيار B: تنفيذ يدوي عبر SQL (Fallback)

استخدم الملف:

- `production_update_20260206.sql`

وشغّله:

```bash
psql -h <host> -U <username> -d <database_name> -f production_update_20260206.sql
```

## بعد التنفيذ (Post-flight)

### 1) التحقق من نسخة Alembic

```sql
SELECT version_num FROM public.alembic_version;
```

المتوقع: `c3a0f1b8d2e4`

### 2) التحقق من الفهارس

```sql
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname IN (
    'ix_exchange_supplier_dir_created_at',
    'ix_exchange_partner_dir_created_at',
    'ix_pay_supplier_dir_status_date',
    'ix_pay_partner_dir_status_date',
    'ix_pay_customer_dir_status_date',
    'ix_expense_payee_type_entity_date'
  )
ORDER BY tablename, indexname;
```

### 3) التحقق من قيد `payee_type`

```sql
SELECT conname, pg_get_constraintdef(c.oid)
FROM pg_constraint c
JOIN pg_class t ON t.oid = c.conrelid
JOIN pg_namespace n ON n.oid = t.relnamespace
WHERE n.nspname = 'public'
  AND t.relname = 'expenses'
  AND c.conname = 'ck_expense_payee_type_allowed';
```

### 4) إعادة تشغيل الخدمة

أعد تشغيل خدمة التطبيق حسب آلية التشغيل عندك (systemd/gunicorn/…).

