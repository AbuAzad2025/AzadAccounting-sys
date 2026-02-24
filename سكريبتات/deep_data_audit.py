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
from models import Check, Expense, SaleReturn, ServiceRequest, Invoice, GLBatch

def run_deep_audit():
    app = create_app()
    with app.app_context():
        print("\n=======================================================")
        print("          DEEP DATA AUDIT REPORT (V2)           ")
        print("=======================================================")
        
        # 1. CHEQUES AUDIT
        print("\n--- 1. Cheques Integrity ---")
        # Find Checks without Payment link (Orphan Checks, might be okay for manual checks but worth checking)
        orphan_checks = db.session.execute(text("""
            SELECT COUNT(*) FROM checks 
            WHERE payment_id IS NULL AND (reference_number IS NULL OR reference_number NOT LIKE 'PMT-%')
        """)).scalar()
        print(f"   - Orphan Checks (No Payment Link): {orphan_checks}")
        
        # Find Cashed Checks without GL (Should have GL entry when cashed)
        # Assuming status 'CASHED' means it hit the bank
        # We look for GL Batch with source_type='CHECK' and source_id=check.id
        cashed_no_gl = db.session.execute(text("""
            SELECT COUNT(*) FROM checks c
            WHERE c.status = 'CASHED'
            AND NOT EXISTS (
                SELECT 1 FROM gl_batches b 
                WHERE b.source_type='CHECK' AND b.source_id=c.id AND b.status='POSTED'
            )
        """)).scalar()
        print(f"   - Cashed Checks without GL: {cashed_no_gl}")
        
        # 2. EXPENSES AUDIT
        print("\n--- 2. Expenses Integrity ---")
        # Expenses without GL Batch
        expenses_no_gl = db.session.execute(text("""
            SELECT COUNT(*) FROM expenses e
            WHERE NOT EXISTS (
                SELECT 1 FROM gl_batches b 
                WHERE b.source_type='EXPENSE' AND b.source_id=e.id AND b.status='POSTED'
            )
        """)).scalar()
        print(f"   - Expenses without GL: {expenses_no_gl}")
        
        # Expenses paid by Check but no Check record created?
        # This is harder to check directly without parsing 'method', let's skip for now unless critical.
        
        # 3. RETURNS AUDIT (Sale Returns)
        print("\n--- 3. Returns Integrity ---")
        returns_no_gl = db.session.execute(text("""
            SELECT COUNT(*) FROM sale_returns sr
            WHERE sr.status = 'COMPLETED'
            AND NOT EXISTS (
                SELECT 1 FROM gl_batches b 
                WHERE b.source_type='SALE_RETURN' AND b.source_id=sr.id AND b.status='POSTED'
            )
        """)).scalar()
        print(f"   - Completed Sale Returns without GL: {returns_no_gl}")
        
        # 4. MAINTENANCE (Service Requests)
        print("\n--- 4. Maintenance Integrity ---")
        # Check if completed service requests have payments or are marked as paid
        # ServiceRequest doesn't have invoice_id directly, it uses Payment with service_id
        
        # Find completed services with no payments (Unpaid Services)
        # Note: This is not necessarily an error (could be credit), but good to know
        services_unpaid = db.session.execute(text("""
            SELECT COUNT(*) FROM service_requests sr
            WHERE sr.status IN ('COMPLETED', 'DELIVERED')
            AND NOT EXISTS (
                SELECT 1 FROM payments p 
                WHERE p.service_id = sr.id AND p.status = 'COMPLETED'
            )
        """)).scalar()
        print(f"   - Completed Jobs without Payments: {services_unpaid}")
        
        # Invoices without GL
        # Invoice status is determined by cancelled_at (if NULL then active/posted)
        invoices_no_gl = db.session.execute(text("""
            SELECT COUNT(*) FROM invoices i
            WHERE i.cancelled_at IS NULL
            AND NOT EXISTS (
                SELECT 1 FROM gl_batches b 
                WHERE b.source_type='INVOICE' AND b.source_id=i.id AND b.status='POSTED'
            )
        """)).scalar()
        print(f"   - Active Invoices without GL: {invoices_no_gl}")

        print("\n=======================================================")
        print("                    AUDIT COMPLETE                      ")
        print("=======================================================")

if __name__ == "__main__":
    run_deep_audit()
