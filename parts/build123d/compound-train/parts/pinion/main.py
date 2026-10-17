import math

from build123d import Align, CenterArc, Cylinder, Polyline, Pos, extrude, make_face

teethCount = 20
gearModule = 2.0
pressureAngle = 20.0
profileShift = 0.0
addendumCoeff = 1.0
dedendumCoeff = 1.25
toothThinning = 0.05
faceWidth = 8.0
boreDiameter = 6.0
flankPoints = 14

pitchRadius = gearModule * teethCount / 2.0
tipRadius = pitchRadius + (addendumCoeff + profileShift) * gearModule
rootRadius = pitchRadius - (dedendumCoeff - profileShift) * gearModule
baseRadius = pitchRadius * math.cos(math.radians(pressureAngle))
toothThickness = (
    math.pi * gearModule / 2.0 + 2.0 * profileShift * gearModule * math.tan(math.radians(pressureAngle)) - toothThinning
)

assert faceWidth > 0.0, "infeasible: faceWidth must be positive"
assert boreDiameter > 0.0, "infeasible: boreDiameter must be positive"
assert boreDiameter < 2.0 * rootRadius, "infeasible: bore exceeds root diameter"
assert flankPoints >= 2, "infeasible: flankPoints must be at least 2"
assert pitchRadius > 0.0, "infeasible: pitchRadius must be positive"
assert tipRadius > baseRadius > rootRadius > 0.0, "infeasible: root, base and tip radii out of order"
assert toothThickness > 0.0, "infeasible: toothThickness must be positive"


def _involute(angle: float) -> float:
    return math.tan(angle) - angle


def _gear_edges() -> list:
    # Half-angle from the tooth centre: psi(t) = psi_b - (t - atan(t)), t the roll from the base circle.
    pressure = math.radians(pressureAngle)
    psi_base = toothThickness / (2.0 * pitchRadius) + _involute(pressure)
    roll_tip = math.sqrt((tipRadius / baseRadius) ** 2 - 1.0)
    samples = int(flankPoints)
    count = int(teethCount)
    edges = []

    def add(segment) -> None:
        edges.extend(segment.edges())

    def at(radius: float, angle: float) -> tuple[float, float]:
        return (radius * math.cos(angle), radius * math.sin(angle))

    def flank(center: float, sign: float, rolls: list[float]) -> list[tuple[float, float]]:
        points = []
        for roll in rolls:
            radius = baseRadius * math.sqrt(1.0 + roll * roll)
            half = psi_base - (roll - math.atan(roll))
            points.append(at(radius, center + sign * half))
        return points

    rolls_up = [roll_tip * k / (samples - 1) for k in range(samples)]
    rolls_down = list(reversed(rolls_up))
    for i in range(count):
        center = 2.0 * math.pi * i / count
        nxt = 2.0 * math.pi * (i + 1) / count
        half_tip = psi_base - (roll_tip - math.atan(roll_tip))
        add(Polyline(at(rootRadius, center - psi_base), at(baseRadius, center - psi_base)))
        add(Polyline(*flank(center, -1.0, rolls_up)))
        add(
            CenterArc(
                (0.0, 0.0),
                tipRadius,
                math.degrees(center - half_tip),
                math.degrees(2.0 * half_tip),
            )
        )
        add(Polyline(*flank(center, 1.0, rolls_down)))
        add(Polyline(at(baseRadius, center + psi_base), at(rootRadius, center + psi_base)))
        add(
            CenterArc(
                (0.0, 0.0),
                rootRadius,
                math.degrees(center + psi_base),
                math.degrees(nxt - center - 2.0 * psi_base),
            )
        )
    return edges


blank = extrude(make_face(_gear_edges()), amount=faceWidth)
bore_overrun = 0.05
bore = Pos(0.0, 0.0, -bore_overrun) * Cylinder(
    boreDiameter / 2.0,
    faceWidth + 2.0 * bore_overrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = blank - bore
