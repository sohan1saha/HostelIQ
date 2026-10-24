@echo off
title HostelIQ - Add Resident Students
cd /d "%~dp0"

echo ==================================================
echo   HostelIQ - Resident Population
echo ==================================================
python add_students.py

echo.
pause
