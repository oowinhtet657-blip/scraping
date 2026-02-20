@echo off
echo Menutup Chrome yang sedang berjalan...
taskkill /F /IM chrome.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo Membuka Chrome dengan debug port 9222...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="C:\Users\NAGA COMPUTER\AppData\Local\Google\Chrome\User Data" ^
  --profile-directory=Default ^
  --no-first-run ^
  --no-default-browser-check

echo Chrome sedang dibuka...
timeout /t 3 /nobreak >nul

echo.
echo Sekarang jalankan: python scraper.py
echo.
pause