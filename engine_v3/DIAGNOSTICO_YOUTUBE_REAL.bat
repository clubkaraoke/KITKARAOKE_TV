@echo off
setlocal
cd /d "%~dp0\.."
title KITKARAOKE V3 - TEST YOUTUBE REAL
if not exist "engine\POT\READY.flag" (
  echo Falta preparar el motor PO Token. Ejecutando preparacion...
  call "%~dp00_PREPARAR_MOTOR_YOUTUBE_2026.bat"
  if errorlevel 1 exit /b 1
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0server.py" --youtube-test JaPJ3sl9DTg
) else (
  python "%~dp0server.py" --youtube-test JaPJ3sl9DTg
)
echo.
pause
