#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  echo "Run ./scripts/setup_libreyolo.sh first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q -r src/backend/requirements.txt

PYTHONPATH=src uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

python -m http.server 8080 --directory src/frontend &
FRONTEND_PID=$!

cleanup() {
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "Backend:  http://127.0.0.1:8000/docs"
echo "Frontend: http://127.0.0.1:8080"
wait
