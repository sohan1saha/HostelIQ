@echo off
title HostelIQ - Simulate Daily Maintenance Tickets
cd /d "%~dp0"

echo ==================================================
echo   HostelIQ - Maintenance Grievance Simulator
echo ==================================================
python simulate_tickets.py

echo.
pause
