@echo off
REM =================================================================
REM CLEANUP.BAT - Script de Limpieza de Residuos
REM Jorge Aguirre Flores Web
REM =================================================================

echo 🧹 Iniciando limpieza de residuos...

REM Root residues
if exist input.css del /f /q input.css
if exist output.css del /f /q output.css
if exist qr_code.png move qr_code.png archive\

REM Old Dockerfiles
if exist core\Dockerfile del /f /q core\Dockerfile

REM Audit files to archive
if exist CREDENTIALS_AND_SECRETS.md move CREDENTIALS_AND_SECRETS.md archive\
if exist DOCKER_INFRA_AUDIT.md move DOCKER_INFRA_AUDIT.md archive\
if exist DOCKER_OPTIMIZATION_AUDIT.md move DOCKER_OPTIMIZATION_AUDIT.md archive\
if exist GIT_PRIVACY_AUDIT.md move GIT_PRIVACY_AUDIT.md archive\
if exist KEEP_ALIVE_AUDIT.md move KEEP_ALIVE_AUDIT.md archive\
if exist META_COST_OPTIMIZATION_AUDIT.md move META_COST_OPTIMIZATION_AUDIT.md archive\
if exist META_SECURITY_AUDIT.md move META_SECURITY_AUDIT.md archive\
if exist META_TRACKING_AUDIT.md move META_TRACKING_AUDIT.md archive\
if exist PROJECT_FINAL_AUDIT.md move PROJECT_FINAL_AUDIT.md archive\
if exist PROJECT_FULL_AUDIT.md move PROJECT_FULL_AUDIT.md archive\

REM Documentation to docs/
if exist AI_README.md move AI_README.md docs\
if exist STRUCTURE.md move STRUCTURE.md docs\

REM Database residues
if exist local_fallback.db move local_fallback.db database\

REM Scripts to scripts/
if exist monitor.bat move monitor.bat scripts\
if exist run_server.bat move run_server.bat scripts\

REM Cleanup Python residues
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo ✅ Limpieza completada.
pause
