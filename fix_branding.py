
import sys
import os
from app import create_app
from extensions import db
from models import SystemSettings

def fix_branding_settings():
    app = create_app()
    with app.app_context():
        print("🔧 Fixing Branding Settings...")
        
        # 1. Update System Name
        sys_name = SystemSettings.query.filter_by(key='system_name').first()
        if not sys_name:
            sys_name = SystemSettings(key='system_name', value='نظام الحازم', description='اسم النظام')
            db.session.add(sys_name)
        else:
            sys_name.value = 'نظام الحازم'
            
        # 2. Update Company Name
        comp_name = SystemSettings.query.filter_by(key='company_name').first()
        if not comp_name:
            comp_name = SystemSettings(key='company_name', value='شركة الحازم', description='اسم الشركة')
            db.session.add(comp_name)
        else:
            comp_name.value = 'شركة الحازم'
            
        # 3. Update Login Title
        login_title = SystemSettings.query.filter_by(key='login_title').first()
        if not login_title:
            login_title = SystemSettings(key='login_title', value='مرحباً بك في نظام الحازم', description='عنوان صفحة الدخول')
            db.session.add(login_title)
        else:
            login_title.value = 'مرحباً بك في نظام الحازم'

        db.session.commit()
        print("✅ Branding settings updated successfully!")
        print("Please reload the web app to see changes.")

if __name__ == "__main__":
    fix_branding_settings()
