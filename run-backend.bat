@echo off
setlocal enableextensions
cd /d "%~dp0"

rem Pick a Python interpreter that has the backend dependencies installed.
rem Priority: project virtualenv -> py -3.12 -> py -3.11 -> python on PATH.
set "PY_EXE="
set "PY_ARGS="

if exist ".venv\Scripts\python.exe" set "PY_EXE=.venv\Scripts\python.exe"

if not defined PY_EXE (
  py -3.12 -c "import fastapi, pydantic_settings, langgraph" >nul 2>&1 && (set "PY_EXE=py" & set "PY_ARGS=-3.12")
)
if not defined PY_EXE (
  py -3.11 -c "import fastapi, pydantic_settings, langgraph" >nul 2>&1 && (set "PY_EXE=py" & set "PY_ARGS=-3.11")
)
if not defined PY_EXE (
  python -c "import fastapi, pydantic_settings, langgraph" >nul 2>&1 && set "PY_EXE=python"
)

if not defined PY_EXE (
  echo [ERROR] No Python interpreter with the backend dependencies was found.
  echo         Install them first with:  python -m pip install -r requirements.txt
  exit /b 1
)

if "%PORT%"=="" set "PORT=8000"
if "%HOST%"=="" set "HOST=127.0.0.1"

set "RELOAD_FLAG=--reload"
if "%RELOAD%"=="0" set "RELOAD_FLAG="

echo Using Python interpreter: %PY_EXE% %PY_ARGS%
echo Starting backend on http://%HOST%:%PORT%  (docs: /docs)
"%PY_EXE%" %PY_ARGS% -m uvicorn backend.app.main:app %RELOAD_FLAG% --host %HOST% --port %PORT%

endlocal
