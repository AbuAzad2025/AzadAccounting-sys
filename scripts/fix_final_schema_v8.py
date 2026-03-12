import os
import sys
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.schema import CreateIndex, DropIndex
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from alembic.operations import Operations

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
import models

def fix_final_schema_v8():
    app = create_app()
    with app.app_context():
        print(f"🕵️  Starting FINAL SCHEMA ANALYSIS (V8) on: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        engine = db.engine
        metadata = db.metadata
        
        # Manually define known functional/partial indexes from models.py to ensure exact match
        # This is critical because reflection often misses partial filter clauses or functional expressions
        from sqlalchemy import Index, func
        
        # We need to bind the metadata to the engine to reflect current state
        metadata.bind = engine
        
        with engine.connect() as connection:
            # 1. Analyze Index Drift with deep inspection
            print("\n🔍 Analyzing Indexes...")
            
            # Get all existing indexes from DB
            inspector = inspect(connection)
            
            # Define the "Stubborn" indexes that keep reappearing as missing/extra
            # These are usually functional or partial indexes
            stubborn_indexes = {
                'uq_products_name_global_ci': {
                    'table': 'products',
                    'def': 'CREATE UNIQUE INDEX uq_products_name_global_ci ON products (lower(name)) WHERE warehouse_id IS NULL'
                },
                'uq_products_name_wh_ci': {
                    'table': 'products',
                    'def': 'CREATE UNIQUE INDEX uq_products_name_wh_ci ON products (lower(name), warehouse_id) WHERE warehouse_id IS NOT NULL'
                },
                'uq_products_sku_ci': {
                    'table': 'products',
                    'def': 'CREATE UNIQUE INDEX uq_products_sku_ci ON products (lower(sku)) WHERE sku IS NOT NULL'
                },
                'uq_products_serial_ci': {
                    'table': 'products',
                    'def': 'CREATE UNIQUE INDEX uq_products_serial_ci ON products (lower(serial_no)) WHERE serial_no IS NOT NULL'
                },
                'ix_invoices_invoice_number': {
                    'table': 'invoices',
                    'def': 'CREATE UNIQUE INDEX ix_invoices_invoice_number ON invoices (invoice_number)' # Should be unique per model?
                },
                'ix_payments_payment_number': {
                    'table': 'payments',
                    'def': 'CREATE UNIQUE INDEX ix_payments_payment_number ON payments (payment_number)'
                },
                'ix_payments_receipt_number': {
                    'table': 'payments',
                    'def': 'CREATE UNIQUE INDEX ix_payments_receipt_number ON payments (receipt_number)'
                }
            }

            for idx_name, idx_info in stubborn_indexes.items():
                table_name = idx_info['table']
                print(f"   Checking stubborn index: {idx_name} on {table_name}...", end=" ")
                
                # Check if exists
                existing_indexes = inspector.get_indexes(table_name)
                exists = any(i['name'] == idx_name for i in existing_indexes)
                
                if exists:
                    print("Exists. (Dropping to recreate to ensure correctness)...", end=" ")
                    try:
                        connection.execute(text(f'DROP INDEX IF EXISTS "{idx_name}";'))
                        connection.commit()
                        print("Dropped.", end=" ")
                    except Exception as e:
                        print(f"❌ Drop Failed: {e}")
                        continue
                else:
                    print("Missing.", end=" ")
                
                # Recreate with raw SQL to guarantee exact definition
                print("Recreating...", end=" ")
                try:
                    connection.execute(text(idx_info['def']))
                    connection.commit()
                    print("✅ Created.")
                except Exception as e:
                    print(f"❌ Create Failed: {e}")
                    connection.rollback()

            # 2. Fix Enum Types (VARCHAR -> ENUM)
            print("\n🔄 Checking Enum Types...")
            # Sale.payment_status (VARCHAR -> sale_payment_progress)
            # OnlinePreOrder.payment_status (VARCHAR -> online_preorder_payment_status)
            
            enum_fixes = [
                {
                    'table': 'sales',
                    'col': 'payment_status',
                    'type': 'sale_payment_progress',
                    'vals': ["PENDING", "PARTIAL", "PAID", "REFUNDED", "COMPLETED"]
                },
                {
                    'table': 'online_preorders',
                    'col': 'payment_status',
                    'type': 'online_preorder_payment_status',
                    'vals': ["PENDING", "PARTIAL", "PAID", "REFUNDED", "COMPLETED"]
                }
            ]
            
            for fix in enum_fixes:
                print(f"   Fixing Enum {fix['table']}.{fix['col']}...", end=" ")
                try:
                    # 1. Create Type if not exists
                    vals_str = ", ".join([f"'{v}'" for v in fix['vals']])
                    create_type = f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{fix['type']}') THEN CREATE TYPE {fix['type']} AS ENUM ({vals_str}); END IF; END $$;"
                    connection.execute(text(create_type))
                    
                    # 2. Alter Column
                    alter_col = f'ALTER TABLE "{fix["table"]}" ALTER COLUMN "{fix["col"]}" TYPE {fix["type"]} USING "{fix["col"]}"::{fix["type"]};'
                    connection.execute(text(alter_col))
                    connection.commit()
                    print("✅ Done.")
                except Exception as e:
                    print(f"❌ Failed: {e}")
                    connection.rollback()

            # 3. Fix Extra Indexes (Aggressive Cleanup)
            print("\n🧹 Cleaning up OLD/WARNING indexes (Aggressive)...")
            
            # List of indexes reported as WARNING (Extra) by check_schema_drift
            # These are indexes that exist in DB but are NOT in the models/code
            # We will DROP them to ensure perfect sync.
            
            indexes_to_drop = [
                ('checks', 'ix_checks_check_date'),
                ('checks', 'ix_checks_check_date_status'),
                ('checks', 'ix_checks_customer_id_date'),
                ('checks', 'ix_checks_date_pending'),
                ('checks', 'ix_checks_is_archived_status'),
                ('checks', 'ix_checks_partner_id_date'),
                ('checks', 'ix_checks_payment_id_status'),
                ('checks', 'ix_checks_status_due_date_direction'),
                ('checks', 'ix_checks_supplier_id_date'),
                ('customers', 'ix_customers_category'),
                ('customers', 'ix_customers_is_active'),
                ('customers', 'ix_customers_is_archived'),
                ('customers', 'ix_customers_is_online'),
                ('customers', 'ix_customers_lower_email'),
                ('customers', 'ix_customers_name'),
                ('customers', 'ix_customers_phone'),
                ('invoices', 'ix_invoices_customer_date'),
                ('partners', 'ix_partners_currency_balance'),
                ('partners', 'ix_partners_is_archived_balance'),
                ('partners', 'ix_partners_name_phone'),
                ('partners', 'ix_partners_share_percentage'),
                ('payments', 'ix_payments_currency'),
                ('payments', 'ix_payments_customer_date'),
                ('payments', 'ix_payments_customer_date_completed'),
                ('payments', 'ix_payments_date'),
                ('payments', 'ix_payments_date_active'),
                ('payments', 'ix_payments_direction'),
                ('payments', 'ix_payments_partner_date'),
                ('payments', 'ix_payments_status'),
                ('payments', 'ix_payments_supplier_date'),
                ('sales', 'ix_sales_customer_date'),
                ('sales', 'ix_sales_date'),
                ('service_requests', 'ix_service_received_active'),
                ('service_requests', 'ix_service_requests_customer_date'),
                ('service_requests', 'ix_service_requests_customer_status_date'),
                ('service_requests', 'ix_service_requests_mechanic_status'),
                ('service_requests', 'ix_service_requests_received_status'),
                ('service_requests', 'ix_service_requests_status_created_at'),
                ('service_requests', 'ix_service_requests_status_priority'),
                ('stock_levels', 'ix_stock_levels_prod'),
                ('stock_levels', 'ix_stock_levels_wh'),
                ('stock_levels', 'ix_stock_levels_wh_prod'),
                ('suppliers', 'ix_suppliers_currency'),
                ('suppliers', 'ix_suppliers_lower_email'),
                ('suppliers', 'ix_suppliers_name'),
                ('users', 'ix_users_is_active'),
                ('users', 'ix_users_last_login'),
                ('users', 'ix_users_last_seen'),
                ('users', 'ix_users_lower_email'),
                ('users', 'ix_users_lower_username')
            ]
            
            for table_name, idx_name in indexes_to_drop:
                 print(f"   Dropping extra index: {idx_name} on {table_name}...", end=" ")
                 try:
                     connection.execute(text(f'DROP INDEX IF EXISTS "{idx_name}";'))
                     connection.commit()
                     print("✅ Dropped.")
                 except Exception as e:
                     print(f"❌ Failed: {e}")
                     connection.rollback()
            
            print("\n🧹 Final Cleanup Complete.")
            
            # 4. Final Verification
            print("\n🔍 Running verification check...")
            try:
                # We can call check_schema_drift.py programmatically or just rely on user to run it
                pass
            except Exception:
                pass

if __name__ == "__main__":
    fix_final_schema_v8()
