import os
import sys
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from app import app, db
    from models import GLBatch, GLEntry
except ImportError as e:
    print(f"Error importing app modules: {e}")
    sys.exit(1)

def cleanup_empty_batches():
    print("===================================================")
    print("   Garage Manager - Cleanup Empty Batches")
    print("===================================================")
    
    with app.app_context():
        conn = db.session.connection()
        
        # 1. Find Empty Batches
        print("\nFinding empty batches...")
        empty_batches = conn.execute(text("""
            SELECT b.id, b.code, b.source_type, b.source_id 
            FROM gl_batches b
            LEFT JOIN gl_entries e ON b.id = e.batch_id
            WHERE e.id IS NULL
        """)).fetchall()
        
        count = len(empty_batches)
        if count == 0:
            print("No empty batches found. Everything looks clean!")
            return

        print(f"Found {count} empty batches.")
        
        # 2. Delete Them
        print(f"Deleting {count} empty batches...")
        try:
            # We use a transaction to be safe
            with conn.begin():
                # Get IDs to delete
                ids_to_delete = [b.id for b in empty_batches]
                
                # Execute deletion
                # Note: We use raw SQL for performance and simplicity here
                if ids_to_delete:
                    # Convert list to tuple for SQL IN clause
                    ids_tuple = tuple(ids_to_delete)
                    if len(ids_tuple) == 1:
                        # Handle single item tuple syntax (id,)
                        query = text("DELETE FROM gl_batches WHERE id = :id")
                        conn.execute(query, {"id": ids_tuple[0]})
                    else:
                        query = text("DELETE FROM gl_batches WHERE id IN :ids")
                        conn.execute(query, {"ids": ids_tuple})
            
            print(f"✅ Successfully deleted {count} empty batches.")
            
        except Exception as e:
            print(f"❌ Error deleting batches: {e}")

if __name__ == "__main__":
    cleanup_empty_batches()
