
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import Role, Permission
from permissions_config.permissions import PermissionsRegistry

def seed_permissions(app=None):
    """
    Seed permissions and roles based on PermissionsRegistry.
    Can be called with an existing app instance or will create one.
    """
    if app is None:
        try:
            from flask import current_app
            if current_app:
                app = current_app
        except RuntimeError:
            pass
            
    if not app:
        app = create_app()

    with app.app_context():
        print("🌱 Seeding Permissions & Roles...")
        
        # 1. Create Permissions
        all_perms = []
        for module, perms_dict in PermissionsRegistry.PERMISSIONS.items():
            for code, data in perms_dict.items():
                existing = Permission.query.filter_by(code=code).first()
                if not existing:
                    p = Permission(
                        code=code,
                        name=data['name_ar'], # Using Arabic name as 'name' field
                        description=data.get('description', '')
                    )
                    db.session.add(p)
                    all_perms.append(p)
                else:
                    all_perms.append(existing)
        
        db.session.commit()
        print(f"✅ Seeded {len(all_perms)} permissions.")
        
        # 2. Create Roles & Assign Permissions
        for role_name, role_data in PermissionsRegistry.ROLES.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(
                    name=role_name,
                    description=role_data.get('description', '')
                )
                db.session.add(role)
            
            # Clear existing permissions to avoid duplicates/stale data
            role.permissions = []
            
            # Assign Permissions
            if role_data.get('permissions') == '*':
                # Assign ALL permissions except excluded
                exclude = set(role_data.get('exclude', []))
                for p in all_perms:
                    if p.code not in exclude:
                        role.permissions.append(p)
            else:
                # Assign specific permissions (if list provided)
                # Note: Currently PermissionsRegistry.ROLES uses '*' mostly, 
                # but if there were lists, we'd handle them here.
                target_perms = set(role_data.get('permissions', []))
                for p in all_perms:
                    if p.code in target_perms:
                        role.permissions.append(p)
            
            # Handle special_access if needed (though usually mapped to permissions)
            # The current system seems to rely on 'permissions' relationship.
            
            db.session.add(role)
        
        db.session.commit()
        print("✅ Roles & Permissions assigned.")

if __name__ == "__main__":
    seed_permissions()
