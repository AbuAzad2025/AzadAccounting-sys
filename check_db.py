import os

os.environ["SKIP_SYSTEM_INTEGRITY"] = "1"

from app import create_app, db
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

def check_database():
    app = create_app()
    with app.app_context():
        print("="*60)
        print("🔍 DATABASE VERIFICATION TOOL | أداة فحص قاعدة البيانات")
        print("="*60)
        
        try:
            # Check connection
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ Database Connection: OK")
                
                # Get all tables
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"📊 Found {len(tables)} tables in database:")
                print("-" * 60)

                def _q_ident(name: str) -> str:
                    return '"' + (name or "").replace('"', '""') + '"'

                def _count_table(table_name: str) -> int | None:
                    if table_name not in tables:
                        return None
                    stmt = text(f"SELECT COUNT(*) FROM public.{_q_ident(table_name)}")
                    return int(conn.execute(stmt).scalar() or 0)

                critical = [
                    "warehouses",
                    "products",
                    "expenses",
                    "payments",
                    "accounts",
                    "gl_batches",
                    "gl_entries",
                    "customers",
                    "sales",
                ]

                print("📌 ملخص سريع للجداول الأساسية:")
                for t in critical:
                    try:
                        c = _count_table(t)
                        if c is None:
                            print(f" - {t:<20} : ❌ غير موجود")
                        else:
                            print(f" - {t:<20} : {c} rows")
                    except Exception as e:
                        print(f" - {t:<20} : Error ({e})")

                print("-" * 60)
                print("📄 باقي الجداول (اختياري):")
                for table in tables:
                    if table in set(critical):
                        continue
                    try:
                        count = _count_table(table)
                        print(f" - {table:<30} : {count} rows")
                    except Exception as e:
                        print(f" - {table:<30} : Error getting count ({e})")
                
                print("-" * 60)
                
                # Check specific critical data
                if 'users' in tables:
                    print("\n👤 Users Check:")
                    try:
                        users_count = _count_table("users")
                        print(f"   - Total users: {users_count}")
                        users = conn.execute(text('SELECT id, username, email, role_id FROM public."users" ORDER BY id LIMIT 20')).fetchall()
                        if not users:
                            print("   ⚠️  No users found!")
                        else:
                            for user in users:
                                print(f"   - ID: {user[0]}, User: {user[1]}, Email: {user[2]}, RoleID: {user[3]}")
                    except Exception as e:
                        print(f"   - Error reading users ({e})")
                
                if 'roles' in tables:
                    print("\n🛡️  Roles Check:")
                    try:
                        roles = conn.execute(text('SELECT id, name FROM public."roles" ORDER BY id')).fetchall()
                        for role in roles:
                            print(f"   - ID: {role[0]}, Name: {role[1]}")
                    except Exception as e:
                        print(f"   - Error reading roles ({e})")

        except SQLAlchemyError as e:
            print(f"❌ Database Error: {e}")
            print("Hint: Check your database URL in .env or config.py")

        print("="*60)

if __name__ == "__main__":
    check_database()
