#!/usr/bin/env bash
# NoorDesk launcher (macOS / Linux). Creates a venv, installs deps, opens dashboard.
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Setting up NoorDesk (first run)…"
  python3 -m venv .venv
  ./.venv/bin/pip install --upgrade pip >/dev/null
  ./.venv/bin/pip install -r requirements.txt
fi

echo "Starting NoorDesk at http://127.0.0.1:8000"
( sleep 2; python3 -m webbrowser "http://127.0.0.1:8000" >/dev/null 2>&1 || true ) &
# Bind to localhost only — never expose on the network.
exec ./.venv/bin/uvicorn webapp.main:app --host 127.0.0.1 --port 8000
