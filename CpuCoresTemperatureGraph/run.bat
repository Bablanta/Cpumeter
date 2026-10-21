@echo off
cd /d "%~dp0"

rem --- Auto-provision virtual environment for fresh clones on other machines ---
if not exist ".venv\Scripts\python.exe" (
  echo [CpuCore0Meter] Virtual environment not found. Creating .venv ...
  python -m venv .venv
  if errorlevel 1 (
    echo [CpuCore0Meter] ERROR: failed to create venv. Install Python 3.11+ and retry.
    pause
    exit /b 1
  )
)
".venv\Scripts\python.exe" -c "import psutil, PIL" >nul 2>&1
if errorlevel 1 (
  echo [CpuCore0Meter] Installing dependencies into .venv ...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt --disable-pip-version-check
)

".venv\Scripts\python.exe" "%~dp0CpuCoresTemperatureGraph.py" --core 0 %*