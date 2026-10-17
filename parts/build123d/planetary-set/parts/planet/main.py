import math

from build123d import Align, CenterArc, Cylinder, Polyline, Pos, extrude, make_face

gearModule = 2.0
toothCount = 12.0
pressureAngle = 20.0
profileShift = 0.0
faceWidth = 10.0
toothThinning = 0.1
boreDiameter = 8.0
toothPhase = 0.0
flankPoints = 14.0

toothPitchAngle = 360.0 / toothCount
pitchRadius = gearModule * toothCount / 2.0
tipRadius = pitchRadius + gearModule * (1.0 + profileShift)
rootRadius = pitchRadius - gearModule * (1.25 - profileShift)
baseRadius = pitchRadius * math.cos(math.radians(pressureAngle))
pitchToothThickness = (
    math.pi * gearModule / 2.0 + 2.0 * profileShift * gearModule * math.tan(math.radians(pressureAngle)) - toothThinning
)

assert faceWidth > 0.0, "infeasible: faceWidth must be positive"
assert boreDiameter > 0.0, "infeasible: boreDiameter must be positive"
assert toothCount >= 3.0, "infeasible: toothCount must be at least 3"
assert abs(toothCount - round(toothCount)) < 1e-6, "infeasible: toothCount must be an integer"
assert flankPoints >= 2.0, "infeasible: flankPoints must be at least 2"
assert abs(flankPoints - round(flankPoints)) < 1e-6, "infeasible: flankPoints must be an integer"
assert tipRadius > baseRadius > rootRadius, "infeasible: tip, base and root radii are out of order"
assert rootRadius > boreDiameter / 2.0, "infeasible: bore cuts through the root circle"
assert 0.0 < pressureAngle < 90.0, "infeasible: pressureAngle must lie between 0 and 90 deg"


def _involute(alpha: float) -> float:
    return math.tan(alpha) - alpha


def _half_angle(radius: float) -> float:
    alpha = math.acos(min(1.0, baseRadius / radius))
    return pitchToothThickness / (2.0 * pitchRadius) + _involute(math.radians(pressureAngle)) - _involute(alpha)


assert _half_angle(tipRadius) > 0.0, "infeasible: tooth thinning points the tip"
assert _half_angle(baseRadius) < math.radians(toothPitchAngle) / 2.0, "infeasible: adjacent teeth meet at the root"


def _point(radius: float, angle_deg: float) -> tuple[float, float]:
    radians = math.radians(angle_deg)
    return (radius * math.cos(radians), radius * math.sin(radians))


tooth_total = round(toothCount)
flank_total = round(flankPoints)
tip_half = math.degrees(_half_angle(tipRadius))
base_half = math.degrees(_half_angle(baseRadius))

segments = []
for tooth in range(tooth_total):
    center = toothPhase + tooth * toothPitchAngle
    lower_flank = []
    upper_flank = []
    for index in range(flank_total):
        radius = baseRadius + (tipRadius - baseRadius) * index / (flank_total - 1)
        half = math.degrees(_half_angle(radius))
        lower_flank.append(_point(radius, center - half))
        upper_flank.append(_point(radius, center + half))
    segments.append(Polyline(_point(rootRadius, center - base_half), *lower_flank))
    segments.append(CenterArc((0.0, 0.0), tipRadius, center - tip_half, 2.0 * tip_half))
    segments.append(Polyline(*reversed(upper_flank), _point(rootRadius, center + base_half)))
    segments.append(
        CenterArc(
            (0.0, 0.0),
            rootRadius,
            center + base_half,
            toothPitchAngle - 2.0 * base_half,
        )
    )

profile = segments[0]
for segment in segments[1:]:
    profile += segment

gear = extrude(make_face(profile), amount=faceWidth)
bore_overrun = 0.05
bore = Pos(0.0, 0.0, -bore_overrun) * Cylinder(
    boreDiameter / 2.0,
    faceWidth + 2.0 * bore_overrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = gear - bore
