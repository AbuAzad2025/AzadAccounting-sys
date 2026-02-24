import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import run_service_gl_sync_after_commit, ServiceRequest, GLBatch

from decimal import Decimal
from datetime import datetime

def fix_service_gl():
    app = create_app()
    with app.app_context():
        sid = 5
        print(f"\n=== FIXING SERVICE {sid} ===")
        
        service = db.session.get(ServiceRequest, sid)
        if not service:
            print("   -> Service not found!")
            return
            
        print(f"   -> Service: {service.service_number} | Customer: {service.customer.name if service.customer else 'Unknown'}")
        print(f"   -> Amount: {service.total_amount} | Status: {service.status}")
        
        # Check if already has GL
        batch = GLBatch.query.filter(
            GLBatch.source_type == 'SERVICE',
            GLBatch.source_id == sid
        ).first()
        
        if batch:
            print(f"   -> Already has GL Batch (ID: {batch.id}). Skipping.")
            return

        print("   -> Running GL Sync...")
        
        try:
            run_service_gl_sync_after_commit(sid)
            db.session.commit()
            print("   ✅ Sync executed successfully (Commit done).")
            
            # Verify
            batch_check = GLBatch.query.filter(
                GLBatch.source_type == 'SERVICE',
                GLBatch.source_id == sid
            ).first()
            
            if batch_check:
                print(f"   ✅ Verified: GL Batch created with ID {batch_check.id}")
            else:
                print("   ❌ Failed: GL Batch still missing.")
                print("   -> Trying MANUAL creation...")
                
                # Manual Creation Logic (Last Resort)
                from models import GLEntry
                
                batch = GLBatch(
                    source_type='SERVICE',
                    source_id=sid,
                    status='POSTED',
                    posted_at=service.completed_at or datetime.now(),
                    entity_type='CUSTOMER',
                    entity_id=service.customer_id,
                    memo=f"Service Revenue {service.service_number}",
                    # created_by_id=1,
                    currency=service.currency or 'ILS'
                )
                db.session.add(batch)
                db.session.flush()
                
                amount = Decimal(str(service.total_amount or 0))
                
                # Debit AR (Customer)
                db.session.add(GLEntry(
                    batch_id=batch.id,
                    account='1100_AR',
                    debit=amount,
                    credit=0,
                    ref=service.service_number
                ))
                
                # Credit Revenue
                db.session.add(GLEntry(
                    batch_id=batch.id,
                    account='4000_REVENUE',
                    debit=0,
                    credit=amount,
                    ref=service.service_number
                ))
                
                db.session.commit()
                print(f"   ✅ Manual Batch created with ID: {batch.id}")
                
        except Exception as e:
            print(f"   ❌ Error during sync: {e}")

if __name__ == "__main__":
    fix_service_gl()
