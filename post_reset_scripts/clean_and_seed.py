
import sys
import os
import glob
import importlib.util
from sqlalchemy import text, inspect

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, bootstrap_database
from extensions import db
from models import User, Role, SystemSettings, Warehouse, GLBatch, GLEntry, GL_ACCOUNTS
from permissions_config.permissions import PermissionsRegistry
import datetime
from decimal import Decimal

def clean_and_seed():
    """
    Cleans the database and seeds initial data for a new tenant.
    Integrated with scripts2 logic for full reset.
    """
    print("🚀 Starting System Cleanup & Seeding...")
    app = create_app()
    
    with app.app_context():
        # 1. Clean Database
        print("🗑️  Dropping all tables (CASCADE)...")
        conn = db.session.connection()
        inspector = inspect(db.engine)
        for table_name in inspector.get_table_names():
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
        db.session.commit()
        print("✅ Tables dropped.")
        
        # 2. Recreate Structure
        print("🏗️  Creating tables...")
        db.create_all()
        print("✅ Tables created.")
        
        # 3. Bootstrap (Settings, Expense Types)
        print("🔧 Running Bootstrap...")
        bootstrap_database()
        
        # 4. Auto-Run Post Reset Scripts
        print("💰 Seeding Shared Data from post_reset_scripts...")
        post_reset_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(post_reset_dir):
            script_files = glob.glob(os.path.join(post_reset_dir, '*.py'))
            print(f"📂 Found {len(script_files)} potential scripts in {post_reset_dir}")
            
            for script_file in sorted(script_files):
                script_name = os.path.basename(script_file)
                if script_name.startswith('__') or script_name == 'clean_and_seed.py': 
                    continue
                    
                print(f"▶️  Running script: {script_name}")
                try:
                    # Dynamic import and execution
                    spec = importlib.util.spec_from_file_location(f"post_reset_{script_name[:-3]}", script_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for 'seed' or 'run' or 'main' function
                    if hasattr(module, 'seed_permissions'):
                        module.seed_permissions(app)
                    elif hasattr(module, 'seed_accounts'):
                        module.seed_accounts(app)
                    elif hasattr(module, 'seed'):
                        module.seed(app)
                    elif hasattr(module, 'run'):
                        module.run(app)
                    else:
                        print(f"⚠️  Script {script_name} has no entry point (seed/run/main)")
                        
                except Exception as e:
                    print(f"❌ Failed to run script {script_name}: {e}")

        # 5. Initialize Tenant Settings (Merged from scripts2/initialize_tenant.py)
        print("\n🏢 Initializing Default Tenant Settings...")
        
        # Company Info Defaults
        SystemSettings.set_setting('company_name', "My Garage", is_public=True)
        SystemSettings.set_setting('company_phone', "", is_public=True)
        SystemSettings.set_setting('company_address', "", is_public=True)
        SystemSettings.set_setting('tax_rate', 16.0, data_type='number', is_public=True)
        SystemSettings.set_setting('currency', 'ILS', is_public=True)
        
        # Warehouse
        if Warehouse.query.count() == 0:
            print("   Creating 'Main Warehouse'...")
            main_wh = Warehouse(
                name="Main Warehouse",
                location="Main",
                is_active=True
            )
            db.session.add(main_wh)
            db.session.commit()
        
        # Opening Balance (Optional - skipped in auto-reset or set to 0)
        # To enable opening balance in auto-reset, we would need to pass parameters or use defaults.
        # For now, we assume 0 opening balance for auto-reset to avoid blocking.
        
        print("✅ Tenant settings initialized.")

        # 5.5 Create Hidden System Owner (ID 1)
        # This is required for the Master Key logic in auth.py to work (it loads User 1)
        print("👻 Ensuring System Owner (ID 1)...")
        owner_role = Role.query.filter_by(name='owner').first()
        if owner_role:
            # Check if ID 1 exists (it shouldn't after drop_all, but just in case)
            owner_user = User.query.get(1)
            if not owner_user:
                import secrets
                import string
                # Random password, access is via Master Key only
                rnd_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
                owner_user = User(
                    id=1, # Force ID 1
                    username='__OWNER__',
                    email='owner@system.local',
                    is_active=True,
                    role=owner_role,
                    is_system_account=True
                )
                owner_user.set_password(rnd_pass)
                db.session.add(owner_user)
                db.session.commit()
                print("✅ System Owner (ID 1) created.")
            else:
                print("ℹ️  System Owner (ID 1) already exists.")
        else:
            print("⚠️  Owner role not found, skipping System Owner creation.")

        # 6. Create Admin User
        print("👤 Creating Admin User...")
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("❌ Admin role not found!")
            return

        # Ensure ID sequence is correct after heavy operations
        try:
            db.session.execute(text("SELECT setval(pg_get_serial_sequence('users', 'id'), coalesce(max(id),0) + 1, false) FROM users;"))
            db.session.commit()
        except Exception:
            pass 

        admin_user = User(
            username='admin',
            email='admin@example.com',
            is_active=True,
            role=admin_role,
            is_system_account=True # Protect this account
        )
        admin_user.set_password('admin')
        db.session.add(admin_user)
        db.session.commit()
        print(f"✅ Admin User Created: username='admin', password='admin'")
        
        print("\n✨ System is ready for the new tenant! ✨")

if __name__ == "__main__":
    if input("⚠️  WARNING: This will DELETE ALL DATA. Are you sure? (y/n): ").lower() == 'y':
        clean_and_seed()
    else:
        print("Operation cancelled.")
