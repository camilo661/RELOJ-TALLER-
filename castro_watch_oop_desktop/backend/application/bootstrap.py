"""Object graph composition for the desktop application."""

import tkinter as tk

from backend.application.clock_engine import ClockEngineSingleton
from backend.application.state_mutator import ClockStateMutator
from frontend.ui.config_panel import ConfigPanelView
from frontend.ui.geometry import GeometryFactory
from frontend.ui.hit_testing import WatchHitTester
from frontend.ui.renderer import WatchRenderer
from frontend.ui.themes import ThemeRegistry
from frontend.ui.window import DesktopApplication


class ApplicationBootstrapper:
    """Builds the OOP desktop watch application."""

    def build(self) -> DesktopApplication:
        engine = ClockEngineSingleton.instance()
        root = tk.Tk()
        root.title("CASTRO Watch OOP")
        root.geometry("860x960")
        root.minsize(680, 820)

        outer = tk.Frame(root)
        outer.pack(fill="both", expand=True, padx=18, pady=18)
        canvas = tk.Canvas(outer, width=760, height=700, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        themes = ThemeRegistry()
        renderer = WatchRenderer(canvas, themes, GeometryFactory())
        hit_tester = WatchHitTester()
        mutator = ClockStateMutator()

        application: DesktopApplication | None = None
        config_panel = ConfigPanelView(outer, themes, lambda theme: application.set_theme(theme))

        application = DesktopApplication(
            engine=engine,
            renderer=renderer,
            hit_tester=hit_tester,
            mutator=mutator,
            config_panel=config_panel,
            root=root,
            canvas=canvas,
            outer=outer,
        )

        root.protocol("WM_DELETE_WINDOW", lambda: self._close(root, engine))
        return application

    def _close(self, root: tk.Tk, engine) -> None:
        engine.stop()
        root.destroy()
