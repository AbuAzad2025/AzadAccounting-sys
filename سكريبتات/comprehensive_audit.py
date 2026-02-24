from __future__ import annotations

import os
import sys
from pathlib import Path
from decimal import Decimal
from sqlalchemy import text, func

ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import (
    Customer, Supplier, Partner, GLBatch, GLEntry, Payment, Sale, Invoice,
    PaymentSplit, Check, CheckStatus, Product, Warehouse, StockLevel,
    ServiceRequest, ServicePart, ServiceTask, Expense
)
from utils import get_entity_balance_in_ils

def _scalar(sql, params=None):
    return db.session.execute(text(sql), params or {}).scalar()

def run_audit():
    app = create_app()
    with app.app_context():
        print("\n=======================================================")
        print("          COMPREHENSIVE SYSTEM AUDIT REPORT            ")
        print("=======================================================\n")
        
        # 1. GL Integrity Check
        print("--- 1. GL Integrity Check ---")
        unbalanced_batches = _scalar("""
            SELECT COUNT(*) FROM (
                SELECT b.id FROM gl_batches b
                JOIN gl_entries e ON e.batch_id = b.id
                WHERE b.status='POSTED'
                GROUP BY b.id
                HAVING ROUND(SUM(e.debit), 2) <> ROUND(SUM(e.credit), 2)
            ) x
        """)
        print(f"   - Unbalanced Posted Batches: {unbalanced_batches}")
        
        orphan_entries = _scalar("""
            SELECT COUNT(*) FROM gl_entries e
            LEFT JOIN gl_batches b ON b.id = e.batch_id
            WHERE b.id IS NULL
        """)
        print(f"   - Orphan GL Entries: {orphan_entries}")
        
        empty_batches = _scalar("""
            SELECT COUNT(*) FROM gl_batches b
            LEFT JOIN gl_entries e ON e.batch_id = b.id
            WHERE e.id IS NULL AND b.status='POSTED'
        """)
        print(f"   - Empty Posted Batches: {empty_batches}")

        # 2. Entity Balance Consistency
        print("\n--- 2. Entity Balance Consistency ---")
        
        def check_entity_balance(model, type_name):
            entities = model.query.filter(model.is_archived == False).all()
            mismatches = 0
            total_diff = Decimal('0.00')
            for e in entities:
                stored_balance = Decimal(str(e.current_balance or 0))
                # Calculate from GL
                gl_balance = get_entity_balance_in_ils(type_name, e.id)
                diff = abs(stored_balance - gl_balance)
                if diff > Decimal('0.01'):
                    mismatches += 1
                    total_diff += diff
                    # print(f"     ! Mismatch {type_name} #{e.id}: Stored={stored_balance}, GL={gl_balance}, Diff={diff}")
            return mismatches, total_diff

        cust_mis, cust_diff = check_entity_balance(Customer, 'CUSTOMER')
        print(f"   - Customers: {cust_mis} mismatches (Total Diff: {cust_diff})")
        
        supp_mis, supp_diff = check_entity_balance(Supplier, 'SUPPLIER')
        print(f"   - Suppliers: {supp_mis} mismatches (Total Diff: {supp_diff})")
        
        part_mis, part_diff = check_entity_balance(Partner, 'PARTNER')
        print(f"   - Partners:  {part_mis} mismatches (Total Diff: {part_diff})")

        # 3. Transaction Integrity
        print("\n--- 3. Transaction Integrity ---")
        
        sales_no_gl = _scalar("""
            SELECT COUNT(*) FROM sales s
            LEFT JOIN gl_batches b ON b.source_type='SALE' AND b.source_id=s.id AND b.status='POSTED'
            WHERE s.status='CONFIRMED' AND b.id IS NULL
        """)
        print(f"   - Confirmed Sales without GL: {sales_no_gl}")
        
        payments_no_gl = _scalar("""
            SELECT COUNT(*) FROM payments p
            LEFT JOIN gl_batches b ON b.source_type='PAYMENT' AND b.source_id=p.id AND b.status='POSTED'
            WHERE p.status='COMPLETED' AND b.id IS NULL
        """)
        print(f"   - Completed Payments without GL: {payments_no_gl}")

        # 4. Stock & Warehouse Integrity
        print("\n--- 4. Stock & Warehouse Integrity ---")
        
        neg_stock = _scalar("SELECT COUNT(*) FROM stock_levels WHERE quantity < 0")
        print(f"   - Negative Stock Levels: {neg_stock}")
        
        orphan_stock = _scalar("""
            SELECT COUNT(*) FROM stock_levels s
            LEFT JOIN products p ON p.id = s.product_id
            WHERE p.id IS NULL
        """)
        print(f"   - Orphan Stock Levels (No Product): {orphan_stock}")

        # 5. Data Anomalies
        print("\n--- 5. Data Anomalies ---")
        
        dup_payments = _scalar("""
            SELECT COUNT(*) FROM (
                SELECT payment_number FROM payments 
                GROUP BY payment_number HAVING COUNT(*) > 1
            ) x
        """)
        print(f"   - Duplicate Payment Numbers: {dup_payments}")
        
        dup_sales = _scalar("""
            SELECT COUNT(*) FROM (
                SELECT sale_number FROM sales 
                GROUP BY sale_number HAVING COUNT(*) > 1
            ) x
        """)
        print(f"   - Duplicate Sale Numbers: {dup_sales}")

        print("\n=======================================================")
        print("                   AUDIT COMPLETE                      ")
        print("=======================================================\n")

if __name__ == "__main__":
    run_audit()
