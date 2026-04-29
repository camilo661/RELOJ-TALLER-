"""Main desktop window controller."""

import math
import tkinter as tk

from backend.application.clock_engine import ClockEngine
from backend.application.state_mutator import ClockStateMutator
from backend.domain.clock_snapshot import ClockSnapshot
from frontend.ui.config_panel import ConfigPanelView
from frontend.ui.hit_testing import WatchHitTester
from frontend.ui.renderer import WatchRenderer


class DesktopApplication:
    """High-level composition root for the desktop watch UI."""

    COMMIT_DELAY_MS = 180
    DRAG_PIXEL_STEP = 18

    def __init__(
        self,
        *,
        engine: ClockEngine,
        renderer: WatchRenderer,
        hit_tester: WatchHitTester,
        mutator: ClockStateMutator,
        config_panel: ConfigPanelView,
        root: tk.Tk,
        canvas: tk.Canvas,
        outer: tk.Frame,
    ):
        self._engine = engine
        self._renderer = renderer
        self._hit_tester = hit_tester
        self._mutator = mutator
        self._config_panel = config_panel
        self._root = root
        self._canvas = canvas
        self._outer = outer
        self._snapshot = engine.snapshot()
        self._config_open = False
        self._active_drag: dict | None = None
        self._commit_job: str | None = None

        self._renderer.set_snapshot(self._snapshot)
        self._renderer.set_theme("white")
        self._apply_theme_visuals()

        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<ButtonPress-1>", self._on_pointer_down)
        self._canvas.bind("<B1-Motion>", self._on_pointer_move)
        self._canvas.bind("<ButtonRelease-1>", self._on_pointer_up)
        self._canvas.bind("<MouseWheel>", self._on_wheel)
        self._root.bind("<Escape>", lambda _event: self._toggle_config(False))

        self._render_loop()
        self._poll_loop()

    def run(self) -> None:
        self._engine.start()
        self._root.mainloop()

    def set_theme(self, theme: str) -> None:
        self._renderer.set_theme(theme)
        self._config_panel.apply_theme(theme)
        self._apply_theme_visuals()
        self._renderer.draw()

    def _apply_theme_visuals(self) -> None:
        palette = self._renderer.palette()
        self._root.configure(bg=palette.background)
        self._outer.configure(bg=palette.background)
        self._canvas.configure(bg=palette.background)
        self._config_panel.apply_theme(self._renderer.theme_name())

    def _toggle_config(self, force_state: bool | None = None) -> None:
        next_state = (not self._config_open) if force_state is None else force_state
        if next_state == self._config_open:
            return
        self._config_open = next_state
        self._renderer.set_interactive_mode(self._config_open)
        self._renderer.set_config_open(self._config_open)
        if self._config_open:
            self._config_panel.pack()
            self._engine.stop()
            self._snapshot = self._engine.snapshot()
        else:
            self._config_panel.pack_forget()
            self._commit_snapshot(self._snapshot)
            self._engine.start()
            self._snapshot = self._engine.snapshot()
        self._renderer.set_snapshot(self._snapshot)
        self._renderer.draw()

    def _render_loop(self) -> None:
        self._renderer.draw()
        self._root.after(40, self._render_loop)

    def _poll_loop(self) -> None:
        if not self._config_open and not self._active_drag:
            self._snapshot = self._engine.snapshot()
            self._renderer.set_snapshot(self._snapshot)
        self._root.after(500, self._poll_loop)

    def _on_pointer_down(self, event: tk.Event) -> None:
        geometry = self._renderer.geometry()
        if geometry is None:
            return
        hit = self._hit_tester.hit_test(event.x, event.y, geometry)
        if hit and hit.zone == "crown":
            self._toggle_config()
            return
        if not self._config_open or hit is None or hit.angle is None:
            return
        self._clear_pending_commit()
        self._active_drag = {
            "zone": hit.zone,
            "last_angle": hit.angle,
            "angle_carry": 0.0,
            "last_y": event.y,
            "pixel_carry": 0.0,
            "initial_snapshot": self._snapshot,
        }

    def _on_pointer_move(self, event: tk.Event) -> None:
        if not self._active_drag:
            return
        geometry = self._renderer.geometry()
        if geometry is None:
            return
        zone = self._active_drag["zone"]
        if zone in {"minute", "hour"}:
            hit = self._hit_tester.hit_test(event.x, event.y, geometry)
            if hit is None or hit.angle is None:
                return
            step_angle = math.tau / 60 if zone == "minute" else math.tau / 12
            self._active_drag["angle_carry"] += self._short_angle_delta(hit.angle - self._active_drag["last_angle"])
            self._active_drag["last_angle"] = hit.angle
            steps = self._consume_angular_steps(step_angle)
            if steps:
                self._snapshot = self._mutator.shift_minutes(self._snapshot, steps) if zone == "minute" else self._mutator.shift_hours(self._snapshot, steps)
        else:
            self._active_drag["pixel_carry"] += event.y - self._active_drag["last_y"]
            self._active_drag["last_y"] = event.y
            steps = self._consume_pixel_steps()
            if steps:
                self._snapshot = self._mutator.shift_months(self._snapshot, steps) if zone == "month" else self._mutator.shift_days(self._snapshot, steps)
        self._renderer.set_snapshot(self._snapshot)

    def _on_pointer_up(self, _event: tk.Event) -> None:
        if not self._active_drag:
            return
        initial_snapshot = self._active_drag["initial_snapshot"]
        self._active_drag = None
        if initial_snapshot == self._snapshot:
            return
        if self._config_open:
            self._commit_snapshot(self._snapshot)

    def _on_wheel(self, event: tk.Event) -> None:
        if not self._config_open:
            return
        geometry = self._renderer.geometry()
        if geometry is None:
            return
        hit = self._hit_tester.hit_test(event.x, event.y, geometry)
        if hit is None or hit.zone not in {"weekday", "day", "month"}:
            return
        self._clear_pending_commit()
        amount = 1 if event.delta > 0 else -1
        self._snapshot = self._mutator.shift_months(self._snapshot, amount) if hit.zone == "month" else self._mutator.shift_days(self._snapshot, amount)
        self._renderer.set_snapshot(self._snapshot)
        self._commit_job = self._root.after(self.COMMIT_DELAY_MS, lambda: self._commit_snapshot(self._snapshot))

    def _commit_snapshot(self, snapshot: ClockSnapshot) -> None:
        self._clear_pending_commit()
        self._engine.set_snapshot(
            year=snapshot.year,
            month=snapshot.month,
            day=snapshot.day_of_month,
            hour=snapshot.hour,
            minute=snapshot.minute,
            second=snapshot.second,
        )
        self._snapshot = self._engine.snapshot()
        self._renderer.set_snapshot(self._snapshot)

    def _clear_pending_commit(self) -> None:
        if self._commit_job is not None:
            self._root.after_cancel(self._commit_job)
            self._commit_job = None

    def _consume_angular_steps(self, step_angle: float) -> int:
        carry = self._active_drag["angle_carry"]
        steps = math.floor(carry / step_angle) if carry >= 0 else math.ceil(carry / step_angle)
        if steps:
            self._active_drag["angle_carry"] -= steps * step_angle
        return steps

    def _consume_pixel_steps(self) -> int:
        carry = self._active_drag["pixel_carry"]
        steps = math.floor(carry / self.DRAG_PIXEL_STEP) if carry >= 0 else math.ceil(carry / self.DRAG_PIXEL_STEP)
        if steps:
            self._active_drag["pixel_carry"] -= steps * self.DRAG_PIXEL_STEP
        return -steps

    def _short_angle_delta(self, delta: float) -> float:
        if delta > math.pi:
            return delta - math.tau
        if delta < -math.pi:
            return delta + math.tau
        return delta

    def _on_canvas_configure(self, _event: tk.Event) -> None:
        self._renderer.draw()
