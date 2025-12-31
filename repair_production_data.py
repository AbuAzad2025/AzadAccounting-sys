
import os
import sys
from flask import Flask
from models import db, Customer, GLBatch, GLEntry
from sqlalchemy import func
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    # Use DATABASE_URL from environment
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("⚠️ DATABASE_URL not found in environment. Using default local.")
        database_url = 'postgresql://postgres:123@localhost:5432/garage_db'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def fix_customer_balances(app):
    print("\n--- 1. Fixing Customer Balances ---")
    with app.app_context():
        customers = Customer.query.all()
        updated_count = 0
        
        for customer in customers:
            # Ledger Balance (Debit - Credit)
            # Positive Ledger Balance means "Asset" (They owe us)
            ledger_balance = db.session.query(func.sum(GLEntry.debit - GLEntry.credit)).join(GLBatch).filter(
                GLBatch.entity_type == 'CUSTOMER',
                GLBatch.entity_id == customer.id,
                GLBatch.status == 'POSTED',
                GLEntry.account == '1100_AR'
            ).scalar() or 0
            
            ledger_balance = float(ledger_balance)
            
            # Current Balance Convention: Negative = They owe us (Debit)
            target_balance = -ledger_balance
            
            current_balance = float(customer.current_balance or 0)
            
            # Check for discrepancy
            if abs(current_balance - target_balance) > 0.1:
                print(f"Fixing {customer.name} (ID: {customer.id}): Cached={current_balance} -> Target={target_balance} (Ledger={ledger_balance})")
                customer.current_balance = target_balance
                updated_count += 1
        
        if updated_count > 0:
            print(f"Updating {updated_count} customers...")
            db.session.commit()
            print("✅ Customer balances updated.")
        else:
            print("✅ All customer balances match Ledger.")

def fix_broken_batches(app):
    print("\n--- 2. Fixing Broken Batches ---")
    with app.app_context():
        # Fix Batch 332 (Known issue)
        batch_332 = GLBatch.query.get(332)
        if batch_332:
            if batch_332.source_type != 'MANUAL' and not batch_332.source_id:
                print(f"Fixing Batch {batch_332.id}: {batch_332.memo}")
                batch_332.source_type = 'MANUAL'
                batch_332.source_id = None
                if batch_332.memo:
                    if "Fixed: Missing Expense" not in batch_332.memo:
                        batch_332.memo += " [Fixed: Missing Expense #54]"
                else:
                    batch_332.memo = "Fixed: Missing Expense #54"
                db.session.commit()
                print("✅ Batch 332 fixed.")
            else:
                print("✅ Batch 332 is already fixed or valid.")
        else:
            print("ℹ️ Batch 332 not found (might be deleted or different DB).")

def main():
    print("🚀 Starting Production Data Repair Script...")
    app = create_app()
    
    try:
        fix_customer_balances(app)
        fix_broken_batches(app)
        print("\n✅ Repair process completed successfully.")
    except Exception as e:
        print(f"\n❌ Error during repair: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
