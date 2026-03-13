# مراجعة شاملة للـ Enums — كل الملفات (فرونت، باك، بيز)

## 1. مصدر التعريف

| الموقع | الملف | المحتوى |
|--------|-------|---------|
| **Backend** | `models.py` | PaymentMethod, PaymentStatus, PaymentDirection, InvoiceStatus, PaymentProgress, TimesheetStatus, TaskStatus, SaleStatus, ServiceStatus, ServicePriority, TransferDirection, OnlinePaymentStatus, OnlineCartStatus, PreOrderStatus, CustomerCategory, WarehouseType, PaymentEntityType, InvoiceSource, PartnerSettlementStatus, SupplierSettlementStatus, SupplierSettlementMode, ProductCondition, ShipmentStatus, ShipmentPriority, DeliveryMethod, AccountType, DeletionType, DeletionStatus, AuthEvent, CheckStatus, **EngineeringTaskStatus** |
| **Backend** | `permissions_config/enums.py` | SystemPermissions, SystemRoles |
| **Backend** | `notifications.py` | NotificationType, NotificationPriority |
| **Frontend (JS)** | `payment_form.js`, `payments.js` | ENTITY_ENUM (مرادف لـ PaymentEntityType للفلتر)، AR_STATUS (مرادف لعرض PaymentStatus بالعربي) — يجب أن تطابق القيم القادمة من الـ API. |

---

## 2. التعديلات المنفذة (عدم تعارض + وجود كل القيم)

### 2.1 Engineering: توحيد حالة المهمة الهندسية
- **المشكلة:** قالب `engineering/tasks.html` كان يستخدم `TaskStatus` (من models) بينما الجدول `EngineeringTask` يستخدم قيماً مختلفة: `PENDING`, `ASSIGNED`, `IN_PROGRESS`, `ON_HOLD`, **REVIEW**, `COMPLETED`, `CANCELLED`, **DEFERRED** (بدون TODO).
- **الإجراء:**
  - إضافة **`EngineeringTaskStatus`** في `models.py` بكل القيم المذكورة أعلاه مع `label` عربي.
  - إضافة `EngineeringTaskStatus` إلى حقن القوالب في `app.py` (`inject_enums`).
  - استبدال استخدام `TaskStatus` في `templates/engineering/tasks.html` بـ **`EngineeringTaskStatus`** (قائمة الحالة + عرض الشارة)، بحيث القائمة والعرض يطابقان قيم عمود `eng_task_status` ولا يظهر خيار غير موجود (مثل TODO) ولا تُخفى حالات (مثل REVIEW، DEFERRED).

### 2.2 Shipments: استخدام الـ enum بدل النص الحرفي
- في `routes/shipments.py` تم استبدال النصوص الحرفية لحالة الشحنة بقيم الـ enum:
  - `"ARRIVED"` → `ShipmentStatus.ARRIVED.value`
  - `"CANCELLED"` → `ShipmentStatus.CANCELLED.value`
  - `"IN_TRANSIT"` → `ShipmentStatus.IN_TRANSIT.value`
  - `"IN_CUSTOMS"` → `ShipmentStatus.IN_CUSTOMS.value`
  - `"DELIVERED"` → `ShipmentStatus.DELIVERED.value`
  - `"RETURNED"` → `ShipmentStatus.RETURNED.value`
- بهذا لا يُستخدم أي نص حرفي لحالة الشحنة في الـ route، والمصدر الوحيد للقيم هو `ShipmentStatus` في `models.py`.

### 2.3 Frontend: توحيد AR_STATUS مع PaymentStatus
- **PaymentStatus** (backend): `PENDING`, `COMPLETED`, `FAILED`, `REFUNDED`, `CANCELLED`.
- في `payment_form.js` كان `AR_STATUS` يفتقد **CANCELLED**.
- تمت إضافة `CANCELLED: 'ملغية'` إلى `AR_STATUS` في `payment_form.js` ليتطابق مع `payments.js` ومع الـ API.

---

## 3. قواعد للمستقبل (عدم تعارض ولا شيء غير موجود)

1. **تعريف الحالات (Status/Type) في مكان واحد:** في الـ backend داخل `models.py` (أو `permissions_config/enums.py` للصلاحيات، و`notifications.py` للإشعارات). أي قائمة قيم جديدة تُضاف كـ enum أو كقائمة معرّفة مرة واحدة.
2. **في الـ Routes:** استخدم دائماً `EnumName.VALUE.value` (أو الـ enum نفسه إن كان النموذج يقبله) وليس نصوصاً حرفية مثل `"PENDING"` أو `"COMPLETED"` حتى لا تظهر قيم غير معرّفة في الـ enum أو تتعارض معها.
3. **في القوالب:** استخدم الـ enum المحقون من `app.py` (مثل `EngineeringTaskStatus`, `TaskStatus`, `PaymentStatus`) للمقارنة والعرض. للمقارنة مع قيمة من الـ DB استخدم `SomeEnum.VALUE.value` لأن العمود عادة يُرجع string.
4. **في الـ JS:** إذا كان هناك ثابت يعكس حالة أو نوعاً (مثل ENTITY_ENUM أو AR_STATUS) فيجب أن تحتوي على **نفس القيم** التي يرسلها الـ API أو يستخدمها الـ backend (من الـ enum المناسب). إضافة أو حذف قيمة فقط بعد تحديث الـ enum في الـ backend.
5. **قوائم الـ sa_str_enum في models:** عند إضافة عمود بحالة محدودة، يفضّل تعريف enum في `models.py` (مثل `EngineeringTaskStatus`) واستخدام قيمه في `sa_str_enum` إن أمكن، أو على الأقل الاحتفاظ بقائمة القيم في مكان واحد وتوثيقها هنا.

---

## 4. مرجع سريع: تطابق JS ↔ Backend

| JS (قيمة مفتاح/عرض) | Backend Enum | ملاحظة |
|----------------------|--------------|--------|
| ENTITY_ENUM: customer→CUSTOMER, supplier→SUPPLIER, … | PaymentEntityType | نفس القيم المستخدمة في الفلتر والـ API. |
| AR_STATUS: PENDING, COMPLETED, FAILED, REFUNDED, CANCELLED | PaymentStatus | تم توحيد CANCELLED في payment_form.js وpayments.js. |

---

## 5. ملخص الملفات المعدّلة

| الملف | التعديل |
|-------|---------|
| `models.py` | إضافة `EngineeringTaskStatus` مع كل قيم `eng_task_status` و`label` عربي. |
| `app.py` | استيراد وحقن `EngineeringTaskStatus` في القوالب. |
| `templates/engineering/tasks.html` | استخدام `EngineeringTaskStatus` بدل `TaskStatus` للقائمة والعرض. |
| `routes/shipments.py` | استبدال نصوص الحالة بـ `ShipmentStatus.*.value`. |
| `static/js/payment_form.js` | إضافة `CANCELLED` إلى `AR_STATUS`. |

بهذا تكون كل الـ enums المستخدمة في الواجهة والـ routes والـ business logic إما معرّفة في مكان واحد أو مذكورة صراحة في هذا المستند، ولا يُفترض وجود قيم غير معرّفة أو متعارضة.
