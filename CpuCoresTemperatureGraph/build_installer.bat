@echo off
setlocal
cd /d "%~dp0"

set "VER=1.5"
if exist "VERSION.txt" (
  set /p VER=<VERSION.txt
)

echo ============================================
echo  Building CpuCore0Meter v%VER% Installer
echo ============================================

if not exist "dist\CpuCore0Meter.exe" (
  echo [ERROR] dist\CpuCore0Meter.exe not found.
  echo Run build_windows.bat first to build the executable.
  exit /b 1
)

set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%SystemDrive%\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist "%ISCC%" (
  echo [ERROR] Inno Setup compiler ISCC.exe not found.
  exit /b 1
)

"%ISCC%" /DMyAppVersion=%VER% installer.iss
if errorlevel 1 (
  echo [ERROR] Inno Setup compile failed.
  exit /b 1
)

echo.
echo Done. Installer: dist_installer\CpuCore0Meter_Setup_v%VER%.exe
endlocal
