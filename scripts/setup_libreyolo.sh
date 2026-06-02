#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIBREYOLO_DIR="$ROOT/vendor/libreyolo"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required (3.10+)." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required." >&2
  exit 1
fi

if [[ ! -d "$LIBREYOLO_DIR/.git" ]]; then
  mkdir -p "$ROOT/vendor"
  git clone -b dev https://github.com/Libre-YOLO/libreyolo.git "$LIBREYOLO_DIR"
fi

cd "$ROOT"
make setup
make verify

echo "Done. Activate with: source .venv/bin/activate"
