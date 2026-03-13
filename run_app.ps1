# تشغيل التطبيق على المنفذ 5000
# التشغيل: من جذر المشروع .\run_app.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

$venvPython = Join-Path $root "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "البيئة الافتراضية غير موجودة. أنشئها أولاً:"
    Write-Host "  python -m venv venv"
    Write-Host "  .\venv\Scripts\pip.exe install -r requirements.txt"
    exit 1
}

$env:PORT = "5000"
$env:HOST = "0.0.0.0"
Write-Host "Starting server on http://127.0.0.1:5000 (first run may take 30-60s for bootstrap)..."
& $venvPython app.py
