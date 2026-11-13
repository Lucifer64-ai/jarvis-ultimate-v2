@echo off
echo ==========================================
echo   JARVIS Ultimate - Clean Build
echo ==========================================
echo.

echo £´°»µ½иµ build °µ°º¾в...
if exist "build\dist" rmdir /S /Q build\dist
if exist "build\build" rmdir /S /Q build\build
if exist "dist" rmdir /S /Q dist
if exist "*.spec" del /Q *.spec

echo £´°»µ½иµ º° Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /S /Q "%%d"
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /S /Q "%%d"

echo £´°»µ½иµ вµ¼µ½½ °¹»¾в...
del /Q *.pyc 2>nul
del /Q *.pyo 2>nul

echo.
echo иº° ·°вµµ½°!
pause
