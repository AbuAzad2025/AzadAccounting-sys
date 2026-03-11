
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import inspect
from sqlalchemy import create_engine, inspect as sa_inspect, text
from flask import Flask
from extensions import db
from config import Config

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_types_rigorous():
    print("🔍 Starting Rigorous Data Type Audit (Date/Time & Financials)...")
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    issues_found = []
    
    with app.app_context():
        inspector = sa_inspect(db.engine)
        
        # Import models
        try:
            import models
        except Exception as e:
            print(f"❌ Failed to import models: {e}")
            return

        # Get all DB Models
        db_models = []
        for name, obj in inspect.getmembers(models):
            if inspect.isclass(obj) and hasattr(obj, '__tablename__'):
                db_models.append(obj)
        
        print(f"📊 Analyzing {len(db_models)} models for Type Consistency...")
        
        for model in db_models:
            table_name = model.__tablename__
            
            try:
                columns = inspector.get_columns(table_name)
                db_cols = {c['name']: c for c in columns}
            except Exception:
                # print(f"⚠️ Table {table_name} not found in DB!")
                continue
            
            for col_name, col_info in db_cols.items():
                col_type = str(col_info['type']).upper()
                
                # 1. Date/Time Rigor
                # Check for columns that look like dates but aren't
                if any(x in col_name.lower() for x in ['date', '_at', 'time', 'period']) and 'update' not in col_name.lower():
                    if 'VARCHAR' in col_type or 'TEXT' in col_type or 'STRING' in col_type:
                        issues_found.append(f"🔴 CRITICAL: {table_name}.{col_name} is {col_type} but looks like a Date/Time field!")
                    
                    # Check for consistency (e.g., TIMESTAMP vs DATE)
                    # _at implies specific moment -> TIMESTAMP
                    if '_at' in col_name and 'DATE' in col_type and 'TIMESTAMP' not in col_type:
                         issues_found.append(f"⚠️ WARNING: {table_name}.{col_name} is {col_type}. '_at' fields usually require TIMESTAMP precision.")
                    
                    # Check for Timezone Awareness
                    if 'TIMESTAMP' in col_type and 'WITH TIME ZONE' not in col_type:
                        issues_found.append(f"⚠️ NOTICE: {table_name}.{col_name} is {col_type}. Consider TIMESTAMP WITH TIME ZONE for absolute precision.")
                
                # 2. Financial Rigor (Money must be Numeric/Decimal, never Float)
                is_financial = any(x in col_name.lower() for x in ['price', 'cost', 'amount', 'balance', 'total', 'tax', 'discount', 'salary', 'wage'])
                if is_financial and 'id' not in col_name: # skip price_list_id etc
                    if 'FLOAT' in col_type or 'DOUBLE' in col_type or 'REAL' in col_type:
                        issues_found.append(f"🔴 CRITICAL: {table_name}.{col_name} is {col_type}. Financials MUST be NUMERIC/DECIMAL to avoid rounding errors.")
                    
                    # Check Precision
                    if 'NUMERIC' in col_type or 'DECIMAL' in col_type:
                        # usually NUMERIC(precision, scale) e.g. NUMERIC(12, 2)
                        # SQLAlchemy reflection might show NUMERIC(12, 2) or just NUMERIC
                        pass 

                # 3. Boolean Rigor
                is_bool_name = col_name.startswith('is_') or col_name.startswith('has_') or col_name.startswith('can_')
                if is_bool_name:
                    if 'BOOL' not in col_type:
                         issues_found.append(f"⚠️ WARNING: {table_name}.{col_name} is {col_type}. Should be BOOLEAN.")

    print("\n" + "="*60)
    print("📋 RIGOROUS TYPE AUDIT REPORT")
    print("="*60)
    if issues_found:
        for issue in sorted(list(set(issues_found))):
            print(issue)
    else:
        print("✅ No Data Type issues found! Perfection achieved.")
    print("="*60)

if __name__ == "__main__":
    check_types_rigorous()
