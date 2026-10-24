@echo off
title HostelIQ - Delete All Database Records
cd /d "%~dp0"

echo ==================================================
echo   HostelIQ - Complete Database Wipe / Reset
echo ==================================================
echo.
python delete_all_records.py

echo.
echo ==================================================
echo   All database records and complaints wiped clean.
echo ==================================================
echo.
pause
