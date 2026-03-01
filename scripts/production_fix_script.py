import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Add project root to sys.path
ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from sqlalchemy import func
from models import (
    ServiceRequest, Payment, GLBatch, GLEntry, GL_ACCOUNTS,
    StockLevel,
    run_service_gl_sync_after_commit, run_payment_gl_sync_after_commit
)

def fix_production_data():
    app = create_app()
    with app.app_context():
        print("\n=======================================================")
        print("          PRODUCTION DATA FIX SCRIPT           ")
        print("=======================================================")
        
        # ---------------------------------------------------------
        # 1. FIX MISSING GL FOR COMPLETED SERVICES
        # ---------------------------------------------------------
        print("\n--- 1. Fixing Completed Services without GL ---")
        services = ServiceRequest.query.filter(
            ServiceRequest.status.in_(['COMPLETED', 'DELIVERED'])
        ).all()
        
        fixed_services = 0
        for svc in services:
            # Check GL
            batch = GLBatch.query.filter(
                GLBatch.source_type == 'SERVICE',
                GLBatch.source_id == svc.id,
                GLBatch.status == 'POSTED'
            ).first()
            
            if not batch:
                print(f"   -> Fixing Service ID {svc.id} ({svc.service_number})...")
                try:
                    # Try automatic sync first
                    run_service_gl_sync_after_commit(svc.id)
                    db.session.commit()
                    
                    # Verify
                    if GLBatch.query.filter(GLBatch.source_type=='SERVICE', GLBatch.source_id==svc.id).first():
                        print("      ✅ Auto-Sync Success.")
                        fixed_services += 1
                        continue
                        
                    # If failed, create Manual
                    print("      ⚠️ Auto-Sync failed/skipped. Creating Manual Entry...")
                    batch = GLBatch(
                        source_type='SERVICE',
                        source_id=svc.id,
                        status='POSTED',
                        posted_at=svc.completed_at or datetime.now(),
                        entity_type='CUSTOMER',
                        entity_id=svc.customer_id,
                        memo=f"Service Revenue {svc.service_number}",
                        currency=svc.currency or 'ILS'
                    )
                    db.session.add(batch)
                    db.session.flush()
                    
                    amount = Decimal(str(svc.total_amount or 0))
                    
                    if amount <= 0:
                        print(f"      ⚠️ Service {svc.id} amount is 0. Skipping GL entry.")
                        continue
                    
                    ar_acc = GL_ACCOUNTS.get("AR", "1100_AR")
                    rev_acc = GL_ACCOUNTS.get("SERVICE_REV", "4100_SERVICE_REVENUE")
                    
                    # Debit AR
                    db.session.add(GLEntry(
                        batch_id=batch.id,
                        account=ar_acc,
                        debit=amount,
                        credit=0,
                        ref=svc.service_number
                    ))
                    # Credit Revenue
                    db.session.add(GLEntry(
                        batch_id=batch.id,
                        account=rev_acc,
                        debit=0,
                        credit=amount,
                        ref=svc.service_number
                    ))
                    db.session.commit()
                    print(f"      ✅ Manual Entry Created (Batch ID: {batch.id})")
                    fixed_services += 1
                    
                except Exception as e:
                    print(f"      ❌ Error fixing Service {svc.id}: {e}")
                    db.session.rollback()
        
        if fixed_services == 0:
            print("   ✅ No services needed fixing.")
        else:
            print(f"   ✅ Fixed {fixed_services} services.")

        # ---------------------------------------------------------
        # 2. FIX MISSING GL FOR COMPLETED PAYMENTS (Like 207)
        # ---------------------------------------------------------
        print("\n--- 2. Fixing Completed Payments without GL ---")
        payments = Payment.query.filter(
            Payment.status == 'COMPLETED'
        ).all()
        
        fixed_payments = 0
        for p in payments:
            batch = GLBatch.query.filter(
                GLBatch.source_type == 'PAYMENT',
                GLBatch.source_id == p.id,
                GLBatch.status == 'POSTED'
            ).first()
            
            if not batch:
                print(f"   -> Fixing Payment ID {p.id} ({p.payment_number})...")
                try:
                    # Try automatic sync
                    run_payment_gl_sync_after_commit(p.id)
                    db.session.commit()
                    
                    if GLBatch.query.filter(GLBatch.source_type=='PAYMENT', GLBatch.source_id==p.id).first():
                        print("      ✅ Auto-Sync Success.")
                        fixed_payments += 1
                        continue
                        
                    # Manual Fallback
                    print("      ⚠️ Auto-Sync failed. Creating Manual Entry...")
                    
                    # Determine Entity
                    ent_type = p.entity_type
                    ent_id = None
                    
                    if ent_type == 'CUSTOMER': ent_id = p.customer_id
                    elif ent_type == 'SUPPLIER': ent_id = p.supplier_id
                    elif ent_type == 'PARTNER': ent_id = p.partner_id
                    elif ent_type == 'SERVICE': ent_id = p.service_id
                    elif ent_type == 'SALE': ent_id = p.sale_id
                    elif ent_type == 'INVOICE': ent_id = p.invoice_id
                    elif ent_type == 'PREORDER': ent_id = p.preorder_id
                    elif ent_type == 'EXPENSE': ent_id = p.expense_id
                    
                    # Determine Account (Dynamic Logic)
                    cash_acc = GL_ACCOUNTS.get("CASH", "1000_CASH")
                    bank_acc = GL_ACCOUNTS.get("BANK", "1010_BANK")
                    ar_acc = GL_ACCOUNTS.get("AR", "1100_AR")
                    ap_acc = GL_ACCOUNTS.get("AP", "2000_AP")
                    exp_acc = GL_ACCOUNTS.get("EXPENSE", "5000_EXPENSES")
                    
                    method_acc = cash_acc
                    if p.payment_method == 'BANK_TRANSFER':
                        method_acc = bank_acc
                    elif p.payment_method == 'CHECK':
                        method_acc = GL_ACCOUNTS.get("CHQ_REC", "1150_CHQ_REC") if p.direction == 'IN' else GL_ACCOUNTS.get("CHQ_PAY", "2150_CHQ_PAY")
                    
                    if p.direction == 'OUT': # Payment to Supplier/Expense
                        credit_account = method_acc
                        debit_account = ap_acc if ent_type == 'SUPPLIER' else exp_acc
                    else: # Receipt from Customer
                        debit_account = method_acc
                        credit_account = ar_acc
                        
                    batch = GLBatch(
                        source_type='PAYMENT',
                        source_id=p.id,
                        status='POSTED',
                        posted_at=p.payment_date or datetime.now(),
                        entity_type=ent_type,
                        entity_id=ent_id,
                        memo=f"Payment {p.payment_number} Fix",
                        currency=p.currency or 'ILS'
                    )
                    db.session.add(batch)
                    db.session.flush()
                    
                    amount = Decimal(str(p.total_amount or 0))
                    
                    if amount <= 0:
                        print(f"      ⚠️ Payment {p.id} amount is 0. Skipping GL entry.")
                        continue
                    
                    if p.direction == 'OUT':
                        # Debit (AP/Expense)
                        db.session.add(GLEntry(
                            batch_id=batch.id,
                            account=debit_account,
                            debit=amount,
                            credit=0,
                            ref=f"Fix-{p.payment_number}"
                        ))
                        # Credit (Cash)
                        db.session.add(GLEntry(
                            batch_id=batch.id,
                            account=credit_account,
                            debit=0,
                            credit=amount,
                            ref=f"Fix-{p.payment_number}"
                        ))
                    else:
                        # Debit (Cash)
                        db.session.add(GLEntry(
                            batch_id=batch.id,
                            account=debit_account,
                            debit=amount,
                            credit=0,
                            ref=f"Fix-{p.payment_number}"
                        ))
                        # Credit (AR)
                        db.session.add(GLEntry(
                            batch_id=batch.id,
                            account=credit_account,
                            debit=0,
                            credit=amount,
                            ref=f"Fix-{p.payment_number}"
                        ))
                        
                    db.session.commit()
                    print(f"      ✅ Manual Entry Created (Batch ID: {batch.id})")
                    fixed_payments += 1
                    
                except Exception as e:
                    print(f"      ❌ Error fixing Payment {p.id}: {e}")
                    db.session.rollback()

        if fixed_payments == 0:
            print("   ✅ No payments needed fixing.")
        else:
            print(f"   ✅ Fixed {fixed_payments} payments.")

        # ---------------------------------------------------------
        # 3. AUDIT STOCK LEVELS
        # ---------------------------------------------------------
        print("\n--- 3. Auditing Stock Levels ---")
        print("   ⚠️ Stock Movement audit skipped (No StockMovement table found).")
        # levels = StockLevel.query.all()
        # issues = 0
        # for lvl in levels:
        #     movements_sum = db.session.query(func.sum(StockMovement.quantity_change)).filter(
        #         StockMovement.product_id == lvl.product_id,
        #         StockMovement.warehouse_id == lvl.warehouse_id
        #     ).scalar() or 0
        #     
        #     if float(lvl.quantity or 0) != float(movements_sum):
        #         print(f"   ⚠️ Mismatch for Product {lvl.product_id} in WH {lvl.warehouse_id}: Level={lvl.quantity}, Movements={movements_sum}")
        #         issues += 1
        # 
        # if issues == 0:
        #     print("   ✅ Stock levels are consistent.")
        # else:
        #     print(f"   ⚠️ Found {issues} stock mismatches.")

        print("\n=======================================================")
        print("                  FIX COMPLETED                        ")
        print("=======================================================")

if __name__ == "__main__":
    fix_production_data()
