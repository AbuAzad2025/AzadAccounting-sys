
import sys
import os
from app import create_app
from extensions import db
from models import Role, Permission
from permissions_config.permissions import PermissionsRegistry

def update_roles():
    app = create_app()
    with app.app_context():
        print("🔧 Updating Roles and Permissions...")

        # 1. Get all available permissions from Registry
        all_perms_map = {} # code -> Permission Object
        
        # Ensure all permissions exist in DB
        for category, perms in PermissionsRegistry.PERMISSIONS.items():
            for code, info in perms.items():
                perm = Permission.query.filter_by(code=code).first()
                if not perm:
                    print(f"  + Creating missing permission: {code}")
                    perm = Permission(
                        code=code,
                        name=info['name_ar'], # Using Arabic name as primary name for consistency
                        name_ar=info['name_ar'],
                        description=info['description'],
                        module=info['module'],
                        is_protected=info.get('is_protected', False)
                    )
                    db.session.add(perm)
                all_perms_map[code] = perm
        
        db.session.commit()
        
        # Reload permissions to get IDs
        all_db_perms = Permission.query.all()
        perm_lookup = {p.code: p for p in all_db_perms}

        # 2. Define Roles and their Permission Codes
        
        # --- OWNER (المالك) ---
        # Gets EVERYTHING
        owner_perms = list(perm_lookup.values())

        # --- SUPER ADMIN (مدير النظام) ---
        # Everything EXCEPT Owner Dashboard, Tenant Mgmt, AI, etc.
        excluded_for_admin = {
            'access_owner_dashboard', 'manage_tenants', 'manage_system_config', 
            'manage_any_user_permissions', 'manage_ai', 'access_ai_assistant', 'train_ai',
            'backup_database', 'restore_database', 'hard_delete', 'manage_saas', 
            'manage_mobile_app', 'manage_system_health'
        }
        super_admin_perms = [p for p in all_db_perms if p.code not in excluded_for_admin]

        # --- ACCOUNTANT (محاسب) ---
        accountant_codes = {
            'access_dashboard',
            'manage_accounting_docs', 'validate_accounting', 'manage_ledger',
            'manage_payments', 'manage_expenses', 'view_reports', 'manage_reports',
            'manage_exchange', 'manage_currencies', 'manage_bank', 'view_bank', 'add_bank_transaction',
            'manage_sales', 'archive_sale', 'view_sales', # Needs to see sales for invoicing
            'view_customers', 'manage_customers', # Needs to manage customer accounts/balances
            'manage_vendors', 'add_supplier', 'add_partner', # Payables
            'view_inventory', 'view_warehouses', # Asset valuation
            'view_shop', 'view_preorders', 'view_own_orders', 'view_own_account'
        }
        accountant_perms = [perm_lookup[c] for c in accountant_codes if c in perm_lookup]

        # --- SERVICE ADVISOR (مستشار صيانة) ---
        service_advisor_codes = {
            'access_dashboard',
            'manage_service', 'view_service',
            'add_customer', 'view_customers', 'manage_customers',
            'view_inventory', 'view_parts', 'view_warehouses',
            'view_sales', # To see history
            'view_barcode',
            'view_notes', 'manage_notes',
            'view_own_orders', 'view_own_account'
        }
        service_advisor_perms = [perm_lookup[c] for c in service_advisor_codes if c in perm_lookup]

        # --- MECHANIC (فني صيانة) ---
        mechanic_codes = {
            'access_dashboard',
            'view_service', # Needs to see tasks. Note: "manage_service" might be too much if it allows deleting.
                            # Ideally we need "update_service_status", but for now view_service often implies working on it.
            'view_parts', 'view_inventory',
            'view_notes',
            'view_own_orders', 'view_own_account'
        }
        mechanic_perms = [perm_lookup[c] for c in mechanic_codes if c in perm_lookup]

        # --- STOREKEEPER (أمين مستودع) ---
        storekeeper_codes = {
            'access_dashboard',
            'manage_warehouses', 'view_warehouses',
            'manage_inventory', 'view_inventory',
            'warehouse_transfer',
            'view_parts',
            'manage_vendors', 'add_supplier',
            'manage_shipments',
            'view_barcode', 'manage_barcode',
            'view_own_orders', 'view_own_account'
        }
        storekeeper_perms = [perm_lookup[c] for c in storekeeper_codes if c in perm_lookup]
        
        # --- SALES REP (مندوب مبيعات) ---
        sales_rep_codes = {
            'access_dashboard',
            'manage_sales', 'view_sales',
            'add_customer', 'view_customers',
            'view_inventory', 'view_shop', 'browse_products', 'place_online_order',
            'view_preorders', 'add_preorder',
            'view_own_orders', 'view_own_account'
        }
        sales_rep_perms = [perm_lookup[c] for c in sales_rep_codes if c in perm_lookup]


        # 3. Apply to Roles
        roles_def = [
            ('Owner', 'المالك', owner_perms),
            ('Super Admin', 'مدير النظام', super_admin_perms),
            ('Accountant', 'محاسب', accountant_perms),
            ('Service Advisor', 'مستشار صيانة', service_advisor_perms),
            ('Mechanic', 'فني صيانة', mechanic_perms),
            ('Storekeeper', 'أمين مستودع', storekeeper_perms),
            ('Sales Representative', 'مندوب مبيعات', sales_rep_perms),
        ]

        for role_name, description, perms in roles_def:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                print(f"  + Creating Role: {role_name}")
                role = Role(name=role_name, description=description)
                db.session.add(role)
            else:
                print(f"  * Updating Role: {role_name}")
                role.description = description
            
            # Update permissions
            role.permissions = perms
            
        db.session.commit()
        print("\n✨ Roles and Permissions updated successfully!")

if __name__ == "__main__":
    update_roles()
