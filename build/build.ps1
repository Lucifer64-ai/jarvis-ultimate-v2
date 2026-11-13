# JARVIS Ultimate - PowerShell Build Script

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  JARVIS Ultimate - Build Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ¾²µº° Python
Write-Host "[1/5] ¾²µº° Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "¸±º°: Python ½µ °½¾²»µ½!" -ForegroundColor Red
    exit 1
}

# ¡¾·´°½¸µ ²¸°»½¾³¾ ¾º¶µ½¸
Write-Host "[2/5] ¡¾·´°½¸µ ²¸°»½¾³¾ ¾º¶µ½¸..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
Write-Host "OK" -ForegroundColor Green

# £°½¾²º° ·°²¸¸¼¾µ¹
Write-Host "[3/5] £°½¾²º° ·°²¸¸¼¾µ¹..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "OK" -ForegroundColor Green

# ¡±¾º° exe
Write-Host "[4/5] ¡±¾º° JARVIS.exe..." -ForegroundColor Yellow
Set-Location build
pyinstaller jarvis.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "¸±º° ±¾º¸!" -ForegroundColor Red
    exit 1
}
Set-Location ..
Write-Host "OK" -ForegroundColor Green

# ¾¿¸¾²°½¸µ º¾½¸³°¸¸
Write-Host "[5/5] ¾¿¸¾²°½¸µ °¹»¾²..." -ForegroundColor Yellow
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
Write-Host "  ¡±¾º° ·°²µµ½° ¿µ½¾!" -ForegroundColor Green
Write-Host "  ¤°¹»: dist\JARVIS\JARVIS.exe" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
