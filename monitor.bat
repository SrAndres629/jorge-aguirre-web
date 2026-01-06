@echo off
SETLOCAL EnableExtensions

echo ========================================================
echo 🚀 EVOLUTION API GOD MONITOR (V4 - SUPABASE EDITION)
echo ========================================================

:: 1. Check if Docker is running
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not running! Please start Docker Desktop.
    pause
    EXIT /B 1
)

:: 2. Check if Evolution MCP Container is running
docker ps --format "{{.Names}}" | findstr "evolution_mcp_server" >nul
IF %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Container 'evolution_mcp_server' is not running.
    echo 🔄 Attempting to start service...
    docker-compose up -d evolution_mcp_server
    timeout /t 5 >nul
)

:: 3. Sync latest monitor script
echo 📦 Syncing latest monitor code (V4)...
docker cp scripts/maintenance/evolution_monitor_v4.py evolution_mcp_server:/app/scripts/maintenance/evolution_monitor_v4.py

:: 4. Launch Monitor
echo 🖥️  Opening Interface...
echo.
docker exec -it -e EVOLUTION_API_URL=http://evolution_api:8080 evolution_mcp_server python scripts/maintenance/evolution_monitor_v4.py

:: 5. Pause on exit
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Monitor exited with error.
    pause
)
