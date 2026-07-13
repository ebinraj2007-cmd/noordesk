@echo off
REM NoorDesk launcher (Windows). Creates a venv, installs deps, opens dashboard.
cd /d "%~dp0"

if not exist ".venv" (
  echo Setting up NoorDesk ^(first run^)...
  python -m venv .venv
  call .venv\Scripts\python -m pip install --upgrade pip
  call .venv\Scripts\pip install -r requirements.txt
)

echo Starting NoorDesk at http://127.0.0.1:8000
start "" http://127.0.0.1:8000
REM Bind to localhost only — never expose on the network.
call .venv\Scripts\uvicorn webapp.main:app --host 127.0.0.1 --port 8000
