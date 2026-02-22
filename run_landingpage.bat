@echo off
cls
title Facebook Group Scraper - Web App

echo.
echo ============================================================
echo.
echo  FACEBOOK GROUP SCRAPER - WEB LANDING PAGE
echo.
echo ============================================================
echo.
echo Merah = ERROR, Kuning = WARNING, Hijau = SUCCESS
echo.
echo ============================================================
echo.

REM Check if venv exists
if not exist venv (
    echo [!] Virtual environment tidak ditemukan.
    echo [*] Membuat virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install requirements
echo [*] Menginstall dependencies...
pip install -r requirements-app.txt -q

REM Create output folder
if not exist output (
    mkdir output
)

REM Start Flask app
echo.
echo [✓] Semua siap! Flask app dimulai...
echo.
echo ============================================================
echo.
echo  Buka browser: http://localhost:5000
echo.
echo ============================================================
echo.

python app.py

pause
