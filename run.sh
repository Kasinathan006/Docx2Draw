#!/usr/bin/env bash
# Doc2Draw AI — one-command dev launcher (macOS / Linux / Git Bash)
#
#   ./run.sh            # start backend (:8000) + frontend (:3000)
#   ./run.sh backend    # backend only
#   ./run.sh frontend   # frontend only
#
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-all}"

start_backend() {
  echo "Starting Doc2Draw API on http://localhost:8000 ..."
  ( cd "$ROOT" && python -m uvicorn backend.app.main:app --reload --port 8000 ) &
}

start_frontend() {
  echo "Starting Doc2Draw web app on http://localhost:3000 ..."
  if [ ! -d "$ROOT/frontend/node_modules" ]; then
    echo "Installing frontend dependencies (first run)..."
    ( cd "$ROOT/frontend" && npm install )
  fi
  ( cd "$ROOT/frontend" && npm run dev ) &
}

case "$MODE" in
  backend)  start_backend ;;
  frontend) start_frontend ;;
  all)      start_backend; start_frontend ;;
  *) echo "usage: ./run.sh [backend|frontend|all]"; exit 1 ;;
esac

echo ""
echo "Doc2Draw AI is starting. Open http://localhost:3000 in your browser."
wait
