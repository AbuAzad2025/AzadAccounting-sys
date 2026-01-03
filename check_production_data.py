import os
import sys
from sqlalchemy import text, or_

# Add current directory to path
sys.path.append(os.getcwd())

from app import create_app
from models import db, Check, Payment, PaymentMethod

app = create_app()

def check_data():
    with app.app_context():
        print("=== Checking Checks Table ===")
        checks = Check.query.all()
        print(f"Total Checks found: {len(checks)}")
        for c in checks:
            print(f"ID: {c.id}, Number: {c.check_number}, Amount: {c.amount}, Status: {c.status}")
        
        print("\n=== Checking Payments Table (Method = CHEQUE/cheque) ===")
        # Check for both cases manually to be sure
        payments = Payment.query.filter(
            or_(
                Payment.method == 'cheque',
                Payment.method == 'CHEQUE'
            )
        ).all()
        
        print(f"Total Check Payments found: {len(payments)}")
        for p in payments:
            print(f"ID: {p.id}, Payment#: {p.payment_number}, Amount: {p.total_amount}, Method: '{p.method}', Check#: {p.check_number}")

        print("\n=== Raw SQL Inspection ===")
        # Inspect raw values to see if there are other variations
        try:
            result = db.session.execute(text("SELECT method, count(*) FROM payments GROUP BY method")).fetchall()
            print("Payment Methods distribution:")
            for row in result:
                print(row)
        except Exception as e:
            print(f"Error inspecting raw payments: {e}")

        try:
            result = db.session.execute(text("SELECT status, count(*) FROM checks GROUP BY status")).fetchall()
            print("Check Status distribution:")
            for row in result:
                print(row)
        except Exception as e:
            print(f"Error inspecting raw checks: {e}")

if __name__ == "__main__":
    check_data()
