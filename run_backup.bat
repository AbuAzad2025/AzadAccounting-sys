@echo off
cd /d "D:\karaj\garage_manager_project\garage_manager"
call .venv\Scripts\activate
python manage_backup.py backup
