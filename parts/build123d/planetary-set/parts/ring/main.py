import math

from build123d import (
    Align,
    CenterArc,
    Compound,
    Cylinder,
    Polyline,
    Pos,
    extrude,
    make_face,
)

faceWidth = 10.0
outerRadius = 58.0
toothCount = 48.0
gearModule = 2.0
pressureAngle = 20.0
profileShift = 0.0
pitchRadius = gearModule * toothCount / 2.0
tipRadius = pitchRadius - gearModule
rootRadius = pitchRadius + 1.25 * gearModule
baseRadius = pitchRadius * math.cos(math.radians(pressureAngle))
spaceWidening = 0.05
spaceWidth = math.pi * gearModule / 2.0 + spaceWidening
toothThickness = math.pi * gearModule / 2.0 - spaceWidening
pitchAngle = 360.0 / toothCount
toothPhase = 0.0
flankPoints = 14.0

assert faceWidth > 0, "infeasible: faceWidth must be positive"
assert outerRadius > rootRadius, "infeasible: outerRadius must clear the tooth roots"
assert tipRadius > baseRadius, "infeasible: tip circle must lie outside the base circle"
assert rootRadius > tipRadius, "infeasible: root radius must exceed the tip radius"
assert toothCount >= 3, "infeasible: toothCount must be at least 3"
assert 0 < pressureAngle < 90, "infeasible: pressureAngle must be between 0 and 90"
assert flankPoints >= 2, "infeasible: flankPoints must be at least 2"
assert toothThickness > 0, "infeasible: toothThickness must be positive"
assert spaceWidth > 0, "infeasible: spaceWidth must be positive"

# Past the bore and both end faces so no tool face lies on the stock.
CUT_OVERRUN = 0.05


def space_half_angle(radius: float) -> float:
    # Pitch half-angle of the cutter tooth, plus involute roll off the pitch circle.
    pressure = math.radians(pressureAngle)
    alpha_r = math.acos(baseRadius / radius)
    inv_pitch = math.tan(pressure) - pressure
    inv_r = math.tan(alpha_r) - alpha_r
    thickening = spaceWidth + 2.0 * profileShift * gearModule * math.tan(pressure)
    return thickening / (2.0 * pitchRadius) + inv_pitch - inv_r


def flank_xy(radius: float, beta: float, side: float) -> tuple[float, float]:
    angle = beta + side * space_half_angle(radius)
    return (radius * math.cos(angle), radius * math.sin(angle))


def flank_radii() -> list[float]:
    count = round(flankPoints)
    phi_tip = math.sqrt((tipRadius / baseRadius) ** 2 - 1.0)
    phi_root = math.sqrt((rootRadius / baseRadius) ** 2 - 1.0)
    radii = []
    for i in range(count):
        phi = phi_tip + (phi_root - phi_tip) * i / (count - 1)
        radii.append(baseRadius * math.sqrt(1.0 + phi * phi))
    radii[0] = tipRadius
    radii[-1] = rootRadius
    return radii


def space_face(beta: float):
    radii = flank_radii()
    inner = tipRadius - CUT_OVERRUN
    if inner <= baseRadius:
        inner = (baseRadius + tipRadius) * 0.5
    right = [flank_xy(inner, beta, 1.0), *[flank_xy(radius, beta, 1.0) for radius in radii]]
    left = [flank_xy(radius, beta, -1.0) for radius in reversed(radii)]
    left.append(flank_xy(inner, beta, -1.0))
    a_right = math.degrees(beta + space_half_angle(radii[-1]))
    a_left = math.degrees(beta - space_half_angle(radii[-1]))
    root_arc = CenterArc((0, 0), radii[-1], a_right, a_left - a_right)
    edges = (
        list(Polyline(*right).edges())
        + list(root_arc.edges())
        + list(Polyline(*left).edges())
        + list(Polyline(left[-1], right[0]).edges())
    )
    return make_face(edges)


def tooth_spaces():
    faces = []
    count = round(toothCount)
    for k in range(count):
        beta = math.radians(toothPhase + (k + 0.5) * pitchAngle)
        faces.append(space_face(beta))
    return extrude(
        Pos(0, 0, -CUT_OVERRUN) * Compound(faces),
        amount=faceWidth + 2 * CUT_OVERRUN,
    )


blank = Cylinder(outerRadius, faceWidth, align=(Align.CENTER, Align.CENTER, Align.MIN))
bore = Pos(0, 0, -CUT_OVERRUN) * Cylinder(
    tipRadius,
    faceWidth + 2 * CUT_OVERRUN,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = (blank - bore - tooth_spaces()).clean()
