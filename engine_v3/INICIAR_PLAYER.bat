@echo off
cd /d "%~dp0\.."
title KITKARAOKE QUEUE PLAYER V3
if not exist "engine\POT\READY.flag" (
  echo Preparando motor YouTube 2026 por primera vez...
  call "engine_v3\0_PREPARAR_MOTOR_YOUTUBE_2026.bat"
)
start "" http://127.0.0.1:8769/?v=3.0
python engine_v3\server.py --port 8769 --no-browser
pause
