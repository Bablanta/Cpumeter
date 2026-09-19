@echo off
cd /d "%~dp0"
call "%~dp0.venv\Scripts\python.exe" "%~dp0CpuCoresTemperatureGraph.py" --view gauge --core 0 %*
