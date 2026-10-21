# -*- coding: utf-8 -*-
"""
Windows Autostart Manager for CpuCore0Meter.
Configures the app to run automatically when Windows starts via HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run.
"""

import os
import sys
import platform

APP_NAME = "CpuCore0Meter"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def is_autostart_enabled() -> bool:
    """Checks whether CpuCore0Meter is registered in Windows startup registry."""
    if platform.system() != "Windows":
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ)
        try:
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(val)
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def set_autostart(enabled: bool) -> bool:
    """
    Enables or disables autostart at Windows boot (compact mini meter only).
    Returns the new autostart state (True if enabled, False if disabled).
    """
    if platform.system() != "Windows":
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
        try:
            if enabled:
                # 1. If running as a frozen PyInstaller executable
                if getattr(sys, 'frozen', False):
                    exe_path = os.path.abspath(sys.executable)
                    cmd = f'"{exe_path}" --core 0'
                else:
                    # 2. Check installed / desktop standalone candidates
                    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
                    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
                    candidates = [
                        os.path.join(program_files, "CpuCore0Meter", "CpuCore0Meter.exe"),
                        os.path.join(user_profile, "Desktop", "CpuCore0Meter.exe"),
                        os.path.join(user_profile, "AppData", "Local", "Programs", "CpuCore0Meter", "CpuCore0Meter.exe"),
                    ]
                    found_exe = None
                    for c in candidates:
                        if os.path.exists(c):
                            found_exe = c
                            break

                    if found_exe:
                        cmd = f'"{found_exe}" --core 0'
                    else:
                        py_exe = os.path.abspath(sys.executable)
                        pyw_candidate = os.path.join(os.path.dirname(py_exe), "pythonw.exe")
                        if os.path.exists(pyw_candidate):
                            py_exe = pyw_candidate
                        script_path = os.path.abspath(sys.argv[0])
                        cmd = f'"{py_exe}" "{script_path}" --core 0'

                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                return True
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
                return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False
