# إنشاء مجلد التبعيات (venv) وتثبيت التبعيات ثم تشغيل التطبيق على البورت 5000
# التشغيل: من جذر المشروع .\setup_venv_and_run.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

# 1) إنشاء البيئة الافتراضية إن لم تكن موجودة
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Creating venv..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

# 2) تثبيت التبعيات
Write-Host "Installing dependencies (this may take several minutes)..."
.\venv\Scripts\pip.exe install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# 3) تشغيل التطبيق
$env:PORT = "5000"
$env:HOST = "127.0.0.1"
Write-Host "Starting server on http://127.0.0.1:5000 ..."
.\venv\Scripts\python.exe app.py
