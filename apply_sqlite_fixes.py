
from app import create_app, db
from models import Customer, GLBatch, GLEntry, Product, StockLevel
from decimal import Decimal
from datetime import datetime, timezone

# Data extracted from SQLite (Old Database)
DATA_TO_FIX = [
    {'name': 'اياد الغزاوي', 'opening_balance': -11200.0},
    {'name': 'فريد ابو اياد الطوري', 'opening_balance': 15000.0},
    {'name': 'محمد فارس', 'opening_balance': -155560.0},
    {'name': 'سامي كمال الطميزي', 'opening_balance': -1000.0}
]

# 3. Cached Balance Resets (Fixing Ghost Balances)
CACHED_BALANCE_RESETS = [
    {'id': 6, 'name': 'وليد قصراوي مضخات', 'balance': 0.0},
    {'id': 9, 'name': 'احمد ياسين طولكرم', 'balance': 0.0},
    {'id': 10, 'name': 'عارف القرناوي رهط', 'balance': 0.0},
    {'id': 11, 'name': 'سميح عموري طولكرم', 'balance': 0.0},
    {'id': 28, 'name': 'ادهم قطام', 'balance': 0.0},
    {'id': 32, 'name': 'مجهول', 'balance': 0.0},
    {'id': 30, 'name': 'طوب شاهين', 'balance': 0.0},
    {'id': 31, 'name': 'ونشات رام الله', 'balance': 0.0},
    {'id': 17, 'name': 'عدنان السلامين', 'balance': 0.0},
    {'id': 21, 'name': 'فيصل الجمل', 'balance': 0.0},
    {'id': 38, 'name': 'موسى الخيري', 'balance': 0.0},
    {'id': 5, 'name': 'يوسف ابو علي دورا', 'balance': -300.0},
    {'id': 1, 'name': 'عامر ابو شخيدم', 'balance': -20500.0}
]

def apply_fixes():
    app = create_app()
    with app.app_context():
        print("--- Applying SQLite Opening Balance Fixes ---")
        
        for item in DATA_TO_FIX:
            name = item['name']
            amount = Decimal(str(item['opening_balance']))
            
            customer = Customer.query.filter_by(name=name).first()
            if not customer:
                print(f"❌ Customer '{name}' not found in Postgres. Skipping.")
                continue
                
            print(f"Processing '{name}'...")
            
            # 1. Update Field
            old_val = customer.opening_balance
            customer.opening_balance = amount
            print(f"  - Updated field: {old_val} -> {amount}")
            
            # 2. Check/Create GL Batch
            # Using source_type='CUSTOMER', source_id=customer.id, purpose='OPENING_BALANCE'
            batch = GLBatch.query.filter(
                GLBatch.source_type == 'CUSTOMER',
                GLBatch.source_id == customer.id,
                GLBatch.purpose == 'OPENING_BALANCE'
            ).first()
            
            if batch:
                print(f"  - Found existing GLBatch {batch.id}. Updating...")
                batch.memo = 'رصيد افتتاحي (مصحح)'
                batch.status = 'POSTED' # Ensure posted
            else:
                print(f"  - Creating NEW GLBatch...")
                batch = GLBatch(
                    source_type='CUSTOMER',
                    source_id=customer.id,
                    entity_type='CUSTOMER',
                    entity_id=customer.id,
                    status='POSTED',
                    posted_at=datetime.now(timezone.utc),
                    memo='رصيد افتتاحي (منقول من النظام القديم)',
                    purpose='OPENING_BALANCE',
                    currency='ILS'
                )
                db.session.add(batch)
                db.session.flush() # To get batch.id
                
            # Prepare Entries
            # Clear existing entries
            GLEntry.query.filter_by(batch_id=batch.id).delete()
            
            entries = []
            abs_amount = abs(amount)
            
            if amount > 0:
                # Debit AR (1100), Credit Equity (3000)
                entries.append(GLEntry(
                    batch_id=batch.id,
                    account='1100_AR',
                    debit=abs_amount,
                    credit=0,
                    ref='رصيد افتتاحي'
                ))
                entries.append(GLEntry(
                    batch_id=batch.id,
                    account='3000_EQUITY', 
                    debit=0,
                    credit=abs_amount,
                    ref='رصيد افتتاحي'
                ))
            elif amount < 0:
                 # Debit Equity (3000), Credit AR (1100)
                entries.append(GLEntry(
                    batch_id=batch.id,
                    account='3000_EQUITY',
                    debit=abs_amount,
                    credit=0,
                    ref='رصيد افتتاحي'
                ))
                entries.append(GLEntry(
                    batch_id=batch.id,
                    account='1100_AR',
                    debit=0,
                    credit=abs_amount,
                    ref='رصيد افتتاحي'
                ))
            
            if abs_amount > 0:
                db.session.add_all(entries)
                print(f"  - Added {len(entries)} GL entries.")
            else:
                print(f"  - Amount is 0, no entries created.")
                
            # 3. Update Current Balance (Cached)
            db.session.commit()
            
            from sqlalchemy import func
            ledger_bal = db.session.query(func.sum(GLEntry.debit - GLEntry.credit)).join(GLBatch).filter(
                GLBatch.entity_type == 'CUSTOMER',
                GLBatch.entity_id == customer.id,
                GLBatch.status == 'POSTED',
                GLEntry.account == '1100_AR'
            ).scalar() or 0
            
            new_cached = -float(ledger_bal)
            customer.current_balance = new_cached
            print(f"  - Recalculated Cached Balance: {new_cached}")
            db.session.commit()
            
        # --- Inventory Fixes ---
        print("\n--- Applying Inventory Fixes ---")
        
        # 1. Missing Stock for 114 (Warehouse 1, Qty 3)
        s114 = StockLevel.query.filter_by(product_id=114, warehouse_id=1).first()
        if not s114:
            print("Adding missing Stock for Product 114 @ Warehouse 1 (Qty 3)...")
            s114 = StockLevel(product_id=114, warehouse_id=1, quantity=3.0)
            db.session.add(s114)
        else:
            print(f"Stock for Product 114 @ Warehouse 1 already exists (Qty: {s114.quantity}).")

        # 2. Ensure Product 112 (Duplicate) stock is merged into 111 if not present
        # Based on SQLite finding: Product 112 had 58 qty in Warehouse 2
        p111 = Product.query.filter_by(id=111).first()
        if p111 and p111.name == 'طرمبة المنيوم صغير':
            s111_w2 = StockLevel.query.filter_by(product_id=111, warehouse_id=2).first()
            if not s111_w2:
                 print("Adding merged Stock for Product 111 @ Warehouse 2 (Qty 58) from old Product 112...")
                 s111_w2 = StockLevel(product_id=111, warehouse_id=2, quantity=58.0)
                 db.session.add(s111_w2)
            else:
                 print(f"Stock for Product 111 @ Warehouse 2 checked (Qty: {s111_w2.quantity}).")
        
        db.session.commit()

        # --- Cached Balance Resets ---
        print("\n--- Applying Cached Balance Resets ---")
        for item in CACHED_BALANCE_RESETS:
            cust = Customer.query.get(item['id'])
            if cust:
                if cust.current_balance != item['balance']:
                    print(f"  - Resetting Cached Balance for {cust.name}: {cust.current_balance} -> {item['balance']}")
                    cust.current_balance = item['balance']
                else:
                    print(f"  - Cached Balance for {cust.name} is correct ({item['balance']}).")
        
        db.session.commit()
            
        print("\n✅ All fixes applied.")

if __name__ == "__main__":
    apply_fixes()
