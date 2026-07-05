# Doc2Draw AI — one-command dev launcher (Windows PowerShell)
#
#   ./run.ps1            # start backend (:8000) + frontend (:3000)
#   ./run.ps1 -Backend   # start backend only
#   ./run.ps1 -Frontend  # start frontend only
#
param(
    [switch]$Backend,
    [switch]$Frontend
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$startBackend = $Backend -or (-not $Backend -and -not $Frontend)
$startFrontend = $Frontend -or (-not $Backend -and -not $Frontend)

if ($startBackend) {
    Write-Host "Starting Doc2Draw API on http://localhost:8000 ..." -ForegroundColor Magenta
    Start-Process -FilePath "python" `
        -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--reload", "--port", "8000" `
        -WorkingDirectory $root
}

if ($startFrontend) {
    Write-Host "Starting Doc2Draw web app on http://localhost:3000 ..." -ForegroundColor Magenta
    if (-not (Test-Path (Join-Path $root "frontend/node_modules"))) {
        Write-Host "Installing frontend dependencies (first run)..." -ForegroundColor Yellow
        Push-Location (Join-Path $root "frontend"); npm install; Pop-Location
    }
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" `
        -WorkingDirectory (Join-Path $root "frontend")
}

Write-Host "`nDoc2Draw AI is starting. Open http://localhost:3000 in your browser." -ForegroundColor Green
