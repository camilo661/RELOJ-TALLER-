"""Use cases for interactive watch adjustments."""

import calendar
import datetime as dt

from backend.domain.clock_snapshot import ClockSnapshot


class ClockStateMutator:
    """Service object that transforms clock snapshots for UI interactions."""

    def shift_minutes(self, snapshot: ClockSnapshot, amount: int) -> ClockSnapshot:
        return self._shift(snapshot, lambda value: value + dt.timedelta(minutes=amount))

    def shift_hours(self, snapshot: ClockSnapshot, amount: int) -> ClockSnapshot:
        return self._shift(snapshot, lambda value: value + dt.timedelta(hours=amount))

    def shift_days(self, snapshot: ClockSnapshot, amount: int) -> ClockSnapshot:
        return self._shift(snapshot, lambda value: value + dt.timedelta(days=amount))

    def shift_months(self, snapshot: ClockSnapshot, amount: int) -> ClockSnapshot:
        def operation(value: dt.datetime) -> dt.datetime:
            month_index = (value.month - 1) + amount
            year = value.year + month_index // 12
            month = month_index % 12 + 1
            limit = calendar.monthrange(year, month)[1]
            return value.replace(year=year, month=month, day=min(value.day, limit))

        return self._shift(snapshot, operation)

    def _shift(self, snapshot: ClockSnapshot, operation) -> ClockSnapshot:
        value = dt.datetime(
            snapshot.year,
            snapshot.month,
            snapshot.day_of_month,
            snapshot.hour,
            snapshot.minute,
            snapshot.second,
        )
        shifted = operation(value)
        return ClockSnapshot(
            hour=shifted.hour,
            minute=shifted.minute,
            second=shifted.second,
            day_of_week=shifted.weekday(),
            day_of_month=shifted.day,
            month=shifted.month,
            year=shifted.year,
            running=False,
        )
