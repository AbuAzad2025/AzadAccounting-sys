param(
    [switch]$Quick
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$pythonCandidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:ProgramFiles\Python311\python.exe",
    "$env:ProgramFiles\Python312\python.exe"
)

$pythonExe = $null
foreach ($candidate in $pythonCandidates) {
    if (Test-Path $candidate) {
        $pythonExe = $candidate
        break
    }
}

if (-not $pythonExe) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $pythonExe = $pythonCmd.Source
    }
}

if (-not $pythonExe) {
    throw "Python is missing. Install Python 3.11 and run again."
}

$sitePackages = Join-Path $root "Lib\site-packages"
if (-not (Test-Path $sitePackages)) {
    New-Item -ItemType Directory -Path $sitePackages -Force | Out-Null
}

if (-not $Quick) {
    & $pythonExe -m pip install --upgrade pip wheel setuptools --target $sitePackages
    & $pythonExe -m pip install -r (Join-Path $root "requirements.txt") --target $sitePackages
}

$env:PYTHONPATH = "$sitePackages;$root"
$env:FLASK_APP = "app:create_app"
& $pythonExe -m flask db upgrade

Write-Output "SETUP_OK"
