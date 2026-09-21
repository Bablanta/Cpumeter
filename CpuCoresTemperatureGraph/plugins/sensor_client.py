# -*- coding: utf-8 -*-
"""
Loopback TCP client for the elevated sensor helper.

Provides:
- start_sensor_helper()  : launch the elevated helper once (UAC prompt).
- is_helper_running()    : quick liveness probe.
- request_sensor_data()  : fetch one JSON payload.
- RemoteSensorMonitor()  : drop-in replacement for TemperatureMonitor that
                           reads through the helper (used when unelevated).
"""

import json
import logging
import os
import platform
import socket
import sys
import time

from .sensor_shared import SENSOR_PORT, core_temp_from_json

logger = logging.getLogger(__name__)


def is_helper_running(timeout=0.5):
    try:
        with socket.create_connection(("127.0.0.1", SENSOR_PORT), timeout=timeout):
            return True
    except Exception:
        return False


def request_sensor_data(timeout=1.0):
    try:
        with socket.create_connection(("127.0.0.1", SENSOR_PORT), timeout=timeout) as s:
            s.settimeout(timeout)
            s.sendall(b"GET\n")
            buf = b""
            while b"\n" not in buf:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
        line = buf.split(b"\n", 1)[0].decode("utf-8", "replace").strip()
        if not line:
            return None
        return json.loads(line)
    except Exception as e:
        logger.debug("sensor helper not reachable: %s", e)
        return None


def start_sensor_helper():
    """Launch the elevated sensor helper via ShellExecuteW(runas)."""
    if platform.system() != "Windows":
        return False
    try:
        import ctypes
        if getattr(sys, "frozen", False):
            exe = os.path.abspath(sys.executable)
            params = "--sensor-helper"
        else:
            exe = sys.executable
            params = '"{0}" --sensor-helper'.format(os.path.abspath(sys.argv[0]))
        # SW_HIDE = 0: elevated helper never shows a window
        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 0)
        return result > 32
    except Exception as e:
        logger.error("failed to start sensor helper: %s", e)
        return False


class RemoteSensorMonitor(object):
    """Reads CPU temperatures through the elevated helper over loopback TCP."""

    def __init__(self, port=SENSOR_PORT):
        self.port = port
        self._cache = []
        self._cache_time = 0.0
        self.sensor_source = "helper"
        self.last_error = None
        self.ever_got_data = False

    def requires_helper(self):
        return True

    def get_core_temperatures(self):
        now = time.time()
        if self._cache and now - self._cache_time < 0.4:
            return self._cache

        payload = request_sensor_data()
        self._cache_time = now

        if payload is None:
            self._cache = []
            self.last_error = "sensor helper tidak aktif"
            self.sensor_source = "none"
            return []

        self.sensor_source = payload.get("source", "helper")
        self.last_error = payload.get("error")
        cores = [core_temp_from_json(c) for c in (payload.get("cores") or [])]
        if cores:
            self.ever_got_data = True
        self._cache = cores
        return cores

    def close(self):
        pass