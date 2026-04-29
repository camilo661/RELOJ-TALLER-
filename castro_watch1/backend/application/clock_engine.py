"""Clock engine service and singleton provider."""

import datetime as dt
import threading

from backend.domain.clock_snapshot import ClockSnapshot
from backend.domain.watch_calendar import WatchCalendar
from backend.infrastructure.ticker import BackgroundTicker


class ClockEngine:
    """Application service that coordinates the watch calendar and ticker."""

    def __init__(self, calendar: WatchCalendar, ticker: BackgroundTicker):
        self._calendar = calendar
        self._ticker = ticker
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            self._calendar.mark_running(True)
            self._ticker.start()

    def stop(self) -> None:
        with self._lock:
            self._calendar.mark_running(False)
            self._ticker.stop()

    def snapshot(self) -> ClockSnapshot:
        with self._lock:
            return self._calendar.snapshot()

    def set_snapshot(self, *, year: int, month: int, day: int, hour: int, minute: int, second: int) -> None:
        with self._lock:
            self._calendar.set_date(year, month, day)
            self._calendar.set_time(hour, minute, second)

    def tick(self) -> None:
        with self._lock:
            self._calendar.advance_second()


class ClockEngineSingleton:
    """Singleton factory for the global clock engine."""

    _instance: ClockEngine | None = None
    _lock = threading.Lock()

    @classmethod
    def instance(cls) -> ClockEngine:
        with cls._lock:
            if cls._instance is None:
                calendar = WatchCalendar(dt.datetime.now())
                ticker = BackgroundTicker(1.0, calendar.advance_second)
                cls._instance = ClockEngine(calendar, ticker)
            return cls._instance
