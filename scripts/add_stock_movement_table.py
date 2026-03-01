import sys
import os
from pathlib import Path

# Add project root to sys.path
ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import create_app
from extensions import db
from models import StockMovement

app = create_app()

with app.app_context():
    print("Creating StockMovement table...")
    try:
        StockMovement.__table__.create(db.engine)
        print("✅ StockMovement table created successfully.")
    except Exception as e:
        print(f"⚠️ Table might already exist: {e}")
