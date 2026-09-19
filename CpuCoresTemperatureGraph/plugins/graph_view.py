# -*- coding: utf-8 -*-
"""
Classic Matplotlib Graph View Plugin.
"""

import math
import matplotlib
import matplotlib.pyplot
from .base import BaseViewPlugin


class GraphViewPlugin(BaseViewPlugin):
    plugin_id = "graph"
    plugin_name = "Classic Graph View"
    description = "Displays CPU core temperatures in real-time line charts with Matplotlib."

    def __init__(self, sensor_monitor, get_processor_info_func, options=None):
        super(GraphViewPlugin, self).__init__(sensor_monitor, get_processor_info_func, options)
        self.window_size = getattr(options, 'window_size', 600) if options else 600
        self.refresh_time = getattr(options, 'refresh_time', 0.5) if options else 0.5
        self.x_time = list(range(self.window_size))
        self.views = {}
        self.fig = None
        self.next_view = None

    def init_UI(self):
        matplotlib.rcParams['toolbar'] = 'none'
        matplotlib.rcParams['grid.color'] = '#3c3c3c'
        matplotlib.pyplot.ion()

        self.fig = matplotlib.pyplot.figure()
        proc_info = self.get_processor_info()
        self.fig.suptitle(proc_info, fontsize=14, color='white')

        if hasattr(self.fig.canvas, 'manager') and hasattr(self.fig.canvas.manager, 'set_window_title'):
            self.fig.canvas.manager.set_window_title(f"CPU Cores Temperature Graph - {proc_info}")

        self.fig.patch.set_facecolor('black')
        self.fig.patch.set_edgecolor('white')
        self.fig.canvas.mpl_connect('close_event', lambda evt: self.request_stop())

        cpu_cores = self.sensor_monitor.get_core_temperatures()
        target_core = getattr(self.options, 'core', '0') if self.options else '0'
        if target_core != "all" and cpu_cores:
            try:
                c_idx = int(target_core)
                if c_idx < len(cpu_cores):
                    cpu_cores = [cpu_cores[c_idx]]
                else:
                    cpu_cores = [cpu_cores[0]]
            except Exception:
                matched = [c for c in cpu_cores if c.label.lower() == str(target_core).lower()]
                if matched:
                    cpu_cores = matched
                else:
                    cpu_cores = cpu_cores[:1]

        self.views = {}
        n_cores = len(cpu_cores)
        if n_cores > 0:
            ncols = math.ceil(math.sqrt(n_cores))
            nrows = math.ceil(n_cores / ncols)

            for index, cpucore in enumerate(cpu_cores):
                self.views[cpucore.label] = {
                    "ax": self.fig.add_subplot(nrows, ncols, index + 1),
                    "data": {
                        "current": [cpucore.current] * self.window_size,
                        "high": [cpucore.high] * self.window_size,
                        "critical": [cpucore.critical] * self.window_size,
                    },
                    "core": cpucore
                }

        matplotlib.pyplot.tight_layout(pad=1, w_pad=1, h_pad=1)
        matplotlib.pyplot.show(block=False)

    def update(self):
        def dyn_update(ax, lx, data, marker='', title='', color="blue"):
            ax.clear()
            ax.patch.set_facecolor('#1c1c1c')
            ax.patch.set_edgecolor('white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.tick_params(axis='x', colors='black')
            ax.tick_params(axis='y', colors='white')
            ax.yaxis.label.set_color('white')
            ax.xaxis.label.set_color('black')
            ax.title.set_color('white')

            ax.plot(lx, data["current"], marker=marker, color=color, label="Temp (C)")
            ax.fill_between(lx, 0, data["current"], alpha=.5, color=color)
            ax.plot(lx, data["high"], marker=marker, color="orange", label=None)
            ax.plot(lx, data["critical"], marker=marker, color="red", label=None)

            ax.set_title(title)
            ax.set_ylabel("Temp (°C)")
            ax.grid(True)
            max_value_critical = max(data["critical"]) if max(data["critical"]) > 0 else 100
            ax.set_ylim(0, 1.1 * max_value_critical)
            ax.set_xlim(0, max(lx) + 1)

        current_cores = {c.label: c for c in self.sensor_monitor.get_core_temperatures()}
        for core_label in self.views.keys():
            cpucore = current_cores.get(core_label)
            if cpucore is None:
                cur_temp = self.views[core_label]["data"]["current"][-1]
                high_temp = self.views[core_label]["data"]["high"][-1]
                crit_temp = self.views[core_label]["data"]["critical"][-1]
            else:
                cur_temp = cpucore.current
                high_temp = cpucore.high
                crit_temp = cpucore.critical

            self.views[core_label]["data"]["current"] = self.views[core_label]["data"]["current"][1:self.window_size] + [cur_temp]
            self.views[core_label]["data"]["high"] = self.views[core_label]["data"]["high"][1:self.window_size] + [high_temp]
            self.views[core_label]["data"]["critical"] = self.views[core_label]["data"]["critical"][1:self.window_size] + [crit_temp]

            dyn_update(
                ax=self.views[core_label]["ax"],
                lx=self.x_time,
                data=self.views[core_label]["data"],
                title=core_label,
                color='green'
            )

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def run(self):
        self.init_UI()
        self.update()
        while self.running:
            if not matplotlib.pyplot.fignum_exists(self.fig.number):
                self.running = False
                break
            try:
                self.update()
                matplotlib.pyplot.pause(self.refresh_time)
            except Exception:
                self.running = False
                break
        self.sensor_monitor.close()
