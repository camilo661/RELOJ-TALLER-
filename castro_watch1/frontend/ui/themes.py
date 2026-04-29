"""Theme models for the watch UI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WatchPalette:
    background: str
    outer_case: str
    outer_case_dark: str
    mid_case: str
    inner_case: str
    face_inner: str
    face_mid: str
    face_outer: str
    rim: str
    rim_dark: str
    marker_minor: str
    marker_major: str
    marker_quarter: str
    roman: str
    brand: str
    tagline: str
    hour_fill: str
    hour_stroke: str
    minute_fill: str
    minute_stroke: str
    second: str
    center_inner: str
    sub_inner: str
    sub_outer: str
    sub_stroke: str
    sub_tick: str
    sub_text: str
    hint: str
    cap_high: str
    cap_mid: str
    cap_low: str
    crown_top: str
    crown_bottom: str
    panel_bg: str
    panel_text: str


class ThemeRegistry:
    """Registry and simple factory for watch themes."""

    def __init__(self):
        self._themes = {
            "white": WatchPalette(
                "#090807", "#c7a24b", "#6f531d", "#2a2014", "#14100b",
                "#fffdf7", "#f2ead9", "#d7cab0", "#b89035", "#6b5120",
                "#8b7a58", "#c9a84c", "#a7771e", "#2b2013", "#2a1f12",
                "#756445", "#2d2213", "#dab45a", "#221a10", "#efcf7d",
                "#9f3a2f", "#9f3a2f", "#f5ecdc", "#ddd0b1", "#c8a449",
                "#897653", "#674e1f", "#d7b965", "#f0d78d", "#c8a449",
                "#7a5d24", "#e3c97f", "#7b5a23", "#16120d", "#d8ccb0",
            ),
            "black": WatchPalette(
                "#090807", "#d0ad58", "#74571f", "#21180f", "#100d09",
                "#2d271f", "#17130f", "#090807", "#d4b15e", "#6a5121",
                "#9f8850", "#e2c56f", "#f0d88e", "#dcc06d", "#dcc06d",
                "#8d7a45", "#c6a351", "#f4dfac", "#d8b764", "#f6e5b8",
                "#c55a49", "#c55a49", "#242019", "#12100d", "#cfae5c",
                "#ae965a", "#e6ce84", "#d8bf73", "#f3dfb0", "#d2b060",
                "#7e611f", "#e2c97f", "#7b5922", "#14110d", "#d9cdaf",
            ),
        }

    def get(self, name: str) -> WatchPalette:
        return self._themes["black" if name == "black" else "white"]
