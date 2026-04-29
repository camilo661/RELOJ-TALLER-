"""Domain object that owns watch time and calendar state."""

import calendar
import datetime as dt

from backend.domain.clock_snapshot import ClockSnapshot
from backend.domain.ring import CyclicRing


class WatchCalendar:
    """Aggregate root for the state of the watch."""

    def __init__(self, now: dt.datetime):
        self._seconds = CyclicRing(0, 59)
        self._minutes = CyclicRing(0, 59)
        self._hours = CyclicRing(0, 23)
        self._weekdays = CyclicRing(0, 6)
        self._month_days = CyclicRing(1, 31)
        self._months = CyclicRing(1, 12)
        self._year = now.year
        self._running = False
        self.apply_datetime(now)

    def mark_running(self, running: bool) -> None:
        self._running = running

    def advance_second(self) -> None:
        if not self._seconds.tick():
            return
        if not self._minutes.tick():
            return
        if not self._hours.tick():
            return
        self._advance_day()

    def apply_datetime(self, value: dt.datetime) -> None:
        self._year = value.year
        self._months.seek(value.month)
        self._month_days.seek(value.day)
        self._weekdays.seek(value.weekday())
        self._hours.seek(value.hour)
        self._minutes.seek(value.minute)
        self._seconds.seek(value.second)

    def set_date(self, year: int, month: int, day: int) -> None:
        safe_month = max(1, min(12, month))
        self._year = year
        self._months.seek(safe_month)
        limit = self._days_in_month(self._year, self._months.current)
        safe_day = max(1, min(limit, day))
        self._month_days.seek(safe_day)
        self._weekdays.seek(dt.date(self._year, self._months.current, safe_day).weekday())

    def set_time(self, hour: int, minute: int, second: int) -> None:
        self._hours.seek(hour % 24)
        self._minutes.seek(minute % 60)
        self._seconds.seek(second % 60)

    def snapshot(self) -> ClockSnapshot:
        return ClockSnapshot(
            hour=self._hours.current,
            minute=self._minutes.current,
            second=self._seconds.current,
            day_of_week=self._weekdays.current,
            day_of_month=self._month_days.current,
            month=self._months.current,
            year=self._year,
            running=self._running,
        )

    def _advance_day(self) -> None:
        self._weekdays.tick()
        new_day = (self._month_days.current % self._days_in_month(self._year, self._months.current)) + 1
        if new_day == 1 and self._months.tick():
            self._year += 1
        self._month_days.seek(new_day)

    def _days_in_month(self, year: int, month: int) -> int:
        return calendar.monthrange(year, month)[1]
