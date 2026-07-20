@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-web.ps1"
echo.
echo Open: http://127.0.0.1:8092
timeout /t 3 >nul
start "" "http://127.0.0.1:8092"
