@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Running fix_account_types (dry-run first)...
python سكريبتات\fix_account_types_standalone.py --dry-run
if errorlevel 1 (
    echo Script failed.
    pause
    exit /b 1
)
echo.
set /p APPLY="Apply fix for real? (y/N): "
if /i "%APPLY%"=="y" (
    python سكريبتات\fix_account_types_standalone.py
    echo Done.
) else (
    echo Skipped. Run without --dry-run to apply.
)
pause
