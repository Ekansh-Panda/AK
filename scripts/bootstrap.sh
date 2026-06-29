#!/usr/bin/env bash
# ============================================================================
# Miori Core — bootstrap (macOS / Linux)
# Sets up the Python backend venv and installs frontend deps.
# ============================================================================
set -euo pipefail

# Bypass tmpfs disk quota issues on Arch Linux / VMs by using disk-backed tmp
export TMPDIR=/var/tmp
export PIP_NO_CACHE_DIR=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "→ Miori Core bootstrap"
echo "  repo: $ROOT"

# ---- Backend -------------------------------------------------------------
echo ""
echo "→ Backend (services/core-api)"
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "  ✗ Python 3.11+ not found. Install it and re-run." >&2
  exit 1
fi

pushd services/core-api >/dev/null
if [ ! -d ".venv" ]; then
  "$PY" -m venv .venv
  echo "  ✓ created services/core-api/.venv"
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet --no-cache-dir -r requirements.txt
echo "  ✓ backend dependencies installed"
deactivate
popd >/dev/null

# ---- Frontends -----------------------------------------------------------
echo ""
echo "→ Frontends (apps/*)"
if command -v pnpm >/dev/null 2>&1; then
  pnpm install
  echo "  ✓ workspace dependencies installed (pnpm)"
else
  echo "  ! pnpm not found — install it (npm i -g pnpm) then run: pnpm install"
fi

echo ""
echo "✓ Bootstrap complete."
echo "  Next: scripts/run-dev.sh all   (or: api | desktop | remote)"
