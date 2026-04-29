"""Canvas renderer for the analog desktop watch."""

import math
import time
import tkinter as tk

from backend.domain.clock_snapshot import ClockSnapshot
from frontend.ui.geometry import GeometryFactory, Point, WatchGeometry
from frontend.ui.themes import ThemeRegistry, WatchPalette


class WatchRenderer:
    """Responsible for drawing the full watch."""

    ROMAN = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
    DAYS_SHORT = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
    DAYS_RING = ["L", "M", "X", "J", "V", "S", "D"]
    MONTHS_SHORT = ["", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    MONTHS_RING = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]

    def __init__(self, canvas: tk.Canvas, themes: ThemeRegistry, geometry_factory: GeometryFactory):
        self._canvas = canvas
        self._themes = themes
        self._geometry_factory = geometry_factory
        self._theme_name = "white"
        self._interactive_mode = False
        self._config_open = False
        self._snapshot = ClockSnapshot(0, 0, 0, 0, 1, 1, 2026, True)
        self._last_server_second = -1
        self._base_timestamp = time.perf_counter()

    def set_theme(self, name: str) -> None:
        self._theme_name = "black" if name == "black" else "white"

    def theme_name(self) -> str:
        return self._theme_name

    def palette(self) -> WatchPalette:
        return self._themes.get(self._theme_name)

    def set_snapshot(self, snapshot: ClockSnapshot) -> None:
        if snapshot.running and (not self._snapshot.running or snapshot.second != self._last_server_second):
            self._base_timestamp = time.perf_counter()
            self._last_server_second = snapshot.second
        self._snapshot = snapshot

    def set_interactive_mode(self, enabled: bool) -> None:
        self._interactive_mode = enabled

    def set_config_open(self, enabled: bool) -> None:
        self._config_open = enabled

    def geometry(self) -> WatchGeometry | None:
        width = max(self._canvas.winfo_width(), 0)
        height = max(self._canvas.winfo_height(), 0)
        if width <= 0 or height <= 0:
            return None
        return self._geometry_factory.create(width, height)

    def draw(self) -> None:
        geometry = self.geometry()
        if geometry is None:
            return
        palette = self.palette()
        self._canvas.delete("all")
        self._canvas.configure(bg=palette.background)
        self._draw_case(geometry, palette)
        self._draw_crown(geometry, palette)
        self._draw_face(geometry, palette)
        self._draw_markers(geometry, palette)
        self._draw_subdials(geometry, palette)
        self._draw_brand_text(geometry, palette)
        self._draw_hands(geometry, palette)
        if self._interactive_mode:
            self._draw_interaction_hints(geometry, palette)

    def _draw_case(self, geometry: WatchGeometry, palette: WatchPalette) -> None:
        cx, cy, radius = geometry.center.x, geometry.center.y, geometry.radius
        for offset, fill, outline, width in (
            (30, palette.outer_case, palette.outer_case_dark, 3),
            (22, palette.outer_case_dark, "#3a2a12", 2),
            (12, palette.mid_case, "#2f2418", 2),
        ):
            self._canvas.create_oval(
                cx - radius - offset,
                cy - radius - offset,
                cx + radius + offset,
                cy + radius + offset,
                fill=fill,
                outline=outline,
                width=width,
            )

    def _draw_crown(self, geometry: WatchGeometry, palette: WatchPalette) -> None:
        crown = geometry.crown
        self._canvas.create_oval(
            crown.x1 - 14,
            (crown.y1 + crown.y2) / 2 - 24,
            crown.x1 + 10,
            (crown.y1 + crown.y2) / 2 + 24,
            fill=palette.mid_case,
            outline="#2f2418",
            width=1,
        )
        self._canvas.create_rectangle(
            crown.x1,
            crown.y1,
            crown.x2,
            crown.y2,
            fill=palette.crown_top if self._config_open else palette.crown_bottom,
            outline="#4b3717",
            width=2,
        )
        ridge_step = max((crown.y2 - crown.y1) / 8, 6)
        ridge_y = crown.y1 + ridge_step / 2
        while ridge_y < crown.y2:
            self._canvas.create_line(crown.x1 + 3, ridge_y, crown.x2 - 3, ridge_y, fill="#543d17", width=1)
            ridge_y += ridge_step

    def _draw_face(self, geometry: WatchGeometry, palette: WatchPalette) -> None:
        cx, cy, radius = geometry.center.x, geometry.center.y, geometry.radius
        self._canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=palette.face_outer, outline=palette.rim_dark, width=5)
        self._canvas.create_oval(cx - radius * 0.97, cy - radius * 0.97, cx + radius * 0.97, cy + radius * 0.97, fill=palette.face_mid, outline=palette.rim, width=3)
        self._canvas.create_oval(cx - radius * 0.91, cy - radius * 0.91, cx + radius * 0.91, cy + radius * 0.91, fill=palette.face_inner, outline="")
        self._canvas.create_oval(cx - radius * 0.77, cy - radius * 0.77, cx + radius * 0.77, cy + radius * 0.77, outline=palette.rim, width=1)

    def _draw_markers(self, geometry: WatchGeometry, palette: WatchPalette) -> None:
        cx, cy, radius = geometry.center.x, geometry.center.y, geometry.radius
        for index in range(60):
            angle = (index / 60) * math.tau - math.pi / 2
            is_hour = index % 5 == 0
            is_quarter = index % 15 == 0
            outer = radius * 0.92
            inner = radius * (0.74 if is_quarter else 0.8 if is_hour else 0.87)
            color = palette.marker_quarter if is_quarter else palette.marker_major if is_hour else palette.marker_minor
            width = 3 if is_quarter else 2 if is_hour else 1
            self._radial_line(cx, cy, outer, inner, angle, color, width)

        label_radius = radius * 0.65
        for index, label in enumerate(self.ROMAN):
            angle = (index / 12) * math.tau - math.pi / 2
            x = cx + label_radius * math.cos(angle)
            y = cy + label_radius * math.sin(angle)
            font_size = max(int(radius * (0.09 if index % 3 == 0 else 0.072)), 12)
            self._canvas.create_text(x, y, text=label, fill=palette.roman, font=("Times New Roman", font_size, "bold" if index % 3 == 0 else "normal"))

        top_marker = radius * 0.82
        self._canvas.create_polygon(cx, cy - top_marker - 12, cx + 7, cy - top_marker, cx, cy - top_marker + 12, cx - 7, cy - top_marker, fill=palette.marker_major, outline="")

    def _draw_subdials(self, geometry: WatchGeometry, palette: WatchPalette) -> None:
        self._draw_subdial(geometry.weekday_center, geometry.sub_radius, 7, self._snapshot.day_of_week % 7, self.DAYS_SHORT[self._snapshot.day_of_week], self.DAYS_RING, palette, center_y_ratio=0.36, center_font_ratio=0.14, ring_label_radius_ratio=0.68, ring_font_ratio=0.09, tick_major_inner_ratio=0.78, tick_minor_inner_ratio=0.84)
        self._draw_subdial(geometry.day_center, geometry.sub_radius, 31, max(self._snapshot.day_of_month - 1, 0), f"{self._snapshot.day_of_month:02d}", None, palette, major_marks=((0, "1"), (7, "8"), (15, "16"), (23, "24")), center_y_ratio=0.36, center_font_ratio=0.14, major_label_radius_ratio=0.66, major_font_ratio=0.1, tick_major_inner_ratio=0.78, tick_minor_inner_ratio=0.85)
        self._draw_subdial(geometry.month_center, geometry.sub_radius, 12, max(self._snapshot.month - 1, 0), self.MONTHS_SHORT[self._snapshot.month], self.MONTHS_RING, palette, center_y_ratio=0.5, center_font_ratio=0.16, ring_label_radius_ratio=0.68, ring_font_ratio=0.09, tick_major_inner_ratio=0.79, tick_minor_inner_ratio=0.85)

    def _draw_subdial(self, center: Point, radius: float, steps: int, value_index: int, center_text: str, ring_labels: list[str] | None, palette: WatchPalette, *, major_marks: tuple[tuple[int, str], ...] = (), center_y_ratio: float = 0.43, center_font_ratio: float = 0.2, ring_label_radius_ratio: float = 0.58, ring_font_ratio: float = 0.15, major_label_radius_ratio: float = 0.55, major_font_ratio: float = 0.16, tick_major_inner_ratio: float = 0.68, tick_minor_inner_ratio: float = 0.76) -> None:
        self._canvas.create_oval(center.x - radius, center.y - radius, center.x + radius, center.y + radius, fill=palette.sub_outer, outline=palette.sub_stroke, width=1)
        self._canvas.create_oval(center.x - radius * 0.88, center.y - radius * 0.88, center.x + radius * 0.88, center.y + radius * 0.88, fill=palette.sub_inner, outline="")
        for step in range(steps):
            angle = (step / steps) * math.tau - math.pi / 2
            is_major = steps <= 12 or step % 5 == 0
            inner = radius * (tick_major_inner_ratio if is_major else tick_minor_inner_ratio)
            self._radial_line(center.x, center.y, radius * 0.92, inner, angle, palette.sub_tick, 1)
        if ring_labels:
            for step, label in enumerate(ring_labels):
                angle = (step / len(ring_labels)) * math.tau - math.pi / 2
                label_radius = radius * ring_label_radius_ratio
                x = center.x + label_radius * math.cos(angle)
                y = center.y + label_radius * math.sin(angle)
                self._canvas.create_text(x, y, text=label, fill=palette.sub_text, font=("Times New Roman", max(int(radius * ring_font_ratio), 6), "bold"))
        for step, label in major_marks:
            angle = (step / steps) * math.tau - math.pi / 2
            label_radius = radius * major_label_radius_ratio
            x = center.x + label_radius * math.cos(angle)
            y = center.y + label_radius * math.sin(angle)
            self._canvas.create_text(x, y, text=label, fill=palette.sub_text, font=("Times New Roman", max(int(radius * major_font_ratio), 6), "bold"))
        self._draw_tapered_hand(center.x, center.y, (value_index / steps) * math.tau - math.pi / 2, radius * 0.66, radius * 0.16, radius * 0.03, palette.cap_mid, palette.cap_low)
        self._canvas.create_oval(center.x - radius * 0.08, center.y - radius * 0.08, center.x + radius * 0.08, center.y + radius * 0.08, fill=palette.center_inner, outline="")
        self._canvas.create_text(center.x, center.y + radius * center_y_ratio, text=center_text, fill=palette.sub_text, font=("Times New Roman", max(int(radius * center_font_ratio), 8), "bold"))

    def _draw_brand_text(self, geometry: WatchGeometry, palette: WatchPalette) -> None:
        cx, cy, radius = geometry.center.x, geometry.center.y, geometry.radius
        self._canvas.create_text(cx, cy - radius * 0.215, text="CASTRO", fill=palette.brand, font=("Times New Roman", max(int(radius * 0.104), 18), "bold"))
        self._canvas.create_text(cx, cy - radius * 0.135, text="AUTOMATIC STYLE", fill=palette.tagline, font=("Georgia", max(int(radius * 0.028), 9), "italic"))

    def _draw_hands(self, geometry: WatchGeometry, palette: WatchPalette) -> None:
        cx, cy, radius = geometry.center.x, geometry.center.y, geometry.radius
        elapsed = 0.0 if not self._snapshot.running else time.perf_counter() - self._base_timestamp
        live_seconds = self._snapshot.second + elapsed
        second_fraction = live_seconds / 60
        minute_fraction = (self._snapshot.minute + live_seconds / 60) / 60
        hour_fraction = ((self._snapshot.hour % 12) + (self._snapshot.minute + live_seconds / 60) / 60) / 12
        self._draw_tapered_hand(cx, cy, hour_fraction * math.tau - math.pi / 2, radius * 0.5, radius * 0.16, radius * 0.06, palette.hour_fill, palette.hour_stroke)
        self._draw_tapered_hand(cx, cy, minute_fraction * math.tau - math.pi / 2, radius * 0.72, radius * 0.18, radius * 0.04, palette.minute_fill, palette.minute_stroke)
        self._draw_second_hand(cx, cy, radius, second_fraction * math.tau - math.pi / 2, palette)
        self._draw_center_cap(cx, cy, radius, palette)

    def _draw_second_hand(self, cx: float, cy: float, radius: float, angle: float, palette: WatchPalette) -> None:
        tip_x = cx + radius * 0.8 * math.cos(angle)
        tip_y = cy + radius * 0.8 * math.sin(angle)
        tail_x = cx + radius * 0.22 * math.cos(angle + math.pi)
        tail_y = cy + radius * 0.22 * math.sin(angle + math.pi)
        self._canvas.create_line(tail_x, tail_y, tip_x, tip_y, fill=palette.second, width=2, capstyle=tk.ROUND)
        weight_x = cx + radius * 0.14 * math.cos(angle + math.pi)
        weight_y = cy + radius * 0.14 * math.sin(angle + math.pi)
        self._canvas.create_oval(weight_x - radius * 0.032, weight_y - radius * 0.032, weight_x + radius * 0.032, weight_y + radius * 0.032, outline=palette.second, width=2)

    def _draw_center_cap(self, cx: float, cy: float, radius: float, palette: WatchPalette) -> None:
        self._canvas.create_oval(cx - radius * 0.04, cy - radius * 0.04, cx + radius * 0.04, cy + radius * 0.04, fill=palette.cap_mid, outline=palette.cap_low, width=1)
        self._canvas.create_oval(cx - radius * 0.015, cy - radius * 0.015, cx + radius * 0.015, cy + radius * 0.015, fill=palette.center_inner, outline="")

    def _draw_interaction_hints(self, geometry: WatchGeometry, palette: WatchPalette) -> None:
        cx, cy, radius = geometry.center.x, geometry.center.y, geometry.radius
        dash = (4, 6)
        self._canvas.create_oval(cx - radius * 0.5, cy - radius * 0.5, cx + radius * 0.5, cy + radius * 0.5, outline=palette.hint, dash=dash, width=1)
        self._canvas.create_oval(cx - radius * 0.72, cy - radius * 0.72, cx + radius * 0.72, cy + radius * 0.72, outline=palette.hint, dash=dash, width=1)
        for center in (geometry.weekday_center, geometry.day_center, geometry.month_center):
            sub_radius = geometry.sub_radius * 1.06
            self._canvas.create_oval(center.x - sub_radius, center.y - sub_radius, center.x + sub_radius, center.y + sub_radius, outline=palette.hint, dash=dash, width=1)

    def _draw_tapered_hand(self, cx: float, cy: float, angle: float, tip_length: float, tail_length: float, half_width: float, fill: str, outline: str) -> None:
        tip_x = cx + tip_length * math.cos(angle)
        tip_y = cy + tip_length * math.sin(angle)
        tail_x = cx + tail_length * math.cos(angle + math.pi)
        tail_y = cy + tail_length * math.sin(angle + math.pi)
        perp_x = -math.sin(angle)
        perp_y = math.cos(angle)
        shoulder = tip_length * 0.45
        points = [tail_x + perp_x * half_width * 0.35, tail_y + perp_y * half_width * 0.35, cx + perp_x * half_width, cy + perp_y * half_width, cx + shoulder * math.cos(angle) + perp_x * half_width * 0.3, cy + shoulder * math.sin(angle) + perp_y * half_width * 0.3, tip_x, tip_y, cx + shoulder * math.cos(angle) - perp_x * half_width * 0.3, cy + shoulder * math.sin(angle) - perp_y * half_width * 0.3, cx - perp_x * half_width, cy - perp_y * half_width, tail_x - perp_x * half_width * 0.35, tail_y - perp_y * half_width * 0.35]
        self._canvas.create_polygon(points, fill=fill, outline=outline, width=1, smooth=True)

    def _radial_line(self, cx: float, cy: float, outer: float, inner: float, angle: float, color: str, width: int) -> None:
        x1 = cx + outer * math.cos(angle)
        y1 = cy + outer * math.sin(angle)
        x2 = cx + inner * math.cos(angle)
        y2 = cy + inner * math.sin(angle)
        self._canvas.create_line(x1, y1, x2, y2, fill=color, width=width, capstyle=tk.ROUND)
