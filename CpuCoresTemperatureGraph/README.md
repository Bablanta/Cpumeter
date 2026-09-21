![CpuCore0Meter banner](./.github/banner.png)

<h1 align="center">CpuCore0Meter</h1>
<p align="center">
  <strong>Ultra-Smooth Real-Time CPU Core 0 Temperature Analog Gauge &amp; Mini Desktop Widget</strong>
  <br>
  <em>Dedicated precision monitoring with 4x supersampled (SSAA) rendering, fluid 60 FPS needle physics, and customizable luxury themes.</em>
</p>

![Classic graph view plotting all eight cores of an Intel Core i7-10700K](./.github/example.png)

> This application lives in the `CpuCoresTemperatureGraph/` folder of the **Cpumeter** repository.

## Requirements

- **Windows 10/11 (64-bit)** for hardware sensor readings — the app loads the bundled
  `LibreHardwareMonitorLib.dll`, and exact per-core temperatures require the
  **sensor helper** to run as Administrator (see *Reading CPU temperatures* below).
- **Python 3.11+** — only needed when running from source; the prebuilt installer is
  self-contained.
- Python packages from `requirements.txt` (`psutil`, `pillow`, `pythonnet`, `clr_loader`,
  `matplotlib`). The `run*.bat` launchers create a local `.venv` and install them
  automatically on first start.
- **Linux**: partially supported — temperatures are read through
  `psutil.sensors_temperatures`. Autostart, the elevated helper and the installer are
  Windows-only, and macOS has no temperature backend yet (it will show no data).

## Features

- [x] **Core 0 Compact Mini Meter (default 5 cm)**: Standalone circular analog meter widget
  dedicated to CPU Core 0, rendered at 4x resolution with supersampling (SSAA) and
  LANCZOS downsampling for razor-sharp edges on any display DPI.
- [x] **Ultra-Smooth 60 FPS Needle**: Continuous spring/lerp needle physics that glides
  smoothly without abrupt jumping.
- [x] **Switchable Styles on the Fly**:
  - **Compact with Hub**: Displays central digital °C temperature and Core 0 badge.
  - **Minimalist Pure Analog**: Clean precision timepiece / aerospace instrument jewel cap
    with zero text clutter.
- [x] **Core 0 Full Gauge View**: Analog circular meter with stats cards and a real-time
  sparkline of the last 60 samples.
- [x] **Classic Graph View**: Matplotlib line chart per CPU core (`--view graph`,
  optionally `--core all`).
- [x] **Hardware Sensor Reading**: `LibreHardwareMonitorLib.dll` on Windows, WMI thermal
  zone fallback, `psutil` on Linux.
- [x] **Interactive Desktop Controls** (compact mini meter):
  - Click & drag anywhere to position the widget on the desktop.
  - Right-click context menu to change style, theme, diameter, transparency, and
    Always-on-Top — plus autostart, sensor service, log folder, and view switching.
  - Double-click to instantly toggle between Compact with Hub and Minimalist Pure Analog.
  - Mouse wheel to zoom/resize (20 px per notch, clamped between 130 px and 290 px).
- [x] **Built-in Luxury Themes**: Dark Luxury, Cyberpunk (labelled "Cyberpunk HUD" in the
  mini meter and "Cyberpunk Neon" in the full gauge), Minimalist Silver, Sport Racing.

## Usage

### 1. Run Compact Mini Meter (default 5 cm)
```bat
run_compact.bat
```
Or with Python:
```bat
python CpuCoresTemperatureGraph.py --view compact --core 0
```
Or start directly in minimalist pure analog mode:
```bat
python CpuCoresTemperatureGraph.py --view compact --style minimal
```

### 2. Run Default Full Core 0 Gauge
```bat
run.bat
```
Or:
```bat
python CpuCoresTemperatureGraph.py --view gauge --core 0
```

### 3. Run Classic Multi-Core Graph
```bat
python CpuCoresTemperatureGraph.py --view graph --core all
```

### 4. Choose Theme
```bat
rem Dark Luxury (default)
python CpuCoresTemperatureGraph.py --view compact --theme dark_luxury

rem Cyberpunk
python CpuCoresTemperatureGraph.py --view compact --theme cyberpunk

rem Minimalist Silver
python CpuCoresTemperatureGraph.py --view compact --theme minimal_silver

rem Sport Racing
python CpuCoresTemperatureGraph.py --view compact --theme sport_racing
```

### 5. Pin Always on Top
```bat
python CpuCoresTemperatureGraph.py --view compact --top
```

> `run.bat` and `run_compact.bat` auto-provision the environment: they create `.venv` and
> run `pip install -r requirements.txt` when needed, so a fresh clone starts with a single
> command. Every flag is listed in the *Command-Line Reference* below.

## Desktop Controls

Compact mini meter (the full gauge supports dragging plus its own right-click menu):

- **Drag**: Left-click and hold anywhere on the widget to move it.
- **Context Menu**: Right-click to switch style (Compact with Hub vs Minimalist Pure
  Analog), theme, diameter ("Ukuran (Diameter)": Mini 4 cm/150 px, Kecil 5 cm/190 px,
  Sedang 6.5 cm/240 px), window transparency ("Transparansi Jendela": 100 %, 90 %, 80 %,
  plus "Lingkaran Melayang (Transparent)"), "Selalu di Atas (Always On Top)", autostart
  ("Buka Otomatis saat Mesin Dinyalakan"), "Mulai Sensor Service (Admin)",
  "Buka Folder Log Sensor", or "Buka Tampilan Standar (Full Gauge)".
- **Double-Click**: Quickly switch between Compact with Digital Hub and Minimalist Pure
  Analog.
- **Mouse Wheel**: Quick adjust diameter.

The full gauge menu additionally offers "🎨 Themes", "🔄 Reset Min / Max",
"⏱ Buka Mini Gauge (5cm Compact)" and "❌ Exit".

## Installation on Other Windows Machines

### Option A — Prebuilt installer (recommended)

1. Download `CpuCore0Meter_Setup_v1.3.exe` from the
   [Releases page](https://github.com/Bablanta/Cpumeter/releases) and copy it to the target
   machine (USB drive, file share, ...).

   > `dist_installer/` is git-ignored, so the setup executable is never part of the
   > repository itself — maintainers attach the built file to a GitHub Release.

2. Double-click the file to run the setup wizard.
3. The wizard will automatically:
   - Install the application into `Program Files` when elevated, or into the user profile
     (`%LOCALAPPDATA%\Programs`) otherwise — no administrator rights strictly required.
   - Create Desktop and Start Menu shortcuts.
   - Provide an option to start automatically on Windows boot ("Jalankan otomatis saat
     Windows dinyalakan" → `HKCU\...\CurrentVersion\Run`).
   - Register a clean uninstaller in Windows Settings / Control Panel ("Installed Apps").

### Option B — Run from source

```bat
git clone https://github.com/Bablanta/Cpumeter.git
cd Cpumeter\CpuCoresTemperatureGraph
run_compact.bat
```

### Rebuilding the executable and the installer

```bat
build_windows.bat
```

Requires the local virtual environment (see *Requirements*) and Inno Setup 6 with
`ISCC.exe` (auto-detected in `Program Files`, `Program Files (x86)` or
`%LOCALAPPDATA%\Programs`). Outputs `dist\CpuCore0Meter.exe` and
`dist_installer\CpuCore0Meter_Setup_v1.3.exe`.

### Reading CPU temperatures ("Sensor tidak aktif" / no data)

Reading exact per-core temperatures requires the hardware monitor helper to run
**as Administrator** (it uses a low-level kernel driver). The GUI itself always
runs normally, so it never interrupts your workflow:

- If no temperature is shown, right-click the gauge and choose
  **"Mulai Sensor Service (Admin)"** — confirm the UAC prompt once. Readings
  flow back to the widget immediately.
- On every boot, the app starts quietly; start the Sensor Service again the
  same way (right-click menu) when you want temperature data inside the widget.

### Troubleshooting

- **App opens but shows no temperature**: the compact hub shows `--°` and `SENSOR OFF`,
  the full gauge shows `NO SENSOR` plus a red hint banner. Start the Sensor Service from
  the right-click menu ("Mulai Sensor Service (Admin)"), or run the app as Administrator.
- **Diagnostic log**: all sensor initialization failures are written to
  `%LOCALAPPDATA%\CpuCore0Meter\cpumeter.log` (open it from the right-click
  menu → "Buka Folder Log Sensor").
- **Rebuild the installer yourself**: run `build_windows.bat` (requires the
  virtual environment and Inno Setup 6 with `ISCC.exe`).
- **No data on macOS / partial data on Linux**: only Windows ships the
  LibreHardwareMonitor + helper backend; Linux falls back to `psutil`.

## Command-Line Reference

| Flag | Values / default | Description |
| --- | --- | --- |
| `--view` (alias `--plugin`) | `gauge` (default), `compact`, `mini`, `graph` | View to display; `mini` is an alias of `compact` |
| `--style` | `compact` (default), `minimal` | Mini meter style: digital hub or pure analog |
| `--core` | `0` (default), `all` | Target CPU core; `all` only affects `--view graph` |
| `--theme` | `dark_luxury` (default), `cyberpunk`, `minimal_silver`, `sport_racing` | Color theme |
| `--top` | flag | Keep the window always on top |
| `--window-size` | `600` | History length (samples) for the graph view |
| `--refresh-time` | `0.5` | Refresh interval in seconds for the graph view |
| `-v`, `--verbose` | flag | Also write log output to stderr |
| `--enable-autostart` / `--disable-autostart` / `--status-autostart` | flag | Manage the Windows boot entry without opening the GUI |

## How It Works

- The GUI always runs **unelevated**. When it detects that it is not elevated it talks to a
  hidden **sensor helper** (the same executable, started with `--sensor-helper` through
  `ShellExecuteW("runas")`) over loopback TCP `127.0.0.1:40123`. Only one helper instance
  can run at a time (named mutex) and it shuts itself down after 10 minutes without
  requests.
- When the app itself is elevated, it reads the hardware monitor in-process instead.
- Temperature sources, in order: LibreHardwareMonitor (`Core #n` plus `Distance to TjMax`),
  AMD-style fallback labels (Tctl/Tdie/CCD/Package), then the WMI
  `MSAcpi_ThermalZoneTemperature` thermal zone. Linux uses `psutil`.
- Logs are appended to `%LOCALAPPDATA%\CpuCore0Meter\cpumeter.log`.
- Theme, diameter, transparency and always-on-top are applied at runtime but are
  **not persisted**; only the autostart registry entry survives a restart.

## License

No `LICENSE` file has been added to this repository yet — choose one (for example MIT or
Apache-2.0) and add it in the repository root before redistributing this project.

### Third-party components

- **LibreHardwareMonitorLib.dll** — © LibreHardwareMonitor contributors, licensed under the
  **Mozilla Public License 2.0 (MPL-2.0)**; upstream:
  <https://github.com/LibreHardwareMonitor/LibreHardwareMonitor>.
- Python dependencies (`psutil`, `Pillow`, `pythonnet`, `clr_loader`, `matplotlib`) remain
  under their respective licenses.
