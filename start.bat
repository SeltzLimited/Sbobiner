@echo off
cd /d "%~dp0"
title Sbobiner
if not exist ".venv\Scripts\python.exe" (
  echo Sbobiner non e' ancora installato: fai doppio click su setup.bat.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" app.py
if errorlevel 1 pause
