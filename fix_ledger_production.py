import os
import sys
from decimal import Decimal
from sqlalchemy import text

# Add the current directory to sys.path to ensure imports work
sys.path.append(os.getcwd())

try:
    from app import app, db
    from models import (
        GLBatch, GLEntry, 
        Sale, Payment, PaymentSplit, SaleReturn, Invoice, 
        ServiceRequest, Expense, PreOrder, OnlinePreOrder,
        _sale_gl_batch_upsert,
        _payment_gl_batch_upsert,
        _payment_split_gl_batch_upsert,
        _sale_return_gl_batch_upsert,
        _invoice_gl_batch_upsert,
        _service_gl_batch_upsert,
        _expense_gl_batch_upsert,
        _preorder_gl_batch_upsert,
        _online_preorder_gl_batch_upsert
    )
except ImportError as e:
    print(f"Error importing app modules: {e}")
    print("Please make sure you are running this script from the project root directory.")
    sys.exit(1)

# Mapping of Source Type to (Model Class, Handler Function)
HANDLER_MAP = {
    'SALE': (Sale, _sale_gl_batch_upsert),
    'PAYMENT': (Payment, _payment_gl_batch_upsert),
    'PAYMENT_SPLIT': (PaymentSplit, _payment_split_gl_batch_upsert),
    'SALE_RETURN': (SaleReturn, _sale_return_gl_batch_upsert),
    'INVOICE': (Invoice, _invoice_gl_batch_upsert),
    'SERVICE': (ServiceRequest, _service_gl_batch_upsert),
    'EXPENSE': (Expense, _expense_gl_batch_upsert),
    'PREORDER': (PreOrder, _preorder_gl_batch_upsert),
    'ONLINE_PREORDER': (OnlinePreOrder, _online_preorder_gl_batch_upsert),
}

def fix_ledger():
    print("===================================================")
    print("   Garage Manager - Ledger Repair Tool (Production)")
    print("===================================================")
    
    with app.app_context():
        # 1. Ensure Critical Accounts Exist (Just in case implicit creation fails)
        ensure_accounts(db.session.connection())
        db.session.commit()

        # 2. Scan and Fix Entities
        total_fixed = 0
        total_scanned = 0
        
        for source_type, (model_cls, handler_func) in HANDLER_MAP.items():
            print(f"\nProcessing {source_type}...")
            items = model_cls.query.all()
            total_scanned += len(items)
            fixed_count = 0
            
            for item in items:
                should_regenerate = False
                
                # Check 1: Does GLBatch exist?
                batch = GLBatch.query.filter_by(source_type=source_type, source_id=item.id).first()
                
                if not batch:
                    # Missing batch -> Regenerate
                    should_regenerate = True
                    # print(f"  - Missing Batch for {source_type} #{item.id}")
                else:
                    # Check 2: Does it have entries?
                    entries = GLEntry.query.filter_by(batch_id=batch.id).all()
                    if not entries:
                        # Empty batch -> Regenerate
                        should_regenerate = True
                        # print(f"  - Empty Batch for {source_type} #{item.id}")
                    else:
                        # Check 3: Is it balanced?
                        total_debit = sum(Decimal(str(e.debit or 0)) for e in entries)
                        total_credit = sum(Decimal(str(e.credit or 0)) for e in entries)
                        if abs(total_debit - total_credit) > Decimal('0.05'):
                            # Unbalanced -> Regenerate
                            should_regenerate = True
                            print(f"  - Unbalanced Batch #{batch.id} for {source_type} #{item.id} (Diff: {total_debit - total_credit})")

                if should_regenerate:
                    try:
                        # Clean up existing bad batch if any
                        if batch:
                            db.session.delete(batch)
                            db.session.commit() # Commit delete first
                        
                        # Regenerate
                        conn = db.session.connection()
                        handler_func(None, conn, item)
                        db.session.commit()
                        fixed_count += 1
                    except Exception as e:
                        db.session.rollback()
                        print(f"  !!! Failed to regenerate {source_type} #{item.id}: {e}")
            
            if fixed_count > 0:
                print(f"  -> Fixed {fixed_count} items.")
                total_fixed += fixed_count
            else:
                print("  -> All clean.")

        print("\n===================================================")
        print(f"Repair Complete.")
        print(f"Total Entities Scanned: {total_scanned}")
        print(f"Total Batches Fixed/Regenerated: {total_fixed}")
        print("===================================================")

def ensure_accounts(connection):
    """Explicitly create the new accounts if they are missing, using raw SQL to be safe."""
    new_accounts = [
        ("4050_SALES_DISCOUNT", "Sales Discount", "EXPENSE"),
        ("4200_SHIPPING_INCOME", "Shipping Income", "REVENUE")
    ]
    
    for code, name, acct_type in new_accounts:
        try:
            # Check existence
            result = connection.execute(
                text("SELECT id FROM accounts WHERE code = :code"),
                {"code": code}
            ).fetchone()
            
            if not result:
                print(f"Creating missing account: {code} - {name}")
                connection.execute(
                    text("""
                        INSERT INTO accounts (code, name, account_type, is_active, created_at, updated_at)
                        VALUES (:code, :name, :type, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """),
                    {"code": code, "name": name, "type": acct_type}
                )
        except Exception as e:
            print(f"Warning: Could not check/create account {code}: {e}")

if __name__ == "__main__":
    fix_ledger()
