
import sys
import os
from sqlalchemy import text

# Add the project directory to the path so we can import the app
sys.path.append(os.getcwd())

from app import create_app
from models import db, Supplier, Partner, Customer, _ensure_customer_for_counterparty

def check_and_fix_links():
    app = create_app()
    with app.app_context():
        print("Checking Suppliers...")
        total_suppliers = Supplier.query.count()
        suppliers_without_customer = Supplier.query.filter(Supplier.customer_id == None).all()
        
        print(f"Total Suppliers: {total_suppliers}")
        if not suppliers_without_customer:
            print("All suppliers have linked customers.")
        else:
            print(f"Found {len(suppliers_without_customer)} suppliers without linked customers.")
            for s in suppliers_without_customer:
                print(f" - Fixing Supplier: {s.name} (ID: {s.id})")
                try:
                    # Use the logic from models.py but adapted since we are outside the event listener
                    # We can call _ensure_customer_for_counterparty passing the connection
                    customer_id = _ensure_customer_for_counterparty(
                        db.session.connection(),
                        name=s.name,
                        phone=s.phone,
                        whatsapp=s.phone, # Assuming whatsapp is same as phone for now
                        email=s.email,
                        address=s.address,
                        currency=s.currency,
                        source_label="SUPPLIER",
                        source_id=s.id
                    )
                    
                    if customer_id:
                        s.customer_id = customer_id
                        db.session.add(s)
                        print(f"   -> Linked to Customer ID: {customer_id}")
                    else:
                        print(f"   -> Failed to create/find customer for {s.name}")
                except Exception as e:
                    print(f"   -> Error processing {s.name}: {e}")

        print("\nChecking Partners...")
        total_partners = Partner.query.count()
        partners_without_customer = Partner.query.filter(Partner.customer_id == None).all()
        
        print(f"Total Partners: {total_partners}")
        if not partners_without_customer:
            print("All partners have linked customers.")
        else:
            print(f"Found {len(partners_without_customer)} partners without linked customers.")
            for p in partners_without_customer:
                print(f" - Fixing Partner: {p.name} (ID: {p.id})")
                try:
                    customer_id = _ensure_customer_for_counterparty(
                        db.session.connection(),
                        name=p.name,
                        phone=p.phone,
                        whatsapp=p.phone,
                        email=p.email,
                        address=p.address,
                        currency="ILS", # Partners usually use ILS or default
                        source_label="PARTNER",
                        source_id=p.id
                    )
                    
                    if customer_id:
                        p.customer_id = customer_id
                        db.session.add(p)
                        print(f"   -> Linked to Customer ID: {customer_id}")
                    else:
                        print(f"   -> Failed to create/find customer for {p.name}")
                except Exception as e:
                    print(f"   -> Error processing {p.name}: {e}")

        # Commit changes
        if suppliers_without_customer or partners_without_customer:
            try:
                db.session.commit()
                print("\nChanges committed successfully.")
            except Exception as e:
                db.session.rollback()
                print(f"\nError committing changes: {e}")
        else:
            print("\nNo changes needed.")

if __name__ == "__main__":
    check_and_fix_links()
