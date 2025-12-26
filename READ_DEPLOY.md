# دليل رفع وتشغيل النظام (Deployment Guide)

هذا الدليل يشرح كيفية رفع النظام إلى GitHub وتشغيله على سيرفر PythonAnywhere (أو أي سيرفر آخر)، مع نقل البيانات.

## 1. تجهيز النظام للرفع (GitHub)

تم تجهيز الملفات اللازمة (`.gitignore`, `requirements.txt`, `wsgi.py`)، وتم تحديث إعدادات النظام ليعمل مع قواعد بيانات MySQL أو PostgreSQL أو SQLite تلقائياً.

لرفع الكود إلى GitHub، نفذ الأوامر التالية في التيرمينال (Terminal):

```bash
# 1. إضافة الملفات الجديدة والمعدلة
git add .

# 2. حفظ التغييرات
git commit -m "Prepare for deployment: Config, WSGI, and Requirements"

# 3. التأكد من الفرع (Branch)
git branch -M main

# 4. ربط المستودع بـ GitHub (إذا لم يتم من قبل)
# git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 5. رفع الملفات
git push -u origin main
```

> **ملاحظة:** مجلد `exports/` (الذي يحتوي على النسخ الاحتياطية) تم استثناؤه من الرفع للحفاظ على أمان البيانات. سنقوم بنقل البيانات بشكل منفصل.

---

## 2. الإعداد على PythonAnywhere

1.  **سحب الكود:**
    *   افتح `Bash` console في PythonAnywhere.
    *   انسخ الكود: `git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git mysite`

2.  **إنشاء البيئة الافتراضية (Virtualenv):**
    ```bash
    cd mysite
    mkvirtualenv --python=/usr/bin/python3.10 myenv
    pip install -r requirements.txt
    ```
    *(تأكد من اختيار Python 3.10)*

3.  **إعداد ملف `.env`:**
    *   أنشئ ملف `.env` في مجلد المشروع (`mysite`).
    *   ضع فيه المتغيرات التالية (مع استبدال `YOUR_PASSWORD` بكلمة مرور قاعدة البيانات التي عينتها):
        ```
        # Secret Key (مفتاح التشفير)
        SECRET_KEY=AxK0bNomy6FLt4VzYx3qhk8BybPl3NKJDI6rt6taq2Og08N7FQOCOH4aeu5pZrTkWPg
        
        # Database Settings (PostgreSQL on PythonAnywhere)
        # استبدل YOUR_PASSWORD بكلمة المرور الخاصة بقاعدة البيانات
        DATABASE_URL=postgresql://super:YOUR_PASSWORD@NASERALLAH-4986.postgres.pythonanywhere-services.com:14986/NASERALLAH$default
        
        # Email Settings
        MAIL_SERVER=smtp.gmail.com
        MAIL_PORT=587
        MAIL_USE_TLS=True
        MAIL_USERNAME=rafideen.ahmadghannam@gmail.com
        MAIL_PASSWORD=your-app-password
        MAIL_DEFAULT_SENDER=rafideen.ahmadghannam@gmail.com
        ```
    *   **هام:** اسم قاعدة البيانات الافتراضي عادة يكون `NASERALLAH$default`. تأكد من الاسم الصحيح من تبويب **Databases** (قد يكون `NASERALLAH$garage_db` إذا قمت بتسميتها هكذا).

4.  **إنشاء جداول قاعدة البيانات:**
    *   بعد إعداد الملفات، نفذ الأمر التالي في التيرمينال لإنشاء الجداول:
        ```bash
        cd ~/mysite
        flask db upgrade
        ```
        *(إذا ظهر خطأ، تأكد من صحة رابط الاتصال في ملف .env)*

5.  **إعداد WSGI:**
    *   في تبويب **Web**، اذهب إلى قسم **WSGI configuration file**.
    *   امسح المحتوى الموجود وضع التالي:
        ```python
        import sys
        import os

        # مسار المشروع
        path = '/home/YOUR_USERNAME/mysite'
        if path not in sys.path:
            sys.path.append(path)

        # تحميل متغيرات البيئة (اختياري إذا كنت تستخدم python-dotenv)
        from dotenv import load_dotenv
        project_folder = os.path.expanduser('~/mysite')
        load_dotenv(os.path.join(project_folder, '.env'))

        from app import create_app
        application = create_app()
        ```

---

## 3. نقل واستعادة البيانات

بما أننا لم نرفع ملفات النسخ الاحتياطي إلى GitHub، سنقوم بنقلها يدوياً:

1.  **تحميل ملف النسخة الاحتياطية:**
    *   من جهازك المحلي، اذهب إلى مجلد `exports` وخذ أحدث ملف JSON (مثلاً `full_backup_20251226_....json`).

2.  **رفعه للسيرفر:**
    *   في PythonAnywhere، اذهب إلى تبويب **Files**.
    *   انتقل لمجلد `mysite/exports` (أنشئه إذا لم يكن موجوداً).
    *   اضغط **Upload a file** واختر ملف JSON.

3.  **استعادة البيانات:**
    *   **الطريقة الأسهل:** بعد تشغيل الموقع، ادخل للوحة التحكم -> "مدير النسخ الاحتياطية" -> تبويب "نسخ JSON". ستجد الملف هناك، اضغط **استعادة**.
    *   **أو عن طريق التيرمينال:**
        ```bash
        cd ~/mysite
        python import_data_json.py exports/full_backup_XXXX.json
        ```

---

## ملاحظات إضافية
*   تم ضبط `config.py` ليعمل تلقائياً مع SQLite إذا لم يتم إعداد قاعدة بيانات، مما يسهل التجربة الأولية.
*   تم إضافة مكتبة `pymysql` لدعم الاتصال بقواعد MySQL في PythonAnywhere.
