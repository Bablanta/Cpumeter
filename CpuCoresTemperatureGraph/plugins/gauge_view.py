# -*- coding: utf-8 -*-
"""
Gauge View Plugin for CpuCoresTemperatureGraph.
Displays a high-precision analog circular meter gauge dedicated exclusively to CPU Core 0,
with zero text overlap:
- Dedicated central hub for digital temperature readout and core badge
- Needle sweeps in the outer annular track (never overlaps central text)
- Separate stats cards below the dial
- Clean real-time sparkline history with title outside the plot
- Color-coded temperature zones and legend
"""

import math
import time
import threading
import tkinter as tk
from .base import BaseViewPlugin
from .autostart import is_autostart_enabled, set_autostart


THEMES = {
    "dark_luxury": {
        "name": "Dark Luxury",
        "bg": "#0d1117",
        "card_bg": "#161b22",
        "card_border": "#30363d",
        "bezel_outer": "#1b2028",
        "bezel_mid": "#2b323d",
        "bezel_inner": "#161b22",
        "dial_face": "#0f131a",
        "hub_bg": "#161b22",
        "hub_border": "#30363d",
        "scale_text": "#8b949e",
        "scale_ticks": "#484f58",
        "needle_color": "#58a6ff",
        "needle_accent": "#ffffff",
        "text_title": "#f0f6fc",
        "text_sub": "#8b949e",
        "text_stats_lbl": "#8b949e",
        "text_stats_val": "#58a6ff",
        "arc_bg": "#21262d",
        "arc_normal": "#2ea043",
        "arc_warm": "#d29922",
        "arc_hot": "#f85149",
        "sparkline_line": "#58a6ff",
        "sparkline_fill": "#1f6feb",
        "grid_line": "#21262d",
    },
    "cyberpunk": {
        "name": "Cyberpunk Neon",
        "bg": "#05050d",
        "card_bg": "#0e0d1f",
        "card_border": "#28204d",
        "bezel_outer": "#120e24",
        "bezel_mid": "#00f0ff",
        "bezel_inner": "#1f153a",
        "dial_face": "#09081a",
        "hub_bg": "#120f29",
        "hub_border": "#00f0ff",
        "scale_text": "#00f0ff",
        "scale_ticks": "#ff007f",
        "needle_color": "#ff007f",
        "needle_accent": "#00f0ff",
        "text_title": "#00f0ff",
        "text_sub": "#ff79c6",
        "text_stats_lbl": "#8b949e",
        "text_stats_val": "#00f0ff",
        "arc_bg": "#161233",
        "arc_normal": "#00f0ff",
        "arc_warm": "#ffb86c",
        "arc_hot": "#ff5555",
        "sparkline_line": "#00f0ff",
        "sparkline_fill": "#ff007f",
        "grid_line": "#1f183d",
    },
    "minimal_silver": {
        "name": "Minimalist Silver",
        "bg": "#f0f2f5",
        "card_bg": "#ffffff",
        "card_border": "#d0d7de",
        "bezel_outer": "#b0b8c1",
        "bezel_mid": "#d0d7de",
        "bezel_inner": "#e1e4e8",
        "dial_face": "#ffffff",
        "hub_bg": "#f6f8fa",
        "hub_border": "#d0d7de",
        "scale_text": "#424a53",
        "scale_ticks": "#8c959f",
        "needle_color": "#0969da",
        "needle_accent": "#1f2328",
        "text_title": "#1f2328",
        "text_sub": "#57606a",
        "text_stats_lbl": "#57606a",
        "text_stats_val": "#0969da",
        "arc_bg": "#eaeef2",
        "arc_normal": "#1a7f37",
        "arc_warm": "#9a6700",
        "arc_hot": "#cf222e",
        "sparkline_line": "#0969da",
        "sparkline_fill": "#54aeff",
        "grid_line": "#eaeef2",
    },
    "sport_racing": {
        "name": "Sport Racing",
        "bg": "#0a0a0a",
        "card_bg": "#141414",
        "card_border": "#2c2c2c",
        "bezel_outer": "#ef4444",
        "bezel_mid": "#282828",
        "bezel_inner": "#181818",
        "dial_face": "#121212",
        "hub_bg": "#18181b",
        "hub_border": "#ef4444",
        "scale_text": "#e5e5e5",
        "scale_ticks": "#737373",
        "needle_color": "#ef4444",
        "needle_accent": "#ffffff",
        "text_title": "#f5f5f5",
        "text_sub": "#ef4444",
        "text_stats_lbl": "#a3a3a3",
        "text_stats_val": "#ef4444",
        "arc_bg": "#262626",
        "arc_normal": "#64748b",
        "arc_warm": "#f59e0b",
        "arc_hot": "#ef4444",
        "sparkline_line": "#ef4444",
        "sparkline_fill": "#991b1b",
        "grid_line": "#262626",
    },
}


class GaugeViewPlugin(BaseViewPlugin):
    plugin_id = "gauge"
    plugin_name = "Core 0 Analog Gauge Meter"
    description = "Displays CPU Core 0 on a clutter-free analog circular meter with clean separation of numbers and text."

    def __init__(self, sensor_monitor, get_processor_info_func, options=None):
        super(GaugeViewPlugin, self).__init__(sensor_monitor, get_processor_info_func, options)
        self.theme_key = getattr(options, 'theme', 'dark_luxury') if options else 'dark_luxury'
        if self.theme_key not in THEMES:
            self.theme_key = "dark_luxury"
        self.theme = THEMES[self.theme_key]
        self.always_on_top = getattr(options, 'top', False) if options else False

        # Core selection: strictly default to Core 0
        target_core = getattr(options, 'core', '0') if options else '0'
        try:
            self.target_core_index = int(target_core)
        except Exception:
            self.target_core_index = 0

        # Window & Geometry Dimensions
        self.win_w = 480
        self.win_h = 560
        self.cx = self.win_w // 2
        self.cy = 195
        self.radius = 170

        # Stats tracking for Core 0
        self.current_temp = 0.0
        self.min_temp = 999.0
        self.max_temp = 0.0
        self.critical_temp = 100.0
        self.high_temp = 85.0
        self.core_label = f"Core {self.target_core_index}"
        self.proc_info = self.get_processor_info() or "CPU Core 0"
        self.next_view = None

        raw_proc = self.proc_info.split('@')[0].strip()
        for prefix in ["Intel(R) Core(TM) ", "Intel(R) ", "AMD Ryzen(TM) ", "AMD Ryzen ", "AMD "]:
            if raw_proc.startswith(prefix):
                raw_proc = raw_proc[len(prefix):]
                break
        self.proc_display_name = raw_proc[:18].strip() if len(raw_proc) > 18 else raw_proc

        # History buffer for sparkline (last 60 samples)
        self.history_size = 60
        self.history = [0.0] * self.history_size

        # UI state
        self.root = None
        self.canvas = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.poll_thread = None

    def _polling_worker(self):
        """Asynchronously polls hardware sensor for Core 0."""
        while self.running:
            try:
                cores = self.sensor_monitor.get_core_temperatures()
                if cores:
                    core_obj = None
                    for idx, c in enumerate(cores):
                        if idx == self.target_core_index or c.label == f"Core {self.target_core_index}":
                            core_obj = c
                            break
                    if core_obj is None and len(cores) > 0:
                        core_obj = cores[0]

                    if core_obj:
                        val = float(core_obj.current)
                        self.current_temp = val
                        self.critical_temp = float(core_obj.critical)
                        self.high_temp = float(core_obj.high)
                        self.core_label = core_obj.label

                        if val < self.min_temp and val > 0:
                            self.min_temp = val
                        if val > self.max_temp:
                            self.max_temp = val

                        self.history = self.history[1:] + [val]
            except Exception:
                pass
            time.sleep(0.4)

    def init_UI(self):
        self.root = tk.Tk()
        self.root.title(f"CPU {self.core_label} Temperature Monitor")
        self.root.geometry(f"{self.win_w}x{self.win_h}")
        self.root.resizable(False, False)
        self.root.configure(bg=self.theme["bg"])
        if self.always_on_top:
            self.root.attributes("-topmost", True)

        self.canvas = tk.Canvas(
            self.root,
            width=self.win_w,
            height=self.win_h,
            bg=self.theme["bg"],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.root.lift()
        self.root.focus_force()

        # Dragging
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)

        # Context Menu
        self.menu = None
        self._build_context_menu()

        self.canvas.bind("<Button-3>", self._show_context_menu)
        self.root.protocol("WM_DELETE_WINDOW", self.request_stop)

    def _build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(
            label="✓ Selalu di Atas (Always on Top)" if self.always_on_top else "  Selalu di Atas (Always on Top)",
            command=self._toggle_always_on_top
        )
        is_auto = is_autostart_enabled()
        self.menu.add_command(
            label="✓ Buka Otomatis saat Mesin Dinyalakan" if is_auto else "  Buka Otomatis saat Mesin Dinyalakan",
            command=self._toggle_autostart
        )
        self.menu.add_command(label="⏱ Buka Mini Gauge (5cm Compact)", command=self._switch_to_compact)

        theme_menu = tk.Menu(self.menu, tearoff=0)
        for key, t in THEMES.items():
            theme_menu.add_command(label=t["name"], command=lambda k=key: self._set_theme(k))
        self.menu.add_cascade(label="🎨 Themes", menu=theme_menu)

        self.menu.add_separator()
        self.menu.add_command(label="🔄 Reset Min / Max", command=self._reset_min_max)
        self.menu.add_command(label="❌ Exit", command=self.request_stop)

    def _toggle_autostart(self):
        current = is_autostart_enabled()
        set_autostart(not current, view="gauge")
        self._build_context_menu()

    def _switch_to_compact(self):
        self.next_view = "compact"
        self.request_stop()

    def _show_context_menu(self, event):
        self._build_context_menu()
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _on_mouse_down(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_mouse_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_start_x)
        y = self.root.winfo_y() + (event.y - self.drag_start_y)
        self.root.geometry(f"+{x}+{y}")

    def _toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        self.root.attributes("-topmost", self.always_on_top)

    def _set_theme(self, key):
        if key in THEMES:
            self.theme_key = key
            self.theme = THEMES[key]
            self.root.configure(bg=self.theme["bg"])
            self.canvas.configure(bg=self.theme["bg"])

    def _reset_min_max(self):
        self.min_temp = self.current_temp
        self.max_temp = self.current_temp

    def draw_gauge(self):
        """Redraws the Core 0 circular gauge with zero text overlap."""
        self.canvas.delete("all")
        t = self.theme
        cx, cy, r = self.cx, self.cy, self.radius

        # =====================================================================
        # 1. OUTER BEZEL & DIAL FACE
        # =====================================================================
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=t["bezel_outer"], outline="")
        self.canvas.create_oval(cx - (r - 7), cy - (r - 7), cx + (r - 7), cy + (r - 7), fill=t["bezel_mid"], outline="")
        self.canvas.create_oval(cx - (r - 12), cy - (r - 12), cx + (r - 12), cy + (r - 12), fill=t["bezel_inner"], outline="")
        self.canvas.create_oval(cx - (r - 16), cy - (r - 16), cx + (r - 16), cy + (r - 16), fill=t["dial_face"], outline=t["bezel_inner"], width=1)

        dial_r = r - 16

        # Gauge Scale Geometry:
        # 240-degree sweep from 150 deg (bottom-left) to 390 deg (bottom-right)
        start_angle = 150.0
        sweep_angle = 240.0
        max_scale = 100.0

        # =====================================================================
        # 2. COLORED GAUGE TRACK (ARC)
        # =====================================================================
        arc_r = dial_r - 16
        bbox = (cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r)

        # Background track
        self.canvas.create_arc(
            bbox, start=-30, extent=240, style=tk.ARC,
            outline=t["arc_bg"], width=7
        )

        # In Tkinter coordinate system: 150 deg clock = 210 deg Tkinter.
        tk_start = 210.0

        # Green Normal Zone (0 to 55°C) -> 55% = 132 deg
        ext_norm = (55.0 / max_scale) * sweep_angle
        self.canvas.create_arc(
            bbox, start=tk_start, extent=-ext_norm, style=tk.ARC,
            outline=t["arc_normal"], width=6
        )

        # Orange Warm Zone (55 to 75°C) -> 20% = 48 deg
        ext_warm = (20.0 / max_scale) * sweep_angle
        self.canvas.create_arc(
            bbox, start=tk_start - ext_norm, extent=-ext_warm, style=tk.ARC,
            outline=t["arc_warm"], width=6
        )

        # Red Hot Zone (75 to 100°C) -> 25% = 60 deg
        ext_hot = (25.0 / max_scale) * sweep_angle
        self.canvas.create_arc(
            bbox, start=tk_start - ext_norm - ext_warm, extent=-ext_hot, style=tk.ARC,
            outline=t["arc_hot"], width=6
        )

        # =====================================================================
        # 3. SCALE TICKS & NUMBERS (Drawn with generous clearance)
        # =====================================================================
        # Ticks extend inwards from arc_r - 5 down to arc_r - 16
        tick_outer = arc_r - 6
        for temp_val in range(0, 101, 5):
            frac = temp_val / max_scale
            angle_deg = start_angle + frac * sweep_angle
            angle_rad = math.radians(angle_deg)

            if temp_val % 10 == 0:
                # Major tick
                tick_inner = tick_outer - 10
                x1 = cx + tick_inner * math.cos(angle_rad)
                y1 = cy + tick_inner * math.sin(angle_rad)
                x2 = cx + tick_outer * math.cos(angle_rad)
                y2 = cy + tick_outer * math.sin(angle_rad)
                self.canvas.create_line(x1, y1, x2, y2, fill=t["scale_text"], width=2)

                # Number: placed with comfortable radial clearance
                lbl_r = tick_inner - 12
                lx = cx + lbl_r * math.cos(angle_rad)
                ly = cy + lbl_r * math.sin(angle_rad)
                self.canvas.create_text(
                    lx, ly,
                    text=str(temp_val),
                    fill=t["scale_text"],
                    font=("Segoe UI", 8, "bold")
                )
            else:
                # Minor tick
                tick_inner = tick_outer - 5
                x1 = cx + tick_inner * math.cos(angle_rad)
                y1 = cy + tick_inner * math.sin(angle_rad)
                x2 = cx + tick_outer * math.cos(angle_rad)
                y2 = cy + tick_outer * math.sin(angle_rad)
                self.canvas.create_line(x1, y1, x2, y2, fill=t["scale_ticks"], width=1)

        # =====================================================================
        # 4. CURRENT VALUE COLOR DETERMINATION
        # =====================================================================
        val = self.current_temp
        if val >= 75.0:
            val_color = t["arc_hot"]
            status_desc = "CRITICAL LOAD"
        elif val >= 55.0:
            val_color = t["arc_warm"]
            status_desc = "WARM LOAD"
        else:
            val_color = t["arc_normal"]
            status_desc = "NORMAL TEMP"

        # =====================================================================
        # 5. DYNAMIC NEEDLE POINTER (Confined to Annular Track: r_in to r_out)
        # =====================================================================
        # The needle travels STRICTLY between r_needle_in and r_needle_out,
        # so it NEVER intersects the central text hub!
        clamped_val = max(0.0, min(val, max_scale))
        needle_frac = clamped_val / max_scale
        needle_deg = start_angle + needle_frac * sweep_angle
        needle_rad = math.radians(needle_deg)

        r_needle_in = 74
        r_needle_out = arc_r - 7

        # Tip of pointer
        tip_x = cx + r_needle_out * math.cos(needle_rad)
        tip_y = cy + r_needle_out * math.sin(needle_rad)

        # Root of pointer
        root_x = cx + r_needle_in * math.cos(needle_rad)
        root_y = cy + r_needle_in * math.sin(needle_rad)

        # Needle width wings
        wing_w = 4.5
        perp_rad = needle_rad + (math.pi / 2.0)
        w1_x = root_x + wing_w * math.cos(perp_rad)
        w1_y = root_y + wing_w * math.sin(perp_rad)
        w2_x = root_x - wing_w * math.cos(perp_rad)
        w2_y = root_y - wing_w * math.sin(perp_rad)

        self.canvas.create_polygon(
            [root_x, root_y, w1_x, w1_y, tip_x, tip_y, w2_x, w2_y],
            fill=val_color, outline=t["dial_face"], width=1
        )

        # =====================================================================
        # 6. CENTRAL TEXT HUB (Dedicated Protected Circular Area, Radius <= 68)
        # =====================================================================
        hub_r = 68
        self.canvas.create_oval(
            cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r,
            fill=t["hub_bg"], outline=t["hub_border"], width=2
        )

        # A. Core Badge (Pill Container)
        badge_w, badge_h = 74, 18
        bx1 = cx - (badge_w // 2)
        by1 = cy - 48
        bx2 = cx + (badge_w // 2)
        by2 = by1 + badge_h
        self.canvas.create_rectangle(
            bx1, by1, bx2, by2,
            fill=t["card_border"], outline="", width=0
        )
        self.canvas.create_text(
            cx, by1 + (badge_h // 2),
            text="CORE 0",
            fill=t["text_title"],
            font=("Segoe UI", 9, "bold")
        )

        # B. Processor Short Name
        self.canvas.create_text(
            cx, cy - 20,
            text=self.proc_display_name,
            fill=t["text_sub"],
            font=("Segoe UI", 8)
        )

        # C. Large Digital Temperature Readout (Centered & Uncluttered)
        disp_temp = f"{int(round(val))}°C" if val > 0 else "--°C"
        self.canvas.create_text(
            cx, cy + 10,
            text=disp_temp,
            fill=val_color,
            font=("Segoe UI", 26, "bold")
        )

        # D. Status Indicator Label
        self.canvas.create_text(
            cx, cy + 42,
            text=status_desc,
            fill=val_color,
            font=("Segoe UI", 7, "bold")
        )

        # =====================================================================
        # 7. METRICS CARDS (Horizontally Structured Below the Dial)
        # =====================================================================
        card_y = 380
        card_h = 44
        card_gap = 10
        total_card_w = self.win_w - 48
        card_w = (total_card_w - (2 * card_gap)) // 3
        start_x = 24

        min_disp = f"{int(round(self.min_temp))}°C" if self.min_temp < 900 else "--"
        max_disp = f"{int(round(self.max_temp))}°C" if self.max_temp > 0 else "--"
        crit_disp = f"{int(self.critical_temp)}°C"

        cards_data = [
            ("MINIMUM", min_disp, t["arc_normal"]),
            ("PEAK (MAX)", max_disp, t["arc_warm"] if self.max_temp >= 55 else t["arc_normal"]),
            ("TJMAX CRIT", crit_disp, t["arc_hot"]),
        ]

        for i, (lbl, val_str, c_color) in enumerate(cards_data):
            c_x1 = start_x + i * (card_w + card_gap)
            c_y1 = card_y
            c_x2 = c_x1 + card_w
            c_y2 = c_y1 + card_h

            # Card background
            self.canvas.create_rectangle(
                c_x1, c_y1, c_x2, c_y2,
                fill=t["card_bg"], outline=t["card_border"], width=1
            )
            # Label
            self.canvas.create_text(
                c_x1 + (card_w // 2), c_y1 + 13,
                text=lbl,
                fill=t["text_stats_lbl"],
                font=("Segoe UI", 7, "bold")
            )
            # Value
            self.canvas.create_text(
                c_x1 + (card_w // 2), c_y1 + 30,
                text=val_str,
                fill=c_color,
                font=("Consolas", 11, "bold")
            )

        # =====================================================================
        # 8. REAL-TIME SPARKLINE HISTORY (With Header Outside Box)
        # =====================================================================
        spark_header_y = 440
        self.canvas.create_text(
            24, spark_header_y,
            anchor="w",
            text="REAL-TIME TEMPERATURE HISTORY (60s)",
            fill=t["text_stats_lbl"],
            font=("Segoe UI", 8, "bold")
        )

        spark_x = 24
        spark_y = spark_header_y + 12
        spark_w = self.win_w - 48
        spark_h = 50

        # Background container
        self.canvas.create_rectangle(
            spark_x, spark_y, spark_x + spark_w, spark_y + spark_h,
            fill=t["card_bg"], outline=t["card_border"], width=1
        )

        # Grid reference lines (at 50°C and 80°C)
        y_50 = (spark_y + spark_h) - int(0.50 * spark_h)
        y_80 = (spark_y + spark_h) - int(0.80 * spark_h)
        self.canvas.create_line(spark_x, y_50, spark_x + spark_w, y_50, fill=t["grid_line"], width=1, dash=(2, 4))
        self.canvas.create_line(spark_x, y_80, spark_x + spark_w, y_80, fill=t["grid_line"], width=1, dash=(2, 4))

        # Sparkline line
        valid_history = [h for h in self.history if h > 0]
        if len(valid_history) >= 2:
            step_x = spark_w / float(self.history_size - 1)
            points = []
            for idx_h, h_val in enumerate(self.history):
                px = spark_x + (idx_h * step_x)
                norm_h = max(0.0, min(h_val / 100.0, 1.0))
                py = (spark_y + spark_h - 2) - (norm_h * (spark_h - 4))
                points.extend([px, py])

            self.canvas.create_line(points, fill=t["sparkline_line"], width=2, smooth=True)

        # =====================================================================
        # 9. BOTTOM LEGEND (Clean, Informative)
        # =====================================================================
        leg_y = 522
        leg_items = [
            ("● <55°C Normal", t["arc_normal"]),
            ("● 55-75°C Warm", t["arc_warm"]),
            ("● >75°C Critical", t["arc_hot"]),
        ]
        leg_gap = 130
        leg_start_x = self.cx - 130

        for i, (leg_txt, leg_col) in enumerate(leg_items):
            self.canvas.create_text(
                leg_start_x + (i * leg_gap), leg_y,
                text=leg_txt,
                fill=leg_col,
                font=("Segoe UI", 8, "bold")
            )

    def _tick(self):
        if not self.running:
            return
        try:
            self.draw_gauge()
            if self.root:
                self.root.after(100, self._tick)
        except Exception:
            self.running = False

    def run(self):
        self.init_UI()

        self.poll_thread = threading.Thread(target=self._polling_worker, daemon=True)
        self.poll_thread.start()

        try:
            cores = self.sensor_monitor.get_core_temperatures()
            if cores and len(cores) > self.target_core_index:
                c = cores[self.target_core_index]
                self.current_temp = float(c.current)
                self.min_temp = self.current_temp
                self.max_temp = self.current_temp
                self.critical_temp = float(c.critical)
                self.core_label = c.label
                self.history = [self.current_temp] * self.history_size
        except Exception:
            pass

        self._tick()

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            if not getattr(self, 'next_view', None):
                self.sensor_monitor.close()

    def request_stop(self):
        self.running = False
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass
