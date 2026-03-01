
import os
import sys
from sqlalchemy.schema import CreateTable
from sqlalchemy import create_mock_engine

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db

def dump_schema():
    """
    Generates the full CREATE TABLE statements for all models in the application.
    This creates a reliable schema snapshot.
    """
    app = create_app()
    
    with app.app_context():
        # Force load all models to ensure they are registered with SQLAlchemy
        import models  # This imports all models if they are defined in models.py
        
        # We can use the metadata directly from the db object
        metadata = db.metadata
        
        # Prepare the output file
        output_file = 'full_database_schema.sql'
        
        # We use a mock engine to generate the SQL without executing it
        def dump(sql, *multiparams, **params):
            # This function receives the SQL string
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(str(sql.compile(dialect=db.engine.dialect)).strip() + ';\n\n')

        # Use the actual engine dialect to ensure compatibility
        engine = create_mock_engine(db.engine.url, dump)
        
        print(f"Generating schema snapshot to {output_file}...")
        
        # Clear existing file
        if os.path.exists(output_file):
            os.remove(output_file)
            
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- Garage Manager System Full Schema Snapshot\n")
            f.write("-- Generated automatically for disaster recovery\n\n")

        # Generate CREATE statements
        metadata.create_all(engine, checkfirst=False)
        
        print("✅ Schema snapshot generated successfully.")
        print(f"File saved: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    dump_schema()
