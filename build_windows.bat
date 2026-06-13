@echo off
REM ============================================================
REM LabQC Windows Build Script
REM ============================================================
REM This script builds LabQC into a standalone Windows installer.
REM
REM Prerequisites:
REM   - Python 3.10+ with pip
REM   - Node.js (if rebuilding frontend)
REM   - Inno Setup 6 (for .exe installer)
REM
REM Usage:
REM   build_windows.bat           -- full build (frontend + exe + installer)
REM   build_windows.bat quick     -- skip frontend rebuild
REM   build_windows.bat exe       -- build exe only, skip installer
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"
set MODE=%1

echo.
echo ============================================================
echo   LabQC Windows Build
echo ============================================================
echo.

REM ---- Step 1: Install Python dependencies ----
echo [1/4] Installing Python dependencies...
pip install -r requirements.txt pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

REM ---- Step 2: Build frontend (skip in quick mode) ----
if "%MODE%"=="quick" goto skip_frontend
echo [2/4] Building frontend...
cd frontend
call npm install --silent
call npx vite build --base=/
cd ..
if errorlevel 1 (
    echo WARNING: Frontend build failed. Using existing dist/ if available.
)

:skip_frontend
if not exist "frontend\dist\index.html" (
    echo ERROR: frontend\dist\index.html not found. Run full build first.
    pause
    exit /b 1
)

REM ---- Step 3: PyInstaller ----
echo [3/4] Building standalone executable...
rmdir /s /q dist build 2>nul
pyinstaller labqc.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)
echo     Done: dist\LabQC\LabQC.exe

REM ---- Step 4: Inno Setup installer ----
if "%MODE%"=="exe" goto done
echo [4/4] Creating Windows installer...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    echo.
    echo     Done: Output\LabQC_Setup_1.0.0.exe
) else (
    echo     Skipped: Inno Setup not found (install from https://jrsoftware.org/isinfo.php)
    echo     Standalone exe is ready at dist\LabQC\LabQC.exe
)

:done
echo.
echo ============================================================
echo   Build complete!
echo   - Standalone: dist\LabQC\LabQC.exe
if exist "Output\LabQC_Setup_1.0.0.exe" (
    echo   - Installer:   Output\LabQC_Setup_1.0.0.exe
)
echo ============================================================
echo.
endlocal
pause
