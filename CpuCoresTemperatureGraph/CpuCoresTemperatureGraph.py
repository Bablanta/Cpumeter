#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import math
import psutil
import platform
import os
import sys
import time
from collections import namedtuple


VERSION = "1.2"

CoreTemp = namedtuple('CoreTemp', ['label', 'current', 'high', 'critical'])


def get_processor_info():
    if platform.system() == "Windows":
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            name = winreg.QueryValueEx(k, "ProcessorNameString")[0].strip()
            if name:
                return name
        except Exception:
            pass
        return platform.processor()
    elif platform.system() == "Darwin":
        p = os.popen("/usr/sbin/sysctl -n machdep.cpu.brand_string")
        model = p.read().strip()
        return model
    elif platform.system() == "Linux":
        p = os.popen("cat /proc/cpuinfo")
        data = p.read().strip()
        data = [l for l in data.split('\n') if l.startswith("model name\t:")]
        if len(data) != 0:
            model = data[0].split(':',1)[1].strip()
            return model
        else:
            return ""
    return ""


class TemperatureMonitor(object):
    """Cross-platform CPU temperature monitor supporting Linux, Windows, and macOS."""

    def __init__(self):
        self.os_name = platform.system()
        self.lhm_computer = None
        self._wmi_cached_results = []
        self._wmi_last_poll = 0.0
        if self.os_name == "Windows":
            self._init_windows()

    def _init_windows(self):
        try:
            import clr
            candidates = [
                os.path.join(getattr(sys, '_MEIPASS', ''), 'LibreHardwareMonitorLib.dll'),
                os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'LibreHardwareMonitorLib.dll'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LibreHardwareMonitorLib.dll'),
                os.path.abspath('LibreHardwareMonitorLib.dll'),
            ]
            dll_path = None
            for p in candidates:
                if p and os.path.exists(p):
                    dll_path = p
                    break

            if dll_path:
                clr.AddReference(os.path.abspath(dll_path))
                from LibreHardwareMonitor.Hardware import Computer
                self.lhm_computer = Computer()
                self.lhm_computer.IsCpuEnabled = True
                self.lhm_computer.Open()
                for h in self.lhm_computer.Hardware:
                    h.Update()
        except Exception:
            self.lhm_computer = None

    def get_core_temperatures(self):
        if self.os_name == "Linux":
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if "coretemp" in temps:
                    return [c for c in temps["coretemp"] if c.label.startswith("Core")]
                for chip in ["k10temp", "zenpower", "cpu_thermal", "soc_thermal"]:
                    if chip in temps:
                        return [c for c in temps[chip]]
                for chip, sensor_list in temps.items():
                    if sensor_list:
                        return sensor_list
            return []

        elif self.os_name == "Windows" and self.lhm_computer is not None:
            tjmax_dict = {}
            temps_dict = {}
            for h in self.lhm_computer.Hardware:
                if str(h.HardwareType) == 'Cpu':
                    h.Update()
                    for s in h.Sensors:
                        if str(s.SensorType) == 'Temperature':
                            val = s.Value
                            if val is not None:
                                name = str(s.Name)
                                if "Distance to TjMax" in name:
                                    core_name = name.replace(" Distance to TjMax", "").strip()
                                    tjmax_dict[core_name] = float(val)
                                elif "Core #" in name:
                                    temps_dict[name] = float(val)

            # Fallback for AMD Ryzen or processors where sensors have alternative labels (e.g. Tctl/Tdie, CCD, Package)
            if not temps_dict:
                for h in self.lhm_computer.Hardware:
                    if str(h.HardwareType) == 'Cpu':
                        for s in h.Sensors:
                            if str(s.SensorType) == 'Temperature':
                                val = s.Value
                                if val is not None:
                                    name = str(s.Name)
                                    if "Distance to TjMax" not in name:
                                        temps_dict[name] = float(val)

            results = []
            for idx, core_name in enumerate(sorted(temps_dict.keys(), key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))):
                cur = temps_dict[core_name]
                dist = tjmax_dict.get(core_name, 50.0)
                crit = cur + dist if dist else 100.0
                high = crit - 15.0
                label = f"Core {idx}"
                results.append(CoreTemp(label=label, current=cur, high=high, critical=crit))
            return results

        elif self.os_name == "Windows":
            now = time.time()
            if self._wmi_cached_results and (now - self._wmi_last_poll < 2.0):
                return self._wmi_cached_results

            # Prevent spawning PowerShell repeatedly if WMI fails or returns nothing
            if not self._wmi_cached_results and (now - self._wmi_last_poll < 5.0):
                return []

            self._wmi_last_poll = now

            # Fallback to WMI thermal zone without EVER popping a console window
            try:
                import subprocess, json
                cmd = 'Get-CimInstance -Namespace "root/wmi" -ClassName "MSAcpi_ThermalZoneTemperature" -ErrorAction SilentlyContinue | Select-Object InstanceName, CurrentTemperature, CriticalTripPoint | ConvertTo-Json'
                
                # Critical: Prevent any console or PowerShell window from flashing/opening
                creationflags = 0x08000000  # CREATE_NO_WINDOW
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                out = subprocess.check_output(
                    ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                    text=True,
                    creationflags=creationflags,
                    startupinfo=startupinfo,
                    timeout=2
                )
                data = json.loads(out)
                if isinstance(data, dict):
                    data = [data]
                results = []
                for item in data:
                    cur = (float(item["CurrentTemperature"]) - 2732) / 10.0
                    crit = (float(item.get("CriticalTripPoint", 3922)) - 2732) / 10.0
                    label = item.get("InstanceName", "CPU Zone")
                    results.append(CoreTemp(label=label, current=cur, high=crit-15.0, critical=crit))
                if results:
                    self._wmi_cached_results = results
                return self._wmi_cached_results
            except Exception:
                return self._wmi_cached_results or []

        return []

    def close(self):
        if self.lhm_computer is not None:
            try:
                self.lhm_computer.Close()
            except Exception:
                pass


def parseArgs():
    parser = argparse.ArgumentParser(add_help=True, description="CPU Core Temperature Monitor & Gauge")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode. (default: False).")
    parser.add_argument(
        "--view", "--plugin",
        dest="view",
        choices=["gauge", "compact", "mini", "graph"],
        default="gauge",
        help="Display view to use: 'gauge' (full circular gauge), 'compact'/'mini' (smooth 4K 5cm mini analog meter), or 'graph' (line chart)."
    )
    parser.add_argument(
        "--style",
        dest="style",
        choices=["compact", "minimal"],
        default="compact",
        help="Display style for mini gauge: 'compact' (with digital hub) or 'minimal' (pure analog precision meter)."
    )
    parser.add_argument(
        "--core",
        dest="core",
        default="0",
        help="Target CPU core to display, e.g. 0 for Core 0 (default: 0). Use 'all' to show all cores in graph mode."
    )
    parser.add_argument(
        "--theme",
        dest="theme",
        choices=["dark_luxury", "cyberpunk", "minimal_silver", "sport_racing"],
        default="dark_luxury",
        help="Color theme: 'dark_luxury', 'cyberpunk', 'minimal_silver', or 'sport_racing' (default: dark_luxury)."
    )
    parser.add_argument("--top", action="store_true", help="Keep window always on top.")
    parser.add_argument("--enable-autostart", action="store_true", help="Enable automatic startup on Windows boot.")
    parser.add_argument("--disable-autostart", action="store_true", help="Disable automatic startup on Windows boot.")
    parser.add_argument("--status-autostart", action="store_true", help="Check whether automatic startup is enabled.")
    parser.add_argument("--window-size", type=int, default=600, help="Window history size for graph view.")
    parser.add_argument("--refresh-time", type=float, default=0.5, help="Refresh time in seconds.")

    options = parser.parse_args()
    return options


if __name__ == '__main__':
    options = parseArgs()

    if options.enable_autostart:
        from plugins.autostart import set_autostart
        set_autostart(True, view=options.view)
        print(f"CpuCore0Meter autostart enabled successfully for view: '{options.view}'")
        sys.exit(0)
    elif options.disable_autostart:
        from plugins.autostart import set_autostart
        set_autostart(False)
        print("CpuCore0Meter autostart disabled successfully.")
        sys.exit(0)
    elif options.status_autostart:
        from plugins.autostart import is_autostart_enabled
        print(f"CpuCore0Meter autostart status: {'ENABLED' if is_autostart_enabled() else 'DISABLED'}")
        sys.exit(0)

    sensor_monitor = TemperatureMonitor()

    current_view = options.view
    try:
        while current_view:
            if current_view in ("compact", "mini"):
                from plugins.compact_gauge import CompactGaugePlugin
                plugin = CompactGaugePlugin(sensor_monitor, get_processor_info, options)
            elif current_view == "graph":
                from plugins.graph_view import GraphViewPlugin
                plugin = GraphViewPlugin(sensor_monitor, get_processor_info, options)
            else:
                from plugins.gauge_view import GaugeViewPlugin
                plugin = GaugeViewPlugin(sensor_monitor, get_processor_info, options)

            plugin.run()
            current_view = getattr(plugin, 'next_view', None)
    finally:
        sensor_monitor.close()
