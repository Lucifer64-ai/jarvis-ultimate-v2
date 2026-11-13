@echo off
chcp 65001 >nul
echo ==========================================
echo   JARVIS Ultimate - Build Script
echo ==========================================
echo.

REM ¾²µº° Python
echo [1/5] ¾²µº° Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ¸±º°: Python ½µ °½¾²»µ½!
    pause
    exit /b 1
)
echo OK

REM ¡¾·´°½¸µ ²¸°»½¾³¾ ¾º¶µ½¸
echo [2/5] ¡¾·´°½¸µ ²¸°»½¾³¾ ¾º¶µ½¸...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
echo OK

REM £°½¾²º° ·°²¸¸¼¾µ¹
echo [3/5] £°½¾²º° ·°²¸¸¼¾µ¹...
pip install -r requirements.txt
echo OK

REM ¡±¾º° exe
echo [4/5] ¡±¾º° JARVIS.exe...
cd build
pyinstaller jarvis.spec --clean --noconfirm
if errorlevel 1 (
    echo ¸±º° ±¾º¸!
    pause
    exit /b 1
)
cd ..
echo OK

REM ¾¿¸¾²°½¸µ º¾½¸³°¸¸
echo [5/5] ¾¿¸¾²°½¸µ °¹»¾²...
if not exist "dist\JARVIS" mkdir dist\JARVIS
copy config.json dist\JARVIS\
copy .env.example dist\JARVIS\.env
if exist "assets" (
    xcopy /E /I /Y assets dist\JARVIS\assets
)
echo OK

echo.
echo ==========================================
echo   ¡±¾º° ·°²µµ½° ¿µ½¾!
echo   ¤°¹»: dist\JARVIS\JARVIS.exe
echo ==========================================
pause
