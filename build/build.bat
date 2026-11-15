@echo off
chcp 65001 >nul
echo ==========================================
echo   JARVIS Ultimate - Build Script
echo ==========================================
echo.

REM [1/5] Проверка Python
echo [1/5] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не найден!
    pause
    exit /b 1
)
echo OK

REM [2/5] Настройка виртуального окружения
echo [2/5] Настройка виртуального окружения...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
echo OK

REM [3/5] Установка зависимостей
echo [3/5] Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo Ошибка установки зависимостей!
    pause
    exit /b 1
)
echo OK

REM [4/5] Генерация exe
echo [4/5] Генерация JARVIS.exe...
cd build
pyinstaller jarvis.spec --clean --noconfirm
if errorlevel 1 (
    echo Ошибка генерации!
    pause
    exit /b 1
)
cd ..
echo OK

REM [5/5] Упаковка дистрибутива
echo [5/5] Упаковка дистрибутива...
if not exist "dist\JARVIS" mkdir dist\JARVIS
copy config.json dist\JARVIS\
copy .env.example dist\JARVIS\.env
if exist "assets" (
    xcopy /E /I /Y assets dist\JARVIS\assets
)
echo OK

echo.
echo ==========================================
echo   Сборка завершена успешно!
echo   Итог: dist\JARVIS\JARVIS.exe
echo ==========================================
pause