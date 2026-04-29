"""Config panel widgets for the desktop app."""

import tkinter as tk
from collections.abc import Callable

from frontend.ui.themes import ThemeRegistry


class ConfigPanelView:
    """Panel responsible for dial theme selection and guidance copy."""

    def __init__(self, parent: tk.Widget, themes: ThemeRegistry, on_theme_selected: Callable[[str], None]):
        self._themes = themes
        self._on_theme_selected = on_theme_selected
        self.frame = tk.Frame(parent, highlightthickness=1, padx=18, pady=18)

        top_row = tk.Frame(self.frame)
        top_row.pack(fill="x")
        self._title_label = tk.Label(top_row, text="Dial", font=("Times New Roman", 15, "bold"))
        self._title_label.pack(side="left")
        self._swatch_row = tk.Frame(top_row)
        self._swatch_row.pack(side="right")

        self._swatches: dict[str, tk.Canvas] = {}
        for theme in ("white", "black"):
            swatch = tk.Canvas(self._swatch_row, width=54, height=54, highlightthickness=0, bd=0, cursor="hand2")
            swatch.pack(side="left", padx=6)
            swatch.bind("<Button-1>", lambda _event, selected=theme: self._on_theme_selected(selected))
            self._swatches[theme] = swatch

        self._divider = tk.Frame(self.frame, height=1)
        self._divider.pack(fill="x", pady=14)

        self._guides: list[tuple[tk.Frame, tk.Label, tk.Label]] = []
        for title, copy in (
            ("Time", "Drag the outer ring for minutes and the inner ring for hours."),
            ("Date", "Use the mouse wheel or a short vertical drag on the day, weekday, and month subdials."),
            ("Crown", "The side crown opens the workshop and keeps the watch language tactile instead of digital."),
        ):
            block = tk.Frame(self.frame, padx=12, pady=10)
            block.pack(fill="x", pady=5)
            title_label = tk.Label(block, text=title, font=("Times New Roman", 13, "bold"), anchor="w")
            title_label.pack(fill="x")
            copy_label = tk.Label(block, text=copy, font=("Georgia", 11), justify="left", wraplength=720, anchor="w")
            copy_label.pack(fill="x", pady=(4, 0))
            self._guides.append((block, title_label, copy_label))

    def pack(self) -> None:
        self.frame.pack(fill="x", pady=(12, 0))

    def pack_forget(self) -> None:
        self.frame.pack_forget()

    def apply_theme(self, active_theme: str) -> None:
        palette = self._themes.get(active_theme)
        self.frame.configure(bg=palette.panel_bg, highlightbackground=palette.rim)
        self._title_label.configure(bg=palette.panel_bg, fg=palette.marker_major)
        self._swatch_row.configure(bg=palette.panel_bg)
        self._divider.configure(bg=palette.rim_dark)

        for block, title_label, copy_label in self._guides:
            block.configure(bg="#1B1611")
            title_label.configure(bg="#1B1611", fg=palette.marker_major)
            copy_label.configure(bg="#1B1611", fg=palette.panel_text)

        for theme_name, swatch in self._swatches.items():
            self._draw_swatch(swatch, theme_name, active_theme)

    def _draw_swatch(self, swatch: tk.Canvas, theme_name: str, active_theme: str) -> None:
        host_palette = self._themes.get(active_theme)
        sample_palette = self._themes.get(theme_name)
        swatch.configure(bg=host_palette.panel_bg)
        swatch.delete("all")
        outline = host_palette.marker_major if theme_name == active_theme else host_palette.rim_dark
        swatch.create_oval(4, 4, 50, 50, fill=host_palette.panel_bg, outline=outline, width=2)
        swatch.create_oval(10, 10, 44, 44, fill=sample_palette.face_mid, outline=sample_palette.rim, width=2)
        swatch.create_oval(14, 14, 40, 40, fill=sample_palette.face_inner, outline="")
