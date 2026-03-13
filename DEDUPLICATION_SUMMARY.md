# ملخص إزالة التكرار (فرونت اند + باك اند)

## الجولة الثالثة: تغطية كامل ملفات المشروع

### فرونت اند – توحيد debounce و showNotification
- **common-utils.js:** إضافة `showNotification(message, type)` (تستدعي `showAlert`) وتصديرها على `window.showNotification`؛ `debounce` و `stripScripts` مُصدَّران مسبقاً.
- **استخدام الدوال الموحدة مع fallback محلي:**
  - **debounce:** payments.js, payment_form.js, service.js, event-utils.js, app.js — استخدام `window.debounce` مع fallback.
  - **showNotification:** warehouses.js, import_upload.js, app.js — استخدام `window.showNotification` مع fallback.

### فرونت اند – توحيد stripScripts
- **common-utils.js:** إضافة `stripScripts(html)` وتصديرها على `window.stripScripts`.
- **ملفات محدَّثة:** notes.js, vendors.js, expenses.js, sales.js, customers.js — استخدام `window.stripScripts` مع fallback محلي.

### فرونت اند – توحيد toNumber / deriveEntityLabel / normalizeEntity / normalizeMethod / validDates
- **payment_form.js:** استبدال التعريفات المحلية لـ toNumber, normalizeEntity, normalizeMethod, normDir, validDates, deriveEntityLabel باستخدام `window.*` من common-utils مع fallback.
- **payments.js:** استبدال normalizeEntity, normalizeMethod, validDates واستخدام `window.*`؛ إضافة `deriveEntityLabel` من window مع fallback (لم تكن معرَّفة محلياً).
- **service.js:** استبدال `toNum` المحلي بـ `window.toNumber` مع fallback.

### باك اند – توحيد _get_or_404 في shipments و service
- **shipments.py:** إزالة الدالة المحلية `_sa_get_or_404` واستيراد `_get_or_404` من utils؛ استبدال كل الاستدعاءات بـ `_get_or_404(..., load_options=[...])`.
- **service.py:** استبدال المعامل `options=` بـ `load_options=` في كل استدعاءات `_get_or_404`.

---

## الجولة الثانية: إزالة كل الدوال المكررة

### باك اند – توحيد _get_or_404
- **مصدر واحد:** الدالة `_get_or_404` في **utils.py** (مع `load_options` و`pk_name`).
- **إزالة التعريفات المكررة من:** notes.py, roles.py, permissions.py, users.py, vendors.py, service.py, expenses.py, customers.py, sales.py, barcode_scanner.py, shop.py.
- **استبدال _sa_get_or_404 في auth.py** بـ `_get_or_404` من utils.
- **warehouses.py** كان يستوردها من utils بالفعل — لم يُغيّر.
- استبدال كل الاستدعاءات التي كانت تستخدم `options=[...]` أو `*options` بـ `load_options=[...]`.

### باك اند – إزالة alias زائد في api.py
- إزالة `_query_limit = _limit_from_request` واستبدال كل استخدامات `_query_limit` المحلية بـ `_limit_from_request`. استدعاءات `utils._query_limit` بقيت كما هي (دالة مختلفة في الحزمة utils).

### فرونت اند – توحيد getCSRFToken
- **مصدر واحد:** **csrf-utils.js** يعرّف `getCSRFToken` ويضعه على `window.getCSRFToken`، مع دعم `meta[name="csrf-token"]` و`#csrf_token` و`input[name="csrf_token"]`.
- **vendors.js:** إزالة الدالة المحلية `getCsrfToken` واستخدام `window.getCSRFToken` مع fallback محلي إن لم تُحمّل csrf-utils أولاً.
- **barcode.js:** استخدام `window.getCSRFToken` مع fallback محلي.
- **payments.js:** إضافة `getCSRFToken` (من window أو fallback) واستبدال كل التكرارات الطويلة لقراءة الـ CSRF بـ `getCSRFToken()`.

---

## ما تم تنفيذه (الجولة الأولى)

### 1. قوالب الأخطاء (Templates)
- **إنشاء** `templates/errors/_error_base.html`: قالب أساسي موحد يحتوي الهيكل والـ CSS المشترك لصفحات الأخطاء.
- **تبسيط** `401.html`, `502.html`, `503.html`: أصبحت تمتد من `_error_base.html` وتعرّف فقط المحتوى المختلف (العنوان، الوصف، الأزرار، التذييل).
- **النتيجة:** تقليل تكرار عشرات الأسطر في كل من 401/502/503 مع الحفاظ على نفس المظهر والسلوك.
- **429.html** لم تُغيَّر لأن لها هيكلاً مختلفاً (عداد تنازلي، ألوان مختلفة).

### 2. JavaScript المشترك (Frontend)
- **إضافة في** `static/js/common-utils.js`:
  - **escapeHtml(value):** هروب أحرف HTML (للاستخدام في عرض نصوص آمن).
  - **fetchWithTimeout(url, options, timeoutMs):** استدعاء `fetch` مع حد زمني.
  - تصدير الدالتين إلى `window` لاستخدامهما من أي سكربت.
- **تبسيط التكرار:**
  - **print.js:** استخدام `window.escapeHtml` مع fallback محلي إن لم يكن محمّلاً.
  - **notes.js:** نفس الأسلوب لـ `escapeHtml`.
  - **charts.js:** نفس الأسلوب لـ `escapeHtml`.
  - **warehouses.js:** استخدام `window.fetchWithTimeout` مع fallback محلي.
  - **vendors.js:** استخدام `window.fetchWithTimeout` مع fallback محلي.

### 3. باك اند (من الجولة السابقة + api)
- **routes/api.py:** دمج مساري `/` و `/docs` في دالة واحدة، إزالة `api_error_response` و `api_success_response`، إزالة تكرار `barcode/validate` (الاعتماد على `barcode.py` فقط).
- **routes/barcode.py:** إضافة حقل `suggested` في استجابة التحقق لتعادل سلوك الـ API السابق.

---

## ما يمكن تنفيذه لاحقاً (بدون تنفيذ حالياً)

### باك اند
- **مسارات /login:** وجود مسار في `main.py` (redirect إلى auth) ومسار في `auth.py` — مقصود (دعم `/login` و `/auth/login`)، لا حاجة لتغيير.
- **partner_settlements و supplier_settlements:** تشابه أسماء دوال؛ يمكن استخراج وحدة مشتركة `settlements_common` لاحقاً.

### فرونت اند
- **payments.js و payment_form.js:** لا يزالان يتشاركان منطقاً (loadPayments، renderPaymentsTable، إلخ). استخراج `payments-common.js` اختياري ويتطلب مراجعة ترتيب التحميل.

---

## ملخص الملفات المعدّلة

| الملف | التعديل |
|-------|---------|
| templates/errors/_error_base.html | **جديد** — قالب أساسي للأخطاء |
| templates/errors/401.html | extends من _error_base، محتوى خاص فقط |
| templates/errors/502.html | extends من _error_base، محتوى خاص فقط |
| templates/errors/503.html | extends من _error_base، محتوى خاص + بلوك صيانة وسكربت |
| static/js/common-utils.js | إضافة escapeHtml، fetchWithTimeout وتصديرهما |
| static/js/print.js | استخدام escapeHtml من common مع fallback |
| static/js/notes.js | استخدام escapeHtml من common مع fallback |
| static/js/charts.js | استخدام escapeHtml من common مع fallback |
| static/js/warehouses.js | استخدام fetchWithTimeout من common مع fallback |
| static/js/vendors.js | استخدام fetchWithTimeout من common مع fallback |
| static/js/common-utils.js (ج3) | إضافة stripScripts، showNotification وتصديرهما |
| static/js/warehouses.js (ج3) | showNotification من window + fallback |
| static/js/import_upload.js | showNotification من window + fallback |
| static/js/app.js | showNotification و debounce من window + fallback |
| static/js/payments.js, payment_form.js | debounce من window؛ normalizeEntity، validDates، deriveEntityLabel من window |
| static/js/service.js | debounce و toNum (من window.toNumber) من window + fallback |
| static/js/event-utils.js | debounce من window + fallback |
| static/js/notes.js, sales.js, customers.js | stripScripts من window + fallback |
| routes/shipments.py | إزالة _sa_get_or_404؛ استخدام _get_or_404 من utils مع load_options |
| routes/service.py | استبدال options= بـ load_options= في _get_or_404 |

لا تغيير في سلوك التطبيق من منظور المستخدم؛ الهدف كان تقليل التكرار وتغطية كامل ملفات المشروع.
