# -*- coding: utf-8 -*-
"""
Elevated sensor helper process (internal use only).

Runs in an administrator context, initializes the hardware monitor (LHM) and
serves CPU temperature readings to the unelevated GUI over loopback TCP.

Protocol: client sends a single line "GET\\n" and receives one JSON payload
terminated by "\\n". Sending "QUIT\\n" shuts the helper down.

This helper is the SAME executable as the GUI, launched with `--sensor-helper`
via ShellExecuteW(runas), so no toolbar/console window is shown.
"""

import ctypes
import json
import logging
import socket
import time

from .sensor_shared import SENSOR_PORT, SENSOR_IDLE_TIMEOUT, core_temp_to_json

logger = logging.getLogger(__name__)

MUTEX_NAME = "Local\\CpuCore0Meter_SensorHelper"


def _single_instance():
    """Returns True if this is the only helper instance (creates named mutex)."""
    try:
        handle = ctypes.windll.kernel32.CreateMutexW(
            None, False, MUTEX_NAME
        )
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            ctypes.windll.kernel32.CloseHandle(handle)
            return False
        return True
    except Exception:
        return True


def build_payload(monitor, get_processor_info):
    try:
        cores = monitor.get_core_temperatures()
        proc = ""
        try:
            proc = get_processor_info()
        except Exception:
            pass
        return {
            "ok": True,
            "source": getattr(monitor, "sensor_source", "unknown"),
            "error": getattr(monitor, "last_error", None),
            "proc": proc,
            "cores": [core_temp_to_json(c) for c in cores],
        }
    except Exception as e:
        logger.exception("sensor read failed")
        return {
            "ok": False,
            "source": getattr(monitor, "sensor_source", "unknown"),
            "error": str(e),
            "proc": "",
            "cores": [],
        }


def run_sensor_helper(monitor, get_processor_info):
    """Serve sensor readings over loopback TCP until QUIT or idle timeout."""
    if not _single_instance():
        logger.info("Sensor helper already running; exiting.")
        return 0

    logger.info("Sensor helper started (elevated) on 127.0.0.1:%d", SENSOR_PORT)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("127.0.0.1", SENSOR_PORT))
    except OSError as e:
        logger.error("helper bind failed (port in use?): %s", e)
        return 0
    server.listen(2)
    server.settimeout(10.0)

    last_activity = time.time()
    try:
        while True:
            try:
                conn, _addr = server.accept()
            except socket.timeout:
                if time.time() - last_activity > SENSOR_IDLE_TIMEOUT:
                    logger.info("Sensor helper idle; shutting down.")
                    break
                continue
            except OSError:
                break

            with conn:
                last_activity = time.time()
                try:
                    conn.settimeout(5.0)
                    data = conn.recv(1024)
                    if not data:
                        continue
                    cmd = data.split(b"\n", 1)[0].decode("utf-8", "replace").strip()
                    if cmd.upper() == "QUIT":
                        logger.info("QUIT received; shutting down sensor helper.")
                        break
                    payload = json.dumps(build_payload(monitor, get_processor_info))
                    conn.sendall((payload + "\n").encode("utf-8"))
                except Exception as e:
                    logger.debug("helper request handling error: %s", e)
    finally:
        try:
            monitor.close()
        except Exception:
            pass
        server.close()
    return 0