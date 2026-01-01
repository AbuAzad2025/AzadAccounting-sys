from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text("UPDATE alembic_version SET version_num = '121683435140'"))
        db.session.commit()
        print("Updated version to 121683435140")
    except Exception as e:
        print("Error:", e)
