@echo off
setlocal
cd /d "%~dp0"

set "VER=1.5"
if exist "VERSION.txt" (
  set /p VER=<VERSION.txt
)

echo ============================================
echo  Building CpuCore0Meter v%VER% (Standalone Exe)
echo ============================================

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment ".venv" not found.
  echo Run:  python -m venv .venv
  echo       .venv\Scripts\pip install -r requirements.txt
  exit /b 1
)

echo [1/1] Building standalone executable with PyInstaller...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm CpuCore0Meter.spec
if errorlevel 1 (
  echo [ERROR] PyInstaller build failed.
  exit /b 1
)
if not exist "dist\CpuCore0Meter.exe" (
  echo [ERROR] dist\CpuCore0Meter.exe not produced.
  exit /b 1
)

echo.
echo Done. Standalone exe ready at: dist\CpuCore0Meter.exe
echo (Installer is NOT built here. Run build_installer.bat to build the installer.)

endlocal
