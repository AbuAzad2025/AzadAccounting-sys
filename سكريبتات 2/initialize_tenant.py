
import sys
import os
import datetime
from decimal import Decimal

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import SystemSettings, Warehouse, GLBatch, GLEntry, GL_ACCOUNTS, User, Role

def get_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input.strip() or default
    else:
        return input(f"{prompt}: ").strip()

def setup_wizard():
    print("="*50)
    print("🚀  Garage Manager - New Tenant Setup Wizard")
    print("="*50)
    print("This script will help you configure the basic settings for a new tenant.")
    print("Ensure the database is clean (run clean_for_new_tenant.py first if needed).")
    print("-" * 50)

    app = create_app()
    with app.app_context():
        # --- Step 1: Company Information ---
        print("\n📝  Step 1: Company Information")
        company_name = get_input("Company Name", "My Garage")
        company_phone = get_input("Company Phone", "")
        company_address = get_input("Company Address", "")
        tax_rate_input = get_input("VAT Tax Rate % (e.g. 16 for 16%)", "16")
        
        try:
            tax_rate = float(tax_rate_input)
        except ValueError:
            tax_rate = 16.0
            print("⚠️  Invalid tax rate, defaulting to 16%")

        print("   Saving settings...")
        SystemSettings.set_setting('company_name', company_name, is_public=True)
        SystemSettings.set_setting('company_phone', company_phone, is_public=True)
        SystemSettings.set_setting('company_address', company_address, is_public=True)
        SystemSettings.set_setting('tax_rate', tax_rate, data_type='number', is_public=True)
        SystemSettings.set_setting('currency', 'ILS', is_public=True) # Defaulting to ILS for now
        
        print("✅  Company settings saved.")

        # --- Step 2: Warehouses ---
        print("\nnb📦  Step 2: Warehouses")
        warehouse_count = Warehouse.query.count()
        if warehouse_count == 0:
            print("   No warehouses found. Creating 'Main Warehouse'...")
            main_wh = Warehouse(
                name="Main Warehouse",
                location="Main",
                is_active=True
            )
            db.session.add(main_wh)
            db.session.commit()
            print("✅  'Main Warehouse' created.")
        else:
            print(f"✅  Found {warehouse_count} existing warehouses. Skipping creation.")

        # --- Step 3: Opening Balance ---
        print("\n💰  Step 3: Opening Capital (Optional)")
        set_opening = get_input("Do you want to record opening cash capital? (y/n)", "n")
        
        if set_opening.lower() == 'y':
            amount_str = get_input("Enter Opening Cash Amount (ILS)", "0")
            try:
                amount = float(amount_str)
                if amount > 0:
                    # Create GL Batch
                    print("   Creating Opening Balance Journal Entry...")
                    
                    # Accounts
                    cash_acct = GL_ACCOUNTS.get("CASH", "1000_CASH")
                    equity_acct = "3000_EQUITY" # Assuming this exists from seed_accounts
                    
                    # Check accounts exist
                    # (We assume seed_accounts.py was run, but let's be safe)
                    
                    entries = [
                        (cash_acct, amount, 0),      # Debit Cash
                        (equity_acct, 0, amount)     # Credit Equity
                    ]
                    
                    # Helper function from models might be complex to import directly if not standard
                    # So we'll do it manually using the model
                    
                    batch = GLBatch(
                        source_type="MANUAL",
                        source_id=0, # System
                        purpose="OPENING_BALANCE",
                        currency="ILS",
                        memo=f"Opening Capital - {datetime.date.today()}",
                        status="POSTED",
                        posted_at=datetime.datetime.now(datetime.timezone.utc)
                    )
                    db.session.add(batch)
                    db.session.flush()
                    
                    for acct_code, dr, cr in entries:
                        entry = GLEntry(
                            batch_id=batch.id,
                            account=acct_code,
                            debit=Decimal(str(dr)),
                            credit=Decimal(str(cr)),
                            currency="ILS"
                        )
                        db.session.add(entry)
                    
                    db.session.commit()
                    print(f"✅  Opening balance of {amount} ILS recorded.")
                else:
                    print("   Amount is 0, skipping.")
            except Exception as e:
                print(f"❌  Error recording opening balance: {e}")
                db.session.rollback()
        else:
            print("   Skipping opening balance.")

        # --- Step 4: Admin User Check ---
        print("\n👤  Step 4: Admin User")
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"ℹ️   Admin user 'admin' exists.")
            reset_pw = get_input("Do you want to reset 'admin' password? (y/n)", "n")
            if reset_pw.lower() == 'y':
                new_pw = get_input("Enter new password", "admin123")
                admin.set_password(new_pw)
                db.session.commit()
                print("✅  Password updated.")
        else:
            print("⚠️   User 'admin' not found! You should ensure there is a super user.")

        print("\n" + "="*50)
        print("🎉  Setup Complete!")
        print("="*50)

if __name__ == "__main__":
    setup_wizard()
