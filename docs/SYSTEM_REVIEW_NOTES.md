# ملاحظات مراجعة نظام AzadAccounting-sys

هذا الملف هو دفتر مراجعة مركزي للنظام. الهدف منه تجميع الملاحظات والتحسينات المطلوبة قبل أي تعديل فعلي على الكود، مع الحفاظ على أثر كل جولة مراجعة.

## قواعد العمل

- لا يتم تعديل الملفات الكبيرة مباشرة بدون مراجعة.
- لا يتم إنشاء ملفات جديدة إلا للضرورة.
- لا يتم استبدال ملف ضخم كاملًا إلا عند الضرورة القصوى وبعد فحص الفرق.
- كل ملاحظة يجب أن تكون مرتبطة بملف أو دالة أو قالب أو تكامل محدد.
- أي تعديل لاحق يجب أن يكون صغيرًا وقابلًا للمراجعة.
- الملفات المالية، الصلاحيات، الشيكات، الدفعات، دفتر الأستاذ، والمخزون ملفات حساسة جدًا.

## رموز التصنيف

| التصنيف | المعنى |
|---|---|
| CRITICAL | مشكلة قد تؤثر على المال أو الصلاحيات أو سلامة البيانات |
| HIGH | مشكلة مهمة تؤثر على الأمان أو الأداء أو الاعتمادية |
| MEDIUM | تحسين مطلوب أو مشكلة متوسطة |
| LOW | تحسين تنظيمي أو تجميلي |
| REVIEW | يحتاج دراسة أو اختبار قبل الحكم |

## حالة المراجعة

| الحالة | المعنى |
|---|---|
| TODO | لم تتم معالجته |
| IN_REVIEW | قيد الدراسة |
| READY | جاهز لتعديل صغير آمن |
| BLOCKED | يحتاج أداة/اختبار/قرار قبل التنفيذ |
| DONE | تمت معالجته |
| DEFERRED | مؤجل |

---

# 1. نظرة عامة على النظام

النظام ERP / محاسبة / إدارة كراج ومخازن ومبيعات ودفعات وشيكات وصلاحيات وذكاء صناعي.

## الوحدات الأساسية

- المصادقة وتسجيل الدخول: `routes/auth.py`
- المستخدمون، الأدوار، الصلاحيات: `routes/users.py`, `routes/roles.py`, `routes/permissions.py`
- العملاء، الموردون، الشركاء: `routes/customers.py`, `routes/vendors.py`
- المبيعات، المرتجعات، الفواتير: `routes/sales.py`, `routes/sale_returns.py`
- الدفعات والشيكات: `routes/payments.py`, `routes/checks.py`
- المصاريف والرواتب والسلف: `routes/expenses.py`
- الشحنات والمخازن والمخزون: `routes/shipments.py`, `routes/warehouses.py`
- دفتر الأستاذ والتقارير المالية: `routes/ledger_blueprint.py`, `routes/ledger_control.py`, `routes/financial_reports.py`
- العملات وأسعار الصرف: `routes/currencies.py`, منطق FX داخل `models.py`
- الذكاء الصناعي: `routes/ai_routes.py`, `routes/ai_admin.py`, مجلد `AI/`
- الأمن والتحكم: `routes/security.py`, `routes/security_control.py`, `middleware/security_middleware.py`
- الأداء: `routes/performance.py`, `utils/performance_monitor.py`
- المشاريع، مراكز التكلفة، الأصول، البنوك، workflows.

---

# 2. سجل الإنجاز

| التاريخ | الملف/النطاق | الإنجاز | الحالة |
|---|---|---|---|
| 2026-05-15 | `app.py` | دراسة ملف التشغيل المركزي من البداية إلى النهاية وتوثيق الملاحظات. | DONE |
| 2026-05-15 | `app.py` | دمج PR #1: تحسين handler 500، CORS، Request ID، كاش إعدادات القوالب، وتنظيف مسار الشعار. | DONE |
| 2026-05-15 | `app.py` | إصلاح ملاحظة `qodo-code-review[bot]`: فشل `cache.set()` في `inject_system_settings` لا يلغي نتائج قاعدة البيانات. | DONE |
| 2026-05-15 | `models.py` | مراجعة الملف من بدايته حتى نهايته على سبع جولات تقريبية وتوثيق الملاحظات. | DONE |

---

# 3. خلاصة `app.py`

## ما تم تحسينه ودمجه

| التصنيف | الحالة | الملاحظة |
|---|---|---|
| HIGH | DONE | منع كشف traceback كامل للمستخدم في الإنتاج عند خطأ 500، مع إرجاع `request_id`. |
| HIGH | DONE | منع الجمع غير الآمن بين `CORS_ORIGINS=*` و credentials على `/api/*`. |
| MEDIUM | DONE | تنظيف `X-Request-Id` القادم من المستخدم ومنع القيم الطويلة أو غير النظيفة داخل logs/headers. |
| HIGH | DONE | تقليل استعلامات `inject_system_settings` عبر قراءة إعدادات القوالب دفعة واحدة وتخزينها مؤقتًا. |
| HIGH | DONE | فصل فشل `cache.set()` عن قراءة قاعدة البيانات حتى لا تضيع إعدادات القوالب عند فشل الكاش. |
| MEDIUM | DONE | تنظيف `custom_logo` ومنع الروابط الخارجية أو مسارات `..`. |

## ما بقي مؤجلًا من `app.py`

هذه البنود لا تعدل مباشرة من `app.py` قبل دراسة الملفات التابعة:

| التصنيف | الحالة | البند | السبب | الملف المطلوب أولًا |
|---|---|---|---|---|
| HIGH | TODO | `csrf.exempt(ledger_bp)` | مرتبط بدفتر الأستاذ وقد يكسر عمليات مالية إذا عُدّل عشوائيًا. | `routes/ledger_blueprint.py` |
| MEDIUM | TODO | `login_manager.session_protection = None` | قد يكون مرتبطًا بـ proxy/PythonAnywhere أو جلسات العملاء. | `routes/auth.py` وبيئة التشغيل |
| HIGH | TODO | أسرار التكاملات من DB | يجب معرفة من يستطيع رؤيتها وهل تُخفى أو تُشفّر. | `SystemSettings`, شاشات الأمن والإعدادات |
| MEDIUM | TODO | تكرار seed/init logic | يوجد أكثر من مصدر تهيئة وقد يكسر التشغيل الأولي إذا وحد عشوائيًا. | `services/system_initializer.py`, `bootstrap_database` |
| HIGH | TODO | ACL والصلاحيات المركزية | حماية routes لا تُفهم من `app.py` فقط. | `acl.py`, `permissions_config/blueprint_guards.py` |
| HIGH | TODO | middleware الأمن العام | يؤثر على كل الطلبات. | `middleware/security_middleware.py` |

---

# 4. ملف الشيكات `routes/checks.py` — ملاحظات أولية محفوظة

| التصنيف | الحالة | المجال | الملاحظة |
|---|---|---|---|
| CRITICAL | IN_REVIEW | حالة الشيك | `CheckActionService.run` هو قلب تغيير حالة الشيك ولا يلمس قبل اختبار. |
| CRITICAL | IN_REVIEW | GL الشيكات | `create_gl_entry_for_check`, `_process_check_gl_queue`, `_create_check_gl_after_commit`, `_check_gl_batch_reverse` حساسة جدًا. |
| CRITICAL | IN_REVIEW | الدفع التلقائي | `_check_create_payment_auto` ينشئ دفعة تلقائيًا عند إنشاء شيك يدوي. |
| HIGH | READY | صلاحيات | `update_check_status`, `add_check`, `edit_check`, `check_detail`, `reports`, `get_first_incomplete_check`, `get_check_lifecycle` تحتاج صلاحيات واضحة. |
| HIGH | TODO | أداء | `get_checks()` و`reports()` و`get_statistics()` تجلب بيانات واسعة وتحتاج pagination/queries مختصرة. |
| HIGH | TODO | Validation | `add_check()` و`edit_check()` يحتاجان تحقق أقوى للمبلغ، الاتجاه، البنك، الرقم، التاريخ، والجهة. |

قاعدة ثابتة: لا يتم لمس GL الشيكات أو event listeners أو إنشاء الدفعات التلقائي قبل اختبار عملي.

---

# 5. ملاحظات عامة خارج `models.py`

| التصنيف | الحالة | الملف/النطاق | الملاحظة |
|---|---|---|---|
| HIGH | TODO | `routes/api.py` | `/api/health` يعرض counts لجداول تجارية؛ الأفضل health بسيط للعامة. |
| MEDIUM | TODO | `config.py` | إعدادات SQLAlchemy pool يجب أن تبقى مناسبة لـ PythonAnywhere ومستخدمين أقل من 100. |
| MEDIUM | TODO | `config.py` | `ITEMS_PER_PAGE=200` و`MAX_ITEMS_PER_PAGE=500` قد تكون ثقيلة للصفحات المالية. |
| REVIEW | TODO | AI | لا تطوير AI جديد قبل فهم النظام الأساسي والـ hooks. |
| HIGH | TODO | أمن | مراجعة صلاحيات routes المالية: الشيكات، الدفعات، المصاريف، الدفتر، المبيعات. |
| HIGH | IN_REVIEW | master key | لا يتم تعطيله؛ التحسين يكون حول audit، عدم كشف السر، وحماية الجلسة. |

---

# 6. مراجعة `models.py`

## 6.1 نطاق المراجعة المنجز

| الجولة | نطاق الأسطر التقريبي | الحالة | الملاحظات |
|---|---:|---|---|
| 1 | 1–1580 | DONE | بداية الملف، event listeners، Archive، الصلاحيات، enums، SystemSettings، العملات وأسعار الصرف. |
| 2 | 1581–2700 | DONE | سياسات الدفعات، Audit/Auth، User/Role/Permission، Customer، GL للرصيد الافتتاحي، بداية Supplier. |
| 3 | 2701–4500 | DONE | Supplier، تسويات الموردين، Partner، تسويات الشركاء، Employee، بداية Product. |
| 4 | 4501–7500 | DONE | Product tail، Branch/Site/Warehouse، StockLevel، Transfers، Exchange، PreOrder، Sale، SaleReturn، Invoice. |
| 5 | 7501–10500 | DONE | Payment، PaymentSplit، Supplier settlement draft، Shipment، ServiceRequest. |
| 6 | 10501–14700 | DONE | Service GL، ServicePart/Task، Online carts/orders/payments، StockAdjustment، Expense، GL، Audit، Check. |
| 7 | 14701–نهاية الملف | DONE | SaaS، Recurring invoices، Budgets، Fixed assets، Bank، Cost centers، Projects، Engineering، Workflows، balance queues. |

---

## 6.2 ملاحظات الجولة الأولى

| التصنيف | الحالة | المجال | الملاحظة |
|---|---|---|---|
| REVIEW | TODO | SQLAlchemy listeners | يوجد استبدال عام لـ `event.listen` بهدف تتبع وتغليف listeners. مفيد للتشخيص لكنه حساس لأنه يؤثر على كل listeners في الشيكات والدفعات ودفتر الأستاذ. |
| HIGH | TODO | Archive | `Archive.archive_record()` قد يفشل خارج سياق مستخدم إذا لم يتم تمرير `user_id` لأن `archived_by` غير قابل لـ NULL. |
| HIGH | READY | SystemSettings | `set_setting()` يمسح `system_setting_{key}` و`system_settings:bundle:v2` فقط، ولا يمسح كاشات `app.py` الجديدة: `system_settings:template_settings:v1` و`system_settings:module_flags:v1`. |
| MEDIUM | TODO | PaymentMethod | يحتوي قيم lowercase وuppercase للتوافق، ويحتاج تدقيق استعماله في payments/checks/expenses لتجنب تضارب `cheque/CHEQUE`. |
| HIGH | TODO | FX | منطق أسعار الصرف داخل `models.py` يجري اتصالات خارجية ويحتوي API key placeholders وخدمات بعضها عبر HTTP. |
| MEDIUM | TODO | FX cache | `_get_rate_cached` يستخدم `lru_cache` يومي، وقد يعطي سعرًا قديمًا بعد إدخال سعر يدوي جديد. |
| MEDIUM | TODO | FX auto update | `auto_update_missing_rates()` يقارن `valid_from == today` مع أن `valid_from` DateTime؛ قد لا يكتشف أسعار اليوم. |

---

## 6.3 ملاحظات الجولة الثانية

| التصنيف | الحالة | المجال | الملاحظة |
|---|---|---|---|
| HIGH | TODO | Payment policies | `validate_payment_policies()` يتحقق من المبلغ ومنع دخل EXPENSE فقط، وباقي القيود مرنة جدًا. |
| MEDIUM | TODO | Refund/Receivable | `refundable_amount_for()` و`receivable_amount_for()` يجب تدقيقهما مع split payments والشيكات المؤجلة/الراجعة. |
| REVIEW | TODO | AuditMixin | يلتقط الحالة السابقة داخل `_previous_state` ويحتاج تتبع أين تُستخدم وهل تغطي الحقول الحساسة. |
| HIGH | TODO | AuthAudit | `_auth_log()` لا يعمل commit مستقل؛ قد لا يُحفظ إذا حصل rollback. |
| HIGH | TODO | User permissions | `User.has_permission()` يعطي صلاحيات كاملة لـ `is_system`, super roles, owner, developer؛ يجب مطابقته مع `routes/auth.py` و`utils.is_super`. |
| MEDIUM | TODO | Customer login | `Customer.get_id()` يرجع `c:{id}` ومتوافق مع `load_user()`؛ يجب الحفاظ عليه. |
| MEDIUM | TODO | Customer password | setter كلمة المرور يقبل أي قيمة ويولد hash حتى لو فارغة حسب مسار الاستدعاء. |
| HIGH | TODO | Customer balances | أعمدة أرصدة كثيرة محفوظة تحتاج مطابقة مع دوال إعادة الحساب حتى لا تنفصل عن الواقع. |
| HIGH | TODO | Customer totals | `total_invoiced` و`total_paid` تستعلم وتحوّل عملات داخل properties، وقد تسبب N+1. |
| HIGH | TODO | Customer opening balance GL | `_customer_opening_balance_gl` يكتب قيود GL من داخل model event؛ حساس جدًا. |
| MEDIUM | TODO | Customer normalize | validation الهاتف وlistener normalize قد يتعارضان. |
| REVIEW | TODO | Auto customer | `_ensure_customer_for_counterparty()` ينشئ عميلًا تلقائيًا وقد يستخدم fallback phone غير حقيقي. |
| HIGH | TODO | Supplier link | `Supplier.customer_id` يربط المورد بعميل تلقائيًا؛ يجب فهم أثره على الأرصدة. |

---

## 6.4 ملاحظات الجولة الثالثة

| التصنيف | الحالة | المجال | الملاحظة |
|---|---|---|---|
| HIGH | TODO | Supplier totals | `Supplier.total_paid` يجمع دفعات مباشرة، دفعات loan settlements، ومصاريف المورد؛ ثقيل ومهم ماليًا. |
| HIGH | TODO | Supplier auto customer | إضافة مورد قد تنشئ/تربط Customer تلقائيًا؛ خطر خلط كيان مورد/عميل. |
| HIGH | TODO | Supplier opening GL | `_supplier_opening_balance_gl` يكتب قيود GL من داخل event. |
| MEDIUM | TODO | SupplierSettlement code | `ensure_code()` يعتمد COUNT وقد يتصادم عند التزامن. |
| HIGH | TODO | SupplierSettlement confirmation | منع التكرار يعتمد على `source_type/source_id` ويحتاج اختبار مع NULL source_id. |
| MEDIUM | TODO | SupplierSettlement payments | `total_paid` يعتمد على `Payment.reference == SupplierSettle:{code}`؛ ربط نصي هش. |
| HIGH | TODO | SupplierLoanSettlement | بعد إدخال تسوية قرض يتم جعل `ProductSupplierLoan.is_settled=True`; يحتاج فحص حذف/تعديل التسوية. |
| REVIEW | TODO | API helpers | `_ok`, `_created`, `_err` موجودة داخل `models.py` وتستخدم `jsonify`؛ خلط طبقات. |
| HIGH | TODO | Partner balances | أعمدة أرصدة Partner كثيرة وتحتاج مطابقة مع `utils.partner_balance_updater`. |
| HIGH | TODO | Partner auto customer | إضافة Partner قد تنشئ/تربط Customer تلقائيًا؛ خطر خلط كيان شريك/عميل. |
| HIGH | TODO | Partner opening GL | يستخدم حساب AP للشريك؛ يحتاج تحقق محاسبي حسب طبيعة الرصيد. |
| MEDIUM | TODO | update_partner_balance | عند تمرير connection غير Session يفتح `db.session.begin()` ويتجاهل connection الفعلي. |
| HIGH | TODO | PartnerSettlement approval | عند `is_approved` يحدث `partners.opening_balance = closing_balance`؛ سلوك مالي قوي جدًا. |
| HIGH | TODO | Partner settlement draft | `INVENTORY_SHARE` يدخل `total_due`؛ يجب حسم هل هو مستحق دفع أم معلومة فقط. |
| MEDIUM | TODO | Returns valuation | مرتجعات المبيعات في تسوية الشريك تستخدم `Product.selling_price` كتقدير. |
| HIGH | TODO | Employee totals | خصائص Employee المالية تعمل باستعلامات داخل properties وتسبب N+1. |
| REVIEW | TODO | Employee tax | منطق ضريبة الموظف ثابت/تقديري داخل model. |
| MEDIUM | TODO | Employee advances | جداول السلف والأقساط تحتاج فحص routes/services لتناسق paid/fully_paid. |
| HIGH | TODO | Product indexes | unique indexes المشروطة ممتازة في PostgreSQL، لكن تحتاج توافق SQLite/local. |
| MEDIUM | TODO | Product prices | تعدد حقول الأسعار يحتاج توحيد معنى كل حقل في routes والقوالب. |

---

## 6.5 ملاحظات الجولة الرابعة

| التصنيف | الحالة | المجال | الملاحظة |
|---|---|---|---|
| MEDIUM | TODO | Product pricing | `_product_before_save` يزامن `selling_price` و`price` ويقيد السعر بين min/max؛ يجب توحيد معنى السعر الأساسي. |
| HIGH | TODO | Warehouse guard | `_warehouse_guard` يمسح حقول supplier/partner حسب نوع المخزن؛ مهم جدًا لفهم مخازن PARTNER/EXCHANGE. |
| MEDIUM | TODO | Online warehouse | `_enforce_single_online_default` يستخدم `online_is_default = 1` في SQL؛ يحتاج فحص توافق PostgreSQL/SQLite مع boolean. |
| HIGH | TODO | StockLevel reservation | تم تعليق check الخاص بالكمية المحجوزة، لكن `available_quantity` ما زال يطرح `reserved_quantity` والحجز موجود في PreOrder/Online. |
| MEDIUM | TODO | Stock row race | `_ensure_stock_row` يعتمد insert ثم reselect عند التصادم؛ يحتاج اختبار تزامن. |
| HIGH | TODO | Stock movement audit | `_apply_stock_delta` يغير المخزون حتى لو فشل تسجيل `StockMovement` لأن الخطأ يبتلع. |
| HIGH | TODO | Reservation delta | `_apply_reservation_delta` لا يزال يفرض توفر المخزون رغم تعليق جزء من reservation في Sale. |
| HIGH | TODO | Transfer events | Transfer after_insert/update/delete يطبق stock deltas مباشرة؛ حساس للمخزون ولا يعدل بلا اختبار. |
| LOW | TODO | Duplicate helper | `_ex_dir_sign` موجودة أكثر من مرة؛ كود مكرر. |
| HIGH | TODO | Exchange GL | `_maybe_post_gl_exchange` قد ينشئ قيود GL عند `GL_AUTO_POST_ON_EXCHANGE`; حساس. |
| MEDIUM | TODO | Partner share model | `ProductPartnerShare` يستخدم نفس جدول `WarehousePartnerShare`; قد يسبب التباسًا في الصيانة. |
| MEDIUM | TODO | Partner share unique | unique مع NULL في `WarehousePartnerShare` قد لا يمنع تكرارات حسب قاعدة البيانات. |
| HIGH | TODO | PreOrder GL | GL للـ PreOrder يتجنب التكرار مع Payment عند وجود دفعة مكتملة؛ يجب اختبار مع الدفعات الجزئية. |
| HIGH | TODO | PreOrder reservation | `_preorder_reservation_flow` يبتلع أخطاء الحجز/الخصم، وقد يخفي فشل مخزون. |
| HIGH | TODO | Sale payment status | `Sale.update_payment_status` يعتمد على تفاصيل الشيك داخل split وعلى reference patterns؛ ربط نصي هش. |
| MEDIUM | TODO | Sale balance validation | validator يقيّد `balance_due` إلى صفر رغم تعليق يقول إن الرصيد السالب مسموح لبعض الحالات. |
| MEDIUM | TODO | Sale number | `sale_number` يعتمد COUNT وقد يتصادم عند التزامن. |
| HIGH | TODO | Sale GL | Sale GL شديد الحساسية ويحسب VAT/COGS/partner shares. |
| HIGH | TODO | Exchange COGS | مبيعات exchange تستخدم آخر unit_cost من ExchangeTransaction وليس FIFO/weighted average. |
| HIGH | TODO | Sale reversal | منطق `run_sale_gl_reversal_after_delete` يحتاج تحقق لأنه يبني عكسًا يدويًا بدل عكس قيد منشور فعليًا. |
| HIGH | TODO | SaleReturn stock | `SaleReturnLine.after_update` يضيف كامل الكمية مرة أخرى عند التعديل، وليس الفرق فقط؛ خطر تضخيم المخزون. |
| HIGH | TODO | SaleReturn GL duplication | يوجد منطق GL في listener قديم ومنطق after-commit لاحق؛ خطر ازدواج أو تضارب. |
| HIGH | TODO | Damaged return cost | منطق damaged goods يستخدم `Product.cost_price` بينما Product لا يظهر فيه هذا الحقل؛ احتمال Bug فعلي. |
| HIGH | TODO | Invoice payments cascade | علاقة Invoice payments فيها `cascade=all, delete-orphan`؛ حذف فاتورة قد يحذف دفعات. |
| MEDIUM | TODO | Invoice status | status الهجين يعتمد على total_paid، ويجب مطابقة property مع expression خصوصًا العملات. |
| MEDIUM | TODO | Invoice tax order | TaxEntry للفواتير قد يتأثر بترتيب listeners بعد إعادة حساب الإجماليات. |

---

## 6.6 ملاحظات الجولة الخامسة

| التصنيف | الحالة | المجال | الملاحظة |
|---|---|---|---|
| HIGH | TODO | Payment entity property | `Payment.entity` قد يرمي ValueError عند عدم وجود link؛ قد يكسر قوالب/API إذا استُخدم مباشرة. |
| HIGH | TODO | Payment transitions | السماح بـ COMPLETED→FAILED/CANCELLED حساس جدًا ومربوط بالشيكات. |
| HIGH | TODO | Payment GL skip | Payment GL يتخطى manual checks والدفعات ذات splits؛ يجب توثيق أن Split GL هو المصدر. |
| HIGH | TODO | Payment reversal delete | `run_payment_gl_reversal_after_delete` يبني العكس من بيانات الدفع وليس من القيد الأصلي؛ خطر mismatch مع split أو expense ledger. |
| HIGH | TODO | Auto check from payment | إنشاء Check تلقائيًا من cheque payment يبتلع الأخطاء؛ قد توجد دفعة شيك بلا سجل Check. |
| MEDIUM | TODO | Auto check creator | عند غياب created_by يستخدم أول user كمنشئ؛ audit غير دقيق. |
| MEDIUM | TODO | Payment number | `payment_number` يعتمد max+1 وقد يتصادم عند التزامن. |
| HIGH | TODO | Split check FX | الشيك المنشأ من PaymentSplit لا يملأ حقول FX issue مثل check العادي. |
| HIGH | TODO | Split check silent fail | فشل إنشاء check من split لا يمنع حفظ split. |
| HIGH | TODO | Split GL failed status | عند status FAILED يجب التأكد أن كل GL split قديم يحذف؛ المسار الحالي معقد وقد يترك قيودًا. |
| HIGH | TODO | Sale paid totals | `_update_sale_payment_totals` يحسب فقط Payments المكتملة المباشرة، ويتجاهل splits والعملات والشيكات الراجعة؛ قد يخالف `Sale.update_payment_status`. |
| HIGH | TODO | Supplier draft source | `build_supplier_settlement_draft` في ON_RECEIPT يعتمد `Warehouse.supplier_id`; قد يفوت ExchangeTransaction إذا المورد على transaction وليس warehouse. |
| MEDIUM | TODO | Supplier invoices draft | يجلب كل فواتير المورد ثم يفحص `balance_due` في Python؛ ثقيل. |
| HIGH | TODO | Supplier inventory holding | ON_CONSUME يضيف `INVENTORY_HOLDING` إلى المستحق؛ قرار محاسبي حساس. |
| MEDIUM | TODO | Shipment number | رقم الشحنة يعتمد count يومي + checksum؛ قد يتصادم عند التزامن. |
| HIGH | TODO | Shipment stock event | `_shipment_status_toggle` يطبق stock delta عند set attribute قبل flush؛ حساس جدًا. |
| HIGH | TODO | Shipment reversal | `_shipment_gl_batch_reverse` يستخدم `target.supplier_id` رغم أن Shipment لا يظهر فيه supplier_id؛ احتمال Bug عند الحذف. |
| HIGH | TODO | Service total_paid | `ServiceRequest.total_paid` يجمع دفعات IN ولا يظهر أنه يفلتر status؛ قد يحتسب PENDING/FAILED. |
| HIGH | TODO | Service totals tax | `total` يحسب tax لكن `_recalc_service_request_totals` يضع `total_amount` بدون tax؛ معنى `total_amount` غير موحد. |
| MEDIUM | TODO | Service transitions | transitions لا تشمل DIAGNOSIS/ON_HOLD/CLOSED رغم وجودها في أجزاء أخرى. |
| MEDIUM | TODO | Service number | `service_number` يعتمد COUNT وقد يتصادم عند التزامن. |

---

## 6.7 ملاحظات الجولة السادسة

| التصنيف | الحالة | المجال | الملاحظة |
|---|---|---|---|
| HIGH | TODO | Service GL | `_service_gl_batch_upsert_sql` يتخطى الصيانة إذا لها Invoice لتجنب double GL؛ يجب ضمان routes تستدعيه after commit. |
| LOW | TODO | Dead code | `_gl_on_service_complete` يبدأ بـ `return` وبعده كود طويل ميت. |
| MEDIUM | TODO | ServicePart tax | `ServicePart.line_total` و`ServiceTask.line_total` لا يشملان tax رغم وجود tax_rate. |
| MEDIUM | TODO | ServicePart unique | unique على `(service_id, part_id, warehouse_id)` يمنع نفس القطعة مرتين لنفس الصيانة والمخزن. |
| REVIEW | TODO | ServicePart insert GL | after_insert مع session يعيد totals ولا يستدعي GL، بينما update/delete يستدعيان GL. |
| MEDIUM | TODO | Online cart/order numbers | أرقام cart/preorder/payment تعتمد COUNT وقد تتصادم. |
| HIGH | TODO | OnlinePreOrder GL | GL للطلب الأونلاين يستخدم كامل total_amount إلى AR/ADVANCE بغض النظر عن prepaid/paid الفعلي. |
| HIGH | TODO | OnlinePreOrder cancel | reversal يعتمد `payment_status == CANCELLED` رغم أن payment_status غالبًا PENDING/PARTIAL/PAID. |
| HIGH | TODO | Card storage | `OnlinePayment` قد يخزن رقم البطاقة كاملًا مشفرًا، ويحتوي `decrypt_card_number`; هذا يدخل النظام في نطاق PCI عالي. |
| HIGH | TODO | Card fingerprint | fingerprint هو SHA256 للـ PAN بدون salt/HMAC؛ حساس. |
| REVIEW | TODO | OnlinePayment order touch | `_opay_touch_order` no-op، والاعتماد على before_flush لتحديث الطلب يحتاج اختبار. |
| HIGH | TODO | StockAdjustment | StockAdjustmentItem يخصم/يعيد المخزون عبر events؛ حساس جدًا. |
| HIGH | TODO | Expense update validation | `_expense_require_entity` يعمل في before_insert فقط، وليس before_update؛ يمكن أن تتغير الجهة وتبقى `payee_type/payee_entity_id` غير متسقة. |
| MEDIUM | TODO | Expense OTHER | Expense يتطلب entity حتى للمصاريف العامة؛ يحتاج فحص routes إذا `OTHER` مستخدمة فعليًا. |
| HIGH | TODO | Expense to_dict | `Expense.to_dict` كبير جدًا ويستدعي `total_paid/balance`، ما يسبب N+1. |
| MEDIUM | TODO | Auto account create | `_ensure_account_exists` ينشئ حسابات تلقائيًا؛ مفيد لكنه قد يخفي أخطاء شجرة الحسابات. |
| HIGH | TODO | Duplicate FX listeners | توجد listeners كثيرة مكررة للعملة/سعر الصرف لنفس النماذج؛ ترتيب التنفيذ قد يسبب غموضًا. |
| HIGH | TODO | GL posted immutability | `_gl_upsert_batch_and_entries` إذا وجد batch POSTED يعيده ولا يحدثه؛ أي تعديل بيانات يتطلب حذف القيد المنشور يدويًا قبل إعادة الإنشاء. |
| HIGH | TODO | GL SQLite compatibility | `_gl_upsert_batch_and_entries` يستخدم `RETURNING id`; يحتاج فحص توافق SQLite المحلي. |
| HIGH | TODO | Audit privacy | AuditLog يسجل old/new كامل للـ AuditMixin؛ قد يسجل حقولًا حساسة. |
| HIGH | TODO | Audit rollback | AuditLog في نفس transaction؛ إذا حصل rollback تختفي سجلات audit. |
| MEDIUM | TODO | Model methods commit | `ProductRatingHelpful.mark_helpful`, `CustomerLoyalty.add_points/use_points/get_or_create` تعمل commit داخل model method. |
| MEDIUM | TODO | Check company key | `Check.entity_name` يستخدم `SystemSettings.get_setting('COMPANY_NAME')` بينما `app.py` يستخدم `company_name/CompanyName`؛ عدم اتساق مفاتيح. |
| HIGH | TODO | Check sync import | Check event يستورد `routes.checks.PaymentStatusSyncService` من داخل model؛ coupling دائري محتمل. |
| HIGH | TODO | Check created_by | `created_by_id` إلزامي، وبعض المسارات تضع fallback لأول user؛ audit يحتاج تحسين. |

---

## 6.8 ملاحظات الجولة السابعة إلى نهاية الملف

| التصنيف | الحالة | المجال | الملاحظة |
|---|---|---|---|
| MEDIUM | TODO | Partner balance queue | تغييرات `WarehousePartnerShare` و`ShipmentItem` تحدث أرصدة الشركاء، لكن الأخطاء تبتلع. |
| MEDIUM | TODO | SaaS models | نماذج SaaS أساسية وتحتاج validators/check constraints أو خدمات توليد فواتير واضحة. |
| MEDIUM | TODO | Recurring invoices | القوالب والجداول موجودة، لكن منطق التوليد يحتاج فحص routes/services. |
| HIGH | TODO | Budget actual | `Budget.get_actual_amount()` يجمع كل مصاريف الفرع/الموقع للسنة ولا يفلتر حسب `account_code`؛ قد يجعل الموازنة حسب الحساب غير دقيقة. |
| MEDIUM | TODO | Budget unique NULL | unique على fiscal/account/branch/site قد يسمح بتكرارات عند NULL حسب قاعدة البيانات. |
| MEDIUM | TODO | FixedAsset supplier | `FixedAsset.supplier_id` يشير إلى `partners.id` رغم الاسم supplier؛ تسمية مربكة. |
| MEDIUM | TODO | BankStatement constraint | check constraint لرصيد كشف البنك دقيق جدًا؛ جيد لكنه قد يسبب رفض imports إذا كان هناك فروقات rounding/fees. |
| HIGH | TODO | ProjectCost update | after_update يضيف amount إلى `projects.actual_cost` مرة أخرى بدل احتساب delta؛ خطر تضخيم التكلفة. |
| HIGH | TODO | ProjectRevenue update | after_update يضيف amount إلى `projects.actual_revenue` مرة أخرى بدل delta. |
| HIGH | TODO | ProjectRevenue phase bug | عند revenue مع phase يحدث `project_phases.actual_cost` بدل حقل revenue؛ احتمال Bug فعلي. |
| HIGH | TODO | ResourceTimeLog update | after_update يضيف الساعات إلى task/resource مرة أخرى بدل delta؛ خطر تضخيم actual_hours/hours_used. |
| MEDIUM | TODO | TimeLog project cost | عند approved ينشئ ProjectCost إذا غير موجود، لكنه لا يحدثه إذا تغير total_cost لاحقًا. |
| MEDIUM | TODO | Milestone invoice number | الفاتورة التلقائية تستخدم `MS-{milestone_number}` وقد تتصادم إذا milestone_number غير عالمي. |
| HIGH | TODO | ChangeOrder budget | عند status APPROVED يضيف cost_impact كل after_update، وقد يكرر الميزانية والمدة. |
| REVIEW | TODO | Workflow SQL JSON | auto workflow يستخدم `json_array_length`; يحتاج فحص توافق PostgreSQL/SQLite. |
| REVIEW | TODO | Boolean raw SQL | عدة مواضع تستخدم `is_active = 1` مع Boolean؛ تحتاج فحص توافق قاعدة البيانات. |
| HIGH | TODO | Balance after_commit | معالجة الأرصدة بعد commit تفتح Session جديدة وتحدث كيانات كثيرة؛ جيدة للفصل لكنها قد تثقل الطلب وتحتاج مراقبة. |
| REVIEW | TODO | Balance get customer ids | `_get_customer_ids_from_payment` يستخدم `session.get`، وإذا مُرّر connection SQL عادي قد يفشل بصمت. |
| REVIEW | TODO | SaleReturn balance SQL | يستخدم `ANY(:pids)` مع قائمة Python؛ يحتاج فحص PostgreSQL/SQLite. |
| HIGH | TODO | Silent failures | آخر الملف يحتوي listeners كثيرة تبتلع الاستثناءات، ما يحمي الحفظ لكنه قد يخفي انحرافات أرصدة/GL/مخزون. |

---

# 7. قائمة التحسينات المرشحة بعد إكمال `models.py`

لا يتم تنفيذ أي بند قبل اختيار دفعة صغيرة وآمنة:

## 7.1 تحسينات صغيرة وآمنة نسبيًا

| الأولوية | البند |
|---|---|
| HIGH | تحديث `SystemSettings.set_setting()` لمسح `system_settings:template_settings:v1` و`system_settings:module_flags:v1`. |
| MEDIUM | توثيق مفاتيح إعدادات الشركة وتوحيد `COMPANY_NAME` مع `company_name/CompanyName`. |
| MEDIUM | إزالة/تعطيل كود ميت واضح مثل الجزء بعد `return` في `_gl_on_service_complete` بعد تأكيد عدم استخدامه. |
| MEDIUM | توثيق حقول أسعار المنتج ومعنى كل حقل في routes والقوالب. |
| MEDIUM | مراجعة COUNT-based code generation وإضافة retry محدود بدل الاعتماد على count فقط. |

## 7.2 تحسينات تحتاج اختبار مالي/مخزون

| الأولوية | البند |
|---|---|
| CRITICAL | مراجعة GL helpers وقرار posted immutability في `_gl_upsert_batch_and_entries`. |
| CRITICAL | مراجعة GL الشيكات والدفعات وPaymentSplit قبل أي تعديل. |
| CRITICAL | مراجعة Sale/SaleReturn GL وتضارب آليتي مرتجعات المبيعات. |
| CRITICAL | مراجعة StockLevel/reservation/PreOrder/Online reservation policy وتوحيدها. |
| HIGH | إصلاح خطر double stock في `SaleReturnLine.after_update` إن ثبت بالاختبار. |
| HIGH | إصلاح `Product.cost_price` غير الموجود في damaged return إن ثبت أنه مستخدم. |
| HIGH | مراجعة `_update_sale_payment_totals` مقابل split/currency/check statuses. |
| HIGH | مراجعة Service total_paid/status/tax consistency. |
| HIGH | مراجعة ProjectCost/Revenue/TimeLog/ChangeOrder double counting. |

## 7.3 تحسينات تنظيمية كبيرة مؤجلة

| الأولوية | البند |
|---|---|
| HIGH | فصل business logic وGL وstock side effects من `models.py` إلى services تدريجيًا. |
| HIGH | نقل API helpers وcommit داخل model methods إلى services/routes. |
| HIGH | تقليل properties التي تستعلم داخل القوائم واستبدالها باستعلامات مجمعة. |
| HIGH | مراجعة كل listeners التي تبتلع الاستثناءات وإضافة مراقبة/Audit للانحرافات. |
| HIGH | فحص PCI: عدم تخزين PAN كاملًا في `OnlinePayment` أو عزله بتصميم آمن. |
| MEDIUM | توحيد FX capture/update/cache وإزالة التكرار الكبير في listeners. |

---

# 8. ترتيب العمل القادم المقترح

| الترتيب | الملف/الوحدة | الهدف | الحالة |
|---|---|---|---|
| 1 | `models.py` | تمت الدراسة الكاملة والتوثيق. | DONE |
| 2 | دفعة صغيرة من `models.py` | تنفيذ تحسينات آمنة جدًا: كاش SystemSettings + مفاتيح company + كود ميت واضح فقط. | READY |
| 3 | `routes/checks.py` | استكمال فحص الشيكات وربطها بما ظهر في `Check` و`PaymentSplit`. | IN_REVIEW |
| 4 | `routes/payments.py` | فحص الدفعات وsplit والشيكات وGL. | TODO |
| 5 | `routes/sales.py` + `routes/sale_returns.py` | فحص المبيعات والمرتجعات والمخزون وGL. | TODO |
| 6 | `routes/expenses.py` | فحص المصاريف وentity/payee وGL. | TODO |
| 7 | `routes/ledger_blueprint.py` | فحص CSRF exemption ودفتر الأستاذ. | TODO |
| 8 | `acl.py` و`permissions_config/blueprint_guards.py` | فحص الصلاحيات المركزية. | TODO |

---

آخر تحديث: 2026-05-15
