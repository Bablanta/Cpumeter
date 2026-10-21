@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Building CpuCore0Meter v1.4 installer
echo ============================================

if not exist "dist\CpuCore0Meter.exe" echo [ERROR] dist\CpuCore0Meter.exe not found. Run build_windows.bat first. & exit /b 1

set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"

if not exist "%ISCC%" echo [ERROR] Inno Setup compiler ISCC.exe not found. & exit /b 1

"%ISCC%" installer.iss
if errorlevel 1 echo [ERROR] Inno Setup compile failed. & exit /b 1

echo.
echo Done. Installer: dist_installer\CpuCore0Meter_Setup_v1.4.exe
endlocal