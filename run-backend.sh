#!/usr/bin/env bash
#
# Start the FastAPI backend.
#   API:  http://localhost:8000
#   Docs: http://localhost:8000/docs
#
# Override the bind address/port with HOST / PORT environment variables.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Use a project-local virtualenv if one is present.
if [ -z "${VIRTUAL_ENV:-}" ] && [ -d ".venv" ]; then
  if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
  elif [ -f ".venv/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source ".venv/Scripts/activate"
  fi
fi

# Ensure `backend.app.*` imports resolve regardless of the working directory.
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
RELOAD="${RELOAD:-1}"

if [ "$RELOAD" = "1" ]; then
  RELOAD_FLAG="--reload"
else
  RELOAD_FLAG=""
fi

echo "Starting backend on http://${HOST}:${PORT} (docs: /docs)"
# shellcheck disable=SC2086
exec python -m uvicorn backend.app.main:app $RELOAD_FLAG --host "$HOST" --port "$PORT"
