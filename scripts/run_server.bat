@echo off
REM ===================================================
REM Script para iniciar el servidor de Jorge Aguirre Web
REM ===================================================

cd /d "%~dp0"
echo Activando entorno virtual...
call ..\.venv\Scripts\activate.bat

echo Iniciando servidor en http://127.0.0.1:8000
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
