import os
import subprocess
import sys
from extensions import _get_pg_bin

def generate_export():
    print("🚀 Starting export process...")
    
    # 1. Find pg_dump
    pg_dump = _get_pg_bin("pg_dump")
    if not os.path.exists(pg_dump):
        print(f"❌ pg_dump not found at {pg_dump}")
        return

    print(f"✅ Found pg_dump: {pg_dump}")

    # 2. Configure environment
    env = os.environ.copy()
    env["PGPASSWORD"] = "123"
    
    output_file = "production_data.sql"
    
    # 3. Build command
    # --data-only: Only data, no schema
    # --column-inserts: Use INSERT INTO table (col1, col2) VALUES ... (safer)
    # --disable-triggers: Disable triggers during restore (only works with --data-only for plain text?) 
    # Actually --disable-triggers is for pg_restore. For plain SQL dump, we use session_replication_role.
    
    cmd = [
        pg_dump,
        "-h", "localhost",
        "-p", "5432",
        "-U", "postgres",
        "-d", "garage_db",
        "--data-only",
        "--column-inserts",
        "--no-owner",
        "--no-privileges",
        "--on-conflict-do-nothing",
        "--exclude-table=users",
        "-f", output_file
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print("✅ Export command finished successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Export failed: {e.stderr}")
        return

    # 4. Post-process to add session_replication_role
    print("🔧 Post-processing SQL file...")
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        header = """
-- AZAD GARAGE MANAGER PRODUCTION EXPORT
-- Generated Automatically
-- Excludes: users ONLY
-- 
BEGIN;

-- Disable Foreign Key checks and Triggers temporarily
SET session_replication_role = 'replica';

"""
        footer = """
-- Re-enable checks
SET session_replication_role = 'origin';

COMMIT;
"""
        
        final_content = header + content + footer
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        print(f"✅ File saved to: {os.path.abspath(output_file)}")
        print(f"📂 Size: {os.path.getsize(output_file) / 1024:.2f} KB")
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")

if __name__ == "__main__":
    generate_export()
