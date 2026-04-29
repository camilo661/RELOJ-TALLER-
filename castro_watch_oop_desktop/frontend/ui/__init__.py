"""User interface layer for CASTRO Watch."""

from frontend.ui.config_panel import ConfigPanelView
from frontend.ui.geometry import CrownBounds, GeometryFactory, Point, WatchGeometry
from frontend.ui.hit_testing import HitZone, WatchHitTester
from frontend.ui.renderer import WatchRenderer
from frontend.ui.themes import ThemeRegistry, WatchPalette
from frontend.ui.window import DesktopApplication

__all__ = [
    "ConfigPanelView",
    "CrownBounds",
    "DesktopApplication",
    "GeometryFactory",
    "HitZone",
    "Point",
    "ThemeRegistry",
    "WatchGeometry",
    "WatchHitTester",
    "WatchPalette",
    "WatchRenderer",
]
