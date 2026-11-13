@echo off
echo ==========================================
echo   JARVIS Ultimate - Clean Build
echo ==========================================
echo.

echo £´°»µ½¸µ build °µ°º¾²...
if exist "build\dist" rmdir /S /Q build\dist
if exist "build\build" rmdir /S /Q build\build
if exist "dist" rmdir /S /Q dist
if exist "*.spec" del /Q *.spec

echo £´°»µ½¸µ º° Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /S /Q "%%d"
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /S /Q "%%d"

echo £´°»µ½¸µ ²µ¼µ½½ °¹»¾²...
del /Q *.pyc 2>nul
del /Q *.pyo 2>nul

echo.
echo ¸º° ·°²µµ½°!
pause
