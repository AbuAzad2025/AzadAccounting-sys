import os
import sys
from pathlib import Path
from sqlalchemy import text, func

# Add project root to sys.path
ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import ServiceRequest, Payment, GLBatch, Customer, GLEntry

def audit_service_gl():
    app = create_app()
    with app.app_context():
        print("\n=======================================================")
        print("          AUDIT: COMPLETED SERVICES GL SYNC           ")
        print("=======================================================")
        
        # 1. Find Completed Services
        completed_services = ServiceRequest.query.filter(
            ServiceRequest.status.in_(['COMPLETED', 'DELIVERED'])
        ).all()
        
        count_services = len(completed_services)
        print(f"Total Completed Services: {count_services}")
        
        missing_gl_count = 0
        services_to_fix = []
        
        for svc in completed_services:
            # Check for GL Batch
            gl_batch = GLBatch.query.filter(
                GLBatch.source_type == 'SERVICE',
                GLBatch.source_id == svc.id,
                GLBatch.status == 'POSTED'
            ).first()
            
            # Check for Payments (just for info)
            payments = Payment.query.filter_by(service_id=svc.id).all()
            total_paid = sum(p.total_amount for p in payments) if payments else 0
            
            has_gl = bool(gl_batch)
            
            if gl_batch:
                gl_rev = sum(e.credit for e in gl_batch.entries if e.account_id in ['4100_SERVICE_REVENUE', '4000_REVENUE'])
                svc_amt = float(svc.total_amount or 0)
                if abs(float(gl_rev) - svc_amt) > 0.01:
                    print(f"   ⚠️ GL Amount Mismatch! Service ID {svc.id}: Service Amt={svc_amt}, GL Revenue={gl_rev}")
            
            is_fully_paid = (total_paid >= (svc.total_amount or 0))
            
            if not has_gl:
                customer_name = svc.customer.name if svc.customer else "Unknown"
                print(f"❌ Service ID {svc.id} ({svc.service_number}) | Customer: {customer_name}")
                print(f"   Amount: {svc.total_amount} | Paid: {total_paid}")
                print(f"   Status: {svc.status} | Has GL: {has_gl}")
                print("   ---")
                missing_gl_count += 1
                services_to_fix.append(svc.id)
                
        if missing_gl_count == 0:
            print("✅ All completed services have GL entries.")
        else:
            print(f"⚠️ Found {missing_gl_count} completed services WITHOUT GL entries.")
            print("   This means revenue/receivables are missing from Accounting.")
            print("   But they might appear on Customer Statement (Operational View).")

        return services_to_fix

if __name__ == "__main__":
    audit_service_gl()
