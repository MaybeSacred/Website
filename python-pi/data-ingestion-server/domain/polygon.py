from math import isfinite

from .home_object import Vector3Dto


def validate_polygon(points: list[Vector3Dto]) -> None:
    def cross(a: Vector3Dto, b: Vector3Dto, c: Vector3Dto) -> float:
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

    def on_segment(a: Vector3Dto, b: Vector3Dto, p: Vector3Dto) -> bool:
        return (
            cross(a, b, p) == 0
            and min(a.x, b.x) <= p.x <= max(a.x, b.x)
            and min(a.y, b.y) <= p.y <= max(a.y, b.y)
        )

    if any(not isfinite(p.x) or not isfinite(p.y) for p in points):
        raise ValueError("Group points must have finite coordinates")
    for i, a in enumerate(points):
        if len(points) < 3:
            continue
        b = points[(i + 1) % len(points)]
        previous = points[(i - 1) % len(points)]
        if (a.x == b.x and a.y == b.y) or (
            cross(previous, a, b) == 0
            and (previous.x - a.x) * (b.x - a.x)
            + (previous.y - a.y) * (b.y - a.y) > 0
        ):
            raise ValueError("Group boundaries must not self-intersect or overlap")
        for j in range(i + 1, len(points)):
            if j == i + 1 or (i == 0 and j == len(points) - 1):
                continue
            c, d = points[j], points[(j + 1) % len(points)]
            if (
                on_segment(a, b, c) or on_segment(a, b, d)
                or on_segment(c, d, a) or on_segment(c, d, b)
                or (
                    cross(a, b, c) * cross(a, b, d) < 0
                    and cross(c, d, a) * cross(c, d, b) < 0
                )
            ):
                raise ValueError("Group boundaries must not self-intersect or overlap")
