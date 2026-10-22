@echo off
setlocal
cd /d "%~dp0"

set "VER=1.5"
if exist "VERSION.txt" (
  set /p VER=<VERSION.txt
)

echo ============================================
echo  CpuCore0Meter v%VER% (Full Build)
echo ============================================

call build_windows.bat
if errorlevel 1 (
  echo [ERROR] Standalone executable build failed.
  exit /b 1
)

echo.
call build_installer.bat
if errorlevel 1 (
  echo [ERROR] Installer build failed.
  exit /b 1
)

echo.
echo ============================================
echo  All builds completed successfully!
echo   Executable: dist\CpuCore0Meter.exe
echo   Installer:  dist_installer\CpuCore0Meter_Setup_v%VER%.exe
echo ============================================
endlocal
