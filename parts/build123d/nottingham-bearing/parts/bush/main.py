import math

from build123d import CenterArc, Line, extrude, make_face

boreDiameter = 100.2
outerDiameter = 150.0
bushLength = 75.0
arcSpan = 180.0

assert bushLength > 0.0, "infeasible: bushLength must be positive"
assert outerDiameter > boreDiameter, "infeasible: outerDiameter must exceed the bore"
assert arcSpan > 0.0, "infeasible: arcSpan must be positive"

bore_radius = boreDiameter / 2.0
outer_radius = outerDiameter / 2.0
# Centre the span on BDC (standard angle -90 deg) so both split edges lie in y = 0.
start_angle = -90.0 - arcSpan / 2.0


def _polar(radius: float, angle_deg: float) -> tuple[float, float]:
    radians = math.radians(angle_deg)
    return (radius * math.cos(radians), radius * math.sin(radians))


outer_start = _polar(outer_radius, start_angle)
outer_end = _polar(outer_radius, start_angle + arcSpan)
inner_end = _polar(bore_radius, start_angle + arcSpan)
inner_start = _polar(bore_radius, start_angle)
section = make_face(
    [
        CenterArc((0, 0), outer_radius, start_angle, arcSpan),
        Line(outer_end, inner_end),
        CenterArc((0, 0), bore_radius, start_angle + arcSpan, -arcSpan),
        Line(inner_start, outer_start),
    ]
)
result = extrude(section, amount=bushLength)
