@echo off
chcp 65001 >nul
echo ==========================================
echo   JARVIS Ultimate - Build Script
echo ==========================================
echo.

REM ¾вµº° Python
echo [1/5] ¾вµº° Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo агента: Python ни °½¾в»µ½!
    pause
    exit /b 1
)
echo OK

REM ¡¾·´°½иµ ви°»½¾³¾ ¾º¶µ½и
echo [2/5] ¡¾·´°½иµ ви°»½¾³¾ ¾º¶µ½и...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
echo OK

REM £°½¾вº° ·°вии¼¾µ¹
echo [3/5] £°½¾вº° ·°вии¼¾µ¹...
pip install -r requirements.txt
echo OK

REM ¡±¾º° exe
echo [4/5] ¡±¾º° JARVIS.exe...
cd build
pyinstaller jarvis.spec --clean --noconfirm
if errorlevel 1 (
    echo агента ±¾ºи!
    pause
    exit /b 1
)
cd ..
echo OK

REM ¾¿и¾в°½иµ º¾½и³°ии
echo [5/5] ¾¿и¾в°½иµ °¹»¾в...
if not exist "dist\JARVIS" mkdir dist\JARVIS
copy config.json dist\JARVIS\
copy .env.example dist\JARVIS\.env
if exist "assets" (
    xcopy /E /I /Y assets dist\JARVIS\assets
)
echo OK

echo.
echo ==========================================
echo   ¡±¾º° ·°вµµ½° ¿µ½¾!
echo   ¤°¹»: dist\JARVIS\JARVIS.exe
echo ==========================================
pause
