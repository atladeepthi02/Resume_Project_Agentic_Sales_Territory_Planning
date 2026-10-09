#!/usr/bin/env bash
#
# Start the Next.js frontend on http://localhost:3000.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR/frontend"

if [ ! -d "node_modules" ]; then
  echo "node_modules not found - installing frontend dependencies..."
  npm install
fi

# Point the browser at the backend (overridable). Shell env wins over .env.local.
API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
export NEXT_PUBLIC_API_URL="$API_URL"

echo "Starting frontend on http://localhost:3000  |  API: $API_URL"
exec npm run dev
