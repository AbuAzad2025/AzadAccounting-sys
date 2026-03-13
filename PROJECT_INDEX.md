# فهرس المشروع — مراجعة شاملة وفهرسة احترافية

هذا المستند يوفّر خريطة موحّدة لهيكل المشروع، الصلاحيات، الـ Blueprints، والتطابق بين المكوّنات دون تعارض أو عدم تطابق.

---

## فهرس حقيقي (فهرسة شاملة — سكريبت واحد للإنتاج)

يُولَّد كل شيء من **سكريبت واحد** قابل للتشغيل محلياً أو على سيرفر الإنتاج:

```bash
python scripts/generate_index.py
# أو حفظ في مسار مخصّص:
python scripts/generate_index.py --output-dir /var/www/app/index
```

الملفات المُولَّدة في مجلد **`index/`** (أو المسار المُحدد):

| الملف | المحتوى |
|-------|---------|
| **INDEX_META.json** | وقت التوليد، بيئة التشغيل، أعداد (مسارات، نماذج، صلاحيات، blueprints، نماذج ويب، قوالب، خدمات). |
| **INDEX_ROUTES.json** / **.md** | كل مسارات التطبيق (rule, endpoint, methods). |
| **INDEX_MODELS.json** / **.md** | النماذج: جدول DB ↔ اسم الكلاس. |
| **INDEX_PERMISSIONS.json** / **.md** | الصلاحيات (SystemPermissions) والأدوار (SystemRoles). |
| **INDEX_BLUEPRINTS.json** / **.md** | الـ Blueprints مع url_prefix وصلاحيات ACL (read_perm, write_perm). |
| **INDEX_FORMS.json** / **.md** | قائمة نماذج Flask-WTF (من forms.py). |
| **INDEX_TEMPLATES.json** / **.md** | إحصائيات القوالب (مجلدات وعدد الملفات). |
| **INDEX_SERVICES.md** | قائمة ملفات services/*.py. |
| **INDEX_SUMMARY.md** | ملخص الفهرسة وتاريخ التحديث. |

تفاصيل التشغيل والإنتاج: **index/README.md**.

---

## فهرسة تسرّع النظام (أداء قاعدة البيانات)

لتسريع الاستعلامات والبحث والفلترة، يُطبَّق على القاعدة **فهارس أداء**:

- **تلقائياً:** عند تشغيل التطبيق إذا `AUTO_CREATE_PERFORMANCE_INDEXES=True` (الافتراضي). يدعم **PostgreSQL** و **SQLite**.
- **يدوياً (محلي أو إنتاج):**  
  `python scripts/apply_speed_indexes.py`

**ما الذي يُنشأ:**
- **PostgreSQL:** فهارس على الأعمدة الأكثر استعلاماً (تواريخ، حالات، هويات، أسماء) + فهارس pg_trgm للبحث الغامض + فهارس جزئية (WHERE) لتحسين استعلامات محددة.
- **SQLite:** نفس الفهارس العادية (بدون GIN/جزئية).

**متى تشغّل السكريبت يدوياً:** بعد استعادة نسخة احتياطية على بيئة جديدة، أو إذا عطّلت التطبيق التلقائي عبر `AUTO_CREATE_PERFORMANCE_INDEXES=False` أو `DISABLE_PERFORMANCE_INDEXES=1`.

السكريبت: **scripts/apply_speed_indexes.py**.

---

## 1. هيكل المشروع (مختصر)

```
garage_manager/
├── app.py                 # نقطة الدخول، تسجيل Blueprints، حقن Enums، ACL
├── config.py              # إعدادات التطبيق، DATABASE_URL، HOST، PORT
├── extensions.py          # db, migrate, login_manager, socketio, mail, backup/restore
├── models.py              # نماذج SQLAlchemy + Enums الأعمال (PaymentStatus, SaleStatus, ...)
├── utils.py               # permission_required, _get_or_404, _PERMISSION_ALIASES
├── acl.py                 # attach_acl (صلاحيات على مستوى Blueprint)
├── forms.py               # نماذج Flask-WTF
├── permissions_config/
│   ├── enums.py           # SystemPermissions, SystemRoles (مصدر واحد لأسماء الصلاحيات)
│   ├── blueprint_guards.py # مصدر واحد لـ attach_acl لكل Blueprint
│   ├── permissions.py     # تسميات عربية، ربط أدوار–صلاحيات
│   └── README.md          # قواعد الصلاحيات
├── routes/                # ~55 ملف Blueprint
├── services/              # ledger_service, workflow_engine, backup_service, ...
├── templates/
├── static/
├── migrations/
└── instance/              # garage.db (SQLite افتراضي)، backups، secret_key
```

---

## 2. فهرس الـ Blueprints (تسجيل + مسار + ACL)

| متغيّر في app.py | اسم Blueprint (داخلي) | url_prefix | في ACL (_blueprints_for_acl)؟ | ملاحظة |
|------------------|------------------------|------------|--------------------------------|--------|
| auth_bp | auth | /auth | لا | تسجيل الدخول/الخروج |
| main_bp | main | / | نعم | لوحة التحكم، الصفحة الرئيسية |
| users_bp | users_bp | /users | نعم | MANAGE_USERS |
| service_bp | service | /service | نعم | VIEW_SERVICE / MANAGE_SERVICE |
| customers_bp | customers | /customers | نعم | MANAGE_CUSTOMERS |
| sales_bp | sales_bp | /sales | نعم | MANAGE_SALES |
| returns_bp | returns | /returns | لا | مرتجعات المبيعات |
| notes_bp | notes_bp | /notes | نعم | VIEW_NOTES / MANAGE_NOTES |
| reports_bp | reports_bp | /reports | نعم | VIEW_REPORTS / MANAGE_REPORTS |
| shop_bp | shop | /shop | نعم | VIEW_SHOP / MANAGE_SHOP + exempt_prefixes |
| expenses_bp | expenses | /expenses | نعم | MANAGE_EXPENSES |
| vendors_bp | vendors_bp | /vendors | نعم | MANAGE_VENDORS |
| shipments_bp | shipments_bp | /shipments | نعم | MANAGE_SHIPMENTS |
| warehouse_bp | warehouse_bp | /warehouses | نعم | VIEW_WAREHOUSES / MANAGE_WAREHOUSES |
| branches_bp | branches_bp | /branches | لا | الفروع |
| payments_bp | payments | /payments | نعم | MANAGE_PAYMENTS |
| permissions_bp | permissions | /permissions | نعم | MANAGE_PERMISSIONS |
| roles_bp | roles | /roles | نعم | MANAGE_ROLES |
| parts_bp | parts_bp | /parts | نعم | VIEW_PARTS / MANAGE_INVENTORY |
| admin_reports_bp | admin_reports | /admin-reports | نعم | VIEW_REPORTS / MANAGE_REPORTS |
| bp_barcode | bp_barcode | /api | نعم | VIEW_PARTS |
| partner_settlements_bp | partner_settlements_bp | /partners | نعم | MANAGE_VENDORS |
| supplier_settlements_bp | supplier_settlements_bp | /suppliers | نعم | MANAGE_VENDORS |
| api_bp | api | /api | نعم | ACCESS_API / MANAGE_API + exempt_prefixes |
| ledger_bp | ledger | /ledger | نعم | MANAGE_LEDGER |
| ledger_control_bp | ledger_control | /security/ledger-control | نعم | MANAGE_LEDGER |
| currencies_bp | currencies | /currencies | نعم | MANAGE_CURRENCIES |
| barcode_scanner_bp | barcode_scanner | /barcode | نعم | VIEW_BARCODE / MANAGE_BARCODE |
| checks_bp | checks | /checks | نعم | MANAGE_PAYMENTS |
| balances_api_bp | balances_api | /api/balances | نعم | VIEW_REPORTS / MANAGE_REPORTS |
| financial_reports_bp | financial_reports | /reports/financial | نعم | VIEW_REPORTS / MANAGE_REPORTS |
| accounting_validation_bp | accounting_validation | /validation/accounting | لا | التحقق المحاسبي |
| accounting_docs_bp | accounting_docs | /docs/accounting | لا | مستندات محاسبية |
| ai_bp | ai | /ai | لا | مساعد AI |
| ai_admin_bp | ai_admin | /ai-admin | لا | إدارة AI |
| user_guide_bp | user_guide | /user-guide | لا | دليل المستخدم |
| other_systems_bp | other_systems | /other-systems | لا | أنظمة أخرى |
| pricing_bp | pricing | /pricing | لا | التسعير |
| health_bp | health | /health | لا | صحة النظام |
| security_bp | security | /security | لا | الأمان والمستخدمين |
| security_expenses_bp | security_expenses | (يُستخرج من الملف) | لا | مصاريف أمنية |
| advanced_bp | advanced | /advanced | لا | التحكم المتقدم |
| security_control_bp | security_control | /advanced | لا | تحكم أمني (قد يتداخل مسار مع advanced) |
| archive_bp | archive | /archive | لا | الأرشيف |
| archive_routes_bp | archive_routes | (بدون prefix) | لا | مسارات أرشيف إضافية |
| budgets_bp | budgets | /budgets | لا | الميزانيات |
| assets_bp | assets | /assets | لا | الأصول |
| bank_bp | bank | /bank | لا | البنك (صلاحية MANAGE_BANK في الـ route) |
| cost_centers_bp | cost_centers | /cost-centers | لا | مراكز التكلفة |
| cost_centers_advanced_bp | cost_centers_advanced | /cost-centers | لا | مراكز تكلفة متقدمة (نفس المسار) |
| engineering_bp | engineering | /engineering | لا | الهندسة |
| projects_bp | projects | /projects | لا | المشاريع |
| project_advanced_bp | project_advanced | /projects | لا | مشاريع متقدمة (نفس المسار) |
| recurring_bp | recurring | /recurring | لا | الفواتير الدورية |
| workflows_bp | workflows | /workflows | لا | سير العمل |
| performance_bp | performance_bp | /system/performance | لا | الأداء |

**ملاحظة تسمية:** بعض الملفات تستخدم اسم Blueprint مختلف عن اسم المتغيّر (مثلاً `sales_bp` كمتغيّر و `Blueprint('sales_bp', ...)`). للتوحيد المستقبلي يُفضّل: متغيّر `xyz_bp` و Blueprint باسم `'xyz'` و url_prefix `/xyz` حيث أمكن.

**تنبيه مسارات مكررة:** التطبيق يسمح بمسارات مكررة معرّفة في `allowed_route_duplicates` (مثل `/sales`, `/reports`). كما أن `cost_centers_bp` و `cost_centers_advanced_bp` يشتركان في `/cost-centers`، و`projects_bp` و `project_advanced_bp` في `/projects`، و`advanced_bp` و `security_control_bp` في `/advanced` — التمييز يتم حسب القواعد الفرعية (rules) داخل كل Blueprint.

---

## 3. الصلاحيات — مصدر واحد وعدم تعارض

- **المصدر الوحيد لأسماء الصلاحيات:** `permissions_config/enums.py` → `SystemPermissions`.
- **استخدام في الكود:**
  - Routes: `@permission_required(SystemPermissions.XXX)` من `utils`.
  - قوالب: `current_user.has_permission('manage_expenses')` — القيمة النهائية من الـ enum (أو alias في utils).
  - ACL: من `blueprint_guards.py` فقط بـ `SystemPermissions.XXX.value`.

**صلاحيات مذكورة في القوالب ومطابقة لـ SystemPermissions (عينة):**  
`manage_expenses`, `manage_vendors`, `manage_service`, `manage_sales`, `manage_inventory`, `manage_payments`, `manage_advanced_accounting`, `delete_preorder` (موجود كـ DELETE_PREORDER في enums).

**مرجع:** `permissions_config/README.md` و `permissions_config/PERMISSIONS_AUDIT.md` و `ENUMS_AUDIT.md`.

---

## 4. Enums — تطابق باك/فرونت/بيز

- **تعريف:** `models.py` (حالات أعمال)، `permissions_config/enums.py` (صلاحيات وأدوار)، `notifications.py` (إشعارات).
- **حقن في القوالب:** من `app.py` عبر `inject_enums()` (مثلاً PaymentStatus, SaleStatus, EngineeringTaskStatus, ...).
- **قواعد:** لا نصوص حرفية للحالات في الـ routes؛ في الـ JS (مثل AR_STATUS, ENTITY_ENUM) يجب أن تطابق قيم الـ API والـ backend.

**مرجع كامل:** `ENUMS_AUDIT.md`.

---

## 5. حماية مسارات "مالك/مطوّر فقط"

الملفات التي تتحقق من `current_user.is_system or current_user.role_name_l in ['owner', 'developer']` ويجب أن تستورد `current_user` من `flask_login`:

| الملف | استيراد current_user |
|-------|----------------------|
| routes/recurring_invoices.py | نعم (تم إصلاحه) |
| routes/workflows.py | نعم |
| routes/projects.py | نعم |
| routes/bank.py | نعم |
| routes/security.py | نعم |
| routes/engineering.py | نعم |
| routes/cost_centers_advanced.py | نعم |
| routes/ai_routes.py | نعم |
| routes/shop.py | نعم |

---

## 6. الخدمات (Services)

| الملف | الوظيفة |
|-------|---------|
| services/ledger_service.py | منطق دفتر الأستاذ |
| services/workflow_engine.py | محرك سير العمل |
| services/backup_service.py | نسخ احتياطي تلقائي |
| services/system_initializer.py | تهيئة النظام وسلامة المكوّنات |
| services/ghost_manager.py | إدارة "Ghost" |
| services/prometheus_service.py | مقاييس Prometheus |

---

## 7. التحقق من السلامة (System Integrity)

- **app.py → _validate_system_integrity:** يتحقق من:
  - عدم تكرار مسارات (مع سماح لبعض المسارات المحددة في `allowed_route_duplicates`).
  - عدم تكرار أسماء جداول النماذج.
  - وجود نماذج وعدد نماذج/نماذج/مسارات متوقعة (للمعلومات المسجّلة عند التشغيل).

---

## 8. أفضل الممارسات المعتمدة في المشروع

1. **صلاحيات:** استخدام `SystemPermissions` فقط؛ عدم نشر نصوص حرفية للصلاحيات.
2. **Enums:** مصدر واحد في الـ backend؛ في الـ routes استخدام `EnumName.VALUE.value`؛ في الـ JS مطابقة قيم الـ API.
3. **استرجاع كيانات:** استخدام `utils._get_or_404(Model, id, load_options=...)` بدل تعريف دوال مكررة في كل route.
4. **ACL:** مصدر واحد في `blueprint_guards.py`؛ ربط الـ blueprints في `app.py` عبر `_blueprints_for_acl` و `get_blueprint_guard_config()`.
5. **قوالب:** استخدام الـ enums المحقونة من `app.py` للمقارنة والعرض (مثل EngineeringTaskStatus، PaymentStatus).
6. **استيراد current_user:** أي route أو before_request يستخدم `current_user` يجب أن يستوردها من `flask_login`.

---

## 9. مستندات مرجعية مرتبطة

| المستند | المحتوى |
|---------|---------|
| permissions_config/README.md | قواعد الصلاحيات ومصدرها الوحيد |
| permissions_config/PERMISSIONS_AUDIT.md | تدقيق الصلاحيات وتطابق المسميات |
| ENUMS_AUDIT.md | تدقيق الـ Enums وتطابق باك/فرونت وقواعد المستقبل |
| PROJECT_AUDIT_REPORT.md | تقرير تدقيق سابق للملفات والهيكل |

---

## 10. خلاصة

- **هيكل المشروع:** موثّق في القسم 1 و 2 (Blueprints، المسارات، ACL).
- **الصلاحيات والأدوار:** مصدر واحد في `enums.py`؛ استخدام موحّد عبر blueprint_guards و utils و القوالب.
- **Enums:** مصدر واحد في models/permissions/notifications؛ تطابق مع القوالب والـ JS موثّق في ENUMS_AUDIT.md.
- **عدم تعارض:** التحقق من السلامة عند التشغيل؛ قواعد واضحة لعدم نشر صلاحيات أو حالات كنصوص مبعثرة.
- **فهرسة:** هذا المستند يعمل كفهرس مركزي للتنقل والمراجعة المستقبلية دون خلل أو تعارض أو عدم تطابق مقصود.
