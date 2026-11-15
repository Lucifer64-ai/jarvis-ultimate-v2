# JARVIS Ultimate - PowerShell Build Script

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  JARVIS Ultimate - Build Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# [1/5] Проверка Python
Write-Host "[1/5] Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Ошибка: Python не найден!" -ForegroundColor Red
    exit 1
}

# [2/5] Настройка виртуального окружения
Write-Host "[2/5] Настройка виртуального окружения..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
Write-Host "OK" -ForegroundColor Green

# [3/5] Установка зависимостей
Write-Host "[3/5] Установка зависимостей..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка установки зависимостей!" -ForegroundColor Red
    exit 1
}
Write-Host "OK" -ForegroundColor Green

# [4/5] Генерация exe
Write-Host "[4/5] Генерация JARVIS.exe..." -ForegroundColor Yellow
Set-Location build
pyinstaller jarvis.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка генерации!" -ForegroundColor Red
    exit 1
}
Set-Location ..
Write-Host "OK" -ForegroundColor Green

# [5/5] Упаковка дистрибутива
Write-Host "[5/5] Упаковка дистрибутива..." -ForegroundColor Yellow
if (-not (Test-Path "dist\JARVIS")) {
    New-Item -ItemType Directory -Path "dist\JARVIS" -Force
}
Copy-Item config.json dist\JARVIS\
Copy-Item .env.example dist\JARVIS\.env
if (Test-Path "assets") {
    Copy-Item -Recurse -Force assets dist\JARVIS\assets
}
Write-Host "OK" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Сборка завершена успешно!" -ForegroundColor Green
Write-Host "  Итог: dist\JARVIS\JARVIS.exe" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green