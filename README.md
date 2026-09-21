![CpuCore0Meter banner](CpuCoresTemperatureGraph/.github/banner.png)

# Cpumeter — CpuCore0Meter

Ultra-smooth real-time CPU **Core 0** temperature monitoring for Windows: a 5 cm analog
desktop widget, a full analog gauge, and a classic per-core graph.

> Source code, full documentation, launchers and build scripts live in
> [`CpuCoresTemperatureGraph/`](CpuCoresTemperatureGraph/README.md).

## Highlights

- 5 cm borderless mini meter with 4x supersampled (SSAA) rendering and a 60 FPS
  spring/lerp needle.
- Switchable styles (digital hub / pure analog), four themes, three diameters, window
  transparency and always-on-top — all from the right-click menu.
- Full analog gauge with stats cards and a sparkline, plus a Matplotlib graph view
  (`--view graph --core all`).
- Exact per-core temperatures via `LibreHardwareMonitorLib.dll`, read by an elevated
  helper process over loopback TCP so the GUI itself always stays unelevated.

## Quick start

```bat
git clone https://github.com/Bablanta/Cpumeter.git
cd Cpumeter\CpuCoresTemperatureGraph
run_compact.bat
```

The launcher creates `.venv` and installs `requirements.txt` automatically. See
[`CpuCoresTemperatureGraph/README.md`](CpuCoresTemperatureGraph/README.md) for the full
usage guide, CLI reference, installer instructions and troubleshooting.

## License

No `LICENSE` file has been added to this repository yet — choose one before
redistributing. The bundled `LibreHardwareMonitorLib.dll` is licensed under MPL-2.0.
