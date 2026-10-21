![CpuCore0Meter banner](CpuCoresTemperatureGraph/.github/banner.png)

# Cpumeter — CpuCore0Meter

Ultra-smooth real-time CPU temperature monitoring for Windows: a compact 4 cm
borderless mini meter (fixed size).

> Source code, full documentation, launchers and build scripts live in
> [`CpuCoresTemperatureGraph/`](CpuCoresTemperatureGraph/README.md).

## Highlights

- 4 cm borderless mini meter with 4x supersampled (SSAA) rendering and a 60 FPS
  spring/lerp needle.
- Pure analog style, three themes, system tray icon, window transparency
  and always-on-top — all from the right-click menu or tray.
- Exact per-core temperatures via `LibreHardwareMonitorLib.dll`, read by an elevated
  helper process over loopback TCP so the GUI itself always stays unelevated.

## Quick start

```bat
git clone https://github.com/Bablanta/Cpumeter.git
cd Cpumeter\CpuCoresTemperatureGraph
run.bat
```

The launcher creates `.venv` and installs `requirements.txt` automatically. See
[`CpuCoresTemperatureGraph/README.md`](CpuCoresTemperatureGraph/README.md) for the full
usage guide, CLI reference, installer instructions and troubleshooting.

## License

No `LICENSE` file has been added to this repository yet — choose one before
redistributing. The bundled `LibreHardwareMonitorLib.dll` is licensed under MPL-2.0.
