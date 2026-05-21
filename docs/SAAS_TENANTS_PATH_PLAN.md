# خطة SaaS (Path‑based) + Schema‑per‑Tenant

## الهدف
- تشغيل أكثر من Tenant داخل نفس تطبيق Flask ونفس قاعدة بيانات PostgreSQL.
- عزل كامل للبيانات عبر PostgreSQL schema لكل Tenant (مثال: `t_nasrallah`, `t_alhazem`).
- فصل صارم بين لوحة المنصة (Platform Owner / Master) وبين لوحات الـ Tenants.
- توجيه Path‑based مناسب لـ PythonAnywhere: `/t/<slug>/...` بدل الاعتماد على subdomain.

## المصطلحات
- Platform: الدومين/المسار الأساسي بدون `/t/<slug>` ويخص مالك الشركة (Master).
- Tenant Scope: أي طلب يبدأ بـ `/t/<slug>` ويخص Tenant واحد فقط.
- Tenant Registry: جدول مركزي في `public` يعرّف جميع الـ Tenants.

## المراحل

### مرحلة 0: Tenant Registry (آمنة)
- إضافة جدول `tenants` في `public`:
  - `slug` (unique)
  - `schema_name` (unique)
  - `display_name`
  - `domain` (اختياري للمستقبل)
  - `is_active`
- لا تغيير على الاستعلامات ولا `search_path` في هذه المرحلة.

### مرحلة 1: Resolver (Path‑based) بدون عزل
- استخراج `tenant_slug` من المسار: `/t/<slug>/...`
- تعيين:
  - `g.tenant_slug`
  - `g.tenant_schema_name` من الـ registry
- حقن معلومات الـ tenant في القوالب للعرض فقط (بدون تغيير البيانات).

### مرحلة 2: Guards (فصل المنصة/التينانت)
- على Platform scope:
  - منع الوصول لصفحات tenant‑only (مثل dashboards/عمليات).
- على Tenant scope:
  - منع الوصول لصفحات المنصة الحساسة (`/security/*`, `/advanced/*`) إلا إذا كانت مخصصة لمالك التينانت داخل الـ tenant scope (حسب قرارنا لاحقاً).

### مرحلة 3: العزل الحقيقي (Schema Switching)
- عند بداية كل Request داخل Tenant scope:
  - استخدام `SET LOCAL search_path TO <tenant_schema>, public` على نفس connection.
- الاعتماد على `SET LOCAL` لضمان عدم تسرّب الـ schema بين الطلبات مع connection pooling.

### مرحلة 4: Provisioning
- إنشاء Tenant جديد:
  - `CREATE SCHEMA <tenant_schema>`
  - تشغيل migrations على ذلك الـ schema
  - Seed مستخدم Owner داخل tenant schema
- Tenant#1 (NASRALLAH):
  - يبقى مؤقتاً على `public` كـ legacy
  - لاحقاً ننقل بياناته إلى `t_nasrallah` بخطة Migration منفصلة لتجنب التخريب.

## قواعد ثابتة
- لا خلط بيانات بين tenants: أي Query داخل tenant scope لازم يمر عبر schema الصحيح.
- Branding (الشعار/الاسم/الأيقونة) يمكن يبقى عبر `SystemSettings` حالياً ثم ننقله لاحقاً للـ registry إذا لزم.
- الصيانة/المالك:
  - Platform maintenance يخص المنصة فقط.
  - Tenant maintenance (إن لزم) يكون ضمن tenant scope لاحقاً.

## التحقق بعد كل مرحلة
- مرحلة 0: تطبيق migrations وقراءة/كتابة جدول `tenants` بدون كسر أي صفحة موجودة.
- مرحلة 1: صفحات `/t/<slug>/` تُظهر أنها ضمن tenant scope بدون تغيير البيانات.
- مرحلة 2: التأكد من منع الوصول المتداخل (Platform ↔ Tenant).
- مرحلة 3: فحص أن أي Tenant يرى بياناته فقط (Smoke tests على جداول حساسة).
- مرحلة 4: إنشاء Tenant جديد بالكامل بدون إعادة تشغيل التطبيق.

