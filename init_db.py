import os
import sys

# Ensure the current directory is in the python path
sys.path.append(os.getcwd())

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Creating all tables...")
    try:
        db.create_all()
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
    
    # Verify
    try:
        print("Verifying 'users' table existence...")
        with db.engine.connect() as connection:
            # We use text() for raw SQL
            result = connection.execute(text("SELECT count(*) FROM users"))
            print(f"Users table count: {result.scalar()}")
            print("Verification successful: 'users' table exists.")
    except Exception as e:
        print(f"Verification warning: {e}")
