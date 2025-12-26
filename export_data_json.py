
import json
import os
import datetime
import decimal
import base64
from sqlalchemy import text
from app import create_app
from extensions import db

def json_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8')
        except UnicodeDecodeError:
            return base64.b64encode(obj).decode('ascii')
    if hasattr(obj, 'name'):  # Enum
        return obj.name
    if hasattr(obj, 'value'): # Enum with value
        return obj.value
    # Handle set/list if needed (though rows usually don't have sets)
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def export_to_json():
    app = create_app()
    with app.app_context():
        data = {}
        
        # Use inspector to get all table names
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        
        connection = db.engine.connect()
        try:
            for table_name in table_names:
                print(f"Exporting {table_name}...")
                try:
                    # Use raw SQL to get all data
                    result = connection.execute(text(f"SELECT * FROM {table_name}"))
                    keys = result.keys()
                    records = []
                    
                    for row in result:
                        # row is a Row object, which is like a tuple but has keys
                        # We convert it to a dict
                        # In newer SQLAlchemy, row._mapping gives a dict-like view
                        item_dict = {}
                        for idx, col_name in enumerate(keys):
                            val = row[idx]
                            item_dict[col_name] = val
                        records.append(item_dict)
                    
                    data[table_name] = records
                except Exception as e:
                    print(f"Error exporting {table_name}: {e}")
        finally:
            connection.close()

        # Ensure directory exists
        backup_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"full_backup_{timestamp}.json"
        filepath = os.path.join(backup_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, default=json_serializer, indent=2, ensure_ascii=False)
            print(f"Backup completed successfully: {filepath}")
        except Exception as e:
            print(f"Error saving backup file: {e}")
            # Try to identify which part failed
            for table, rows in data.items():
                try:
                    json.dumps(rows, default=json_serializer)
                except Exception as inner_e:
                    print(f"Serialization failed for table {table}: {inner_e}")
                    # Remove problematic table from final dump or fix it
                    # For now, just report it

if __name__ == "__main__":
    export_to_json()
