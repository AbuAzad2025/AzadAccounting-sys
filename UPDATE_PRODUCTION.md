# تعليمات تحديث الإنتاج (Production Update)

## تحديث الفهارس وقاعدة البيانات (Indexes Update)

لتطبيق التغييرات الأخيرة (تحسينات الأداء والفهارس) على سيرفر الإنتاج، يرجى اتباع الخطوات التالية:

### 1. تحديث الكود المصدري
قم بسحب آخر التغييرات من المستودع:

```bash
cd /path/to/project
git pull origin main
```

### 2. تحديث قاعدة البيانات
لديك خياران لتحديث قاعدة البيانات:

#### الخيار أ: باستخدام Flask-Migrate (المفضل)
إذا كان السيرفر مهيأ بشكل صحيح، يمكنك تشغيل أمر الترحيل مباشرة:

```bash
# تفعيل البيئة الافتراضية أولاً
source .venv/bin/activate  # أو حسب مسار البيئة لديك

# تشغيل الترحيل
python -m flask db upgrade
```

#### الخيار ب: باستخدام ملف SQL (يدوي)
إذا واجهت مشاكل في الترحيل التلقائي، يمكنك تنفيذ ملف SQL المرفق مباشرة على قاعدة البيانات:

```bash
psql -h <host> -U <username> -d <database_name> -f production_update_indexes.sql
```

> **ملاحظة:** ملف `production_update_indexes.sql` يقوم أيضاً بتحديث رقم إصدار قاعدة البيانات (alembic version) لضمان التوافق مستقبلاً.

### 3. إعادة تشغيل الخدمة
بعد التحديث، يفضل إعادة تشغيل خدمة التطبيق لتطبيق أي تغييرات في الكود:

```bash
# مثال (Gunicorn/Systemd)
sudo systemctl restart garage_manager
# أو
sudo service garage_manager restart
```
