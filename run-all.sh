#!/usr/bin/env bash
#
# Start the backend and frontend together. Ctrl+C stops both.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$ROOT_DIR/run-backend.sh" &
BACKEND_PID=$!

"$ROOT_DIR/run-frontend.sh" &
FRONTEND_PID=$!

cleanup() {
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup INT TERM

echo "Backend PID: $BACKEND_PID  |  Frontend PID: $FRONTEND_PID  (Ctrl+C to stop)"
wait
