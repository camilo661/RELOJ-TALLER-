"""Immutable clock snapshot model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClockSnapshot:
    """Serializable view of the current watch state."""

    hour: int
    minute: int
    second: int
    day_of_week: int
    day_of_month: int
    month: int
    year: int
    running: bool

    def to_mapping(self) -> dict:
        return {
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
            "day_of_week": self.day_of_week,
            "day_of_month": self.day_of_month,
            "month": self.month,
            "year": self.year,
            "running": self.running,
        }
