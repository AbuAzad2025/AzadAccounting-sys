# تقرير إحصاء وهيكلة مشروع Garage Manager

## 1. نظرة عامة على الهيكل

المشروع عبارة عن تطبيق **Flask** وحيد (Monolith) لإدارة ورشة/كراج، مع واجهة Jinja2، وقاعدة بيانات SQLAlchemy، ووحدات AI اختيارية. لا يوجد بناء front-end منفصل (لا Node/SPA).

```
garage_manager/
├── [جذر] ملفات التطبيق الأساسية (.py)
├── .github/          قوالب Issues (تم حذف .md سابقاً)
├── .trae/            (أداة خارجية - لا يؤثر على التشغيل)
├── .vscode/          إعدادات المحرر (في .gitignore)
├── AI/               نظام الذكاء الاصطناعي (اختياري عبر AI_SYSTEMS_ENABLED)
├── helpers/          أحداث الأرصدة (SocketIO + Cache)
├── instance/         سري، قاعدة SQLite محلي، مفتاح الجلسة
├── middleware/       وسيط الأمان
├── migrations/       Alembic (نسخ قاعدة البيانات)
├── mobile_app/       مجلد (فارغ أو قالب لتوليد التطبيق من advanced_control)
├── non_production/   سكريبتات/بذور/اختبارات للتطوير (في .gitignore)
├── permissions_config/  تعريف الصلاحيات والأدوار
├── routes/           كل واجهات الويب (Blueprints)
├── services/         منطق الأعمال (نظام، نسخ، دفتر، سير workflows، إلخ)
├── static/           CSS, JS, AdminLTE, صور
├── templates/        Jinja2 HTML
├── tools/            مجلد فارغ
├── translations/     ترجمة (مثلاً accounting_ar)
└── utils/            أدوات مساعدة (أرصدة، ترخيص، أداء، تليمتري)
```

---

## 2. الملفات في جذر المشروع ووظائفها

| الملف | الوظيفة | الترابط |
|-------|---------|---------|
| **app.py** | نقطة الدخول: إنشاء التطبيق، تسجيل كل الـ Blueprints، ACL، قوالب، معالجة أخطاء، تشغيل SocketIO | يستورد من config, extensions, models, acl, routes/*, utils, services (system_initializer, ghost_manager), cli |
| **config.py** | إعدادات التطبيق: DB, Redis, CORS, جلسات، حدود رفع الملفات، خريطة المكونات | يُستورد من app, extensions؛ يقرأ .env |
| **extensions.py** | تهيئة Flask-SQLAlchemy, Migrate, Login, SocketIO, Mail, CSRF, Limiter, Cache, Compress, Sentry, Scheduler, Logging | يُستورد من app, config؛ يُستورد من معظم الملفات (db, login_manager, socketio, …) |
| **models.py** | كل نماذج SQLAlchemy (جداول وقيمتها) | يُستورد من app, routes, services, reports, forms, utils, barcodes (normalize_barcode) |
| **forms.py** | نماذج WTForms للعرض والتحقق | يُستورد من routes؛ يستورد models, extensions, constants, barcodes, custom_validators |
| **acl.py** | ربط الصلاحيات بالـ Blueprints (attach_acl) | يُستورد من app فقط |
| **barcodes.py** | تطبيع وتحقق وتوليد صور للباركود/QR | يُستورد من models, forms, routes (barcode, barcode_scanner, api, parts), warehouses |
| **constants.py** | عملة افتراضية، خيارات عملات، ثوابت رقمية | يُستورد من utils, forms, models, routes (payments, security) |
| **utils.py** | أدوات عامة (تنسيق، تواريخ، أرصدة، صلاحيات، إلخ) + init_app | يُستورد من app, routes, reports, acl؛ يستورد helpers.balance_events |
| **reports.py** | دوال التقارير (مبيعات، أرصدة عملاء/موردين/شركاء، تقدم الذمم) | يُستورد من routes (report_routes, main, currencies), cli |
| **notifications.py** | إشعارات (طلبات، مدفوعات، مخزون منخفض، تنبيهات) | يُستورد من routes/payments, extensions, app |
| **cli.py** | أوامر Flask (سكربتات، بذور، تقارير) | يُستورد من app (register_cli) |
| **custom_validators.py** | محققون مخصصون للنماذج | يُستورد من forms |
| **wsgi.py** | نقطة دخول للنشر (Gunicorn/uWSGI)؛ مسار المشروع مضمّن | يُستدعى من خادم الويب؛ في .gitignore غالباً |
| **requirements.txt** | تبعيات Python | ضروري للتثبيت |

**خلاصة الجذر:** لا يوجد ملف مكرر أو زائد. كل ملف مستخدم ومرتبط بباقي المشروع.

---

## 3. المجلدات الرئيسية والترابط

### 3.1 routes/ (Blueprints)

كل الملفات التالية مسجّلة في **app.py** وتُستخدم:

| الملف | الـ Blueprint | البادئة | الوظيفة |
|-------|--------------|---------|----------|
| auth.py | auth_bp | /auth | تسجيل دخول/خروج، استعادة كلمة المرور |
| main.py | main_bp | (بدون) | الصفحة الرئيسية، لوحة التحكم |
| users.py | users_bp | /users | إدارة المستخدمين |
| service.py | service_bp | /service | طلبات الخدمة |
| customers.py | customers_bp | /customers | العملاء |
| sales.py | sales_bp | /sales | المبيعات/الفواتير |
| sale_returns.py | returns_bp | /returns | مرتجعات المبيعات |
| notes.py | notes_bp | /notes | الملاحظات |
| report_routes.py | reports_bp | /reports | التقارير العامة |
| shop.py | shop_bp | /shop | المتجر الإلكتروني |
| expenses.py | expenses_bp | /expenses | المصاريف |
| vendors.py | vendors_bp | /vendors | الموردين |
| shipments.py | shipments_bp | /shipments | الشحنات |
| warehouses.py | warehouse_bp | /warehouses | المستودعات والمخزون |
| branches.py | branches_bp | /branches | الفروع |
| payments.py | payments_bp | /payments | المدفوعات |
| permissions.py | permissions_bp | /permissions | الصلاحيات |
| roles.py | roles_bp | /roles | الأدوار |
| api.py | api_bp | /api | API عام |
| admin_reports.py | admin_reports_bp | /admin/reports | تقارير إدارية |
| parts.py | parts_bp | /parts | القطع/المنتجات |
| barcode.py | bp_barcode | /api | التحقق من الباركود (API فقط) |
| barcode_scanner.py | barcode_scanner_bp | /barcode | واجهة ماسح الباركود |
| partner_settlements.py | partner_settlements_bp | /partners | تسويات الشركاء |
| supplier_settlements.py | supplier_settlements_bp | /suppliers | تسويات الموردين |
| ledger_blueprint.py | ledger_bp | /ledger | دفتر الأستاذ |
| ledger_control.py | ledger_control_bp | /security/ledger-control | تحكم الدفتر |
| financial_reports.py | financial_reports_bp | /reports/financial | التقارير المالية |
| accounting_validation.py | accounting_validation_bp | /validation/accounting | التحقق المحاسبي |
| accounting_docs.py | accounting_docs_bp | /docs/accounting | وثائق محاسبية |
| ai_routes.py | ai_bp | /ai | واجهة المستخدم للـ AI |
| ai_admin.py | ai_admin_bp | /ai-admin | إدارة الـ AI |
| currencies.py | currencies_bp | /currencies | العملات |
| user_guide.py | user_guide_bp | /user-guide | دليل المستخدم |
| other_systems.py | other_systems_bp | /other-systems | أنظمة أخرى/تكامل |
| pricing.py | pricing_bp | /pricing | التسعير |
| checks.py | checks_bp | /checks | الشيكات |
| budgets.py | budgets_bp | /budgets | الميزانيات |
| assets.py | assets_bp | /assets | الأصول |
| bank.py | bank_bp | /bank | البنك |
| cost_centers.py | cost_centers_bp | /cost-centers | مراكز التكلفة |
| cost_centers_advanced.py | cost_centers_advanced_bp | /cost-centers | مراكز تكلفة متقدمة |
| engineering.py | engineering_bp | /engineering | الهندسة |
| projects.py | projects_bp | /projects | المشاريع |
| project_advanced.py | project_advanced_bp | /projects | مشاريع متقدمة |
| recurring_invoices.py | recurring_bp | /recurring | فواتير دورية |
| health.py | health_bp | /health | صحة النظام |
| security.py | security_bp | /security | الأمان والإعدادات |
| security_expenses.py | security_expenses_bp | /security/expenses-control | مصاريف أمنية |
| advanced_control.py | advanced_bp | /advanced | التحكم المتقدم (مولد تطبيق جوال، إلخ) |
| workflows.py | workflows_bp | /workflows | سير العمل |
| security_control.py | security_control_bp | /advanced | تحكم أمني متقدم |
| archive.py | archive_bp | /archive | واجهة الأرشفة |
| archive_routes.py | archive_routes_bp | (بدون) | أرشفة الشحنات/الشيكات من مساراتها |
| balances_api.py | balances_api_bp | /api/balances | API الأرصدة |
| performance.py | performance_bp | /system/performance | أداء النظام |

**ملاحظات:**
- **archive.py** و **archive_routes.py** غير مكررين: الأول لواجهة /archive، الثاني لعمليات أرشفة من صفحات الشحنات والشيكات.
- **barcode.py** (API تحقق) و **barcode_scanner.py** (واجهة ماسح): وظيفتان مختلفتان.
- **report_routes.py** و **admin_reports.py** و **financial_reports.py** مختلفة: تقارير عامة، إدارية، ومالية.
- لا يوجد **warehouse.py** منفصل؛ المستودعات كلها في **warehouses.py** (و warehouse_bp منه).
- لا يوجد **accountancy_docs.py**؛ المستخدم فقط **accounting_docs.py**.

---

### 3.2 services/

| الملف | الاستخدام | القرار |
|-------|-----------|--------|
| system_initializer.py | app.py (تهيئة النظام عند البدء) | **يلزم** |
| ghost_manager.py | app.py (ضمان مالك افتراضي) | **يلزم** |
| workflow_engine.py | routes/workflows.py, cli.py, models.py | **يلزم** |
| backup_service.py | routes/advanced_control.py, extensions.py | **يلزم** |
| ledger_service.py | routes/ledger_blueprint.py, extensions.py | **يلزم** |
| prometheus_service.py | routes/security.py (مقاييس) | **يلزم** |
| audit_service.py | يُشغّل ذاتياً فقط (سكريبت تدقيق GL) | **اختياري** – للصيانة فقط |
| bootstrap_data.py | غير مستدعى من أي مكان (بذور أنواع مصاريف) | **اختياري** – يمكن استدعاؤه يدوياً أو ربطه لاحقاً بـ system_initializer |

---

### 3.3 utils/

كل الوحدات مستخدمة:
- **balance_calculator, customer_balance_updater, partner_balance_calculator, partner_balance_updater, supplier_balance_updater** – أرصدة.
- **performance_monitor** – app.py.
- **telemetry** – app.py.
- **licensing** – يُستورد من مكان في المشروع (مراجعة بالبحث إن رغبت).

**القرار:** الكل **يلزم** أو مستخدم؛ لا حذف.

---

### 3.4 helpers/

- **balance_events.py**: يُستورد من utils (customer_balance_updater, partner_balance_updater, supplier_balance_updater) و utils.py؛ يصدّر حدث تحديث الأرصدة (SocketIO + Cache).

**القرار:** **يلزم**.

---

### 3.5 middleware/

- **security_middleware.py**: وسيط أمان (مثلاً IP، حماية). يُستدعى من **app.py** عبر `init_security_middleware(app)`.

**القرار:** **يلزم** (مُسجّل في app.py).

---

### 3.6 permissions_config/

- **enums.py**, **permissions.py**: تعريف الصلاحيات والأدوار؛ مُستخدَم من routes و acl و services.

**القرار:** **يلزم**.

---

### 3.7 AI/

- **scheduler.py** و **engine/** (محركات، ذاكرة، تدريب، إلخ): تعمل عند تفعيل **AI_SYSTEMS_ENABLED**؛ routes (ai_routes, ai_admin) تعتمد عليها.

**القرار:** **يلزم** إذا كنت تستخدم ميزات الـ AI؛ **اختياري** إذا أردت تعطيل الـ AI بالكامل.

---

### 3.8 migrations/

- نسخ Alembic لتطور قاعدة البيانات.

**القرار:** **يلزم**؛ لا تحذف.

---

### 3.9 static/, templates/, translations/

- أصول الواجهة والترجمة.

**القرار:** **يلزم**.

---

## 4. مجلدات وملفات مشكوك فيها أو زائدة

### 4.1 tools/

- **المحتوى:** مجلد فارغ (لا ملفات).
- **الاستخدام:** لا يُستورد ولا يُشار إليه في الكود.
- **القرار النهائي:** **لا يلزم**. يمكن حذف المجلد أو تركه فارغاً؛ لا تأثير على التشغيل.

---

### 4.2 non_production/

- **المحتوى:** scripts, seeds, tests (للتطوير).
- **الاستخدام:** في **.gitignore**؛ لا يُستدعى من التطبيق الرئيسي.
- **القرار النهائي:** **اختياري**. إن لم تعد تحتاج سكريبتات/بذور/اختبارات تطوير داخل المشروع يمكن حذف المجلد؛ إن احتفظت به فالأفضل أن يبقى في .gitignore.

---

### 4.3 mobile_app/

- **المحتوى:** يبدو فارغاً أو قالباً.
- **الاستخدام:** **advanced_control** يبني تطبيقاً جوالاً ويحفظه في **instance/mobile_apps/** وليس بالضرورة من هذا المجلد.
- **القرار النهائي:** **غير ضروري** إن كان فارغاً؛ يمكن حذفه. إن كان يحتوي على أصول تُستخدم عند التوليد فاتركه أو انقل المحتوى إلى مكان واضح (مثلاً داخل static أو instance).

---

### 4.4 .trae/

- أداة خارجية (على الأرجح Cursor/IDE).
- **القرار:** لا يؤثر على التشغيل؛ يمكن تجاهله أو إضافته لـ .gitignore إن أردت.

---

### 4.5 .vscode/

- موجود في **.gitignore**.
- **القرار:** إعدادات محلي فقط؛ لا يلزم للمشروع كمنتج.

---

### 4.6 wsgi.py

- **ملاحظة:** مذكور في **.gitignore** (أي قد لا يُرفع إلى المستودع).
- **الوظيفة:** ضروري للنشر على خادم (مثل Gunicorn).
- **القرار النهائي:** **يلزم للنشر**. إن كان مُتجاهلاً في git، احتفظ بنسخة محلية أو وثّق محتواها (استدعاء create_app) في دليل النشر.

---

## 5. ملخص القرارات النهائية

| العنصر | القرار | ملاحظة |
|--------|--------|--------|
| كل ملفات الجذر (.py المذكورة أعلاه) | **يلزم** | لا تكرار ولا ملف بلا استعمال في الهيكل الحالي |
| routes/* (كل الـ 56 ملفاً) | **يلزم** | كلها مسجّلة ومستخدمة |
| services/* (ما عدا audit_service, bootstrap_data) | **يلزم** | |
| services/audit_service.py | **اختياري** | سكريبت تدقيق؛ للصيانة فقط |
| services/bootstrap_data.py | **اختياري** | غير مستدعى؛ يمكن ربطه لاحقاً أو تشغيله يدوياً |
| utils/*, helpers/*, permissions_config/* | **يلزم** | |
| middleware/* | **يلزم** | مُسجّل في app.py (init_security_middleware) |
| AI/* | **يلزم** إذا AI مفعّل | **اختياري** إذا تعطّل الـ AI |
| migrations/* | **يلزم** | |
| static, templates, translations | **يلزم** | |
| **tools/** | **لا يلزم** | مجلد فارغ – آمن حذفه |
| **non_production/** | **اختياري** | للتطوير؛ في .gitignore – احذف إن لم تحتجه |
| **mobile_app/** | **لا يلزم** إن كان فارغاً | احذف أو استخدم كقالب إن كان فيه محتوى |
| .trae, .vscode | لا تأثير على التشغيل | يمكن تجاهلها أو إضافتها لـ .gitignore |
| wsgi.py | **يلزم للنشر** | احتفظ به أو وثّق محتواه |

---

## 6. توصيات إضافية

1. **لا يوجد ملف route مكرر بوظيفة نفسية**؛ أسماء متقاربة (مثل archive vs archive_routes، barcode vs barcode_scanner) تعكس تقسيم وظائف مختلف.
2. **bootstrap_data.py**: إن أردت بذور أنواع المصاريف تلقائياً عند أول تشغيل، يمكن استدعاء `seed_core_expense_types(db)` من داخل **system_initializer** مرة واحدة.
3. **audit_service.py**: إن لم تستخدم تدقيق GL يدوياً، يمكن تركه كسكريبت صيانة أو حذفه إن لم تعد تحتاجه.
4. **مجلد tools**: إن لم تخطط لاستخدامه، احذفه لتبسيط الهيكل.

تم إعداد هذا التقرير بناءً على مسح الهيكل والاستيرادات والاستخدام الفعلي في المشروع.
