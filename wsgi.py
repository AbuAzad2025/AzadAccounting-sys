import sys
import os
from dotenv import load_dotenv

# 1. تحديد مسار المشروع
project_home = '/home/NASERALLAH/ramallah'

# 2. إضافة المسار لبيئة التشغيل
if project_home not in sys.path:
    sys.path.append(project_home)

# 3. تحميل ملف .env الموجود في المشروع
load_dotenv(os.path.join(project_home, '.env'))

# 4. إعدادات PythonAnywhere (تم دمجها هنا لراحتك فلا داعي لتعديل .env)
# هذه الإعدادات تمنع خطأ "too many clients"
os.environ['SQLALCHEMY_POOL_SIZE'] = '5'
os.environ['SQLALCHEMY_MAX_OVERFLOW'] = '10'
os.environ['SQLALCHEMY_POOL_RECYCLE'] = '280'
os.environ['SQLALCHEMY_POOL_TIMEOUT'] = '30'

# 5. تشغيل التطبيق
from app import create_app
application = create_app()
