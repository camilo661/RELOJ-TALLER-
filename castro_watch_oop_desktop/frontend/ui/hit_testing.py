"""Hit-testing services for the watch UI."""

import math
from dataclasses import dataclass

from frontend.ui.geometry import Point, WatchGeometry


@dataclass(frozen=True)
class HitZone:
    zone: str
    angle: float | None = None


class WatchHitTester:
    """Computes interactive zones for the analog watch."""

    def hit_test(self, x: float, y: float, geometry: WatchGeometry) -> HitZone | None:
        if geometry.crown.contains(x, y):
            return HitZone("crown")

        sub_radius = geometry.sub_radius * 1.1
        for zone, center in {
            "weekday": geometry.weekday_center,
            "day": geometry.day_center,
            "month": geometry.month_center,
        }.items():
            if self._distance(center, x, y) <= sub_radius:
                angle = self._normalize(math.atan2(y - center.y, x - center.x) + math.pi / 2)
                return HitZone(zone, angle)

        distance = self._distance(geometry.center, x, y)
        if distance > geometry.radius * 0.92 or distance < geometry.radius * 0.18:
            return None

        zone = "minute" if distance > geometry.radius * 0.56 else "hour"
        angle = self._normalize(math.atan2(y - geometry.center.y, x - geometry.center.x) + math.pi / 2)
        return HitZone(zone, angle)

    def _distance(self, center: Point, x: float, y: float) -> float:
        return math.hypot(x - center.x, y - center.y)

    def _normalize(self, angle: float) -> float:
        return (angle % math.tau + math.tau) % math.tau
