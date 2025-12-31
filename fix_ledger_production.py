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
        # 1. Ensure Critical Accounts Exist (Using safer method with rollback)
        try:
             ensure_accounts(db.session.connection())
             db.session.commit()
        except Exception as e:
             print(f"Error creating accounts: {e}")
             db.session.rollback()

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
                    should_regenerate = True
                else:
                    # Check 2: Does it have entries?
                    entries = GLEntry.query.filter_by(batch_id=batch.id).all()
                    if not entries:
                        should_regenerate = True
                    else:
                        # Check 3: Is it balanced?
                        total_debit = sum(Decimal(str(e.debit or 0)) for e in entries)
                        total_credit = sum(Decimal(str(e.credit or 0)) for e in entries)
                        if abs(total_debit - total_credit) > Decimal('0.05'):
                            should_regenerate = True
                            print(f"  - Unbalanced Batch #{batch.id} for {source_type} #{item.id} (Diff: {total_debit - total_credit})")

                if should_regenerate:
                    try:
                        # Ensure we have a fresh transaction for each item
                        # Delete existing bad batch if any
                        if batch:
                            db.session.execute(text("DELETE FROM gl_entries WHERE batch_id = :bid"), {"bid": batch.id})
                            db.session.execute(text("DELETE FROM gl_batches WHERE id = :bid"), {"bid": batch.id})
                            db.session.commit()
                        
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
                # Note: 'type' column is used in some schemas instead of 'account_type'
                # We try 'type' first using a savepoint to prevent transaction abort
                created = False
                try:
                    with connection.begin_nested():
                        # We must quote "type" because it's a reserved keyword in some contexts
                        connection.execute(
                            text("""
                                INSERT INTO accounts (code, name, "type", is_active, created_at, updated_at)
                                VALUES (:code, :name, :type, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            """),
                            {"code": code, "name": name, "type": acct_type}
                        )
                    created = True
                except Exception as e_type:
                     # Fallback to account_type if type fails
                     print(f"Failed to create with 'type' column: {e_type}")
                     print(f"Retrying with account_type for {code}...")
                     try:
                        with connection.begin_nested():
                            connection.execute(
                                text("""
                                    INSERT INTO accounts (code, name, account_type, is_active, created_at, updated_at)
                                    VALUES (:code, :name, :type, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                """),
                                {"code": code, "name": name, "type": acct_type}
                            )
                        created = True
                     except Exception as e_final:
                        print(f"Failed to create account {code} with account_type: {e_final}")
                
                if created:
                    print(f"Successfully created account {code}")

        except Exception as e:
            print(f"Warning: Could not check/create account {code}: {e}")
            # Do not re-raise, let the script continue

if __name__ == "__main__":
    fix_ledger()
