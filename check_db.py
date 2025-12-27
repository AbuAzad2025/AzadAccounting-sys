from app import create_app, db
from sqlalchemy import text, inspect

def check_database():
    app = create_app()
    with app.app_context():
        print("="*60)
        print("🔍 DATABASE VERIFICATION TOOL | أداة فحص قاعدة البيانات")
        print("="*60)
        
        try:
            # Check connection
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✅ Database Connection: OK")
                
                # Get all tables
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"📊 Found {len(tables)} tables in database:")
                print("-" * 60)
                
                # List tables and row counts
                for table in tables:
                    try:
                        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                        print(f" - {table:<30} : {count} rows")
                    except Exception as e:
                        print(f" - {table:<30} : Error getting count ({e})")
                
                print("-" * 60)
                
                # Check specific critical data
                if 'users' in tables:
                    print("\n👤 Users Check:")
                    users = conn.execute(text("SELECT id, username, email, role_id FROM users")).fetchall()
                    if not users:
                        print("   ⚠️  No users found!")
                    else:
                        for user in users:
                            print(f"   - ID: {user[0]}, User: {user[1]}, Email: {user[2]}, RoleID: {user[3]}")
                
                if 'roles' in tables:
                    print("\n🛡️  Roles Check:")
                    roles = conn.execute(text("SELECT id, name FROM roles")).fetchall()
                    for role in roles:
                        print(f"   - ID: {role[0]}, Name: {role[1]}")

        except Exception as e:
            print(f"❌ Database Error: {e}")
            print("Hint: Check your database URL in .env or config.py")

        print("="*60)

if __name__ == "__main__":
    check_database()
