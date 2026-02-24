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
from models import (
    ServiceRequest, Payment, GLBatch, GLEntry, 
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
                    
                    # Debit AR
                    db.session.add(GLEntry(
                        batch_id=batch.id,
                        account='1100_AR',
                        debit=amount,
                        credit=0,
                        ref=svc.service_number
                    ))
                    # Credit Revenue
                    db.session.add(GLEntry(
                        batch_id=batch.id,
                        account='4000_REVENUE',
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
                    
                    # Determine Account (Simple Logic)
                    if p.direction == 'OUT': # Payment to Supplier/Expense
                        # Credit Cash/Bank, Debit AP/Expense
                        credit_account = '1100_CASH' # Default
                        debit_account = '2100_AP' if ent_type == 'SUPPLIER' else '5000_EXPENSE'
                    else: # Receipt from Customer
                        # Debit Cash, Credit AR
                        debit_account = '1100_CASH'
                        credit_account = '1100_AR'
                        
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

        print("\n=======================================================")
        print("                  FIX COMPLETED                        ")
        print("=======================================================")

if __name__ == "__main__":
    fix_production_data()
