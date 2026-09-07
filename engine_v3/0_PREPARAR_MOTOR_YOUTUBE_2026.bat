@echo off
setlocal
cd /d "%~dp0\.."
title KITKARAOKE - PREPARAR MOTOR YOUTUBE 2026
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_pot.ps1"
if errorlevel 1 (
  echo.
  echo ERROR: no se pudo preparar el motor PO Token.
  echo Revisa el mensaje de arriba y enviame una captura.
  pause
  exit /b 1
)
echo.
pause
exit /b 0
