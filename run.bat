@echo off
title FlowKit
cd /d "%~dp0"

:: Force kill old sessions (port + window title)
echo [PRE] Force killing old sessions...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8100" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":9222" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq FlowKit*" >nul 2>&1

:: Start FlowKit agent server in background
echo [1/2] Starting FlowKit server (port 8100)...
start /b cmd /c "python -m agent.main"

:: Wait for agent to be ready
echo Waiting for agent to be ready...
:wait_loop
ping -n 2 127.0.0.1 >nul 2>&1
curl -s http://127.0.0.1:8100/health >nul 2>&1
if errorlevel 1 goto wait_loop
echo Agent ready.

:: Start dashboard dev server in background
echo [2/2] Starting Dashboard UI (port 5173)...
start /b cmd /c "cd dashboard && npm run dev"

:: Wait for Vite to start
echo Waiting for Dashboard...
ping -n 3 127.0.0.1 >nul 2>&1

:: Open browser windows
echo Opening browser...
start chrome --new-window "http://localhost:5173" "https://labs.google/fx/tools/flow"

echo.
echo ==============================================================
echo [SUCCESS] All services are running in this window!
echo Dashboard: http://localhost:5173  ^|  Agent: http://127.0.0.1:8100
echo.
echo Press Ctrl+C to stop all services.
echo ==============================================================
:: Keep window open
cmd /k
