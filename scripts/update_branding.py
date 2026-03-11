
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from extensions import db
from config import Config

def update_system_branding(new_system_name, new_company_name, new_logo_path=None):
    print("🎨 Updating System Branding (Name & Logo)...")
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Import SystemSettings model (must be inside app context)
        from models import SystemSettings
        
        # Helper to update or create setting
        def set_setting(key, value):
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                print(f"✅ Updated '{key}': {value}")
            else:
                setting = SystemSettings(key=key, value=value)
                db.session.add(setting)
                print(f"✅ Created '{key}': {value}")

        if new_system_name:
            set_setting('system_name', new_system_name)
        
        if new_company_name:
            set_setting('company_name', new_company_name)
            set_setting('COMPANY_NAME', new_company_name) # Update uppercase too just in case

        if new_logo_path:
            # Check if logo exists if it's a local file path
            if not new_logo_path.startswith('http'):
                full_path = os.path.join(app.root_path, 'static', new_logo_path.replace('static/', ''))
                if not os.path.exists(full_path):
                    print(f"⚠️ WARNING: Logo file not found at {full_path}. Setting updated anyway.")
            
            set_setting('custom_logo', new_logo_path)

        # Footer text is now HARDCODED in templates/partials/footer.html to protect IP rights.
        # if new_footer_text:
        #    set_setting('footer_text', new_footer_text)
        
        db.session.commit()
        print("\n🎉 Branding updated successfully!")
        print("Note: You may need to restart the application for changes to take effect immediately.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_branding.py <system_name> [company_name] [logo_path]")
        print("Example: python update_branding.py 'My Garage' 'My Company Ltd.' 'img/my_logo.png'")
        sys.exit(1)
    
    sys_name = sys.argv[1]
    comp_name = sys.argv[2] if len(sys.argv) > 2 else None
    logo = sys.argv[3] if len(sys.argv) > 3 else None
    
    update_system_branding(sys_name, comp_name, logo)
