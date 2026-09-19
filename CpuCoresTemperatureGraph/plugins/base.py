# -*- coding: utf-8 -*-
"""
Base plugin interface for CpuCoresTemperatureGraph.
"""

class BaseViewPlugin(object):
    """Base class that all view plugins must inherit from."""

    plugin_id = "base"
    plugin_name = "Base View"
    description = "Abstract base view plugin"

    def __init__(self, sensor_monitor, get_processor_info_func, options=None):
        self.sensor_monitor = sensor_monitor
        self.get_processor_info = get_processor_info_func
        self.options = options
        self.running = True

    def run(self):
        """Start the plugin's GUI loop (blocking)."""
        raise NotImplementedError("Plugins must implement the run() method.")

    def request_stop(self):
        """Signal the plugin to stop running."""
        self.running = False
