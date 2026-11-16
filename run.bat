@echo off
cd /d "%~dp0"
title DobroDelo Server
echo ========================================================
echo  DobroDelo Server - http://127.0.0.1:5000
echo  Database: PostgreSQL (dobrodelo)
echo ========================================================
echo.
"%~dp0venv\Scripts\python.exe" "%~dp0run.py"
if errorlevel 1 pause
