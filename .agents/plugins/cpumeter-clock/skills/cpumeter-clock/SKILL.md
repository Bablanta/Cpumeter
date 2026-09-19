---
name: cpumeter-clock
description: >-
  Launch, monitor, and customize the real-time CPU Core 0 Temperature Gauge
  desktop widget application on Windows.
---

# CPU Core 0 Temperature Gauge Plugin Skill

This skill provides procedures for running, managing, and querying the CPU Core 0 Temperature application.

## Overview
The application monitors CPU Core 0 temperature in real time using `LibreHardwareMonitorLib.dll` and presents it in a dedicated circular analog meter gauge with a dynamic needle pointer, color temperature zones, digital readout, and live sparkline.

## Quick Launch Commands

### 1. Launch Default Core 0 Gauge
```powershell
Start-Process -FilePath "E:\Cpumeter\CpuCoresTemperatureGraph\.venv\Scripts\python.exe" -ArgumentList "E:\Cpumeter\CpuCoresTemperatureGraph\CpuCoresTemperatureGraph.py --view gauge --core 0" -WorkingDirectory "E:\Cpumeter\CpuCoresTemperatureGraph"
```
Or double-click:
```cmd
E:\Cpumeter\CpuCoresTemperatureGraph\run.bat
```

### 2. Launch Compact Mini Meter (5cm 4K Anti-Aliased)
```powershell
Start-Process -FilePath "E:\Cpumeter\CpuCoresTemperatureGraph\.venv\Scripts\python.exe" -ArgumentList "E:\Cpumeter\CpuCoresTemperatureGraph\CpuCoresTemperatureGraph.py --view compact --core 0" -WorkingDirectory "E:\Cpumeter\CpuCoresTemperatureGraph"
```
Or double-click:
```cmd
E:\Cpumeter\CpuCoresTemperatureGraph\run_compact.bat
```

### 3. Launch Core 0 Line Graph
```powershell
Start-Process -FilePath "E:\Cpumeter\CpuCoresTemperatureGraph\.venv\Scripts\python.exe" -ArgumentList "E:\Cpumeter\CpuCoresTemperatureGraph\CpuCoresTemperatureGraph.py --view graph --core 0" -WorkingDirectory "E:\Cpumeter\CpuCoresTemperatureGraph"
```

### 4. Launch Always-On-Top
```powershell
Start-Process -FilePath "E:\Cpumeter\CpuCoresTemperatureGraph\.venv\Scripts\python.exe" -ArgumentList "E:\Cpumeter\CpuCoresTemperatureGraph\CpuCoresTemperatureGraph.py --top" -WorkingDirectory "E:\Cpumeter\CpuCoresTemperatureGraph"
```

## Available Themes
- `dark_luxury`: Slate / obsidian & ice-blue luxury gauge dial.
- `cyberpunk`: Neon cyan / hot magenta HUD theme.
- `minimal_silver`: Clean brushed silver / aluminum theme.
- `sport_racing`: Matte carbon tachometer dial with racing red needle.

## In-App Controls
- **Left-Click + Drag**: Move the gauge anywhere on the desktop.
- **Right-Click**: Open context menu to switch styles (Compact with Hub vs Minimalist Pure Analog), themes, diameter (4cm, 5cm, 6.5cm), window transparency, Always-On-Top, or switch to Full Gauge view.
- **Double-Click** (in Compact view): Instantly toggle between Compact with Digital Hub and Minimalist Pure Analog.
- **Mouse Wheel** (in Compact view): Quick zoom in / out diameter.
