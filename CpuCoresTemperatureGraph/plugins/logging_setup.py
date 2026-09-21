# -*- coding: utf-8 -*-
"""
Logging setup for CpuCore0Meter.

Logs are appended to %LOCALAPPDATA%\\CpuCore0Meter\\cpumeter.log so that
failures on other machines (silent GUI mode, console=False) are never invisible.
"""

import logging
import os
import sys

APP_LOG_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"),
    "CpuCore0Meter",
)


def get_log_path():
    return os.path.join(APP_LOG_DIR, "cpumeter.log")


def get_log_dir():
    return APP_LOG_DIR


def init_logging(verbose=False):
    try:
        os.makedirs(APP_LOG_DIR, exist_ok=True)
    except Exception:
        pass

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")

    if not any(isinstance(h, logging.FileHandler) for h in root.handlers):
        try:
            fh = logging.FileHandler(get_log_path(), encoding="utf-8")
            fh.setFormatter(fmt)
            root.addHandler(fh)
        except Exception:
            pass

    if verbose:
        try:
            sh = logging.StreamHandler(sys.stderr)
            sh.setFormatter(fmt)
            root.addHandler(sh)
        except Exception:
            pass