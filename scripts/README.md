# Maintenance & Utility Scripts

This directory contains various utility scripts for maintaining, fixing, and initializing the Garage Manager system.

## Scripts

- `production_fix_script.py`: Script to fix data inconsistencies in production.
- `audit_service_gl.py`: Audits Service GL entries.
- `backup_automation.py`: Automates database backups.
- `export_schema.py`: Exports the database schema.
- `fix_branding.py`: Updates branding settings.
- `fix_sequence.py`: Fixes database sequence issues.
- `init_prod_db.py`: Initializes the production database (CAUTION: Resets DB).
- `update_roles.py`: Updates user roles and permissions.

## Usage

Run these scripts from the project root directory using `python -m scripts.script_name` or `python scripts/script_name.py`.
Ensure your virtual environment is activated.
