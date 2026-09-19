# CpuMeter & Core 0 Gauge Rules

Guidelines for running and monitoring the CPU Core 0 Temperature Gauge application.

## Execution Rules
- Always use the virtual environment Python interpreter at `E:\Cpumeter\CpuCoresTemperatureGraph\.venv\Scripts\python.exe`.
- Use the launcher `run.bat` or `CpuCoresTemperatureGraph.py` to start the application.
- The default display is `gauge` focusing exclusively on `Core 0` (no wall clock time hands).
- To switch views:
  - Core 0 Circular Gauge: `python CpuCoresTemperatureGraph.py --view gauge --core 0`
  - Core 0 Compact Mini Meter (5cm 4K): `python CpuCoresTemperatureGraph.py --view compact --core 0`
  - Core 0 Line Chart: `python CpuCoresTemperatureGraph.py --view graph --core 0`
- Themes supported:
  - `dark_luxury` (default slate/gold gauge dial)
  - `cyberpunk` (neon cyan & magenta HUD)
  - `minimal_silver` (clean brushed aluminum)
  - `sport_racing` (matte carbon & racing red tachometer)
