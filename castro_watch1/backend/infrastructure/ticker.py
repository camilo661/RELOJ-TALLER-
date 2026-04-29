"""Background ticker infrastructure."""

import threading
import time
from collections.abc import Callable


class BackgroundTicker:
    """Drives a periodic callback on a daemon thread."""

    def __init__(self, interval_seconds: float, callback: Callable[[], None]):
        self._interval_seconds = interval_seconds
        self._callback = callback
        self._running = False
        self._thread: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            time.sleep(self._interval_seconds)
            if not self._running:
                break
            self._callback()
