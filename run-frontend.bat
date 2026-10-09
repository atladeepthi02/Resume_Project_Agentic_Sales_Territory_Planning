@echo off
setlocal enableextensions
cd /d "%~dp0frontend"

if not exist "node_modules" (
  echo node_modules not found - installing frontend dependencies...
  call npm install
)

if not defined NEXT_PUBLIC_API_URL set NEXT_PUBLIC_API_URL=http://localhost:8000

echo Starting frontend on http://localhost:3000  ^|  API: %NEXT_PUBLIC_API_URL%
call npm run dev

endlocal
