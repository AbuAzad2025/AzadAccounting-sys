
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from extensions import db
from config import Config

def set_tenant_name():
    print("🎨 Updating Tenant Name directly...")
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        from models import SystemSettings
        
        def set_setting(key, value):
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                print(f"✅ Updated '{key}': {value}")
            else:
                setting = SystemSettings(key=key, value=value)
                db.session.add(setting)
                print(f"✅ Created '{key}': {value}")

        # Hardcoded Arabic strings to avoid shell issues
        set_setting('system_name', "المهندس الفلسطيني")
        set_setting('company_name', "المهندس الفلسطيني للمعدات الثقيلة")
        set_setting('COMPANY_NAME', "المهندس الفلسطيني للمعدات الثقيلة")
        
        db.session.commit()
        print("\n🎉 Tenant Name updated successfully!")

if __name__ == "__main__":
    set_tenant_name()
