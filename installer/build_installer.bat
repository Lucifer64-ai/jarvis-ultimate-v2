@echo off
REM Build JARVIS Ultimate Installer
REM Requires: Inno Setup 6+ installed in PATH or default location

setlocal enabledelayedexpansion

echo ========================================
echo JARVIS Ultimate Installer Builder
echo ========================================
echo.

REM Check if Inno Setup is installed
set ISCC_PATH=
where iscc >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set ISCC_PATH=iscc
) else (
    REM Try default installation paths
    if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    ) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
        set ISCC_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
    ) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
        set ISCC_PATH="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    )
)

if not defined ISCC_PATH (
    echo ERROR: Inno Setup not found!
    echo.
    echo Please install Inno Setup from:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Found Inno Setup: %ISCC_PATH%
echo.

REM Check if dist folder exists
if not exist "dist\jarvis" (
    echo ERROR: dist\jarvis folder not found!
    echo.
    echo Please build the application first:
    echo   pyinstaller --name=jarvis --windowed --onefile main.py
    echo.
    pause
    exit /b 1
)

REM Create output directory
if not exist "installer\output" mkdir installer\output

REM Build installer
echo Building installer...
echo.

%ISCC_PATH% "installer\jarvis_installer.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Installer created:
    echo ========================================
    echo.
    dir /b installer\output\*.exe 2>nul
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Installer build failed!
    echo ========================================
    echo.
)

pause
