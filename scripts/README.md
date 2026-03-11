# Maintenance & Utility Scripts

This directory contains various utility scripts for maintaining, fixing, and initializing the Garage Manager system.

## Priority Script

- `db_upgrade_pipeline.py` is the highest-priority script for database alignment.
- Run it first after restoring any production backup to local.
- Re-run it after every migration or data-fix update so production rollout stays consistent.
- Command: `python scripts/db_upgrade_pipeline.py`
- Before running the pipeline on production, run:
  - `python scripts/migration_precheck.py`

## Scripts

- `production_fix_script.py`: Script to fix data inconsistencies in production.
- `audit_service_gl.py`: Audits Service GL entries.
- `backup_automation.py`: Automates database backups.
- `export_schema.py`: Exports the database schema.
- `fix_branding.py`: Updates branding settings.
- `fix_sequence.py`: Fixes database sequence issues.
- `init_prod_db.py`: Initializes the production database (CAUTION: Resets DB).
- `update_roles.py`: Updates user roles and permissions.
- `check_deps.py`: Checks critical runtime Python dependencies.
- `db_upgrade_pipeline.py`: Idempotent schema/data upgrade pipeline for local and production rollout.
- `migration_precheck.py`: Non-destructive readiness checks before production migration rollout.

## Usage

Run these scripts from the project root directory using `python -m scripts.script_name` or `python scripts/script_name.py`.
Ensure your virtual environment is activated.

## Production-safe order

1. `python scripts/check_deps.py`
2. `python scripts/migration_precheck.py`
3. `python scripts/db_upgrade_pipeline.py`
4. Optional fixes (only if needed): `python scripts/production_fix_script.py`

If precheck fails, do not run the upgrade pipeline before resolving reported issues.

For full Windows runtime setup and migration, run:
`powershell -NoProfile -ExecutionPolicy Bypass -File setup_windows.ps1`
