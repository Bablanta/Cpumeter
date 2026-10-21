# -*- coding: utf-8 -*-
"""
Compact Mini Gauge View Plugin for CpuCoresTemperatureGraph.

Features:
- Ultra-smooth 4K anti-aliased rendering using 4x supersampling (SSAA) with Pillow LANCZOS.
- Compact 4cm (150 px) circular analog meter dedicated exclusively to a single CPU core.
- Fluid 60 FPS needle animation with spring/lerp physics (no abrupt stepping).
- Zero text overlap: Center hub is isolated and framed, with unobstructed readability.
- Switchable modes:
    * Compact with Digital Hub (includes digital °C and core badge)
    * Minimalist Pure Analog (clean precision instrument with jewel cap)
- Multiple luxury themes:
    * dark_luxury (obsidian & gold / ice-blue)
    * cyberpunk (neon cyan & hot magenta HUD)
    * sport_racing (matte carbon & racing red tachometer)
- Borderless floating circular widget with left-click drag support anywhere on desktop.
- Right-click context menu for instantaneous switching of themes, styles, opacity,
  and always-on-top.
"""

import math
import os
import time
import threading
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import pystray
from pystray import MenuItem as Item, Menu
from .base import BaseViewPlugin
from .autostart import is_autostart_enabled, set_autostart
from .sensor_client import start_sensor_helper, is_helper_running
from .logging_setup import get_log_dir


# The widget has a fixed size: Mini 4cm (~150 px at 96 DPI).
WIDGET_SIZE = 150
# Layout is designed for 190 px and downscaled, keeping the original proportions.
DESIGN_SIZE = 190


THEMES = {
    "dark_luxury": {
        "name": "Dark Luxury",
        "bg": (12, 16, 22, 255),
        "dial": (15, 19, 26, 255),
        "bezel_outer": (48, 54, 61, 255),
        "bezel_inner": (32, 38, 48, 255),
        "track_bg": (33, 38, 45, 255),
        "normal": (46, 160, 67, 255),
        "warm": (210, 153, 34, 255),
        "hot": (248, 81, 73, 255),
        "needle": (88, 166, 255, 255),
        "needle_glow": (88, 166, 255, 110),
        "needle_spine": (255, 255, 255, 240),
        "hub_bg": (18, 22, 29, 255),
        "hub_border": (56, 64, 75, 255),
        "hub_text": (88, 166, 255, 255),
        "hub_sub": (139, 148, 158, 255),
        "tick_maj": (200, 210, 225, 255),
        "tick_min": (110, 120, 135, 220),
        "scale_txt": (180, 190, 205, 255),
    },
    "cyberpunk": {
        "name": "Cyberpunk HUD",
        "bg": (5, 5, 13, 255),
        "dial": (9, 8, 26, 255),
        "bezel_outer": (0, 240, 255, 255),
        "bezel_inner": (31, 21, 58, 255),
        "track_bg": (22, 18, 51, 255),
        "normal": (0, 240, 255, 255),
        "warm": (255, 184, 108, 255),
        "hot": (255, 0, 127, 255),
        "needle": (255, 0, 127, 255),
        "needle_glow": (255, 0, 127, 130),
        "needle_spine": (255, 200, 230, 255),
        "hub_bg": (18, 15, 41, 255),
        "hub_border": (0, 240, 255, 255),
        "hub_text": (0, 240, 255, 255),
        "hub_sub": (255, 121, 198, 255),
        "tick_maj": (0, 240, 255, 255),
        "tick_min": (150, 0, 200, 200),
        "scale_txt": (0, 240, 255, 255),
    },
    "sport_racing": {
        "name": "Sport Racing",
        "bg": (10, 10, 10, 255),
        "dial": (20, 20, 20, 255),
        "bezel_outer": (239, 68, 68, 255),
        "bezel_inner": (40, 40, 40, 255),
        "track_bg": (35, 35, 35, 255),
        "normal": (100, 116, 139, 255),
        "warm": (245, 158, 11, 255),
        "hot": (239, 68, 68, 255),
        "needle": (239, 68, 68, 255),
        "needle_glow": (239, 68, 68, 120),
        "needle_spine": (255, 255, 255, 250),
        "hub_bg": (24, 24, 27, 255),
        "hub_border": (239, 68, 68, 255),
        "hub_text": (255, 255, 255, 255),
        "hub_sub": (239, 68, 68, 255),
        "tick_maj": (245, 245, 245, 255),
        "tick_min": (115, 115, 115, 200),
        "scale_txt": (220, 220, 220, 255),
    }
}


class CompactGaugePlugin(BaseViewPlugin):
    """
    Compact 4cm (150 px) circular analog meter with 4x SSAA rendering and smooth 60 FPS animation.
    """

    plugin_id = "compact"
    plugin_name = "Compact Mini Gauge"
    description = "Ultra-smooth 4K 4cm circular analog meter for a single CPU core"

    def __init__(self, sensor_monitor, get_processor_info_func, options=None):
        super().__init__(sensor_monitor, get_processor_info_func, options)

        # Target Core
        target_core_str = getattr(options, 'core', '0') if options else '0'
        try:
            self.target_core_index = int(target_core_str)
        except ValueError:
            self.target_core_index = 0

        # Theme & Display Style
        self.current_theme = getattr(options, 'theme', 'dark_luxury') if options else 'dark_luxury'
        if self.current_theme not in THEMES:
            self.current_theme = 'dark_luxury'

        # Dimensions: fixed Mini size (~4cm / 150 px at 96 DPI)
        self.size = WIDGET_SIZE
        self.scale = 4  # 4x Supersampling for true 4K sharpness
        self.always_on_top = getattr(options, 'top', False) if options else False
        self.transparent_circle = True
        self.opacity = 1.0

        # Temperatures & Animation
        self.target_temp = 40.0
        self.display_temp = 40.0
        self.core_label = f"Core {self.target_core_index}"
        self.has_data = False
        self.sensor_error = None

        # Drag state
        self._drag_start_x = 0
        self._drag_start_y = 0

        # UI Handles
        self.root = None
        self.canvas = None
        self.photo_image = None
        self.context_menu = None
        self.poll_thread = None

        # System tray
        self.tray_icon = None
        self._exit_requested = False

        # Cache fonts
        self._load_fonts()

    def _load_fonts(self):
        """Loads TrueType fonts scaled for 4x SSAA."""
        s = self.scale
        try:
            self.font_tick = ImageFont.truetype('segoeui.ttf', int(7 * s))
            self.font_temp = ImageFont.truetype('segoeuib.ttf', int(15 * s))
            self.font_lbl = ImageFont.truetype('segoeuib.ttf', int(6 * s))
            self.font_min_lbl = ImageFont.truetype('segoeuib.ttf', int(12 * s))
        except Exception:
            self.font_tick = ImageFont.load_default()
            self.font_temp = ImageFont.load_default()
            self.font_lbl = ImageFont.load_default()
            self.font_min_lbl = ImageFont.load_default()

    def _polling_worker(self):
        """Asynchronously reads temperature from sensors."""
        while self.running:
            try:
                cores = self.sensor_monitor.get_core_temperatures()
                if not cores:
                    self.has_data = False
                    self.sensor_error = getattr(self.sensor_monitor, 'last_error', None)
                else:
                    core_obj = None
                    for idx, c in enumerate(cores):
                        if idx == self.target_core_index or c.label == f"Core {self.target_core_index}":
                            core_obj = c
                            break
                    if core_obj is None and len(cores) > 0:
                        core_obj = cores[0]

                    if core_obj:
                        val = float(core_obj.current)
                        self.target_temp = val
                        self.core_label = core_obj.label
                        self.has_data = True
                        self.sensor_error = None
            except Exception as e:
                self.has_data = False
                self.sensor_error = repr(e)
            time.sleep(0.3)

    def render_gauge_image(self):
        """Renders the dial at 4x resolution and downsamples with LANCZOS for 4K smoothness."""
        t = THEMES[self.current_theme]
        dim = DESIGN_SIZE * self.scale
        cx, cy = dim / 2.0, dim / 2.0
        s = self.scale
        r = (dim / 2.0) - (6 * s)

        # Base image
        img = Image.new('RGBA', (dim, dim), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        # 1. Bezel & Dial Face
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=t['bg'], outline=t['bezel_outer'], width=int(2.5 * s))
        inner_r = r - (5 * s)
        d.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=t['dial'], outline=t['bezel_inner'], width=int(1.2 * s))

        # 2. Scale Arc Setup (135° to 405° = 270° sweep, 0 to 100°C)
        start_deg = 135.0
        end_deg = 405.0
        sweep = end_deg - start_deg
        track_r = inner_r - (7 * s)
        track_w = int(4.5 * s)

        # Background track arc
        d.arc([cx - track_r, cy - track_r, cx + track_r, cy + track_r], start=135, end=405, fill=t['track_bg'], width=track_w)

        # Dynamic active arc up to current animated temperature
        eff_temp = self.display_temp if self.has_data else 0.0
        cur_frac = max(0.0, min(eff_temp / 100.0, 1.0))
        cur_deg = start_deg + cur_frac * sweep
        deg_55 = start_deg + (55.0 / 100.0) * sweep
        deg_75 = start_deg + (75.0 / 100.0) * sweep

        # Fill color zones
        d.arc([cx - track_r, cy - track_r, cx + track_r, cy + track_r], start=135, end=min(cur_deg, deg_55), fill=t['normal'], width=track_w)
        if cur_deg > deg_55:
            d.arc([cx - track_r, cy - track_r, cx + track_r, cy + track_r], start=deg_55, end=min(cur_deg, deg_75), fill=t['warm'], width=track_w)
        if cur_deg > deg_75:
            d.arc([cx - track_r, cy - track_r, cx + track_r, cy + track_r], start=deg_75, end=cur_deg, fill=t['hot'], width=track_w)

        # Warning redline notch markings on outer rim
        d.arc([cx - (track_r + 4.5*s), cy - (track_r + 4.5*s), cx + (track_r + 4.5*s), cy + (track_r + 4.5*s)],
              start=deg_75, end=405, fill=t['hot'], width=int(1.2 * s))

        # 3. Ticks & Numbers
        for t_val in range(0, 101, 10):
            frac = t_val / 100.0
            angle_deg = start_deg + frac * sweep
            rad = math.radians(angle_deg)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)

            is_major = (t_val % 20 == 0)
            len_tick = (8 * s) if is_major else (4 * s)
            tick_w = int(2 * s) if is_major else int(1 * s)

            p1 = (cx + (track_r - track_w/2.0 - 2*s) * cos_a, cy + (track_r - track_w/2.0 - 2*s) * sin_a)
            p2 = (cx + (track_r - track_w/2.0 - 2*s - len_tick) * cos_a, cy + (track_r - track_w/2.0 - 2*s - len_tick) * sin_a)
            tick_col = t['tick_maj'] if is_major else t['tick_min']
            d.line([p1, p2], fill=tick_col, width=tick_w)

            if is_major:
                num_r = track_r - track_w/2.0 - 2*s - len_tick - (7 * s)
                tx = cx + num_r * cos_a
                ty = cy + num_r * sin_a
                txt = str(t_val)
                bbox = self.font_tick.getbbox(txt)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                d.text((tx - tw/2.0, ty - th/2.0), txt, fill=t['scale_txt'], font=self.font_tick)

        # 4. Needle (Drawn under the center hub overlay to guarantee zero text obstruction)
        n_rad = math.radians(cur_deg)
        n_cos = math.cos(n_rad)
        n_sin = math.sin(n_rad)
        perp_rad = math.radians(cur_deg + 90)
        p_cos = math.cos(perp_rad)
        p_sin = math.sin(perp_rad)

        hub_r = 30 * s
        needle_len = track_r + (2 * s)
        tip = (cx + needle_len * n_cos, cy + needle_len * n_sin)

        base_dist = hub_r * 0.70
        w_base = 3.5 * s
        w_mid = 1.8 * s
        mid_dist = (base_dist + needle_len) * 0.50

        b_left = (cx + base_dist * n_cos + w_base * p_cos, cy + base_dist * n_sin + w_base * p_sin)
        b_right = (cx + base_dist * n_cos - w_base * p_cos, cy + base_dist * n_sin - w_base * p_sin)
        m_left = (cx + mid_dist * n_cos + w_mid * p_cos, cy + mid_dist * n_sin + w_mid * p_sin)
        m_right = (cx + mid_dist * n_cos - w_mid * p_cos, cy + mid_dist * n_sin - w_mid * p_sin)

        # Luminous needle glow
        d.line([(cx + base_dist * n_cos, cy + base_dist * n_sin), tip], fill=t['needle_glow'], width=int(6 * s))
        # Needle blade polygon
        d.polygon([b_left, m_left, tip, m_right, b_right], fill=t['needle'], outline=(255, 255, 255, 240), width=int(1 * s))
        # Needle central sharp highlight spine
        d.line([(cx + base_dist * n_cos, cy + base_dist * n_sin), tip], fill=t['needle_spine'], width=int(1.2 * s))

        # 5. Center Hub Overlay (solid hub like the previous UI, with the
        #    digital temperature readout in the middle of the needle circle)
        d.ellipse([cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r], fill=t['hub_bg'], outline=t['hub_border'], width=int(2 * s))
        d.ellipse([cx - (hub_r - 2*s), cy - (hub_r - 2*s), cx + (hub_r - 2*s), cy + (hub_r - 2*s)], outline=t['bezel_inner'], width=int(1 * s))

        # Digital temperature readout in the center of the hub (font 15*s)
        txt_t = f"{self.display_temp:.1f}°" if self.has_data else "--°"
        bbox_t = self.font_temp.getbbox(txt_t)
        tw_t = bbox_t[2] - bbox_t[0]
        th_t = bbox_t[3] - bbox_t[1]
        d.text((cx - tw_t/2.0, cy - th_t/2.0 - 4*s), txt_t, fill=t['hub_text'], font=self.font_temp)

        # Core badge (bigger, below the hub)
        txt_c = self.core_label.upper() if self.has_data else "SENSOR OFF"
        bbox_c = self.font_min_lbl.getbbox(txt_c)
        tw_c = bbox_c[2] - bbox_c[0]
        th_c = bbox_c[3] - bbox_c[1]
        d.text((cx - tw_c/2.0, cy + (hub_r + 6*s)), txt_c, fill=t['hub_sub'], font=self.font_min_lbl)

        # 6. Downsample with LANCZOS to the fixed widget size (4K supersampled look)
        final_img = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
        return final_img

    def _anim_loop(self):
        """Fluid 60 FPS animation loop with spring/lerp needle movement."""
        if not self.running:
            return

        # Smooth lerp physics
        diff = self.target_temp - self.display_temp
        if abs(diff) > 0.02:
            self.display_temp += diff * 0.14
        else:
            self.display_temp = self.target_temp

        # Render frame
        try:
            gauge_img = self.render_gauge_image()

            # Handle transparency
            if self.transparent_circle:
                # Composite onto transparent mask color
                bg_mask = Image.new('RGBA', (self.size, self.size), (0, 0, 1, 255))
                final = Image.alpha_composite(bg_mask, gauge_img)
            else:
                final = gauge_img

            self.photo_image = ImageTk.PhotoImage(final)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
        except Exception:
            pass

        if self.running and self.root:
            self.root.after(16, self._anim_loop)  # ~60 FPS

    def _start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() - self._drag_start_x + event.x
        y = self.root.winfo_y() - self._drag_start_y + event.y
        self.root.geometry(f"+{x}+{y}")

    def _show_context_menu(self, event):
        self._build_context_menu()
        if self.context_menu:
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def _start_sensor_service(self):
        if not start_sensor_helper():
            self.sensor_error = "Sensor Service tidak dapat dimulai (UAC ditolak?)"

    def _open_log_dir(self):
        try:
            os.startfile(get_log_dir())
        except Exception:
            pass

    def _create_tray_image(self):
        """Build a small tray icon image (a colored circle)."""
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        t = THEMES.get(self.current_theme, THEMES['dark_luxury'])
        d.ellipse([4, 4, size - 4, size - 4], fill=t['needle'], outline=t['bezel_outer'], width=3)
        d.ellipse([size//2 - 6, size//2 - 6, size//2 + 6, size//2 + 6], fill=t['needle_spine'])
        return img

    def _hide_to_tray(self):
        if self.root:
            try:
                self.root.withdraw()
            except Exception:
                pass

    def _show_window(self):
        if self.root:
            try:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
            except Exception:
                pass

    def _exit_app(self):
        self._exit_requested = True
        self.running = False
        if self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass

    def _set_theme_from_tray(self, theme_key):
        def _apply():
            if theme_key in THEMES:
                self.current_theme = theme_key
                self._build_context_menu()
        if self.root:
            try:
                self.root.after(0, _apply)
            except Exception:
                _apply()

    def _start_tray(self):
        def on_show(icon, item):
            if self.root:
                self.root.after(0, self._show_window)

        def on_exit(icon, item):
            if self.root:
                self.root.after(0, self._exit_app)

        def make_theme_action(key):
            def action(icon, item):
                self._set_theme_from_tray(key)
            return action

        theme_items = [Item(th_info["name"], make_theme_action(k)) for k, th_info in THEMES.items()]

        menu = Menu(
            Item("Tampilkan", on_show, default=True),
            Menu.SEPARATOR,
            Item("Tema", Menu(*theme_items)),
            Menu.SEPARATOR,
            Item("Keluar", on_exit),
        )

        self.tray_icon = pystray.Icon("CpuCore0Meter", self._create_tray_image(), "CpuCore0Meter", menu)
        try:
            self.tray_icon.run()
        except Exception:
            pass

    def _build_context_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg="#161b22", fg="#f0f6fc", activebackground="#1f6feb", activeforeground="#ffffff")

        # Theme Submenu
        theme_menu = tk.Menu(menu, tearoff=0, bg="#161b22", fg="#f0f6fc", activebackground="#1f6feb", activeforeground="#ffffff")
        for th_key, th_info in THEMES.items():
            theme_menu.add_command(label=th_info["name"], command=lambda k=th_key: self.set_theme(k))
        menu.add_cascade(label="Tema (Theme)", menu=theme_menu)

        # Sensor status / service section
        menu.add_separator()
        menu.add_command(
            label="Sensor: AKTIF" if self.has_data else "Sensor: TIDAK AKTIF",
            state="disabled",
        )
        requires_helper = False
        if hasattr(self.sensor_monitor, 'requires_helper'):
            try:
                requires_helper = bool(self.sensor_monitor.requires_helper())
            except Exception:
                requires_helper = False
        if requires_helper and not is_helper_running():
            menu.add_command(label="Mulai Sensor Service (Admin)", command=self._start_sensor_service)
        elif requires_helper:
            menu.add_command(label="✓ Sensor Service (Admin) Berjalan", state="disabled")
        menu.add_command(label="Buka Folder Log Sensor", command=self._open_log_dir)
        menu.add_separator()

        # Window Options
        menu.add_separator()
        menu.add_command(
            label="✓ Selalu di Atas (Always On Top)" if self.always_on_top else "  Selalu di Atas (Always On Top)",
            command=self.toggle_always_on_top
        )
        menu.add_command(
            label="✓ Lingkaran Melayang (Transparent)" if self.transparent_circle else "  Lingkaran Melayang (Transparent)",
            command=self.toggle_transparent_circle
        )
        is_auto = is_autostart_enabled()
        menu.add_command(
            label="✓ Buka Otomatis saat Mesin Dinyalakan" if is_auto else "  Buka Otomatis saat Mesin Dinyalakan",
            command=self.toggle_autostart
        )

        # Opacity Submenu
        op_menu = tk.Menu(menu, tearoff=0, bg="#161b22", fg="#f0f6fc", activebackground="#1f6feb", activeforeground="#ffffff")
        op_menu.add_command(label="100%", command=lambda: self.set_opacity(1.0))
        op_menu.add_command(label="90%", command=lambda: self.set_opacity(0.9))
        op_menu.add_command(label="80%", command=lambda: self.set_opacity(0.8))
        menu.add_cascade(label="Transparansi Jendela", menu=op_menu)

        menu.add_separator()
        menu.add_command(label="🔽 Sembunyikan ke Tray", command=self._hide_to_tray)
        menu.add_command(label="❌ Keluar", command=self._exit_app)

        self.context_menu = menu

    def toggle_autostart(self):
        current = is_autostart_enabled()
        set_autostart(not current)
        self._build_context_menu()

    def set_theme(self, theme_key):
        if theme_key in THEMES:
            self.current_theme = theme_key
            self._build_context_menu()

    def set_opacity(self, op):
        self.opacity = op
        if self.root:
            self.root.wm_attributes("-alpha", self.opacity)

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        if self.root:
            self.root.wm_attributes("-topmost", self.always_on_top)
        self._build_context_menu()

    def toggle_transparent_circle(self):
        self.transparent_circle = not self.transparent_circle
        if self.root:
            if self.transparent_circle:
                self.root.wm_attributes("-transparentcolor", "#000001")
                self.canvas.config(bg="#000001")
            else:
                self.root.wm_attributes("-transparentcolor", "")
                self.canvas.config(bg="#0d1117")
        self._build_context_menu()

    def init_UI(self):
        self.root = tk.Tk()
        self.root.title("CPU Core 0 Compact Gauge")
        self.root.geometry(f"{self.size}x{self.size}+100+100")
        self.root.overrideredirect(True)  # Frameless floating widget
        self.root.wm_attributes("-topmost", self.always_on_top)
        self.root.wm_attributes("-alpha", self.opacity)

        # Transparent circular shape
        if self.transparent_circle:
            try:
                self.root.wm_attributes("-transparentcolor", "#000001")
                bg_color = "#000001"
            except Exception:
                self.transparent_circle = False
                bg_color = "#0d1117"
        else:
            bg_color = "#0d1117"

        self.canvas = tk.Canvas(
            self.root,
            width=self.size,
            height=self.size,
            bg=bg_color,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Drag bindings
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._on_drag)

        # Context menu
        self.canvas.bind("<Button-3>", self._show_context_menu)

        self._build_context_menu()

    def run(self):
        self.init_UI()

        # Start hardware sensor polling
        self.poll_thread = threading.Thread(target=self._polling_worker, daemon=True)
        self.poll_thread.start()

        # Read initial temperature
        try:
            cores = self.sensor_monitor.get_core_temperatures()
            if cores:
                core_obj = None
                for idx, c in enumerate(cores):
                    if idx == self.target_core_index or c.label == f"Core {self.target_core_index}":
                        core_obj = c
                        break
                if core_obj is None:
                    core_obj = cores[0]
                c = core_obj
                self.target_temp = float(c.current)
                self.display_temp = self.target_temp
                self.core_label = c.label
                self.has_data = True
        except Exception:
            self.has_data = False

        # Start 60 FPS animation loop
        self._anim_loop()

        # Start system tray icon in a background thread
        tray_thread = threading.Thread(target=self._start_tray, daemon=True)
        tray_thread.start()

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            if self.tray_icon is not None:
                try:
                    self.tray_icon.stop()
                except Exception:
                    pass
            self.sensor_monitor.close()

    def request_stop(self):
        # Hide to tray instead of quitting; use _exit_app to really quit.
        self._hide_to_tray()
