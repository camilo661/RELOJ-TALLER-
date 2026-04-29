"""Geometry helpers for watch rendering and hit testing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class CrownBounds:
    x1: float
    y1: float
    x2: float
    y2: float

    def contains(self, x: float, y: float) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2


@dataclass(frozen=True)
class WatchGeometry:
    width: float
    height: float
    center: Point
    radius: float
    sub_radius: float
    weekday_center: Point
    day_center: Point
    month_center: Point
    crown: CrownBounds


class GeometryFactory:
    """Factory for derived geometry values."""

    def create(self, width: float, height: float) -> WatchGeometry:
        available_width = max(width - 110, 240)
        radius = min(available_width / 2 - 26, height / 2 - 26)
        radius = max(radius, 120)
        center = Point(width / 2 - 26, height / 2)
        crown_height = radius * 0.42
        crown_width = radius * 0.16
        return WatchGeometry(
            width=width,
            height=height,
            center=center,
            radius=radius,
            sub_radius=radius * 0.14,
            weekday_center=Point(center.x - radius * 0.39, center.y - radius * 0.05),
            day_center=Point(center.x + radius * 0.39, center.y - radius * 0.05),
            month_center=Point(center.x, center.y + radius * 0.41),
            crown=CrownBounds(
                x1=center.x + radius + 16,
                x2=center.x + radius + 16 + crown_width,
                y1=center.y - crown_height / 2,
                y2=center.y + crown_height / 2,
            ),
        )
