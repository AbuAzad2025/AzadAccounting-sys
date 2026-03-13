# الفهرس الشامل للمشروع (Index)

هذا المجلد يحتوي على **فهرس فعلي** يُولَّد بواسطة السكريبت `scripts/generate_index.py` ويشمل كل المكونات العملية.

## تشغيل الفهرسة (محلي أو إنتاج)

من جذر المشروع (مع تفعيل البيئة الافتراضية):

```bash
python scripts/generate_index.py
```

على سيرفر الإنتاج (بعد النشر):

```bash
cd /path/to/garage_manager
source venv/bin/activate   # أو: .\venv\Scripts\Activate.ps1 على Windows
python scripts/generate_index.py
```

حفظ الفهرسة في مسار آخر (مثلاً للمراجعة أو النسخ الاحتياطي):

```bash
python scripts/generate_index.py --output-dir /var/www/app/index
python scripts/generate_index.py -o ./backup_index_$(date +%Y%m%d)
```

---

## الملفات المُولَّدة

| الملف | المحتوى |
|-------|---------|
| **INDEX_META.json** | وقت التوليد، إصدار Python، بيئة التشغيل، وأعداد (مسارات، نماذج، صلاحيات، إلخ). مفيد لمراجعة الإنتاج. |
| **INDEX_ROUTES.json** | كل مسارات التطبيق: rule, endpoint, methods. |
| **INDEX_ROUTES.md** | نفس المسارات كجدول Markdown. |
| **INDEX_MODELS.json** | النماذج: جدول (DB) ↔ اسم الكلاس. |
| **INDEX_MODELS.md** | نفس النماذج كجدول. |
| **INDEX_PERMISSIONS.json** | الصلاحيات (SystemPermissions) والأدوار (SystemRoles) مع القيم. |
| **INDEX_PERMISSIONS.md** | نفس الصلاحيات والأدوار كجدول. |
| **INDEX_BLUEPRINTS.json** | كل Blueprint مع url_prefix وصلاحيات القراءة/الكتابة (ACL). |
| **INDEX_BLUEPRINTS.md** | نفس الـ Blueprints كجدول. |
| **INDEX_FORMS.json** | أسماء كلاسات نماذج Flask-WTF (من forms.py). |
| **INDEX_FORMS.md** | قائمة النماذج. |
| **INDEX_TEMPLATES.json** | إحصائيات القوالب (عدد الملفات لكل مجلد تحت templates/). |
| **INDEX_TEMPLATES.md** | جدول مجلدات القوالب وعدد الملفات. |
| **INDEX_SERVICES.md** | قائمة ملفات الخدمات (services/*.py). |
| **INDEX_SUMMARY.md** | ملخص واحد: تاريخ التوليد، الأعداد، وقائمة الملفات المُولَّدة. |

---

## استخدام الفهرس

- **مراجعة الإنتاج:** قارن `INDEX_META.json` بعد كل نشر (عدد المسارات والنماذج والصلاحيات).
- **البحث عن مسار أو endpoint:** ابحث في `INDEX_ROUTES.md` أو `INDEX_ROUTES.json`.
- **ربط جدول بقاعدة البيانات باسم الكلاس:** استخدم `INDEX_MODELS.md`.
- **التحقق من صلاحية أو دور:** استخدم `INDEX_PERMISSIONS.md`.
- **معرفة صلاحيات كل Blueprint:** استخدم `INDEX_BLUEPRINTS.md`.

السكريبت محفوظ في المشروع ويمكن تشغيله في أي وقت محلياً أو على سيرفر الإنتاج.
