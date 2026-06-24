# ============================================================================
# Miori Core - bootstrap (Windows / PowerShell)
# Sets up the Python backend venv and installs frontend deps.
# ============================================================================
$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

Write-Host "-> Miori Core bootstrap"
Write-Host "   repo: $Root"

# ---- Backend -------------------------------------------------------------
Write-Host ""
Write-Host "-> Backend (services/core-api)"

$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { $py = (Get-Command python3 -ErrorAction SilentlyContinue) }
if (-not $py) { Write-Error "Python 3.11+ not found. Install it and re-run."; exit 1 }

Push-Location services/core-api
if (-not (Test-Path ".venv")) {
  & $py.Source -m venv .venv
  Write-Host "   created services/core-api/.venv"
}
& ".\.venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
Write-Host "   backend dependencies installed"
Pop-Location

# ---- Frontends -----------------------------------------------------------
Write-Host ""
Write-Host "-> Frontends (apps/*)"
$pnpm = (Get-Command pnpm -ErrorAction SilentlyContinue)
if ($pnpm) {
  pnpm install
  Write-Host "   workspace dependencies installed (pnpm)"
} else {
  Write-Host "   ! pnpm not found - install it (npm i -g pnpm) then run: pnpm install"
}

Write-Host ""
Write-Host "Bootstrap complete."
Write-Host "  Next: scripts\run-dev.ps1 all   (or: api | desktop | remote)"
