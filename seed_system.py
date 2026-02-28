
import sys
import os
import logging
from datetime import datetime, timezone
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.getcwd())

from extensions import db
from models import (
    User, Role, Permission, SystemSettings, Currency, Warehouse, Account,
    ProductCategory, ExpenseType, AccountType, ExchangeRate
)
from permissions_config.permissions import PermissionsRegistry

# Setup logger
logger = logging.getLogger("seed_system")
logging.basicConfig(level=logging.INFO)

def seed_system_settings():
    """Initialize default system settings"""
    logger.info("🔧 Seeding System Settings...")
    defaults = {
        'system_name': ('نظام الحازم', 'اسم النظام'),
        'company_name': ('شركة الحازم للأنظمة الذكية', 'اسم الشركة'),
        'login_title': ('مرحباً بك', 'عنوان صفحة الدخول'),
        'login_subtitle': ('سجل دخولك للمتابعة', 'وصف صفحة الدخول'),
        'footer_text': ('جميع الحقوق محفوظة © 2026', 'نص التذييل'),
        'primary_color': ('#007bff', 'اللون الأساسي'),
        'secondary_color': ('#1f2937', 'اللون الثانوي'),
        'sidebar_bg': ('#111827', 'لون القائمة الجانبية'),
        'sidebar_text': ('#f9fafb', 'لون نص القائمة'),
        'currency_base': ('ILS', 'العملة الأساسية'),
        'tax_rate': ('16', 'نسبة الضريبة الافتراضية'),
        'online_fx_enabled': ('true', 'تفعيل تحديث أسعار العملات تلقائياً'),
        'developer_name': ('Eng. Ahmad Ghannam', 'اسم المطور'),
        'developer_email': ('rafideen.ahmadghannam@gmail.com', 'ايميل المطور'),
    }

    for key, (val, desc) in defaults.items():
        if not SystemSettings.query.filter_by(key=key).first():
            SystemSettings.set_setting(key, val, description=desc, commit=False)
    
    db.session.commit()

def seed_currencies():
    """Initialize default currencies"""
    logger.info("💰 Seeding Currencies...")
    currencies = [
        ('ILS', 'الشيقل الإسرائيلي', '₪', 2, True),
        ('USD', 'الدولار الأمريكي', '$', 2, True),
        ('JOD', 'الدينار الأردني', 'JD', 3, True),
        ('EUR', 'اليورو', '€', 2, True),
        ('AED', 'الدرهم الإماراتي', 'د.إ', 2, True),
    ]

    for code, name, symbol, decimals, active in currencies:
        if not Currency.query.filter_by(code=code).first():
            cur = Currency(code=code, name=name, symbol=symbol, decimals=decimals, is_active=active)
            db.session.add(cur)
    
    db.session.commit()
    
    # Seed default exchange rates (Approximate)
    if not ExchangeRate.query.first():
         logger.info("💱 Seeding Initial Exchange Rates...")
         # USD Base
         db.session.add(ExchangeRate(base_code='USD', quote_code='ILS', rate=3.75))
         db.session.add(ExchangeRate(base_code='USD', quote_code='JOD', rate=0.708))
         db.session.add(ExchangeRate(base_code='USD', quote_code='AED', rate=3.67))
         
         # ILS Base
         db.session.add(ExchangeRate(base_code='ILS', quote_code='USD', rate=1/3.75))
         db.session.add(ExchangeRate(base_code='ILS', quote_code='JOD', rate=1/5.29))
         
         db.session.commit()

def seed_warehouses():
    """Initialize main warehouse"""
    logger.info("🏭 Seeding Warehouses...")
    if not Warehouse.query.first():
        wh = Warehouse(
            name="المستودع الرئيسي",
            location="المقر الرئيسي",
            is_active=True,
            warehouse_type="MAIN",
            online_is_default=True
        )
        db.session.add(wh)
        db.session.commit()

def seed_chart_of_accounts():
    """Initialize Chart of Accounts"""
    logger.info("📊 Seeding Chart of Accounts...")
    
    # Basic COA Structure
    accounts = [
        # Assets (1xxx)
        (1000, 'النقدية في الصندوق', AccountType.ASSET, 'ILS', None),
        (1010, 'البنك - شيقل', AccountType.ASSET, 'ILS', None),
        (1020, 'البنك - دولار', AccountType.ASSET, 'USD', None),
        (1100, 'الذمم المدينة (العملاء)', AccountType.ASSET, 'ILS', None),
        (1200, 'المخزون', AccountType.ASSET, 'ILS', None),
        (1300, 'الأصول الثابتة', AccountType.ASSET, 'ILS', None),
        
        # Liabilities (2xxx)
        (2000, 'الذمم الدائنة (الموردين)', AccountType.LIABILITY, 'ILS', None),
        (2100, 'ضريبة القيمة المضافة مستحقة الدفع', AccountType.LIABILITY, 'ILS', None),
        (2200, 'قروض قصيرة الأجل', AccountType.LIABILITY, 'ILS', None),
        
        # Equity (3xxx)
        (3000, 'رأس المال', AccountType.EQUITY, 'ILS', None),
        (3100, 'الأرباح المحتجزة', AccountType.EQUITY, 'ILS', None),
        (3200, 'جاري الشركاء', AccountType.EQUITY, 'ILS', None),
        
        # Revenue (4xxx)
        (4000, 'إيرادات المبيعات', AccountType.REVENUE, 'ILS', None),
        (4100, 'إيرادات الخدمات', AccountType.REVENUE, 'ILS', None),
        (4200, 'إيرادات أخرى', AccountType.REVENUE, 'ILS', None),
        
        # Expenses (5xxx)
        (5000, 'تكلفة البضاعة المباعة', AccountType.EXPENSE, 'ILS', None),
        (5100, 'رواتب وأجور', AccountType.EXPENSE, 'ILS', None),
        (5200, 'إيجار', AccountType.EXPENSE, 'ILS', None),
        (5300, 'كهرباء وماء', AccountType.EXPENSE, 'ILS', None),
        (5400, 'مصاريف تسويق', AccountType.EXPENSE, 'ILS', None),
        (5500, 'مصاريف إدارية وعمومية', AccountType.EXPENSE, 'ILS', None),
        (5600, 'مصاريف صيانة', AccountType.EXPENSE, 'ILS', None),
    ]

    for code, name, type_, currency, parent_id in accounts:
        exists = Account.query.filter_by(code=str(code)).first()
        if not exists:
            # Handle type conversion if it's an Enum
            type_val = getattr(type_, "value", type_)
            
            acc = Account(
                code=str(code),
                name=name,
                type=type_val,
                is_active=True
            )
            db.session.add(acc)
    
    db.session.commit()

def seed_categories():
    """Initialize Product and Expense Categories"""
    logger.info("🏷️ Seeding Categories...")
    
    # Product Categories
    prod_cats = ['قطع غيار', 'زيوت', 'إطارات', 'بطاريات', 'اكسسوارات', 'خدمات']
    for name in prod_cats:
        if not ProductCategory.query.filter_by(name=name).first():
            db.session.add(ProductCategory(name=name, description=f"تصنيف {name}"))
            
    # Expense Types
    exp_types = ['رواتب', 'إيجار', 'كهرباء', 'مياه', 'انترنت', 'ضيافة', 'نثريات', 'صيانة معدات', 'تسويق']
    for name in exp_types:
        if not ExpenseType.query.filter_by(name=name).first():
            db.session.add(ExpenseType(name=name, description=f"مصروف {name}"))
            
    db.session.commit()

def seed_roles_and_permissions():
    """Initialize Roles and Permissions (from update_roles.py logic)"""
    logger.info("🛡️ Seeding Roles and Permissions...")
    
    # 1. Ensure permissions exist
    all_perms_map = {}
    for category, perms in PermissionsRegistry.PERMISSIONS.items():
        for code, info in perms.items():
            perm = Permission.query.filter_by(code=code).first()
            if not perm:
                perm = Permission(
                    code=code,
                    name=info['name_ar'],
                    name_ar=info['name_ar'],
                    description=info['description'],
                    module=info['module'],
                    is_protected=info.get('is_protected', False)
                )
                db.session.add(perm)
            all_perms_map[code] = perm
    db.session.commit()
    
    # Reload permissions
    all_db_perms = Permission.query.all()
    perm_lookup = {p.code: p for p in all_db_perms}
    
    # 2. Define Roles
    owner_perms = list(perm_lookup.values())

    excluded_for_admin = {
        'access_owner_dashboard', 'manage_tenants', 'manage_system_config', 
        'manage_any_user_permissions', 'manage_ai', 'access_ai_assistant', 'train_ai',
        'backup_database', 'restore_database', 'hard_delete', 'manage_saas', 
        'manage_mobile_app', 'manage_system_health'
    }
    super_admin_perms = [p for p in all_db_perms if p.code not in excluded_for_admin]

    accountant_codes = {
        'access_dashboard',
        'manage_accounting_docs', 'validate_accounting', 'manage_ledger',
        'manage_payments', 'manage_expenses', 'view_reports', 'manage_reports',
        'manage_exchange', 'manage_currencies', 'manage_bank', 'view_bank', 'add_bank_transaction',
        'manage_sales', 'archive_sale', 'view_sales',
        'view_customers', 'manage_customers',
        'manage_vendors', 'add_supplier', 'add_partner',
        'view_inventory', 'view_warehouses',
        'view_shop', 'view_preorders', 'view_own_orders', 'view_own_account'
    }
    accountant_perms = [perm_lookup[c] for c in accountant_codes if c in perm_lookup]

    service_advisor_codes = {
        'access_dashboard',
        'manage_service', 'view_service',
        'add_customer', 'view_customers', 'manage_customers',
        'view_inventory', 'view_parts', 'view_warehouses',
        'view_sales',
        'view_barcode',
        'view_notes', 'manage_notes',
        'view_own_orders', 'view_own_account'
    }
    service_advisor_perms = [perm_lookup[c] for c in service_advisor_codes if c in perm_lookup]

    mechanic_codes = {
        'access_dashboard',
        'view_service',
        'view_parts', 'view_inventory',
        'view_notes',
        'view_own_orders', 'view_own_account'
    }
    mechanic_perms = [perm_lookup[c] for c in mechanic_codes if c in perm_lookup]

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
    
    sales_rep_codes = {
        'access_dashboard',
        'manage_sales', 'view_sales',
        'add_customer', 'view_customers',
        'view_inventory', 'view_shop', 'browse_products', 'place_online_order',
        'view_preorders', 'add_preorder',
        'view_own_orders', 'view_own_account'
    }
    sales_rep_perms = [perm_lookup[c] for c in sales_rep_codes if c in perm_lookup]

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
            role = Role(name=role_name, description=description)
            db.session.add(role)
        else:
            role.description = description
        role.permissions = perms
        
    db.session.commit()

def seed_users():
    """Initialize Admin User if no users exist"""
    logger.info("👤 Seeding Users...")
    
    # Ensure roles exist first
    seed_roles_and_permissions()
    
    # Check if any user exists
    if User.query.first():
        return

    # Create Owner/Admin
    admin_role = Role.query.filter_by(name='Owner').first()
    if not admin_role:
        admin_role = Role.query.filter_by(name='Super Admin').first()
        
    user = User(
        username='admin',
        email='admin@alhazem.com',
        role=admin_role,
        is_active=True,
        is_system_account=True
    )
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    logger.info(f"✅ Created default admin user: admin / admin123")

def seed_all():
    """Run all seeders"""
    try:
        seed_system_settings()
        seed_currencies()
        seed_warehouses()
        seed_chart_of_accounts()
        seed_categories()
        seed_users()
        logger.info("✨ System initialization completed successfully!")
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        db.session.rollback()
        raise

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_all()
