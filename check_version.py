from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        result = db.session.execute(text("SELECT * FROM alembic_version")).fetchall()
        print("Current version:", result)
    except Exception as e:
        print("Error:", e)
