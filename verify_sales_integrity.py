from app import create_app
from models import Sale, Payment, PaymentStatus
from sqlalchemy import func
from decimal import Decimal

def verify_sales_integrity():
    app = create_app()
    with app.app_context():
        print("Checking Sales Integrity for Customer 1...")
        sales = Sale.query.filter_by(customer_id=1, status='CONFIRMED').all()
        
        total_discrepancy = Decimal('0.00')
        
        for sale in sales:
            stored_paid = Decimal(str(sale.total_paid or 0))
            
            # Sum actual payments linked to this sale
            # Note: Payment status should be COMPLETED or PENDING (if PENDING counts as paid? usually only COMPLETED)
            # But let's check what matches stored_paid.
            
            actual_payments = Payment.query.filter(
                Payment.sale_id == sale.id,
                Payment.status.in_([PaymentStatus.COMPLETED, PaymentStatus.PENDING])
            ).all()
            
            calculated_paid = sum(Decimal(str(p.total_amount or 0)) for p in actual_payments)
            
            if abs(stored_paid - calculated_paid) > 0.01:
                print(f"Mismatch in Sale {sale.id} ({sale.sale_number}):")
                print(f"  Stored Total Paid: {stored_paid}")
                print(f"  Sum of Payments:   {calculated_paid}")
                print(f"  Difference:        {stored_paid - calculated_paid}")
                total_discrepancy += (stored_paid - calculated_paid)
        
        print("-" * 30)
        print(f"Total Discrepancy (Stored Paid - Actual Payments): {total_discrepancy}")

if __name__ == "__main__":
    verify_sales_integrity()
