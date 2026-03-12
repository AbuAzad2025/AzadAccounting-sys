# دليل النشر على خادم PythonAnywhere (Production Deployment Guide)

اتبع هذه الخطوات بدقة لنقل النظام والبيانات من جهازك المحلي إلى سيرفر الإنتاج.

## المتطلبات المسبقة
- حساب PythonAnywhere فعال.
- قاعدة بيانات PostgreSQL مهيأة على PythonAnywhere.
- بيانات الاتصال بقاعدة البيانات (Host, Port, User, Password, Database Name).

---

## الخطوة 1: تحديث الكود على GitHub
لقد قمت بالفعل برفع أحدث نسخة من الكود إلى GitHub. تأكد من أن المستودع محدث.

## الخطوة 2: تحضير ملف البيانات (محلياً)
لقد تم إنشاء ملف يحتوي على جميع بياناتك المحلية باسم:
`production_data.json.gz`
(موجود في المجلد الرئيسي للمشروع).

**هام:** لا تقم برفع هذا الملف إلى GitHub لأنه يحتوي على بيانات حساسة. سنقوم برفعه يدوياً إلى السيرفر.

## الخطوة 3: إعداد السيرفر (على PythonAnywhere)

1.  **افتح Console جديد (Bash)** في لوحة تحكم PythonAnywhere.
2.  **اسحب الكود:**
    ```bash
    git clone https://github.com/AbuAzad2025/AzadAccounting-sys.git mysite
    cd mysite
    ```
    *(إذا كان المجلد موجوداً مسبقاً، استخدم `cd mysite && git pull`)*

3.  **أنشئ البيئة الافتراضية:**
    ```bash
    mkvirtualenv --python=/usr/bin/python3.10 myenv
    pip install -r requirements.txt
    pip install psycopg2-binary
    ```

4.  **إعداد ملف `.env`:**
    أنشئ ملف `.env` في مجلد المشروع (`/home/username/mysite/.env`) وضع فيه الإعدادات التالية (استبدل القيم ببياناتك):
    ```env
    APP_ENV=production
    DEBUG=False
    SECRET_KEY=ضع_مفتاح_سري_طويل_وصعب_هنا
    DATABASE_URL=postgresql://super:PASSWORD@NASERALLAH-4986.postgres.pythonanywhere-services.com:14986/super
    ```
    *(تأكد من اسم قاعدة البيانات واسم المستخدم وكلمة المرور من تبويب Databases)*

## الخطوة 4: رفع البيانات (Upload Data)

1.  اذهب إلى تبويب **Files** في لوحة تحكم PythonAnywhere.
2.  ادخل إلى مجلد المشروع (مثلاً `mysite`).
3.  اضغط على زر **Upload a file**.
4.  اختر ملف `production_data.json.gz` من جهازك المحلي.

## الخطوة 5: استيراد البيانات (Import Data)

بعد رفع الملف، عد إلى الـ Console (Bash) ونفذ الأمر التالي لاستيراد البيانات:

```bash
# تأكد أنك داخل المجلد والبيئة الافتراضية مفعلة
workon myenv
cd ~/mysite

# تشغيل أداة الاستيراد
python Scripts/db_migration_tool.py restore
```

ستقوم هذه الأداة بمسح البيانات التجريبية على السيرفر واستبدالها ببياناتك المحلية.

## الخطوة 6: إعداد Web App (WSGI)

1.  اذهب إلى تبويب **Web**.
2.  تأكد من إعداد **Virtualenv** ليشير إلى: `/home/NASERALLAH/.virtualenvs/myenv`
3.  عدل ملف **WSGI configuration file** ليكون كالتالي:

```python
import sys
import os
from dotenv import load_dotenv

project_home = '/home/NASERALLAH/mysite'  # تأكد من اسم المجلد الصحيح

if project_home not in sys.path:
    sys.path.append(project_home)

# تحميل المتغيرات البيئية
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

from app import create_app
application = create_app()
```

4.  اضغط **Reload** في أعلى الصفحة.

---
**مبروك!** النظام الآن يعمل ببياناتك المحلية.
