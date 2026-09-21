@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Building CpuCore0Meter v1.3
echo ============================================

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment "\.venv" not found.
  echo Run:  python -m venv .venv
  echo       .venv\Scripts\pip install -r requirements.txt
  exit /b 1
)

echo [1/2] Building standalone executable with PyInstaller...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm CpuCore0Meter.spec
if errorlevel 1 (
  echo [ERROR] PyInstaller build failed.
  exit /b 1
)
if not exist "dist\CpuCore0Meter.exe" (
  echo [ERROR] dist\CpuCore0Meter.exe not produced.
  exit /b 1
)

echo [2/2] Building Inno Setup installer...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"

if defined ISCC (
  "%ISCC%" installer.iss
  if errorlevel 1 (
    echo [ERROR] Inno Setup compile failed.
    exit /b 1
  )
  echo.
  echo Done. Installer: dist_installer\CpuCore0Meter_Setup_v1.3.exe
) else (
  echo [WARN] Inno Setup compiler not found; installer skipped.
  echo        Standalone exe ready at: dist\CpuCore0Meter.exe
)

endlocal