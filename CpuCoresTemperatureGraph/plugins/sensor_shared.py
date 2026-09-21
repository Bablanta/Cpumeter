# -*- coding: utf-8 -*-
"""
Shared primitives for the two-process sensor architecture (GUI <-> elevated helper).

- CoreTemp namedtuple used across all view plugins.
- Loopback TCP port used for intra-machine sensor transport.
- JSON (de)serialization helpers.
"""

from collections import namedtuple

CoreTemp = namedtuple('CoreTemp', ['label', 'current', 'high', 'critical'])

# loopback TCP port for the elevated sensor helper
SENSOR_PORT = 40123

SENSOR_IDLE_TIMEOUT = 600.0


def core_temp_to_json(ct):
    return {
        "label": ct.label,
        "current": ct.current,
        "high": ct.high,
        "critical": ct.critical,
    }


def core_temp_from_json(obj):
    return CoreTemp(
        label=str(obj.get("label", "Core")),
        current=float(obj.get("current", 0.0)),
        high=float(obj.get("high", 85.0)),
        critical=float(obj.get("critical", 100.0)),
    )