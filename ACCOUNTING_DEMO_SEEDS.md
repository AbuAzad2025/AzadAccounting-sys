# بذور ديمو محاسبية شاملة (Demo Seeds)

هذا الملف يوفّر بذور بيانات “معقّدة وواضحة” لتغطية أغلب أنواع الحركات المحاسبية والتشغيلية في النظام: عميل/مورد/شريك + عملات متعددة + شيكات مرتدة + مرتجعات + فواتير + خدمات + دفعات + مصاريف + تسويات + شحنات + ملاحظات + حركات مستودعات.

## 1) تشغيل بذور الديمو الشاملة

يشغّل سيناريو واحد يُنشئ:
- عميل + مورد + شريك (ومزامنة علاقات الطرف المقابل عبر customer_id)
- عملات (ILS/USD/JOD/EUR) + أسعار صرف ثابتة (Manual/demo)
- مستودعات (MAIN/EXCHANGE/PARTNER/ONLINE/INVENTORY) + إدخال/إخراج/تحويل + حجز/فك حجز
- شحنة كاملة (DRAFT → IN_TRANSIT → IN_CUSTOMS → ARRIVED → DELIVERED) + بنود + شركاء + مصاريف شحن/جمارك + دفعة شحن
- مبيعات + دفعة + مرتجع مبيعات
- فاتورة USD + دفعة USD (تُحوّل إلى ILS عند الحساب)
- خدمة (قطع + أجرة) مع نسبة شريك
- شيك USD مرتد (Payment FAILED + Check BOUNCED)
- مصاريف مرتبطة بالعميل/المورد/الشريك
- خصم مخزون تالف (Stock Adjustment) + مصروف مرتبط به
- ملاحظات متنوعة (Pinned/Notification/Targeted) مرتبطة بكيانات مختلفة
- دفعات صادرة للمورد وللشريك
- تسوية مورد + تسوية شريك (إن اخترت ذلك)

الأمر:

```bash
flask seed-accounting-demo
```

خيارات مفيدة:

```bash
flask seed-accounting-demo --tag DEMO2026 --days-ago 0 --with-settlements
flask seed-accounting-demo --tag DEMO2026 --no-settlements
```

المخرجات تكون JSON فيها `seed_tag` ومعرّفات الكيانات المنشأة (customer_id / supplier_id / partner_id …) لاستخدامها مباشرة في الواجهات أو أوامر الفحص.

## 2) بذرة كشف حساب عميل (أخفّ)

إذا أردت “كشف حساب” سريع للعميل الحالي مع مبيعات/دفعات/خدمة/مصاريف/شيك:

```bash
flask seed-customer-statement-demo --customer-id 3 --warehouse-id 3 --days-ago 0 --tag STMT1
```

## 3) فحص سلامة التكامل بعد البذور

هذه أوامر موجودة في النظام تساعدك على التأكد أن الحسابات والاتساق يعملان:

```bash
flask currency-validate
flask currency-health
flask sync-balances
flask audit-integrity
```

ولعرض “تقرير عملات” سريع:

```bash
flask currency-report
```

## 4) مسارات UI مفيدة للاختبار اليدوي (Smoke)

بعد تشغيل `seed-accounting-demo` خذ `customer_id` من JSON ثم افتح:

- كشف حساب العميل:
  - `/customers/<customer_id>/account_statement`
- تسويات المورد:
  - `/suppliers/<supplier_id>/settlements`
- تسويات الشريك:
  - `/partners/<partner_id>/settlements`

إذا كانت الصفحة تطلب صلاحيات، شغّل مرة واحدة:

```bash
flask seed-all --force
```

## 5) ما الذي يعتبر “أنواع حسابات” مغطاة هنا؟

- **العميل**: مبيعات، دفعات واردة (Cash/Bank)، دفعات بعملة أجنبية، شيك مرتد، مرتجع مبيعات، مصروف مرتبط بالعميل، خدمات (قطع + أجرة).
- **المورد**: تبادل/استلام مخزون (Exchange IN)، دفعات صادرة، مصروف مرتبط بالمورد، تسوية مورد (Draft ثم Confirm).
- **الشريك**: حصة من قطع الخدمة/المبيعات، دفعات صادرة، مصروف مرتبط بالشريك، تسوية شريك (Draft ثم Confirm).
- **العملات**: ILS/USD/JOD/EUR مع أسعار صرف مُثبّتة لضمان أن الحسابات لا تعتمد على مصادر خارجية أثناء الاختبار.
