![](./.github/banner.png)

<h1 align="center">CpuCore0Meter</h1>
<p align="center">
  <strong>Ultra-Smooth Real-Time CPU Core 0 Temperature Analog Gauge & Mini Desktop Widget</strong>
  <br>
  <em>Dedicated precision monitoring with 4K SSAA rendering, fluid 60 FPS needle physics, and customizable luxury themes.</em>
</p>

## Features

- [x] **Core 0 Compact Mini Meter (5cm 4K)**: Standalone 5cm diameter circular analog meter widget dedicated exclusively to CPU Core 0, rendered with 4x supersampling (SSAA) for razor-sharp 4K clarity.
- [x] **Ultra-Smooth 60 FPS Needle**: Continuous spring/lerp needle physics that glides smoothly without abrupt jumping.
- [x] **Switchable Styles on the Fly**:
  - **Compact with Hub**: Displays central digital °C temperature and Core 0 badge.
  - **Minimalist Pure Analog**: Clean precision timepiece / aerospace instrument jewel cap with zero text clutter.
- [x] **Core 0 Full Gauge View**: Analog circular meter with stats cards and 60-second real-time sparkline history.
- [x] **Cross-Platform Support**: High-precision hardware sensor reading via `LibreHardwareMonitorLib.dll` on Windows.
- [x] **Interactive Desktop Controls**:
  - Click & drag anywhere to position on desktop.
  - Right-click context menu to change style, theme, diameter (4cm, 5cm, 6.5cm), transparency, and Always-on-Top.
  - Double-click to instantly toggle between Compact with Hub and Minimalist Pure Analog.
  - Mouse wheel to zoom/resize.
- [x] **Built-in Luxury Themes**: Dark Luxury, Cyberpunk Neon, Minimalist Silver, Sport Racing.

## Usage

### 1. Run Compact Mini Meter (5cm 4K)
```bash
./run_compact.bat
```
Or with Python:
```bash
python CpuCoresTemperatureGraph.py --view compact --core 0
```
Or start directly in minimalist pure analog mode:
```bash
python CpuCoresTemperatureGraph.py --view compact --style minimal
```

### 2. Run Default Full Core 0 Gauge
```bash
./run.bat
```
Or:
```bash
python CpuCoresTemperatureGraph.py --view gauge --core 0
```

### 3. Choose Theme
```bash
# Dark Luxury (Default)
python CpuCoresTemperatureGraph.py --view compact --theme dark_luxury

# Cyberpunk Neon
python CpuCoresTemperatureGraph.py --view compact --theme cyberpunk

# Minimalist Silver
python CpuCoresTemperatureGraph.py --view compact --theme minimal_silver

# Sport Racing
python CpuCoresTemperatureGraph.py --view compact --theme sport_racing
```

### 4. Pin Always on Top
```bash
python CpuCoresTemperatureGraph.py --view compact --top
```

## Desktop Controls
- **Drag**: Left-click and hold anywhere on the gauge to move the widget.
- **Context Menu**: Right-click to switch style (Compact with Hub vs Minimalist Pure Analog), theme, diameter, transparency, Always-on-Top, or switch to Full Gauge.
- **Double-Click**: Quickly switch between Compact with Digital Hub and Minimalist Pure Analog.
- **Mouse Wheel**: Quick adjust diameter.

## Installation on Other Windows Machines

To install this application on any other Windows computer:

1. Copy `CpuCore0Meter_Setup_v1.2.exe` (located in `dist_installer/` or on the Desktop) to a USB drive or transfer it to the target machine.
2. Double-click `CpuCore0Meter_Setup_v1.2.exe` to run the setup wizard.
3. The wizard will automatically:
   - Install the application into `Program Files` or user profile (no administrator rights strictly required).
   - Create Desktop and Start Menu shortcuts.
   - Provide an option to start automatically on Windows boot.
   - Register a clean uninstaller in Windows Settings / Control Panel ("Installed Apps").


