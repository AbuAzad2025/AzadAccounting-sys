
import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import GL_ACCOUNTS

def seed_accounts():
    app = create_app()
    with app.app_context():
        print("🌱 Seeding Chart of Accounts...")
        
        # Standard Account Map (Copied from models.py _ensure_account_exists)
        account_name_map = {
            "1000_CASH": "الصندوق",
            "1010_BANK": "البنك",
            "1020_CARD_CLEARING": "البطاقات",
            "1100_AR": "ذمم العملاء",
            "1150_CHQ_REC": "شيكات تحت التحصيل",
            "1205_INV_EXCHANGE": "مخزون توريد تبادل",
            "1300_INVENTORY": "المخزون",
            "1300_INV_RSV": "احتياطي مخزون",
            "1599_ACC_DEP": "مخصص إهلاك متراكم",
            "2000_AP": "ذمم الموردين والخصوم",
            "2100_VAT_PAYABLE": "ضريبة القيمة المضافة",
            "2200_INCOME_TAX_PAYABLE": "ضريبة الدخل المستحقة",
            "2200_PARTNER_CLEARING": "تسوية الشركاء",
            "2150_CHQ_PAY": "شيكات تحت الدفع",
            "2150_PAYROLL_CLR": "قيد الرواتب",
            "2300_ADV_PAY": "إيرادات مقدمة",
            "3000_EQUITY": "حقوق الملكية",
            "3100_OWNER_CURRENT": "حساب المالك الجاري",
            "3200_CURRENT_EARNINGS": "أرباح محتجزة جارية",
            "4000_SALES": "المبيعات",
            "4050_SALES_DISCOUNT": "خصم المبيعات",
            "4100_SERVICE_REVENUE": "إيراد الخدمات",
            "4200_SHIPPING_INCOME": "إيراد الشحن",
            "5000_EXPENSES": "مصروفات",
            "5100_COGS": "تكلفة البضاعة المباعة",
            "5100_PURCHASES": "المشتريات",
            "5100_SUPPLIER_EXPENSES": "مصروفات موردين",
            "5100_SUPPLIER_EXPENS": "مصروفات موردين",
            "5105_COGS_EXCHANGE": "تكلفة توريد تبادل",
            "6100_SALARIES": "الرواتب",
            "6500_FUEL": "وقود",
            "6600_OFFICE": "مستلزمات مكتب",
            "6200_INCOME_TAX_EXPENSE": "ضريبة الدخل (مصروف)",
            "6800_DEPRECIATION": "إهلاك",
            "6960_HOME_EXPENSE": "مصروفات منزلية",
            # Additional Standard Accounts
            "6110_EMPLOYEE_ADVANCES": "سلف موظفين",
            "6200_RENT": "إيجار",
            "6300_UTILITIES": "مرافق",
            "6400_MAINTENANCE": "صيانة",
            "6700_INSURANCE": "تأمين",
            "6800_GOV_FEES": "رسوم حكومية",
            "6900_TRAVEL": "سفر",
            "6910_TRAINING": "تدريب",
            "6920_MARKETING": "تسويق",
            "6930_SOFTWARE": "برمجيات",
            "6940_BANK_FEES": "رسوم بنكية",
            "6950_HOSPITALITY": "ضيافة",
            "6970_OWNER_CURRENT": "مصاريف المالك",
            "6980_ENTERTAINMENT": "ترفيه",
            "5200_PART_EXP": "مصروفات شركاء",
            "5510_SHIP_INSURANCE": "تأمين شحن",
            "5520_SHIP_CUSTOMS": "جمارك شحن",
            "5530_SHIP_IMPORT_TAX": "ضريبة استيراد شحن",
            "5540_SHIP_FREIGHT": "نولون شحن",
            "5550_SHIP_CLEARANCE": "تخليص شحن",
            "5560_SHIP_HANDLING": "مناولة شحن",
            "5570_SHIP_PORT_FEES": "رسوم ميناء شحن",
            "5580_SHIP_STORAGE": "تخزين شحن",
        }

        # Merge with GL_ACCOUNTS values just in case
        all_codes = set(account_name_map.keys())
        for k, v in GL_ACCOUNTS.items():
            all_codes.add(v)

        # Helper to determine type
        def get_type(code):
            if code.startswith('1'): return 'ASSET'
            if code.startswith('2'): return 'LIABILITY'
            if code.startswith('3'): return 'EQUITY'
            if code.startswith('4'): return 'REVENUE'
            if code.startswith('5'): return 'EXPENSE'
            if code.startswith('6'): return 'EXPENSE'
            return 'ASSET'

        conn = db.session.connection()
        added = 0
        
        for code in all_codes:
            name = account_name_map.get(code, code.replace("_", " ").title())
            type_ = get_type(code)
            
            # Check existence using raw SQL for speed/simplicity
            exists = conn.execute(text("SELECT 1 FROM accounts WHERE code = :c"), {"c": code}).scalar()
            
            if not exists:
                conn.execute(text("""
                    INSERT INTO accounts (code, name, type, is_active, created_at, updated_at)
                    VALUES (:c, :n, :t, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """), {"c": code, "n": name, "t": type_})
                added += 1
        
        db.session.commit()
        print(f"✅ Seeded {added} accounts.")

if __name__ == "__main__":
    seed_accounts()
